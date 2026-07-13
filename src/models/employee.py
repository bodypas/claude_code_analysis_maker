from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Employee(Base):
    """SQLAlchemy model for employees dataset."""
    __tablename__ = "employees"
    
    email: Mapped[str] = mapped_column(String, primary_key=True)
    full_name: Mapped[str] = mapped_column(String)
    level: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    practice: Mapped[str] = mapped_column(String)
