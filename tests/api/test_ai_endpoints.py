import pytest
from fastapi.testclient import TestClient

from main import app
from src.api.dependencies import get_ai_service


# Mock service
class MockAIService:
    async def generate_telemetry_summary(self):
        return "Mocked AI Summary"

@pytest.fixture
def client():
    # Override dependency
    app.dependency_overrides[get_ai_service] = lambda: MockAIService()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_get_telemetry_summary(client):
    response = client.get("/api/v1/ai/telemetry-summary")
    assert response.status_code == 200
    assert response.json() == {"summary": "Mocked AI Summary"}
