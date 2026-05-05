from sqlalchemy.orm import Session

from src.core.enums import EventStatus
from src.models import Event


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_event(self) -> Event | None:
        return self.db.query(Event).filter(Event.status == EventStatus.ACTIVE.value).first()
