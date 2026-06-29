"""SyntheticDataSource implementation.

Implements the DataSource interface wrapping the existing synthetic data generator
and local store methods.
"""
from __future__ import annotations

import pandas as pd
from app.data.adapters.datasource import DataSource
from app.services import store


class SyntheticDataSource(DataSource):

    def get_transactions(self, customer_id: str) -> pd.DataFrame:
        """Retrieve historical transaction log from the synthetic dataset."""
        return store.get_transactions(customer_id)

    def get_balances(self, customer_id: str) -> dict:
        """Calculate balances using the customer profile and transaction log."""
        cust = store.get_customer(customer_id)
        if cust is None:
            return {"opening_savings": 0.0, "current_savings": 0.0}

        opening = float(cust.get("opening_savings", 0.0))
        tx = store.get_transactions(customer_id)
        
        if not tx.empty:
            # The synthetic transaction amount is positive for credits and negative for debits
            net_flow = float(tx["amount"].astype(float).sum())
            current = opening + net_flow
        else:
            current = opening

        return {
            "opening_savings": round(opening, 2),
            "current_savings": round(current, 2),
        }
