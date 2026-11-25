"""Safety guards, CU budget checks, manifest hashing, and zero-credential static audit."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.colab.config import (
    ALLOWED_GPUS,
    FULL_SCALE_CU_CAP,
    FULL_TIMEOUT_SEC,
    HARD_STOP_BALANCE_FLOOR,
    MODEL_LICENSES,
    PILOT_CU_CAP,
    PILOT_TIMEOUT_SEC,
    PLAN_SHA8,
)


class GuardViolation(RuntimeError):
    """Raised when a Colab pipeline safety, budget, license, or credential guard fails."""


_FORBIDDEN_IMPORTS: tuple[str, ...] = (
    ".".join(["google", "cloud", "firestore"]),
    ".".join(["google", "cloud", "storage"]),
    "_".join(["firebase", "admin"]),
)

_FORBIDDEN_LITERALS: tuple[str, ...] = (
    "".join(["service", "AccountKey"]),
    "_".join(["GOOGLE", "APPLICATION", "CREDENTIALS"]),
    "-".join(["colab", "mcp"]),
)


def parse_colab_usage(text: str) -> float:
    """Parse remaining compute units from `colab usage` CLI output."""
    if not text or not text.strip():
        raise GuardViolation("Empty output from `colab usage`; cannot verify compute unit balance.")

    patterns = (
        r"(?:available|remaining|balance|compute\s*units?)[^\d\-]*(\d+(?:,\d{3})*(?:\.\d+)?)",
        r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:compute\s*units?|cus?\b)",
    )
    for pat in patterns:
        match = re.search(pat, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    raise GuardViolation(f"Could not parse compute unit balance from `colab usage` output: {text!r}")


def validate_model_license(model_name: str, allow_offline_gpl: bool = False) -> dict[str, Any]:
    """Validate that a model has an approved open-weight license for the pipeline."""
    info = MODEL_LICENSES.get(model_name)
    if info is None:
        raise GuardViolation(f"Unknown or unapproved model {model_name!r}; register license in config.py first.")
    if not info.commercial_ok:
        if allow_offline_gpl and "GPL" in info.spdx and "AGPL" not in info.spdx:
            return {"model": model_name, "spdx": info.spdx, "commercial_ok": False, "offline_waiver": True}
        raise GuardViolation(
            f"Model {model_name!r} has disallowed license {info.spdx!r} ({info.notes})."
        )
    return {"model": model_name, "spdx": info.spdx, "commercial_ok": True, "offline_waiver": False}


def enforce_pre_run_guards(
    *,
    balance_cu: float,
    cumulative_cu: float,
    mode: str,
    gpu: str,
    model_name: str,
    timeout_sec: int,
    allow_offline_gpl: bool = False,
) -> dict[str, Any]:
    """Validate balance floor, CU cap, GPU allowlist, timeout ceiling, and model license."""
    if mode not in ("pilot", "full"):
        raise GuardViolation(f"Invalid mode {mode!r}; expected 'pilot' or 'full'.")

    if balance_cu < HARD_STOP_BALANCE_FLOOR:
        raise GuardViolation(
            f"Hard stop balance floor triggered: available {balance_cu:.2f} CUs < {HARD_STOP_BALANCE_FLOOR:.2f} CUs."
        )

    gpu_norm = gpu.strip().upper()
    if gpu_norm not in ALLOWED_GPUS:
        raise GuardViolation(
            f"GPU {gpu!r} is not permitted; allowed tiers are {ALLOWED_GPUS}."
        )

    cap = PILOT_CU_CAP if mode == "pilot" else FULL_SCALE_CU_CAP
    if cumulative_cu >= cap:
        raise GuardViolation(
            f"{mode.title()} CU cap reached/exceeded: {cumulative_cu:.2f} >= {cap:.2f} CUs."
        )

    max_timeout = PILOT_TIMEOUT_SEC if mode == "pilot" else FULL_TIMEOUT_SEC
    if timeout_sec <= 0 or timeout_sec > max_timeout:
        raise GuardViolation(
            f"Timeout {timeout_sec}s out of bounds for {mode} mode (must be 1..{max_timeout}s)."
        )

    license_meta = validate_model_license(model_name, allow_offline_gpl=allow_offline_gpl)
    return {
        "mode": mode,
        "gpu": gpu_norm,
        "balance_cu": balance_cu,
        "cumulative_cu": cumulative_cu,
        "cu_cap": cap,
        "timeout_sec": timeout_sec,
        "license": license_meta,
    }


def compute_sha256(path: Path) -> str:
    """Return lowercase hex SHA-256 digest for a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(
    *,
    job_id: str,
    milestone: str,
    mode: str,
    output_dir: Path,
    model_name: str,
    input_provenance: list[dict[str, Any]],
    extra_meta: dict[str, Any] | None = None,
) -> Path:
    """Create manifest.json recording per-file SHA-256 checksums, license, and provenance."""
    output_dir.mkdir(parents=True, exist_ok=True)
    license_meta = validate_model_license(model_name, allow_offline_gpl=True)

    files_entries: list[dict[str, Any]] = []
    for p in sorted(output_dir.rglob("*")):
        if not p.is_file() or p.name == "manifest.json":
            continue
        files_entries.append({
            "path": p.relative_to(output_dir).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": compute_sha256(p),
        })

    payload: dict[str, Any] = {
        "plan_sha8": PLAN_SHA8,
        "job_id": job_id,
        "milestone": milestone,
        "mode": mode,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": license_meta,
        "input_provenance": input_provenance,
        "files": files_entries,
    }
    if extra_meta:
        payload["extra"] = extra_meta

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_bytes((json.dumps(payload, indent=2) + "\n").encode("utf-8"))
    return manifest_path


def verify_manifest(manifest_path: Path) -> bool:
    """Verify every file listed in manifest.json exists and matches its SHA-256 digest."""
    if not manifest_path.is_file():
        return False
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_dir = manifest_path.parent
    files = data.get("files", [])
    if not isinstance(files, list):
        return False
    for entry in files:
        target = base_dir / entry["path"]
        if not target.is_file():
            return False
        if target.stat().st_size != entry["bytes"]:
            return False
        if compute_sha256(target) != entry["sha256"]:
            return False
    return True


def static_credential_audit(root_dir: Path) -> list[str]:
    """Scan Python files under root_dir for forbidden GCP/Firestore/GCS/MCP references."""
    violations: list[str] = []
    for py_file in sorted(root_dir.rglob("*.py")):
        src = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(src, filename=str(py_file))
        except SyntaxError as exc:
            violations.append(f"{py_file}: SyntaxError {exc}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for bad in _FORBIDDEN_IMPORTS:
                        if alias.name == bad or alias.name.startswith(bad + "."):
                            violations.append(f"{py_file}:{node.lineno} forbidden import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for bad in _FORBIDDEN_IMPORTS:
                    if mod == bad or mod.startswith(bad + "."):
                        violations.append(f"{py_file}:{node.lineno} forbidden import-from {mod}")

        for token in _FORBIDDEN_LITERALS:
            if token in src:
                violations.append(f"{py_file}: forbidden literal {token}")

    return violations
