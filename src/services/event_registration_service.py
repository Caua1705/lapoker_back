from uuid import UUID

from sqlalchemy.orm import Session

from src.core.enums import RegistrationStatus
from src.models import EventRegistration
from src.repositories import EventRegistrationRepository


class EventRegistrationService:
    def __init__(self, db: Session):
        self.db = db
        self.registration_repo = EventRegistrationRepository(db)

    def get_existing_registration(self, person_id: UUID, event_id: UUID) -> EventRegistration | None:
        return self.registration_repo.get_by_person_and_event(person_id, event_id)

    def create_pending_registration(self, person_id: UUID, event_id: UUID) -> EventRegistration:
        registration_data = {
            "person_id": person_id,
            "event_id": event_id,
            "status": RegistrationStatus.PENDING.value,
        }
        return self.registration_repo.create(registration_data)
