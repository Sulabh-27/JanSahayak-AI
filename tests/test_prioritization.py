"""
JanSahayak AI — Prioritization Tests
Tests for priority scoring, ordering, and explainability.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.prioritization import (
    calculate_priority,
    sort_applications_by_priority,
    get_priority_counts,
)


from datetime import datetime, timedelta


# --- Fixtures ---

def _base_app(**overrides):
    """Create a base application with overrides."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    app = {
        "application_id": "TEST-PRI-001",
        "applicant_name": "टेस्ट आवेदक",
        "application_type": "आय प्रमाण पत्र",
        "submission_date": today_str,
        "last_updated": today_str,
        "status": "pending",
        "district": "भोपाल",
        "address": "टेस्ट पता",
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
    app.update(overrides)
    return app


# --- Priority Scoring Tests ---

class TestPriorityScoring:
    def test_low_priority_complete_recent(self):
        app = _base_app()
        priority = calculate_priority(app)
        assert priority["level"] == "low"
        assert priority["score"] >= 0

    def test_high_urgency_increases_score(self):
        normal = _base_app(urgency="normal")
        high = _base_app(urgency="high")
        
        p_normal = calculate_priority(normal)
        p_high = calculate_priority(high)
        
        assert p_high["score"] > p_normal["score"]

    def test_missing_docs_increases_priority(self):
        complete = _base_app()
        incomplete = _base_app(
            submitted_documents='["identity_proof", "self_declaration"]',
            document_details='{"identity_proof": {"type": "Aadhaar", "status": "submitted"}, "self_declaration": {"type": "Declaration", "status": "submitted"}}'
        )
        
        p_complete = calculate_priority(complete)
        p_incomplete = calculate_priority(incomplete)
        
        assert p_incomplete["score"] > p_complete["score"]

    def test_old_application_increases_priority(self):
        recent_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        old_date = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d")
        recent = _base_app(submission_date=recent_date)
        old = _base_app(submission_date=old_date)
        
        p_recent = calculate_priority(recent)
        p_old = calculate_priority(old)
        
        assert p_old["score"] > p_recent["score"]

    def test_inconsistency_increases_priority(self):
        consistent = _base_app()
        inconsistent = _base_app(
            declared_annual_income=250000,
            secondary_income_record=400000,
        )
        
        p_consistent = calculate_priority(consistent)
        p_inconsistent = calculate_priority(inconsistent)
        
        assert p_inconsistent["score"] > p_consistent["score"]

    def test_priority_has_explanation(self):
        app = _base_app(urgency="high")
        priority = calculate_priority(app)
        assert len(priority["reasons_hi"]) > 0
        assert isinstance(priority["reasons_hi"], list)

    def test_priority_levels(self):
        app = _base_app()
        priority = calculate_priority(app)
        assert priority["level"] in ("high", "medium", "low")
        assert priority["level_hi"] in ("उच्च", "मध्यम", "सामान्य")

    def test_priority_factors_present(self):
        app = _base_app()
        priority = calculate_priority(app)
        assert "factors" in priority
        assert "days_pending" in priority["factors"]
        assert "missing_documents" in priority["factors"]
        assert "inconsistencies" in priority["factors"]
        assert "urgency" in priority["factors"]


# --- Sorting Tests ---

class TestPrioritySorting:
    def test_sort_by_priority(self):
        recent_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        old_date = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d")
        apps = [
            _base_app(application_id="LOW", urgency="normal", submission_date=recent_date),
            _base_app(application_id="HIGH", urgency="high", submission_date=old_date,
                      submitted_documents='["identity_proof"]',
                      document_details='{"identity_proof": {"type": "Aadhaar", "status": "submitted"}}'),
        ]
        
        sorted_apps = sort_applications_by_priority(apps)
        assert sorted_apps[0]["application_id"] == "HIGH"

    def test_priority_counts(self):
        apps = [
            _base_app(application_id="A1"),
            _base_app(application_id="A2"),
        ]
        counts = get_priority_counts(apps)
        assert isinstance(counts, dict)
        assert "high" in counts
        assert "medium" in counts
        assert "low" in counts


# --- Edge Cases ---

class TestPriorityEdgeCases:
    def test_empty_application(self):
        app = {
            "application_id": "EMPTY",
            "applicant_name": "",
            "application_type": "",
            "submission_date": "",
            "status": "pending",
            "submitted_documents": "[]",
            "document_details": "{}",
            "urgency": "normal",
            "declared_annual_income": None,
            "secondary_income_record": None,
            "conflicting_dates": None,
        }
        priority = calculate_priority(app)
        assert priority["score"] >= 0
        assert priority["level"] in ("high", "medium", "low")

    def test_invalid_date(self):
        app = _base_app(submission_date="invalid-date")
        priority = calculate_priority(app)
        assert priority["score"] >= 0
