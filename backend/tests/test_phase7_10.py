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
