import logging
import smtplib
from email.message import EmailMessage
from html import escape
from pathlib import Path

from src.core.config import (
    ADMIN_NOTIFICATION_EMAIL,
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
    SUBJECT_ACCESS_CONFIRMATION = "Convite Alá Poker"
    SUBJECT_ADMIN_NOTIFICATION = "Novo cadastro de convite"

    def send_access_invitation_email(
        self,
        to_email: str | None,
        name: str | None = None,
    ) -> None:
        """
        Sends the invitation email to the person who submitted the form.

        This method never raises exceptions to avoid breaking the main form flow.
        """
        logger.info("[email] Starting user invitation email flow. to_email=%s", to_email)

        if not to_email:
            logger.warning("[email] No user email provided. Skipping user invitation email.")
            return

        if not self._is_smtp_config_valid():
            logger.warning("[email] SMTP configuration incomplete. Skipping user invitation email.")
            return

        try:
            html = self._render_template(
                "access_request_confirmation.html",
                {
                    "name": escape(name or "convidado"),
                },
            )

            message = EmailMessage()
            message["Subject"] = self.SUBJECT_ACCESS_CONFIRMATION
            message["From"] = self._format_sender()
            message["To"] = to_email

            message.set_content(
                "Enviamos seu convite. Confira os detalhes no conteúdo em HTML deste e-mail."
            )
            message.add_alternative(html, subtype="html")

            self._send(message)

            logger.info("[email] User invitation email sent successfully to %s", to_email)

        except Exception:
            logger.exception("[email] User invitation email failed.")

    def send_admin_access_notification(
        self,
        name: str | None,
        email: str | None,
        phone: str | None = None,
        instagram: str | None = None,
    ) -> None:
        """
        Sends a notification email to the configured admin email.

        This method never raises exceptions to avoid breaking the main form flow.
        """
        logger.info("[email] Starting admin notification email flow.")

        if not ADMIN_NOTIFICATION_EMAIL:
            logger.warning("[email] ADMIN_NOTIFICATION_EMAIL not configured. Skipping admin notification.")
            return

        if not self._is_smtp_config_valid():
            logger.warning("[email] SMTP configuration incomplete. Skipping admin notification.")
            return

        try:
            safe_name = name or "-"
            safe_email = email or "-"
            safe_phone = phone or "-"
            safe_instagram = instagram or "-"

            message = EmailMessage()
            message["Subject"] = self.SUBJECT_ADMIN_NOTIFICATION
            message["From"] = self._format_sender()
            message["To"] = ADMIN_NOTIFICATION_EMAIL

            body = f"""
Novo cadastro de convite.

Nome: {safe_name}
Email: {safe_email}
Telefone: {safe_phone}
Instagram: {safe_instagram}
"""

            html = f"""
<!doctype html>
<html lang="pt-BR">
  <body style="margin:0; padding:24px; background:#090909; font-family:Arial, sans-serif; color:#f6efe2;">
    <div style="max-width:560px; margin:0 auto; border:1px solid #b79358; border-radius:14px; padding:24px; background:#111;">
      <h2 style="margin:0 0 18px; color:#fff8e8;">Novo cadastro de convite</h2>

      <p style="margin:0 0 10px;"><strong style="color:#b79358;">Nome:</strong> {escape(safe_name)}</p>
      <p style="margin:0 0 10px;"><strong style="color:#b79358;">Email:</strong> {escape(safe_email)}</p>
      <p style="margin:0 0 10px;"><strong style="color:#b79358;">Telefone:</strong> {escape(safe_phone)}</p>
      <p style="margin:0;"><strong style="color:#b79358;">Instagram:</strong> {escape(safe_instagram)}</p>
    </div>
  </body>
</html>
"""

            message.set_content(body)
            message.add_alternative(html, subtype="html")

            self._send(message)

            logger.info(
                "[email] Admin notification sent successfully to %s",
                ADMIN_NOTIFICATION_EMAIL,
            )

        except Exception:
            logger.exception("[email] Admin notification email failed.")

    def _send(self, message: EmailMessage) -> None:
        logger.info("[email] Connecting to SMTP server %s:%s", SMTP_HOST, SMTP_PORT)

        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
                self._login_and_send(smtp, message)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
                if SMTP_PORT == 587:
                    smtp.starttls()
                self._login_and_send(smtp, message)

    def _login_and_send(self, smtp: smtplib.SMTP, message: EmailMessage) -> None:
        if SMTP_USER and SMTP_PASSWORD:
            logger.info("[email] Logging into SMTP as %s", SMTP_USER)
            smtp.login(SMTP_USER, SMTP_PASSWORD)

        smtp.send_message(message)

    def _render_template(self, template_name: str, context: dict[str, str]) -> str:
        template_path = EMAIL_TEMPLATES_DIR / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Email template not found: {template_path}")

        html = template_path.read_text(encoding="utf-8")

        for key, value in context.items():
            html = html.replace(f"{{{{ {key} }}}}", value)

        return html

    def _format_sender(self) -> str:
        if SMTP_FROM_NAME:
            return f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"

        return SMTP_FROM_EMAIL or ""

    def _is_smtp_config_valid(self) -> bool:
        return all(
            [
                SMTP_HOST,
                SMTP_PORT,
                SMTP_USER,
                SMTP_PASSWORD,
                SMTP_FROM_EMAIL,
            ]
        )