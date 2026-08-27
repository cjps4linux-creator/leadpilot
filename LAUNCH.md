# leadpilot — Launch Readiness

**Date:** 2026-08-27
**Owner:** Conrad CJ Wilson
**Repo:** cjps4linux-creator/leadpilot
**Status:** Functional prototype

---

## Readiness Snapshot

| Gate | Status | Evidence |
|---|---|---|
| CI passing | Pending | GitHub Actions workflow defined |
| Tests passing | Pending | pytest fixtures in `backend/tests/` |
| Security scan | Pending | SECURITY.md in place |
| README complete | Complete | Architecture, pipeline stages, ADRs, honest limitations |
| LICENSE | Complete | MIT — Conrad CJ Wilson |
| Docker build | Complete | Dockerfile + docker-compose.yml present |
| Documentation | Complete | API endpoints, configuration table, architecture diagram |

---

## Requirements

- Python 3.11+
- Docker (optional, for containerized deployment)
- Salesforce credentials (for production mode; mock mode requires nothing)

---

## Known Gaps

- CI has not been verified running on GitHub Actions for this commit
- Salesforce integration has not been tested against a live instance
- Entity resolution uses simple similarity thresholds; production deployments should evaluate ML-based matching
- No authentication layer on the API; deploy behind reverse proxy for production

---

## Actions Required Before Production

1. Verify CI passes on GitHub Actions
2. Test Salesforce integration with live sandbox
3. Enable GitHub secret scanning and vulnerability alerts
4. Configure branch protection with required status checks
5. Add authentication/authorization layer for production deployment

---

## Contact

Conrad CJ Wilson — conradcjwilson0@gmail.com
