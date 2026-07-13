from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, populated from environment variables."""
    # Using asyncpg driver for async SQLAlchemy
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/analytics"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
