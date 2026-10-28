"""
JanSahayak AI — Validation Service
Deterministic document and field validation rules.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import config


def validate_application(app: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run all deterministic validation checks on an application.
    Returns a list of findings, each with:
      - severity: 'error', 'warning', 'info'
      - finding_hi: Hindi description
      - finding_en: English description
      - evidence: field references or values
      - recommendation_hi: suggested next step in Hindi
    """
    findings = []
    
    # Parse submitted documents
    submitted = _parse_json_field(app.get("submitted_documents", "[]"))
    doc_details = _parse_json_field(app.get("document_details", "{}"))
    
    # 1. Check required documents
    findings.extend(_check_required_documents(submitted, doc_details))
    
    # 2. Check income consistency
    findings.extend(_check_income_consistency(app))
    
    # 3. Check date consistency
    findings.extend(_check_date_consistency(app))
    
    # 4. Check required fields
    findings.extend(_check_required_fields(app))
    
    # 5. Check document verification status
    findings.extend(_check_document_verification(doc_details))
    
    return findings


def get_document_completeness(app: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute document completeness for an application.
    Returns:
      - total_required: count of required documents
      - submitted: count of submitted documents
      - missing: list of missing document IDs
      - missing_names_hi: list of missing document names in Hindi
      - completeness_pct: percentage complete
      - documents: list of all document statuses
    """
    submitted = _parse_json_field(app.get("submitted_documents", "[]"))
    doc_details = _parse_json_field(app.get("document_details", "{}"))
    
    total_required = len(config.REQUIRED_DOCUMENTS)
    missing = []
    missing_names_hi = []
    documents = []
    
    for req_doc in config.REQUIRED_DOCUMENTS:
        doc_id = req_doc["id"]
        is_submitted = doc_id in submitted
        detail = doc_details.get(doc_id, {})
        
        status = "missing"
        if is_submitted:
            doc_status = detail.get("status", "submitted")
            if doc_status == "verified":
                status = "verified"
            elif doc_status == "needs_verification":
                status = "needs_verification"
            else:
                status = "submitted"
        else:
            missing.append(doc_id)
            missing_names_hi.append(req_doc["name_hi"])
        
        documents.append({
            "id": doc_id,
            "name_hi": req_doc["name_hi"],
            "name_en": req_doc["name_en"],
            "status": status,
            "detail": detail,
        })
    
    submitted_count = total_required - len(missing)
    completeness_pct = round((submitted_count / total_required) * 100) if total_required > 0 else 0
    
    return {
        "total_required": total_required,
        "submitted": submitted_count,
        "missing": missing,
        "missing_names_hi": missing_names_hi,
        "completeness_pct": completeness_pct,
        "documents": documents,
    }


def has_missing_documents(app: Dict[str, Any]) -> bool:
    """Quick check if an application has any missing required documents."""
    completeness = get_document_completeness(app)
    return len(completeness["missing"]) > 0


def count_missing_documents(app: Dict[str, Any]) -> int:
    """Count how many required documents are missing."""
    completeness = get_document_completeness(app)
    return len(completeness["missing"])


# --- Internal Check Functions ---

def _check_required_documents(submitted: List[str], doc_details: Dict) -> List[Dict]:
    """Check for missing required documents."""
    findings = []
    for req_doc in config.REQUIRED_DOCUMENTS:
        doc_id = req_doc["id"]
        if doc_id not in submitted:
            findings.append({
                "severity": "error",
                "finding_hi": f"आवश्यक दस्तावेज़ गायब: {req_doc['name_hi']}",
                "finding_en": f"Required document missing: {req_doc['name_en']}",
                "evidence": f"दस्तावेज़ '{req_doc['name_hi']}' प्रस्तुत नहीं किया गया है",
                "recommendation_hi": f"आवेदक से {req_doc['name_hi']} प्रस्तुत करने का अनुरोध करें",
            })
    return findings


def _check_income_consistency(app: Dict[str, Any]) -> List[Dict]:
    """Check for income value inconsistencies."""
    findings = []
    declared = app.get("declared_annual_income")
    secondary = app.get("secondary_income_record")
    
    if declared is not None and secondary is not None:
        if declared != secondary:
            diff = abs(declared - secondary)
            pct = round((diff / max(declared, secondary, 1)) * 100, 1)
            findings.append({
                "severity": "warning",
                "finding_hi": f"आय में विसंगति: घोषित आय ₹{declared:,.0f} और अन्य रिकॉर्ड ₹{secondary:,.0f} में अंतर ({pct}%)",
                "finding_en": f"Income inconsistency: declared ₹{declared:,.0f} vs secondary record ₹{secondary:,.0f} ({pct}% difference)",
                "evidence": f"declared_annual_income={declared}, secondary_income_record={secondary}",
                "recommendation_hi": "आय के दोनों स्रोतों की सत्यापन जांच करें। विसंगति का कारण जानने हेतु आवेदक से स्पष्टीकरण मांगें।",
            })
    
    if declared is not None and declared == 0:
        findings.append({
            "severity": "warning",
            "finding_hi": "घोषित वार्षिक आय ₹0 है — यह असामान्य हो सकता है",
            "finding_en": "Declared annual income is ₹0 — this may be unusual",
            "evidence": "declared_annual_income=0",
            "recommendation_hi": "आवेदक से आय का विवरण और स्रोत की पुष्टि करें",
        })
    
    return findings


def _check_date_consistency(app: Dict[str, Any]) -> List[Dict]:
    """Check for date-related issues."""
    findings = []
    
    # Check conflicting dates field
    conflicting = app.get("conflicting_dates")
    if conflicting:
        if isinstance(conflicting, str):
            try:
                conflicting = json.loads(conflicting)
            except (json.JSONDecodeError, TypeError):
                conflicting = None
        
        if conflicting and isinstance(conflicting, dict):
            issue = conflicting.get("issue", "तिथि विसंगति पाई गई")
            findings.append({
                "severity": "warning",
                "finding_hi": f"तिथि विसंगति: {issue}",
                "finding_en": f"Date conflict: {issue}",
                "evidence": json.dumps(conflicting, ensure_ascii=False),
                "recommendation_hi": "दस्तावेज़ों की तिथियों की जांच करें और नवीनतम प्रति का अनुरोध करें",
            })
    
    # Check if application is very old
    try:
        sub_date = datetime.strptime(app.get("submission_date", ""), "%Y-%m-%d")
        days_pending = (datetime.now() - sub_date).days
        if days_pending > 30 and app.get("status") in (config.STATUS_PENDING, config.STATUS_UNDER_REVIEW):
            findings.append({
                "severity": "info",
                "finding_hi": f"यह आवेदन {days_pending} दिनों से लंबित है",
                "finding_en": f"Application has been pending for {days_pending} days",
                "evidence": f"submission_date={app.get('submission_date')}, days_pending={days_pending}",
                "recommendation_hi": "प्राथमिकता के आधार पर शीघ्र समीक्षा करें",
            })
    except (ValueError, TypeError):
        pass
    
    return findings


def _check_required_fields(app: Dict[str, Any]) -> List[Dict]:
    """Check for missing or empty required fields."""
    findings = []
    
    required_fields = [
        ("applicant_name", "आवेदक का नाम"),
        ("declared_annual_income", "घोषित वार्षिक आय"),
        ("income_source", "आय का स्रोत"),
        ("district", "जिला"),
        ("address", "पता"),
    ]
    
    for field, name_hi in required_fields:
        value = app.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            findings.append({
                "severity": "warning",
                "finding_hi": f"आवश्यक फ़ील्ड खाली है: {name_hi}",
                "finding_en": f"Required field is empty: {field}",
                "evidence": f"{field} is empty or missing",
                "recommendation_hi": f"आवेदक से {name_hi} की जानकारी प्राप्त करें",
            })
    
    if app.get("family_members") is not None and app.get("family_members") == 0:
        findings.append({
            "severity": "info",
            "finding_hi": "परिवार के सदस्यों की संख्या 0 दर्ज है — कृपया सत्यापित करें",
            "finding_en": "Family members count is 0 — please verify",
            "evidence": "family_members=0",
            "recommendation_hi": "आवेदक से परिवार के सदस्यों की सही संख्या की पुष्टि करें",
        })
    
    return findings


def _check_document_verification(doc_details: Dict) -> List[Dict]:
    """Check for documents that need verification."""
    findings = []
    for doc_id, detail in doc_details.items():
        if detail.get("status") == "needs_verification":
            doc_name = doc_id.replace("_", " ").title()
            # Find Hindi name
            for req in config.REQUIRED_DOCUMENTS:
                if req["id"] == doc_id:
                    doc_name = req["name_hi"]
                    break
            findings.append({
                "severity": "info",
                "finding_hi": f"दस्तावेज़ सत्यापन शेष: {doc_name}",
                "finding_en": f"Document needs verification: {doc_id}",
                "evidence": f"document '{doc_id}' status = needs_verification",
                "recommendation_hi": f"{doc_name} की प्रामाणिकता सत्यापित करें",
            })
    return findings


def _parse_json_field(value):
    """Safely parse a JSON string field."""
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return [] if value.startswith("[") else {}
    return []
