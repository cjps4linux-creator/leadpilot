# leadpilot: AI lead discovery → enrichment → scoring → Salesforce sync

Built as a demonstration of the exact workflow The Future Perfect described:
discovery through Salesforce sync, with qualification, scoring, dedup, idempotent
sync, retries, logging, and observability — runnable headless at zero cloud spend.

MOCK_MODE=true (default): no external APIs. Swap in real adapters (discovery API,
Clearbit enrichment, Salesforce simple-salesforce) by flipping env + implementing
the adapter functions — the orchestration, scoring, dedup, and sync contracts stay.

## Run
```bash
docker build -f backend/Dockerfile -t leadpilot:latest .
docker run --rm -p 8000:8000 leadpilot:latest
curl -X POST http://localhost:8000/run      # full pipeline
curl http://localhost:8000/leads?qualified=true
curl http://localhost:8000/metrics
```

## What it demonstrates (maps to the JD)
- Lead discovery from sources (pluggable adapters)
- Enrichment + data normalization + entity resolution / dedup
- Rule + model scoring pipeline (qualification)
- Idempotent Salesforce upsert (ExternalId, no duplicates, safe retries w/ backoff)
- Repeatable runs, error handling, logging, monitoring
- Clean handoff: REST API + SQLite store + this doc

## Endpoints
- POST /run — execute pipeline
- GET /leads?qualified=true — view stored leads
- GET /runs — run history
- GET /metrics — counts + salesforce call count
- POST /reset — clear state

Swap in real adapters (discovery API, Clearbit enrichment, Salesforce `simple-salesforce`) by flipping env + implementing the adapter functions — the orchestration, scoring, dedup, and sync contracts stay.
