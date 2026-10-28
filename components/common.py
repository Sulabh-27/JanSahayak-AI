"""
JanSahayak AI — Common UI Components
Shared CSS, styling, and reusable UI elements.
"""
import streamlit as st
import config


def inject_global_css():
    """Inject the global application CSS."""
    st.markdown("""
    <style>
        /* === Global Styles === */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            font-family: 'Noto Sans Devanagari', 'Inter', sans-serif;
        }
        
        /* === Sidebar === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1440 0%, #1a237e 50%, #1a2960 100%);
        }
        [data-testid="stSidebar"] * {
            color: #e8eaf6 !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: #c5cae9 !important;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.15) !important;
        }
        
        /* === Metric Cards === */
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            box-shadow: 0 2px 16px rgba(26, 35, 126, 0.06);
            border: 1px solid #e8eaf6;
            text-align: center;
            transition: all 0.3s ease;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 24px rgba(26, 35, 126, 0.12);
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 0.3rem;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #616161;
            font-weight: 500;
        }
        
        /* === Status Badges === */
        .status-badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        .status-pending { background: #fff3e0; color: #e65100; }
        .status-under_review { background: #e3f2fd; color: #1565c0; }
        .status-approved { background: #e8f5e9; color: #2e7d32; }
        .status-rejected { background: #fce4ec; color: #c62828; }
        .status-returned { background: #fff8e1; color: #f57f17; }
        
        /* === Priority Badges === */
        .priority-high { background: #fce4ec; color: #c62828; padding: 3px 12px; border-radius: 12px; font-size: 0.82rem; font-weight: 600; }
        .priority-medium { background: #fff3e0; color: #e65100; padding: 3px 12px; border-radius: 12px; font-size: 0.82rem; font-weight: 600; }
        .priority-low { background: #e8f5e9; color: #2e7d32; padding: 3px 12px; border-radius: 12px; font-size: 0.82rem; font-weight: 600; }
        
        /* === Section Headers === */
        .section-header {
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        /* === Cards === */
        .info-card {
            background: white;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
            border: 1px solid #e8eaf6;
            margin-bottom: 0.8rem;
        }
        
        /* === Demo Badge === */
        .demo-badge {
            background: #fff3e0;
            color: #e65100;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 500;
            display: inline-block;
            border: 1px solid #ffe0b2;
        }
        
        /* === Finding Severities === */
        .finding-error {
            border-left: 4px solid #c62828;
            background: #fce4ec;
            padding: 0.8rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 0.5rem;
        }
        .finding-warning {
            border-left: 4px solid #e65100;
            background: #fff3e0;
            padding: 0.8rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 0.5rem;
        }
        .finding-info {
            border-left: 4px solid #1565c0;
            background: #e3f2fd;
            padding: 0.8rem 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 0.5rem;
        }
        
        /* === AI Review Box === */
        .ai-review-box {
            background: linear-gradient(135deg, #f3e5f5 0%, #ede7f6 100%);
            border: 1px solid #ce93d8;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .ai-demo-banner {
            background: #fff8e1;
            border: 1px solid #ffcc80;
            border-radius: 12px;
            padding: 0.8rem 1.2rem;
            text-align: center;
            font-weight: 600;
            color: #e65100;
            margin-bottom: 1rem;
        }
        
        /* === Document Status Icons === */
        .doc-submitted { color: #2e7d32; }
        .doc-missing { color: #c62828; }
        .doc-verification { color: #e65100; }
        .doc-verified { color: #1b5e20; }
        
        /* === Confirmation Dialog === */
        .confirm-box {
            background: #fffde7;
            border: 2px solid #ffd54f;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin: 1rem 0;
        }
        
        /* === Table Styles === */
        .dataframe {
            font-size: 0.9rem !important;
        }
        
        /* === Button Styles === */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px) !important;
        }
        
        /* === Scrollbar === */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f5f5f5;
        }
        ::-webkit-scrollbar-thumb {
            background: #bdbdbd;
            border-radius: 3px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header(officer_name: str):
    """Render the app header with branding and officer info."""
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        st.markdown("""
        <div style="padding: 0.3rem 0;">
            <span style="font-size: 1.8rem; font-weight: 700; color: #1a237e;">🏛️ जनसहायक AI</span>
            <br>
            <span style="color: #5c6bc0; font-size: 0.95rem;">आवेदन समीक्षा सहायक</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 0.5rem;">
            <span class="demo-badge">🔶 डेमो वातावरण — प्रदर्शन प्रोटोटाइप</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 0.3rem;">
            <span style="color: #424242; font-size: 0.9rem;">👤 {officer_name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")


def render_metric_card(label: str, value, color: str = "#1a237e", icon: str = ""):
    """Render a single metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{icon} {value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Return HTML for a status badge."""
    label = config.STATUS_LABELS_HI.get(status, status)
    css_class = f"status-{status}"
    return f'<span class="status-badge {css_class}">{label}</span>'


def render_priority_badge(level: str, level_hi: str) -> str:
    """Return HTML for a priority badge."""
    return f'<span class="priority-{level}">{level_hi}</span>'


def render_finding(finding: dict):
    """Render a validation finding with severity styling."""
    severity = finding.get("severity", "info")
    css_class = f"finding-{severity}"
    icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
    severity_hi = {"error": "त्रुटि", "warning": "चेतावनी", "info": "सूचना"}.get(severity, "सूचना")
    
    st.markdown(f"""
    <div class="{css_class}">
        <strong>{icon} {severity_hi}:</strong> {finding['finding_hi']}<br>
        <span style="font-size: 0.85rem; color: #616161;">
            📎 {finding.get('evidence', '')}<br>
            💡 {finding.get('recommendation_hi', '')}
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(message: str):
    """Render an empty state message."""
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: #9e9e9e;">
        <span style="font-size: 3rem;">📭</span>
        <p style="font-size: 1.1rem; margin-top: 0.5rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
