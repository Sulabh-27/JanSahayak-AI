"""
JanSahayak AI — Authentication Service
Demo credentials validation and officer metadata.
"""
import config

def validate_credentials(username: str, password: str) -> bool:
    """Validate demo officer credentials."""
    return username == config.DEMO_USERNAME and password == config.DEMO_PASSWORD

def get_demo_officer_info() -> dict:
    """Return default demo officer profile."""
    return {
        "officer_id": config.DEMO_OFFICER_ID,
        "officer_name": config.DEMO_OFFICER_NAME,
        "role": "तहसीलदार / राजस्व अधिकारी",
        "department": "राजस्व एवं लोक सेवा प्रबंधन विभाग, मध्य प्रदेश"
    }
