from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.enums import RegistrationStatus


class EventRegistrationCreate(BaseModel):
    """Schema for creating an event registration."""
    person_id: UUID
    event_id: UUID
    status: RegistrationStatus = RegistrationStatus.PENDING


class EventRegistrationUpdate(BaseModel):
    """Schema for updating an event registration."""
    status: RegistrationStatus


class EventRegistrationResponse(BaseModel):
    """Schema for event registration response."""
    id: UUID
    person_id: UUID
    event_id: UUID
    status: RegistrationStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
