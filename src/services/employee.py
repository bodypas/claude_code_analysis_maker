import csv
from pathlib import Path
from typing import Sequence, Dict, Set, Optional, List

from loguru import logger
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.employee import Employee
from src.repositories.employee import EmployeeRepository
from src.schemas.employee import EmployeeSchema
from src.tools.schema_analyzer import analyze_csv_schema


class EmployeeService:
    """Service layer handling business logic for Employees."""

    def __init__(self, session: AsyncSession):
        self.repository = EmployeeRepository(session)

    async def get_employees(
        self,
        skip: int = 0,
        limit: int = 100,
        levels: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        practices: Optional[List[str]] = None,
        search_query: Optional[str] = None
    ) -> Sequence[Employee]:
        """Retrieves employees via the repository, optionally applying filters."""
        return await self.repository.get_filtered(
            skip=skip,
            limit=limit,
            levels=levels,
            locations=locations,
            practices=practices,
            search_query=search_query
        )

    async def analyze_employee_file(self, file_path: Path) -> Dict[str, Set[str]]:
        """Analyzes employee file schema."""
        return analyze_csv_schema(file_path)

    async def seed_employees(self, file_path: Path) -> None:
        """Seeds employee data into the database."""
        if not file_path.exists():
            logger.error(f"Employees file {file_path} not found.")
            raise FileNotFoundError(f"Employees file {file_path} not found.")

        logger.info(f"Seeding employees from {file_path}...")
        try:
            with file_path.open(mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        valid_data = EmployeeSchema(**row)
                        db_employee = Employee(**valid_data.model_dump())
                        await self.repository.add(db_employee)
                    except ValidationError as e:
                        logger.warning(f"Validation error for employee {row.get('email', 'unknown')}: {e}. Skipping.")
                    except Exception as e:
                        logger.error(f"Error processing employee row: {e}. Skipping.")
            await self.repository.commit()
            logger.info("Finished seeding employees.")
        except Exception as e:
            logger.error(f"Failed to read employees file {file_path}: {e}")
            raise

    async def delete_all_employees(self) -> None:
        """Deletes all employees from the database."""
        logger.info("Deleting all employees...")
        await self.repository.delete_all()
        await self.repository.commit()
        logger.info("Finished deleting all employees.")
