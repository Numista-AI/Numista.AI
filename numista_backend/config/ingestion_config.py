"""
Ingestion Configuration & Calibrated Calibration Weights
Numista.AI System of Record
"""

# Mandatory Model Policy (2026 Production Active Models - Gemini 4 Tiered)
CLASSIFIER_MODEL = "gemini-4-hydrogen"
EXTRACTION_MODEL = "gemini-4-argon"
FALLBACK_FLASH_MODEL = "gemini-4-hydrogen"
FALLBACK_PRO_MODEL = "gemini-3.1-pro-preview"

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
