"""Configuration constants, budgets, and reviewer-mandated thresholds for tools/colab.

Authorized under PLAN_COLAB_GPU_PIPELINE_v1.0.md (pinned SHA8 d0322dc7).
Gates passed: SAG 97, Gemini 98, Muse 96. BUILD only (25 Nov 2026).
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

PLAN_SHA8 = "d0322dc7"
CONFIRMED_CU_BASELINE = 1531.77

# GPU hardware policy
ALLOWED_GPUS: tuple[str, ...] = ("L4", "T4")
DEFAULT_GPU = "L4"
BLOCKED_GPUS: tuple[str, ...] = ("A100", "H100", "BLACKWELL", "V100", "TPU")

# Compute Unit (CU) and timeout budgets
PILOT_CU_CAP = 25.0
FULL_SCALE_CU_CAP = 150.0
HARD_STOP_BALANCE_FLOOR = 500.0

PILOT_TIMEOUT_SEC = 2700  # 45 minutes
FULL_TIMEOUT_SEC = 7200   # 120 minutes

# Reviewer-mandated pilot thresholds
# M1 (Muse #1): numerically pin 75% target / >= 73% minimum framing ratio
M1_FRAMING_TARGET_PCT = 75.0
M1_FRAMING_MIN_PCT = 73.0
M1_FRAMING_MAX_PCT = 77.0

# M2 (Muse #4): advisory-only flags routed to TRK-002 review queue
M2_REVIEW_OWNER = "TRK-002 SAG/Muse Review Queue"

# M3 (Gemini + Muse + SAG #3): Apache 2.0 RT-DETR default, AGPL YOLOv11 blocked, pilot count pinned
M3_DEFAULT_MODEL = "RT-DETR"
M3_PILOT_ANNOTATION_COUNT = 150

# M4 (Muse #2): hand-check sample minimum and numeric CER/WER reporting
M4_DEFAULT_MODEL = "OlmOCR"
M4_OCR_HANDCHECK_MIN_SAMPLE: int = 10

# One-line confirmation required by Muse / Eric BUILD approval (Condition #5)
GCP_SECTION_17_CONFIRMATION: str = (
    "Confirmed: Google Cloud Service Specific Terms Section 17 (effective Jan 1, 2027) "
    "does not apply — pipeline runs via google-colab-cli (colab run) only with interactive MCP excluded, "
    "holds zero GCP API/MCP credentials, and stages only Eric's own catalog data in Google Drive."
)

# Google Drive staging destination (Numista.Ai -> Colab_Staging)
DRIVE_STAGING_FOLDER_ID = "1yAEA7ob4eUY_pkWqCj2m9ipXgvB5okcA"
DRIVE_STAGING_URL = "https://drive.google.com/drive/folders/1yAEA7ob4eUY_pkWqCj2m9ipXgvB5okcA"

DEFAULT_COLAB_CLI_PATH = Path(r"C:\Users\ericd\.colab-cli-venv\Scripts\colab.exe")


@dataclass(frozen=True)
class ModelLicenseInfo:
    """License metadata for an open-weight model used in Colab batch jobs."""

    spdx: str
    commercial_ok: bool
    notes: str = ""


MODEL_LICENSES: dict[str, ModelLicenseInfo] = {
    "BiRefNet": ModelLicenseInfo(spdx="MIT", commercial_ok=True, notes="M1 background segmentation"),
    "SAM2": ModelLicenseInfo(spdx="Apache-2.0", commercial_ok=True, notes="M1 segmentation fallback"),
    "DINOv2": ModelLicenseInfo(spdx="Apache-2.0", commercial_ok=True, notes="M2 visual embeddings"),
    "SigLIP": ModelLicenseInfo(spdx="Apache-2.0", commercial_ok=True, notes="M2 multimodal embeddings"),
    "RT-DETR": ModelLicenseInfo(spdx="Apache-2.0", commercial_ok=True, notes="M3 default coin/mintmark detector"),
    "OlmOCR": ModelLicenseInfo(spdx="Apache-2.0", commercial_ok=True, notes="M4 default historical OCR"),
    "Marker": ModelLicenseInfo(spdx="GPL-3.0", commercial_ok=False, notes="Blocked without offline-only waiver"),
    "Surya": ModelLicenseInfo(spdx="GPL-3.0-Modified", commercial_ok=False, notes="Blocked without offline-only waiver"),
    "YOLOv11": ModelLicenseInfo(spdx="AGPL-3.0", commercial_ok=False, notes="Explicitly blocked per Gemini/Muse gate"),
    "CUDA-Smoke": ModelLicenseInfo(spdx="Apache-2.0", commercial_ok=True, notes="AT-01/AT-02 live GPU smoke verification"),
}


def resolve_colab_cli() -> str:
    """Return the path to the google-colab-cli executable."""
    env_bin = os.environ.get("COLAB_CLI_BIN")
    if env_bin:
        return env_bin
    if DEFAULT_COLAB_CLI_PATH.exists():
        return str(DEFAULT_COLAB_CLI_PATH)
    found = shutil.which("colab")
    if found:
        return found
    return str(DEFAULT_COLAB_CLI_PATH)


def resolve_gdrive_cli() -> str:
    """Return the path to the gdrive CLI executable (resolving .cmd on Windows)."""
    env_bin = os.environ.get("GDRIVE_CLI_BIN")
    if env_bin:
        return env_bin
    found = shutil.which("gdrive")
    if found:
        return found
    return "gdrive"
