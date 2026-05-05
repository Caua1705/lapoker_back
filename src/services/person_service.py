from sqlalchemy.orm import Session

from src.models import Person
from src.repositories import PersonRepository


class PersonService:
    def __init__(self, db: Session):
        self.db = db
        self.person_repo = PersonRepository(db)

    def create_or_update_person_by_phone(
        self,
        name: str,
        phone: str,
        instagram: str | None = None,
        email: str | None = None,
    ) -> Person:
        person = self.person_repo.get_by_phone(phone)

        if person:
            update_data = {
                "name": name,
                "instagram": instagram,
                "email": email,
            }
            return self.person_repo.update(person, update_data)

        person_data = {
            "name": name,
            "phone": phone,
            "instagram": instagram,
            "email": email,
        }
        return self.person_repo.create(person_data)
