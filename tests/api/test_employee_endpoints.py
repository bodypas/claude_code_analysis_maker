import pytest
from fastapi.testclient import TestClient
from main import app
from src.api.dependencies import get_employee_service
from src.schemas.employee import EmployeeSchema
from typing import List

# Mock service
class MockEmployeeService:
    async def get_employees(self, skip: int, limit: int) -> List[dict]:
        return [{"id": 1, "full_name": "John Doe", "email": "john@example.com", "level": "L1", "location": "US", "practice": "Dev"}]
    
    async def seed_employees(self, path):
        return None
    
    async def delete_all_employees(self):
        return None

@pytest.fixture
def client():
    # Override dependency
    app.dependency_overrides[get_employee_service] = lambda: MockEmployeeService()
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

def test_list_employees(client):
    response = client.get("/api/v1/employees?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["full_name"] == "John Doe"

def test_seed_employees(client):
    response = client.post("/api/v1/employees/seed")
    assert response.status_code == 200
    assert response.json() == {"message": "Employees seeded successfully"}

def test_delete_employees(client):
    response = client.delete("/api/v1/employees")
    assert response.status_code == 200
    assert response.json() == {"message": "Employees deleted successfully"}
