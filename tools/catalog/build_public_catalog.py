#!/usr/bin/env python3
"""
tools/catalog/build_public_catalog.py
Sanitizes entries_master_20261103.jsonl into public catalog JSON.
Strict allow-list, PII scrub, BOUND_12 normalization, and C1-C4 compliance.
"""

import json
import os
import re
import sys
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

APPROVED_GCS_BUCKETS = frozenset({
    "us_mint_coin_images",
    "numista-reference-library",
})

IMAGE_URL_KEYS = ("url", "full_url", "thumb_url")

PRIMARY_IMAGE_KEYS = [
    "url",
    "full_url",
    "thumb_url",
    "file",
    "side",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
    "resolution",
]
TYPE_IMAGE_KEYS = [
    "url",
    "full_url",
    "thumb_url",
    "file",
    "side",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
    "note",
    "resolution",
]
SECONDARY_IMAGE_KEYS = ["url", "file", "side", "resolution", "source", "unique_side"]
EXTRA_IMAGE_KEYS = [
    "url",
    "full_url",
    "thumb_url",
    "side",
    "unique_side",
    "license",
    "credit",
    "source",
    "source_url",
    "resolution",
]


def _has_raw_dot_segment(url):
    path_part = url.split("?", 1)[0].split("#", 1)[0]
    return any(seg in (".", "..") for seg in path_part.split("/"))


def is_approved_image_url(raw_url):
    """Strict allow-list check matching Dart isApprovedCatalogImageUrl, minus uploads-studio."""
    if not isinstance(raw_url, str):
        return False
    url = raw_url.strip()
    if not url:
        return False
    # Reject raw backslashes, query strings, fragments, and dot-segments before parsing.
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

    # Bundled local catalog assets stay accepted (no traversal or bare directory prefix).
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
    return segs[0] in APPROVED_GCS_BUCKETS


def _is_gcs_hosted_value(val):
    if not isinstance(val, str):
        return False
    lower = val.lower()
    return (
        "storage.googleapis.com" in lower
        or "firebasestorage.googleapis.com" in lower
        or "googleapis.com" in lower
        or "gs://" in lower
    )


def sanitize_image_path(val):
    if not val or not isinstance(val, str):
        return val
    # Public https museum URLs stay unchanged
    if val.startswith("http://") or val.startswith("https://"):
        return val
    for sub in FORBIDDEN_PATH_SUBSTRINGS:
        if sub in val:
            base = os.path.basename(val)
            return f"reference_images/{base}" if base else None
    return val


def sanitize_image_dict(
    img_dict,
    allowed_keys,
    *,
    nac_code=None,
    field_name=None,
    dropped_report=None,
):
    if not img_dict or not isinstance(img_dict, dict):
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

    if has_gcs_url and not is_certified_license(img_dict.get("license")):
        if dropped_report is not None:
            dropped_report.append({
                "nac_code": nac_code,
                "field": field_name,
                "key": "license",
                "reason": "uncertified_or_missing_license",
            })
        return None

    out = {}
    for k in allowed_keys:
        if k in img_dict:
            v = img_dict[k]
            if k == "source" and v == "collection photo, owner removed":
                v = "Numista.Ai reference photo"
            elif k in ("url", "full_url", "thumb_url", "file"):
                v = sanitize_image_path(v)
            out[k] = v
    return out if out else None


def audit_catalog_images(records):
    """Validates all image objects across catalog records and returns dropped entries."""
    dropped = []
    field_specs = (
        ("primary_image", PRIMARY_IMAGE_KEYS),
        ("type_image", TYPE_IMAGE_KEYS),
        ("secondary_image", SECONDARY_IMAGE_KEYS),
    )
    for row in records:
        nac_code = row.get("nac_code")
        for field_name, keys in field_specs:
            val = row.get(field_name)
            if isinstance(val, dict):
                sanitize_image_dict(
                    val,
                    keys,
                    nac_code=nac_code,
                    field_name=field_name,
                    dropped_report=dropped,
                )
        for idx, extra in enumerate(row.get("extra_images") or []):
            if isinstance(extra, dict):
                sanitize_image_dict(
                    extra,
                    EXTRA_IMAGE_KEYS,
                    nac_code=nac_code,
                    field_name=f"extra_images[{idx}]",
                    dropped_report=dropped,
                )
    return dropped

def build_public_catalog(input_path, output_path):
    print(f"Reading master entries from: {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    records = []
    dropped_images = []
    album_renames_count = 0
    source_rewrites_count = 0
    composition_scrub_count = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            nac_code = row.get("nac_code")

            # 1. BOUND_12 Normalization
            name = row.get("name")
            series = row.get("series")
            if nac_code in BOUND_12:
                name = BOUND_12[nac_code]["name"]
                series = BOUND_12[nac_code]["series"]
                album_renames_count += 1

            # 2. History prose scrub (Section 3.2-6)
            history = row.get("history")
            if nac_code == "NAC1.CN.US.20DOLLARS.COINS.1849.P.BASE.S" and history:
                history = history.replace("This large collection includes", "This large holding includes")

            # 3. Images sanitization
            # primary_image keys: url, full_url, thumb_url, file, side, unique_side, license, credit, source, source_url, resolution
            primary_keys = PRIMARY_IMAGE_KEYS
            primary_image = sanitize_image_dict(
                row.get("primary_image"),
                primary_keys,
                nac_code=nac_code,
                field_name="primary_image",
                dropped_report=dropped_images,
            )
            if row.get("primary_image") and row.get("primary_image", {}).get("source") == "collection photo, owner removed":
                source_rewrites_count += 1

            # type_image keys: url, full_url, thumb_url, file, side, unique_side, license, credit, source, source_url, note, resolution
            type_keys = TYPE_IMAGE_KEYS
            type_image = sanitize_image_dict(
                row.get("type_image"),
                type_keys,
                nac_code=nac_code,
                field_name="type_image",
                dropped_report=dropped_images,
            )
            if row.get("type_image") and row.get("type_image", {}).get("source") == "collection photo, owner removed":
                source_rewrites_count += 1

            # secondary_image keys: url, file, side, resolution, source, unique_side
            secondary_keys = SECONDARY_IMAGE_KEYS
            secondary_image = sanitize_image_dict(
                row.get("secondary_image"),
                secondary_keys,
                nac_code=nac_code,
                field_name="secondary_image",
                dropped_report=dropped_images,
            )
            if row.get("secondary_image") and row.get("secondary_image", {}).get("source") == "collection photo, owner removed":
                source_rewrites_count += 1

            # extra_images: [{url, full_url, thumb_url, side, unique_side, license, credit, source, source_url, resolution}]
            extra_keys = EXTRA_IMAGE_KEYS
            extra_images = []
            for idx, e in enumerate(row.get("extra_images") or []):
                cleaned_e = sanitize_image_dict(
                    e,
                    extra_keys,
                    nac_code=nac_code,
                    field_name=f"extra_images[{idx}]",
                    dropped_report=dropped_images,
                )
                if cleaned_e:
                    extra_images.append(cleaned_e)

            # 4. Varieties: [{name, attribution, reference_work}]
            varieties = []
            for v in (row.get("varieties") or []):
                cleaned_v = {}
                for k in ["name", "attribution", "reference_work"]:
                    if k in v:
                        cleaned_v[k] = v[k]
                if cleaned_v:
                    varieties.append(cleaned_v)

            # 5. Sources: [{label, url, title}], drop collection-derived & dropped CoinWeek Jacobson URL
            sources = []
            for s in (row.get("sources") or []):
                stype = s.get("type", "")
                slabel = s.get("label", "")
                surl = s.get("url", "")
                if stype == "collection-derived" or "collection-derived" in slabel:
                    continue
                if "harvey-b-jacobson-jr-collection" in surl:
                    continue
                cleaned_s = {}
                for k in ["label", "url", "title"]:
                    if k in s:
                        cleaned_s[k] = s[k]
                if cleaned_s:
                    sources.append(cleaned_s)

            # 6. Mintage: {value, label, source_url}
            mintage = None
            if row.get("mintage") and isinstance(row["mintage"], dict):
                m = row["mintage"]
                mintage = {
                    "value": m.get("value"),
                    "label": m.get("label"),
                    "source_url": m.get("source_url")
                }

            # 7. Figures: {mintage, weight_g, diameter_mm, fineness, composition}
            figures = None
            if row.get("figures") and isinstance(row["figures"], dict):
                fig_in = row["figures"]
                figures = {}
                for metric in ["mintage", "weight_g", "diameter_mm", "fineness", "composition"]:
                    if metric in fig_in and isinstance(fig_in[metric], dict):
                        m_obj = fig_in[metric]
                        val = m_obj.get("value")
                        unit = m_obj.get("unit")
                        lbl = m_obj.get("label")
                        src_url = m_obj.get("source_url")
                        if metric == "composition":
                            if m_obj.get("status") == "COLLECTION_DERIVED" or (lbl and "collection-derived" in lbl):
                                composition_scrub_count += 1
                                lbl = "Needs source"
                        figures[metric] = {
                            "value": val,
                            "unit": unit,
                            "label": lbl,
                            "source_url": src_url
                        }

            # 8. Derived Public Fields (C1 strict Pre-Federal)
            is_pre_federal = (row.get("pre_federal") is True)
            is_placeholder = (row.get("display_label") == "details coming")
            is_interleaved = (row.get("fold_source") == "seed_images")

            # Status badge priority: Pre-Federal > Details coming > Needs source
            comp_needs_src = False
            if figures and figures.get("composition"):
                if figures["composition"].get("label") == "Needs source":
                    comp_needs_src = True
            mint_needs_src = (mintage and mintage.get("label") == "Needs source")

            if is_pre_federal:
                status_badge = "Pre-Federal"
            elif is_placeholder:
                status_badge = "Details coming"
            elif comp_needs_src or mint_needs_src:
                status_badge = "Needs source"
            else:
                status_badge = None

            # Social posts
            social_posts = row.get("social_posts")

            # Assembled Record
            rec = {
                "nac_code": nac_code,
                "name": name,
                "type": row.get("type"),
                "year": row.get("year"),
                "denomination": row.get("denomination"),
                "series": series,
                "mint_facility": row.get("mint_facility"),
                "mint_mark_on_coin": row.get("mint_mark_on_coin"),
                "composition": row.get("composition"),
                "era": row.get("era"),
                "designer": row.get("designer"),
                "weight_g": row.get("weight_g"),
                "diameter_mm": row.get("diameter_mm"),
                "history": history,
                "pre_federal": row.get("pre_federal", False),
                "pre_federal_state": row.get("pre_federal_state"),
                "display_label": row.get("display_label"),
                "note_size": row.get("note_size"),
                "mintage": mintage,
                "figures": figures,
                "sources": sources,
                "primary_image": primary_image,
                "type_image": type_image,
                "secondary_image": secondary_image,
                "extra_images": extra_images if extra_images else None,
                "varieties": varieties if varieties else None,
                "social_posts": social_posts if social_posts else None,
                "status_badge": status_badge,
                "is_pre_federal": is_pre_federal,
                "is_placeholder": is_placeholder,
                "is_interleaved_checklist_only": is_interleaved,
            }
            records.append(rec)

    assert len(records) == 3202, f"Expected 3202 records, got {len(records)}"
    assert album_renames_count == 12, f"Expected 12 album renames, got {album_renames_count}"
    assert source_rewrites_count == 1070, f"Expected 1070 source rewrites, got {source_rewrites_count}"
    assert composition_scrub_count == 1724, f"Expected 1724 composition scrubs, got {composition_scrub_count}"

    pre_fed_count = sum(1 for r in records if r["is_pre_federal"])
    assert pre_fed_count == 9, f"C1 violation: Expected exactly 9 Pre-Federal records, got {pre_fed_count}"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(records)} sanitized records to: {output_path}")
    print(f"Stats: Album renames: {album_renames_count}, Source rewrites: {source_rewrites_count}, Composition scrubs: {composition_scrub_count}, Pre-Federal: {pre_fed_count}, Dropped images: {len(dropped_images)}")
    if dropped_images:
        print("Dropped image objects report:")
        for d in dropped_images:
            print(f"  - {d['nac_code']} ({d['field']}.{d['key']}): {d['reason']}")
    return 0

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_PATH
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_PATH
    sys.exit(build_public_catalog(inp, out))
