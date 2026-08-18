"""
Numista.AI Centralized Backend Configuration Package
"""

import os

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
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.7-flash")          # Primary workhorse
GEMINI_PRO_MODEL   = os.getenv("GEMINI_PRO_MODEL",   "gemini-3.1-pro-preview")    # High-reasoning tasks
GEMINI_LITE_MODEL  = os.getenv("GEMINI_LITE_MODEL",  "gemini-3.5-flash-lite")     # Lightweight/fast tasks
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")    # Image generation

# Route-level model aliases (used by scan_routes.py and ai_routes.py)
# These allow per-route overrides via env vars while defaulting to the core models above.
DEFAULT_VISION_MODEL  = os.getenv("DEFAULT_VISION_MODEL",  GEMINI_FLASH_MODEL)    # Coin image analysis
FALLBACK_VISION_MODEL = os.getenv("FALLBACK_VISION_MODEL", GEMINI_LITE_MODEL)     # Vision fallback
DEFAULT_CHAT_MODEL    = os.getenv("DEFAULT_CHAT_MODEL",    GEMINI_FLASH_MODEL)    # Morgan AI chat
FALLBACK_CHAT_MODEL   = os.getenv("FALLBACK_CHAT_MODEL",   GEMINI_LITE_MODEL)     # Chat fallback
