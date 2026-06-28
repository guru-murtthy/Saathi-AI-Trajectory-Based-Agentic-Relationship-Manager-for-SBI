"""Phase 7: Financial Future Graph.

Projects a customer's net-worth / savings trajectory forward N months using an
EWMA of historical monthly net cashflow plus the observed income-growth rate.
Deterministic and explainable (no black box) so the judge can see WHY the line
goes up.

The LSTM upgrade (PyTorch) is the production roadmap item; the MVP uses a
transparent statistical projection that is fast and reproducible.
"""
from __future__ import annotations

import pandas as pd


def _monthly_net_cashflow(tx: pd.DataFrame) -> pd.Series:
    t = tx.copy()
    t["amount"] = t["amount"].astype(float)
    t["month"] = pd.to_datetime(t["ts"]).dt.to_period("M")
    return t.groupby("month")["amount"].sum()


def project(customer: dict, tx: pd.DataFrame, features: dict, horizon_months: int = 24) -> dict:
    """Return projected savings balance for the next `horizon_months`."""
    net = _monthly_net_cashflow(tx)
    opening = float(customer.get("opening_savings", 0.0))
    current_balance = opening + float(net.cumsum().iloc[-1]) if len(net) else opening

    # EWMA of monthly net flow = expected monthly saving going forward.
    if len(net) >= 2:
        ewma_flow = float(net.ewm(span=4).mean().iloc[-1])
    else:
        ewma_flow = float(net.mean()) if len(net) else 0.0

    growth = float(features.get("income_growth_rate", 0.0))

    history = [
        {"month": str(m), "balance": round(opening + float(net.iloc[: i + 1].sum()), 2)}
        for i, m in enumerate(net.index)
    ]

    projection = []
    balance = current_balance
    flow = ewma_flow
    last_period = net.index[-1] if len(net) else pd.Period("2026-06", freq="M")
    for k in range(1, horizon_months + 1):
        flow *= (1 + growth)  # income (and thus saving capacity) compounds
        balance += flow
        projection.append(
            {"month": str(last_period + k), "balance": round(balance, 2)}
        )

    return {
        "current_balance": round(current_balance, 2),
        "monthly_saving_estimate": round(ewma_flow, 2),
        "income_growth_rate": round(growth, 4),
        "history": history,
        "projection": projection,
        "horizon_months": horizon_months,
        "explanation": (
            f"Projected from current balance \u20b9{round(current_balance):,} using an "
            f"estimated \u20b9{round(ewma_flow):,}/month saving capacity, compounding at "
            f"{round(growth * 100, 1)}% income growth."
        ),
    }
