import logging

from sqlalchemy.orm import Session

from src.schemas.access_request import AccessRequestCreate, AccessRequestResponse
from src.services.person_service import PersonService
from src.services.event_service import EventService
from src.services.event_registration_service import EventRegistrationService
from src.services.email_service import EmailService

# from src.services.n8n_webhook_service import N8nWebhookService


logger = logging.getLogger(__name__)


class AccessRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.person_service = PersonService(db)
        self.event_service = EventService(db)
        self.registration_service = EventRegistrationService(db)
        self.email_service = EmailService()
        # self.webhook_service = N8nWebhookService()

    def submit_access_request(
        self,
        request_in: AccessRequestCreate,
    ) -> AccessRequestResponse:
        active_event = self.event_service.get_active_event()

        if not active_event:
            logger.warning("[access-request] No active event found.")

            return AccessRequestResponse(
                success=False,
                message="Nenhum evento ativo no momento.",
                registration_status="none",
            )

        person = self.person_service.get_or_create_person_by_phone(
            name=request_in.name,
            phone=request_in.phone,
            instagram=request_in.instagram,
            email=request_in.email,
        )

        existing = self.registration_service.get_existing_registration(
            person_id=person.id,
            event_id=active_event.id,
        )

        if existing:
            logger.info(
                "[access-request] Existing registration found. person_id=%s event_id=%s status=%s",
                person.id,
                active_event.id,
                existing.status,
            )

            self._send_emails_safely(
                name=request_in.name,
                email=str(request_in.email) if request_in.email else None,
                phone=request_in.phone,
                instagram=request_in.instagram,
            )

            return AccessRequestResponse(
                success=True,
                message="Sua solicitação já foi recebida.",
                registration_status=existing.status,
            )

        registration = self.registration_service.create_pending_registration(
            person_id=person.id,
            event_id=active_event.id,
        )

        logger.info(
            "[access-request] New registration created. person_id=%s event_id=%s registration_id=%s status=%s",
            person.id,
            active_event.id,
            registration.id,
            registration.status,
        )

        self._send_emails_safely(
            name=request_in.name,
            email=str(request_in.email) if request_in.email else None,
            phone=request_in.phone,
            instagram=request_in.instagram,
        )

        return AccessRequestResponse(
            success=True,
            message="Solicitação recebida com sucesso.",
            registration_status=registration.status,
        )

    def _send_emails_safely(
        self,
        name: str | None,
        email: str | None,
        phone: str | None,
        instagram: str | None,
    ) -> None:
        try:
            logger.info("[access-request] Sending user confirmation email to %s", email)

            self.email_service.send_access_confirmation_email(
                to_email=email,
                name=name,
            )

            logger.info("[access-request] User confirmation email flow finished.")
        except Exception:
            logger.exception("[access-request] Failed to send user confirmation email.")

        try:
            logger.info("[access-request] Sending admin notification email.")

            self.email_service.send_admin_access_notification(
                name=name,
                email=email,
                phone=phone,
                instagram=instagram,
            )

            logger.info("[access-request] Admin notification email flow finished.")
        except Exception:
            logger.exception("[access-request] Failed to send admin notification email.")