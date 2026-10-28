"""
JanSahayak AI — जनसहायक AI
AI-assisted Government Application Review System
Main application entry point.

This is a demonstration prototype, NOT an official government service.
"""
import streamlit as st
import logging

import config
from services import database as db
from services.authentication import check_login, get_officer_info, logout, render_login_page
from components.common import inject_global_css, render_header
from components.dashboard import render_dashboard
from components.application_table import render_application_table
from components.application_review import render_application_review

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="JanSahayak AI — जनसहायक AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Initialize database on first run
    _init_app()
    
    # Check authentication
    if not check_login():
        render_login_page()
        return
    
    # Inject global CSS
    inject_global_css()
    
    # Get officer info
    officer = get_officer_info()
    
    # Render header
    render_header(officer["officer_name"])
    
    # Sidebar navigation
    _render_sidebar(officer)
    
    # Route to the correct page
    page = st.session_state.get("page", "dashboard")
    
    if page == "dashboard":
        render_dashboard()
    elif page == "applications":
        render_application_table()
    elif page == "review":
        render_application_review()
    elif page == "history":
        _render_history_page()
    elif page == "help":
        _render_help_page()


def _init_app():
    """Initialize the application: database and seed data."""
    if not st.session_state.get("_db_initialized"):
        try:
            db.init_db()
            db.seed_data()
            st.session_state["_db_initialized"] = True
            logger.info("Application initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            st.error(f"❌ एप्लिकेशन प्रारंभ करने में त्रुटि: {e}")


def _render_sidebar(officer: dict):
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <span style="font-size: 1.5rem; font-weight: 700;">🏛️ जनसहायक AI</span>
            <br>
            <span style="font-size: 0.85rem; opacity: 0.8;">आवेदन समीक्षा सहायक</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("#### 📍 नेविगेशन")
        
        pages = {
            "📊 डैशबोर्ड": "dashboard",
            "📋 लंबित आवेदन": "applications",
            "📜 समीक्षा इतिहास": "history",
            "❓ सहायता एवं जानकारी": "help",
        }
        
        current_page = st.session_state.get("page", "dashboard")
        
        for label, page_key in pages.items():
            if st.button(label, use_container_width=True,
                        key=f"nav_{page_key}",
                        type="primary" if current_page == page_key else "secondary"):
                st.session_state["page"] = page_key
                # Clear review state when navigating away
                if page_key != "review":
                    st.session_state.pop("selected_app", None)
                    st.session_state.pop("ai_review_result", None)
                    st.session_state.pop("confirm_action", None)
                st.rerun()
        
        st.markdown("---")
        
        # Officer info
        st.markdown(f"""
        <div style="padding: 0.5rem 0;">
            <span style="font-size: 0.85rem;">👤 {officer['officer_name']}</span><br>
            <span style="font-size: 0.75rem; opacity: 0.7;">{officer['officer_id']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 लॉगआउट", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        
        # Data reset (with confirmation)
        with st.expander("🔧 डेटा प्रबंधन"):
            st.caption("⚠️ यह डेमो डेटा को रीसेट करेगा")
            if st.button("🔄 डेमो डेटा रीसेट करें", key="reset_data"):
                st.session_state["confirm_reset"] = True
            
            if st.session_state.get("confirm_reset"):
                st.warning("⚠️ क्या आप वाकई सभी डेटा रीसेट करना चाहते हैं?")
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button("✅ हां", key="confirm_yes"):
                        db.seed_data(force_reseed=True)
                        st.session_state.pop("confirm_reset", None)
                        st.success("✅ डेटा सफलतापूर्वक रीसेट हो गया")
                        st.rerun()
                with rc2:
                    if st.button("❌ नहीं", key="confirm_no"):
                        st.session_state.pop("confirm_reset", None)
                        st.rerun()
        
        st.markdown("""
        <div style="text-align: center; padding-top: 1rem; opacity: 0.5; font-size: 0.7rem;">
            v1.0.0 | डेमो प्रोटोटाइप
        </div>
        """, unsafe_allow_html=True)


def _render_history_page():
    """Render the review history page."""
    st.markdown('<div class="section-header">📜 समीक्षा इतिहास — निर्णय लॉग</div>', unsafe_allow_html=True)
    
    all_history = db.get_all_audit_history()
    
    if not all_history:
        st.info("📭 अभी तक कोई निर्णय दर्ज नहीं हुआ है। आवेदनों की समीक्षा करें और निर्णय लें।")
        return
    
    st.markdown(f"**कुल इतिहास प्रविष्टियां: {len(all_history)}**")
    
    for event in all_history:
        event_icons = {
            "decision_approve": "✅",
            "decision_reject": "❌",
            "decision_return": "🔄",
        }
        icon = event_icons.get(event["event_type"], "📝")
        
        old_hi = config.STATUS_LABELS_HI.get(event.get("old_status", ""), "—")
        new_hi = config.STATUS_LABELS_HI.get(event.get("new_status", ""), "—")
        
        ai_info = ""
        if event.get("ai_recommendation"):
            ai_labels_map = {
                "APPROVE": "स्वीकृति", "REJECT": "अस्वीकृति",
                "RETURN_FOR_CORRECTION": "सुधार हेतु वापसी",
                "NEEDS_MANUAL_REVIEW": "मैन्युअल समीक्षा"
            }
            ai_info = f" | 🤖 AI: {ai_labels_map.get(event['ai_recommendation'], event['ai_recommendation'])}"
        
        st.markdown(f"""
        <div class="info-card">
            {icon} <strong>{event.get('application_id', '')}</strong> — 
            {old_hi} → <strong>{new_hi}</strong><br>
            <span style="color: #616161; font-size: 0.85rem;">
                👤 {event.get('officer_name', '')} | 🕐 {event.get('created_at', '')}{ai_info}
            </span><br>
            <span style="color: #424242; font-size: 0.9rem;">
                💬 {event.get('remarks', 'कोई टिप्पणी नहीं')}
            </span>
        </div>
        """, unsafe_allow_html=True)


def _render_help_page():
    """Render the help and information page."""
    st.markdown('<div class="section-header">❓ सहायता एवं जानकारी</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🏛️ जनसहायक AI — आवेदन समीक्षा सहायक
    
    यह एक **प्रदर्शन प्रोटोटाइप** है जो सरकारी अधिकारियों को आय प्रमाण पत्र आवेदनों की 
    समीक्षा में AI-सहायता प्रदान करता है।
    
    > ⚠️ **महत्वपूर्ण:** यह एक आधिकारिक सरकारी सेवा **नहीं** है। सभी डेटा काल्पनिक है।
    
    ---
    
    ### 📋 मुख्य सुविधाएं
    
    | सुविधा | विवरण |
    |--------|--------|
    | 📊 डैशबोर्ड | आवेदनों का सारांश और प्राथमिकता अवलोकन |
    | 📋 आवेदन सूची | खोज, फ़िल्टर और प्राथमिकता-क्रमित सूची |
    | 🔍 सत्यापन | नियम-आधारित दस्तावेज़ और डेटा जांच |
    | 🤖 AI समीक्षा | AI-सहायित आवेदन सारांश और सिफारिश |
    | ⚖️ निर्णय | स्वीकृत, अस्वीकृत, या सुधार हेतु वापस |
    | 📜 इतिहास | निर्णयों का ऑडिट ट्रेल |
    
    ---
    
    ### 🔒 सुरक्षा एवं गोपनीयता
    
    - सभी डेटा **काल्पनिक** है — कोई वास्तविक नागरिक जानकारी नहीं
    - डेमो प्रमाणीकरण — उत्पादन-स्तरीय सुरक्षा नहीं
    - API कुंजियां पर्यावरण चरों में संग्रहित
    
    ---
    
    ### 🤖 AI समीक्षा कैसे काम करती है
    
    1. **नियम-आधारित जांच** पहले चलती है (दस्तावेज़, आय विसंगति, तिथि)
    2. **AI मॉडल** (Groq API) आवेदन का सारांश और सिफारिश देता है
    3. AI सिफारिश **अंतिम निर्णय नहीं** है
    4. **अधिकारी** को स्वयं निर्णय लेना होता है
    5. API key न होने पर **डेमो मोड** सक्रिय होता है
    
    ---
    
    ### ⚖️ महत्वपूर्ण अस्वीकरण
    
    - यह सॉफ्टवेयर **प्रदर्शन प्रोटोटाइप** है
    - सत्यापन नियम **उदाहरणात्मक** हैं, आधिकारिक सरकारी पात्रता मानदंड नहीं
    - AI सिफारिशें **सहायक** हैं, निर्णायक नहीं
    - कोई भी डेटा **वास्तविक** नहीं है
    """)
    
    st.markdown("---")
    st.caption("JanSahayak AI v1.0.0 | Kenpath Full Stack AI Engineer Assignment | Built with Streamlit + Groq AI")


if __name__ == "__main__":
    main()
