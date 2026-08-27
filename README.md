# leadpilot

AI lead discovery, enrichment, scoring, and CRM sync — demonstrates the full data pipeline from raw lead sources through qualification, deduplication, and idempotent Salesforce integration. Runs headless at zero cloud spend with mock mode.

Built by Conrad CJ Wilson.

## What It Demonstrates

| Capability | Implementation |
|---|---|
| Lead discovery | Pluggable discovery adapters for multiple lead sources |
| Data enrichment | Field normalization and entity resolution across heterogeneous sources |
| Deduplication | Rule-based and model-based matching with configurable similarity thresholds |
| Lead scoring | Composite scoring pipeline combining explicit rules and learned signals |
| Idempotent CRM sync | Salesforce upsert via ExternalId with safe retries and exponential backoff |
| Observability | `/metrics` endpoint with lead counts, qualification rates, and Salesforce call counts |
| Zero-dependency mode | Deterministic mock adapters for evaluation without external APIs |
| Repeatable execution | Stateless pipeline design with full run history and audit trail |

## Stack

| Layer | Tooling |
|---|---|
| Language | Python 3.11 |
| API | FastAPI + uvicorn |
| Data store | SQLite with SQLAlchemy 2.0 |
| Orchestration | Async pipeline with explicit stage boundaries |
| CRM integration | simple-salesforce (production) / mock adapter (development) |
| Enrichment | Pluggable adapter pattern (Clearbit-style in production) |
| Testing | pytest with pipeline fixtures |
| Infrastructure | Docker, Docker Compose |
| Observability | Prometheus `/metrics`, structured logging |

## Architecture

```
Lead Sources
    │
    ▼
Discovery Adapter (pluggable)
    │
    ▼
Enrichment + Normalization
    │
    ▼
Entity Resolution / Dedup
    │
    ▼
Scoring Pipeline (rules + model)
    │
    ▼
Qualification Gate
    │
    ▼
Salesforce Sync (idempotent upsert)
    │
    ▼
Run History + Metrics
```

### Pipeline stages

1. **Discovery**: Raw leads are fetched from configured sources through adapter functions. Mock mode generates deterministic synthetic leads.
2. **Enrichment**: Leads are normalized to a common schema. Fields are standardized (company names, titles, domains).
3. **Deduplication**: Entity resolution matches leads against existing records using configurable similarity thresholds. Matched leads are merged; new leads are staged.
4. **Scoring**: A composite score is computed from explicit rules (industry, title, company size) and model-based signals.
5. **Qualification**: Leads above a configurable threshold are marked qualified; others are archived for review.
6. **Sync**: Qualified leads are upserted to Salesforce using ExternalId for idempotency. Retries use exponential backoff with jitter.
7. **Observability**: Pipeline metrics are exposed via `/metrics`. Run history is persisted for audit.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Installation

```bash
git clone https://github.com/cjps4linux-creator/leadpilot.git
cd leadpilot

python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate   # Linux/macOS

pip install -r backend/requirements.txt
```

### Configuration

Set the following environment variables:

| Variable | Purpose |
|---|---|
| `MOCK_MODE` | `true` (default) for mock adapters, `false` for real APIs |
| `SALESFORCE_USERNAME` | Salesforce username (production mode) |
| `SALESFORCE_PASSWORD` | Salesforce password + security token (production mode) |
| `SALESFORCE_SECURITY_TOKEN` | Salesforce security token (production mode) |
| `DISCOVERY_API_KEY` | Lead discovery source API key (production mode) |
| `ENRICHMENT_API_KEY` | Data enrichment API key (production mode) |

### Run

```bash
# Mock mode (default — no external APIs required)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Execute the full pipeline
curl -X POST http://localhost:8000/run

# View qualified leads
curl "http://localhost:8000/leads?qualified=true"

# View pipeline metrics
curl http://localhost:8000/metrics
```

### Docker

```bash
docker build -f backend/Dockerfile -t leadpilot:latest .
docker run --rm -p 8000:8000 leadpilot:latest
```

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/run` | Execute the full pipeline (discover -> enrich -> score -> sync) |
| GET | `/leads` | View stored leads (supports `?qualified=true` filter) |
| GET | `/runs` | Pipeline run history with status and timing |
| GET | `/metrics` | Lead counts, qualification rates, Salesforce call counts |
| POST | `/reset` | Clear all stored state |

## Architecture Decision Records

### ADR-001: Idempotent Salesforce Sync via ExternalId

Salesforce upserts use ExternalId rather than name or email matching. This ensures that repeated pipeline runs do not create duplicate records and that retries after transient failures do not corrupt data. The ExternalId is derived from a stable composite of source identifier and normalized company domain.

### ADR-002: Mock Mode as Default

The pipeline runs in mock mode by default. This allows the entire system to be evaluated, demonstrated, and tested without external API dependencies. Real adapters are swapped in through environment configuration and adapter implementation, keeping the orchestration, scoring, dedup, and sync contracts unchanged.

### ADR-003: Composite Scoring Pipeline

Lead scoring combines explicit rules (industry fit, title seniority, company size) with model-based signals. This hybrid approach provides interpretability through the rule layer while capturing patterns that rules alone miss. The scoring contract is explicit: each lead receives a score, a qualification flag, and a breakdown of contributing factors.

## Honest Limitations

- Mock mode uses synthetic leads with deterministic scoring. Real-world lead quality depends on the accuracy of discovery and enrichment adapters, which are not implemented in this version.
- Salesforce integration is demonstrated with the `simple-salesforce` library but has not been tested against a live Salesforce instance with real data volumes.
- The entity resolution algorithm is a simple similarity threshold; production deployments should evaluate more sophisticated matching (fuzzy matching, ML-based entity resolution) for noisy datasets.
- No authentication or authorization is implemented on the API layer. Deploy behind a reverse proxy or API gateway for production access control.

## Current State

Functional prototype with complete pipeline architecture, mock adapters, idempotent sync design, and observability. The platform runs in zero-dependency mock mode and is structured for real adapter integration without changing the core orchestration logic.

## License

MIT — use, modify, and ship freely.

**Author:** Conrad CJ Wilson
**GitHub:** https://github.com/cjps4linux-creator
**LinkedIn:** https://www.linkedin.com/in/conradcjwilson
