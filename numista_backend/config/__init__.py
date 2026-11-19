"""
Numista.AI Centralized Backend Configuration Package
"""

import os
from typing import Optional
from google.genai import types as genai_types

# Primary Public Domain for Numista.AI
APP_PUBLIC_DOMAIN = os.getenv("APP_PUBLIC_DOMAIN", "numista.ai")

# Base Web Application URL for Deep Links & QR Codes
APP_BASE_URL = os.getenv("APP_BASE_URL", f"https://{APP_PUBLIC_DOMAIN}")

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "transfers@numista.ai")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Gemini Model Configuration
# Centralized here so main.py and all routes import from one place.
# Defaults match the model IDs documented in main.py — Cloud Run env vars take precedence.
GEMINI_FLASH_MODEL           = os.getenv("GEMINI_FLASH_MODEL", "gemini-4-hydrogen")          # Primary workhorse (interactive vision, chat, OCR)
GEMINI_PRO_MODEL             = os.getenv("GEMINI_PRO_MODEL",   "gemini-4-argon")             # High-reasoning tasks (invoices, estate, grading)
GEMINI_LITE_MODEL            = os.getenv("GEMINI_LITE_MODEL",  "gemini-3.5-flash-lite")      # Lightweight/fast fallback tasks
GEMINI_IMAGE_MODEL           = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")     # Nano Banana 2 (overflow/default image gen)
GEMINI_IMAGE_PRO_MODEL       = os.getenv("GEMINI_IMAGE_PRO_MODEL", "gemini-3-pro-image")     # Nano Banana Pro (first 100/mo for typography)
GEMINI_IMAGE_PRO_MONTHLY_CAP = int(os.getenv("GEMINI_IMAGE_PRO_MONTHLY_CAP", "100"))         # Monthly Pro image generation cap
GEMINI_EMBEDDING_MODEL       = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")     # Vector embeddings / RAG

# Route-level model aliases (used by scan_routes.py and ai_routes.py)
# These allow per-route overrides via env vars while defaulting to the core models above.
DEFAULT_VISION_MODEL  = os.getenv("DEFAULT_VISION_MODEL",  GEMINI_FLASH_MODEL)    # Coin image analysis
FALLBACK_VISION_MODEL = os.getenv("FALLBACK_VISION_MODEL", GEMINI_LITE_MODEL)     # Vision fallback
DEFAULT_CHAT_MODEL    = os.getenv("DEFAULT_CHAT_MODEL",    GEMINI_FLASH_MODEL)    # Morgan AI chat
FALLBACK_CHAT_MODEL   = os.getenv("FALLBACK_CHAT_MODEL",   GEMINI_LITE_MODEL)     # Chat fallback


def is_gemini4_model(model_id: str) -> bool:
    """Return True iff model_id targets a Gemini 4 tier (Hydrogen/Argon/Carbon)."""
    return str(model_id or "").strip().lower().startswith("gemini-4-")


def gemini4_thinking_config(
    model_id: str, level: str = "low"
) -> Optional[genai_types.ThinkingConfig]:
    """Return explicit ThinkingConfig for Gemini 4 models, or None on rollback/lite."""
    if not is_gemini4_model(model_id):
        return None
    return genai_types.ThinkingConfig(thinking_level=level)
