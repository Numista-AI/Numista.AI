#!/usr/bin/env python3
"""
remediate_2026_collectibles_docs.py
Phase B targeted Firestore remediation for 2026 America250 - Numismatic Collectibles.

Safety guarantees:
  - Requires BOTH explicit --user_email AND explicit --doc_ids (no blind sweeps).
  - Defaults to DRY-RUN; never writes without --write.
  - Captures full pre-write JSON backups when --backup_out is supplied.
  - Writes machine-readable audit changelog when --changelog_out is supplied.
  - Supports --rollback --backup <path> to restore exact pre-write field states.
  - Uses Firestore REST API with active gcloud ADC/CLI access token (eric@numista.ai).
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List

PROJECT_ID = "studio-9101802118-8c9a8"
FIRESTORE_BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# Exact locked v2.1 field remediations keyed by Firestore doc_id
DOC_REMEDIATIONS: Dict[str, Dict[str, Any]] = {
    # 26EA — American Eagle 2026 1oz Silver Proof (remove bogus "Reverse" token)
    "e91efa62-4e8d-4920-a928-c0c97659bcdc": {
        "Variety": "250 Privy / W-Proof",
        "Strike Type": "Proof",
    },
    # 26SQRP — Semiquincentennial President Donald J. Trump $1 Roll (Philadelphia, unmarked)
    "7a32932ebc4e94a586534e7180cd1c4372c4f17d": {
        "Mint Mark": "",
        "mint_mark": "",
        "mint": "Philadelphia",
    },
    # 26XL — Peace Silver Dollar 2026 Reverse Proof (schema consistency backfill)
    "a59853c1-b72b-414d-8b8e-de6813c29996": {
        "Strike Type": "Reverse Proof",
    },
}


def get_access_token() -> str:
    gcloud_bin = "gcloud.cmd" if os.name == "nt" else "gcloud"
    return subprocess.check_output([gcloud_bin, "auth", "print-access-token"], text=True).strip()


def get_operator_email() -> str:
    gcloud_bin = "gcloud.cmd" if os.name == "nt" else "gcloud"
    try:
        return subprocess.check_output(
            [gcloud_bin, "config", "get-value", "account"], text=True
        ).strip()
    except Exception:
        return "unknown"


def unwrap_fs_value(val: Dict[str, Any]) -> Any:
    if "stringValue" in val:
        return val["stringValue"]
    if "integerValue" in val:
        return int(val["integerValue"])
    if "doubleValue" in val:
        return float(val["doubleValue"])
    if "booleanValue" in val:
        return val["booleanValue"]
    if "nullValue" in val:
        return None
    if "arrayValue" in val:
        return [unwrap_fs_value(x) for x in val["arrayValue"].get("values", [])]
    if "mapValue" in val:
        return {k: unwrap_fs_value(v) for k, v in val["mapValue"].get("fields", {}).items()}
    return None


def wrap_fs_value(val: Any) -> Dict[str, Any]:
    if val is None:
        return {"nullValue": None}
    if isinstance(val, bool):
        return {"booleanValue": val}
    if isinstance(val, int):
        return {"integerValue": str(val)}
    if isinstance(val, float):
        return {"doubleValue": val}
    if isinstance(val, str):
        return {"stringValue": val}
    if isinstance(val, list):
        return {"arrayValue": {"values": [wrap_fs_value(x) for x in val]}}
    if isinstance(val, dict):
        return {"mapValue": {"fields": {k: wrap_fs_value(v) for k, v in val.items()}}}
    return {"stringValue": str(val)}


def fs_get_doc(token: str, user_email: str, doc_id: str) -> Dict[str, Any]:
    doc_path = f"users/{urllib.parse.quote(user_email, safe='')}/coins/{urllib.parse.quote(doc_id, safe='')}"
    req = urllib.request.Request(
        f"{FIRESTORE_BASE}/{doc_path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    return {k: unwrap_fs_value(v) for k, v in raw.get("fields", {}).items()}


def fs_patch_fields(token: str, user_email: str, doc_id: str, updates: Dict[str, Any]) -> None:
    """Applies field updates (omits field from body to delete it when value is _DELETE_SENTINEL)."""
    doc_path = f"users/{urllib.parse.quote(user_email, safe='')}/coins/{urllib.parse.quote(doc_id, safe='')}"
    mask_parts = []
    fields_payload: Dict[str, Any] = {}
    for k, v in updates.items():
        field_expr = f"`{k}`" if not k.replace("_", "").isalnum() else k
        mask_parts.append("updateMask.fieldPaths=" + urllib.parse.quote(field_expr, safe=""))
        if v is not _ABSENT:
            fields_payload[k] = wrap_fs_value(v)

    url = f"{FIRESTORE_BASE}/{doc_path}?{'&'.join(mask_parts)}"
    body = json.dumps({"fields": fields_payload}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        resp.read()


_ABSENT = object()


def run_remediate(
    user_email: str,
    doc_ids: List[str],
    write: bool,
    backup_out: str | None,
    changelog_out: str | None,
) -> int:
    unknown_ids = [d for d in doc_ids if d not in DOC_REMEDIATIONS]
    if unknown_ids:
        print(f"ERROR: Refusing to process unknown doc_id(s) not in allowlist: {unknown_ids}", file=sys.stderr)
        return 2

    token = get_access_token()
    operator = get_operator_email()
    ts_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    mode = "WRITE" if write else "DRY-RUN"
    print("=" * 72)
    print(f"remediate_2026_collectibles_docs [{mode}]")
    print(f"user_email : {user_email}")
    print(f"operator   : {operator}")
    print(f"doc_ids    : {', '.join(doc_ids)}")
    print("=" * 72)

    backup_payload: Dict[str, Any] = {
        "captured_utc": ts_utc,
        "project_id": PROJECT_ID,
        "user_email": user_email,
        "docs": {},
    }
    changelog_entries: List[Dict[str, Any]] = []

    for doc_id in doc_ids:
        current = fs_get_doc(token, user_email, doc_id)
        backup_payload["docs"][doc_id] = current
        target_fields = DOC_REMEDIATIONS[doc_id]
        sku = current.get("Retailer Item No.") or current.get("item_number") or current.get("retailer_item_num") or "?"

        print(f"\nDoc: {doc_id} (SKU={sku})")
        pending_patch: Dict[str, Any] = {}
        for field, after_val in target_fields.items():
            before_val = current.get(field, "<ABSENT>")
            changed = (field not in current) or (current[field] != after_val)
            status_tag = "CHANGE" if changed else "NO-OP"
            print(f"  [{status_tag}] {field!r}: {before_val!r} -> {after_val!r}")
            if changed:
                pending_patch[field] = after_val
                changelog_entries.append({
                    "doc_id": doc_id,
                    "sku": sku,
                    "field": field,
                    "before": None if field not in current else current[field],
                    "before_existed": field in current,
                    "after": after_val,
                    "timestamp_utc": ts_utc,
                    "operator": operator,
                    "mode": mode,
                })

        if write and pending_patch:
            fs_patch_fields(token, user_email, doc_id, pending_patch)
            print(f"  -> PATCHED {len(pending_patch)} field(s) in Firestore.")
        elif not write:
            print("  -> [DRY-RUN] No writes performed.")

    if backup_out:
        os.makedirs(os.path.dirname(os.path.abspath(backup_out)), exist_ok=True)
        with open(backup_out, "w", encoding="utf-8") as fh:
            json.dump(backup_payload, fh, indent=2, default=str)
        print(f"\nPre-write backup written: {backup_out}")

    if changelog_out:
        os.makedirs(os.path.dirname(os.path.abspath(changelog_out)), exist_ok=True)
        with open(changelog_out, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "timestamp_utc": ts_utc,
                    "user_email": user_email,
                    "mode": mode,
                    "operator": operator,
                    "changes": changelog_entries,
                },
                fh,
                indent=2,
                default=str,
            )
        print(f"Audit changelog written: {changelog_out}")

    return 0


def run_rollback(user_email: str, doc_ids: List[str], backup_path: str, write: bool) -> int:
    with open(backup_path, "r", encoding="utf-8") as fh:
        backup = json.load(fh)
    docs_map = backup.get("docs", {})
    token = get_access_token()
    mode = "ROLLBACK-WRITE" if write else "ROLLBACK-DRY-RUN"
    print(f"Running {mode} from {backup_path} for {user_email}...")

    for doc_id in doc_ids:
        if doc_id not in docs_map or doc_id not in DOC_REMEDIATIONS:
            print(f"ERROR: Missing {doc_id} in backup or allowlist.", file=sys.stderr)
            return 2
        orig = docs_map[doc_id]
        restore_patch: Dict[str, Any] = {}
        for field in DOC_REMEDIATIONS[doc_id]:
            restore_patch[field] = orig[field] if field in orig else _ABSENT
            print(f"  {doc_id} | {field!r} -> {'<DELETE>' if restore_patch[field] is _ABSENT else repr(restore_patch[field])}")
        if write:
            fs_patch_fields(token, user_email, doc_id, restore_patch)
            print(f"  -> Restored {doc_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Targeted Phase B Firestore remediation for 2026 Collectibles.")
    parser.add_argument("--user_email", required=True, help="Target user email (required).")
    parser.add_argument("--doc_ids", nargs="+", required=True, help="Explicit Firestore document IDs (required).")
    parser.add_argument("--backup_out", default=None, help="Path to write full pre-write JSON backup.")
    parser.add_argument("--changelog_out", default=None, help="Path to write field-level audit changelog JSON.")
    parser.add_argument("--write", action="store_true", default=False, help="Apply writes (default is dry-run).")
    parser.add_argument("--rollback", action="store_true", default=False, help="Restore fields from --backup.")
    parser.add_argument("--backup", default=None, help="Backup JSON path for --rollback.")
    args = parser.parse_args()

    if not args.user_email or not args.doc_ids:
        print("ERROR: Both --user_email and --doc_ids are required.", file=sys.stderr)
        return 2

    if args.rollback:
        if not args.backup:
            print("ERROR: --rollback requires --backup <path>.", file=sys.stderr)
            return 2
        return run_rollback(args.user_email, args.doc_ids, args.backup, args.write)

    return run_remediate(
        user_email=args.user_email,
        doc_ids=args.doc_ids,
        write=args.write,
        backup_out=args.backup_out,
        changelog_out=args.changelog_out,
    )


if __name__ == "__main__":
    raise SystemExit(main())
