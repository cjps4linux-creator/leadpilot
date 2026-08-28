from pydantic import BaseModel, Field
# Removed Optional in favor of X | None


class Lead(BaseModel):
    """Normalized lead entity. Stable identity = (email or normalized company+name)."""
    id: int | None = None
    email: str | None = None
    name: str
    company: str
    title: str | None = None
    source: str = "unknown"
    # enrichment
    industry: str | None = None
    company_size: str | None = None
    # scoring
    score: float = 0.0
    qualified: bool = False
    # sync
    sf_id: str | None = None
    last_sync_status: str | None = None
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
