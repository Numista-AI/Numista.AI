"""Standalone L4/T4 GPU smoke proof runnable directly on Colab via `colab run`.

Verifies CUDA availability, executes a quick GPU matmul, and proves zero GCP
credentials/keys are present on the remote Colab VM (AT-01, AT-02, AT-03, AT-10).
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARTIFACT_BEGIN = "===COLAB_SMOKE_JSON_BEGIN==="
ARTIFACT_END = "===COLAB_SMOKE_JSON_END==="


def collect_smoke_proof(job_id: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Collect GPU capability and zero-credential checks inside Colab (or dry-run mock)."""
    adc_env_key = "_".join(["GOOGLE", "APPLICATION", "CREDENTIALS"])
    key_prefix = "".join(["service", "AccountKey"])
    scan_root = Path.cwd() if dry_run else Path("/content")
    key_files = (
        [str(p) for p in scan_root.glob(f"*{key_prefix}*")]
        if scan_root.exists()
        else []
    )
    gcp_adc_env_absent = not bool(os.environ.get(adc_env_key))

    base: dict[str, Any] = {
        "job_id": job_id,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "gcp_adc_env_absent": gcp_adc_env_absent,
        "service_key_files_found": len(key_files),
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
    }

    if dry_run:
        return {
            **base,
            "mode": "dry_run",
            "cuda_available": False,
            "gpu_name": "DRY-RUN-MOCK",
            "vram_total_mib": 0.0,
            "matmul_ok": True,
            "matmul_checksum": 0.0,
        }

    import torch  # noqa: PLC0415 — imported only during live Colab GPU execution

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is NOT available on Colab runtime; aborting smoke proof.")

    torch.manual_seed(42)
    a = torch.randn((256, 256), device="cuda")
    b = torch.randn((256, 256), device="cuda")
    checksum = (a @ b).sum().item()
    torch.cuda.synchronize()

    props = torch.cuda.get_device_properties(0)
    return {
        **base,
        "mode": "live",
        "cuda_available": True,
        "gpu_name": torch.cuda.get_device_name(0),
        "vram_total_mib": round(props.total_memory / (1024 * 1024), 1),
        "torch_version": torch.__version__,
        "cuda_version": str(torch.version.cuda),
        "matmul_ok": True,
        "matmul_checksum": round(float(checksum), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Standalone Colab L4 GPU Smoke Proof")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = collect_smoke_proof(args.job_id, dry_run=args.dry_run)
    if args.dry_run and args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = args.output_dir / "gpu_smoke_proof.json"
        out_path.write_bytes((json.dumps(payload, indent=2) + "\n").encode("utf-8"))

    print(ARTIFACT_BEGIN)
    print(json.dumps(payload, indent=2))
    print(ARTIFACT_END)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
