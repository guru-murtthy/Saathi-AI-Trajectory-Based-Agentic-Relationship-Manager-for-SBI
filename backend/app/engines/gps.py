"""Phase 8: Financial GPS - explainable goal planning engine.

Given a goal (target amount + target date) and current corpus + projected saving
capacity, it computes the gap, the required monthly contribution, and an
allocation plan across FD / Debt Fund / SIP based on the time horizon.

Example (Rahul):
    Goal: Buy House, target \u20b918,00,000, current \u20b93,00,000
    Gap \u20b915,00,000 -> required monthly \u2248 \u20b941,000 -> plan generated.
"""
from __future__ import annotations

from datetime import date

# Expected annual returns used purely for transparent planning math.
INSTRUMENT_RETURNS = {"fd": 0.067, "debt_fund": 0.08, "sip": 0.12}


def _months_between(target: date, start: date) -> int:
    return max(1, (target.year - start.year) * 12 + (target.month - start.month))


def _allocation(months: int) -> dict:
    """Time-horizon based allocation (shorter = safer)."""
    if months <= 12:
        return {"fd": 0.6, "debt_fund": 0.3, "sip": 0.1}
    if months <= 36:
        return {"fd": 0.3, "debt_fund": 0.3, "sip": 0.4}
    return {"fd": 0.1, "debt_fund": 0.2, "sip": 0.7}


def _blended_monthly_rate(alloc: dict) -> float:
    annual = sum(INSTRUMENT_RETURNS[k] * w for k, w in alloc.items())
    return annual / 12


def _required_monthly(gap: float, months: int, monthly_rate: float) -> float:
    """PMT for a future value annuity. Falls back to linear if rate ~0."""
    if monthly_rate <= 1e-9:
        return gap / months
    r = monthly_rate
    return gap * r / ((1 + r) ** months - 1)


def plan_goal(
    goal_kind: str,
    target_amount: float,
    current_amount: float,
    target_date: date,
    monthly_capacity: float | None = None,
    today: date | None = None,
) -> dict:
    today = today or date(2026, 6, 1)
    months = _months_between(target_date, today)
    gap = max(0.0, target_amount - current_amount)
    alloc = _allocation(months)
    monthly_rate = _blended_monthly_rate(alloc)
    required = _required_monthly(gap, months, monthly_rate)

    feasibility = None
    if monthly_capacity is not None:
        feasibility = {
            "monthly_capacity": round(monthly_capacity, 2),
            "on_track": monthly_capacity >= required,
            "shortfall": round(max(0.0, required - monthly_capacity), 2),
        }

    plan = [
        {
            "instrument": k.upper().replace("_", " "),
            "allocation_pct": round(w * 100, 1),
            "monthly_amount": round(required * w, 2),
            "expected_return": INSTRUMENT_RETURNS[k],
        }
        for k, w in alloc.items()
    ]

    return {
        "goal": goal_kind,
        "target_amount": round(target_amount, 2),
        "current_amount": round(current_amount, 2),
        "gap": round(gap, 2),
        "months_to_goal": months,
        "required_monthly": round(required, 2),
        "plan": plan,
        "feasibility": feasibility,
        "explanation": (
            f"To reach \u20b9{round(target_amount):,} for '{goal_kind}' in {months} months, "
            f"a gap of \u20b9{round(gap):,} needs \u2248 \u20b9{round(required):,}/month, "
            f"allocated across FD/Debt/SIP based on a {months}-month horizon."
        ),
    }
