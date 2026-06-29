"""Abstract DataSource interface.

Proves the "synthetic-data-first, production adapter swap" architecture.
Allows swap-out of synthetic CSV source with actual core banking system interfaces.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import pandas as pd


class DataSource(ABC):

    @abstractmethod
    def get_transactions(self, customer_id: str) -> pd.DataFrame:
        """Retrieve historical transaction log for a given customer."""
        pass

    @abstractmethod
    def get_balances(self, customer_id: str) -> dict:
        """Retrieve current and opening savings balance metrics for a given customer."""
        pass
