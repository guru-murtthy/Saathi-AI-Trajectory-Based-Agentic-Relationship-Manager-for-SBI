"""Phase 9a: Community Intelligence Layer.

Embeds each customer's feature vector into ChromaDB and answers peer-cohort
questions via similarity search, e.g.
    "82% of similar customers purchased homes within 24 months."

Falls back to an in-memory cosine search if ChromaDB is unavailable so the demo
always runs.
"""
from __future__ import annotations

import numpy as np

from app.features.pipeline import features_to_vector
from app.services import store

import threading

_collection = None
_fallback_vectors: dict[str, np.ndarray] = {}
_fallback_meta: dict[str, dict] = {}
_index_lock = threading.Lock()
_index_built = False


def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n else v


def _cohort_label(features: dict) -> dict:
    """Synthetic ground-truth outcome flags used for cohort statistics."""
    return {
        "bought_home_24m": 1
        if (features.get("income_growth_rate", 0) > 0.01
            and features.get("savings_growth_rate", 0) > 0.0
            and features.get("has_regular_rent", 0) > 0.5)
        else 0,
        "started_sip": 1 if features.get("investment_ratio", 0) > 0.08 else 0,
    }


def build_index() -> int:
    """Index all synthetic customers. Returns count indexed."""
    global _collection, _fallback_vectors, _fallback_meta
    customers = store.list_customers()
    try:
        import chromadb

        client = chromadb.Client()
        
        class MockEmbeddingFunction:
            def __call__(self, input):
                return [[0.0] * 16 for _ in input]

        _collection = client.get_or_create_collection(
            name="saathi_customers",
            embedding_function=MockEmbeddingFunction()
        )
    except Exception:
        _collection = None

    ids, embeddings, metadatas = [], [], []
    fallback_vectors = {}
    fallback_meta = {}

    for _, c in customers.iterrows():
        cid = c["customer_id"]
        feats = store.get_features(cid)
        if not feats:
            continue
        vec = _normalize(features_to_vector(feats)).tolist()
        meta = {
            "age": float(c.get("age", 0)),
            "city": str(c.get("city", "")),
            "segment": str(c.get("segment", "")),
            "income": float(feats.get("monthly_income", 0)),
            **_cohort_label(feats),
        }
        ids.append(cid)
        embeddings.append(vec)
        metadatas.append(meta)
        fallback_vectors[cid] = np.array(vec)
        fallback_meta[cid] = meta

    _fallback_vectors = fallback_vectors
    _fallback_meta = fallback_meta

    if _collection is not None and ids:
        try:
            _collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)
        except Exception:
            pass
    return len(ids)


def _ensure_index():
    global _index_built
    if not _index_built:
        with _index_lock:
            if not _index_built:
                build_index()
                _index_built = True


def peers(customer_id: str, k: int = 50) -> dict:
    """Find similar customers and compute cohort statistics."""
    _ensure_index()
    feats = store.get_features(customer_id)
    if not feats:
        return {"error": "customer not found"}
    query = _normalize(features_to_vector(feats))

    neighbor_ids: list[str] = []
    if _collection is not None:
        try:
            res = _collection.query(query_embeddings=[query.tolist()], n_results=k + 1)
            neighbor_ids = [i for i in res["ids"][0] if i != customer_id][:k]
        except Exception:
            neighbor_ids = []

    if not neighbor_ids:
        sims = {
            cid: float(np.dot(query, v))
            for cid, v in _fallback_vectors.items()
            if cid != customer_id
        }
        neighbor_ids = [c for c, _ in sorted(sims.items(), key=lambda kv: kv[1], reverse=True)[:k]]

    metas = [_fallback_meta[c] for c in neighbor_ids if c in _fallback_meta]
    n = len(metas) or 1
    home_pct = round(100 * sum(m["bought_home_24m"] for m in metas) / n, 1)
    sip_pct = round(100 * sum(m["started_sip"] for m in metas) / n, 1)
    avg_income = round(sum(m["income"] for m in metas) / n, 0)

    return {
        "customer_id": customer_id,
        "cohort_size": len(metas),
        "insights": [
            f"{home_pct}% of similar customers purchased homes within 24 months.",
            f"{sip_pct}% of similar customers started a SIP.",
            f"Average monthly income in this cohort is \u20b9{int(avg_income):,}.",
        ],
        "stats": {
            "home_purchase_24m_pct": home_pct,
            "sip_adoption_pct": sip_pct,
            "avg_income": avg_income,
        },
    }
