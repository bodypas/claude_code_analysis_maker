from typing import List, Optional, Sequence, Any, Dict
import sqlalchemy
from sqlalchemy import select, func, cast, String, Integer, Float, case, desc, Date
from sqlalchemy.ext.asyncio import AsyncSession


from src.models.telemetry import TelemetryLog
from src.models.events import (
    UserPromptEvent,
    ToolDecisionEvent,
    ToolResultEvent,
    ApiRequestEvent,
    ApiErrorEvent,
)
from src.repositories.base import BaseRepository


class TelemetryRepository(BaseRepository[TelemetryLog]):
    """Repository for managing TelemetryLog database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TelemetryLog)

    # --- Analytics Queries ---

    async def get_usage_overview(self) -> Dict[str, Any]:
        prompts = await self.session.scalar(select(func.count()).select_from(UserPromptEvent))
        tools = await self.session.scalar(select(func.count()).select_from(ToolDecisionEvent))
        results = await self.session.scalar(select(func.count()).select_from(ToolResultEvent))
        requests = await self.session.scalar(select(func.count()).select_from(ApiRequestEvent))
        errors = await self.session.scalar(select(func.count()).select_from(ApiErrorEvent))
        sessions = await self.session.scalar(select(func.count(func.distinct(TelemetryLog.attributes["session.id"]))).select_from(TelemetryLog))
        cost = await self.session.scalar(select(func.sum(ApiRequestEvent.cost_usd)).select_from(ApiRequestEvent))
        
        return {
            "total_prompts": prompts or 0,
            "total_sessions": sessions or 0,
            "total_tool_calls": (tools or 0) + (results or 0),
            "total_api_requests": requests or 0,
            "total_errors": errors or 0,
            "total_cost_usd": float(cost or 0)
        }

    async def get_activity_over_time(self) -> List[Dict[str, Any]]:
        # Query Prompts
        prompts_res = await self.session.execute(
            select(
                func.cast(UserPromptEvent.event_timestamp, Date).label("day"), 
                func.count().label("prompt_count")
            )
            .group_by(func.cast(UserPromptEvent.event_timestamp, Date))
            .order_by(func.cast(UserPromptEvent.event_timestamp, Date))
        )
        
        # Query Requests
        requests_res = await self.session.execute(
            select(
                func.cast(ApiRequestEvent.event_timestamp, Date).label("day"), 
                func.count().label("request_count")
            )
            .select_from(ApiRequestEvent)
            .group_by(func.cast(ApiRequestEvent.event_timestamp, Date))
            .order_by(func.cast(ApiRequestEvent.event_timestamp, Date))
        )
        
        prompt_map = {row.day: row.prompt_count for row in prompts_res.all()}
        request_map = {row.day: row.request_count for row in requests_res.all()}

        all_days = sorted(set(prompt_map.keys()) | set(request_map.keys()))

        return [
            {
                "day": str(day),
                "prompt_count": prompt_map.get(day, 0),
                "request_count": request_map.get(day, 0),
            }
            for day in all_days
        ]

    async def get_cost_breakdown(self) -> List[Dict[str, Any]]:
        stmt = select(
            ApiRequestEvent.model,
            func.sum(ApiRequestEvent.cost_usd).label("cost"),
            func.sum(ApiRequestEvent.input_tokens).label("input_tokens"),
            func.sum(ApiRequestEvent.output_tokens).label("output_tokens")
        ).group_by(ApiRequestEvent.model)
        result = await self.session.execute(stmt)
        return [{"model": r.model, "cost": r.cost or 0, "input_tokens": r.input_tokens or 0, "output_tokens": r.output_tokens or 0} for r in result.all()]

    async def get_tool_usage(self) -> Dict[str, List[Dict[str, Any]]]:
        results = await self.session.execute(
            select(
                ToolResultEvent.tool_name,
                func.count().label("total_calls"),
                func.sum(cast(ToolResultEvent.success, Integer)).label("success_count")
            ).group_by(ToolResultEvent.tool_name)
        )
        decisions = await self.session.execute(
            select(
                ToolDecisionEvent.tool_name,
                func.sum(case((ToolDecisionEvent.decision == 'accept', 1), else_=0)).label("accepts"),
                func.sum(case((ToolDecisionEvent.decision == 'reject', 1), else_=0)).label("rejects")
            ).group_by(ToolDecisionEvent.tool_name)
        )
        return {"results": [r._asdict() for r in results.all()], "decisions": [d._asdict() for d in decisions.all()]}

    async def get_error_analysis(self) -> List[Dict[str, Any]]:
        stmt = select(
            ApiErrorEvent.model,
            ApiErrorEvent.error,
            func.count().label("count"),
            func.avg(ApiErrorEvent.attempt).label("avg_attempts")
        ).group_by(ApiErrorEvent.model, ApiErrorEvent.error)
        result = await self.session.execute(stmt)
        return [r._asdict() for r in result.all()]

    async def get_terminal_breakdown(self) -> List[Dict[str, Any]]:
        stmt = select(
            UserPromptEvent.terminal_type,
            func.count().label("count")
        ).group_by(UserPromptEvent.terminal_type)
        result = await self.session.execute(stmt)
        return [r._asdict() for r in result.all()]

    async def get_event_type_distribution(self) -> List[Dict[str, Any]]:
        """Counts records across all event tables for distribution analysis."""
        
        counts = [
            {"event_type": "User Prompt", "count": await self.session.scalar(select(func.count()).select_from(UserPromptEvent))},
            {"event_type": "Tool Decision", "count": await self.session.scalar(select(func.count()).select_from(ToolDecisionEvent))},
            {"event_type": "Tool Result", "count": await self.session.scalar(select(func.count()).select_from(ToolResultEvent))},
            {"event_type": "API Request", "count": await self.session.scalar(select(func.count()).select_from(ApiRequestEvent))},
            {"event_type": "API Error", "count": await self.session.scalar(select(func.count()).select_from(ApiErrorEvent))},
        ]
        return counts

    # --- Existing Methods ---

    async def get_filtered_metrics(
        self,
        practices: Optional[List[str]] = None,
        emails: Optional[List[str]] = None,
        terminal_types: Optional[List[str]] = None
    ) -> Sequence[TelemetryLog]:
        """Retrieves filtered telemetry logs using SQL."""
        stmt = select(TelemetryLog)
        
        if practices:
            stmt = stmt.where(TelemetryLog.attributes["user.practice"].as_string().in_(practices))
        if emails:
            stmt = stmt.where(TelemetryLog.employee_email.in_(emails))
        if terminal_types:
            stmt = stmt.where(TelemetryLog.attributes["terminal.type"].as_string().in_(terminal_types))
            
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_telemetry_stats(self) -> dict:
        """Retrieves aggregated telemetry stats using SQL."""
        # Helper to extract JSONB key as float
        def get_jsonb_float(col, key):
            return cast(col[key].astext, sqlalchemy.Float)

        # 1. Daily Cost
        daily_cost_stmt = select(
            func.date(TelemetryLog.timestamp).label("date"),
            func.sum(get_jsonb_float(TelemetryLog.attributes, "cost_usd")).label("total_cost")
        ).group_by(func.date(TelemetryLog.timestamp))
        daily_cost = await self.session.execute(daily_cost_stmt)
        
        # 2. Cost by Event
        event_name_expr = TelemetryLog.attributes["event.name"].astext
        cost_by_event_stmt = select(
            event_name_expr.label("event_name"),
            func.sum(get_jsonb_float(TelemetryLog.attributes, "cost_usd")).label("total_cost")
        ).group_by(event_name_expr)
        cost_by_event = await self.session.execute(cost_by_event_stmt)
        
        # 3. Tool Usage
        tool_name_expr = TelemetryLog.attributes["tool_name"].astext
        tool_usage_stmt = select(
            tool_name_expr.label("tool_name"),
            func.count().label("count")
        ).where(tool_name_expr != "unknown").group_by(tool_name_expr)
        tool_usage = await self.session.execute(tool_usage_stmt)
        
        return {
            "daily_cost": [{"date": str(row.date), "cost": row.total_cost or 0} for row in daily_cost.all()],
            "cost_by_event": [{"event_name": row.event_name, "cost": row.total_cost or 0} for row in cost_by_event.all()],
            "tool_usage": [{"tool_name": row.tool_name, "count": row.count} for row in tool_usage.all()]
        }

    async def get_telemetry_metadata(self) -> dict:
        """Retrieves filter metadata using database-level DISTINCT queries."""
        practices = await self.session.execute(
            select(func.distinct(TelemetryLog.attributes["user.practice"].as_string()))
        )
        emails = await self.session.execute(
            select(func.distinct(TelemetryLog.employee_email))
        )
        terminal_types = await self.session.execute(
            select(func.distinct(TelemetryLog.attributes["terminal.type"].as_string()))
        )
        
        return {
            "practices": sorted([p for p in practices.scalars().all() if p is not None]),
            "emails": sorted([e for e in emails.scalars().all() if e is not None]),
            "terminal_types": sorted([t for t in terminal_types.scalars().all() if t is not None])
        }


