import asyncio
from pathlib import Path

from loguru import logger

from src.db.connection import AsyncSessionLocal, init_db
from src.services.employee import EmployeeService
from src.services.telemetry import TelemetryService


async def main() -> None:
    """Main execution function to initialize DB and seed data."""
    logger.info("Starting database seeding process...")
    
    # Initialize DB schemas
    await init_db()
    
    base_dir = Path("data/output")
    employees_file = base_dir / "employees.csv"
    telemetry_file = base_dir / "telemetry_logs.jsonl"
    
    async with AsyncSessionLocal() as session:
        try:
            employee_service = EmployeeService(session)
            telemetry_service = TelemetryService(session)
            
            await employee_service.seed_employees(employees_file)
            await telemetry_service.seed_telemetry(telemetry_file)
        except Exception as e:
            logger.error(f"An unexpected error occurred during seeding: {e}")
            await session.rollback()
            
    logger.info("Database seeding process complete.")


if __name__ == "__main__":
    asyncio.run(main())
