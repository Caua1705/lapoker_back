import logging

from sqlalchemy.exc import IntegrityError
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
                code="no_active_event",
                message="Nenhum evento ativo no momento.",
                name=None,
                email=None,
                delivery_method="email",
                registration_status="none",
            )

        email = str(request_in.email).strip().lower()
        person = self.person_service.get_or_create_person_by_email(
            name=request_in.name,
            email=email,
            phone=request_in.phone,
            instagram=request_in.instagram,
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

            return AccessRequestResponse(
                success=False,
                code="already_registered",
                message="Este e-mail já está cadastrado para este evento.",
                name=person.name,
                email=person.email,
                delivery_method="email",
                registration_status=existing.status,
            )

        try:
            registration = self.registration_service.create_pending_registration(
                person_id=person.id,
                event_id=active_event.id,
            )
        except IntegrityError:
            self.db.rollback()
            existing = self.registration_service.get_existing_registration(
                person_id=person.id,
                event_id=active_event.id,
            )
            if existing:
                logger.info(
                    "[access-request] Registration already existed after integrity error. person_id=%s event_id=%s status=%s",
                    person.id,
                    active_event.id,
                    existing.status,
                )
                return AccessRequestResponse(
                    success=False,
                    code="already_registered",
                    message="Este e-mail já está cadastrado para este evento.",
                    name=person.name,
                    email=person.email,
                    delivery_method="email",
                    registration_status=existing.status,
                )
            raise

        logger.info(
            "[access-request] New registration created. person_id=%s event_id=%s registration_id=%s status=%s",
            person.id,
            active_event.id,
            registration.id,
            registration.status,
        )

        self._send_emails_safely(
            name=person.name,
            email=email,
            phone=request_in.phone,
            instagram=request_in.instagram,
        )

        return AccessRequestResponse(
            success=True,
            code="created",
            message="Convite enviado com sucesso.",
            name=person.name,
            email=email,
            delivery_method="email",
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
