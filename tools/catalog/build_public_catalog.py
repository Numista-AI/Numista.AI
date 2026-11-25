#!/usr/bin/env python3
"""
tools/catalog/build_public_catalog.py
Sanitizes canonical deep-stripped catalog master JSONL into public catalog JSON.

Wave 2 v2.1 hardening (Plan cc9d2916):
- Strict scalar enforcement (_ensure_scalar, closes CR d2-3 / MF-1).
- Fail-closed filter dropping held_from_live rows AND held_from_live / visibility=internal varieties
  (e.g., 1875-S/S repunched mint mark never emits publicly).
- Rewrites "Collector reference" labels to "Numismatic reference (standard trade specification)"
  (closes MF-5 without loosening pii_gate_validator.py).
- Exports sanitized `search_aliases` (keywords only) and `nac_aliases` (retired codes only).
- Supports Sets / OGP Packaging / Privy Detail Vision UI (`packaging_images[]`, `set_members[]`, `role`).
- Enforces 31 CFR § 411.1 / 18 U.S.C. §§ 475, 504 on AI banknote images (one-sided obverse only,
  `allow_marketing_use: false`) and mandatory AI disclosure captions.
- Scrubs "Used with permission" / "courtesy" captions to "Image: United States Mint".
- Minifies JSON by default (separators=(",", ":")) with 8 MB warning / 10 MB split guard.
- Zero GSIDs, zero Greysheet URLs, zero internal keys.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

try:
    from tools.catalog.image_license_allowlist import is_certified_license
except ImportError:
    try:
        from image_license_allowlist import is_certified_license
    except ImportError:
        _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        if _THIS_DIR not in sys.path:
            sys.path.insert(0, _THIS_DIR)
        from image_license_allowlist import is_certified_license

DEFAULT_INPUT_PATH = os.path.join(
    r"1 NUMISTA.AI", "Grok CoS to Antigravity", "INBOX", "NET-747_inputs", "entries_master_20261103.jsonl"
)
DEFAULT_OUTPUT_PATH = os.path.join(
    "numista_mobile", "assets", "catalog", "catalog_public_v1.json"
)

BOUND_12 = {
    "NAC1.CN.US.1C.THEWORLDWA.1942.S.BASE.1": {
        "name": "1942-S Lincoln cent (World War II issue)",
        "series": "Lincoln Cent",
    },
    "NAC1.CN.US.50C.THEWORLDWA.1942.S.BASE.K": {
        "name": "1942-S Walking Liberty half dollar (World War II issue)",
        "series": "Walking Liberty Half Dollar",
    },
    "NAC1.CN.US.25C.THEWORLDWA.1942.S.BASE.H": {
        "name": "1942-S Washington quarter (World War II issue)",
        "series": "Washington Quarter",
    },
    "NAC1.CN.US.5C.THEUSNICKE.1975.XX.BASE.2": {
        "name": "1975 Jefferson nickel",
        "series": "Jefferson Nickel",
    },
    "NAC1.CN.US.5C.THEUSNICKE.1993.XX.BASE.J": {
        "name": "1993 Jefferson nickel",
        "series": "Jefferson Nickel",
    },
    "NAC1.CN.US.5C.THEUSNICKE.1998.XX.BASE.T": {
        "name": "1998 Jefferson nickel",
        "series": "Jefferson Nickel",
    },
    "NAC1.CN.US.1D.MODERNMORG.2023.XX.BASE.S": {
        "name": "2023 Morgan & Peace Silver Dollars",
        "series": "Modern Commemorative Dollars",
    },
    "NAC1.CN.US.1D.MODERNMORG.2023.XX.MORGANDOLL.Q": {
        "name": "2023 Morgan Silver Dollar",
        "series": "Modern Commemorative Dollars",
    },
    "NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACE.B": {
        "name": "2023 Peace Silver Dollar",
        "series": "Modern Commemorative Dollars",
    },
    "NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACESILVE.0": {
        "name": "2023 Peace Silver Dollar (Specimen)",
        "series": "Modern Commemorative Dollars",
    },
    "NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACEDOLLA.Y": {
        "name": "2023 Peace Silver Dollar",
        "series": "Modern Commemorative Dollars",
    },
    "NAC1.CN.US.25C.CELEBRATIN.2024.XX.DRMARYEDWA.6": {
        "name": "2024 American Women quarter (Dr. Mary Edwards Walker)",
        "series": "American Women Quarters",
    },
}

FORBIDDEN_PATH_SUBSTRINGS = ["seed_images/", "/workspace", "gs://", "users/", "googleapis"]

# Approved public GCS buckets (matches Dart catalog_image_guard.dart):
#   1. us_mint_coin_images
#   2. numista-reference-library
#   3. numista-uploads-studio-9101802118-8c9a8/reference/... (promoted reference path only)
APPROVED_GCS_BUCKETS = frozenset({
    "us_mint_coin_images",
    "numista-reference-library",
})
PROMOTED_UPLOADS_BUCKET = "numista-uploads-studio-9101802118-8c9a8"

IMAGE_URL_KEYS = ("url", "full_url", "thumb_url")

ALLOWED_IMAGE_ROLES = frozenset({
    "packaging",
    "packaging_alt",
    "set_contents",
    "privy_detail",
    "set_member",
    "primary",
    "secondary",
    "extra",
})

PRIMARY_IMAGE_KEYS = [
    "url",
    "full_url",
    "thumb_url",
    "file",
    "side",
    "role",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
    "note",
    "resolution",
    "ai_generated",
    "allow_marketing_use",
]
TYPE_IMAGE_KEYS = [
    "url",
    "full_url",
    "thumb_url",
    "file",
    "side",
    "role",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
    "note",
    "resolution",
    "ai_generated",
    "allow_marketing_use",
]
SECONDARY_IMAGE_KEYS = [
    "url",
    "full_url",
    "file",
    "side",
    "role",
    "resolution",
    "license",
    "credit",
    "source",
    "source_url",
    "note",
    "unique_side",
    "ai_generated",
    "allow_marketing_use",
]
EXTRA_IMAGE_KEYS = [
    "url",
    "full_url",
    "thumb_url",
    "side",
    "role",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
    "note",
    "resolution",
    "ai_generated",
    "allow_marketing_use",
]
PACKAGING_IMAGE_KEYS = EXTRA_IMAGE_KEYS

WARN_SIZE_BYTES = 8 * 1024 * 1024
SPLIT_THRESHOLD_BYTES = 10 * 1024 * 1024
SPLIT_THRESHOLD_ROWS = 10000

_FORBIDDEN_GREYSHEET_RE = re.compile(
    r"greysheet\.com|greysheet_gsid|\bgsid\b|cdnexchange",
    re.IGNORECASE,
)
_COLLECTOR_REF_RE = re.compile(r"\bCollector reference\b", re.IGNORECASE)
_MINT_PERMISSION_RE = re.compile(
    r"(?:used with permission|courtesy of(?: the)?\s+u\.?s\.?\s*mint|courtesy\s+u\.?s\.?\s*mint)",
    re.IGNORECASE,
)


def _ensure_scalar(val: Any, field_name: str) -> Any:
    """
    Closes CR finding d2-3 / MF-1: rejects dicts or lists accidentally nested in scalar fields.
    Permits None, str, int, float, bool only.
    """
    if val is None or isinstance(val, (str, int, float, bool)):
        return val
    raise ValueError(
        f"Non-scalar value ({type(val).__name__}) rejected in scalar field '{field_name}'"
    )


def _rewrite_public_text(val: Any) -> Any:
    """Applies MF-5 ('Collector reference') and credit-line ('Used with permission') rewrites."""
    if not isinstance(val, str):
        return val
    out = _COLLECTOR_REF_RE.sub("Numismatic reference (standard trade specification)", val)
    if _MINT_PERMISSION_RE.search(out):
        out = "Image: United States Mint"
    return out


def _has_raw_dot_segment(url: str) -> bool:
    path_part = url.split("?", 1)[0].split("#", 1)[0]
    return any(seg in (".", "..") for seg in path_part.split("/"))


def is_approved_image_url(raw_url: Any, *, allow_promoted_uploads: bool = False) -> bool:
    """Strict allow-list check matching Dart isApprovedCatalogImageUrl."""
    if not isinstance(raw_url, str):
        return False
    url = raw_url.strip()
    if not url:
        return False
    if "\\" in url or "?" in url or "#" in url:
        return False
    if _has_raw_dot_segment(url):
        return False
    lower = url.lower()
    if (
        "%2e" in lower
        or "%2f" in lower
        or "%5c" in lower
        or "%3f" in lower
        or "%23" in lower
    ):
        return False

    if url.startswith("assets/catalog/images/"):
        segs = url.split("/")
        return len(segs) >= 4 and not any(s in ("", ".", "..") for s in segs)

    if any(ch.isspace() for ch in url):
        return False
    parsed = urlsplit(url)
    if parsed.scheme != "https":
        return False
    if (
        parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or "@" in parsed.netloc
        or ":" in parsed.netloc
    ):
        return False
    if parsed.netloc.lower() != "storage.googleapis.com":
        return False
    if (parsed.hostname or "").lower() != "storage.googleapis.com":
        return False
    if parsed.query or parsed.fragment:
        return False
    if not parsed.path.startswith("/") or parsed.path.startswith("//"):
        return False

    segs = parsed.path[1:].split("/")
    if len(segs) < 2 or any(s in ("", ".", "..") for s in segs):
        return False
    if segs[0] in APPROVED_GCS_BUCKETS:
        return True
    if allow_promoted_uploads and segs[0] == PROMOTED_UPLOADS_BUCKET:
        return len(segs) >= 3 and segs[1] == "reference"
    return False


def _is_gcs_hosted_value(val: Any) -> bool:
    if not isinstance(val, str):
        return False
    lower = val.lower()
    return (
        "storage.googleapis.com" in lower
        or "firebasestorage.googleapis.com" in lower
        or "googleapis.com" in lower
        or "gs://" in lower
    )


def sanitize_image_path(val: Any) -> Any:
    if not val or not isinstance(val, str):
        return val
    if val.startswith("http://") or val.startswith("https://"):
        return val
    for sub in FORBIDDEN_PATH_SUBSTRINGS:
        if sub in val:
            base = os.path.basename(val)
            return f"reference_images/{base}" if base else None
    return val


def sanitize_image_dict(
    img_dict: Any,
    allowed_keys: List[str],
    *,
    nac_code: Optional[str] = None,
    field_name: Optional[str] = None,
    item_type: Optional[str] = None,
    dropped_report: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    if not img_dict or not isinstance(img_dict, dict):
        return None

    is_ai = img_dict.get("ai_generated") is True
    is_note = (str(item_type or "").lower() == "note") or str(nac_code or "").startswith("NAC1.BN.")

    # 31 CFR § 411.1 / Wave 2 Component F: AI banknote images MUST be one-sided obverse ONLY.
    if is_ai and is_note:
        side = str(img_dict.get("side") or "").strip().lower()
        if side != "obverse":
            if dropped_report is not None:
                dropped_report.append({
                    "nac_code": nac_code,
                    "field": field_name,
                    "key": "side",
                    "reason": "cfr_411_ai_banknote_non_obverse_rejected",
                })
            return None

    # Fail-closed GCS URL & certified-license gate (D1, D2, D3, N1)
    has_gcs_url = False
    for uk in IMAGE_URL_KEYS:
        if uk not in img_dict:
            continue
        raw_val = img_dict[uk]
        if raw_val is None or raw_val == "":
            continue
        if _is_gcs_hosted_value(raw_val):
            has_gcs_url = True
            if not is_approved_image_url(raw_val):
                if dropped_report is not None:
                    dropped_report.append({
                        "nac_code": nac_code,
                        "field": field_name,
                        "key": uk,
                        "reason": "unapproved_gcs_url",
                    })
                return None

    if has_gcs_url and not is_ai and not is_certified_license(img_dict.get("license")):
        if dropped_report is not None:
            dropped_report.append({
                "nac_code": nac_code,
                "field": field_name,
                "key": "license",
                "reason": "uncertified_or_missing_license",
            })
        return None

    out: Dict[str, Any] = {}
    for k in allowed_keys:
        if k in img_dict:
            v = _ensure_scalar(img_dict[k], f"{field_name}.{k}")
            if k == "role" and v is not None:
                if str(v) not in ALLOWED_IMAGE_ROLES:
                    continue
            if k in ("source", "credit") and v == "collection photo, owner removed":
                v = "Numista.Ai reference photo"
            elif k in ("source", "credit", "note") and isinstance(v, str):
                v = _rewrite_public_text(v)
            elif k in ("url", "full_url", "thumb_url", "file"):
                v = sanitize_image_path(v)
            out[k] = v

    if is_ai and is_note:
        # 18 U.S.C. § 475: AI banknotes are strictly excluded from ads/marketing.
        out["allow_marketing_use"] = False
        out["ai_generated"] = True

    return out if out else None


def sanitize_set_members(
    raw_members: Any,
    *,
    nac_code: Optional[str] = None,
    dropped_report: Optional[List[Dict[str, Any]]] = None,
) -> Optional[List[Dict[str, Any]]]:
    """Allow-list sanitizer for set_members[] (Eric Images Vision Statement / sets_packaging_privy.md)."""
    if not isinstance(raw_members, list) or not raw_members:
        return None
    cleaned_members: List[Dict[str, Any]] = []
    for idx, mem in enumerate(raw_members):
        if not isinstance(mem, dict):
            continue
        cm: Dict[str, Any] = {}
        for sk in ("position", "label", "mint", "denomination", "member_nac1", "default_side"):
            if sk in mem:
                cm[sk] = _rewrite_public_text(_ensure_scalar(mem[sk], f"set_members[{idx}].{sk}"))
        for side_key in ("obverse", "reverse"):
            side_obj = mem.get(side_key)
            if isinstance(side_obj, dict):
                raw_img = side_obj.get("image") if isinstance(side_obj.get("image"), dict) else side_obj
                sanitized_side = sanitize_image_dict(
                    raw_img,
                    EXTRA_IMAGE_KEYS,
                    nac_code=nac_code,
                    field_name=f"set_members[{idx}].{side_key}",
                    item_type="coin",
                    dropped_report=dropped_report,
                )
                if sanitized_side:
                    cm[side_key] = sanitized_side
        if cm:
            cleaned_members.append(cm)
    return cleaned_members if cleaned_members else None


def audit_catalog_images(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validates all image objects across catalog records and returns dropped entries."""
    dropped: List[Dict[str, Any]] = []
    field_specs = (
        ("primary_image", PRIMARY_IMAGE_KEYS),
        ("type_image", TYPE_IMAGE_KEYS),
        ("secondary_image", SECONDARY_IMAGE_KEYS),
    )
    for row in records:
        nac_code = row.get("nac_code")
        item_type = row.get("type")
        for field_name, keys in field_specs:
            val = row.get(field_name)
            if isinstance(val, dict):
                sanitize_image_dict(
                    val,
                    keys,
                    nac_code=nac_code,
                    field_name=field_name,
                    item_type=item_type,
                    dropped_report=dropped,
                )
        for list_field, keys in (("extra_images", EXTRA_IMAGE_KEYS), ("packaging_images", PACKAGING_IMAGE_KEYS)):
            for idx, extra in enumerate(row.get(list_field) or []):
                if isinstance(extra, dict):
                    sanitize_image_dict(
                        extra,
                        keys,
                        nac_code=nac_code,
                        field_name=f"{list_field}[{idx}]",
                        item_type=item_type,
                        dropped_report=dropped,
                    )
        if row.get("set_members"):
            sanitize_set_members(row.get("set_members"), nac_code=nac_code, dropped_report=dropped)
    return dropped


def _clean_string_list(val: Any, field_name: str) -> Optional[List[str]]:
    if not isinstance(val, list) or not val:
        return None
    out: List[str] = []
    seen = set()
    for item in val:
        s = _ensure_scalar(item, field_name)
        if isinstance(s, str):
            trimmed = s.strip()
            if trimmed and trimmed not in seen:
                seen.add(trimmed)
                out.append(trimmed)
    return out if out else None


def _write_split_index(records: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
    """Emits lightweight search index + lazy per-era detail chunks when payload exceeds 10 MB / 10k rows."""
    out_dir = os.path.dirname(os.path.abspath(output_path))
    chunks_dir = os.path.join(out_dir, "chunks")
    os.makedirs(chunks_dir, exist_ok=True)
    index_records = []
    by_era: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        era_slug = re.sub(r"[^a-z0-9]+", "_", str(r.get("era") or "undated").lower()).strip("_") or "undated"
        by_era.setdefault(era_slug, []).append(r)
        prim = r.get("primary_image") or r.get("type_image") or {}
        index_records.append({
            "nac_code": r.get("nac_code"),
            "nac_aliases": r.get("nac_aliases"),
            "search_aliases": r.get("search_aliases"),
            "name": r.get("name"),
            "type": r.get("type"),
            "year": r.get("year"),
            "denomination": r.get("denomination"),
            "series": r.get("series"),
            "era": r.get("era"),
            "status_badge": r.get("status_badge"),
            "thumb_url": prim.get("thumb_url") or prim.get("url") if isinstance(prim, dict) else None,
            "chunk": f"chunks/era_{era_slug}.json",
        })
    index_path = os.path.join(out_dir, "catalog_search_index_v1.json")
    with open(index_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index_records, f, separators=(",", ":"), ensure_ascii=False)
    for slug, chunk_rows in by_era.items():
        with open(os.path.join(chunks_dir, f"era_{slug}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(chunk_rows, f, separators=(",", ":"), ensure_ascii=False)
    return {"index_path": index_path, "chunks": len(by_era)}


def build_public_catalog(
    input_path: str,
    output_path: str,
    *,
    pretty: bool = False,
    strict_legacy_counts: bool = False,
    emit_split_index: bool = False,
) -> int:
    print(f"Reading master entries from: {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    records: List[Dict[str, Any]] = []
    dropped_images: List[Dict[str, Any]] = []
    held_rows_dropped = 0
    held_varieties_dropped = 0
    album_renames_count = 0
    source_rewrites_count = 0
    composition_scrub_count = 0
    seen_nacs = set()

    with open(input_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)

            # Fail-closed held/internal row filter (MF-1)
            if row.get("held_from_live") is True or row.get("visibility") == "internal":
                held_rows_dropped += 1
                continue

            nac_code = _ensure_scalar(row.get("nac_code"), "nac_code")
            if not isinstance(nac_code, str) or not nac_code.strip():
                raise ValueError(f"Line {line_num}: missing or invalid nac_code")
            if nac_code in seen_nacs:
                raise ValueError(f"Duplicate nac_code detected: {nac_code}")
            seen_nacs.add(nac_code)

            item_type = _ensure_scalar(row.get("type"), "type")

            # 1. BOUND_12 Normalization
            name = _ensure_scalar(row.get("name"), "name")
            series = _ensure_scalar(row.get("series"), "series")
            if nac_code in BOUND_12:
                name = BOUND_12[nac_code]["name"]
                series = BOUND_12[nac_code]["series"]
                album_renames_count += 1

            # 2. History prose scrub (Section 3.2-6 + MF-5)
            history = _ensure_scalar(row.get("history"), "history")
            if nac_code == "NAC1.CN.US.20DOLLARS.COINS.1849.P.BASE.S" and isinstance(history, str):
                history = history.replace("This large collection includes", "This large holding includes")
            history = _rewrite_public_text(history)

            # 3. Images sanitization
            primary_image = sanitize_image_dict(
                row.get("primary_image"),
                PRIMARY_IMAGE_KEYS,
                nac_code=nac_code,
                field_name="primary_image",
                item_type=item_type,
                dropped_report=dropped_images,
            )
            if isinstance(row.get("primary_image"), dict) and row["primary_image"].get("source") == "collection photo, owner removed":
                source_rewrites_count += 1

            type_image = sanitize_image_dict(
                row.get("type_image"),
                TYPE_IMAGE_KEYS,
                nac_code=nac_code,
                field_name="type_image",
                item_type=item_type,
                dropped_report=dropped_images,
            )
            if isinstance(row.get("type_image"), dict) and row["type_image"].get("source") == "collection photo, owner removed":
                source_rewrites_count += 1

            secondary_image = sanitize_image_dict(
                row.get("secondary_image"),
                SECONDARY_IMAGE_KEYS,
                nac_code=nac_code,
                field_name="secondary_image",
                item_type=item_type,
                dropped_report=dropped_images,
            )
            if isinstance(row.get("secondary_image"), dict) and row["secondary_image"].get("source") == "collection photo, owner removed":
                source_rewrites_count += 1

            extra_images = []
            for idx, e in enumerate(row.get("extra_images") or []):
                cleaned_e = sanitize_image_dict(
                    e,
                    EXTRA_IMAGE_KEYS,
                    nac_code=nac_code,
                    field_name=f"extra_images[{idx}]",
                    item_type=item_type,
                    dropped_report=dropped_images,
                )
                if cleaned_e:
                    extra_images.append(cleaned_e)

            packaging_images = []
            for idx, pimg in enumerate(row.get("packaging_images") or []):
                cleaned_p = sanitize_image_dict(
                    pimg,
                    PACKAGING_IMAGE_KEYS,
                    nac_code=nac_code,
                    field_name=f"packaging_images[{idx}]",
                    item_type=item_type,
                    dropped_report=dropped_images,
                )
                if cleaned_p:
                    packaging_images.append(cleaned_p)

            set_members = sanitize_set_members(
                row.get("set_members"),
                nac_code=nac_code,
                dropped_report=dropped_images,
            )

            # 4. Varieties: fail-closed drop held_from_live or visibility=internal (closes MF-1 1875-S/S leak)
            varieties = []
            for v in (row.get("varieties") or []):
                if not isinstance(v, dict):
                    continue
                if v.get("held_from_live") is True or v.get("visibility") == "internal":
                    held_varieties_dropped += 1
                    continue
                cleaned_v = {}
                for k in ("name", "attribution", "reference_work"):
                    if k in v:
                        cleaned_v[k] = _rewrite_public_text(_ensure_scalar(v[k], f"varieties.{k}"))
                if cleaned_v:
                    varieties.append(cleaned_v)

            # 5. Sources: [{label, url, title}], drop collection-derived & dropped CoinWeek Jacobson URL
            sources = []
            for s in (row.get("sources") or []):
                if not isinstance(s, dict):
                    continue
                stype = str(s.get("type") or "")
                slabel = str(s.get("label") or "")
                surl = str(s.get("url") or "")
                if stype == "collection-derived" or "collection-derived" in slabel:
                    continue
                if "harvey-b-jacobson-jr-collection" in surl:
                    continue
                cleaned_s = {}
                for k in ("label", "url", "title"):
                    if k in s and s[k] is not None:
                        val = _ensure_scalar(s[k], f"sources.{k}")
                        cleaned_s[k] = _rewrite_public_text(val) if k in ("label", "title") else val
                if cleaned_s:
                    sources.append(cleaned_s)

            # 6. Mintage: {value, label, source_url} (strictly scalar-validated)
            mintage = None
            if row.get("mintage") and isinstance(row["mintage"], dict):
                m = row["mintage"]
                mintage = {
                    "value": _ensure_scalar(m.get("value"), "mintage.value"),
                    "label": _rewrite_public_text(_ensure_scalar(m.get("label"), "mintage.label")),
                    "source_url": _ensure_scalar(m.get("source_url"), "mintage.source_url"),
                }

            # 7. Figures: {mintage, weight_g, diameter_mm, fineness, composition} (strictly scalar-validated)
            figures = None
            if row.get("figures") and isinstance(row["figures"], dict):
                fig_in = row["figures"]
                figures = {}
                for metric in ("mintage", "weight_g", "diameter_mm", "fineness", "composition"):
                    if metric in fig_in and isinstance(fig_in[metric], dict):
                        m_obj = fig_in[metric]
                        val = _ensure_scalar(m_obj.get("value"), f"figures.{metric}.value")
                        unit = _ensure_scalar(m_obj.get("unit"), f"figures.{metric}.unit")
                        lbl = _ensure_scalar(m_obj.get("label"), f"figures.{metric}.label")
                        src_url = _ensure_scalar(m_obj.get("source_url"), f"figures.{metric}.source_url")
                        if metric == "composition":
                            if m_obj.get("status") == "COLLECTION_DERIVED" or (
                                isinstance(lbl, str) and "collection-derived" in lbl
                            ):
                                composition_scrub_count += 1
                                lbl = "Needs source"
                        figures[metric] = {
                            "value": val,
                            "unit": unit,
                            "label": _rewrite_public_text(lbl),
                            "source_url": src_url,
                        }

            # 8. Derived Public Fields (C1 strict Pre-Federal)
            is_pre_federal = row.get("pre_federal") is True
            is_placeholder = row.get("display_label") == "details coming"
            is_interleaved = row.get("fold_source") == "seed_images"

            comp_needs_src = False
            if figures and figures.get("composition"):
                if figures["composition"].get("label") == "Needs source":
                    comp_needs_src = True
            mint_needs_src = bool(mintage and mintage.get("label") == "Needs source")

            if is_pre_federal:
                status_badge = "Pre-Federal"
            elif is_placeholder:
                status_badge = "Details coming"
            elif comp_needs_src or mint_needs_src:
                status_badge = "Needs source"
            else:
                status_badge = None

            # 9. Aliases (nac_aliases for retired NAC redirects; search_aliases for colloquial search keywords)
            nac_aliases = _clean_string_list(row.get("nac_aliases"), "nac_aliases")
            search_aliases = _clean_string_list(row.get("search_aliases"), "search_aliases")

            social_posts = row.get("social_posts")

            rec = {
                "nac_code": nac_code,
                "nac_aliases": nac_aliases,
                "search_aliases": search_aliases,
                "name": name,
                "type": item_type,
                "year": _ensure_scalar(row.get("year"), "year"),
                "denomination": _ensure_scalar(row.get("denomination"), "denomination"),
                "series": series,
                "mint_facility": _ensure_scalar(row.get("mint_facility"), "mint_facility"),
                "mint_mark_on_coin": _ensure_scalar(row.get("mint_mark_on_coin"), "mint_mark_on_coin"),
                "composition": _ensure_scalar(row.get("composition"), "composition"),
                "era": _ensure_scalar(row.get("era"), "era"),
                "designer": _ensure_scalar(row.get("designer"), "designer"),
                "weight_g": _ensure_scalar(row.get("weight_g"), "weight_g"),
                "diameter_mm": _ensure_scalar(row.get("diameter_mm"), "diameter_mm"),
                "history": history,
                "pre_federal": is_pre_federal,
                "pre_federal_state": _ensure_scalar(row.get("pre_federal_state"), "pre_federal_state"),
                "display_label": _ensure_scalar(row.get("display_label"), "display_label"),
                "note_size": _ensure_scalar(row.get("note_size"), "note_size"),
                "mintage": mintage,
                "figures": figures,
                "sources": sources,
                "primary_image": primary_image,
                "type_image": type_image,
                "secondary_image": secondary_image,
                "extra_images": extra_images if extra_images else None,
                "packaging_images": packaging_images if packaging_images else None,
                "set_members": set_members,
                "varieties": varieties if varieties else None,
                "social_posts": social_posts if social_posts else None,
                "status_badge": status_badge,
                "is_pre_federal": is_pre_federal,
                "is_placeholder": is_placeholder,
                "is_interleaved_checklist_only": is_interleaved,
            }
            records.append(rec)

    if strict_legacy_counts:
        assert len(records) == 3202, f"Expected 3202 records, got {len(records)}"
        assert album_renames_count == 12, f"Expected 12 album renames, got {album_renames_count}"
        assert source_rewrites_count == 1070, f"Expected 1070 source rewrites, got {source_rewrites_count}"
        assert composition_scrub_count == 1724, f"Expected 1724 composition scrubs, got {composition_scrub_count}"
        pre_fed_count = sum(1 for r in records if r["is_pre_federal"])
        assert pre_fed_count == 9, f"C1 violation: Expected exactly 9 Pre-Federal records, got {pre_fed_count}"
    else:
        assert len(records) > 0, "Builder produced zero public records"

    serialized = (
        json.dumps(records, indent=2, ensure_ascii=False)
        if pretty
        else json.dumps(records, separators=(",", ":"), ensure_ascii=False)
    )

    # Hard Greysheet / GSID fail-closed assertion on public output
    gs_match = _FORBIDDEN_GREYSHEET_RE.search(serialized)
    if gs_match:
        raise RuntimeError(f"Greysheet/GSID leak detected in public catalog build: {gs_match.group(0)!r}")

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(serialized)

    out_bytes = len(serialized.encode("utf-8"))
    pre_fed_count = sum(1 for r in records if r["is_pre_federal"])
    print(f"Successfully generated {len(records)} sanitized records ({out_bytes:,} bytes) to: {output_path}")
    print(
        f"Stats: Held rows dropped={held_rows_dropped}, Held varieties dropped={held_varieties_dropped}, "
        f"Album renames={album_renames_count}, Source rewrites={source_rewrites_count}, "
        f"Composition scrubs={composition_scrub_count}, Pre-Federal={pre_fed_count}, "
        f"Dropped images={len(dropped_images)}"
    )

    if out_bytes >= WARN_SIZE_BYTES:
        print(f"WARNING: Public catalog payload ({out_bytes:,} bytes) reached >= 8 MB watch threshold.")
    if emit_split_index or out_bytes > SPLIT_THRESHOLD_BYTES or len(records) > SPLIT_THRESHOLD_ROWS:
        split_info = _write_split_index(records, output_path)
        print(f"Scaling guard emitted split search index ({split_info['chunks']} era chunks): {split_info['index_path']}")

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build sanitized public catalog JSON (Wave 2 v2.1).")
    parser.add_argument("input_path", nargs="?", default=DEFAULT_INPUT_PATH)
    parser.add_argument("output_path", nargs="?", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON with indent=2")
    parser.add_argument("--strict-legacy-counts", action="store_true", help="Enforce legacy 3,202 snapshot counts")
    parser.add_argument("--split-index", action="store_true", help="Force emit split search index + era chunks")
    args = parser.parse_args(argv)
    return build_public_catalog(
        args.input_path,
        args.output_path,
        pretty=args.pretty,
        strict_legacy_counts=args.strict_legacy_counts,
        emit_split_index=args.split_index,
    )


if __name__ == "__main__":
    sys.exit(main())
