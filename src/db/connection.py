from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.models import Base

# Create async engine using the database URL from settings
engine = create_async_engine(settings.database_url, echo=False)

# Session factory for generating async sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db() -> None:
    """Initialize database schemas based on SQLAlchemy models."""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database schemas: {e}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for creating isolated async DB sessions.
    Gracefully handles session cleanup and rollback on errors.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
