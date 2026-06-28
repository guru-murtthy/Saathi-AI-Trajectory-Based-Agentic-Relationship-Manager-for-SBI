"""LLM adapter layer for the Agentic RM.

Providers are pluggable via the SAATHI_LLM_PROVIDER env var:
    - "offline" (default): deterministic template reasoner, NO API keys, always runs.
    - "openai": uses OPENAI_API_KEY.
    - "gemini": uses GEMINI_API_KEY.
    - "llama":  uses a local/remote OpenAI-compatible endpoint (LLAMA_BASE_URL).

The offline provider guarantees the SBI judge demo works with zero setup.
"""
from __future__ import annotations

import os


def _provider() -> str:
    return os.getenv("SAATHI_LLM_PROVIDER", "offline").lower()


def generate(system: str, prompt: str) -> str:
    provider = _provider()
    try:
        if provider == "openai":
            return _openai(system, prompt)
        if provider == "gemini":
            return _gemini(system, prompt)
        if provider == "llama":
            return _llama(system, prompt)
    except Exception as exc:  # graceful fallback keeps the demo alive
        return f"[offline fallback: {exc}]\n" + _offline(system, prompt)
    return _offline(system, prompt)


def _offline(system: str, prompt: str) -> str:
    # The reasoning content is fully assembled by the RM; offline mode just
    # returns the structured prompt body as the final narrative.
    return prompt


def _openai(system: str, prompt: str) -> str:
    import httpx

    key = os.environ["OPENAI_API_KEY"]
    r = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _gemini(system: str, prompt: str) -> str:
    import httpx

    key = os.environ["GEMINI_API_KEY"]
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    r = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        json={"contents": [{"parts": [{"text": system + "\n\n" + prompt}]}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def _llama(system: str, prompt: str) -> str:
    import httpx

    base = os.getenv("LLAMA_BASE_URL", "http://localhost:11434/v1")
    r = httpx.post(
        f"{base}/chat/completions",
        json={
            "model": os.getenv("LLAMA_MODEL", "llama3"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
