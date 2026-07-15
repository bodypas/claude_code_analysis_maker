from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException

from src.api.dependencies import get_employee_service
from src.schemas.employee import EmployeeSchema
from src.services.employee import EmployeeService

router = APIRouter()


@router.get("", response_model=List[EmployeeSchema])
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: EmployeeService = Depends(get_employee_service)
) -> List[EmployeeSchema]:
    """
    Retrieve a paginated list of employees.
    """
    return await service.get_employees(skip=skip, limit=limit)


@router.post("/seed")
async def seed_employees(service: EmployeeService = Depends(get_employee_service)):
    """
    Seed employee data into the database.
    """
    try:
        await service.seed_employees(Path("data/output/employees.csv"))
        return {"message": "Employees seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("")
async def delete_all_employees(service: EmployeeService = Depends(get_employee_service)):
    """
    Delete all employee data from the database.
    """
    try:
        await service.delete_all_employees()
        return {"message": "Employees deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
