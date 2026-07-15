import json
from typing import Any, Dict

from fastapi.encoders import jsonable_encoder
from google import genai
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.schemas.telemetry import TelemetryAggregationSchema
from src.services.telemetry import TelemetryService


class AIService:
    """Service layer handling AI interactions."""

    def __init__(self, session: AsyncSession) -> None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
        self.telemetry_service = TelemetryService(session)

    async def aggregate_telemetry_data(self) -> TelemetryAggregationSchema:
        """Aggregates telemetry data for AI summary."""
        data = {
            "usage_overview": await self.telemetry_service.get_usage_overview(),
            "activity_over_time": await self.telemetry_service.get_activity_over_time(),
            "cost_breakdown": await self.telemetry_service.get_cost_breakdown(),
            "tool_usage": await self.telemetry_service.get_tool_usage(),
            "error_analysis": await self.telemetry_service.get_error_analysis(),
            "terminal_breakdown": await self.telemetry_service.get_terminal_breakdown(),
            "event_type_distribution": await self.telemetry_service.get_event_type_distribution(),
        }
        return TelemetryAggregationSchema(**data)

    async def generate_telemetry_summary(self) -> str:
        if not self.client:
            return "AI service is not configured (missing API key)."

        data = await self.aggregate_telemetry_data()

        # Use jsonable_encoder to handle non-serializable types like Decimal
        data_serializable = jsonable_encoder(data)

        prompt = f"""You are analyzing Claude Code usage data for an engineering org.
                    Here is the aggregated telemetry data (JSON):

                    {json.dumps(data_serializable, indent=2)}

                    Write a concise summary (4-6 bullet points) covering:
                    - Overall usage trend
                    - Notable cost patterns
                    - Tool adoption/trust signals (accept vs reject rates)
                    - Any reliability concerns (errors)
                    Keep it factual, grounded only in the numbers given. No speculation beyond the data."""

        try:
            # Using recommended client.models.generate_content
            response = self.client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return "Failed to generate AI summary."

