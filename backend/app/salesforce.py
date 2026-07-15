"""Salesforce sync: idempotent upsert keyed on a stable external id.

Demonstrates 'Salesforce data sync patterns', 'idempotency', 'prevent duplicates',
and 'safe retries'. In mock mode we simulate the Salesforce REST upsert (sobject
upsert by ExternalId) with an in-memory store. Real mode would use simple-salesforce.
"""
import time
import threading
from app.models import Lead

# In-memory Salesforce simulator (mock mode)
_sf: dict[str, dict] = {}
_sf_lock = threading.Lock()
_call_count = 0  # observe retries


def _sf_upsert(lead: Lead) -> tuple[str, str]:
    """Returns (salesforce_id, status). Idempotent: same external_id -> same record."""
    global _call_count
    with _sf_lock:
        _call_count += 1
        ext = lead.identity_key()
        if ext in _sf:
            rec = _sf[ext]
            rec["score"] = lead.score
            rec["qualified"] = lead.qualified
            return rec["id"], "updated"
        sf_id = f"003{abs(hash(ext)) % 10**12:012d}"
        _sf[ext] = {"id": sf_id, "email": lead.email, "company": lead.company,
                    "score": lead.score, "qualified": lead.qualified}
        return sf_id, "created"


def sync_lead(lead: Lead, max_retries: int = 3) -> Lead:
    """Idempotent Salesforce upsert with bounded retries + backoff."""
    last_err = None
    for attempt in range(max_retries):
        try:
            sf_id, status = _sf_upsert(lead)
            lead.sf_id = sf_id
            lead.last_sync_status = status
            return lead
        except Exception as e:  # noqa: BLE001 - demonstrate safe retry
            last_err = e
            time.sleep(0.05 * (attempt + 1))  # exponential-ish backoff
    lead.last_sync_status = f"error: {last_err}"
    return lead


def sf_call_count() -> int:
    return _call_count
