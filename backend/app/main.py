"""FastAPI application entrypoint for Saathi AI 3.0."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router

app = FastAPI(
    title="Saathi AI 3.0 - The Financial Future Operating System",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def startup_event():
    import threading
    from app.engines.community import _ensure_index
    threading.Thread(target=_ensure_index, daemon=True).start()


@app.get("/")
def root():
    return {"service": "saathi-ai", "version": __version__, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
