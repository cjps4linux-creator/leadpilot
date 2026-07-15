"""Per-run metrics: counts + timings + cost, observable for handoff."""
import threading


class RunMetrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.discovered = 0
        self.enriched = 0
        self.qualified = 0
        self.synced = 0
        self._lat = 0.0
        self.errors = 0

    def inc(self, field: str, n: int = 1):
        with self._lock:
            setattr(self, field, getattr(self, field) + n)

    def record_latency(self, s: float):
        with self._lock:
            self._lat += s

    def reset(self):
        with self._lock:
            self.discovered = 0
            self.enriched = 0
            self.qualified = 0
            self.synced = 0
            self._lat = 0.0
            self.errors = 0

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "discovered": self.discovered,
                "enriched": self.enriched,
                "qualified": self.qualified,
                "synced": self.synced,
                "errors": self.errors,
                "total_latency_s": round(self._lat, 3),
            }


metrics = RunMetrics()
