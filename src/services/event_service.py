from sqlalchemy.orm import Session

from src.models import Event
from src.repositories import EventRepository


class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)

    def get_active_event(self) -> Event | None:
        return self.event_repo.get_active_event()
