from datetime import datetime, timezone


def heartbeat() -> str:
    return datetime.now(timezone.utc).isoformat()
