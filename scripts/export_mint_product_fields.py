#!/usr/bin/env python3
"""Offline local-file-in / local-file-out exporter for NET-810 U.S. Mint overlay.

Zero network calls. Reads data/usmint/usmint_product_schedule_2024.json (when acquired)
and emits numista_mobile/assets/catalog/mint_product_fields_v1.json.
Per MF-3 / AC-11: omits any entry lacking source_url + retrieved_at provenance,
and leaves the overlay as {} until the official schedule file is present.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "data" / "usmint" / "usmint_product_schedule_2024.json"
DEFAULT_OUTPUT = (
    REPO_ROOT / "numista_mobile" / "assets" / "catalog" / "mint_product_fields_v1.json"
)

ALLOWED_FIELDS = (
    "product_price_usd",
    "mint_schedule_status",
    "product_availability",
    "release_date",
    "release_time_et",
    "mint_product_as_of",
    "source_url",
    "retrieved_at",
)

FORBIDDEN_PRIVATE_KEYS = {
    "Purchase Cost", "purchaseCost",
    "Purchase Date", "purchaseDate",
    "Retailer/Website", "retailer",
    "Retailer Item No.", "retailerItemNo",
    "Retailer Invoice #", "retailerInvoiceNo",
    "Storage Location", "storageLocation",
    "Personal Notes I", "personalNotes",
    "Personal Reference #", "personalRef",
    "owner_photos", "ownerPhotos",
    "provenanceLedger",
    "transferStatus", "transferId",
}


def export_overlay(input_path: Path, output_path: Path) -> dict[str, dict[str, Any]]:
    if not input_path.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("{}\n", encoding="utf-8")
        return {}

    raw = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected JSON object keyed by nac_code in {input_path}")

    out: dict[str, dict[str, Any]] = {}
    for nac_code, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        for k in entry:
            if k in FORBIDDEN_PRIVATE_KEYS:
                raise ValueError(f"Forbidden private key {k!r} in {nac_code}")
        source_url = str(entry.get("source_url") or "").strip()
        retrieved_at = str(entry.get("retrieved_at") or "").strip()
        if not source_url or not retrieved_at:
            continue
        cleaned = {k: entry[k] for k in ALLOWED_FIELDS if k in entry and entry[k] is not None}
        cleaned["source_url"] = source_url
        cleaned["retrieved_at"] = retrieved_at
        out[str(nac_code).strip().upper()] = cleaned

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    in_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUT
    out_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUTPUT
    result = export_overlay(in_path, out_path)
    print(f"Exported {len(result)} provenance-verified overlay entries to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
