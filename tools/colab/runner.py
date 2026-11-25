"""Wrapper runner for google-colab-cli (`colab run`) with CU guards and Drive staging."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tarfile
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
from tools.colab.jobs.m1_framing import evaluate_framing_metrics, pack_m1_pilot_inputs
from tools.colab.jobs.m2_embeddings import pack_m2_pilot_inputs
from tools.colab.jobs.m4_ocr import pack_m4_pilot_inputs

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

    ls_proc = _run_gdrive_with_retry(
        ["readonly", "ls", DRIVE_STAGING_FOLDER_ID, "--max", "0", "--json"],
        timeout_sec=60,
    )
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
            timeout_sec=300,
        )
    return folder_id


def _execute_colab_session(
    *,
    cli_bin: str,
    job_id: str,
    gpu: str,
    effective_timeout: int,
    inputs_tar: Path,
    remote_input_path: str,
    remote_script: Path,
    remote_output_path: str,
    local_outputs_tar_gz: Path,
    output_dir: Path,
) -> bool:
    """Provision a Colab GPU VM, upload inputs, exec script, download outputs, and always stop."""
    new_proc = run_with_timeout([cli_bin, "new", "--gpu", gpu.upper(), "-s", job_id], timeout_sec=300)
    if new_proc.returncode != 0:
        raise RuntimeError(f"`colab new` failed ({new_proc.returncode}): {new_proc.stderr}")

    sessions_clean = False
    try:
        up_proc = run_with_timeout(
            [cli_bin, "upload", "-s", job_id, str(inputs_tar), remote_input_path],
            timeout_sec=300,
        )
        if up_proc.returncode != 0:
            raise RuntimeError(f"`colab upload` failed ({up_proc.returncode}): {up_proc.stderr}")

        exec_proc = run_with_timeout(
            [cli_bin, "exec", "-s", job_id, "--timeout", "0", "-f", str(remote_script)],
            timeout_sec=effective_timeout,
        )
        if exec_proc.returncode != 0:
            raise RuntimeError(
                f"`colab exec` failed ({exec_proc.returncode}):\nstdout:\n{exec_proc.stdout}\nstderr:\n{exec_proc.stderr}"
            )

        dl_proc = run_with_timeout(
            [cli_bin, "download", "-s", job_id, remote_output_path, str(local_outputs_tar_gz)],
            timeout_sec=300,
        )
        if dl_proc.returncode != 0:
            raise RuntimeError(f"`colab download` failed ({dl_proc.returncode}): {dl_proc.stderr}")
    finally:
        try:
            run_with_timeout([cli_bin, "stop", "-s", job_id], timeout_sec=90)
        finally:
            sess_proc = run_with_timeout([cli_bin, "sessions"], timeout_sec=60)
            sessions_clean = verify_zero_active_sessions(sess_proc.stdout, expected_session=job_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(local_outputs_tar_gz, "r:gz") as tf:
        tf.extractall(output_dir, filter="data")
    return sessions_clean


def _run_staged_milestone_live(
    *,
    milestone: str,
    cli_bin: str,
    job_id: str,
    gpu: str,
    effective_timeout: int,
    input_dir: Path,
    limit: int,
    output_dir: Path,
) -> tuple[bool, list[dict[str, Any]], dict[str, Any]]:
    """Pack inputs, run remote M1/M2/M4 GPU worker in Colab, and validate staged outputs."""
    jobs_dir = Path(__file__).resolve().parent / "jobs"
    inputs_tar = output_dir.parent / f"{job_id}_inputs.tar"
    outputs_tar_gz = output_dir.parent / f"{job_id}_outputs.tar.gz"

    if milestone == "M1":
        provenance = pack_m1_pilot_inputs(input_dir, inputs_tar, limit=limit)
        remote_script = jobs_dir / "m1_framing_remote.py"
        remote_in, remote_out = "/content/m1_inputs.tar", "/content/m1_outputs.tar.gz"
    elif milestone == "M2":
        provenance = pack_m2_pilot_inputs(input_dir, inputs_tar, limit=limit)
        remote_script = jobs_dir / "m2_embeddings_remote.py"
        remote_in, remote_out = "/content/m2_inputs.tar", "/content/m2_outputs.tar.gz"
    elif milestone == "M4":
        provenance = pack_m4_pilot_inputs(input_dir, inputs_tar, max_pages=limit)
        remote_script = jobs_dir / "m4_ocr_remote.py"
        remote_in, remote_out = "/content/m4_inputs.tar", "/content/m4_outputs.tar.gz"
    else:
        raise GuardViolation(f"Milestone {milestone!r} does not use staged archive live execution.")

    sessions_clean = _execute_colab_session(
        cli_bin=cli_bin,
        job_id=job_id,
        gpu=gpu,
        effective_timeout=effective_timeout,
        inputs_tar=inputs_tar,
        remote_input_path=remote_in,
        remote_script=remote_script,
        remote_output_path=remote_out,
        local_outputs_tar_gz=outputs_tar_gz,
        output_dir=output_dir,
    )

    if milestone == "M1":
        metrics_data = json.loads((output_dir / "framing_metrics.json").read_text(encoding="utf-8"))
        local_eval = evaluate_framing_metrics(metrics_data["items"])
        extra: dict[str, Any] = {
            "framing_total": local_eval["total"],
            "framing_passed": local_eval["passed"],
            "framing_pass_rate_pct": local_eval["pass_rate_pct"],
            "framing_min_measured_pct": metrics_data.get("min_measured_pct"),
            "framing_max_measured_pct": metrics_data.get("max_measured_pct"),
            "framing_mean_measured_pct": metrics_data.get("mean_measured_pct"),
        }
    elif milestone == "M2":
        flags_data = json.loads((output_dir / "advisory_flags.json").read_text(encoding="utf-8"))
        if flags_data.get("advisory_only") is not True or flags_data.get("mutated_catalog") is not False:
            raise GuardViolation("M2 advisory_flags.json violated zero-mutation governance fields.")
        eval_data = json.loads((output_dir / "m2_eval_report.json").read_text(encoding="utf-8"))
        extra = {
            "m2_total_images": eval_data["total_images"],
            "m2_flagged_count": eval_data["flagged_count"],
            "m2_known_bad_recall_pct": eval_data["known_bad_recall_pct"],
            "m2_at07_passed": eval_data["at07_passed"],
        }
    else:
        ocr_report = json.loads((output_dir / "ocr_error_report.json").read_text(encoding="utf-8"))
        extra = {
            "m4_handcheck_status": ocr_report.get("status"),
            "m4_sample_pages_checked": ocr_report.get("sample_pages_checked"),
            "m4_cer": ocr_report.get("cer"),
            "m4_wer": ocr_report.get("wer"),
        }
    return sessions_clean, provenance, extra


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
    input_dir: Path | None = None,
    limit: int = 120,
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
    input_provenance: list[dict[str, Any]] = [{"milestone": milestone, "mode": mode}]
    milestone_extra: dict[str, Any] = {}

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
        if milestone in ("M1", "M2", "M4"):
            if input_dir is None:
                raise GuardViolation(f"Live {milestone} pilot requires --input-dir pointing to staged inputs.")
            sessions_clean, input_provenance, milestone_extra = _run_staged_milestone_live(
                milestone=milestone,
                cli_bin=cli_bin,
                job_id=job_id,
                gpu=gpu,
                effective_timeout=effective_timeout,
                input_dir=input_dir,
                limit=limit,
                output_dir=output_dir,
            )
        else:
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
    summary_lines = [
        f"# Colab Job Summary — {job_id}\n\n",
        f"- Plan SHA8: `{PLAN_SHA8}`\n",
        f"- Milestone / Mode: `{milestone}` / `{mode}`\n",
        f"- GPU: `{gpu.upper()}`\n",
        f"- CU Balance: `{pre_balance:.2f}` -> `{post_balance:.2f}` (spent `{receipt['cu_spent']:.4f}`)\n",
        f"- Auto-Shutdown Verified: `{sessions_clean}`\n",
        f"- Duration: `{duration_sec:.2f}s`\n",
        f"- Section 17 Terms Check: {GCP_SECTION_17_CONFIRMATION}\n",
    ]
    if milestone == "M1" and milestone_extra:
        summary_lines.append(
            f"- M1 Framing Pass Rate: `{milestone_extra['framing_passed']}/{milestone_extra['framing_total']}` "
            f"(`{milestone_extra['framing_pass_rate_pct']}%`, min `{milestone_extra['framing_min_measured_pct']}%`, "
            f"max `{milestone_extra['framing_max_measured_pct']}%`, mean `{milestone_extra['framing_mean_measured_pct']}%`)\n"
        )
    elif milestone == "M2" and milestone_extra:
        summary_lines.append(
            f"- M2 Advisory Audit: `{milestone_extra['m2_flagged_count']}/{milestone_extra['m2_total_images']}` flagged "
            f"(known-bad recall `{milestone_extra['m2_known_bad_recall_pct']}%`, AT-07 passed `{milestone_extra['m2_at07_passed']}`)\n"
        )
    elif milestone == "M4" and milestone_extra:
        summary_lines.append(
            f"- M4 OCR Hand-Check: status `{milestone_extra['m4_handcheck_status']}`, "
            f"pages `{milestone_extra['m4_sample_pages_checked']}`, CER `{milestone_extra['m4_cer']}`, WER `{milestone_extra['m4_wer']}`\n"
        )
    (output_dir / "summary.md").write_bytes("".join(summary_lines).encode("utf-8"))

    extra_meta: dict[str, Any] = {
        "cu_spent": receipt["cu_spent"],
        "auto_shutdown_verified": sessions_clean,
        **milestone_extra,
    }
    if milestone == "M2":
        extra_meta["m2_review_owner"] = M2_REVIEW_OWNER

    manifest_path = build_manifest(
        job_id=job_id,
        milestone=milestone,
        mode=mode,
        output_dir=output_dir,
        model_name=default_model,
        input_provenance=input_provenance,
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
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=120)
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
        input_dir=args.input_dir,
        limit=args.limit,
    )
    print(f"Completed {args.job_id}: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
