"""Lead sources / discovery. Pluggable adapters; mock source generates
realistic records to demonstrate the full pipeline headless."""
from app.models import Lead
from app.config import MOCK_MODE


def _mock_source() -> list[Lead]:
    """Synthetic but realistic discovery output (demonstrates entity resolution)."""
    return [
        Lead(name="Jane Doe", company="acme corp", title="CTO", email="jane@acme.com",
             source="mock", raw={"query": "ai design leads"}),
        Lead(name="jane doe", company="Acme Corp", title="Chief Technology Officer",
             email="JANE@ACME.COM", source="mock", raw={"query": "acme expansion"}),
        Lead(name="Carlos Ruiz", company="studio norte", title="Founder",
             email="carlos@studionorte.io", source="mock", raw={"query": "design studios"}),
        Lead(name="Mei Lin", company="northwind", title="Head of Procurement",
             email="mei@northwind.co", source="mock", raw={"query": "furniture buyers"}),
        Lead(name="Mei Lin", company="Northwind", title="Procurement Lead",
             email="mei@northwind.co", source="mock", raw={"query": "northwind repeat"}),
    ]


def discover() -> list[Lead]:
    """Return raw discovered leads. Swap mock for a real API adapter (Apify, etc.)."""
    if MOCK_MODE:
        return _mock_source()
    # Real adapter would call a discovery API here and map to Lead objects.
    raise NotImplementedError("Set MOCK_MODE=true or implement a real source adapter.")
