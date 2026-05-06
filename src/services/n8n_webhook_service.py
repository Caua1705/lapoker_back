import logging

import requests

from src.core.config import N8N_WEBHOOK_URL

logger = logging.getLogger(__name__)


class N8nWebhookService:
    WEBHOOK_URL = N8N_WEBHOOK_URL
    TIMEOUT_SECONDS = 5

    def trigger_access_request(self, payload: dict) -> None:
        """Send registration data to the n8n webhook.

        Fails silently so that a webhook outage never breaks the main flow.
        """
        if not self.WEBHOOK_URL:
            logger.warning(
                "N8N_WEBHOOK_URL is not set – skipping webhook."
            )
            return

        try:
            response = requests.post(
                self.WEBHOOK_URL,
                json=payload,
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            logger.info(
                "n8n webhook triggered successfully (status %s).", response.status_code
            )
        except requests.exceptions.RequestException as exc:
            logger.error("n8n webhook call failed (non-blocking): %s", exc)
