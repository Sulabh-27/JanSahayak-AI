"""
JanSahayak AI — Application Table Component
Application list with search, filters, sorting, and navigation.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

import config
from services import database as db
from services.prioritization import calculate_priority, sort_applications_by_priority
from services.validation import has_missing_documents, get_document_completeness
from components.common import render_status_badge, render_priority_badge, render_empty_state


def render_application_table():
    """Render the applications table with filters and search."""
    
    st.markdown('<div class="section-header">📋 लंबित आवेदन — आवेदन सूची</div>', unsafe_allow_html=True)
    
    # --- Filters Row ---
    st.markdown("#### 🔍 खोज एवं फ़िल्टर")
    
    fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])
    
    with fc1:
        search_query = st.text_input(
            "🔎 आवेदन ID या आवेदक नाम खोजें",
            placeholder="MP-INC-2024-0001 या नाम टाइप करें...",
            key="search_apps"
        )
    
    with fc2:
        status_filter = st.selectbox(
            "📌 स्थिति",
            options=["सभी", "लंबित", "समीक्षाधीन", "स्वीकृत", "अस्वीकृत", "सुधार हेतु वापस"],
            key="status_filter"
        )
    
    with fc3:
        priority_filter = st.selectbox(
            "🎯 प्राथमिकता",
            options=["सभी", "उच्च", "मध्यम", "सामान्य"],
            key="priority_filter"
        )
    
    with fc4:
        doc_filter = st.selectbox(
            "📄 दस्तावेज़ स्थिति",
            options=["सभी", "दस्तावेज़ अधूरे", "दस्तावेज़ पूर्ण"],
            key="doc_filter"
        )
    
    # --- Get and process applications ---
    all_apps = db.get_all_applications()
    
    if not all_apps:
        render_empty_state("कोई आवेदन नहीं मिला। डेटाबेस में आवेदन लोड नहीं हुए हैं।")
        return
    
    # Add computed fields
    for app in all_apps:
        app["priority"] = calculate_priority(app)
        app["doc_complete"] = not has_missing_documents(app)
        completeness = get_document_completeness(app)
        app["completeness_pct"] = completeness["completeness_pct"]
        try:
            sub_date = datetime.strptime(app.get("submission_date", ""), "%Y-%m-%d")
            app["days_pending"] = (datetime.now() - sub_date).days
        except (ValueError, TypeError):
            app["days_pending"] = 0
    
    # --- Apply Filters ---
    filtered = all_apps
    
    # Search filter
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = [a for a in filtered if (
            q in a.get("application_id", "").lower() or
            q in a.get("applicant_name", "").lower() or
            q in a.get("applicant_name_en", "").lower()
        )]
    
    # Status filter
    status_map = {
        "लंबित": config.STATUS_PENDING,
        "समीक्षाधीन": config.STATUS_UNDER_REVIEW,
        "स्वीकृत": config.STATUS_APPROVED,
        "अस्वीकृत": config.STATUS_REJECTED,
        "सुधार हेतु वापस": config.STATUS_RETURNED,
    }
    if status_filter != "सभी":
        target_status = status_map.get(status_filter)
        if target_status:
            filtered = [a for a in filtered if a["status"] == target_status]
    
    # Priority filter
    priority_map = {"उच्च": "high", "मध्यम": "medium", "सामान्य": "low"}
    if priority_filter != "सभी":
        target_priority = priority_map.get(priority_filter)
        if target_priority:
            filtered = [a for a in filtered if a["priority"]["level"] == target_priority]
    
    # Document filter
    if doc_filter == "दस्तावेज़ अधूरे":
        filtered = [a for a in filtered if not a["doc_complete"]]
    elif doc_filter == "दस्तावेज़ पूर्ण":
        filtered = [a for a in filtered if a["doc_complete"]]
    
    # Sort by priority (highest first), then submission date (oldest first)
    filtered.sort(key=lambda a: (-a["priority"]["score"], a.get("submission_date", "")))
    
    # --- Display Results ---
    st.markdown(f"**कुल परिणाम: {len(filtered)} आवेदन**")
    
    if not filtered:
        render_empty_state("चयनित फ़िल्टर के लिए कोई आवेदन नहीं मिला")
        return
    
    # Render as interactive cards
    for i, app in enumerate(filtered):
        _render_app_row(app, i)


def _render_app_row(app: dict, index: int):
    """Render a single application as a row card."""
    priority = app["priority"]
    status = app["status"]
    status_hi = config.STATUS_LABELS_HI.get(status, status)
    
    # Color coding
    priority_colors = {"high": "#c62828", "medium": "#e65100", "low": "#2e7d32"}
    status_colors = config.STATUS_COLORS.get(status, "#757575")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 1.5, 1, 1, 1.2, 1, 1])
    
    with col1:
        st.markdown(f"**{app['application_id']}**")
        st.caption(f"📅 {app.get('submission_date', 'N/A')}")
    
    with col2:
        st.markdown(f"**{app['applicant_name']}**")
        st.caption(f"📍 {app.get('district', 'N/A')}")
    
    with col3:
        days = app.get("days_pending", 0)
        color = "#c62828" if days > 14 else "#e65100" if days > 7 else "#2e7d32"
        st.markdown(f"<span style='color: {color}; font-weight: 600;'>{days} दिन</span>", unsafe_allow_html=True)
    
    with col4:
        pct = app.get("completeness_pct", 0)
        color = "#2e7d32" if pct == 100 else "#e65100" if pct >= 50 else "#c62828"
        st.markdown(f"<span style='color: {color}; font-weight: 600;'>{pct}%</span>", unsafe_allow_html=True)
    
    with col5:
        st.markdown(render_priority_badge(priority["level"], priority["level_hi"]), unsafe_allow_html=True)
    
    with col6:
        st.markdown(render_status_badge(status), unsafe_allow_html=True)
    
    with col7:
        if st.button("📂 खोलें", key=f"open_app_{app['application_id']}_{index}"):
            st.session_state["selected_app"] = app["application_id"]
            st.session_state["page"] = "review"
            st.rerun()
    
    st.markdown("<hr style='margin: 0.3rem 0; border-color: #e8eaf6;'>", unsafe_allow_html=True)
