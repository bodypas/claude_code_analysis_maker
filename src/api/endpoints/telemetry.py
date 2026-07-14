from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from src.api.dependencies import get_telemetry_service
from src.schemas.telemetry import (
    TelemetryLogSchema,
    UsageOverviewSchema,
    ActivityOverTimeSchema,
    CostBreakdownSchema,
    ToolUsageSchema,
    ErrorAnalysisSchema,
    TerminalBreakdownSchema,
    EventDistributionSchema,
)
from src.services.telemetry import TelemetryService

router = APIRouter()

@router.get("/usage-overview", response_model=UsageOverviewSchema)
async def get_usage_overview(service: TelemetryService = Depends(get_telemetry_service)):
    """Summary of total events and cost."""
    return await service.get_usage_overview()

@router.get("/activity-over-time", response_model=List[ActivityOverTimeSchema])
async def get_activity_over_time(service: TelemetryService = Depends(get_telemetry_service)):
    """Prompts and API requests grouped by time."""
    return await service.get_activity_over_time()

@router.get("/cost-breakdown", response_model=List[CostBreakdownSchema])
async def get_cost_breakdown(service: TelemetryService = Depends(get_telemetry_service)):
    """Cost and token usage by model."""
    return await service.get_cost_breakdown()

@router.get("/tool-usage", response_model=ToolUsageSchema)
async def get_tool_usage(service: TelemetryService = Depends(get_telemetry_service)):
    """Tool usage counts and success/decision rates."""
    return await service.get_tool_usage()

@router.get("/error-analysis", response_model=List[ErrorAnalysisSchema])
async def get_error_analysis(service: TelemetryService = Depends(get_telemetry_service)):
    """Error counts by model/message and average attempts."""
    return await service.get_error_analysis()

@router.get("/terminal-breakdown", response_model=List[TerminalBreakdownSchema])
async def get_terminal_breakdown(service: TelemetryService = Depends(get_telemetry_service)):
    """Events by terminal type."""
    return await service.get_terminal_breakdown()

@router.get("/event-type-distribution", response_model=List[EventDistributionSchema])
async def get_event_type_distribution(service: TelemetryService = Depends(get_telemetry_service)):
    """Count records across all event tables for distribution analysis."""
    return await service.get_event_type_distribution()

@router.post("/seed")
async def seed_telemetry(service: TelemetryService = Depends(get_telemetry_service)):
    """Seed telemetry data into the database."""
    try:
        await service.seed_telemetry(Path("data/output/telemetry_logs.jsonl"))
        return {"message": "Telemetry seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("")
async def delete_all_telemetry(service: TelemetryService = Depends(get_telemetry_service)):
    """Delete all telemetry data from the database."""
    try:
        await service.delete_all_telemetry()
        return {"message": "Telemetry deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

