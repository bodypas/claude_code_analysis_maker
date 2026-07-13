from typing import TypeVar, Generic, Sequence, Type
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
    """Base repository with common database operations."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieves a paginated list of items from the database."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_unlimited(self) -> Sequence[ModelType]:
        """Retrieves all items from the database without pagination."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, item: ModelType) -> None:
        """Adds a new item to the database session."""
        self.session.add(item)

    async def delete_all(self) -> None:
        """Deletes all items from the table."""
        stmt = delete(self.model)
        await self.session.execute(stmt)

    async def commit(self) -> None:
        """Commits the current transaction."""
        await self.session.commit()
