from typing import List, Optional, Sequence
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.employee import Employee
from src.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for managing Employee database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Employee)

    async def get_filtered(
        self,
        levels: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        practices: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Employee]:
        """Retrieves a filtered and paginated list of employees."""
        stmt = select(self.model)
        if levels:
            stmt = stmt.where(self.model.level.in_(levels))
        if locations:
            stmt = stmt.where(self.model.location.in_(locations))
        if practices:
            stmt = stmt.where(self.model.practice.in_(practices))
        if search_query:
            stmt = stmt.where(
                or_(
                    self.model.full_name.ilike(f"%{search_query}%"),
                    self.model.email.ilike(f"%{search_query}%")
                )
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
