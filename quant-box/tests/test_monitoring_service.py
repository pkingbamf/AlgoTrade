from datetime import datetime, timedelta, timezone

from monitoring.observability import MonitoringService


def test_job_lifecycle_tracking():
    svc = MonitoringService()
    svc.record_job_start("exp")
    svc.record_job_end("exp", "completed", {"n": 1})
    jobs = svc.job_status()
    assert len(jobs) == 1
    assert jobs[0]["status"] == "completed"


def test_data_freshness_and_alert_hook():
    svc = MonitoringService()
    stale_ts = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    freshness = svc.data_freshness(stale_ts, stale_after_seconds=3600)
    assert freshness["is_stale"]
    svc.alert_if(freshness["is_stale"], "stale_data", freshness)
    assert len(svc.alerts) == 1
