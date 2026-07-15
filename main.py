from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.api.router import api_router
from src.db.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the FastAPI application.
    Runs startup logic (e.g., initializing DB) and teardown logic.
    """
    logger.info("Starting up FastAPI application...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database during startup: {e}")
        # Not raising here allows the app to start and serve 500s or health checks if needed,
        # but depending on the environment, raising might be preferred.
    
    yield
    
    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="Claude Code Analytics Platform API",
    description="Backend API for interacting with Employee and Telemetry Log data.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
