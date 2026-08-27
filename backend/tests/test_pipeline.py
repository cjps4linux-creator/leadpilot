"""Contract tests for leadpilot pipeline (headless, mock mode)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["MOCK_MODE"] = "true"
# isolate DB so tests don't collide with any real data
os.environ["DB_PATH"] = os.path.join(os.path.dirname(__file__), "test_leadpilot.db")

from app import store, salesforce
from app.metrics import metrics as metrics_mod
from app.models import Lead
from app.enrichment import enrich
from app.scoring import score_lead
from app.salesforce import sync_lead
from app.pipeline import run_pipeline


def setup_module(_):
    store.init()
    store.reset()


def test_scoring_qualifies_senior():
    store.reset()
    lead = Lead(name="Jane Doe", company="acme corp", title="CTO", email="jane@acme.com")
    lead = enrich(lead)
    lead = score_lead(lead)
    assert lead.score > 0
    assert lead.qualified is True
    print(f"PASS scoring senior (score={lead.score}, qualified={lead.qualified})")


def test_dedup_entity_resolution():
    store.reset()
    a = Lead(name="jane doe", company="Acme Corp", email="JANE@ACME.COM", source="mock")
    b = Lead(name="Jane Doe", company="acme corp", email="jane@acme.com", source="mock")
    a = store.upsert_lead(a)
    b = store.upsert_lead(b)
    # same identity -> same id, no duplicate
    assert a.id == b.id, "duplicate created for same identity"
    assert len(store.list_leads()) == 1
    print("PASS dedup/entity resolution (same identity -> 1 record)")


def test_salesforce_idempotent_upsert():
    store.reset()
    lead = Lead(name="Carlos Ruiz", company="studio norte", email="carlos@studionorte.io")
    lead = enrich(lead)
    lead = score_lead(lead)
    l1 = sync_lead(lead)
    l2 = sync_lead(lead)  # re-sync same lead
    assert l1.sf_id == l2.sf_id, "salesforce id changed on re-sync"
    assert l2.last_sync_status == "updated"
    # idempotent: only ONE salesforce create/update call path per external id
    print(f"PASS salesforce idempotent upsert (sf_id={l1.sf_id}, status={l2.last_sync_status})")


def test_full_pipeline_run():
    metrics_mod.reset()
    salesforce._sf.clear()
    res = run_pipeline()
    assert res["status"] == "success"
    assert res["discovered"] >= 5
    # mock data has duplicates -> stored count < discovered
    leads = store.list_leads()
    assert len(leads) < res["discovered"], "dedup did not reduce stored count"
    assert res["synced"] >= 1
    print(f"PASS full pipeline: discovered={res['discovered']} stored={len(leads)} "
          f"qualified_synced={res['synced']} e2e={res['e2e_latency_s']}s")


def test_metrics_observe():
    m = metrics_mod.snapshot()
    assert "discovered" in m and "synced" in m
    full = __import__("app.main", fromlist=["app"]).get_metrics()
    assert "salesforce_calls" in full
    print(f"PASS metrics observable: {m}")


if __name__ == "__main__":
    setup_module(None)
    test_scoring_qualifies_senior()
    test_dedup_entity_resolution()
    test_salesforce_idempotent_upsert()
    test_full_pipeline_run()
    test_metrics_observe()
    print("\nALL TESTS PASSED")
