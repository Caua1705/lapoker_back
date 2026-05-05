from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.enums import EventStatus


class EventCreate(BaseModel):
    """Schema for creating an event."""
    name: str
    event_date: date
    status: EventStatus = EventStatus.DRAFT


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    name: str | None = None
    event_date: date | None = None
    status: EventStatus | None = None


class EventResponse(BaseModel):
    """Schema for event response."""
    id: UUID
    name: str
    event_date: date
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
