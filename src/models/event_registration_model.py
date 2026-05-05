import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.enums import RegistrationStatus
from src.db.base import Base


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    __table_args__ = (
        UniqueConstraint("person_id", "event_id", name="uq_person_event"),
        {"schema": "lapoker"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lapoker.people.id", ondelete="RESTRICT"),
        nullable=False,
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lapoker.events.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RegistrationStatus.PENDING.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    person: Mapped["Person"] = relationship(
        "Person",
        back_populates="registrations",
    )

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="registrations",
    )
