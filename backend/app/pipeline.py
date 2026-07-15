"""Pipeline orchestrator: discovery -> enrich -> score -> (dedup via store) -> sync.

Repeatable, observable, idempotent. Mirrors the project the client described:
'build and ship an AI-powered lead discovery workflow from discovery through
Salesforce sync' with error handling, logging, safe retries.
"""
import time
from datetime import datetime, timezone

from app import store
from app.metrics import metrics
from app.sources import discover
from app.enrichment import enrich
from app.scoring import score_lead
from app.salesforce import sync_lead


def run_pipeline() -> dict:
    metrics.reset()
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()

    raw = discover()
    metrics.inc("discovered", len(raw))

    qualified = 0
    synced = 0
    for lead in raw:
        try:
            lead = enrich(lead)
            lead = score_lead(lead)
            # store.upsert_lead is idempotent by identity_key -> dedup happens here
            lead = store.upsert_lead(lead)
            metrics.inc("enriched")
            if lead.qualified:
                qualified += 1
                metrics.inc("qualified")
                lead = sync_lead(lead)  # only sync qualified leads
                store.upsert_lead(lead)
                if lead.last_sync_status in ("created", "updated"):
                    synced += 1
                    metrics.inc("synced")
        except Exception:  # noqa: BLE001 - pipeline continues; errors counted
            metrics.errors += 1

    elapsed = time.perf_counter() - t0
    metrics.record_latency(elapsed)
    finished = datetime.now(timezone.utc).isoformat()
    store.log_run(started, finished, "success", metrics.discovered,
                  qualified, synced, f"e2e {elapsed:.2f}s")

    return {
        "status": "success",
        "discovered": metrics.discovered,
        "qualified": qualified,
        "synced": synced,
        "e2e_latency_s": round(elapsed, 3),
        "errors": metrics.errors,
    }
