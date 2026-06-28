"""In-memory data store loaded from the synthetic CSVs.

For the hackathon MVP this avoids needing a live Postgres for the demo to run,
while keeping the same access shape we will later back with SQLAlchemy.
"""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from app.config import CUSTOMERS_CSV, TRANSACTIONS_CSV
from app.features.pipeline import build_features


@lru_cache(maxsize=1)
def _load():
    customers = pd.read_csv(CUSTOMERS_CSV)
    txns = pd.read_csv(TRANSACTIONS_CSV)
    return customers, txns


@lru_cache(maxsize=1)
def _load_lookup():
    customers, txns = _load()
    cust_dict = {row["customer_id"]: row.to_dict() for _, row in customers.iterrows()}
    tx_dict = {cid: group for cid, group in txns.groupby("customer_id")}
    return cust_dict, tx_dict


def get_customer(customer_id: str) -> dict | None:
    cust_dict, _ = _load_lookup()
    return cust_dict.get(customer_id)


def get_transactions(customer_id: str) -> pd.DataFrame:
    _, tx_dict = _load_lookup()
    if customer_id in tx_dict:
        return tx_dict[customer_id].copy()
    return pd.DataFrame(columns=["customer_id", "ts", "category", "amount", "direction", "channel"])


@lru_cache(maxsize=5000)
def get_features(customer_id: str) -> dict | None:
    cust = get_customer(customer_id)
    if cust is None:
        return None
    tx = get_transactions(customer_id)
    if tx.empty:
        return None
    return build_features(cust, tx)


def list_customers() -> pd.DataFrame:
    customers, _ = _load()
    return customers
