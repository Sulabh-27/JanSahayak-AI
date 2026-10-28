"""
JanSahayak AI — Decisions Service
Approve, reject, return actions and audit record management.
"""
import logging
from typing import Dict, Any, Optional

import config
from services import database as db

logger = logging.getLogger(__name__)


# Status mapping for actions
ACTION_TO_STATUS = {
    "approve": config.STATUS_APPROVED,
    "reject": config.STATUS_REJECTED,
    "return": config.STATUS_RETURNED,
}

ACTION_LABELS_HI = {
    "approve": "स्वीकृत",
    "reject": "अस्वीकृत",
    "return": "सुधार हेतु वापस",
}


def process_decision(
    app_id: str,
    action: str,
    officer_id: str,
    officer_name: str,
    reason: str,
    ai_recommendation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process an officer's decision on an application.
    
    Args:
        app_id: Application ID
        action: 'approve', 'reject', or 'return'
        officer_id: Officer's ID
        officer_name: Officer's name
        reason: Officer's mandatory reason/remarks
        ai_recommendation: The AI's suggested action, if any
    
    Returns:
        dict with:
          - success: bool
          - message_hi: Hindi result message
          - message_en: English result message
    """
    # Validate action
    if action not in ACTION_TO_STATUS:
        return {
            "success": False,
            "message_hi": f"अमान्य कार्रवाई: {action}",
            "message_en": f"Invalid action: {action}",
        }
    
    # Validate reason
    if not reason or not reason.strip():
        return {
            "success": False,
            "message_hi": "कारण/टिप्पणी अनिवार्य है। कृपया अपना कारण दर्ज करें।",
            "message_en": "Reason/remarks are required.",
        }
    
    # Get current application
    app = db.get_application_by_id(app_id)
    if not app:
        return {
            "success": False,
            "message_hi": f"आवेदन '{app_id}' नहीं मिला",
            "message_en": f"Application '{app_id}' not found",
        }
    
    old_status = app["status"]
    new_status = ACTION_TO_STATUS[action]
    
    # Check if already in terminal state (approve can't be re-approved, etc.)
    if old_status == new_status:
        return {
            "success": False,
            "message_hi": f"आवेदन पहले से '{ACTION_LABELS_HI.get(action, action)}' स्थिति में है",
            "message_en": f"Application is already in '{new_status}' status",
        }
    
    # Determine if officer followed AI recommendation
    ai_followed = None
    if ai_recommendation:
        ai_action_map = {
            "APPROVE": "approve",
            "REJECT": "reject",
            "RETURN_FOR_CORRECTION": "return",
            "NEEDS_MANUAL_REVIEW": None,
        }
        expected_action = ai_action_map.get(ai_recommendation)
        if expected_action is not None:
            ai_followed = 1 if action == expected_action else 0
    
    # Update application status (with optimistic concurrency)
    updated = db.update_application_status(app_id, new_status, review_notes=reason)
    if not updated:
        return {
            "success": False,
            "message_hi": "आवेदन की स्थिति अपडेट नहीं हो सकी। हो सकता है किसी अन्य ने बीच में परिवर्तन किया हो। कृपया पुनः प्रयास करें।",
            "message_en": "Could not update — possible concurrent modification. Please retry.",
        }
    
    # Record the decision
    decision_id = db.add_decision(
        app_id=app_id,
        action=action,
        officer_id=officer_id,
        officer_name=officer_name,
        reason=reason,
        ai_recommendation=ai_recommendation,
        ai_followed=ai_followed,
    )
    
    if decision_id is None:
        logger.warning(f"Duplicate decision blocked for {app_id}")
        return {
            "success": False,
            "message_hi": "यह निर्णय पहले से दर्ज है। डुप्लिकेट निर्णय अवरोधित।",
            "message_en": "Duplicate decision blocked.",
        }
    
    # Record audit event
    event_type = f"decision_{action}"
    db.add_audit_event(
        app_id=app_id,
        event_type=event_type,
        old_status=old_status,
        new_status=new_status,
        officer_id=officer_id,
        officer_name=officer_name,
        remarks=reason,
        ai_recommendation=ai_recommendation,
    )
    
    action_label = ACTION_LABELS_HI.get(action, action)
    return {
        "success": True,
        "message_hi": f"✅ आवेदन {app_id} सफलतापूर्वक '{action_label}' किया गया।",
        "message_en": f"Application {app_id} successfully marked as '{new_status}'.",
        "decision_id": decision_id,
    }


def get_application_decisions(app_id: str):
    """Get all decisions for an application."""
    return db.get_decisions_for_application(app_id)


def get_application_audit_trail(app_id: str):
    """Get the full audit trail for an application."""
    return db.get_audit_history(app_id)
