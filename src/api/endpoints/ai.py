from fastapi import APIRouter, Depends

from src.api.dependencies import get_ai_service
from src.schemas.ai import TelemetrySummaryResponse
from src.services.ai import AIService

router = APIRouter()

@router.get("/telemetry-summary", response_model=TelemetrySummaryResponse)
async def get_telemetry_summary(
    ai_service: AIService = Depends(get_ai_service)
):
    """Generates an AI summary report for telemetry data."""
    summary = await ai_service.generate_telemetry_summary()
    
    return TelemetrySummaryResponse(summary=summary)
