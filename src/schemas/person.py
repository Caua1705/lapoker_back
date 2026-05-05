from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PersonCreate(BaseModel):
    """Schema for creating a person."""
    name: str
    phone: str
    instagram: str | None = None
    email: str | None = None


class PersonUpdate(BaseModel):
    """Schema for updating a person."""
    name: str | None = None
    instagram: str | None = None
    email: str | None = None


class PersonResponse(BaseModel):
    """Schema for person response."""
    id: UUID
    name: str
    phone: str
    instagram: str | None = None
    email: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
