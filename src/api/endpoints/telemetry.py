from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from src.api.dependencies import get_telemetry_service
from src.schemas.telemetry import TelemetryLogSchema
from src.services.telemetry import TelemetryService

router = APIRouter()

@router.get("", response_model=List[TelemetryLogSchema])
async def list_telemetry_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Retrieve a paginated list of telemetry logs."""
    logs = await service.get_telemetry_logs(skip=skip, limit=limit)
    return [TelemetryLogSchema.model_validate(log) for log in logs]

@router.get("/usage-overview")
async def get_usage_overview(service: TelemetryService = Depends(get_telemetry_service)):
    """Summary of total events and cost."""
    return await service.get_usage_overview()

@router.get("/activity-over-time")
async def get_activity_over_time(service: TelemetryService = Depends(get_telemetry_service)):
    """Prompts and API requests grouped by time."""
    return await service.get_activity_over_time()

@router.get("/cost-breakdown")
async def get_cost_breakdown(service: TelemetryService = Depends(get_telemetry_service)):
    """Cost and token usage by model."""
    return await service.get_cost_breakdown()

@router.get("/tool-usage")
async def get_tool_usage(service: TelemetryService = Depends(get_telemetry_service)):
    """Tool usage counts and success/decision rates."""
    return await service.get_tool_usage()

@router.get("/error-analysis")
async def get_error_analysis(service: TelemetryService = Depends(get_telemetry_service)):
    """Error counts by model/message and average attempts."""
    return await service.get_error_analysis()

@router.get("/terminal-breakdown")
async def get_terminal_breakdown(service: TelemetryService = Depends(get_telemetry_service)):
    """Events by terminal type."""
    return await service.get_terminal_breakdown()

@router.get("/event-type-distribution")
async def get_event_type_distribution(service: TelemetryService = Depends(get_telemetry_service)):
    """Count records across all event tables for distribution analysis."""
    return await service.get_event_type_distribution()

@router.get("/metadata")
async def get_telemetry_metadata(service: TelemetryService = Depends(get_telemetry_service)):
    """Retrieve telemetry filter metadata."""
    return await service.get_telemetry_metadata()

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

