from fastapi import FastAPI

from app import store, salesforce
from app.metrics import metrics
from app.pipeline import run_pipeline
from app.config import MOCK_MODE

app = FastAPI(title="leadpilot", version="0.1.0")


@app.on_event("startup")
def _startup():
    store.init()


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": MOCK_MODE}


@app.post("/run")
def run():
    """Execute a full discovery->enrich->score->sync pipeline run."""
    return run_pipeline()


@app.get("/leads")
def leads(qualified: bool = False):
    return [lead.model_dump() for lead in store.list_leads(qualified_only=qualified)]


@app.get("/runs")
def runs():
    return store.list_runs()


@app.get("/metrics")
def get_metrics():
    return {**metrics.snapshot(), "salesforce_calls": salesforce.sf_call_count()}


@app.post("/reset")
def reset():
    store.reset()
    metrics.reset()
    return {"status": "reset"}
