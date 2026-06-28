"""Phase 3: Feature engineering pipeline.

Turns raw transactions into the engineered feature vector that powers the
Financial DNA, Life Event Graph and FFI. No hardcoded behavioural values:
everything is computed from the transaction trail.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Feature columns produced by this pipeline (stable order matters for the model).
FEATURE_COLUMNS = [
    "monthly_income",
    "income_growth_rate",
    "savings_rate",
    "savings_growth_rate",
    "expense_volatility",
    "rent_ratio",
    "has_regular_rent",
    "investment_ratio",
    "travel_ratio",
    "jewelry_ratio",
    "education_ratio",
    "emi_ratio",
    "upi_share",
    "discretionary_ratio",
    "income_regularity",
    "age",
]


def _safe_div(a: float, b: float) -> float:
    return float(a / b) if b else 0.0


def _monthly_series(tx: pd.DataFrame, mask: pd.Series) -> pd.Series:
    sub = tx[mask]
    if sub.empty:
        return pd.Series(dtype=float)
    months = sub["ts"].astype(str).str[:7]
    return sub.groupby(months)["amount"].sum().abs()


def _growth_rate(series: pd.Series) -> float:
    """Average month-over-month growth, robust to short series."""
    s = series.dropna()
    if len(s) < 2:
        return 0.0
    first, last = s.iloc[0], s.iloc[-1]
    if first <= 0:
        return 0.0
    months = len(s) - 1
    return float((last / first) ** (1 / months) - 1)


def build_features(customer: dict, tx: pd.DataFrame) -> dict:
    """Compute the engineered feature vector for one customer.

    Args:
        customer: customer row (dict) with age / segment / income.
        tx: transactions DataFrame for this customer only.
    """
    tx = tx.copy()
    tx["amount"] = tx["amount"].astype(float)
    credits = tx[tx["direction"] == "credit"]
    debits = tx[tx["direction"] == "debit"]

    income_series = _monthly_series(tx, tx["category"].isin(["salary", "payroll"]))
    monthly_income = float(income_series.mean()) if not income_series.empty else float(
        customer.get("base_monthly_income", 0.0)
    )
    total_credit = float(credits["amount"].sum())
    total_debit = float(debits["amount"].abs().sum())

    invest_series = _monthly_series(tx, tx["category"] == "investment")
    rent_series = _monthly_series(tx, tx["category"] == "rent")
    expense_series = _monthly_series(tx, tx["direction"] == "debit")

    savings = total_credit - total_debit
    savings_rate = _safe_div(savings, total_credit)

    def cat_ratio(cat: str) -> float:
        amt = float(debits[debits["category"] == cat]["amount"].abs().sum())
        return _safe_div(amt, total_credit)

    rent_months = rent_series[rent_series > 0].count()
    has_regular_rent = 1.0 if rent_months >= 6 else 0.0

    upi_amt = float(tx[tx["channel"] == "upi"]["amount"].abs().sum())
    total_amt = float(tx["amount"].abs().sum())

    discretionary = sum(cat_ratio(c) for c in ("travel", "jewelry"))
    income_regularity = (
        1.0 - float(np.clip(income_series.std() / (income_series.mean() + 1e-9), 0, 1))
        if len(income_series) > 1 else 0.5
    )

    return {
        "monthly_income": round(monthly_income, 2),
        "income_growth_rate": round(_growth_rate(income_series), 4),
        "savings_rate": round(savings_rate, 4),
        "savings_growth_rate": round(_growth_rate(invest_series), 4),
        "expense_volatility": round(
            float(expense_series.std() / (expense_series.mean() + 1e-9)) if len(expense_series) > 1 else 0.0, 4
        ),
        "rent_ratio": round(cat_ratio("rent"), 4),
        "has_regular_rent": has_regular_rent,
        "investment_ratio": round(cat_ratio("investment"), 4),
        "travel_ratio": round(cat_ratio("travel"), 4),
        "jewelry_ratio": round(cat_ratio("jewelry"), 4),
        "education_ratio": round(cat_ratio("education"), 4),
        "emi_ratio": round(cat_ratio("emi"), 4),
        "upi_share": round(_safe_div(upi_amt, total_amt), 4),
        "discretionary_ratio": round(discretionary, 4),
        "income_regularity": round(income_regularity, 4),
        "age": float(customer.get("age", 35)),
    }


def features_to_vector(features: dict) -> np.ndarray:
    return np.array([features.get(c, 0.0) for c in FEATURE_COLUMNS], dtype=float)
