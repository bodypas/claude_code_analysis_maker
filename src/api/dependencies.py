from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import get_session
from src.services.employee import EmployeeService
from src.services.telemetry import TelemetryService
from src.services.ai import AIService


def get_employee_service(session: AsyncSession = Depends(get_session)) -> EmployeeService:
    """Dependency to provide EmployeeService."""
    return EmployeeService(session)


def get_telemetry_service(session: AsyncSession = Depends(get_session)) -> TelemetryService:
    """Dependency to provide TelemetryService."""
    return TelemetryService(session)

def get_ai_service(session: AsyncSession = Depends(get_session)) -> AIService:
    """Dependency to provide AIService."""
    return AIService(session)