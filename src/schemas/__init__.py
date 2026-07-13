from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class EmployeeSchema(BaseModel):
    """Pydantic schema for Employee data validation."""
    email: str
    full_name: str
    level: str
    location: str
    practice: str
    
    model_config = ConfigDict(from_attributes=True)


class TelemetryLogSchema(BaseModel):
    """Pydantic schema for Telemetry Log data validation."""
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    logGroup: Optional[str] = None
    logStream: Optional[str] = None
    messageType: Optional[str] = None
    owner: Optional[str] = None
    logEvents: Optional[List[Dict[str, Any]]] = None
    subscriptionFilters: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
