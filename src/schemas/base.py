from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    """Base Pydantic model with common configuration."""
    model_config = ConfigDict(from_attributes=True)