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
    GCP_SECTION_17_CONFIRMATION,
    M2_REVIEW_OWNER,
    M3_DEFAULT_MODEL,
    M4_DEFAULT_MODEL,
    PILOT_TIMEOUT_SEC,
    PLAN_SHA8,
    resolve_colab_cli,
    resolve_gdrive_cli,
)
from tools.colab.guards import (
    GuardViolation,
    build_manifest,
    enforce_pre_run_guards,
    parse_colab_usage,
    verify_manifest,
)

MILESTONE_SCRIPTS: dict[str, tuple[Path, str]] = {
    "SMOKE": (Path(__file__).resolve().parent / "jobs" / "smoke_gpu.py", "CUDA-Smoke"),
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


def extract_delimited_json(stdout: str, begin_marker: str, end_marker: str) -> dict[str, Any] | None:
    """Extract a JSON object emitted between markers in subprocess stdout."""
    start_idx = stdout.find(begin_marker)
    if start_idx == -1:
        return None
    end_idx = stdout.find(end_marker, start_idx + len(begin_marker))
    if end_idx == -1:
        return None
    raw = stdout[start_idx + len(begin_marker) : end_idx].strip()
    if not raw:
        return None
    data = json.loads(raw)
    return data if isinstance(data, dict) else None


def _run_gdrive_with_retry(args: list[str], *, timeout_sec: int = 90) -> subprocess.CompletedProcess[str]:
    """Run gdrive CLI resolving .cmd on Windows, retrying transient 403/rate-limit errors."""
    gdrive_bin = resolve_gdrive_cli()
    last_proc: subprocess.CompletedProcess[str] | None = None
    for attempt in range(4):
        proc = run_with_timeout([gdrive_bin, *args], timeout_sec=timeout_sec)
        last_proc = proc
        if proc.returncode == 0:
            return proc
        err_text = (proc.stderr or "") + (proc.stdout or "")
        if "rateLimitExceeded" in err_text or "403" in err_text:
            time.sleep(3 * (attempt + 1))
            continue
        break
    assert last_proc is not None
    raise RuntimeError(f"gdrive {args} failed ({last_proc.returncode}): {last_proc.stderr}")


def _parse_drive_folder_id(stdout: str, job_id: str) -> str:
    """Extract Drive folder ID from gdrive mkdir JSON/text output, or fall back to folder ls."""
    text = (stdout or "").strip()
    if text:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and parsed.get("id"):
                return str(parsed["id"])
        except json.JSONDecodeError:
            for token in text.split():
                if token.endswith(")"):
                    return token.rstrip(")")

    ls_proc = _run_gdrive_with_retry(["readonly", "ls", DRIVE_STAGING_FOLDER_ID, "--json"], timeout_sec=60)
    try:
        items = json.loads(ls_proc.stdout)
        if isinstance(items, list):
            for entry in reversed(items):
                if isinstance(entry, dict) and entry.get("name") == job_id and entry.get("id"):
                    return str(entry["id"])
    except json.JSONDecodeError:
        for line in reversed(ls_proc.stdout.splitlines()):
            parts = line.split()
            if len(parts) >= 2 and parts[1] == job_id:
                return parts[0]
    return ""


def upload_staging_bundle(output_dir: Path, job_id: str) -> str:
    """Upload staged job artifacts to Google Drive -> Numista.Ai -> Colab_Staging/<job_id>/."""
    mkdir_proc = _run_gdrive_with_retry(
        ["mutate", "mkdir", job_id, "--parent", DRIVE_STAGING_FOLDER_ID, "--json"],
        timeout_sec=60,
    )
    folder_id = _parse_drive_folder_id(mkdir_proc.stdout, job_id)
    if not folder_id:
        raise RuntimeError(f"Could not resolve Drive staging folder ID for {job_id!r}.")

    for artifact in sorted(output_dir.rglob("*")):
        if not artifact.is_file():
            continue
        _run_gdrive_with_retry(
            ["mutate", "upload", str(artifact), "--parent", folder_id],
            timeout_sec=120,
        )
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
    full_scale_authorized: bool = False,
) -> Path:
    """Execute a milestone batch job under all budget, license, timeout, and staging guards."""
    if milestone not in MILESTONE_SCRIPTS:
        raise GuardViolation(f"Unknown milestone {milestone!r}; expected one of {tuple(MILESTONE_SCRIPTS)}.")
    if mode == "full" and not full_scale_authorized:
        raise GuardViolation(
            "Full-scale mode is blocked under PILOTS ONLY BUILD authorization; "
            "pass full_scale_authorized=True only after pilot acceptance and a separate full-scale BUILD YES."
        )

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

        if milestone == "SMOKE":
            smoke_payload = extract_delimited_json(
                run_proc.stdout,
                "===COLAB_SMOKE_JSON_BEGIN===",
                "===COLAB_SMOKE_JSON_END===",
            )
            if (
                smoke_payload is None
                or not smoke_payload.get("cuda_available")
                or not smoke_payload.get("matmul_ok")
                or not smoke_payload.get("gcp_adc_env_absent")
                or smoke_payload.get("service_key_files_found", 1) != 0
            ):
                raise GuardViolation(
                    f"Live GPU smoke verification failed checks: {smoke_payload!r}\nstdout:\n{run_proc.stdout}"
                )
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "gpu_smoke_proof.json").write_bytes(
                (json.dumps(smoke_payload, indent=2) + "\n").encode("utf-8")
            )

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
        f"- Section 17 Terms Check: {GCP_SECTION_17_CONFIRMATION}\n"
    )
    (output_dir / "summary.md").write_bytes(summary_text.encode("utf-8"))

    extra_meta: dict[str, Any] = {
        "cu_spent": receipt["cu_spent"],
        "auto_shutdown_verified": sessions_clean,
    }
    if milestone == "M2":
        extra_meta["m2_review_owner"] = M2_REVIEW_OWNER

    manifest_path = build_manifest(
        job_id=job_id,
        milestone=milestone,
        mode=mode,
        output_dir=output_dir,
        model_name=default_model,
        input_provenance=[{"milestone": milestone, "mode": mode}],
        extra_meta=extra_meta,
    )
    if not verify_manifest(manifest_path):
        raise GuardViolation(f"Manifest verification failed for {manifest_path}")

    if not dry_run:
        folder_id = upload_staging_bundle(output_dir, job_id)
        print(f"Uploaded Drive staging folder ID: {folder_id}")
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
