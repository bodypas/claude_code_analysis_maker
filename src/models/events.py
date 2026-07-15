from typing import Optional

from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin

from src.models.base import Base


@declarative_mixin
class EventBase:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_id: Mapped[int] = mapped_column(Integer, ForeignKey("telemetry_logs.id"))
    employee_email: Mapped[str] = mapped_column(String, index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    event_timestamp: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), index=True)
    terminal_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class UserPromptEvent(Base, EventBase):
    __tablename__ = "user_prompt_events"
    prompt_length: Mapped[int] = mapped_column(Integer)

class ToolDecisionEvent(Base, EventBase):
    __tablename__ = "tool_decision_events"
    tool_name: Mapped[str] = mapped_column(String, index=True)
    decision: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)

class ToolResultEvent(Base, EventBase):
    __tablename__ = "tool_result_events"
    tool_name: Mapped[str] = mapped_column(String, index=True)
    success: Mapped[bool] = mapped_column(Boolean)
    decision_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    decision_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer)
    tool_result_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class ApiRequestEvent(Base, EventBase):
    __tablename__ = "api_request_events"
    model: Mapped[str] = mapped_column(String, index=True)
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    cache_read_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cache_creation_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer)

class ApiErrorEvent(Base, EventBase):
    __tablename__ = "api_error_events"
    model: Mapped[str] = mapped_column(String, index=True)
    error: Mapped[str] = mapped_column(String)
    status_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attempt: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
