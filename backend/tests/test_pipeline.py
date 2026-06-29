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


def test_consent_gate():
    from app.compliance.dpdp import ConsentStore
    from app.agent.rm import advise

    # 1. Assert default active consent (backward-compatible)
    assert ConsentStore.is_active("rahul", "recommendation") is True

    # 2. Revoke consent and assert it is blocked
    ConsentStore.revoke("rahul", "recommendation")
    assert ConsentStore.is_active("rahul", "recommendation") is False

    res = advise("rahul")
    assert "error" in res
    assert "Consent not active" in res["error"]
    assert "Obtain DPDP consent" in res["loop"]["recommend"]["action"]

    # 3. Grant consent back and assert recommendations work again
    ConsentStore.grant("rahul", "recommendation", "read")
    assert ConsentStore.is_active("rahul", "recommendation") is True
    res2 = advise("rahul")
    assert "error" not in res2


def test_datasource_adapter():
    from app.data.adapters.synthetic_datasource import SyntheticDataSource

    ds = SyntheticDataSource()
    tx = ds.get_transactions("rahul")
    assert not tx.empty

    bal = ds.get_balances("rahul")
    assert bal["opening_savings"] == 400000.0
    assert bal["current_savings"] > 0


def test_llm_fallback():
    import os
    from app.agent.llm import generate

    old_provider = os.getenv("SAATHI_LLM_PROVIDER", "offline")
    old_key = os.getenv("GEMINI_API_KEY")

    try:
        os.environ["SAATHI_LLM_PROVIDER"] = "gemini"
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

        res = generate("system prompt", "user query")
        assert "[offline fallback:" in res
        assert "user query" in res
    finally:
        os.environ["SAATHI_LLM_PROVIDER"] = old_provider
        if old_key is not None:
            os.environ["GEMINI_API_KEY"] = old_key

