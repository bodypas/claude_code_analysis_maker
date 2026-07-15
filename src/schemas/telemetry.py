from datetime import datetime
from typing import Any, Optional, List

from src.schemas.base import Base


class TelemetryLogSchema(Base):
    """Pydantic schema for Telemetry Log data validation."""
    employee_email: str
    timestamp: Optional[datetime] = None
    body: Optional[str] = None
    attributes: Optional[dict[str, Any]] = None
    scope: Optional[dict[str, Any]] = None
    resource: Optional[dict[str, Any]] = None


class UsageOverviewSchema(Base):
    total_prompts: int
    total_sessions: int
    total_tool_calls: int
    total_api_requests: int
    total_errors: int
    total_cost_usd: float


class ActivityOverTimeSchema(Base):
    day: str
    prompt_count: int
    request_count: int


class CostBreakdownSchema(Base):
    model: str
    cost: float
    input_tokens: int
    output_tokens: int


class ToolResultStats(Base):
    tool_name: str
    total_calls: int
    success_count: int


class ToolDecisionStats(Base):
    tool_name: str
    accepts: int
    rejects: int


class ToolUsageSchema(Base):
    results: List[ToolResultStats]
    decisions: List[ToolDecisionStats]


class ErrorAnalysisSchema(Base):
    model: str
    error: str
    count: int
    avg_attempts: float


class TerminalBreakdownSchema(Base):
    terminal_type: str
    count: int


class EventDistributionSchema(Base):
    event_type: str
    count: int