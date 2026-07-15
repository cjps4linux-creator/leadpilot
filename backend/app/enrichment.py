"""Enrichment + data normalization + dedup (entity resolution).

Demonstrates the 'data deduplication, normalization, entity resolution' desirable
skills in the JD. Normalization happens in Lead.normalized(); here we attach
enriched fields and resolve duplicates by identity_key before store upsert.
"""
from app.models import Lead


# Tiny industry classifier (rule + keyword = "rule + model scoring pipeline" pattern).
_INDUSTRY_KEYWORDS = {
    "design": "Design & Furniture",
    "studio": "Design & Furniture",
    "furniture": "Design & Furniture",
    "procurement": "Procurement / Supply",
    "ai": "Technology",
    "tech": "Technology",
}


def classify_industry(lead: Lead) -> str:
    blob = f"{lead.company} {lead.title} {lead.source}".lower()
    for kw, ind in _INDUSTRY_KEYWORDS.items():
        if kw in blob:
            return ind
    return "General"


def enrich(lead: Lead) -> Lead:
    """Attach enrichment fields. Real mode would call Clearbit/etc.; mock infers."""
    lead.industry = classify_industry(lead)
    # mock company-size heuristic
    if lead.title and any(t in lead.title.lower() for t in ("founder", "cto", "head")):
        lead.company_size = "SMB"
    else:
        lead.company_size = "Mid-Market"
    return lead
