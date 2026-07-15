import pytest
from fastapi.testclient import TestClient

from main import app
from src.api.dependencies import get_telemetry_service


# Mock service
class MockTelemetryService:
    async def get_usage_overview(self):
        return {
            "total_prompts": 10,
            "total_sessions": 2,
            "total_tool_calls": 5,
            "total_api_requests": 3,
            "total_errors": 0,
            "total_cost_usd": 0.05
        }
    
    async def get_activity_over_time(self):
        return [{"day": "2026-07-14", "prompt_count": 5, "request_count": 2}]

    async def get_cost_breakdown(self):
        return [{"model": "claude-3-5-sonnet", "cost": 0.05, "input_tokens": 100, "output_tokens": 50}]

    async def get_tool_usage(self):
        return {
            "results": [{"tool_name": "search", "total_calls": 2, "success_count": 2}],
            "decisions": [{"tool_name": "search", "accepts": 1, "rejects": 0}]
        }

    async def get_error_analysis(self):
        return [{"model": "claude-3-5-sonnet", "error": "timeout", "count": 1, "avg_attempts": 1.0}]

    async def get_terminal_breakdown(self):
        return [{"terminal_type": "vscode", "count": 10}]

    async def get_event_type_distribution(self):
        return [{"event_type": "User Prompt", "count": 10}]
    
    async def seed_telemetry(self, path):
        return None
    
    async def delete_all_telemetry(self):
        return None

@pytest.fixture
def client():
    # Override dependency
    app.dependency_overrides[get_telemetry_service] = lambda: MockTelemetryService()
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_get_usage_overview(client):
    response = client.get("/api/v1/telemetry/usage-overview")
    assert response.status_code == 200
    assert response.json() == {
        "total_prompts": 10,
        "total_sessions": 2,
        "total_tool_calls": 5,
        "total_api_requests": 3,
        "total_errors": 0,
        "total_cost_usd": 0.05
    }
