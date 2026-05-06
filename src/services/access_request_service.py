from sqlalchemy.orm import Session

from src.schemas.access_request import AccessRequestCreate, AccessRequestResponse
from src.services.person_service import PersonService
from src.services.event_service import EventService
from src.services.event_registration_service import EventRegistrationService
from src.services.n8n_webhook_service import N8nWebhookService


class AccessRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.person_service = PersonService(db)
        self.event_service = EventService(db)
        self.registration_service = EventRegistrationService(db)
        self.webhook_service = N8nWebhookService()

    def submit_access_request(self, request_in: AccessRequestCreate) -> AccessRequestResponse:
        # 1. Find the current active event
        active_event = self.event_service.get_active_event()

        if not active_event:
            return AccessRequestResponse(
                success=False,
                message="Nenhum evento ativo no momento.",
                registration_status="none",
            )

        # 2. Get or create the person using phone as the main identifier
        person = self.person_service.get_or_create_person_by_phone(
            name=request_in.name,
            phone=request_in.phone,
            instagram=request_in.instagram,
            email=request_in.email,
        )

        # 3. Check if this person is already registered for the active event
        existing = self.registration_service.get_existing_registration(
            person_id=person.id,
            event_id=active_event.id,
        )

        if existing:
            return AccessRequestResponse(
                success=True,
                message="Sua solicitação já foi recebida.",
                registration_status=existing.status,
            )

        # 4. Create a new registration with status "pending"
        registration = self.registration_service.create_pending_registration(
            person_id=person.id,
            event_id=active_event.id,
        )

        # 5. Notify n8n (non-blocking – webhook failures must not affect the response)
        self.webhook_service.trigger_access_request({
            "name": person.name,
            "phone": person.phone,
            "instagram": person.instagram,
            "email": person.email,
            "registration_id": str(registration.id),
            "event_id": str(active_event.id),
            "event_name": active_event.name,
            "registration_status": registration.status,
        })

        return AccessRequestResponse(
            success=True,
            message="Solicitação recebida com sucesso.",
            registration_status=registration.status,
        )
