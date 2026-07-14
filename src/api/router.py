from fastapi import APIRouter

from src.api.endpoints.employee import router as employee_router
from src.api.endpoints.telemetry import router as telemetry_router
from src.api.endpoints.ai import router as ai_router

api_router = APIRouter()

api_router.include_router(employee_router, prefix="/employees", tags=["Employees"])
api_router.include_router(telemetry_router, prefix="/telemetry", tags=["Telemetry"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
