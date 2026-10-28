"""
JanSahayak AI — API Endpoints Tests
Tests for FastAPI REST API endpoints using TestClient.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
import config

client = TestClient(app)

class TestApiEndpoints:
    def test_health_check(self):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["version"] == "2.0.0"

    def test_login_success(self):
        res = client.post("/api/auth/login", json={
            "username": config.DEMO_USERNAME,
            "password": config.DEMO_PASSWORD
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "officer" in data
        assert data["officer"]["officer_name"] == config.DEMO_OFFICER_NAME

    def test_login_failure(self):
        res = client.post("/api/auth/login", json={
            "username": "wrong_officer",
            "password": "wrong_password"
        })
        assert res.status_code == 401

    def test_dashboard_stats(self):
        res = client.get("/api/dashboard/stats")
        assert res.status_code == 200
        data = res.json()
        assert "total_applications" in data
        assert "pending" in data
        assert "high_priority" in data
        assert "incomplete_documents" in data
        assert data["total_applications"] >= 20

    def test_applications_list(self):
        res = client.get("/api/applications")
        assert res.status_code == 200
        data = res.json()
        assert "count" in data
        assert "applications" in data
        assert data["count"] > 0
        
        # Verify augmented fields
        first = data["applications"][0]
        assert "priority" in first
        assert "doc_complete" in first
        assert "completeness_pct" in first
        assert "days_pending" in first

    def test_applications_search(self):
        res = client.get("/api/applications?search=राजकुमार")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 1
        assert "MP-INC-2024-0001" in [a["application_id"] for a in data["applications"]]

    def test_applications_filter_status(self):
        res = client.get("/api/applications?status=approved")
        assert res.status_code == 200
        data = res.json()
        for a in data["applications"]:
            assert a["status"] == "approved"

    def test_applications_filter_priority(self):
        res = client.get("/api/applications?priority=high")
        assert res.status_code == 200
        data = res.json()
        for a in data["applications"]:
            assert a["priority"]["level"] == "high"

    def test_application_detail(self):
        res = client.get("/api/applications/MP-INC-2024-0001")
        assert res.status_code == 200
        data = res.json()
        assert "application" in data
        assert "completeness" in data
        assert "findings" in data
        assert "priority" in data
        assert data["application"]["application_id"] == "MP-INC-2024-0001"

    def test_application_detail_not_found(self):
        res = client.get("/api/applications/INVALID-APP-999")
        assert res.status_code == 404

    def test_ai_review(self):
        res = client.post("/api/applications/MP-INC-2024-0001/ai-review")
        assert res.status_code == 200
        data = res.json()
        assert "review" in data
        assert "suggested_action" in data["review"]
        assert data["review"]["suggested_action"] in (
            "APPROVE", "REJECT", "RETURN_FOR_CORRECTION", "NEEDS_MANUAL_REVIEW"
        )

    def test_decision_without_reason_fails(self):
        res = client.post("/api/applications/MP-INC-2024-0001/decision", json={
            "action": "approve",
            "reason": ""
        })
        assert res.status_code == 422 or res.status_code == 400

    def test_audit_history(self):
        res = client.get("/api/audit-history")
        assert res.status_code == 200
        data = res.json()
        assert "history" in data
        assert isinstance(data["history"], list)

    def test_reseed_endpoint(self):
        res = client.post("/api/system/reseed")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["count"] >= 20
