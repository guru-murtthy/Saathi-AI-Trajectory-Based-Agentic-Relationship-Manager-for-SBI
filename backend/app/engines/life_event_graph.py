"""Phase 5: Life Event Knowledge Graph.

A graph-based reasoning engine (networkx) that links observed financial SIGNALS
to life EVENTS, then to NEEDS, then to recommended JOURNEYS. The graph is what
makes predictions explainable: every event probability comes with the signal
path that produced it.

    salary_increase + savings_growth + rent_payments
        -> home_purchase -> home_loan_need -> home_loan_journey
"""
from __future__ import annotations

import networkx as nx

# Signal -> (feature, threshold, human label). A signal fires when the feature
# crosses its threshold.
SIGNALS: dict[str, tuple[str, float, str]] = {
    "salary_increase": ("income_growth_rate", 0.01, "Salary increasing month over month"),
    "savings_growth": ("savings_growth_rate", 0.01, "Savings growing steadily"),
    "rent_payments": ("has_regular_rent", 0.5, "Regular rent payments detected"),
    "high_savings": ("savings_rate", 0.20, "High savings rate"),
    "investment_activity": ("investment_ratio", 0.08, "Active investing behaviour"),
    "jewelry_purchase": ("jewelry_ratio", 0.05, "Jewelry purchases observed"),
    "education_expense": ("education_ratio", 0.08, "Education-related expenses"),
    "travel_bookings": ("travel_ratio", 0.08, "Frequent travel bookings"),
    "gst_growth": ("income_growth_rate", 0.015, "GST / business inflow growing"),
}

# Event -> list of (signal, weight). Probability is logistic over fired signals.
EVENT_RULES: dict[str, list[tuple[str, float]]] = {
    "home_purchase": [
        ("salary_increase", 1.4),
        ("savings_growth", 1.6),
        ("rent_payments", 1.5),
        ("high_savings", 1.0),
    ],
    "marriage": [
        ("jewelry_purchase", 1.8),
        ("savings_growth", 0.8),
        ("salary_increase", 0.6),
    ],
    "investment_readiness": [
        ("high_savings", 1.5),
        ("investment_activity", 1.8),
        ("salary_increase", 0.8),
    ],
    "business_creation": [
        ("gst_growth", 1.6),
        ("high_savings", 1.0),
        ("investment_activity", 0.6),
    ],
    "travel": [
        ("travel_bookings", 2.0),
        ("salary_increase", 0.7),
    ],
}

# Event -> (need, recommended journey).
EVENT_OUTCOMES: dict[str, tuple[str, str]] = {
    "home_purchase": ("home_loan_need", "SBI Home Loan + Financial GPS savings plan"),
    "marriage": ("wedding_finance_need", "SBI Personal Loan + RD wedding fund"),
    "investment_readiness": ("wealth_growth_need", "SBI Mutual Funds + SIP onboarding"),
    "business_creation": ("working_capital_need", "SBI MSME loan + current account"),
    "travel": ("travel_finance_need", "SBI Travel Card + forex"),
}

import math


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def fired_signals(features: dict) -> dict[str, str]:
    """Return signals that are active for this customer with their labels."""
    fired: dict[str, str] = {}
    for sig, (feat, thresh, label) in SIGNALS.items():
        if float(features.get(feat, 0.0)) >= thresh:
            fired[sig] = label
    return fired


def build_graph(features: dict) -> nx.DiGraph:
    """Construct the reasoning graph for a single customer."""
    g = nx.DiGraph()
    fired = fired_signals(features)

    for sig, label in fired.items():
        g.add_node(sig, kind="signal", label=label)

    for event, rules in EVENT_RULES.items():
        z = -1.0  # bias
        active = []
        for sig, w in rules:
            if sig in fired:
                z += w
                active.append(sig)
        prob = round(_sigmoid(z) * 100, 1)
        g.add_node(event, kind="event", probability=prob)
        for sig in active:
            g.add_edge(sig, event, weight=dict(rules)[sig])
        need, journey = EVENT_OUTCOMES[event]
        g.add_node(need, kind="need")
        g.add_node(journey, kind="journey")
        g.add_edge(event, need)
        g.add_edge(need, journey)
    return g


def predict_events(features: dict) -> list[dict]:
    """Return ranked life-event predictions with explanation paths."""
    g = build_graph(features)
    fired = fired_signals(features)
    results = []
    for event in EVENT_RULES:
        prob = g.nodes[event]["probability"]
        active = [s for s in g.predecessors(event)]
        need, journey = EVENT_OUTCOMES[event]
        results.append(
            {
                "event": event,
                "probability": prob,
                "signals": [{"signal": s, "why": fired.get(s, s)} for s in active],
                "need": need,
                "recommended_journey": journey,
                "explanation": _explain(event, active, fired, prob),
            }
        )
    return sorted(results, key=lambda r: r["probability"], reverse=True)


def _explain(event: str, active: list[str], fired: dict, prob: float) -> str:
    if not active:
        return f"No strong signals yet for {event.replace('_', ' ')} ({prob}%)."
    reasons = " + ".join(fired.get(s, s) for s in active)
    return (
        f"{reasons} -> {event.replace('_', ' ')} probability {prob}%."
    )
