"""
Centralized Gemini Model Configuration & Backend Settings

This module serves as the single source of truth for Gemini model bindings across
all Python backend services, API handlers, background tasks, and utility scripts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded relative to numista_backend directory
_BACKEND_DIR = Path(__file__).resolve().parent
_ENV_PATH = _BACKEND_DIR / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH)

# ==============================================================================
# GEMINI MODEL BINDINGS
# ==============================================================================
# Primary workhorse model for multimodal coin identification, receipt OCR,
# fast structured extraction, and general AI assistant tasks.
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.6-flash")
DEFAULT_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", GEMINI_FLASH_MODEL)
FALLBACK_VISION_MODEL = "gemini-3.5-flash"

# High-reasoning model for complex valuation reports, rare variety verification,
# and deep numismatic analysis fallback.
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")

# High-volume, lightweight model for cheap background processing (e.g. bulk catalog tagging).
GEMINI_LITE_MODEL = os.getenv("GEMINI_LITE_MODEL", "gemini-3.5-flash-lite")

# Dedicated image generation / editing model.
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")

# Backward compatibility alias
PRIMARY_MODEL = GEMINI_FLASH_MODEL

# ==============================================================================
# EXTERNAL API & PRODUCTION SECRETS (GCP Secret Manager mounted envs)
# ==============================================================================
GREYSHEET_API_KEY = os.getenv("GREYSHEET_API_KEY", "")
GREYSHEET_API_TOKEN = os.getenv("GREYSHEET_API_TOKEN", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

