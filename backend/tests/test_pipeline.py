"""Phase 8: Testing instructions - core engine tests.

Run:
    cd backend && pytest -q

These tests assert the Rahul demo story holds end to end so the SBI judge flow
never silently breaks.
"""
from __future__ import annotations

from app.data.generator import _rahul, _rahul_transactions, _rng
import pandas as pd

from app.engines.dna import compute_dna
from app.engines.ffi import compute_ffi
from app.engines.life_event_graph import predict_events
from app.features.pipeline import FEATURE_COLUMNS, build_features


def _rahul_features():
    cust = _rahul()
    tx = pd.DataFrame(_rahul_transactions(_rng()))
    return build_features(cust, tx)


def test_feature_vector_complete():
    f = _rahul_features()
    for col in FEATURE_COLUMNS:
        assert col in f, f"missing feature {col}"


def test_rahul_income_growth_positive():
    f = _rahul_features()
    assert f["income_growth_rate"] > 0
    assert f["has_regular_rent"] == 1.0


def test_rahul_home_buyer_dna_high():
    dna = compute_dna(_rahul_features())
    assert dna["home_buyer"]["score"] > 50


def test_rahul_home_purchase_top_event():
    events = predict_events(_rahul_features())
    top = events[0]
    assert top["event"] == "home_purchase"
    assert top["probability"] > 60
    assert top["signals"], "home_purchase must have explanation signals"


def test_rahul_ffi_in_range():
    res = compute_ffi(_rahul_features())
    assert 0 <= res["ffi"] <= 100
    assert res["sub_scores"]["home_ownership"] > 60
    assert res["top_drivers"]
