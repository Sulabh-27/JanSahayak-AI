"""
JanSahayak AI — FastAPI Production REST API Server
Provides endpoints for Officer Dashboard, Application Management,
Deterministic Validation, AI Review (Groq LLM), and Audit Logging.
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

import config
from services import database as db
from services.validation import validate_application, get_document_completeness, has_missing_documents
from services.prioritization import calculate_priority, get_priority_counts
from services.ai_review import perform_ai_review, is_ai_available
from services.decisions import process_decision, get_application_audit_trail

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("jansahayak-api")

# Initialize DB and Seed Data on startup
db.init_db()
db.seed_data()

app = FastAPI(
    title="JanSahayak AI API — जनसहायक AI",
    description="AI-Assisted Government Application Review System for Madhya Pradesh Officers",
    version="2.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Request/Response Models ---

class LoginRequest(BaseModel):
    username: str
    password: str

class DecisionRequest(BaseModel):
    action: str = Field(..., description="'approve', 'reject', or 'return'")
    officer_id: Optional[str] = None
    officer_name: Optional[str] = None
    reason: str = Field(..., min_length=2, description="Mandatory officer reason/remarks")
    ai_recommendation: Optional[str] = None

class AIReviewRequest(BaseModel):
    force_refresh: bool = False


# --- API Routes ---

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": config.APP_NAME,
        "app_name_hi": config.APP_NAME_HI,
        "version": "2.0.0",
        "ai_available": is_ai_available(),
        "groq_model": config.GROQ_MODEL,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/auth/login")
def login(creds: LoginRequest):
    if creds.username == config.DEMO_USERNAME and creds.password == config.DEMO_PASSWORD:
        return {
            "success": True,
            "officer": {
                "officer_id": config.DEMO_OFFICER_ID,
                "officer_name": config.DEMO_OFFICER_NAME,
                "role": "तहसीलदार / राजस्व अधिकारी",
                "department": "राजस्व एवं लोक सेवा प्रबंधन विभाग, मध्य प्रदेश",
                "username": creds.username
            },
            "token": "demo-officer-session-token-mp"
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="अमान्य क्रेडेंशियल्स (Invalid credentials)")


@app.get("/api/dashboard/stats")
def get_dashboard_summary():
    stats = db.get_dashboard_stats()
    all_apps = db.get_all_applications()
    
    pending_apps = [a for a in all_apps if a["status"] in (config.STATUS_PENDING, config.STATUS_UNDER_REVIEW)]
    priority_counts = get_priority_counts(pending_apps) if pending_apps else {"high": 0, "medium": 0, "low": 0}
    incomplete_docs_count = sum(1 for a in pending_apps if has_missing_documents(a))
    
    # Calculate aged backlog (> 14 days)
    aged_count = 0
    now = datetime.now()
    for a in pending_apps:
        try:
            sub = datetime.strptime(a.get("submission_date", ""), "%Y-%m-%d")
            if (now - sub).days > 14:
                aged_count += 1
        except Exception:
            pass

    return {
        "total_applications": stats["total"],
        "pending": stats["pending"],
        "approved": stats["approved"],
        "rejected": stats["rejected"],
        "returned": stats["returned"],
        "high_priority": priority_counts.get("high", 0),
        "medium_priority": priority_counts.get("medium", 0),
        "low_priority": priority_counts.get("low", 0),
        "incomplete_documents": incomplete_docs_count,
        "aged_backlog_14_days": aged_count
    }


@app.get("/api/applications")
def list_applications(
    search: Optional[str] = Query(None, description="Search by ID or applicant name"),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    doc_filter: Optional[str] = Query(None, description="'complete' or 'incomplete'")
):
    all_apps = db.get_all_applications()
    now = datetime.now()
    
    augmented = []
    for app_item in all_apps:
        priority = calculate_priority(app_item)
        doc_complete = not has_missing_documents(app_item)
        completeness = get_document_completeness(app_item)
        
        days_pending = 0
        try:
            sub_date = datetime.strptime(app_item.get("submission_date", ""), "%Y-%m-%d")
            days_pending = max(0, (now - sub_date).days)
        except Exception:
            pass

        app_item["priority"] = priority
        app_item["doc_complete"] = doc_complete
        app_item["completeness_pct"] = completeness["completeness_pct"]
        app_item["days_pending"] = days_pending
        augmented.append(app_item)
    
    # Filtering
    filtered = augmented
    if search and search.strip():
        q = search.strip().lower()
        filtered = [
            a for a in filtered
            if q in a.get("application_id", "").lower()
            or q in a.get("applicant_name", "").lower()
            or q in a.get("applicant_name_en", "").lower()
            or q in a.get("district", "").lower()
        ]
    
    if status_filter and status_filter != "all":
        filtered = [a for a in filtered if a["status"] == status_filter]
        
    if priority_filter and priority_filter != "all":
        filtered = [a for a in filtered if a["priority"]["level"] == priority_filter]
        
    if doc_filter == "incomplete":
        filtered = [a for a in filtered if not a["doc_complete"]]
    elif doc_filter == "complete":
        filtered = [a for a in filtered if a["doc_complete"]]
        
    # Default sorting: priority score desc, then oldest submission date asc
    filtered.sort(key=lambda a: (-a["priority"]["score"], a.get("submission_date", "")))
    
    return {
        "count": len(filtered),
        "total": len(all_apps),
        "applications": filtered
    }


@app.get("/api/applications/{app_id}")
def get_application_detail(app_id: str):
    app_data = db.get_application_by_id(app_id)
    if not app_data:
        raise HTTPException(status_code=404, detail="आवेदन नहीं मिला (Application not found)")
        
    findings = validate_application(app_data)
    completeness = get_document_completeness(app_data)
    priority = calculate_priority(app_data)
    audit_trail = get_application_audit_trail(app_id)
    
    # Parse document details JSON safely
    doc_details = {}
    try:
        if isinstance(app_data.get("document_details"), str):
            doc_details = json.loads(app_data["document_details"])
        elif isinstance(app_data.get("document_details"), dict):
            doc_details = app_data["document_details"]
    except Exception:
        pass

    days_pending = 0
    try:
        sub_date = datetime.strptime(app_data.get("submission_date", ""), "%Y-%m-%d")
        days_pending = max(0, (datetime.now() - sub_date).days)
    except Exception:
        pass

    return {
        "application": app_data,
        "document_details": doc_details,
        "completeness": completeness,
        "findings": findings,
        "priority": priority,
        "days_pending": days_pending,
        "audit_trail": audit_trail
    }


@app.post("/api/applications/{app_id}/ai-review")
def run_ai_review(app_id: str):
    app_data = db.get_application_by_id(app_id)
    if not app_data:
        raise HTTPException(status_code=404, detail="आवेदन नहीं मिला (Application not found)")
        
    result = perform_ai_review(app_data)
    return result


@app.post("/api/applications/{app_id}/decision")
def submit_decision(app_id: str, decision: DecisionRequest):
    if not decision.reason or not decision.reason.strip():
        raise HTTPException(status_code=400, detail="निर्णय का कारण/टिप्पणी अनिवार्य है (Remarks are mandatory)")
        
    officer_id = decision.officer_id or config.DEMO_OFFICER_ID
    officer_name = decision.officer_name or config.DEMO_OFFICER_NAME
    
    result = process_decision(
        app_id=app_id,
        action=decision.action,
        officer_id=officer_id,
        officer_name=officer_name,
        reason=decision.reason.strip(),
        ai_recommendation=decision.ai_recommendation
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message_hi", "निर्णय दर्ज करने में त्रुटि"))
        
    return result


@app.get("/api/audit-history")
def get_global_audit_history():
    return {
        "history": db.get_all_audit_history()
    }


@app.post("/api/system/reseed")
def reseed_database():
    count = db.seed_data(force_reseed=True)
    return {
        "success": True,
        "message": f"डेटाबेस सफलतापूर्वक रीसेट हो गया ({count} आवेदन लोड हुए)",
        "count": count
    }


# Mount Static Build if frontend/dist exists
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
