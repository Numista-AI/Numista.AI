"""Wrapper runner for google-colab-cli (`colab run`) with CU guards and Drive staging."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.colab.config import (
    DEFAULT_GPU,
    DRIVE_STAGING_FOLDER_ID,
    FULL_TIMEOUT_SEC,
    M3_DEFAULT_MODEL,
    M4_DEFAULT_MODEL,
    PILOT_TIMEOUT_SEC,
    PLAN_SHA8,
    resolve_colab_cli,
)
from tools.colab.guards import (
    GuardViolation,
    build_manifest,
    enforce_pre_run_guards,
    parse_colab_usage,
    verify_manifest,
)

MILESTONE_SCRIPTS: dict[str, tuple[Path, str]] = {
    "M1": (Path(__file__).resolve().parent / "jobs" / "m1_framing.py", "BiRefNet"),
    "M2": (Path(__file__).resolve().parent / "jobs" / "m2_embeddings.py", "DINOv2"),
    "M3": (Path(__file__).resolve().parent / "jobs" / "m3_cropper.py", M3_DEFAULT_MODEL),
    "M4": (Path(__file__).resolve().parent / "jobs" / "m4_ocr.py", M4_DEFAULT_MODEL),
}


def run_with_timeout(
    cmd: list[str],
    timeout_sec: int,
    *,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Execute a subprocess and strictly kill it if wall-clock timeout_sec is exceeded."""
    if timeout_sec <= 0:
        raise GuardViolation(f"timeout_sec must be positive; got {timeout_sec}.")

    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        proc.kill()
        proc.communicate()
        raise TimeoutError(
            f"Colab job exceeded wall-clock timeout ({timeout_sec}s) and was killed: {cmd}"
        ) from exc

    return subprocess.CompletedProcess(
        args=cmd,
        returncode=proc.returncode,
        stdout=stdout,
        stderr=stderr,
    )


def verify_zero_active_sessions(sessions_output: str, expected_session: str | None = None) -> bool:
    """Confirm no active Colab sessions remain after `colab run` exits (AT-02)."""
    norm = (sessions_output or "").strip().lower()
    if not norm or "no active" in norm or "0 active" in norm or "no sessions" in norm:
        return True
    if expected_session and expected_session.lower() not in norm:
        return True
    raise GuardViolation(
        f"Auto-shutdown check failed; active Colab session still listed:\n{sessions_output}"
    )


def build_cu_receipt(
    *,
    job_id: str,
    milestone: str,
    mode: str,
    gpu: str,
    pre_balance_cu: float,
    post_balance_cu: float,
    duration_sec: float,
    sessions_clean: bool,
) -> dict[str, Any]:
    """Build cu_receipt.json payload recording pre/post CU balance and runtime."""
    cu_spent = round(max(pre_balance_cu - post_balance_cu, 0.0), 4)
    return {
        "plan_sha8": PLAN_SHA8,
        "job_id": job_id,
        "milestone": milestone,
        "mode": mode,
        "gpu": gpu,
        "pre_balance_cu": pre_balance_cu,
        "post_balance_cu": post_balance_cu,
        "cu_spent": cu_spent,
        "duration_sec": round(duration_sec, 2),
        "auto_shutdown_verified": sessions_clean,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def upload_staging_bundle(output_dir: Path, job_id: str) -> str:
    """Upload staged job artifacts to Google Drive -> Numista.Ai -> Colab_Staging/<job_id>/."""
    mkdir_proc = run_with_timeout(
        [
            "gdrive",
            "mutate",
            "mkdir",
            job_id,
            "--parent",
            DRIVE_STAGING_FOLDER_ID,
            "--json",
        ],
        timeout_sec=60,
    )
    if mkdir_proc.returncode != 0:
        raise RuntimeError(f"gdrive mkdir failed: {mkdir_proc.stderr}")

    folder_id = ""
    try:
        folder_id = json.loads(mkdir_proc.stdout).get("id", "")
    except json.JSONDecodeError:
        for token in mkdir_proc.stdout.split():
            if token.endswith(")"):
                folder_id = token.rstrip(")")
    if not folder_id:
        raise RuntimeError(f"Could not parse Drive staging job folder ID from: {mkdir_proc.stdout}")

    for artifact in sorted(output_dir.rglob("*")):
        if not artifact.is_file():
            continue
        up_proc = run_with_timeout(
            ["gdrive", "mutate", "upload", str(artifact), "--parent", folder_id, "--json"],
            timeout_sec=120,
        )
        if up_proc.returncode != 0:
            raise RuntimeError(f"gdrive upload failed for {artifact}: {up_proc.stderr}")
    return folder_id


def run_job(
    *,
    milestone: str,
    mode: str,
    job_id: str,
    output_dir: Path,
    gpu: str = DEFAULT_GPU,
    timeout_sec: int | None = None,
    cumulative_cu: float = 0.0,
    dry_run: bool = False,
) -> Path:
    """Execute a milestone batch job under all budget, license, timeout, and staging guards."""
    if milestone not in MILESTONE_SCRIPTS:
        raise GuardViolation(f"Unknown milestone {milestone!r}; expected one of {tuple(MILESTONE_SCRIPTS)}.")

    script_path, default_model = MILESTONE_SCRIPTS[milestone]
    effective_timeout = timeout_sec if timeout_sec is not None else (
        PILOT_TIMEOUT_SEC if mode == "pilot" else FULL_TIMEOUT_SEC
    )
    cli_bin = resolve_colab_cli()

    if dry_run:
        pre_balance = 1531.77
        enforce_pre_run_guards(
            balance_cu=pre_balance,
            cumulative_cu=cumulative_cu,
            mode=mode,
            gpu=gpu,
            model_name=default_model,
            timeout_sec=effective_timeout,
        )
        t0 = time.monotonic()
        proc = run_with_timeout(
            [
                sys.executable,
                "-m",
                f"tools.colab.jobs.{script_path.stem}",
                "--output-dir",
                str(output_dir),
                "--job-id",
                job_id,
                "--dry-run",
            ],
            timeout_sec=effective_timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Dry-run job failed ({proc.returncode}): {proc.stderr}")
        post_balance = pre_balance
        sessions_clean = True
    else:
        pre_usage_proc = run_with_timeout([cli_bin, "usage"], timeout_sec=60)
        if pre_usage_proc.returncode != 0:
            raise RuntimeError(f"`colab usage` failed: {pre_usage_proc.stderr}")
        pre_balance = parse_colab_usage(pre_usage_proc.stdout)

        enforce_pre_run_guards(
            balance_cu=pre_balance,
            cumulative_cu=cumulative_cu,
            mode=mode,
            gpu=gpu,
            model_name=default_model,
            timeout_sec=effective_timeout,
        )

        t0 = time.monotonic()
        colab_cmd = [
            cli_bin,
            "run",
            "--gpu",
            gpu.upper(),
            "--session",
            job_id,
            "--timeout",
            "0",
            str(script_path),
            "--output-dir",
            str(output_dir),
            "--job-id",
            job_id,
        ]
        run_proc = run_with_timeout(colab_cmd, timeout_sec=effective_timeout)
        if run_proc.returncode != 0:
            raise RuntimeError(f"`colab run` failed ({run_proc.returncode}): {run_proc.stderr}")

        sess_proc = run_with_timeout([cli_bin, "sessions"], timeout_sec=60)
        sessions_clean = verify_zero_active_sessions(sess_proc.stdout, expected_session=job_id)

        post_usage_proc = run_with_timeout([cli_bin, "usage"], timeout_sec=60)
        post_balance = parse_colab_usage(post_usage_proc.stdout)

    duration_sec = time.monotonic() - t0
    receipt = build_cu_receipt(
        job_id=job_id,
        milestone=milestone,
        mode=mode,
        gpu=gpu.upper(),
        pre_balance_cu=pre_balance,
        post_balance_cu=post_balance,
        duration_sec=duration_sec,
        sessions_clean=sessions_clean,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cu_receipt.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    summary_text = (
        f"# Colab Job Summary — {job_id}\n\n"
        f"- Plan SHA8: `{PLAN_SHA8}`\n"
        f"- Milestone / Mode: `{milestone}` / `{mode}`\n"
        f"- GPU: `{gpu.upper()}`\n"
        f"- CU Balance: `{pre_balance:.2f}` -> `{post_balance:.2f}` (spent `{receipt['cu_spent']:.4f}`)\n"
        f"- Auto-Shutdown Verified: `{sessions_clean}`\n"
        f"- Duration: `{duration_sec:.2f}s`\n"
    )
    (output_dir / "summary.md").write_bytes(summary_text.encode("utf-8"))

    manifest_path = build_manifest(
        job_id=job_id,
        milestone=milestone,
        mode=mode,
        output_dir=output_dir,
        model_name=default_model,
        input_provenance=[{"milestone": milestone, "mode": mode}],
        extra_meta={"cu_spent": receipt["cu_spent"], "auto_shutdown_verified": sessions_clean},
    )
    if not verify_manifest(manifest_path):
        raise GuardViolation(f"Manifest verification failed for {manifest_path}")

    if not dry_run:
        upload_staging_bundle(output_dir, job_id)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Numista.AI Google AI Ultra Colab Runner")
    parser.add_argument("--milestone", required=True, choices=tuple(MILESTONE_SCRIPTS))
    parser.add_argument("--mode", default="pilot", choices=("pilot", "full"))
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gpu", default=DEFAULT_GPU)
    parser.add_argument("--timeout-sec", type=int, default=None)
    parser.add_argument("--cumulative-cu", type=float, default=0.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = run_job(
        milestone=args.milestone,
        mode=args.mode,
        job_id=args.job_id,
        output_dir=args.output_dir,
        gpu=args.gpu,
        timeout_sec=args.timeout_sec,
        cumulative_cu=args.cumulative_cu,
        dry_run=args.dry_run,
    )
    print(f"Completed {args.job_id}: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
