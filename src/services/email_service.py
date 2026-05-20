import logging
import smtplib
from email.message import EmailMessage
from html import escape
from pathlib import Path

from src.core.config import (
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)

logger = logging.getLogger(__name__)

EMAIL_TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"


class EmailService:
    SUBJECT_ACCESS_REQUEST_CONFIRMATION = "Solicitação recebida - Alá Poker"

    def send_access_request_confirmation_email(
        self,
        to_email: str | None,
        name: str | None = None,
    ) -> None:
        """Send a confirmation email for a submitted access request.

        Fails silently so that email delivery never breaks the main form flow.
        """
        if not to_email:
            return

        if not SMTP_HOST or not SMTP_FROM_EMAIL:
            logger.warning("SMTP configuration is incomplete - skipping email.")
            return

        try:
            html = self._render_template(
                "access_request_confirmation.html",
                {
                    "name": escape(name or "Olá"),
                },
            )

            message = EmailMessage()
            message["Subject"] = self.SUBJECT_ACCESS_REQUEST_CONFIRMATION
            message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
            message["To"] = to_email
            message.set_content(
                "Recebemos sua solicitação de acesso. Nossa equipe irá analisá-la em breve."
            )
            message.add_alternative(html, subtype="html")

            if SMTP_PORT == 465:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                    self._send_message(smtp, message)
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                    if SMTP_PORT == 587:
                        smtp.starttls()
                    self._send_message(smtp, message)

            logger.info("Access request confirmation email sent to %s.", to_email)
        except Exception as exc:
            logger.error(
                "Access request confirmation email failed (non-blocking): %s",
                exc,
            )

    def _send_message(self, smtp: smtplib.SMTP, message: EmailMessage) -> None:
        if SMTP_USER and SMTP_PASSWORD:
            smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(message)

    def _render_template(self, template_name: str, context: dict[str, str]) -> str:
        template_path = EMAIL_TEMPLATES_DIR / template_name
        html = template_path.read_text(encoding="utf-8")

        for key, value in context.items():
            html = html.replace(f"{{{{ {key} }}}}", value)

        return html
