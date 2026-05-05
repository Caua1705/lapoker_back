from uuid import UUID

from sqlalchemy.orm import Session

from src.models import EventRegistration


class EventRegistrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_person_and_event(self, person_id: UUID, event_id: UUID) -> EventRegistration | None:
        return self.db.query(EventRegistration).filter(
            EventRegistration.person_id == person_id,
            EventRegistration.event_id == event_id,
        ).first()

    def create(self, registration_data: dict) -> EventRegistration:
        db_registration = EventRegistration(**registration_data)
        self.db.add(db_registration)
        self.db.commit()
        self.db.refresh(db_registration)
        return db_registration
