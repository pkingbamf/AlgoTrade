from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db: str
    heartbeat: str
