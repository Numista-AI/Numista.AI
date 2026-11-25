#!/usr/bin/env python3
"""
tools/catalog/apply_image_attach.py
Offline, fail-closed local image-attach writer for attach_manifest_v4 (CR3 v1.1).

Makes ZERO network calls. Enforces manifest SHA verification before reading,
strict approved GCS URL and certified license allow-lists before writing,
explicit 7-key output mapping (source == credit; never internal columns or
*_file_page_url), pre-write target md5 + named backup, post-write sanitize /
pii_gate / P10 validation, and post-write md5 readback.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    from tools.catalog.build_public_catalog import (
        audit_catalog_images,
        is_approved_image_url,
    )
    from tools.catalog.image_license_allowlist import is_certified_license
    from tools.catalog.pii_gate_validator import scan_document_for_leaks
except ImportError:
    try:
        from build_public_catalog import audit_catalog_images, is_approved_image_url
        from image_license_allowlist import is_certified_license
        from pii_gate_validator import scan_document_for_leaks
    except ImportError:
        _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        if _THIS_DIR not in sys.path:
            sys.path.insert(0, _THIS_DIR)
        from build_public_catalog import audit_catalog_images, is_approved_image_url
        from image_license_allowlist import is_certified_license
        from pii_gate_validator import scan_document_for_leaks


# Explicit 7-key allow-list (Part 4, m1) + optional Wave 2 Component E `role` key
# (packaging, packaging_alt, set_contents, privy_detail, set_member, primary, extra).
ALLOWED_IMAGE_KEYS = (
    "url",
    "side",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
)
ALLOWED_ROLE_VALUES = frozenset({
    "packaging",
    "packaging_alt",
    "set_contents",
    "privy_detail",
    "set_member",
    "primary",
    "extra",
})

REPRESENTATIVE_PHOTO_LABEL = "Representative photo \u2014 date or mint may differ"
DEFAULT_CAPTION = "Numista.Ai reference photo"

# m2: "copy" and "path" are broad words; any future real credit that trips them
# needs an explicitly reviewed exception, never silent removal from this list.
P10_FORBIDDEN_PATTERNS: Tuple[Tuple[str, re.Pattern], ...] = (
    ("this pass", re.compile(r"this pass", re.IGNORECASE)),
    ("path", re.compile(r"path", re.IGNORECASE)),
    ("re-pointed", re.compile(r"re-pointed", re.IGNORECASE)),
    ("copy", re.compile(r"copy", re.IGNORECASE)),
    ("CanonicalMintAssetService", re.compile(r"CanonicalMintAssetService", re.IGNORECASE)),
    ("coin_image_index", re.compile(r"coin_image_index", re.IGNORECASE)),
    ("/workspace", re.compile(r"/workspace", re.IGNORECASE)),
    ("gs://", re.compile(r"gs://", re.IGNORECASE)),
    ("numista-reference-library", re.compile(r"numista-reference-library", re.IGNORECASE)),
    ("us_mint_coin_images", re.compile(r"us_mint_coin_images", re.IGNORECASE)),
    ("No copy", re.compile(r"No copy", re.IGNORECASE)),
    ("service_class", re.compile(r"\b[A-Z][A-Za-z0-9]+Service\b")),
    ("storage.googleapis.com", re.compile(r"storage\.googleapis\.com", re.IGNORECASE)),
    ("raw_boolean", re.compile(r"\b(?:true|false)\b", re.IGNORECASE)),
    ("nac_or_id", re.compile(r"(?:NAC1\.|\bgsid\b)", re.IGNORECASE)),
    ("null_or_None", re.compile(r"\b(?:null|None)\b")),
)


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def file_md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_yes_no_bool(raw_val: Any, *, field_name: str) -> bool:
    if isinstance(raw_val, bool):
        return raw_val
    if isinstance(raw_val, str):
        val = raw_val.strip()
        if val == "Y":
            return True
        if val == "N":
            return False
    raise ValueError(f"{field_name} must be 'Y' or 'N', got {raw_val!r}")


def scan_text_p10(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    return [name for name, pat in P10_FORBIDDEN_PATTERNS if pat.search(text)]


def scan_rendered_captions_p10(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Checks rendered card/detail captions (`credit ?? source`, fallback DEFAULT_CAPTION)
    and representative labels for every image object in `records`, plus raw `source`.
    """
    hits: List[Dict[str, Any]] = []
    for row in records:
        nac = row.get("nac_code")
        for field_name in ("primary_image", "type_image"):
            img = row.get(field_name)
            if not isinstance(img, dict):
                continue
            _check_image_captions_p10(nac, field_name, img, field_name == "type_image", hits)
        for idx, extra in enumerate(row.get("extra_images") or []):
            if isinstance(extra, dict):
                _check_image_captions_p10(nac, f"extra_images[{idx}]", extra, False, hits)
    return hits


def _check_image_captions_p10(
    nac: Optional[str],
    field_name: str,
    img: Dict[str, Any],
    is_type_field: bool,
    hits: List[Dict[str, Any]],
) -> None:
    credit = img.get("credit")
    source = img.get("source")
    raw_caption = (
        credit.strip()
        if isinstance(credit, str) and credit.strip()
        else (
            source.strip()
            if isinstance(source, str) and source.strip()
            else DEFAULT_CAPTION
        )
    )
    texts_to_check = [("rendered_caption", raw_caption)]
    if isinstance(source, str) and source.strip():
        texts_to_check.append(("raw_source", source.strip()))
    if isinstance(credit, str) and credit.strip():
        texts_to_check.append(("raw_credit", credit.strip()))
    unique_side = img.get("unique_side")
    if unique_side is False or (unique_side is None and is_type_field):
        texts_to_check.append(("representative_label", REPRESENTATIVE_PHOTO_LABEL))

    for label, text in texts_to_check:
        matched = scan_text_p10(text)
        if matched:
            hits.append({
                "nac_code": nac,
                "field": field_name,
                "label": label,
                "tokens": matched,
                "text": text,
            })


def build_side_image_object(row: Dict[str, Any], side: str) -> Dict[str, Any]:
    """
    Maps a single side ('obverse', 'reverse', 'packaging', or 'privy_detail') into a
    strict allow-listed catalog image object. Fails closed on unapproved URL, uncertified
    license, missing credit/source_url, non-Y/N unique_side, invalid role, or P10 caption leak.
    """
    if side not in ("obverse", "reverse", "packaging", "privy_detail"):
        raise ValueError(f"Unsupported side {side!r}; expected 'obverse', 'reverse', 'packaging', or 'privy_detail'")

    url = (row.get(f"{side}_public_url") or "").strip()
    if not is_approved_image_url(url):
        raise ValueError(f"{side}_public_url rejected by allow-list: {url!r}")

    lic = row.get(f"{side}_license")
    lic_class = row.get(f"{side}_license_class")
    class_arg = lic_class if (f"{side}_license_class" in row and lic_class != "") else None
    if f"{side}_license_class" in row and not (isinstance(lic_class, str) and lic_class):
        raise ValueError(f"{side}_license_class missing or empty")
    if not is_certified_license(lic, class_arg):
        raise ValueError(f"{side}_license is missing, empty, or not certified: {lic!r}")

    unique_side = parse_yes_no_bool(
        row.get(f"{side}_unique_side"),
        field_name=f"{side}_unique_side",
    )

    credit = (row.get(f"{side}_credit") or "").strip()
    if not credit:
        raise ValueError(f"{side}_credit is missing or empty")
    if "used with permission" in credit.lower() or "courtesy" in credit.lower():
        raise ValueError(f"{side}_credit uses forbidden wording (use 'Image: United States Mint'): {credit!r}")

    source_url = (row.get(f"{side}_source_url") or "").strip()
    if not source_url:
        raise ValueError(f"{side}_source_url is missing or empty")

    raw_source = (row.get(f"{side}_source") or "").strip()
    if raw_source and scan_text_p10(raw_source):
        raise ValueError(f"{side}_source failed P10 check: {raw_source!r}")
    if scan_text_p10(credit):
        raise ValueError(f"{side}_credit failed P10 check: {credit!r}")

    obj = {
        "url": url,
        "side": side,
        "unique_side": unique_side,
        "license": lic,
        "credit": credit,
        "source": credit,  # Spec: source always equals credit
        "source_url": source_url,
    }
    raw_role = (row.get(f"{side}_role") or "").strip()
    if raw_role:
        if raw_role not in ALLOWED_ROLE_VALUES:
            raise ValueError(f"{side}_role not in ALLOWED_ROLE_VALUES: {raw_role!r}")
        obj["role"] = raw_role
    else:
        assert tuple(obj.keys()) == ALLOWED_IMAGE_KEYS
    return obj


def attach_packaging_or_privy_image(
    target_entry: Dict[str, Any],
    img_obj: Dict[str, Any],
) -> None:
    """
    Wave 2 Component E helper: attaches packaging/packaging_alt/set_contents images into
    `packaging_images[]` and `privy_detail` close-ups as an additional `extra_images[]` item
    (preserving full obverse & full reverse as separate entries; never overwrites primary).
    """
    role = (img_obj.get("role") or "").strip()
    if role in ("packaging", "packaging_alt", "set_contents"):
        pkg_list = list(target_entry.get("packaging_images") or [])
        if role == "packaging":
            # Eric Vision Rule 2a: OGP packaging is [0] / default image for set rows
            pkg_list = [img_obj] + [p for p in pkg_list if p.get("url") != img_obj.get("url")]
        else:
            if not any(p.get("url") == img_obj.get("url") for p in pkg_list):
                pkg_list.append(img_obj)
        target_entry["packaging_images"] = pkg_list
    elif role == "privy_detail":
        extras = list(target_entry.get("extra_images") or [])
        if not any(e.get("url") == img_obj.get("url") for e in extras):
            extras.append(img_obj)
        target_entry["extra_images"] = extras
    else:
        raise ValueError(f"Unsupported packaging/privy role: {role!r}")


def _load_target_records(target_path: str) -> Tuple[List[Dict[str, Any]], bool]:
    """Loads JSON array or JSONL catalog file; returns (records, is_jsonl)."""
    with open(target_path, "r", encoding="utf-8") as f:
        raw = f.read()
    stripped = raw.lstrip()
    if stripped.startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON target must be a list of catalog objects")
        return data, False
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return records, True


def _write_records(output_path: str, records: List[Dict[str, Any]], is_jsonl: bool) -> None:
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        if is_jsonl:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        else:
            json.dump(records, f, indent=2, ensure_ascii=False)
            f.write("\n")


def apply_image_attach(
    *,
    manifest_path: str,
    target_path: str,
    output_path: str,
    expected_sha256: Optional[str] = None,
    expected_sha8: Optional[str] = None,
    backup_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the 6-step local image-attach pipeline:
      1. Verify manifest SHA before reading CSV.
      2. Pre-validate every manifest row & both sides (abort before any write on failure).
      3. Read target md5 and write a verified named backup copy.
      4. Apply mapped image objects to a copy of the target records and write output_path.
      5. Run builder image sanitize audit, pii_gate_validator, and P10 on output_path.
      6. Read back output_path md5 and sha256.
    """
    if not expected_sha256 and not expected_sha8:
        raise ValueError("Must provide expected_sha256 or expected_sha8 to verify manifest")
    if str(output_path).lower().startswith("gs://") or str(target_path).lower().startswith("gs://"):
        raise ValueError("Offline local script refuses gs:// URIs")

    # Step 1: Check manifest SHA BEFORE reading CSV rows.
    actual_sha256 = file_sha256(manifest_path)
    actual_sha8 = actual_sha256[:8]
    if expected_sha256 and actual_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"Manifest SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
    if expected_sha8 and actual_sha8.lower() != expected_sha8.lower():
        raise ValueError(
            f"Manifest SHA8 mismatch: expected {expected_sha8}, got {actual_sha8}"
        )

    # Step 2: Parse CSV and pre-validate ALL rows before touching any output file.
    with open(manifest_path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("Manifest contains zero rows")

    records, is_jsonl = _load_target_records(target_path)
    by_nac = {r.get("nac_code"): r for r in records if r.get("nac_code")}

    validated_plan: List[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]] = []
    validation_errors: List[str] = []

    for idx, row in enumerate(rows, start=1):
        nac = (row.get("nac1") or row.get("nac_code") or f"row#{idx}").strip()
        if nac not in by_nac:
            validation_errors.append(f"Row {idx} ({nac}): missing from target catalog")
            continue

        obv_target = (row.get("obverse_target_field") or "").strip()
        rev_target = (row.get("reverse_target_field") or "").strip()
        if obv_target not in ("primary_image", "type_image"):
            validation_errors.append(
                f"Row {idx} ({nac}) [obverse]: invalid target_field {obv_target!r}"
            )
            continue
        if rev_target != "extra_images[]":
            validation_errors.append(
                f"Row {idx} ({nac}) [reverse]: invalid target_field {rev_target!r}"
            )
            continue

        obv_obj = None
        rev_obj = None
        for side in ("obverse", "reverse"):
            try:
                built = build_side_image_object(row, side)
                if side == "obverse":
                    obv_obj = built
                else:
                    rev_obj = built
            except ValueError as exc:
                validation_errors.append(f"Row {idx} ({nac}) [{side}]: {exc}")

        if obv_obj is not None and rev_obj is not None:
            validated_plan.append((row, by_nac[nac], obv_obj, rev_obj))

    if validation_errors:
        preview = "\n  ".join(validation_errors[:25])
        raise ValueError(
            f"Validation failed for {len(validation_errors)} item(s); aborting before any write:\n  {preview}"
        )

    # Step 3: Read target md5 first and keep a verified named backup.
    pre_md5 = file_md5(target_path)
    out_abs = os.path.abspath(output_path)
    out_dir = os.path.dirname(out_abs)
    os.makedirs(out_dir, exist_ok=True)
    if not backup_path:
        base_name = os.path.basename(target_path)
        stem, ext = os.path.splitext(base_name)
        backup_path = os.path.join(out_dir, f"{stem}.backup.{pre_md5[:12]}{ext}")
    shutil.copyfile(target_path, backup_path)
    backup_md5 = file_md5(backup_path)
    if backup_md5 != pre_md5:
        raise RuntimeError(
            f"Backup md5 verification failed: target={pre_md5} backup={backup_md5}"
        )

    # Step 4: Apply validated objects in memory and write output.
    updated_records = json.loads(json.dumps(records, ensure_ascii=False))
    updated_by_nac = {r.get("nac_code"): r for r in updated_records if r.get("nac_code")}
    primary_count = 0
    type_count = 0
    extra_replace_count = 0

    for row, _orig_entry, obv_obj, rev_obj in validated_plan:
        nac = row["nac1"].strip()
        target_entry = updated_by_nac[nac]
        obv_target = row["obverse_target_field"].strip()
        if obv_target == "primary_image":
            target_entry["primary_image"] = obv_obj
            primary_count += 1
        elif obv_target == "type_image":
            target_entry["type_image"] = obv_obj
            # Ensure primary_image does not mask type_image when primary is not unique.
            target_entry["primary_image"] = None
            type_count += 1

        extra_action = (row.get("extra_images_action") or "").strip()
        if extra_action.startswith("replace"):
            target_entry["extra_images"] = [rev_obj]
            extra_replace_count += 1
        else:
            existing = list(target_entry.get("extra_images") or [])
            preserved = [
                e for e in existing
                if isinstance(e, dict) and str(e.get("side") or "").lower() != "reverse"
            ]
            preserved.append(rev_obj)
            target_entry["extra_images"] = preserved

    _write_records(output_path, updated_records, is_jsonl)

    # Step 5: Post-write sanitize audit, pii_gate, and P10 on written output.
    disk_records, _ = _load_target_records(output_path)
    dropped = audit_catalog_images(disk_records)
    if dropped:
        os.remove(output_path)
        raise RuntimeError(
            f"Post-write builder sanitize dropped {len(dropped)} image(s): {dropped[:5]}"
        )

    leaks = scan_document_for_leaks(disk_records)
    if leaks:
        os.remove(output_path)
        raise RuntimeError(
            f"Post-write pii_gate failed with {len(leaks)} leak(s): {leaks[:5]}"
        )

    p10_hits = scan_rendered_captions_p10(disk_records)
    if p10_hits:
        os.remove(output_path)
        raise RuntimeError(
            f"Post-write P10 scan failed with {len(p10_hits)} hit(s): {p10_hits[:5]}"
        )

    # Step 6: Read back output md5.
    output_md5 = file_md5(output_path)
    output_sha256 = file_sha256(output_path)

    return {
        "manifest_sha256": actual_sha256,
        "manifest_sha8": actual_sha8,
        "rows_applied": len(validated_plan),
        "primary_image_writes": primary_count,
        "type_image_writes": type_count,
        "extra_images_replaces": extra_replace_count,
        "target_pre_md5": pre_md5,
        "backup_path": backup_path,
        "backup_md5": backup_md5,
        "output_path": output_path,
        "output_md5": output_md5,
        "output_sha256": output_sha256,
        "sanitize_dropped": 0,
        "pii_gate_leaks": 0,
        "p10_hits": 0,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline CR3 catalog image-attach writer (local copy only)."
    )
    parser.add_argument("--manifest", required=True, help="Path to attach_manifest CSV")
    parser.add_argument("--target", required=True, help="Path to local target catalog JSON/JSONL")
    parser.add_argument("--output", required=True, help="Path to write attached copy")
    parser.add_argument("--expected-sha256", default=None, help="Expected full SHA-256 of manifest")
    parser.add_argument("--expected-sha8", default=None, help="Expected 8-char SHA prefix of manifest")
    parser.add_argument("--backup", default=None, help="Optional named backup path")
    args = parser.parse_args(argv)

    report = apply_image_attach(
        manifest_path=args.manifest,
        target_path=args.target,
        output_path=args.output,
        expected_sha256=args.expected_sha256,
        expected_sha8=args.expected_sha8,
        backup_path=args.backup,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
