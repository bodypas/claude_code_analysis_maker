from typing import Optional, Any
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class TelemetryLog(Base):
    """SQLAlchemy model for telemetry_logs dataset."""
    __tablename__ = "telemetry_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_email: Mapped[str] = mapped_column(String)
    timestamp: Mapped[Optional[Any]] = mapped_column(DateTime)
    body: Mapped[Optional[str]] = mapped_column(String)
    attributes: Mapped[Optional[Any]] = mapped_column(JSONB)
    scope: Mapped[Optional[Any]] = mapped_column(JSONB)
    resource: Mapped[Optional[Any]] = mapped_column(JSONB)
