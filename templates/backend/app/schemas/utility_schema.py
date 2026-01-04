from pydantic import BaseModel


class DatabaseVersionResponse(BaseModel):
    """Response schema for database version endpoint."""
    version: str
    status: str = "success"

