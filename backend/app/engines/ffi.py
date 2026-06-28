"""Phase 6: Financial Future Index (FFI) - the central metric.

FFI is a 0-100 "credit score for the future" plus per-event sub-scores
(home ownership, marriage, investment readiness, business creation, travel).

The overall FFI is produced by a LightGBM regressor trained on synthetic data
(see app/ml/train_ffi.py). The per-event sub-scores come from the Life Event
Knowledge Graph so they stay fully explainable. If no trained model is present,
FFI falls back to a transparent heuristic so the demo never breaks.
"""
from __future__ import annotations

import json

import numpy as np

from app.config import FFI_META_PATH, FFI_MODEL_PATH
from app.engines.life_event_graph import predict_events
from app.features.pipeline import FEATURE_COLUMNS, features_to_vector

_model = None
_meta = None


def _load_model():
    global _model, _meta
    if _model is not None:
        return _model
    if FFI_MODEL_PATH.exists():
        import lightgbm as lgb

        _model = lgb.Booster(model_file=str(FFI_MODEL_PATH))
        if FFI_META_PATH.exists():
            _meta = json.loads(FFI_META_PATH.read_text())
    return _model


def _heuristic_ffi(features: dict) -> float:
    """Transparent fallback when no model is trained."""
    z = (
        50
        + 120 * features.get("savings_rate", 0)
        + 200 * features.get("savings_growth_rate", 0)
        + 200 * features.get("income_growth_rate", 0)
        + 60 * features.get("investment_ratio", 0)
        + 10 * features.get("income_regularity", 0)
        - 40 * features.get("expense_volatility", 0)
    )
    return float(np.clip(z, 0, 100))


def compute_ffi(features: dict) -> dict:
    """Compute the FFI plus explainable sub-scores."""
    model = _load_model()
    if model is not None:
        vec = features_to_vector(features).reshape(1, -1)
        score = float(np.clip(model.predict(vec)[0], 0, 100))
        source = "lightgbm"
    else:
        score = _heuristic_ffi(features)
        source = "heuristic"

    events = predict_events(features)
    sub_scores = {e["event"]: e["probability"] for e in events}

    # Top drivers via simple feature contribution for explainability.
    drivers = _top_drivers(features)

    return {
        "ffi": round(score, 1),
        "source": source,
        "sub_scores": {
            "home_ownership": sub_scores.get("home_purchase", 0),
            "marriage": sub_scores.get("marriage", 0),
            "investment_readiness": sub_scores.get("investment_readiness", 0),
            "business_creation": sub_scores.get("business_creation", 0),
            "travel": sub_scores.get("travel", 0),
        },
        "top_drivers": drivers,
        "explanation": (
            f"FFI {round(score, 1)}/100 driven by "
            + ", ".join(d["label"] for d in drivers[:3])
            + "."
        ),
    }


_DRIVER_LABELS = {
    "savings_growth_rate": "growing savings",
    "income_growth_rate": "rising income",
    "savings_rate": "strong savings rate",
    "investment_ratio": "active investing",
    "income_regularity": "stable income",
    "expense_volatility": "expense volatility",
}


def _top_drivers(features: dict) -> list[dict]:
    weights = {
        "savings_growth_rate": 200,
        "income_growth_rate": 200,
        "savings_rate": 120,
        "investment_ratio": 60,
        "income_regularity": 10,
        "expense_volatility": -40,
    }
    contribs = [
        {
            "feature": f,
            "label": _DRIVER_LABELS.get(f, f),
            "impact": round(w * float(features.get(f, 0.0)), 2),
        }
        for f, w in weights.items()
    ]
    return sorted(contribs, key=lambda d: abs(d["impact"]), reverse=True)
