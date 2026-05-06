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
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")