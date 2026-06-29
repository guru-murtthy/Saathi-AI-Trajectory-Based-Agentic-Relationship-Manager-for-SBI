"""Compliance Audit Logger.

Provides append-only structured auditing to satisfy regulatory frameworks.
Writes JSON lines to backend/data/audit_log.jsonl.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AuditEvent(BaseModel):
    event_id: str
    customer_id: str
    signal_fired: List[str]
    recommendation: str
    model_version: str
    timestamp: str
    approved_by: Optional[str] = None


class AuditLogger:
    # Resolve backend/data directory relative to this file
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_FILE = os.path.join(_BASE_DIR, "data", "audit_log.jsonl")

    @classmethod
    def log(
        cls,
        customer_id: str,
        signal_fired: List[str],
        recommendation: str,
        model_version: str = "v1.0.0",
        approved_by: Optional[str] = None,
    ) -> AuditEvent:
        # Ensure target data directory exists
        os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            customer_id=customer_id,
            signal_fired=signal_fired,
            recommendation=recommendation,
            model_version=model_version,
            timestamp=datetime.utcnow().isoformat() + "Z",
            approved_by=approved_by,
        )
        
        with open(cls.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
            
        return event

    @classmethod
    def get_logs(cls, customer_id: str) -> List[dict]:
        if not os.path.exists(cls.LOG_FILE):
            return []
        
        events = []
        with open(cls.LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get("customer_id") == customer_id:
                        events.append(data)
                except Exception:
                    pass
        return events
