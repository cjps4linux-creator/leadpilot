"""Scoring: rule-based feature extraction + model/classification signal combined.

This is the 'rule + model scoring pipeline' the JD names. In mock mode we use a
deterministic rule score; the architecture accepts a model signal (classifier
probability) added on top, and the two are combined with explicit weights.
"""
from app.models import Lead
from app.config import QUALIFIED_THRESHOLD


def rule_score(lead: Lead) -> float:
    s = 0.0
    if lead.email:
        s += 0.25
    if lead.title:
        s += 0.15
    # seniority signal
    title = (lead.title or "").lower()
    if any(t in title for t in ("cto", "founder", "head", "vp", "director")):
        s += 0.30
    if lead.industry in ("Design & Furniture", "Technology"):
        s += 0.20
    if lead.company_size in ("SMB", "Mid-Market"):
        s += 0.10
    return min(s, 1.0)


def model_signal(lead: Lead) -> float:
    """Deterministic pseudo-score from identity (stable across runs/processes).
    Stands in for a classifier probability in real mode."""
    import hashlib
    h = hashlib.sha256(lead.identity_key().encode()).hexdigest()
    return round(int(h[:4], 16) / 0xFFFF * 0.19 + 0.10, 3)  # 0.10..0.29


def score_lead(lead: Lead, rule_w: float = 0.7, model_w: float = 0.3) -> Lead:
    r = rule_score(lead)
    m = model_signal(lead)
    combined = round(r * rule_w + m * model_w, 3)
    lead.score = combined
    lead.qualified = combined >= QUALIFIED_THRESHOLD
    return lead
