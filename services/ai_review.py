"""
JanSahayak AI — AI Review Service
Groq LLM integration with structured output validation and demo fallback.
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from typing import List

import config
from services.validation import validate_application, get_document_completeness

logger = logging.getLogger(__name__)


# --- Pydantic Schema for AI Response ---

class AIReviewResponse(BaseModel):
    """Structured schema for AI review output."""
    summary_hi: str = Field(..., description="Concise Hindi summary of the application")
    missing_documents: List[str] = Field(default_factory=list, description="List of missing required documents")
    inconsistencies: List[str] = Field(default_factory=list, description="List of identified discrepancies")
    suggested_action: str = Field(..., description="APPROVE, REJECT, RETURN_FOR_CORRECTION, or NEEDS_MANUAL_REVIEW")
    reasons_hi: List[str] = Field(default_factory=list, description="Evidence-based explanations in Hindi")
    evidence: List[str] = Field(default_factory=list, description="References to available application fields")
    confidence: Optional[str] = Field(default=None, description="Calibrated confidence indicator")
    uncertainty_hi: str = Field(default="", description="Limitations or additional checks needed in Hindi")

    @field_validator("suggested_action")
    @classmethod
    def validate_action(cls, v):
        valid_actions = ["APPROVE", "REJECT", "RETURN_FOR_CORRECTION", "NEEDS_MANUAL_REVIEW"]
        if v.upper() not in valid_actions:
            return "NEEDS_MANUAL_REVIEW"
        return v.upper()


def is_ai_available() -> bool:
    """Check if Groq API key is configured."""
    return bool(config.GROQ_API_KEY and config.GROQ_API_KEY.strip())


def perform_ai_review(app: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform AI-assisted review of an application.
    Falls back to deterministic demo review if API key is missing or call fails.
    
    Returns a dict with:
      - review: the AIReviewResponse as dict
      - is_demo: True if demo fallback was used
      - error: error message if AI call failed
    """
    # Always run deterministic checks first
    findings = validate_application(app)
    completeness = get_document_completeness(app)
    
    if not is_ai_available():
        logger.info("No Groq API key — using demo fallback review")
        return {
            "review": _generate_demo_review(app, findings, completeness),
            "is_demo": True,
            "error": None,
        }
    
    # Try live AI review
    try:
        review = _call_groq_api(app, findings, completeness)
        return {
            "review": review,
            "is_demo": False,
            "error": None,
        }
    except Exception as e:
        logger.error(f"AI review failed: {e}")
        return {
            "review": _generate_demo_review(app, findings, completeness),
            "is_demo": True,
            "error": str(e),
        }


def _call_groq_api(app: Dict[str, Any], findings: list, completeness: dict) -> dict:
    """Call Groq API for AI review with structured output."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("Groq SDK not installed. Install with: pip install groq")
    
    client = Groq(api_key=config.GROQ_API_KEY)
    
    # Build minimal structured input for the LLM
    app_summary = _build_app_summary(app, findings, completeness)
    
    system_prompt = """आप एक सरकारी आवेदन समीक्षा सहायक AI हैं। आपको आय प्रमाण पत्र आवेदनों की समीक्षा में सहायता करनी है।

महत्वपूर्ण नियम:
1. आप केवल सहायक हैं — अंतिम निर्णय अधिकारी लेंगे
2. कोई तथ्य गढ़ें नहीं — केवल उपलब्ध जानकारी पर आधारित विश्लेषण करें
3. कोई सरकारी नीति या पात्रता मानदंड न बनाएं
4. किसी दस्तावेज़ की सामग्री का दावा न करें जो आपने नहीं देखा
5. अपर्याप्त साक्ष्य होने पर NEEDS_MANUAL_REVIEW सुझाएं
6. अस्वीकृति की सिफारिश केवल गायब जानकारी पर आधारित न करें

आपको निम्नलिखित JSON फॉर्मेट में उत्तर देना है:
{
    "summary_hi": "आवेदन का संक्षिप्त हिंदी सारांश",
    "missing_documents": ["गायब दस्तावेज़ की सूची"],
    "inconsistencies": ["पाई गई विसंगतियां"],
    "suggested_action": "APPROVE / REJECT / RETURN_FOR_CORRECTION / NEEDS_MANUAL_REVIEW",
    "reasons_hi": ["साक्ष्य-आधारित कारण हिंदी में"],
    "evidence": ["संदर्भित फील्ड और मान"],
    "confidence": "उच्च / मध्यम / निम्न",
    "uncertainty_hi": "सीमाएं या अतिरिक्त जांच"
}

केवल JSON दें, कोई अतिरिक्त टेक्स्ट नहीं।"""

    user_prompt = f"""निम्नलिखित आवेदन की समीक्षा करें:

{app_summary}

केवल ऊपर दिए गए JSON फॉर्मेट में उत्तर दें।"""

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=2000,
            timeout=config.GROQ_TIMEOUT,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean JSON if wrapped in markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
            content = content.strip()
        
        # Parse and validate
        try:
            parsed = json.loads(content)
            validated = AIReviewResponse(**parsed)
            return validated.model_dump()
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to parse AI response: {e}\nContent: {content[:500]}")
            raise RuntimeError(f"AI प्रतिक्रिया पार्स करने में त्रुटि: {e}")
    
    except Exception as e:
        if "timeout" in str(e).lower():
            raise RuntimeError("AI सेवा टाइमआउट — कृपया पुनः प्रयास करें")
        elif "rate" in str(e).lower():
            raise RuntimeError("API दर सीमा — कृपया कुछ समय बाद प्रयास करें")
        raise


def _build_app_summary(app: Dict[str, Any], findings: list, completeness: dict) -> str:
    """Build a minimal structured text summary for the LLM."""
    lines = [
        f"आवेदन ID: {app.get('application_id', 'N/A')}",
        f"आवेदक: {app.get('applicant_name', 'N/A')}",
        f"पिता: {app.get('father_name', 'N/A')}",
        f"आवेदन प्रकार: {app.get('application_type', 'N/A')}",
        f"जमा तिथि: {app.get('submission_date', 'N/A')}",
        f"स्थिति: {app.get('status', 'N/A')}",
        f"जिला: {app.get('district', 'N/A')}",
        f"पता: {app.get('address', 'N/A')}",
        f"घोषित वार्षिक आय: ₹{app.get('declared_annual_income', 0):,.0f}",
        f"आय स्रोत: {app.get('income_source', 'N/A')}",
        f"परिवार के सदस्य: {app.get('family_members', 'N/A')}",
        f"तत्कालता: {app.get('urgency', 'normal')}",
    ]
    
    # Secondary income
    secondary = app.get("secondary_income_record")
    if secondary:
        lines.append(f"द्वितीयक आय रिकॉर्ड: ₹{secondary:,.0f}")
    
    # Document completeness
    lines.append(f"\nदस्तावेज़ पूर्णता: {completeness['completeness_pct']}% ({completeness['submitted']}/{completeness['total_required']})")
    if completeness["missing_names_hi"]:
        lines.append(f"गायब दस्तावेज़: {', '.join(completeness['missing_names_hi'])}")
    
    # Validation findings
    if findings:
        lines.append("\nसत्यापन निष्कर्ष:")
        for f in findings:
            lines.append(f"  [{f['severity'].upper()}] {f['finding_hi']}")
    
    # Review notes
    notes = app.get("review_notes", "")
    if notes:
        lines.append(f"\nसमीक्षा टिप्पणी: {notes}")
    
    return "\n".join(lines)


def _generate_demo_review(app: Dict[str, Any], findings: list, completeness: dict) -> dict:
    """Generate a deterministic demo review based on validation findings."""
    missing_docs = completeness.get("missing_names_hi", [])
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    
    # Determine suggested action based on deterministic rules
    inconsistencies = [f["finding_hi"] for f in warnings if "विसंगति" in f["finding_hi"]]
    
    # Build evidence
    evidence = []
    for f in findings:
        evidence.append(f["evidence"])
    
    # Decision logic
    if len(errors) == 0 and len(warnings) == 0 and completeness["completeness_pct"] == 100:
        suggested_action = "APPROVE"
        confidence = "मध्यम"
        reasons_hi = [
            "सभी आवश्यक दस्तावेज़ प्रस्तुत किए गए हैं",
            "कोई विसंगति नहीं पाई गई",
            f"दस्तावेज़ पूर्णता: {completeness['completeness_pct']}%",
        ]
        uncertainty_hi = "यह डेमो समीक्षा है — दस्तावेज़ों की वास्तविक सामग्री की जांच नहीं की गई है। अधिकारी को भौतिक सत्यापन करना चाहिए।"
    elif len(missing_docs) > 0 and len(inconsistencies) == 0:
        suggested_action = "RETURN_FOR_CORRECTION"
        confidence = "मध्यम"
        reasons_hi = [
            f"{len(missing_docs)} आवश्यक दस्तावेज़ गायब {'हैं' if len(missing_docs) > 1 else 'है'}: {', '.join(missing_docs)}",
            "गायब दस्तावेज़ प्रस्तुत करने के बाद पुनर्विचार संभव है",
        ]
        uncertainty_hi = "यह डेमो समीक्षा है। गायब दस्तावेज़ों की सूची नियम-आधारित जांच पर आधारित है।"
    elif len(inconsistencies) > 0:
        suggested_action = "NEEDS_MANUAL_REVIEW"
        confidence = "निम्न"
        reasons_hi = [
            "विसंगतियां पाई गई हैं जिनकी मैन्युअल जांच आवश्यक है",
        ] + inconsistencies
        if missing_docs:
            reasons_hi.append(f"अतिरिक्त: {len(missing_docs)} दस्तावेज़ भी गायब {'हैं' if len(missing_docs) > 1 else 'है'}")
        uncertainty_hi = "विसंगतियों का कारण जानने हेतु आवेदक से स्पष्टीकरण आवश्यक है। यह डेमो समीक्षा है।"
    else:
        suggested_action = "NEEDS_MANUAL_REVIEW"
        confidence = "निम्न"
        reasons_hi = ["अपर्याप्त जानकारी — मैन्युअल समीक्षा आवश्यक"]
        for f in findings:
            reasons_hi.append(f["finding_hi"])
        uncertainty_hi = "उपलब्ध जानकारी के आधार पर स्पष्ट सिफारिश देना संभव नहीं है। यह डेमो समीक्षा है।"
    
    # Build summary
    applicant = app.get("applicant_name", "अज्ञात")
    district = app.get("district", "अज्ञात")
    income = app.get("declared_annual_income", 0)
    app_type = app.get("application_type", "आय प्रमाण पत्र")
    
    summary_hi = (
        f"{applicant}, जिला {district} से {app_type} हेतु आवेदन। "
        f"घोषित वार्षिक आय ₹{income:,.0f}। "
        f"दस्तावेज़ पूर्णता {completeness['completeness_pct']}%। "
        f"कुल {len(findings)} सत्यापन निष्कर्ष पाए गए।"
    )
    
    return {
        "summary_hi": summary_hi,
        "missing_documents": missing_docs,
        "inconsistencies": inconsistencies,
        "suggested_action": suggested_action,
        "reasons_hi": reasons_hi,
        "evidence": evidence,
        "confidence": confidence,
        "uncertainty_hi": uncertainty_hi,
    }
