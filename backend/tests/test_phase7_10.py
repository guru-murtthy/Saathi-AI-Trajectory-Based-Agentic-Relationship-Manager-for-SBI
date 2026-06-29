"""Tests for Future Graph, GPS, Community, and Agentic RM."""
from __future__ import annotations

from datetime import date

import pandas as pd

from app.data.generator import _rahul, _rahul_transactions, _rng
from app.engines.future_graph import project
from app.engines.gps import plan_goal
from app.features.pipeline import build_features


def _rahul_ctx():
    cust = _rahul()
    tx = pd.DataFrame(_rahul_transactions(_rng()))
    feats = build_features(cust, tx)
    return cust, tx, feats


def test_future_graph_projects_forward():
    cust, tx, feats = _rahul_ctx()
    res = project(cust, tx, feats, horizon_months=24)
    assert len(res["projection"]) == 24
    assert res["current_balance"] > 0


def test_gps_rahul_house_plan():
    plan = plan_goal(
        goal_kind="Buy House",
        target_amount=1_800_000,
        current_amount=300_000,
        target_date=date(2029, 6, 1),
        monthly_capacity=40000,
    )
    assert plan["gap"] == 1_500_000
    assert plan["required_monthly"] > 0
    assert sum(p["allocation_pct"] for p in plan["plan"]) == 100.0
    assert plan["feasibility"] is not None


def test_api_endpoints_and_metrics(monkeypatch):
    import pandas as pd
    from app.services import store
    from fastapi.testclient import TestClient
    from app.main import app
    from app.compliance.dpdp import ConsentStore
    import os
    
    # Mock list_customers to only return Rahul to speed up build_index in tests
    monkeypatch.setattr(store, "list_customers", lambda: pd.DataFrame([{
        "customer_id": "rahul",
        "name": "Rahul",
        "age": 28,
        "city": "Bangalore",
        "segment": "retail",
        "base_monthly_income": 65000.0,
        "opening_savings": 400000.0,
    }]))

    # Ensure active consent for testing
    ConsentStore.grant("rahul", "recommendation", "read")

    client = TestClient(app)
    
    # 1. Test FFI Endpoint (triggers timing log)
    res_ffi = client.get("/api/v1/customers/rahul/ffi")
    assert res_ffi.status_code == 200
    assert "ffi" in res_ffi.json()

    # 2. Test RM Chat Endpoint (triggers timing log)
    res_rm = client.post("/api/v1/customers/rahul/rm", json={"question": "What is the recommended product?"})
    assert res_rm.status_code == 200
    assert "narrative" in res_rm.json()

    # 3. Test Compliance Audit Endpoint
    res_audit = client.get("/api/v1/compliance/audit/rahul")
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert len(audit_data) > 0
    assert audit_data[0]["customer_id"] == "rahul"

    # 4. Test Feedback Endpoint
    res_fb = client.post("/api/v1/feedback", json={
        "customer_id": "rahul",
        "thumbs_up": True,
        "comment": "Outstanding, personalized recommendation!"
    })
    assert res_fb.status_code == 200
    assert res_fb.json()["status"] == "success"

    # Verify that log files were created
    perf_log = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "performance.log")
    feedback_log = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback.jsonl")
    
    assert os.path.exists(perf_log)
    assert os.path.exists(feedback_log)

