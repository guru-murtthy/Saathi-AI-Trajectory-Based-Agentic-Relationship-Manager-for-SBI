"""Phase 4: Financial DNA engine.

Produces behavioural DNA strands (Saver / Investor / Borrower / Traveler /
Home Buyer) as 0-100 scores derived from engineered features. Values are NOT
hardcoded - each strand is a transparent weighted function of features, squashed
to [0,1] with a logistic so it behaves like a probability/affinity.

Each strand also returns the top contributing features for explainability.
"""
from __future__ import annotations

import math

# strand -> {feature: weight}. Positive weight = feature increases the strand.
DNA_WEIGHTS: dict[str, dict[str, float]] = {
    "saver": {
        "savings_rate": 4.0,
        "savings_growth_rate": 3.0,
        "income_regularity": 1.0,
        "discretionary_ratio": -2.0,
        "_bias": -0.5,
    },
    "investor": {
        "investment_ratio": 6.0,
        "savings_growth_rate": 2.5,
        "income_growth_rate": 1.5,
        "_bias": -1.0,
    },
    "borrower": {
        "emi_ratio": 6.0,
        "rent_ratio": 1.0,
        "savings_rate": -2.0,
        "_bias": -1.5,
    },
    "traveler": {
        "travel_ratio": 7.0,
        "discretionary_ratio": 2.0,
        "income_growth_rate": 1.0,
        "_bias": -1.2,
    },
    "home_buyer": {
        "has_regular_rent": 1.5,
        "rent_ratio": 2.0,
        "savings_growth_rate": 3.0,
        "income_growth_rate": 2.5,
        "savings_rate": 2.0,
        "_bias": -2.0,
    },
}

FEATURE_LABELS = {
    "savings_rate": "savings rate",
    "savings_growth_rate": "savings growth",
    "income_growth_rate": "rising income",
    "income_regularity": "income stability",
    "investment_ratio": "investment activity",
    "emi_ratio": "EMI burden",
    "rent_ratio": "rent payments",
    "has_regular_rent": "regular rent payments",
    "travel_ratio": "travel spending",
    "discretionary_ratio": "discretionary spending",
}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def compute_dna(features: dict) -> dict:
    """Return DNA strands as percentages with per-strand explanations."""
    strands: dict[str, dict] = {}
    for strand, weights in DNA_WEIGHTS.items():
        z = weights.get("_bias", 0.0)
        contributions: list[tuple[str, float]] = []
        for feat, w in weights.items():
            if feat == "_bias":
                continue
            val = float(features.get(feat, 0.0))
            contrib = w * val
            z += contrib
            contributions.append((feat, contrib))
        score = round(_sigmoid(z) * 100, 1)
        top = sorted(contributions, key=lambda kv: abs(kv[1]), reverse=True)[:3]
        strands[strand] = {
            "score": score,
            "drivers": [
                {
                    "feature": f,
                    "label": FEATURE_LABELS.get(f, f),
                    "impact": round(c, 3),
                    "direction": "increases" if c >= 0 else "decreases",
                }
                for f, c in top
            ],
        }
    return strands
