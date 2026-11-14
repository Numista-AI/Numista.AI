"""
Ingestion Configuration & Calibrated Calibration Weights
Numista.AI System of Record
"""

import os

from config import GEMINI_FLASH_MODEL, GEMINI_LITE_MODEL, GEMINI_PRO_MODEL

# Mandatory Model Policy (2026 Production Active Models - Gemini 4 Tiered)
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", GEMINI_FLASH_MODEL)
EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", GEMINI_PRO_MODEL)
FALLBACK_FLASH_MODEL = os.getenv("FALLBACK_FLASH_MODEL", GEMINI_LITE_MODEL)
FALLBACK_PRO_MODEL = os.getenv("FALLBACK_PRO_MODEL", GEMINI_FLASH_MODEL)

# Prompt and Processing Versions
CHECKLIST_PROMPT_VERSION = "checklist_v7_20260815"
INVOICE_PROMPT_VERSION = "invoice_v4_20260815"

# Multi-factor Confidence Scoring Weights
BOX_CLARITY_WEIGHT = 0.50
SUBJECT_OCR_WEIGHT = 0.30
HEADER_VALIDATION_WEIGHT = 0.20

# Operational Gating Thresholds
HANDWRITING_QUARANTINE_THRESHOLD = 0.75
CLASSIFIER_CONFIDENCE_THRESHOLD = 0.85

# Batching & Deduplication
MAX_ROWS_PER_EXTRACTION_CHUNK = 25
ACTIVE_IMPORT_STATUSES = ["provisional", "staged", "quarantined"]
