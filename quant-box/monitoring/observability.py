from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class JobRecord:
    job_name: str
    status: str
    started_at: str
    ended_at: str | None = None
    detail: dict | None = None


class MonitoringService:
    """In-memory monitoring helpers for MVP observability."""

    def __init__(self):
        self.jobs: dict[str, JobRecord] = {}
        self.alerts: list[dict] = []

    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def record_job_start(self, job_name: str) -> JobRecord:
        job = JobRecord(job_name=job_name, status="running", started_at=self.now())
        self.jobs[job_name] = job
        return job

    def record_job_end(self, job_name: str, status: str, detail: dict | None = None) -> JobRecord:
        existing = self.jobs.get(job_name)
        started_at = existing.started_at if existing else self.now()
        job = JobRecord(job_name=job_name, status=status, started_at=started_at, ended_at=self.now(), detail=detail or {})
        self.jobs[job_name] = job
        return job

    def job_status(self) -> list[dict]:
        return [vars(v) for v in self.jobs.values()]

    def data_freshness(self, latest_ts_iso: str | None, stale_after_seconds: int = 3600) -> dict:
        if not latest_ts_iso:
            return {"is_stale": True, "freshness_seconds": None, "stale_after_seconds": stale_after_seconds}
        latest = datetime.fromisoformat(latest_ts_iso.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - latest.astimezone(timezone.utc)).total_seconds()
        return {
            "is_stale": age > stale_after_seconds,
            "freshness_seconds": int(age),
            "stale_after_seconds": stale_after_seconds,
        }

    def system_metrics(self, counters: dict[str, int], health: dict[str, str]) -> dict:
        return {
            "timestamp": self.now(),
            "counters": counters,
            "services": health,
            "jobs_running": sum(1 for j in self.jobs.values() if j.status == "running"),
            "alerts_count": len(self.alerts),
        }

    def alert_if(self, condition: bool, name: str, payload: dict) -> None:
        if condition:
            self.alerts.append({"name": name, "payload": payload, "created_at": self.now()})
