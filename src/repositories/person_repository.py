from sqlalchemy.orm import Session

from src.models import Person


class PersonRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_phone(self, phone: str) -> Person | None:
        return self.db.query(Person).filter(Person.phone == phone).first()

    def create(self, person_data: dict) -> Person:
        db_person = Person(**person_data)
        self.db.add(db_person)
        self.db.commit()
        self.db.refresh(db_person)
        return db_person

    def update(self, person: Person, update_data: dict) -> Person:
        for key, value in update_data.items():
            if value is not None:
                setattr(person, key, value)
        self.db.commit()
        self.db.refresh(person)
        return person
