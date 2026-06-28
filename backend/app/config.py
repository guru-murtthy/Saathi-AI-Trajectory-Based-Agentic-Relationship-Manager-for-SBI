"""Central configuration for Saathi AI 3.0."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

CUSTOMERS_CSV = DATA_DIR / "customers.csv"
TRANSACTIONS_CSV = DATA_DIR / "transactions.csv"
FFI_MODEL_PATH = MODEL_DIR / "ffi_lgbm.txt"
FFI_META_PATH = MODEL_DIR / "ffi_meta.json"

# Reproducibility
RANDOM_SEED = int(os.getenv("SAATHI_SEED", "42"))
N_SYNTHETIC_CUSTOMERS = int(os.getenv("SAATHI_N_CUSTOMERS", "2000"))

# Life events the platform predicts.
LIFE_EVENTS = [
    "home_purchase",
    "marriage",
    "investment_readiness",
    "business_creation",
    "travel",
]
