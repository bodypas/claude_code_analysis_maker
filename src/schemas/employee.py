from src.schemas.base import Base
from pydantic import ConfigDict


class EmployeeSchema(Base):
    """Pydantic schema for Employee data validation."""
    email: str
    full_name: str
    level: str
    location: str
    practice: str