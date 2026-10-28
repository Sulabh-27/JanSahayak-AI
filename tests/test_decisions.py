"""
JanSahayak AI — Decisions Tests
Tests for approval, rejection, return actions, audit history, and edge cases.
"""
import sys
import os
import sqlite3
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from services import database as db
from services.decisions import process_decision
from services.ai_review import _generate_demo_review
from services.validation import validate_application, get_document_completeness


# --- Test Database Setup ---

@pytest.fixture(autouse=True)
def temp_database(tmp_path):
    """Use a temporary SQLite database for each test."""
    test_db = str(tmp_path / "test_jansahayak.db")
    original = db._DB_PATH
    db._DB_PATH = test_db
    db.init_db()
    _insert_test_application(test_db)
    yield test_db
    db._DB_PATH = original


def _insert_test_application(db_path):
    """Insert a test application into the database."""
    import json
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO applications (
            application_id, applicant_name, applicant_name_en, father_name,
            application_type, submission_date, last_updated, status,
            assigned_officer, district, address, contact,
            declared_annual_income, income_source, family_members,
            submitted_documents, document_details, review_notes, urgency,
            secondary_income_record, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "TEST-DEC-001", "टेस्ट आवेदक", "Test Applicant", "श्री टेस्ट",
        "आय प्रमाण पत्र", "2024-10-01", "2024-10-01", "pending",
        "OFF-TEST-001", "भोपाल", "टेस्ट पता", "98XX-XXX-000",
        150000, "कृषि", 4,
        json.dumps(["identity_proof", "address_proof", "income_proof", "ration_card", "self_declaration", "bank_statement"]),
        json.dumps({
            "identity_proof": {"type": "Aadhaar", "status": "submitted"},
            "address_proof": {"type": "Bill", "status": "submitted"},
            "income_proof": {"type": "Slip", "status": "submitted"},
            "ration_card": {"type": "APL", "status": "submitted"},
            "self_declaration": {"type": "Declaration", "status": "submitted"},
            "bank_statement": {"type": "SBI", "status": "submitted"},
        }),
        "", "normal", None, 1
    ))
    conn.commit()
    conn.close()


# --- Approval Tests ---

class TestApproval:
    def test_approve_with_reason(self):
        result = process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="सभी दस्तावेज़ सत्यापित, आवेदन उचित है"
        )
        assert result["success"] is True
        assert "सफलतापूर्वक" in result["message_hi"]
        
        # Verify status changed
        app = db.get_application_by_id("TEST-DEC-001")
        assert app["status"] == config.STATUS_APPROVED

    def test_approve_creates_audit_event(self):
        process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="टेस्ट कारण"
        )
        
        history = db.get_audit_history("TEST-DEC-001")
        assert len(history) >= 1
        assert history[0]["event_type"] == "decision_approve"
        assert history[0]["new_status"] == config.STATUS_APPROVED


# --- Rejection Tests ---

class TestRejection:
    def test_reject_without_reason_fails(self):
        result = process_decision(
            app_id="TEST-DEC-001",
            action="reject",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason=""
        )
        assert result["success"] is False
        assert "अनिवार्य" in result["message_hi"]

    def test_reject_with_reason(self):
        result = process_decision(
            app_id="TEST-DEC-001",
            action="reject",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="दस्तावेज़ अपर्याप्त हैं"
        )
        assert result["success"] is True
        
        app = db.get_application_by_id("TEST-DEC-001")
        assert app["status"] == config.STATUS_REJECTED


# --- Return for Corrections Tests ---

class TestReturnForCorrections:
    def test_return_with_remarks(self):
        result = process_decision(
            app_id="TEST-DEC-001",
            action="return",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="बैंक विवरण की नवीनतम प्रति प्रस्तुत करें"
        )
        assert result["success"] is True
        
        app = db.get_application_by_id("TEST-DEC-001")
        assert app["status"] == config.STATUS_RETURNED

    def test_return_without_reason_fails(self):
        result = process_decision(
            app_id="TEST-DEC-001",
            action="return",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="   "
        )
        assert result["success"] is False


# --- Audit History Tests ---

class TestAuditHistory:
    def test_audit_records_officer_info(self):
        process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="टेस्ट कारण"
        )
        
        history = db.get_audit_history("TEST-DEC-001")
        assert history[0]["officer_id"] == "OFF-TEST-001"
        assert history[0]["officer_name"] == "टेस्ट अधिकारी"
        assert history[0]["remarks"] == "टेस्ट कारण"

    def test_audit_records_ai_recommendation(self):
        process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="AI सिफारिश के अनुसार",
            ai_recommendation="APPROVE"
        )
        
        history = db.get_audit_history("TEST-DEC-001")
        assert history[0]["ai_recommendation"] == "APPROVE"


# --- Dashboard Metrics Tests ---

class TestDashboardMetrics:
    def test_metrics_after_approval(self):
        stats_before = db.get_dashboard_stats()
        pending_before = stats_before["pending"]
        
        process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="स्वीकृत"
        )
        
        stats_after = db.get_dashboard_stats()
        assert stats_after["approved"] == stats_before["approved"] + 1
        assert stats_after["pending"] == pending_before - 1


# --- Edge Cases ---

class TestDecisionEdgeCases:
    def test_invalid_action(self):
        result = process_decision(
            app_id="TEST-DEC-001",
            action="invalid_action",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="टेस्ट"
        )
        assert result["success"] is False

    def test_nonexistent_application(self):
        result = process_decision(
            app_id="DOES-NOT-EXIST",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="टेस्ट"
        )
        assert result["success"] is False

    def test_duplicate_status_blocked(self):
        # First approve
        process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="पहला स्वीकृति"
        )
        
        # Try to approve again
        result = process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="दूसरा स्वीकृति"
        )
        assert result["success"] is False

    def test_ai_followed_tracking(self):
        """Test that AI recommendation following is tracked."""
        result = process_decision(
            app_id="TEST-DEC-001",
            action="approve",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="AI अनुसार",
            ai_recommendation="APPROVE"
        )
        assert result["success"] is True
        
        decisions = db.get_decisions_for_application("TEST-DEC-001")
        assert len(decisions) >= 1
        assert decisions[0]["ai_recommendation_followed"] == 1

    def test_ai_overridden_tracking(self):
        """Test that AI override is tracked."""
        result = process_decision(
            app_id="TEST-DEC-001",
            action="reject",
            officer_id="OFF-TEST-001",
            officer_name="टेस्ट अधिकारी",
            reason="AI से असहमत",
            ai_recommendation="APPROVE"
        )
        assert result["success"] is True
        
        decisions = db.get_decisions_for_application("TEST-DEC-001")
        assert decisions[0]["ai_recommendation_followed"] == 0


# --- Demo Fallback Tests ---

class TestDemoFallback:
    def test_demo_review_complete_app(self):
        app = {
            "application_id": "DEMO-001",
            "applicant_name": "डेमो आवेदक",
            "application_type": "आय प्रमाण पत्र",
            "district": "भोपाल",
            "declared_annual_income": 150000,
            "submitted_documents": '["identity_proof", "address_proof", "income_proof", "ration_card", "self_declaration", "bank_statement"]',
            "document_details": '{"identity_proof": {"type": "Aadhaar", "status": "submitted"}, "address_proof": {"type": "Bill", "status": "submitted"}, "income_proof": {"type": "Slip", "status": "submitted"}, "ration_card": {"type": "APL", "status": "submitted"}, "self_declaration": {"type": "Declaration", "status": "submitted"}, "bank_statement": {"type": "SBI", "status": "submitted"}}',
            "status": "pending",
            "urgency": "normal",
            "secondary_income_record": None,
            "conflicting_dates": None,
            "submission_date": "2024-10-01",
        }
        findings = validate_application(app)
        completeness = get_document_completeness(app)
        review = _generate_demo_review(app, findings, completeness)
        
        assert "summary_hi" in review
        assert "suggested_action" in review
        assert review["suggested_action"] in ("APPROVE", "REJECT", "RETURN_FOR_CORRECTION", "NEEDS_MANUAL_REVIEW")
        assert "reasons_hi" in review
        assert len(review["reasons_hi"]) > 0

    def test_demo_review_incomplete_app(self):
        app = {
            "application_id": "DEMO-002",
            "applicant_name": "अधूरा आवेदक",
            "application_type": "आय प्रमाण पत्र",
            "district": "इंदौर",
            "declared_annual_income": 100000,
            "submitted_documents": '["identity_proof"]',
            "document_details": '{"identity_proof": {"type": "Aadhaar", "status": "submitted"}}',
            "status": "pending",
            "urgency": "normal",
            "secondary_income_record": None,
            "conflicting_dates": None,
            "submission_date": "2024-10-01",
        }
        findings = validate_application(app)
        completeness = get_document_completeness(app)
        review = _generate_demo_review(app, findings, completeness)
        
        assert review["suggested_action"] in ("RETURN_FOR_CORRECTION", "NEEDS_MANUAL_REVIEW")
        assert len(review["missing_documents"]) > 0

    def test_demo_review_invalid_llm_not_used(self):
        """Ensure demo review doesn't claim to be from a live LLM."""
        app = {
            "application_id": "DEMO-003",
            "applicant_name": "डेमो",
            "application_type": "आय प्रमाण पत्र",
            "district": "भोपाल",
            "declared_annual_income": 100000,
            "submitted_documents": "[]",
            "document_details": "{}",
            "status": "pending",
            "urgency": "normal",
            "secondary_income_record": None,
            "conflicting_dates": None,
            "submission_date": "2024-10-01",
        }
        findings = validate_application(app)
        completeness = get_document_completeness(app)
        review = _generate_demo_review(app, findings, completeness)
        
        # Ensure uncertainty mentions demo
        assert "डेमो" in review.get("uncertainty_hi", "")
