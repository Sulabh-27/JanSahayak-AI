"""
JanSahayak AI — Prioritization Service
Deterministic, explainable priority scoring for applications.
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple

import config
from services.validation import count_missing_documents, validate_application


def calculate_priority(app: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate an explainable priority score for an application.
    
    Returns:
      - score: numeric priority score
      - level: 'high', 'medium', 'low'
      - level_hi: Hindi label
      - reasons_hi: list of reasons explaining the priority
      - factors: dict of individual factor scores
    """
    score = 0.0
    reasons_hi = []
    factors = {}
    
    # Factor 1: Days pending
    days_pending = _get_days_pending(app)
    days_score = 0.0
    if days_pending > 21:
        days_score = 3.0
        reasons_hi.append(f"आवेदन {days_pending} दिनों से लंबित है (21 दिन से अधिक)")
    elif days_pending > 14:
        days_score = 2.0
        reasons_hi.append(f"आवेदन {days_pending} दिनों से लंबित है (14 दिन से अधिक)")
    elif days_pending > 7:
        days_score = 1.0
        reasons_hi.append(f"आवेदन {days_pending} दिनों से लंबित है (7 दिन से अधिक)")
    factors["days_pending"] = days_score
    score += days_score * config.PRIORITY_WEIGHT_DAYS_PENDING
    
    # Factor 2: Missing documents
    missing_count = count_missing_documents(app)
    missing_score = 0.0
    if missing_count >= 3:
        missing_score = 3.0
        reasons_hi.append(f"{missing_count} आवश्यक दस्तावेज़ गायब हैं — तत्काल ध्यान आवश्यक")
    elif missing_count >= 1:
        missing_score = 1.5
        reasons_hi.append(f"{missing_count} आवश्यक दस्तावेज़ गायब {'हैं' if missing_count > 1 else 'है'}")
    factors["missing_documents"] = missing_score
    score += missing_score * config.PRIORITY_WEIGHT_MISSING_DOCS
    
    # Factor 3: Inconsistencies
    findings = validate_application(app)
    warnings = [f for f in findings if f["severity"] == "warning"]
    errors = [f for f in findings if f["severity"] == "error"]
    inconsistency_score = 0.0
    
    # Only count non-document warnings (income, date issues) as inconsistencies
    non_doc_warnings = [w for w in warnings if "दस्तावेज़ गायब" not in w["finding_hi"]]
    if len(non_doc_warnings) >= 2:
        inconsistency_score = 2.0
        reasons_hi.append("एकाधिक विसंगतियां पाई गई हैं")
    elif len(non_doc_warnings) == 1:
        inconsistency_score = 1.0
        reasons_hi.append("एक विसंगति पाई गई है")
    factors["inconsistencies"] = inconsistency_score
    score += inconsistency_score * config.PRIORITY_WEIGHT_INCONSISTENCIES
    
    # Factor 4: Configured urgency
    urgency = app.get("urgency", "normal")
    urgency_score = 0.0
    if urgency == "high":
        urgency_score = 3.0
        reasons_hi.append("उच्च तत्कालता चिह्नित है")
    elif urgency == "medium":
        urgency_score = 1.5
        reasons_hi.append("मध्यम तत्कालता चिह्नित है")
    factors["urgency"] = urgency_score
    score += urgency_score * config.PRIORITY_WEIGHT_URGENCY
    
    # Determine level
    if score >= config.PRIORITY_HIGH_THRESHOLD:
        level = "high"
        level_hi = "उच्च"
    elif score >= config.PRIORITY_MEDIUM_THRESHOLD:
        level = "medium"
        level_hi = "मध्यम"
    else:
        level = "low"
        level_hi = "सामान्य"
    
    if not reasons_hi:
        reasons_hi.append("कोई विशेष प्राथमिकता कारक नहीं — सामान्य प्रसंस्करण")
    
    return {
        "score": round(score, 1),
        "level": level,
        "level_hi": level_hi,
        "reasons_hi": reasons_hi,
        "factors": factors,
    }


def sort_applications_by_priority(applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort applications by priority score (highest first), then by submission date (oldest first).
    Each application dict gets a 'priority' key added.
    """
    for app in applications:
        app["priority"] = calculate_priority(app)
    
    applications.sort(
        key=lambda a: (-a["priority"]["score"], a.get("submission_date", "")),
    )
    return applications


def get_priority_counts(applications: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count applications by priority level."""
    counts = {"high": 0, "medium": 0, "low": 0}
    for app in applications:
        priority = calculate_priority(app)
        counts[priority["level"]] = counts.get(priority["level"], 0) + 1
    return counts


def _get_days_pending(app: Dict[str, Any]) -> int:
    """Calculate how many days an application has been pending."""
    try:
        sub_date = datetime.strptime(app.get("submission_date", ""), "%Y-%m-%d")
        return (datetime.now() - sub_date).days
    except (ValueError, TypeError):
        return 0
