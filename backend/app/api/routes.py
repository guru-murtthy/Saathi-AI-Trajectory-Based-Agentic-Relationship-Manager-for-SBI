"""API contracts for the Saathi AI 3.0 backend (Phases 4-10)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.rm import advise
from app.engines.community import peers
from app.engines.dna import compute_dna
from app.engines.ffi import compute_ffi
from app.engines.future_graph import project
from app.engines.gps import plan_goal
from app.engines.life_event_graph import predict_events
from app.services import store

router = APIRouter(prefix="/api/v1")


def _features_or_404(customer_id: str) -> dict:
    feats = store.get_features(customer_id)
    if feats is None:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found")
    return feats


@router.get("/customers")
def list_customers(limit: int = 25):
    df = store.list_customers().head(limit)
    return df.to_dict(orient="records")


@router.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    cust = store.get_customer(customer_id)
    if cust is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return cust


@router.get("/customers/{customer_id}/features")
def get_features(customer_id: str):
    return _features_or_404(customer_id)


@router.get("/customers/{customer_id}/dna")
def get_dna(customer_id: str):
    feats = _features_or_404(customer_id)
    return {"customer_id": customer_id, "dna": compute_dna(feats)}


@router.get("/customers/{customer_id}/life-events")
def get_life_events(customer_id: str):
    feats = _features_or_404(customer_id)
    return {"customer_id": customer_id, "predictions": predict_events(feats)}


@router.get("/customers/{customer_id}/ffi")
def get_ffi(customer_id: str):
    import time
    from pathlib import Path
    feats = _features_or_404(customer_id)
    
    t0 = time.perf_counter()
    res = compute_ffi(feats)
    duration = time.perf_counter() - t0
    
    print(f"[METRIC] FFI inference latency: {duration:.4f}s")
    perf_log = Path(__file__).resolve().parent.parent.parent / "data" / "performance.log"
    perf_log.parent.mkdir(exist_ok=True)
    with open(perf_log, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ffi_inference - {duration:.4f}s\n")
        
    return {"customer_id": customer_id, **res}


@router.get("/customers/{customer_id}/future-graph")
def get_future_graph(customer_id: str, horizon_months: int = 24):
    feats = _features_or_404(customer_id)
    cust = store.get_customer(customer_id)
    tx = store.get_transactions(customer_id)
    return {"customer_id": customer_id, **project(cust, tx, feats, horizon_months)}


class GoalRequest(BaseModel):
    goal_kind: str = "Buy House"
    target_amount: float
    current_amount: float
    target_date: date


@router.post("/customers/{customer_id}/gps")
def post_gps(customer_id: str, req: GoalRequest):
    feats = _features_or_404(customer_id)
    cust = store.get_customer(customer_id)
    tx = store.get_transactions(customer_id)
    fg = project(cust, tx, feats)
    return plan_goal(
        goal_kind=req.goal_kind,
        target_amount=req.target_amount,
        current_amount=req.current_amount,
        target_date=req.target_date,
        monthly_capacity=fg["monthly_saving_estimate"],
    )


@router.get("/customers/{customer_id}/peers")
def get_peers(customer_id: str):
    _features_or_404(customer_id)
    return peers(customer_id)


class RMRequest(BaseModel):
    question: str | None = None


@router.post("/customers/{customer_id}/rm")
def post_rm(customer_id: str, req: RMRequest):
    import time
    from pathlib import Path
    _features_or_404(customer_id)
    
    t0 = time.perf_counter()
    res = advise(customer_id, req.question)
    duration = time.perf_counter() - t0
    
    print(f"[METRIC] LLM narration latency (RM advice): {duration:.4f}s")
    perf_log = Path(__file__).resolve().parent.parent.parent / "data" / "performance.log"
    perf_log.parent.mkdir(exist_ok=True)
    with open(perf_log, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - llm_narration - {duration:.4f}s\n")
        
    return res


@router.get("/compliance/audit/{customer_id}")
def get_compliance_audit(customer_id: str):
    _features_or_404(customer_id)
    from app.compliance.audit_log import AuditLogger
    return AuditLogger.get_logs(customer_id)


class FeedbackRequest(BaseModel):
    customer_id: str
    thumbs_up: bool
    comment: str | None = None


@router.post("/feedback")
def post_feedback(req: FeedbackRequest):
    from pathlib import Path
    import json
    import uuid
    from datetime import datetime
    
    feedback_file = Path(__file__).resolve().parent.parent.parent / "data" / "feedback.jsonl"
    feedback_file.parent.mkdir(exist_ok=True)
    
    entry = {
        "feedback_id": str(uuid.uuid4()),
        "customer_id": req.customer_id,
        "thumbs_up": req.thumbs_up,
        "comment": req.comment,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(feedback_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        
    return {"status": "success", "feedback_id": entry["feedback_id"]}


@router.get("/sbi/prospects")
def sbi_prospects(event: str = "home_purchase", limit: int = 20):
    """Phase 10 backend: rank customers as prospects for a given life event."""
    rows = []
    for _, c in store.list_customers().iterrows():
        cid = c["customer_id"]
        feats = store.get_features(cid)
        if not feats:
            continue
        events = {e["event"]: e["probability"] for e in predict_events(feats)}
        ffi = compute_ffi(feats)["ffi"]
        rows.append(
            {
                "customer_id": cid,
                "name": c.get("name", cid),
                "city": c.get("city", ""),
                "segment": c.get("segment", ""),
                "ffi": ffi,
                "probability": events.get(event, 0),
            }
        )
    rows.sort(key=lambda r: (r["probability"], r["ffi"]), reverse=True)
    return {"event": event, "prospects": rows[:limit]}
