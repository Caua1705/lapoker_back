import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import Person
from src.repositories import PersonRepository


logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, db: Session):
        self.db = db
        self.person_repo = PersonRepository(db)

    def get_or_create_person_by_phone(
        self,
        name: str,
        phone: str,
        instagram: str | None = None,
        email: str | None = None,
    ) -> Person:
        person = self.person_repo.get_by_phone(phone)

        if person:
            return person

        person_data = {
            "name": name,
            "phone": phone,
            "instagram": instagram,
            "email": email,
        }
        return self.person_repo.create(person_data)

    def get_person_by_email(self, email: str) -> Person | None:
        return self.person_repo.get_by_email(email.strip().lower())

    def get_or_create_person_by_email(
        self,
        name: str,
        email: str,
        phone: str | None = None,
        instagram: str | None = None,
    ) -> Person:
        normalized_email = email.strip().lower()
        person = self.get_person_by_email(normalized_email)

        if person:
            return self.update_missing_person_fields(
                person=person,
                name=name,
                phone=phone,
                instagram=instagram,
            )

        person_data = {
            "name": name,
            "email": normalized_email,
            "phone": phone,
            "instagram": instagram,
        }
        try:
            return self.person_repo.create(person_data)
        except IntegrityError:
            self.db.rollback()
            person = self.get_person_by_email(normalized_email)
            if person:
                return person

            if phone:
                logger.warning(
                    "[person] Person creation failed with phone metadata. Retrying without phone. email=%s",
                    normalized_email,
                )
                person_data["phone"] = None
                return self.person_repo.create(person_data)

            raise

    def update_missing_person_fields(
        self,
        person: Person,
        name: str | None = None,
        phone: str | None = None,
        instagram: str | None = None,
    ) -> Person:
        updates = {}

        if name and not person.name:
            updates["name"] = name

        if phone and not person.phone:
            updates["phone"] = phone

        if instagram and not person.instagram:
            updates["instagram"] = instagram

        if not updates:
            return person

        try:
            return self.person_repo.update(person, updates)
        except IntegrityError:
            self.db.rollback()
            logger.warning("[person] Optional person field update skipped. person_id=%s", person.id)
            return person
