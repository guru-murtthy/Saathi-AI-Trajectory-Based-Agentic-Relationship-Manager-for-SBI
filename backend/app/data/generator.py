"""Phase 2: Synthetic banking dataset generator.

Generates realistic-but-synthetic customers and 12 months of transactions.
No real or hardcoded customer values are used downstream; everything is derived
from this generated data via the feature pipeline.

The generator also injects the demo customer "Rahul" so the SBI judge demo flow
is deterministic.

Run:
    python -m app.data.generator
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from app.config import (
    CUSTOMERS_CSV,
    N_SYNTHETIC_CUSTOMERS,
    RANDOM_SEED,
    TRANSACTIONS_CSV,
)

CITIES = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Kolkata"]
SEGMENTS = ["retail", "msme"]

CATEGORIES = [
    "salary", "rent", "groceries", "utilities", "education", "jewelry",
    "travel", "investment", "emi", "upi_p2p", "gst", "payroll_out",
]


def _rng(seed: int = RANDOM_SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def _gen_customer(rng: np.random.Generator, idx: int) -> dict:
    segment = rng.choice(SEGMENTS, p=[0.85, 0.15])
    age = int(np.clip(rng.normal(34, 9), 21, 65))
    base_salary = float(np.clip(rng.lognormal(mean=10.9, sigma=0.45), 18000, 400000))
    return {
        "customer_id": f"cust_{idx:05d}",
        "name": f"Customer {idx}",
        "age": age,
        "city": rng.choice(CITIES),
        "segment": segment,
        "base_monthly_income": round(base_salary, 2),
        "opening_savings": round(float(np.clip(rng.normal(base_salary * 4, base_salary * 3), 0, None)), 2),
    }


def _gen_transactions(rng: np.random.Generator, cust: dict, months: int = 12) -> list[dict]:
    """Generate a 12-month transaction trail with realistic trajectories."""
    txns: list[dict] = []
    income = cust["base_monthly_income"]
    # Some customers have rising salaries (a key home-purchase signal).
    salary_growth = rng.choice([0.0, 0.0, 0.01, 0.02, 0.03], p=[0.4, 0.2, 0.2, 0.1, 0.1])
    pays_rent = rng.random() < 0.55
    rent = round(income * rng.uniform(0.18, 0.32), 2) if pays_rent else 0.0
    saver_bias = rng.uniform(0.05, 0.45)

    start = pd.Timestamp("2025-06-01")
    for m in range(months):
        month_income = income * ((1 + salary_growth) ** m)
        ts = start + pd.DateOffset(months=m)

        if cust["segment"] == "retail":
            txns.append(_tx(ts, cust, "salary", +month_income, "neft"))
        else:
            # MSME: payroll inflow + GST outflow scaling with business growth.
            txns.append(_tx(ts, cust, "payroll", +month_income * rng.uniform(1.5, 4), "neft"))
            txns.append(_tx(ts, cust, "gst", -month_income * rng.uniform(0.05, 0.18), "neft"))

        if rent:
            txns.append(_tx(ts, cust, "rent", -rent, "upi"))

        txns.append(_tx(ts, cust, "groceries", -month_income * rng.uniform(0.08, 0.18), "upi"))
        txns.append(_tx(ts, cust, "utilities", -month_income * rng.uniform(0.03, 0.07), "upi"))

        if rng.random() < 0.25:
            txns.append(_tx(ts, cust, "travel", -month_income * rng.uniform(0.1, 0.4), "card"))
        if rng.random() < 0.08:
            txns.append(_tx(ts, cust, "jewelry", -month_income * rng.uniform(0.3, 1.2), "card"))
        if rng.random() < 0.30:
            txns.append(_tx(ts, cust, "education", -month_income * rng.uniform(0.05, 0.25), "neft"))

        # Savings / investment behaviour scales with saver_bias and rising income.
        invest = month_income * saver_bias * rng.uniform(0.5, 1.5)
        if invest > 0:
            txns.append(_tx(ts, cust, "investment", -invest, "neft"))

    return txns


def _tx(ts, cust, category, amount, channel) -> dict:
    return {
        "customer_id": cust["customer_id"],
        "ts": ts.isoformat(),
        "category": category,
        "amount": round(float(amount), 2),
        "direction": "credit" if amount > 0 else "debit",
        "channel": channel,
    }


def _rahul() -> dict:
    """Deterministic demo customer for the SBI judge flow."""
    return {
        "customer_id": "rahul",
        "name": "Rahul",
        "age": 28,
        "city": "Bangalore",
        "segment": "retail",
        "base_monthly_income": 65000.0,
        "opening_savings": 400000.0,
    }


def _rahul_transactions(rng: np.random.Generator) -> list[dict]:
    """Rahul: rising salary, regular rent (18k), steady savings growth."""
    cust = _rahul()
    txns: list[dict] = []
    start = pd.Timestamp("2025-06-01")
    for m in range(12):
        income = 65000 * (1.02 ** m)  # consistent salary increases
        ts = start + pd.DateOffset(months=m)
        txns.append(_tx(ts, cust, "salary", +income, "neft"))
        txns.append(_tx(ts, cust, "rent", -18000, "upi"))  # regular rent payments
        txns.append(_tx(ts, cust, "groceries", -income * 0.12, "upi"))
        txns.append(_tx(ts, cust, "utilities", -income * 0.04, "upi"))
        # Growing savings: investment amount rises over the year.
        txns.append(_tx(ts, cust, "investment", -(8000 + m * 600), "neft"))
        if m in (3, 9):
            txns.append(_tx(ts, cust, "travel", -income * 0.2, "card"))
    return txns


def generate(n: int = N_SYNTHETIC_CUSTOMERS, seed: int = RANDOM_SEED):
    rng = _rng(seed)
    customers = [_gen_customer(rng, i) for i in range(n)]
    txns: list[dict] = []
    for c in customers:
        txns.extend(_gen_transactions(rng, c))

    # Inject the deterministic demo customer.
    customers.append(_rahul())
    txns.extend(_rahul_transactions(rng))

    cust_df = pd.DataFrame(customers)
    tx_df = pd.DataFrame(txns)
    cust_df.to_csv(CUSTOMERS_CSV, index=False)
    tx_df.to_csv(TRANSACTIONS_CSV, index=False)
    return cust_df, tx_df


if __name__ == "__main__":
    c, t = generate()
    print(f"Generated {len(c)} customers and {len(t)} transactions.")
    print(f"  -> {CUSTOMERS_CSV}")
    print(f"  -> {TRANSACTIONS_CSV}")
