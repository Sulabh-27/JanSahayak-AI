"""
JanSahayak AI — Application Review Component
Detailed application review workspace with AI review and decision actions.
"""
import json
import streamlit as st
from datetime import datetime

import config
from services import database as db
from services.validation import validate_application, get_document_completeness
from services.prioritization import calculate_priority
from services.ai_review import perform_ai_review, is_ai_available
from services.decisions import process_decision, get_application_audit_trail
from services.authentication import get_officer_info
from components.common import (
    render_status_badge, render_priority_badge, render_finding,
    render_empty_state
)


def render_application_review():
    """Render the full application review workspace."""
    
    app_id = st.session_state.get("selected_app")
    
    if not app_id:
        render_empty_state("कोई आवेदन चयनित नहीं है। कृपया 'लंबित आवेदन' से एक आवेदन खोलें।")
        if st.button("← लंबित आवेदन पर वापस जाएं"):
            st.session_state["page"] = "applications"
            st.rerun()
        return
    
    app = db.get_application_by_id(app_id)
    
    if not app:
        st.error(f"❌ आवेदन '{app_id}' नहीं मिला")
        if st.button("← वापस जाएं"):
            st.session_state["page"] = "applications"
            st.rerun()
        return
    
    # Back button
    if st.button("← आवेदन सूची पर वापस जाएं"):
        st.session_state["selected_app"] = None
        st.session_state.pop("ai_review_result", None)
        st.session_state.pop("confirm_action", None)
        st.session_state["page"] = "applications"
        st.rerun()
    
    # Compute validation and priority
    findings = validate_application(app)
    completeness = get_document_completeness(app)
    priority = calculate_priority(app)
    
    # Header
    st.markdown(f"""
    <div class="section-header">
        📋 आवेदन समीक्षा — {app_id}
        &nbsp;&nbsp;{render_status_badge(app['status'])}
        &nbsp;&nbsp;{render_priority_badge(priority['level'], priority['level_hi'])}
    </div>
    """, unsafe_allow_html=True)
    
    # === Section A: Application Details ===
    _render_application_details(app, priority)
    
    # === Section B: Document Checklist ===
    _render_document_checklist(completeness)
    
    # === Section C: Validation Findings ===
    _render_validation_findings(findings)
    
    # === Section D: AI Review ===
    _render_ai_review_section(app, findings, completeness)
    
    # === Section E: Decision Actions ===
    _render_decision_section(app, findings)
    
    # === Audit History ===
    _render_audit_history(app_id)


def _render_application_details(app: dict, priority: dict):
    """Render application details section."""
    st.markdown("### 📝 आवेदन विवरण")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <strong>आवेदन ID:</strong> {app.get('application_id', 'N/A')}<br>
            <strong>आवेदक:</strong> {app.get('applicant_name', 'N/A')} ({app.get('applicant_name_en', '')})<br>
            <strong>पिता का नाम:</strong> {app.get('father_name', 'N/A')}<br>
            <strong>आवेदन प्रकार:</strong> {app.get('application_type', 'N/A')}<br>
            <strong>जमा तिथि:</strong> {app.get('submission_date', 'N/A')}<br>
            <strong>अंतिम अपडेट:</strong> {app.get('last_updated', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        income = app.get('declared_annual_income', 0)
        secondary = app.get('secondary_income_record')
        secondary_text = f"<br><strong>द्वितीयक आय रिकॉर्ड:</strong> <span style='color: #c62828;'>₹{secondary:,.0f}</span>" if secondary else ""
        
        st.markdown(f"""
        <div class="info-card">
            <strong>जिला:</strong> {app.get('district', 'N/A')} ({app.get('district_en', '')})<br>
            <strong>पता:</strong> {app.get('address', 'N/A')}<br>
            <strong>संपर्क:</strong> {app.get('contact', 'N/A')}<br>
            <strong>घोषित वार्षिक आय:</strong> ₹{income:,.0f}<br>
            <strong>आय स्रोत:</strong> {app.get('income_source', 'N/A')}<br>
            <strong>परिवार के सदस्य:</strong> {app.get('family_members', 'N/A')}
            {secondary_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Priority explanation
    if priority["reasons_hi"]:
        reasons_text = " • ".join(priority["reasons_hi"])
        level_color = {"high": "#c62828", "medium": "#e65100", "low": "#2e7d32"}.get(priority["level"], "#757575")
        st.markdown(f"""
        <div class="info-card" style="border-left: 4px solid {level_color};">
            <strong>🎯 प्राथमिकता:</strong> {render_priority_badge(priority['level'], priority['level_hi'])}
            &nbsp;(स्कोर: {priority['score']})<br>
            <span style="font-size: 0.9rem; color: #616161;">📌 {reasons_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Review notes
    notes = app.get("review_notes", "")
    if notes:
        st.markdown(f"""
        <div class="info-card" style="border-left: 4px solid #5c6bc0;">
            <strong>📝 समीक्षा टिप्पणी:</strong><br>{notes}
        </div>
        """, unsafe_allow_html=True)


def _render_document_checklist(completeness: dict):
    """Render the document checklist section."""
    st.markdown("### 📄 दस्तावेज़ सत्यापन चेकलिस्ट")
    
    pct = completeness["completeness_pct"]
    color = "#2e7d32" if pct == 100 else "#e65100" if pct >= 50 else "#c62828"
    
    st.markdown(f"""
    <div class="info-card">
        <strong>दस्तावेज़ पूर्णता:</strong> 
        <span style="font-size: 1.3rem; font-weight: 700; color: {color};">{pct}%</span>
        ({completeness['submitted']}/{completeness['total_required']} प्रस्तुत)
    </div>
    """, unsafe_allow_html=True)
    
    # Document list
    for doc in completeness["documents"]:
        status = doc["status"]
        if status == "verified":
            icon = "✅"
            label = "सत्यापित"
            color = "#2e7d32"
        elif status == "submitted":
            icon = "📎"
            label = "प्रस्तुत"
            color = "#1565c0"
        elif status == "needs_verification":
            icon = "⚠️"
            label = "सत्यापन शेष"
            color = "#e65100"
        else:
            icon = "❌"
            label = "गायब"
            color = "#c62828"
        
        detail_info = ""
        if doc["detail"]:
            d = doc["detail"]
            detail_info = f" — {d.get('type', '')} ({d.get('doc_number', '')})"
        
        st.markdown(f"""
        <div style="padding: 0.4rem 0.8rem; border-bottom: 1px solid #f5f5f5;">
            {icon} <strong>{doc['name_hi']}</strong> 
            <span style="color: {color}; font-size: 0.85rem;">({label})</span>
            <span style="color: #9e9e9e; font-size: 0.8rem;">{detail_info}</span>
        </div>
        """, unsafe_allow_html=True)


def _render_validation_findings(findings: list):
    """Render the validation findings section."""
    st.markdown("### 🔍 सत्यापन निष्कर्ष")
    
    if not findings:
        st.success("✅ कोई विशेष निष्कर्ष नहीं — सभी नियम-आधारित जांच पास")
        return
    
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    infos = [f for f in findings if f["severity"] == "info"]
    
    st.markdown(f"**कुल निष्कर्ष: {len(findings)}** (❌ {len(errors)} त्रुटि, ⚠️ {len(warnings)} चेतावनी, ℹ️ {len(infos)} सूचना)")
    
    for finding in findings:
        render_finding(finding)


def _render_ai_review_section(app: dict, findings: list, completeness: dict):
    """Render the AI-assisted review section."""
    st.markdown("### 🤖 AI समीक्षा")
    
    # Show AI availability status
    if is_ai_available():
        st.info("🟢 Groq AI उपलब्ध — लाइव AI समीक्षा संभव है")
    else:
        st.warning("🟡 Groq API Key कॉन्फ़िगर नहीं है — डेमो समीक्षा मोड सक्रिय")
    
    # AI Review Button
    if st.button("🤖 AI से आवेदन की समीक्षा करें", use_container_width=True, type="primary"):
        with st.spinner("🔄 AI समीक्षा प्रगति पर है..."):
            result = perform_ai_review(app)
            st.session_state["ai_review_result"] = result
    
    # Display AI Review Result
    ai_result = st.session_state.get("ai_review_result")
    if ai_result:
        _display_ai_review(ai_result)


def _display_ai_review(ai_result: dict):
    """Display the AI review result in a structured format."""
    review = ai_result.get("review", {})
    is_demo = ai_result.get("is_demo", True)
    error = ai_result.get("error")
    
    # Demo banner
    if is_demo:
        st.markdown("""
        <div class="ai-demo-banner">
            🔶 डेमो समीक्षा — लाइव AI विश्लेषण नहीं<br>
            <span style="font-size: 0.8rem; font-weight: 400;">यह समीक्षा नियम-आधारित जांच पर आधारित है, वास्तविक AI मॉडल से नहीं</span>
        </div>
        """, unsafe_allow_html=True)
    
    if error:
        st.error(f"⚠️ AI सेवा त्रुटि: {error} — डेमो समीक्षा प्रदर्शित है")
    
    st.markdown('<div class="ai-review-box">', unsafe_allow_html=True)
    
    # Summary
    st.markdown(f"#### 📋 सारांश")
    st.markdown(f"> {review.get('summary_hi', 'सारांश उपलब्ध नहीं')}")
    
    # Missing Documents
    missing = review.get("missing_documents", [])
    if missing:
        st.markdown("#### ❌ गायब दस्तावेज़")
        for doc in missing:
            st.markdown(f"- 📄 {doc}")
    
    # Inconsistencies
    inconsistencies = review.get("inconsistencies", [])
    if inconsistencies:
        st.markdown("#### ⚠️ विसंगतियां")
        for inc in inconsistencies:
            st.markdown(f"- ⚠️ {inc}")
    
    # Suggested Action
    action = review.get("suggested_action", "NEEDS_MANUAL_REVIEW")
    action_labels = {
        "APPROVE": ("✅ स्वीकृति की सिफारिश", "#2e7d32"),
        "REJECT": ("❌ अस्वीकृति की सिफारिश", "#c62828"),
        "RETURN_FOR_CORRECTION": ("🔄 सुधार हेतु वापसी की सिफारिश", "#e65100"),
        "NEEDS_MANUAL_REVIEW": ("🔍 मैन्युअल समीक्षा आवश्यक", "#5c6bc0"),
    }
    label, color = action_labels.get(action, ("🔍 अनिश्चित", "#757575"))
    
    st.markdown(f"""
    <div style="background: white; border: 2px solid {color}; border-radius: 12px; padding: 1rem; text-align: center; margin: 0.5rem 0;">
        <span style="font-size: 1.2rem; font-weight: 700; color: {color};">{label}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Reasons
    reasons = review.get("reasons_hi", [])
    if reasons:
        st.markdown("#### 📌 कारण एवं साक्ष्य")
        for r in reasons:
            st.markdown(f"- {r}")
    
    # Confidence
    confidence = review.get("confidence", "")
    if confidence:
        conf_colors = {"उच्च": "#2e7d32", "मध्यम": "#e65100", "निम्न": "#c62828"}
        conf_color = conf_colors.get(confidence, "#757575")
        st.markdown(f"**विश्वास स्तर:** <span style='color: {conf_color}; font-weight: 600;'>{confidence}</span>",
                    unsafe_allow_html=True)
    
    # Uncertainty
    uncertainty = review.get("uncertainty_hi", "")
    if uncertainty:
        st.markdown(f"#### ⚠️ सीमाएं एवं अनिश्चितता")
        st.markdown(f"> {uncertainty}")
    
    # Evidence
    evidence = review.get("evidence", [])
    if evidence:
        with st.expander("🔎 विस्तृत साक्ष्य (तकनीकी विवरण)"):
            for ev in evidence:
                st.code(ev, language=None)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Disclaimer
    st.caption("⚠️ यह AI सिफारिश है, अंतिम निर्णय नहीं। अधिकारी को स्वयं निर्णय लेना होगा।")


def _render_decision_section(app: dict, findings: list):
    """Render the decision action section."""
    status = app["status"]
    
    # Only show decision buttons for actionable statuses
    if status not in (config.STATUS_PENDING, config.STATUS_UNDER_REVIEW, config.STATUS_RETURNED):
        st.markdown(f"""
        <div class="info-card" style="text-align: center; border-left: 4px solid {config.STATUS_COLORS.get(status, '#757575')};">
            <strong>इस आवेदन पर पहले ही निर्णय लिया जा चुका है: {render_status_badge(status)}</strong>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("### ⚖️ अधिकारी का निर्णय")
    st.markdown("*कृपया अपना निर्णय दर्ज करें। कारण/टिप्पणी अनिवार्य है।*")
    
    officer = get_officer_info()
    
    # Get AI recommendation if available
    ai_result = st.session_state.get("ai_review_result")
    ai_recommendation = None
    if ai_result and ai_result.get("review"):
        ai_recommendation = ai_result["review"].get("suggested_action")
    
    # Officer remarks
    reason = st.text_area(
        "📝 कारण / टिप्पणी (अनिवार्य)",
        placeholder="अपना निर्णय का कारण या टिप्पणी यहां लिखें...",
        key="decision_reason",
        height=100,
    )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ स्वीकृत करें", use_container_width=True, type="primary"):
            if not reason or not reason.strip():
                st.error("❌ कारण/टिप्पणी अनिवार्य है")
            else:
                st.session_state["confirm_action"] = {
                    "action": "approve",
                    "action_hi": "स्वीकृत",
                    "reason": reason,
                    "ai_recommendation": ai_recommendation,
                }
    
    with col2:
        if st.button("❌ अस्वीकृत करें", use_container_width=True):
            if not reason or not reason.strip():
                st.error("❌ अस्वीकृति हेतु कारण अनिवार्य है")
            else:
                st.session_state["confirm_action"] = {
                    "action": "reject",
                    "action_hi": "अस्वीकृत",
                    "reason": reason,
                    "ai_recommendation": ai_recommendation,
                }
    
    with col3:
        if st.button("🔄 सुधार हेतु वापस करें", use_container_width=True):
            if not reason or not reason.strip():
                st.error("❌ सुधार विवरण अनिवार्य है")
            else:
                st.session_state["confirm_action"] = {
                    "action": "return",
                    "action_hi": "सुधार हेतु वापस",
                    "reason": reason,
                    "ai_recommendation": ai_recommendation,
                }
    
    # Confirmation step
    confirm = st.session_state.get("confirm_action")
    if confirm:
        st.markdown(f"""
        <div class="confirm-box">
            <strong>⚠️ पुष्टि करें:</strong><br>
            क्या आप वाकई आवेदन <strong>{app['application_id']}</strong> को 
            <strong>'{confirm['action_hi']}'</strong> करना चाहते हैं?<br>
            <strong>कारण:</strong> {confirm['reason']}
        </div>
        """, unsafe_allow_html=True)
        
        # AI vs Officer comparison
        if confirm.get("ai_recommendation"):
            ai_action_labels = {
                "APPROVE": "स्वीकृति",
                "REJECT": "अस्वीकृति", 
                "RETURN_FOR_CORRECTION": "सुधार हेतु वापसी",
                "NEEDS_MANUAL_REVIEW": "मैन्युअल समीक्षा",
            }
            ai_label = ai_action_labels.get(confirm["ai_recommendation"], confirm["ai_recommendation"])
            officer_label = confirm["action_hi"]
            
            # Check if officer follows AI
            ai_action_map = {"APPROVE": "approve", "REJECT": "reject", "RETURN_FOR_CORRECTION": "return"}
            expected = ai_action_map.get(confirm["ai_recommendation"])
            if expected == confirm["action"]:
                st.info(f"🤝 अधिकारी का निर्णय AI सिफारिश ({ai_label}) के अनुरूप है")
            else:
                st.warning(f"🔀 अधिकारी का निर्णय ({officer_label}) AI सिफारिश ({ai_label}) से भिन्न है — यह अधिकारी का विवेकाधिकार है")
        
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✅ हां, पुष्टि करें", use_container_width=True, type="primary"):
                result = process_decision(
                    app_id=app["application_id"],
                    action=confirm["action"],
                    officer_id=officer["officer_id"],
                    officer_name=officer["officer_name"],
                    reason=confirm["reason"],
                    ai_recommendation=confirm.get("ai_recommendation"),
                )
                
                if result["success"]:
                    st.success(result["message_hi"])
                    st.session_state.pop("confirm_action", None)
                    st.session_state.pop("ai_review_result", None)
                    st.balloons()
                    import time
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(result["message_hi"])
        
        with cc2:
            if st.button("❌ रद्द करें", use_container_width=True):
                st.session_state.pop("confirm_action", None)
                st.rerun()


def _render_audit_history(app_id: str):
    """Render the audit history for an application."""
    st.markdown("### 📜 निर्णय इतिहास")
    
    history = get_application_audit_trail(app_id)
    
    if not history:
        st.info("📭 इस आवेदन का कोई इतिहास नहीं है")
        return
    
    for event in history:
        event_icons = {
            "decision_approve": "✅",
            "decision_reject": "❌",
            "decision_return": "🔄",
        }
        icon = event_icons.get(event["event_type"], "📝")
        
        old_status_hi = config.STATUS_LABELS_HI.get(event.get("old_status", ""), "—")
        new_status_hi = config.STATUS_LABELS_HI.get(event.get("new_status", ""), "—")
        
        ai_info = ""
        if event.get("ai_recommendation"):
            ai_labels = {
                "APPROVE": "स्वीकृति",
                "REJECT": "अस्वीकृति",
                "RETURN_FOR_CORRECTION": "सुधार हेतु वापसी",
                "NEEDS_MANUAL_REVIEW": "मैन्युअल समीक्षा",
            }
            ai_label = ai_labels.get(event["ai_recommendation"], event["ai_recommendation"])
            ai_info = f"<br>🤖 <strong>AI सिफारिश:</strong> {ai_label}"
        
        st.markdown(f"""
        <div class="info-card" style="border-left: 4px solid #5c6bc0;">
            {icon} <strong>{event.get('created_at', '')}</strong><br>
            📌 {old_status_hi} → <strong>{new_status_hi}</strong><br>
            👤 {event.get('officer_name', 'N/A')} ({event.get('officer_id', '')})<br>
            💬 {event.get('remarks', 'कोई टिप्पणी नहीं')}
            {ai_info}
        </div>
        """, unsafe_allow_html=True)
