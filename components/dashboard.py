"""
JanSahayak AI — Dashboard Component
Officer dashboard with summary cards, statistics, and navigation.
"""
import streamlit as st
from datetime import datetime

import config
from services import database as db
from services.prioritization import calculate_priority, get_priority_counts
from services.validation import has_missing_documents
from components.common import render_metric_card, render_empty_state


def render_dashboard():
    """Render the main officer dashboard."""
    
    # Summary Cards
    stats = db.get_dashboard_stats()
    all_apps = db.get_all_applications()
    
    # Calculate additional metrics
    pending_apps = [a for a in all_apps if a["status"] in (config.STATUS_PENDING, config.STATUS_UNDER_REVIEW)]
    priority_counts = get_priority_counts(pending_apps) if pending_apps else {"high": 0, "medium": 0, "low": 0}
    incomplete_docs = sum(1 for a in pending_apps if has_missing_documents(a))
    
    st.markdown('<div class="section-header">📊 डैशबोर्ड — सारांश</div>', unsafe_allow_html=True)
    
    # Metric Cards Row
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        render_metric_card("कुल आवेदन", stats["total"], "#1a237e", "📋")
    with c2:
        render_metric_card("समीक्षा हेतु लंबित", stats["pending"], "#E67E22", "⏳")
    with c3:
        render_metric_card("उच्च प्राथमिकता", priority_counts["high"], "#c62828", "🔴")
    with c4:
        render_metric_card("दस्तावेज़ अधूरे", incomplete_docs, "#F39C12", "📄")
    with c5:
        render_metric_card("निर्णय की प्रतीक्षा", stats["pending"], "#3498DB", "⚖️")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Status breakdown
    st.markdown('<div class="section-header">📈 स्थिति विवरण</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("स्वीकृत", stats["approved"], "#27AE60", "✅")
    with col2:
        render_metric_card("अस्वीकृत", stats["rejected"], "#E74C3C", "❌")
    with col3:
        render_metric_card("सुधार हेतु वापस", stats["returned"], "#F39C12", "🔄")
    with col4:
        render_metric_card("प्राथमिकता वितरण",
                          f"🔴{priority_counts['high']} 🟡{priority_counts['medium']} 🟢{priority_counts['low']}",
                          "#424242")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown('<div class="section-header">⚡ त्वरित कार्रवाई</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if priority_counts["high"] > 0:
            st.warning(f"🔴 {priority_counts['high']} उच्च प्राथमिकता आवेदन शीघ्र समीक्षा की प्रतीक्षा में हैं")
        else:
            st.success("✅ कोई उच्च प्राथमिकता आवेदन नहीं")
    
    with col2:
        if incomplete_docs > 0:
            st.warning(f"📄 {incomplete_docs} आवेदनों में दस्तावेज़ अधूरे हैं")
        else:
            st.success("✅ सभी लंबित आवेदनों में दस्तावेज़ पूर्ण हैं")
    
    with col3:
        # Check for old applications
        old_apps = 0
        for a in pending_apps:
            try:
                sub_date = datetime.strptime(a.get("submission_date", ""), "%Y-%m-%d")
                if (datetime.now() - sub_date).days > 14:
                    old_apps += 1
            except (ValueError, TypeError):
                pass
        
        if old_apps > 0:
            st.warning(f"⏰ {old_apps} आवेदन 14 दिनों से अधिक समय से लंबित हैं")
        else:
            st.success("✅ कोई पुराना लंबित आवेदन नहीं")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent Activity
    st.markdown('<div class="section-header">🕐 हालिया गतिविधि</div>', unsafe_allow_html=True)
    
    audit_events = db.get_all_audit_history()
    if audit_events:
        for event in audit_events[:5]:
            action_icon = {"decision_approve": "✅", "decision_reject": "❌", "decision_return": "🔄"}.get(
                event["event_type"], "📝"
            )
            status_hi = config.STATUS_LABELS_HI.get(event.get("new_status", ""), event.get("new_status", ""))
            st.markdown(f"""
            <div class="info-card" style="padding: 0.8rem 1.2rem;">
                {action_icon} <strong>{event.get('application_id', '')}</strong> — 
                {status_hi} — 
                <span style="color: #757575; font-size: 0.85rem;">
                    {event.get('officer_name', '')} | {event.get('created_at', '')}
                </span>
                {f"<br><span style='color: #616161; font-size: 0.85rem;'>💬 {event.get('remarks', '')}</span>" if event.get('remarks') else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 अभी तक कोई गतिविधि दर्ज नहीं हुई है। आवेदनों की समीक्षा शुरू करें।")
