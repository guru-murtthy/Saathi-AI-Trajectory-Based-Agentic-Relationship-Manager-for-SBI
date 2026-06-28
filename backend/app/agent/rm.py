"""Phase 9b: Agentic Relationship Manager.

The RM is NOT a chatbot. It runs a fixed cognitive loop:
    OBSERVE  -> pull the customer's features, DNA, FFI, events, peers
    REASON   -> connect signals to predicted needs
    PREDICT  -> surface the top life event + probability
    EXPLAIN  -> attach the why (signal path + drivers)
    RECOMMEND-> propose a concrete SBI action with reasoning

The LLM (offline by default) only narrates the structured reasoning the engines
produce, so every recommendation is grounded and explainable.
"""
from __future__ import annotations

from app.agent.llm import generate
from app.engines.community import peers
from app.engines.dna import compute_dna
from app.engines.ffi import compute_ffi
from app.engines.future_graph import project
from app.engines.life_event_graph import predict_events
from app.services import store

SYSTEM = (
    "You are Saathi, an Agentic Relationship Manager for SBI. You observe, reason, "
    "predict, explain, and recommend. Every recommendation must include reasoning. "
    "You never move money without human approval."
)


def _observe(customer_id: str) -> dict:
    cust = store.get_customer(customer_id)
    feats = store.get_features(customer_id)
    tx = store.get_transactions(customer_id)
    return {
        "customer": cust,
        "features": feats,
        "dna": compute_dna(feats),
        "ffi": compute_ffi(feats),
        "events": predict_events(feats),
        "future_graph": project(cust, tx, feats),
        "peers": peers(customer_id),
    }


def _recommendation(ctx: dict) -> dict:
    top = ctx["events"][0]
    fg = ctx["future_graph"]
    rec = {
        "home_purchase": {
            "action": "Offer SBI Home Loan pre-approval + start a Financial GPS plan",
            "product": "SBI Home Loan",
        },
        "investment_readiness": {
            "action": "Onboard to SBI Mutual Fund SIP",
            "product": "SBI SIP",
        },
        "business_creation": {
            "action": "Offer SBI MSME working-capital loan + current account",
            "product": "SBI MSME Loan",
        },
        "marriage": {"action": "Offer an RD wedding fund + personal loan", "product": "SBI RD"},
        "travel": {"action": "Offer SBI Travel Card + forex", "product": "SBI Travel Card"},
    }.get(top["event"], {"action": "Engage with a savings review", "product": "SBI Savings"})

    return {
        **rec,
        "target_event": top["event"],
        "probability": top["probability"],
        "reasoning": top["explanation"],
        "requires_human_approval": True,
        "supporting": {
            "ffi": ctx["ffi"]["ffi"],
            "projected_balance_24m": fg["projection"][-1]["balance"] if fg["projection"] else None,
            "peer_insight": ctx["peers"]["insights"][0] if ctx["peers"].get("insights") else None,
        },
    }


def advise(customer_id: str, question: str | None = None) -> dict:
    if store.get_features(customer_id) is None:
        return {"error": "customer not found"}
    observed = _observe(customer_id)
    rec = _recommendation(observed)
    name = observed["customer"].get("name", customer_id)

    narrative_prompt = (
        f"Customer: {name}.\n"
        f"FFI: {observed['ffi']['ffi']}/100.\n"
        f"Top life event: {rec['target_event']} at {rec['probability']}%.\n"
        f"Why: {rec['reasoning']}\n"
        f"Peer insight: {rec['supporting']['peer_insight']}\n"
        f"Recommended action: {rec['action']} (requires human approval).\n"
        + (f"\nCustomer question: {question}\nAnswer using the reasoning above." if question else "")
    )
    narrative = generate(SYSTEM, narrative_prompt)

    return {
        "customer_id": customer_id,
        "loop": {
            "observe": {
                "ffi": observed["ffi"]["ffi"],
                "top_dna": max(observed["dna"].items(), key=lambda kv: kv[1]["score"])[0],
            },
            "reason": rec["reasoning"],
            "predict": {"event": rec["target_event"], "probability": rec["probability"]},
            "explain": observed["events"][0]["signals"],
            "recommend": rec,
        },
        "narrative": narrative,
    }
