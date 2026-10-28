"""
JanSahayak AI — Configuration
Central configuration for the application.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Application ---
APP_NAME = "JanSahayak AI"
APP_NAME_HI = "जनसहायक AI"
APP_TAGLINE_HI = "आवेदन समीक्षा सहायक"
APP_VERSION = "1.0.0"
DEMO_BADGE = "🔶 डेमो वातावरण — यह एक प्रदर्शन प्रोटोटाइप है, आधिकारिक सरकारी सेवा नहीं"

# --- Database ---
DATABASE_PATH = os.getenv("DATABASE_PATH", "jansahayak.db")
SEED_DATA_PATH = os.getenv("SEED_DATA_PATH", "data/sample_applications.json")

# --- Authentication (Demo Only) ---
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "officer")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "jansahayak2024")
DEMO_OFFICER_NAME = os.getenv("DEMO_OFFICER_NAME", "श्री राजेश शर्मा")
DEMO_OFFICER_ID = os.getenv("DEMO_OFFICER_ID", "OFF-MP-001")

# --- Groq AI ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "30"))
GROQ_MAX_RETRIES = int(os.getenv("GROQ_MAX_RETRIES", "2"))

# --- Priority Scoring Weights ---
PRIORITY_WEIGHT_DAYS_PENDING = 2.0
PRIORITY_WEIGHT_MISSING_DOCS = 3.0
PRIORITY_WEIGHT_INCONSISTENCIES = 2.5
PRIORITY_WEIGHT_URGENCY = 1.5
PRIORITY_HIGH_THRESHOLD = 7.0
PRIORITY_MEDIUM_THRESHOLD = 4.0

# --- Document Requirements for Income Certificate ---
REQUIRED_DOCUMENTS = [
    {"id": "identity_proof", "name_hi": "पहचान प्रमाण (आधार/वोटर ID)", "name_en": "Identity Proof"},
    {"id": "address_proof", "name_hi": "पता प्रमाण", "name_en": "Address Proof"},
    {"id": "income_proof", "name_hi": "आय प्रमाण पत्र / वेतन पर्ची", "name_en": "Income Proof"},
    {"id": "ration_card", "name_hi": "राशन कार्ड", "name_en": "Ration Card"},
    {"id": "self_declaration", "name_hi": "स्व-घोषणा पत्र", "name_en": "Self Declaration"},
    {"id": "bank_statement", "name_hi": "बैंक विवरण (6 माह)", "name_en": "Bank Statement (6 months)"},
]

# --- Application Statuses ---
STATUS_PENDING = "pending"
STATUS_UNDER_REVIEW = "under_review"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_RETURNED = "returned_for_correction"

STATUS_LABELS_HI = {
    STATUS_PENDING: "लंबित",
    STATUS_UNDER_REVIEW: "समीक्षाधीन",
    STATUS_APPROVED: "स्वीकृत",
    STATUS_REJECTED: "अस्वीकृत",
    STATUS_RETURNED: "सुधार हेतु वापस",
}

STATUS_COLORS = {
    STATUS_PENDING: "#E67E22",
    STATUS_UNDER_REVIEW: "#3498DB",
    STATUS_APPROVED: "#27AE60",
    STATUS_REJECTED: "#E74C3C",
    STATUS_RETURNED: "#F39C12",
}
