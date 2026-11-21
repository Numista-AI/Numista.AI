# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
build_image_index.py
─────────────────────────────────────────────────────────────────────────────
Scans all Numista.AI GCS image buckets and builds a Firestore image index
at collection: coin_image_index

Each document key = canonical coin key: {year}_{program}_{side}
                 or: {year}_{mint}_{program}_{side} when mint is known

Run:
    python build_image_index.py [--dry-run]

Options:
    --dry-run   Print index entries without writing to Firestore
    --wipe      Clear existing coin_image_index before re-indexing
"""

import os
import re
import sys
import argparse
import json
import base64
import unicodedata
from datetime import datetime
from pathlib import Path
from google.cloud import storage, firestore
import google.auth

# Force UTF-8 output so emoji in print() work on Windows cp1252 consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ─── Config ───────────────────────────────────────────────────────────────────

PROJECT = "studio-9101802118-8c9a8"
FIRESTORE_COLLECTION = "coin_image_index"
PUBLIC_URL_BASE = "https://storage.googleapis.com"

os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json"
)

# Buckets to scan: (bucket_name, gcs_prefix, source_tier, source_label, attribution)
SCAN_TARGETS = [
    (
        "us_mint_coin_images",
        "Numista_Attributed_Coins (1)/",
        1,
        "US Mint",
        "United States Mint image",
    ),
    (
        "numista-reference-library",
        "reference_library/us_mint_official/",
        1,
        "US Mint",
        "United States Mint image",
    ),
    (
        "numista-reference-library",
        "reference_library/atb_quarters/",
        2,
        "Numista Reference Library (ATB)",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/2023_series/",
        2,
        "Numista Reference Library (2023)",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/2024_series/",
        2,
        "Numista Reference Library (2024)",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/2025_series/",
        2,
        "Numista Reference Library (2025)",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/bulk_programs/",
        2,
        "Numista Reference Library",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/wikimedia_uscoin/",
        3,
        "Wikimedia Commons",
        "Wikimedia Commons / Public Domain",
    ),
    (
        "numista-reference-library",
        "reference_library/rare_uscoin/",
        2,
        "Numista Reference Library (Rare)",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/balabaskar_coins/",
        2,
        "Numista Reference Library",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/2026_series/",
        2,
        "Numista Reference Library (2026)",
        "",
    ),
    (
        "numista-reference-library",
        "reference_library/user_contributed/",
        5,
        "User Contributed",
        "",  # pulled from per-folder MANIFEST.json
    ),
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# ─── Shared Canonical Schema ───────────────────────────────────────────────────

_SCHEMA_PATH = Path(__file__).with_name("coin_image_schema.json")
with open(_SCHEMA_PATH, "r", encoding="utf-8") as _f:
    _SCHEMA = json.load(_f)

PROGRAM_TO_DENOM = _SCHEMA["program_to_denom"]
DISTINCTIVE_SIDE = _SCHEMA["distinctive_side"]
SHARED_WILDCARD_SIDES = _SCHEMA["shared_wildcard_sides"]
PRESIDENTIAL_SUBJECTS = _SCHEMA["presidential_subjects"]
ATB_PARK_SUBJECTS = _SCHEMA["atb_park_subjects"]
STATE_QUARTER_SUBJECTS = _SCHEMA["state_quarter_subjects"]
WOMEN_QUARTER_SUBJECTS = _SCHEMA["women_quarter_subjects"]
NATIVE_AMERICAN_YEARS = _SCHEMA["native_american_years"]
SEMIQUINCENTENNIAL_2026_SUBJECTS = _SCHEMA["semiquincentennial_2026_subjects"]

# ─── Slug → metadata parser ────────────────────────────────────────────────────

# Programs that have per-design subjects (State, President, Woman, etc.)
# For these programs we extract and encode the subject into the canonical key.
SUBJECT_PROGRAMS = {
    "50-state-quarters",
    "presidential-dollars",
    "american-women-quarters",
    "america-the-beautiful",
    "american-innovation",
    "native-american-dollar",
    "commemorative",
    "semiquincentennial",
    "quarter",
    "dime",
}

# Known program slug fragments → canonical program name
PROGRAM_MAP = [
    (r"silver.?eagle|american.?eagle.?silver",          "american-eagle-silver"),
    (r"gold.?eagle|american.?eagle.?gold",              "american-eagle-gold"),
    (r"platinum.?eagle|american.?eagle.?platinum",      "american-eagle-platinum"),
    (r"palladium.?eagle|american.?eagle.?palladium",    "american-eagle-palladium"),
    (r"state.?quarter|50.?state",                       "50-state-quarters"),
    (r"atb.?quarter|america.?the.?beautiful|america.?beautiful|national.?park|\batb\b", "america-the-beautiful"),
    (r"american.?women",                                "american-women-quarters"),
    (r"american.?innov",                                "american-innovation"),
    (r"native.?american|sacagawea",                     "native-american-dollar"),
    (r"presidential.?dollar|president",                 "presidential-dollars"),
    (r"morgan",                                         "morgan-dollar"),
    (r"peace.?dollar",                                  "peace-dollar"),
    (r"walking.?liberty",                               "walking-liberty"),
    (r"mercury.?dime|winged.?liberty",                  "mercury-dime"),
    (r"lincoln|wheat.?cent|memorial.?cent",             "lincoln-cent"),
    (r"jefferson.?nickel",                              "jefferson-nickel"),
    (r"buffalo.?nickel",                                "buffalo-nickel"),
    (r"kennedy.?half|half.?dollar",                     "kennedy-half-dollar"),
    (r"saint.?gaudens|double.?eagle",                   "saint-gaudens"),
    (r"bicentennial",                                   "bicentennial"),
    (r"commemorative",                                  "commemorative"),
    (r"american.?liberty",                              "american-liberty"),
    (r"flowing.?hair",                                  "flowing-hair"),
    (r"dime",                                           "dime"),
    (r"quarter",                                        "quarter"),
    (r"dollar",                                         "dollar"),
    (r"nickel",                                         "nickel"),
    (r"cent|penny",                                     "cent"),
]

MINT_MARKS = {"P": "P", "D": "D", "S": "S", "W": "W", "CC": "CC", "O": "O"}

_REVERSE_DISTINCTIVE_PROGRAMS = {
    "american-women-quarters",
    "america-the-beautiful",
    "50-state-quarters",
    "american-innovation",
}

# Middle initials that appear in president/honoree names and must never be read as mint marks
_MIDDLE_INITIAL_CONTEXTS = (
    r"(?:^|[-_\s])(?:"
    r"franklin[-_\s]+d[-_\s]+roosevelt|"
    r"harry[-_\s]+s[-_\s]+truman|"
    r"dwight[-_\s]+d[-_\s]+eisenhower|"
    r"ulysses[-_\s]+s[-_\s]+grant|"
    r"john[-_\s]+f[-_\s]+kennedy|"
    r"lyndon[-_\s]+b[-_\s]+johnson|"
    r"george[-_\s]+h[-_\s]+w[-_\s]+bush|"
    r"james[-_\s]+k[-_\s]+polk|"
    r"james[-_\s]+a[-_\s]+garfield|"
    r"chester[-_\s]+a[-_\s]+arthur|"
    r"warren[-_\s]+g[-_\s]+harding|"
    r"rutherford[-_\s]+b[-_\s]+hayes|"
    r"richard[-_\s]+m[-_\s]+nixon|"
    r"gerald[-_\s]+r[-_\s]+ford|"
    r"ida[-_\s]+b[-_\s]+wells|"
    r"ely[-_\s]+s[-_\s]+parker|"
    r"mary[-_\s]+g[-_\s]+ross|"
    r"d[-_\s]+roosevelt|"
    r"s[-_\s]+truman|"
    r"d[-_\s]+eisenhower|"
    r"s[-_\s]+grant|"
    r"f[-_\s]+kennedy|"
    r"b[-_\s]+johnson"
    r")(?=$|[-_\s])"
)

def slugify(text):
    """Normalize text for matching."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text.lower()

def detect_side(slug, program=None, subject=None, year=None):
    if re.search(r"(?:^|[-_\s])(obv|obverse|front)(?:$|[-_\s])", slug, re.I):
        return "obverse"
    if re.search(r"(?:^|[-_\s])(rev|reverse|back)(?:$|[-_\s])", slug, re.I):
        return "reverse"
    if subject:
        if program in _REVERSE_DISTINCTIVE_PROGRAMS:
            return "reverse"
        if program == "native-american-dollar" and year and year.isdigit() and int(year) >= 2009:
            return "reverse"
        if program in ("quarter", "semiquincentennial") and year == "2026":
            return "reverse"
        if program == "presidential-dollars":
            return "obverse"
    return "obverse"  # single-design series default

def detect_year(slug):
    m = re.search(r"(?<!\d)(1[789]\d{2}|20[012]\d)(?!\d)", slug)
    return m.group(1) if m else None

def detect_mint(slug, program=None):
    # Strip personal-name middle initials so e.g. 2014_D_roosevelt or harry-s-truman
    # never triggers a false Denver/San Francisco mint mark.
    cleaned = re.sub(_MIDDLE_INITIAL_CONTEXTS, " ", slug, flags=re.I)
    if program == "presidential-dollars":
        # Presidential dollars in this index never key on mint; also guard against
        # abbreviated middle-initial filenames like 2014_D_roosevelt.
        cleaned = re.sub(r"(?<!\d)(?:1[789]\d{2}|20[012]\d)[-_ ]+[ds](?=[-_ ]+[a-z])", " ", cleaned, flags=re.I)
    m = re.search(
        r"(?:(?<!\d)(?:1[789]\d{2}|20[012]\d)[-_ ]+([PDSWpdswOo]|CC)(?=[-_ .)]|$)|"
        r"(?:^|[-_\s(])mint[-_ ]?([PDSWpdswOo]|CC)(?=[-_ .)]|$)|"
        r"[-_\s(]([PDSWpdswOo]|CC)[-_ ](?:obv|obverse|rev|reverse|unc|uncirculated|proof)(?=[-_ .)]|$))",
        cleaned,
    )
    if m:
        val = next((g for g in m.groups() if g), None)
        return val.upper() if val else None
    return None

def detect_program(slug):
    for pattern, canonical in PROGRAM_MAP:
        if re.search(pattern, slug, re.I):
            return canonical
    return None

def _match_subject_map(slug, subject_map):
    for name_lower, name_slug in sorted(subject_map.items(), key=lambda x: -len(x[0])):
        pattern = r"(?:^|[^a-z0-9])" + re.escape(name_lower).replace(r"\ ", r"[\s_-]+") + r"(?:$|[^a-z0-9])"
        if re.search(pattern, slug, re.I):
            return name_slug
    return None

def detect_subject(slug, program, year=None):
    """
    Program-scoped exact subject extraction. Never mixes subjects across programs.
    Returns a canonical slug string or None.
    """
    if program not in SUBJECT_PROGRAMS:
        return None

    if program == "presidential-dollars":
        # Handle abbreviated middle-initial filenames like 2014_D_roosevelt
        if year == "2014" and re.search(r"(?:^|[-_\s])roosevelt(?:$|[-_\s])", slug, re.I):
            return "franklin-d-roosevelt"
        if year == "2013" and re.search(r"(?:^|[-_\s])roosevelt(?:$|[-_\s])", slug, re.I):
            return "theodore-roosevelt"
        return _match_subject_map(slug, PRESIDENTIAL_SUBJECTS)

    if program == "america-the-beautiful":
        return _match_subject_map(slug, ATB_PARK_SUBJECTS)

    if program in ("50-state-quarters", "american-innovation"):
        return _match_subject_map(slug, STATE_QUARTER_SUBJECTS)

    if program == "american-women-quarters":
        return _match_subject_map(slug, WOMEN_QUARTER_SUBJECTS)

    if program == "native-american-dollar":
        if year and year in NATIVE_AMERICAN_YEARS:
            return NATIVE_AMERICAN_YEARS[year]
        return None

    if program in ("quarter", "semiquincentennial", "dime"):
        if year == "2026":
            return _match_subject_map(slug, SEMIQUINCENTENNIAL_2026_SUBJECTS)
        return None

    return None

def build_composite_key(denom, program, year, subject, side, mint=None, include_mint=False):
    subj = subject if (subject and subject.strip()) else "standard"
    parts = [denom, program, year, subj, side]
    if include_mint and mint:
        parts.append(mint)
    return "|".join(parts)

def parse_filename(blob_name, bucket, prefix, source_tier):
    """
    Parse a GCS blob path into structured coin metadata.
    Returns a dict or None if the file is not a coin image.
    """
    # Strip prefix and get just the filename
    rel_path = blob_name[len(prefix):]
    # For nested folders, use the folder name as program hint
    parts = rel_path.split("/")
    folder_hint = parts[0] if len(parts) > 1 else ""
    filename = parts[-1]

    # Filter non-image files
    ext = os.path.splitext(filename)[1].lower()
    if ext not in IMAGE_EXTENSIONS:
        return None
    if filename.startswith(".") or filename in ("MANIFEST.json", "attribution.json"):
        return None

    # Strip prefix junk like "final_attributed_"
    clean = re.sub(r"^final_attributed_", "", filename, flags=re.I)
    clean = os.path.splitext(clean)[0]  # remove extension

    slug = slugify(f"{folder_hint} {clean}")

    year    = detect_year(slug)
    program = detect_program(slug) or slugify(folder_hint).replace(" ", "-") or "unknown"
    mint    = detect_mint(slug, program=program)

    if not year:
        return None  # can't index without a year

    # Detect optional per-design subject (program-scoped)
    subject = detect_subject(slug, program, year=year)
    side    = detect_side(slug, program=program, subject=subject, year=year)
    denom   = PROGRAM_TO_DENOM.get(program, program)

    composite_key = build_composite_key(denom, program, year, subject, side)

    # Legacy key preserved for dual-read diagnostics
    legacy_parts = [year]
    if mint:
        legacy_parts.append(mint)
    if subject:
        legacy_parts.append(subject)
    legacy_parts.append(program)
    legacy_parts.append(side)
    legacy_key = "_".join(legacy_parts)

    is_uncirculated = bool(re.search(r"uncirculated|\bunc\b", slug, re.I))
    filename_specificity = len(clean)

    # Build public URL
    encoded_path = blob_name.replace(" ", "%20")
    public_url = f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"

    return {
        "canonical_key":        composite_key,
        "composite_key":        composite_key,
        "legacy_key":           legacy_key,
        "denom":                denom,
        "year":                 year,
        "mint":                 mint,
        "subject":              subject,
        "program":              program,
        "side":                 side,
        "is_uncirculated":      is_uncirculated,
        "filename_specificity": filename_specificity,
        "gcs_path":             f"gs://{bucket}/{blob_name}",
        "public_url":           public_url,
        "filename":             filename,
        "source_tier":          source_tier,
    }

# ─── Manifest loader ───────────────────────────────────────────────────────────

def load_manifests(storage_client, bucket_name, prefix):
    """Load MANIFEST.json files from user_contributed subfolders."""
    manifests = {}
    try:
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            if blob.name.endswith("MANIFEST.json"):
                data = json.loads(blob.download_as_text())
                folder = "/".join(blob.name.split("/")[:-1]) + "/"
                manifests[folder] = data
    except Exception as e:
        print(f"  [warn] Could not load manifests from {prefix}: {e}")
    return manifests

# ─── Main ─────────────────────────────────────────────────────────────────────

# ─── Gemini Vision fallback ────────────────────────────────────────────────────

GEMINI_VISION_PROMPT = """
You are a US coin identification expert. Examine this coin image and return a JSON object with:
  year:    (string) the 4-digit year on the coin, e.g. "1921"
  mint:    (string) mint mark if visible: P, D, S, W, CC, O — or null
  program: (string) canonical program name, one of:
           american-eagle-silver, american-eagle-gold, american-eagle-platinum,
           american-eagle-palladium, 50-state-quarters, america-the-beautiful,
           american-women-quarters, american-innovation, native-american-dollar,
           presidential-dollars, morgan-dollar, peace-dollar, walking-liberty,
           mercury-dime, lincoln-cent, jefferson-nickel, buffalo-nickel,
           kennedy-half-dollar, saint-gaudens, bicentennial, commemorative,
           american-liberty, flowing-hair, dollar, dime, quarter, nickel, cent, unknown
  side:    "obverse" or "reverse"
  confidence: "high", "medium", or "low"

Return ONLY the JSON object, no markdown, no explanation.
"""

def classify_with_gemini(blob, storage_client):
    """Download image bytes from GCS and ask Gemini Vision to identify the coin."""
    if not GEMINI_AVAILABLE:
        return None
    try:
        image_bytes = blob.download_as_bytes()
        ext  = Path(blob.name).suffix.lower()
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext.lstrip('.')}"

        client = genai.Client(vertexai=True, project=PROJECT, location="global")
        response = client.models.generate_content(
            model="gemini-4-hydrogen",
            contents=[
                genai_types.Part.from_text(GEMINI_VISION_PROMPT),
                genai_types.Part.from_bytes(data=image_bytes, mime_type=mime),
            ]
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        return data
    except Exception as e:
        print(f"    [vision] Gemini error for {blob.name}: {e}")
        return None


# ─── Contribution folder setup ─────────────────────────────────────────────────

CONTRIBUTION_LOCAL_DIR = r"C:\Users\ericd\Documents\MyVertexProject\new_coin_images"

MANIFEST_TEMPLATE = {
    "contributed_by": "Eric D.",
    "contributed_date": "",
    "source_name": "",
    "license": "Personal Permission / Public Domain / CC-BY / other",
    "attribution_text": "Image courtesy of [Source]. Used with permission.",
    "auto_stock": False,
    "submitter_emails": [
        "eric@numista.ai",
        "eric.seaman@yahoo.com",
        "ericdcman@gmail.com"
    ],
    "images": [
        {
            "filename": "EXAMPLE-2025-silver-eagle-army-privy-obverse.jpg",
            "year": "2025",
            "mint": "W",
            "program": "american-eagle-silver",
            "side": "obverse",
            "notes": "US Army Privy Mark"
        }
    ]
}

def setup_contribution_folder():
    """Create the local contribution drop folder and a MANIFEST template."""
    local_dir = Path(CONTRIBUTION_LOCAL_DIR)
    local_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = local_dir / "MANIFEST.json"
    if not manifest_path.exists():
        import datetime as dt
        template = dict(MANIFEST_TEMPLATE)
        template["contributed_date"] = dt.date.today().isoformat()
        manifest_path.write_text(
            json.dumps(template, indent=2), encoding="utf-8"
        )
        print(f"  Created: {manifest_path}")
    else:
        print(f"  Exists: {manifest_path}")

    readme = local_dir / "README.txt"
    readme.write_text(
        "NUMISTA.AI — COIN IMAGE CONTRIBUTION FOLDER\n"
        "=============================================\n\n"
        "HOW TO USE:\n"
        "1. Copy coin images into this folder (any subfolder is OK)\n"
        "2. Edit MANIFEST.json to describe the images and their source\n"
        "3. Run: python numista_backend/build_image_index.py --ingest-contributions\n\n"
        "ADMIN ACCOUNTS (auto-stock, no consent needed):\n"
        "  eric@numista.ai\n"
        "  eric.seaman@yahoo.com\n"
        "  ericdcman@gmail.com\n\n"
        "All other users: image will be proposed to them for consent + rewards.\n",
        encoding="utf-8"
    )
    print(f"  Created: {readme}")
    print(f"\n  Contribution folder ready at: {local_dir}")
    print(f"  GCS destination: gs://numista-reference-library/reference_library/user_contributed/")


def _candidate_rank_tuple(item):
    return (
        item.get("source_tier", 99),
        0 if item.get("is_uncirculated") else 1,
        -(item.get("filename_specificity", 0)),
        item.get("gcs_path", ""),
    )


def select_winners(parsed_items):
    """
    Group parsed items by composite_key and deterministically select the winner
    for each key without last-writer-wins overwrites.
    Returns (winners_by_key, collision_count).
    """
    grouped = {}
    for item in parsed_items:
        key = item["composite_key"]
        grouped.setdefault(key, []).append(item)

    winners = {}
    collisions = 0
    for key, candidates in grouped.items():
        ranked = sorted(candidates, key=_candidate_rank_tuple)
        winner = dict(ranked[0])
        if len(ranked) > 1:
            collisions += len(ranked) - 1
            winner["alternates"] = [
                {
                    "gcs_path": c["gcs_path"],
                    "public_url": c["public_url"],
                    "source_tier": c["source_tier"],
                }
                for c in ranked[1:6]
            ]
        else:
            winner["alternates"] = []
        winners[key] = winner
    return winners, collisions


def main():
    parser = argparse.ArgumentParser(description="Build Numista coin image index")
    parser.add_argument("--dry-run",              action="store_true", help="Print only, no Firestore writes")
    parser.add_argument("--report-json",          type=str, default=None, help="Write dry-run report JSON to this path")
    parser.add_argument("--wipe",                 action="store_true", help="Delete existing index before re-indexing")
    parser.add_argument("--vision-pass",          action="store_true", help="Re-classify 'unknown' entries using Gemini Vision")
    parser.add_argument("--ingest-contributions", action="store_true", help="Upload local new_coin_images/ to GCS and index")
    parser.add_argument("--setup-contribution",   action="store_true", help="Create the local contribution drop folder")
    args = parser.parse_args()

    if args.setup_contribution:
        setup_contribution_folder()
        return

    credentials, _ = google.auth.default()
    storage_client  = storage.Client(credentials=credentials, project=PROJECT)
    db              = firestore.Client(credentials=credentials, project=PROJECT)

    if args.wipe and not args.dry_run:
        print("🗑  Wiping existing coin_image_index...")
        col = db.collection(FIRESTORE_COLLECTION)
        docs = col.stream()
        batch = db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            if count % 500 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        print(f"   Deleted {count} existing entries.")

    # Skip full GCS scan if we only want to run the vision pass
    skip_scan = args.vision_pass and not args.dry_run and not args.wipe

    total_scanned  = 0
    total_indexed  = 0
    total_skipped  = 0
    program_counts = {}
    all_candidates = []

    for (bucket_name, prefix, source_tier, source_label, default_attribution) in SCAN_TARGETS:
        if skip_scan:
            break
        print(f"\n📂 Scanning gs://{bucket_name}/{prefix} (Tier {source_tier}: {source_label})")

        # Load manifests for user_contributed folder
        manifests = {}
        if "user_contributed" in prefix:
            manifests = load_manifests(storage_client, bucket_name, prefix)

        try:
            bucket_obj = storage_client.bucket(bucket_name)
            blobs = list(bucket_obj.list_blobs(prefix=prefix))
        except Exception as e:
            print(f"  ❌ Could not list bucket: {e}")
            continue

        for blob in blobs:
            total_scanned += 1
            result = parse_filename(blob.name, bucket_name, prefix, source_tier)
            if not result:
                total_skipped += 1
                continue

            # Resolve attribution from manifest if available
            attribution = default_attribution
            blob_folder = "/".join(blob.name.split("/")[:-1]) + "/"
            if blob_folder in manifests:
                attribution = manifests[blob_folder].get("attribution_text", default_attribution)

            result["source_label"] = source_label
            result["attribution"] = attribution
            all_candidates.append(result)

    winners, collisions = select_winners(all_candidates)
    batch = db.batch() if not args.dry_run else None
    batch_n = 0

    for doc_key, result in sorted(winners.items()):
        side_key = result["side"]
        doc_data = {
            side_key: {
                "gcs_path":      result["gcs_path"],
                "public_url":    result["public_url"],
                "source_tier":   result["source_tier"],
                "source_label":  result["source_label"],
                "attribution":   result["attribution"],
                "indexed_at":    datetime.utcnow().isoformat(),
            },
            "denom":      result["denom"],
            "year":       result["year"],
            "mint":       result["mint"],
            "subject":    result.get("subject"),
            "program":    result["program"],
            "alternates": result.get("alternates", []),
        }

        if args.dry_run:
            print(f"  [{result['source_tier']}] {doc_key} → {result['public_url'][:80]}...")
        else:
            doc_ref = db.collection(FIRESTORE_COLLECTION).document(doc_key)
            batch.set(doc_ref, doc_data, merge=True)
            batch_n += 1
            if batch_n >= 400:
                batch.commit()
                batch = db.batch()
                batch_n = 0

        total_indexed += 1
        prog = result["program"]
        program_counts[prog] = program_counts.get(prog, 0) + 1

    if not args.dry_run and batch_n > 0:
        batch.commit()

    if args.report_json:
        report = {
            "total_scanned": total_scanned,
            "total_candidates": len(all_candidates),
            "total_indexed": total_indexed,
            "total_skipped": total_skipped,
            "collisions_deduped": collisions,
            "program_counts": program_counts,
            "keys": sorted(winners.keys()),
        }
        Path(args.report_json).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"  Wrote dry-run report to {args.report_json}")

    # ── Gemini Vision second pass ──────────────────────────────────────────────
    if args.vision_pass:
        if not GEMINI_AVAILABLE:
            print("\n  [vision] google.genai not installed — skipping.")
            print("  Run: pip install google-genai")
        else:
            print("\n  Running Gemini Vision pass on unclassified entries...")

            # Programs that need reclassification — either unknown or folder-name placeholders
            NON_CANONICAL = {
                "unknown", "aj_collection", "aj-collection",
                "si_quarters", "si-quarters",
                "us_mint_manual", "us-mint-manual",
                "balabaskar_coins", "balabaskar-coins",
                "rare_uscoin", "rare-uscoin",
                "2026_series", "2026-series",
            }

            # Collect all docs needing reclassification
            needs_vision = []
            for prog in NON_CANONICAL:
                docs = list(
                    db.collection(FIRESTORE_COLLECTION)
                      .where(filter=firestore.FieldFilter("program", "==", prog))
                      .stream()
                )
                needs_vision.extend(docs)

            print(f"  Found {len(needs_vision)} entries to classify")

            vision_updated = 0
            for doc in needs_vision:
                data   = doc.to_dict()
                side   = "obverse" if "obverse" in data else "reverse"
                gcs_path = data.get(side, {}).get("gcs_path", "")
                if not gcs_path:
                    continue

                # Parse gs://bucket/blob from gcs_path
                gcs_path_clean = gcs_path.replace("gs://", "")
                bkt_name, blob_name = gcs_path_clean.split("/", 1)
                blob = storage_client.bucket(bkt_name).blob(blob_name)

                result = classify_with_gemini(blob, storage_client)
                if not result or result.get("confidence") == "low":
                    continue
                if result.get("program", "unknown") == "unknown":
                    continue

                # Build new canonical key
                new_year    = result.get("year") or data.get("year", "")
                new_mint    = result.get("mint") or data.get("mint")
                new_program = result.get("program", "unknown")
                new_side    = result.get("side", side)

                key_parts = [new_year]
                if new_mint:
                    key_parts.append(new_mint)
                key_parts.append(new_program)
                key_parts.append(new_side)
                new_key = "_".join(key_parts)

                if args.dry_run:
                    print(f"    [vision] {doc.id} -> {new_key} ({result.get('confidence')})") 
                else:
                    # Write to new key, delete old
                    new_ref = db.collection(FIRESTORE_COLLECTION).document(new_key)
                    new_ref.set({
                        new_side: data.get(side, {}),
                        "year":    new_year,
                        "mint":    new_mint,
                        "program": new_program,
                        "vision_classified": True,
                    }, merge=True)
                    doc.reference.delete()
                    vision_updated += 1
                    print(f"    [vision] {doc.id} -> {new_key}")

            print(f"  Vision pass complete: {vision_updated} entries reclassified")

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE")
    print(f"  Scanned:  {total_scanned:,} files")
    print(f"  Indexed:  {total_indexed:,} coin images")
    print(f"  Skipped:  {total_skipped:,} (non-image / no year detected)")
    print(f"\n  Images by program:")
    for prog, count in sorted(program_counts.items(), key=lambda x: -x[1]):
        print(f"    {count:>5}  {prog}")

    if not args.dry_run:
        print(f"  Firestore collection '{FIRESTORE_COLLECTION}' updated.")
        db.collection("config").document("image_index_stats").set({
            "total_indexed": total_indexed,
            "total_scanned": total_scanned,
            "program_counts": program_counts,
            "last_run": datetime.utcnow().isoformat(),
        })
    else:
        print(f"\n  (dry-run — nothing written to Firestore)")

if __name__ == "__main__":
    main()
