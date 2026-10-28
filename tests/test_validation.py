"""
JanSahayak AI — Validation Tests
Tests for document completeness, missing documents, inconsistencies, and field validation.
"""
import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.validation import (
    validate_application,
    get_document_completeness,
    has_missing_documents,
    count_missing_documents,
)


# --- Fixtures ---

def _complete_app():
    """A fully complete application."""
    return {
        "application_id": "TEST-001",
        "applicant_name": "टेस्ट आवेदक",
        "father_name": "श्री टेस्ट पिता",
        "application_type": "आय प्रमाण पत्र",
        "submission_date": "2024-10-01",
        "last_updated": "2024-10-01",
        "status": "pending",
        "district": "भोपाल",
        "address": "टेस्ट पता",
        "contact": "98XX-XXX-000",
        "declared_annual_income": 150000,
        "income_source": "कृषि",
        "family_members": 4,
        "submitted_documents": '["identity_proof", "address_proof", "income_proof", "ration_card", "self_declaration", "bank_statement"]',
        "document_details": '{"identity_proof": {"type": "Aadhaar", "status": "submitted"}, "address_proof": {"type": "Bill", "status": "submitted"}, "income_proof": {"type": "Slip", "status": "submitted"}, "ration_card": {"type": "APL", "status": "submitted"}, "self_declaration": {"type": "Declaration", "status": "submitted"}, "bank_statement": {"type": "SBI", "status": "submitted"}}',
        "urgency": "normal",
        "secondary_income_record": None,
        "conflicting_dates": None,
        "review_notes": "",
    }


def _missing_docs_app():
    """Application missing income proof and bank statement."""
    app = _complete_app()
    app["application_id"] = "TEST-002"
    app["submitted_documents"] = '["identity_proof", "address_proof", "ration_card", "self_declaration"]'
    app["document_details"] = '{"identity_proof": {"type": "Aadhaar", "status": "submitted"}, "address_proof": {"type": "Bill", "status": "submitted"}, "ration_card": {"type": "APL", "status": "submitted"}, "self_declaration": {"type": "Declaration", "status": "submitted"}}'
    return app


def _inconsistent_income_app():
    """Application with income inconsistency."""
    app = _complete_app()
    app["application_id"] = "TEST-003"
    app["declared_annual_income"] = 250000
    app["secondary_income_record"] = 350000
    return app


def _empty_fields_app():
    """Application with missing required fields."""
    return {
        "application_id": "TEST-004",
        "applicant_name": "",
        "application_type": "आय प्रमाण पत्र",
        "submission_date": "2024-10-01",
        "last_updated": "2024-10-01",
        "status": "pending",
        "district": "",
        "address": "",
        "declared_annual_income": 0,
        "income_source": "",
        "family_members": 0,
        "submitted_documents": "[]",
        "document_details": "{}",
        "urgency": "normal",
        "secondary_income_record": None,
        "conflicting_dates": None,
    }


# --- Document Completeness Tests ---

class TestDocumentCompleteness:
    def test_complete_application(self):
        app = _complete_app()
        completeness = get_document_completeness(app)
        assert completeness["completeness_pct"] == 100
        assert len(completeness["missing"]) == 0
        assert completeness["submitted"] == completeness["total_required"]

    def test_missing_documents(self):
        app = _missing_docs_app()
        completeness = get_document_completeness(app)
        assert completeness["completeness_pct"] < 100
        assert "income_proof" in completeness["missing"]
        assert "bank_statement" in completeness["missing"]
        assert len(completeness["missing"]) == 2

    def test_has_missing_documents_true(self):
        app = _missing_docs_app()
        assert has_missing_documents(app) is True

    def test_has_missing_documents_false(self):
        app = _complete_app()
        assert has_missing_documents(app) is False

    def test_count_missing_documents(self):
        app = _missing_docs_app()
        assert count_missing_documents(app) == 2

    def test_all_missing_documents(self):
        app = _empty_fields_app()
        completeness = get_document_completeness(app)
        assert completeness["completeness_pct"] == 0
        assert completeness["submitted"] == 0
        assert len(completeness["missing"]) == 6

    def test_document_status_types(self):
        app = _complete_app()
        import json
        doc_details = json.loads(app["document_details"])
        doc_details["income_proof"]["status"] = "needs_verification"
        app["document_details"] = json.dumps(doc_details)
        
        completeness = get_document_completeness(app)
        income_doc = next(d for d in completeness["documents"] if d["id"] == "income_proof")
        assert income_doc["status"] == "needs_verification"


# --- Validation Finding Tests ---

class TestValidationFindings:
    def test_complete_app_no_errors(self):
        app = _complete_app()
        findings = validate_application(app)
        errors = [f for f in findings if f["severity"] == "error"]
        assert len(errors) == 0

    def test_missing_docs_generates_errors(self):
        app = _missing_docs_app()
        findings = validate_application(app)
        errors = [f for f in findings if f["severity"] == "error"]
        assert len(errors) == 2  # income_proof and bank_statement

    def test_income_inconsistency_warning(self):
        app = _inconsistent_income_app()
        findings = validate_application(app)
        warnings = [f for f in findings if f["severity"] == "warning" and "विसंगति" in f["finding_hi"]]
        assert len(warnings) >= 1

    def test_zero_income_warning(self):
        app = _empty_fields_app()
        # Set income to 0 explicitly
        app["declared_annual_income"] = 0
        findings = validate_application(app)
        income_warnings = [f for f in findings if "₹0" in f.get("finding_hi", "")]
        assert len(income_warnings) >= 1

    def test_empty_fields_warnings(self):
        app = _empty_fields_app()
        findings = validate_application(app)
        field_warnings = [f for f in findings if "फ़ील्ड खाली" in f.get("finding_hi", "")]
        assert len(field_warnings) >= 3  # applicant_name, district, address, income_source

    def test_conflicting_dates(self):
        app = _complete_app()
        app["conflicting_dates"] = '{"submission_date": "2024-10-06", "bank_statement_date": "2024-03-15", "issue": "बैंक विवरण 6 माह से अधिक पुराना है"}'
        findings = validate_application(app)
        date_warnings = [f for f in findings if "तिथि विसंगति" in f.get("finding_hi", "")]
        assert len(date_warnings) >= 1

    def test_needs_verification_finding(self):
        app = _complete_app()
        import json
        doc_details = json.loads(app["document_details"])
        doc_details["income_proof"]["status"] = "needs_verification"
        app["document_details"] = json.dumps(doc_details)
        
        findings = validate_application(app)
        verification_findings = [f for f in findings if "सत्यापन शेष" in f.get("finding_hi", "")]
        assert len(verification_findings) >= 1

    def test_finding_structure(self):
        app = _missing_docs_app()
        findings = validate_application(app)
        assert len(findings) > 0
        for f in findings:
            assert "severity" in f
            assert "finding_hi" in f
            assert "evidence" in f
            assert "recommendation_hi" in f
            assert f["severity"] in ("error", "warning", "info")
