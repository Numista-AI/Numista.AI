"""
Two-field mint backfill migration script (`mint` + `mint_mark`).

Safety controls (PLAN_TWO_FIELD_MINT_MODEL_v3.0.md §5):
  - Default mode is `--dry-run` (zero Firestore writes).
  - Live writes require `--execute --confirm-token=YES` (and Founder Eric's typed YES).
  - Rollback mode (`--rollback --backup-file=<path> --confirm-token=YES`) restores
    every modified document from the pre-mutation JSONL snapshot.
  - Phase 7 cleanup (`--prune-legacy-key --confirm-token=YES`) deletes deprecated `'Mint Mark'`.
  - Zero PII in logs or dry-run reports (only anonymized doc IDs and rule counts).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure repo / backend imports resolve whether invoked from root or numista_backend/
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent
_REPO_ROOT = _BACKEND_DIR.parent
for _p in (str(_REPO_ROOT), str(_BACKEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from services.mint_helpers import (
    read_mint_facility,
    read_mint_mark,
    resolve_two_field_mint,
)

BATCH_LIMIT = 400


def _durable_flush(fh: Any) -> None:
    """Flush + fsync so backup records survive a crash before the batch commits."""
    fh.flush()
    os.fsync(fh.fileno())


def _anon_doc_id(doc_path: str) -> str:
    """Return a non-PII short identifier for logging (never logs user email)."""
    parts = doc_path.split("/")
    coin_id = parts[-1] if parts else doc_path
    user_hash = hashlib.sha256(doc_path.encode("utf-8")).hexdigest()[:8]
    return f"u:{user_hash}/coins/{coin_id}"


def compute_migration_update(doc_data: dict[str, Any], force_recheck: bool = False) -> tuple[dict[str, Any] | None, int | None, str]:
    """
    Determine whether a coin document needs migration and return
    `(update_payload_or_None, rule_id_or_None, status_tag)`.
    """
    has_mint = "mint" in doc_data and doc_data.get("mint") is not None
    has_mm = "mint_mark" in doc_data and doc_data.get("mint_mark") is not None
    if has_mint and has_mm and not force_recheck:
        return None, None, "already_migrated"

    raw_mm = read_mint_mark(doc_data)
    raw_mint = read_mint_facility(doc_data)
    year = str(doc_data.get("Year") or doc_data.get("year") or "").strip()
    series = str(doc_data.get("Program/Series") or doc_data.get("program_series") or "").strip()
    denom = str(doc_data.get("Denomination") or doc_data.get("denomination") or "").strip()
    country = str(doc_data.get("Country") or doc_data.get("country") or "United States").strip()
    variety = str(doc_data.get("Variety") or doc_data.get("variety") or "").strip()
    strike_type = str(doc_data.get("Strike Type") or doc_data.get("strike_type") or "").strip()
    metal = str(doc_data.get("Metal Content") or doc_data.get("metal_content") or "").strip()
    item_no = str(doc_data.get("Retailer Item No.") or doc_data.get("retailer_item_no") or "").strip()

    new_mint, new_mm, rule_id = resolve_two_field_mint(
        raw_mint_mark=raw_mm,
        raw_mint=raw_mint,
        year=year,
        series=series,
        denomination=denom,
        country=country,
        variety=variety,
        strike_type=strike_type,
        metal_content=metal,
        retailer_item_no=item_no,
    )

    # F1 guard: never overwrite a non-empty existing facility with "".
    if not new_mint and raw_mint:
        new_mint = raw_mint

    payload = {
        "mint": new_mint,
        "mint_mark": new_mm,
        "Mint Mark": new_mm,
    }
    return payload, rule_id, f"rule_{rule_id}"


def run_forward(
    db: Any,
    execute: bool = False,
    limit: int | None = None,
    force_recheck: bool = False,
    backup_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Run forward migration in `--dry-run` (default) or `--execute` mode."""
    query = db.collection_group("coins")
    if limit is not None and limit > 0:
        query = query.limit(limit)

    stats: Counter[str] = Counter()
    samples: list[dict[str, Any]] = []
    backup_path: Path | None = None
    backup_fh = None

    if execute:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_dir = Path(backup_dir) if backup_dir else (_REPO_ROOT / "scratch")
        out_dir.mkdir(parents=True, exist_ok=True)
        backup_path = out_dir / f"mint_migration_backup_{ts}.jsonl"
        backup_fh = backup_path.open("w", encoding="utf-8")
        try:
            os.chmod(backup_path, 0o600)  # F4: backup holds user-identifying doc paths
        except OSError:
            pass

    batch = db.batch() if execute else None
    pending_ops = 0

    try:
        for snap in query.stream():
            stats["scanned"] += 1
            data = snap.to_dict() or {}
            payload, rule_id, tag = compute_migration_update(data, force_recheck=force_recheck)
            if payload is None:
                stats["already_migrated"] += 1
                continue

            stats["would_update"] += 1
            stats[tag] += 1

            doc_path = snap.reference.path
            if len(samples) < 10:
                samples.append({
                    "anon_id": _anon_doc_id(doc_path),
                    "rule": rule_id,
                    "before_mint": data.get("mint"),
                    "before_legacy_mm": data.get("Mint Mark"),
                    "after_mint": payload["mint"],
                    "after_mint_mark": payload["mint_mark"],
                })

            if execute and batch is not None and backup_fh is not None:
                backup_record = {
                    "doc_path": doc_path,
                    "had_mint": "mint" in data,
                    "prev_mint": data.get("mint"),
                    "had_mint_mark": "mint_mark" in data,
                    "prev_mint_mark": data.get("mint_mark"),
                    "had_legacy_mint_mark": "Mint Mark" in data,
                    "prev_legacy_mint_mark": data.get("Mint Mark"),
                    # F3: what this run wrote, so rollback can detect later user edits.
                    "new_mint": payload["mint"],
                    "new_mint_mark": payload["mint_mark"],
                    "new_legacy_mint_mark": payload["Mint Mark"],
                }
                backup_fh.write(json.dumps(backup_record) + "\n")
                batch.update(snap.reference, payload)
                pending_ops += 1
                if pending_ops >= BATCH_LIMIT:
                    _durable_flush(backup_fh)  # F4: backup on disk BEFORE commit
                    batch.commit()
                    stats["batches_committed"] += 1
                    batch = db.batch()
                    pending_ops = 0

        if execute and batch is not None and pending_ops > 0:
            _durable_flush(backup_fh)  # F4
            batch.commit()
            stats["batches_committed"] += 1
    finally:
        if backup_fh is not None:
            backup_fh.close()

    return {
        "mode": "execute" if execute else "dry-run",
        "stats": dict(stats),
        "samples": samples,
        "backup_file": str(backup_path) if backup_path else None,
    }


def run_rollback(
    db: Any,
    backup_file: str | Path,
    execute: bool = False,
    delete_sentinel: Any = None,
    force: bool = False,
) -> dict[str, Any]:
    """Restore documents from a JSONL backup snapshot created during `--execute`."""
    path = Path(backup_file)
    if not path.exists():
        raise FileNotFoundError(f"Backup file not found: {path}")

    if delete_sentinel is None:
        from firebase_admin import firestore as fb_firestore
        delete_sentinel = fb_firestore.DELETE_FIELD

    stats: Counter[str] = Counter()
    skipped: list[str] = []
    batch = db.batch() if execute else None
    pending_ops = 0

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            stats["records_read"] += 1
            rec = json.loads(line)
            doc_ref = db.document(rec["doc_path"])

            # F3: skip docs edited after the migration wrote them (unless forced).
            if not force and "new_mint" in rec:
                cur_snap = doc_ref.get()
                cur = (cur_snap.to_dict() or {}) if getattr(cur_snap, "exists", True) else {}
                if (
                    cur.get("mint") != rec["new_mint"]
                    or cur.get("mint_mark") != rec["new_mint_mark"]
                    or cur.get("Mint Mark") != rec["new_legacy_mint_mark"]
                ):
                    stats["skipped_modified_since_migration"] += 1
                    skipped.append(_anon_doc_id(rec["doc_path"]))
                    continue

            restore_payload: dict[str, Any] = {
                "mint": rec["prev_mint"] if rec.get("had_mint") else delete_sentinel,
                "mint_mark": rec["prev_mint_mark"] if rec.get("had_mint_mark") else delete_sentinel,
                # F3: forward always wrote the legacy key; remove it if it did not exist before.
                "Mint Mark": (
                    rec.get("prev_legacy_mint_mark")
                    if rec.get("had_legacy_mint_mark")
                    else delete_sentinel
                ),
            }

            stats["would_restore"] += 1
            if execute and batch is not None:
                batch.update(doc_ref, restore_payload)
                pending_ops += 1
                stats["restored"] += 1
                if pending_ops >= BATCH_LIMIT:
                    batch.commit()
                    batch = db.batch()
                    pending_ops = 0

    if execute and batch is not None and pending_ops > 0:
        batch.commit()

    return {
        "mode": "rollback-execute" if execute else "rollback-dry-run",
        "stats": dict(stats),
        "skipped_modified": skipped[:50],
    }


def run_prune_legacy_key(
    db: Any,
    execute: bool = False,
    delete_sentinel: Any = None,
) -> dict[str, Any]:
    """Phase 7: Delete deprecated `'Mint Mark'` field after 14-day zero-sync verification."""
    if delete_sentinel is None:
        from firebase_admin import firestore as fb_firestore
        delete_sentinel = fb_firestore.DELETE_FIELD

    stats: Counter[str] = Counter()
    batch = db.batch() if execute else None
    pending_ops = 0

    for snap in db.collection_group("coins").stream():
        stats["scanned"] += 1
        data = snap.to_dict() or {}
        if "Mint Mark" not in data:
            continue
        if "mint" not in data or "mint_mark" not in data:
            stats["skipped_unmigrated"] += 1
            continue
        stats["would_prune"] += 1
        if execute and batch is not None:
            batch.update(snap.reference, {"Mint Mark": delete_sentinel})
            pending_ops += 1
            stats["pruned"] += 1
            if pending_ops >= BATCH_LIMIT:
                batch.commit()
                batch = db.batch()
                pending_ops = 0

    if execute and batch is not None and pending_ops > 0:
        batch.commit()

    return {"mode": "prune-execute" if execute else "prune-dry-run", "stats": dict(stats)}


def _init_firestore() -> Any:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
        else:
            firebase_admin.initialize_app()
    return firestore.client()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Two-field mint migration tool (dry-run by default).")
    parser.add_argument("--dry-run", action="store_true", help="Report counts without writing (default).")
    parser.add_argument("--execute", action="store_true", help="Execute live Firestore writes (requires --confirm-token=YES).")
    parser.add_argument("--rollback", action="store_true", help="Rollback from JSONL backup file.")
    parser.add_argument("--rollback-force", action="store_true", help="Rollback even docs edited after migration.")
    parser.add_argument("--prune-legacy-key", action="store_true", help="Phase 7: remove deprecated 'Mint Mark' key.")
    parser.add_argument("--backup-file", type=str, default="", help="Path to JSONL backup file for --rollback.")
    parser.add_argument("--confirm-token", type=str, default="", help="Must be 'YES' for any write operation.")
    parser.add_argument("--limit", type=int, default=None, help="Optional document limit for canary dry-run.")
    parser.add_argument("--force-recheck", action="store_true", help="Re-evaluate docs that already have mint & mint_mark.")
    args = parser.parse_args(argv)

    is_confirmed = args.confirm_token == "YES"
    db = _init_firestore()

    if args.rollback:
        if not args.backup_file:
            parser.error("--rollback requires --backup-file=<path>")
        result = run_rollback(db, args.backup_file, execute=is_confirmed, force=args.rollback_force)
    elif args.prune_legacy_key:
        result = run_prune_legacy_key(db, execute=is_confirmed)
    else:
        if args.execute and not is_confirmed:
            print("BLOCKED: --execute requires --confirm-token=YES and Founder Eric's explicit YES.", file=sys.stderr)
            return 2
        result = run_forward(
            db,
            execute=bool(args.execute and is_confirmed),
            limit=args.limit,
            force_recheck=args.force_recheck,
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
