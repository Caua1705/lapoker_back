import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# DATABASE
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# =========================
# N8N WEBHOOKS
# =========================
N8N_ACCESS_REQUEST_WEBHOOK_URL = os.getenv("N8N_ACCESS_REQUEST_WEBHOOK_URL")

# =========================
# SMTP EMAIL
# =========================
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "587")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = (os.getenv("SMTP_PASSWORD") or "").replace(" ", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Private Event")

ADMIN_NOTIFICATION_EMAIL = os.getenv("ADMIN_NOTIFICATION_EMAIL")