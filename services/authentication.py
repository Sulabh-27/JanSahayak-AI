"""
JanSahayak AI — Authentication Service
Simple demo-only officer login and session management.
"""
import streamlit as st
import config


def check_login() -> bool:
    """Check if the user is currently logged in."""
    return st.session_state.get("authenticated", False)


def get_officer_info() -> dict:
    """Get the currently logged-in officer's info."""
    if check_login():
        return {
            "officer_id": st.session_state.get("officer_id", config.DEMO_OFFICER_ID),
            "officer_name": st.session_state.get("officer_name", config.DEMO_OFFICER_NAME),
        }
    return {}


def login(username: str, password: str) -> bool:
    """
    Validate demo credentials and create session.
    Returns True if login is successful.
    """
    if username == config.DEMO_USERNAME and password == config.DEMO_PASSWORD:
        st.session_state["authenticated"] = True
        st.session_state["officer_id"] = config.DEMO_OFFICER_ID
        st.session_state["officer_name"] = config.DEMO_OFFICER_NAME
        st.session_state["username"] = username
        return True
    return False


def logout():
    """Clear session and log out."""
    keys_to_clear = ["authenticated", "officer_id", "officer_name", "username",
                     "selected_app", "ai_review_result", "confirm_action"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def render_login_page():
    """Render the login page UI."""
    _inject_login_css()
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="color: #1a237e; margin-bottom: 0.2rem; font-size: 2.2rem;">🏛️ जनसहायक AI</h1>
        <p style="color: #5c6bc0; font-size: 1.1rem; margin-bottom: 0.5rem;">आवेदन समीक्षा सहायक</p>
        <span style="background: #fff3e0; color: #e65100; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem;">
            🔶 डेमो वातावरण
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### 👤 अधिकारी लॉगिन")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("उपयोगकर्ता नाम / Username", placeholder="officer")
            password = st.text_input("पासवर्ड / Password", type="password", placeholder="••••••")
            
            submitted = st.form_submit_button("🔐 लॉगिन करें", use_container_width=True)
            
            if submitted:
                if login(username, password):
                    st.rerun()
                else:
                    st.error("❌ गलत उपयोगकर्ता नाम या पासवर्ड। कृपया पुनः प्रयास करें।")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem;">
            <p style="color: #9e9e9e; font-size: 0.8rem;">
                📋 डेमो क्रेडेंशियल्स: .env फ़ाइल में कॉन्फ़िगर किए गए हैं<br>
                ⚠️ यह प्रदर्शन उद्देश्य हेतु है — उत्पादन-स्तरीय प्रमाणीकरण नहीं है
            </p>
        </div>
        """, unsafe_allow_html=True)


def _inject_login_css():
    """Inject custom CSS for the login page."""
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
        }
        [data-testid="stForm"] {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(26, 35, 126, 0.08);
            border: 1px solid #e8eaf6;
        }
        .stButton > button {
            background: linear-gradient(135deg, #1a237e, #283593) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.5rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #283593, #3949ab) !important;
            box-shadow: 0 4px 12px rgba(26, 35, 126, 0.3) !important;
            transform: translateY(-1px) !important;
        }
    </style>
    """, unsafe_allow_html=True)
