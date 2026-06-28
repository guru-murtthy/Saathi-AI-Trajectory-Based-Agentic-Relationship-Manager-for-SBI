"""Train the LightGBM FFI regressor on synthetic data.

We build a synthetic target FFI from a known generative function plus noise,
then fit LightGBM to recover it. This gives us a real, serialized model for the
demo while keeping the ground truth explainable.

Run:
    python -m app.ml.train_ffi
"""
from __future__ import annotations

import json

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from app.config import (
    CUSTOMERS_CSV,
    FFI_META_PATH,
    FFI_MODEL_PATH,
    RANDOM_SEED,
    TRANSACTIONS_CSV,
)
from app.features.pipeline import FEATURE_COLUMNS, build_features


def _synthetic_target(f: dict) -> float:
    """Ground-truth FFI used to train the model (kept explainable)."""
    z = (
        50
        + 120 * f["savings_rate"]
        + 200 * f["savings_growth_rate"]
        + 200 * f["income_growth_rate"]
        + 60 * f["investment_ratio"]
        + 10 * f["income_regularity"]
        - 40 * f["expense_volatility"]
    )
    return float(np.clip(z, 0, 100))


def build_dataset() -> pd.DataFrame:
    customers = pd.read_csv(CUSTOMERS_CSV)
    txns = pd.read_csv(TRANSACTIONS_CSV)
    rows = []
    for _, c in customers.iterrows():
        ctx = txns[txns["customer_id"] == c["customer_id"]]
        if ctx.empty:
            continue
        feats = build_features(c.to_dict(), ctx)
        feats["_target"] = _synthetic_target(feats)
        rows.append(feats)
    return pd.DataFrame(rows)


def main():
    df = build_dataset()
    rng = np.random.default_rng(RANDOM_SEED)
    y = df["_target"].values + rng.normal(0, 2.0, len(df))  # add noise
    X = df[FEATURE_COLUMNS].values

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED)
    train_set = lgb.Dataset(X_tr, label=y_tr, feature_name=FEATURE_COLUMNS)
    params = {
        "objective": "regression",
        "metric": "l1",
        "num_leaves": 31,
        "learning_rate": 0.05,
        "verbose": -1,
        "seed": RANDOM_SEED,
    }
    model = lgb.train(params, train_set, num_boost_round=300)
    preds = model.predict(X_te)
    mae = mean_absolute_error(y_te, preds)

    model.save_model(str(FFI_MODEL_PATH))
    FFI_META_PATH.write_text(
        json.dumps({"mae": round(float(mae), 3), "features": FEATURE_COLUMNS}, indent=2)
    )
    print(f"Trained FFI model. Test MAE={mae:.3f}")
    print(f"  -> {FFI_MODEL_PATH}")


if __name__ == "__main__":
    main()
