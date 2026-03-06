from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db: str
    heartbeat: str
    details: dict[str, Any] | None = None
