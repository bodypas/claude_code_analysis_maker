from typing import Any, Optional
from datetime import datetime
from src.schemas.base import Base


class TelemetryLogSchema(Base):
    """Pydantic schema for Telemetry Log data validation."""
    employee_email: str
    timestamp: Optional[datetime] = None
    body: Optional[str] = None
    attributes: Optional[dict[str, Any]] = None
    scope: Optional[dict[str, Any]] = None
    resource: Optional[dict[str, Any]] = None