from pydantic import BaseModel, Field
from typing import Optional


class Lead(BaseModel):
    """Normalized lead entity. Stable identity = (email or normalized company+name)."""
    id: Optional[int] = None
    email: Optional[str] = None
    name: str
    company: str
    title: Optional[str] = None
    source: str = "unknown"
    # enrichment
    industry: Optional[str] = None
    company_size: Optional[str] = None
    # scoring
    score: float = 0.0
    qualified: bool = False
    # sync
    sf_id: Optional[str] = None
    last_sync_status: Optional[str] = None
    # provenance
    raw: dict = Field(default_factory=dict)

    def identity_key(self) -> str:
        """Deterministic dedup key for entity resolution."""
        if self.email:
            return f"email:{self.email.strip().lower()}"
        comp = "".join(c for c in self.company.lower() if c.isalnum())
        nm = "".join(c for c in self.name.lower() if c.isalnum())
        return f"co:{comp}|nm:{nm}"

    def normalized(self) -> "Lead":
        """Data normalization: trim, lowercase email, title-case name/company."""
        self.email = self.email.strip().lower() if self.email else None
        self.name = self.name.strip().title()
        self.company = self.company.strip().title()
        self.title = self.title.strip() if self.title else None
        return self
