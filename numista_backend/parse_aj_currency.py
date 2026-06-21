"""
parse_aj_currency.py
====================
Parses the `Description` field of AJ's 413 currency items in Firestore and
populates blank Denomination, Series, and Year fields.

Steps
-----
1. Sample  – print the first 30 Description values
2. Parse   – extract denomination, series/year, type, issuer for ALL 413 items
3. Dry-run – print all parsed rows + success-rate summary
4. CSV     – save to AJ_Currency_Parsed.csv
5. Firestore write – update blank fields (DRY_RUN toggle)

Usage
-----
    python parse_aj_currency.py
"""

import csv
import os
import re
import sys

# ── ensure UTF-8 console output on Windows ──────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Firestore setup ──────────────────────────────────────────────────────────
KEY_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json.json")
USER_EMAIL   = "jseaman1204@gmail.com"
COLLECTION   = f"users/{USER_EMAIL}/currency"
CSV_OUT      = r"C:\Users\ericd\Documents\MyVertexProject\AJ_Currency_Parsed.csv"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

import firebase_admin
from firebase_admin import credentials, firestore as fs_admin

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = fs_admin.client()

# ── Step 1 : Fetch all documents ─────────────────────────────────────────────
print("=" * 70)
print("STEP 1 — Fetching currency documents …")
print("=" * 70)
raw_docs  = list(db.collection(COLLECTION).stream())
print(f"  → {len(raw_docs)} documents retrieved\n")

records = [(d.id, d.to_dict() or {}) for d in raw_docs]

print("--- First 30 Description values ---")
for i, (doc_id, data) in enumerate(records[:30], 1):
    desc = str(data.get("Description") or "").strip()
    print(f"  {i:>3}.  {desc[:100]}")

# ── Step 2 : Parser ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 2 — Building parser …")
print("=" * 70)

# ---- Type keywords (ordered – most-specific first) --------------------------
TYPE_PATTERNS = [
    # Confederate
    (r'\bCSA\b|\bConfederate\b',                            "Confederate"),
    # Demand Notes
    (r'\bDemand\s+Note\b',                                  "Demand Note"),
    # Interest Bearing Note
    (r'\bInterest[\s-]Bearing\b',                           "Interest Bearing Note"),
    # Refunding Certificate
    (r'\bRefunding\s+Cert',                                 "Refunding Certificate"),
    # Compound Interest
    (r'\bCompound\s+Interest',                              "Compound Interest Note"),
    # Treasury / Coin Notes (sometimes called "Coin Note")
    (r'\bTreasury\s+Note\b|\bCoin\s+Note\b',               "Treasury Note"),
    # Gold Certificate
    (r'\bGold\s+Cert',                                      "Gold Certificate"),
    # Silver Certificate
    (r'\bSilver\s+Cert',                                    "Silver Certificate"),
    # National Bank Note
    (r'\bNational\s+Bank\b|\bNBN\b',                        "National Bank Note"),
    # Federal Reserve Bank Note  (must come BEFORE FRN)
    (r'\bFederal\s+Reserve\s+Bank\s+Note\b|\bFRBN\b',      "Federal Reserve Bank Note"),
    # Federal Reserve Note
    (r'\bFederal\s+Reserve\s+Note\b|\bFRN\b',              "Federal Reserve Note"),
    # Fractional Currency
    (r'\bFractional\b',                                     "Fractional Currency"),
    # Legal Tender / United States Note
    (r'\bLegal\s+Tender\b|\bUnited\s+States\s+Note\b',     "Legal Tender Note"),
    # Educational Series (Silver Cert variety)
    (r'\bEducational\b',                                    "Silver Certificate"),
    # Error note
    (r'\bError\b',                                          "Error Note"),
]

# ---- Denomination patterns --------------------------------------------------
# Matches:  $1  $1.00  $½  ½ Dollar  1/2 Dollar  50 cents  50c  50¢
DENOM_PATTERNS = [
    # Dollar sign followed by number (e.g. $1, $10, $100, $1.00)
    r'\$\s*(\d+(?:\.\d+)?)',
    # e.g. "One Dollar" / "Five Dollar" / "Half Dollar" written-out
    r'\b(One|Two|Three|Four|Five|Ten|Twenty|Fifty|One\s+Hundred|Five\s+Hundred|One\s+Thousand|Five\s+Thousand|Ten\s+Thousand|One\s+Hundred\s+Thousand|Five\s+Cents|Ten\s+Cents|Fifteen\s+Cents|Twenty(?:-|\s)Five\s+Cents|Fifty\s+Cents|Half)\s+(?:Dollar|Dollars|Cent|Cents|Dollar\s+Bill|Dollar\s+Note)\b',
    # e.g. "50 cents"  "25 cents"
    r'\b(\d+)\s+[Cc]ents?\b',
    # e.g. "5C"  "10C"  (fractional)
    r'\b(\d+)[Cc]\b',
    # e.g. "½ Dollar"  "1/2 Dollar"
    r'(½|1/2)\s+Dollar',
]

WORD_TO_DENOM = {
    "one": "$1", "two": "$2", "three": "$3", "four": "$4", "five": "$5",
    "ten": "$10", "twenty": "$20", "fifty": "$50",
    "one hundred": "$100", "five hundred": "$500",
    "one thousand": "$1000", "five thousand": "$5000",
    "ten thousand": "$10000", "one hundred thousand": "$100000",
    "five cents": "5¢", "ten cents": "10¢", "fifteen cents": "15¢",
    "twenty-five cents": "25¢", "twenty five cents": "25¢", "fifty cents": "50¢",
    "half": "50¢",
}

# ---- Federal-Reserve issuer banks -------------------------------------------
FRB_CITIES = [
    "Boston", "New York", "Philadelphia", "Cleveland", "Richmond",
    "Atlanta", "Chicago", "St. Louis", "Minneapolis", "Kansas City",
    "Dallas", "San Francisco",
]
FRB_PATTERN = re.compile(
    r'Federal\s+Reserve\s+Bank\s+of\s+(' + '|'.join(re.escape(c) for c in FRB_CITIES) + r')',
    re.IGNORECASE,
)

# ---- Series/Year patterns ---------------------------------------------------
# Accepts:  1957   1934A   1963B   1957 B   Fr. 1504   "Series 1899"
YEAR_PATTERN = re.compile(
    r'\b(1[6-9]\d{2}|20[0-2]\d)\s*([A-Ha-h])?\b'   # year + optional letter suffix
)

FR_NUMBER = re.compile(r'\bFr\.?\s*(\d+)\b', re.IGNORECASE)   # Friedberg #


def normalize_denom(raw: str) -> str:
    """Return a canonical denomination string."""
    raw = raw.strip()
    # already dollar-sign form
    m = re.match(r'^\$\s*(\d+(?:\.\d+)?)$', raw)
    if m:
        v = float(m.group(1))
        return f"${int(v) if v == int(v) else v}"
    # written-out form
    lower = raw.lower().strip(".")
    if lower in WORD_TO_DENOM:
        return WORD_TO_DENOM[lower]
    # fractional cents
    m = re.match(r'^(\d+)[Cc]$', raw)
    if m:
        return f"{m.group(1)}¢"
    m = re.match(r'^(\d+)\s+[Cc]ents?$', raw, re.IGNORECASE)
    if m:
        return f"{m.group(1)}¢"
    if raw in ("½", "1/2"):
        return "50¢"
    return raw


def parse_description(desc: str) -> dict:
    """
    Return dict with keys:
        denomination_parsed, series_year_parsed, type_parsed, issuer_parsed
    Each value is either a non-empty string or "" if not found.
    """
    if not desc or not desc.strip():
        return dict(denomination_parsed="", series_year_parsed="",
                    type_parsed="", issuer_parsed="")

    desc_norm = " ".join(desc.split())   # collapse whitespace

    # ---- type ---------------------------------------------------------------
    type_parsed = ""
    for pattern, label in TYPE_PATTERNS:
        if re.search(pattern, desc_norm, re.IGNORECASE):
            type_parsed = label
            break

    # ---- issuer (Federal Reserve Bank of …) ---------------------------------
    issuer_parsed = ""
    m_frb = FRB_PATTERN.search(desc_norm)
    if m_frb:
        issuer_parsed = f"Federal Reserve Bank of {m_frb.group(1).title()}"

    # ---- denomination -------------------------------------------------------
    denomination_parsed = ""

    # Pattern 1: dollar sign
    m = re.search(r'\$\s*(\d+(?:\.\d+)?)', desc_norm)
    if m:
        v = float(m.group(1))
        denomination_parsed = f"${int(v) if v == int(v) else v}"

    # Pattern 2: written-out name (only if still blank)
    if not denomination_parsed:
        for pattern in DENOM_PATTERNS[1:]:   # skip pattern 0 ($ already done)
            m = re.search(pattern, desc_norm, re.IGNORECASE)
            if m:
                raw_match = m.group(1) if m.lastindex else m.group(0)
                denomination_parsed = normalize_denom(raw_match)
                if denomination_parsed:
                    break

    # ---- series/year --------------------------------------------------------
    series_year_parsed = ""
    # Check for explicit "Series YYYY" prefix
    m_series = re.search(r'\bSeries\s+(1[6-9]\d{2}|20[0-2]\d)\s*([A-Ha-h])?\b', desc_norm, re.IGNORECASE)
    if m_series:
        yr   = m_series.group(1)
        suf  = (m_series.group(2) or "").upper()
        series_year_parsed = yr + suf
    else:
        # Find ALL year matches and pick the most plausible one
        matches = list(YEAR_PATTERN.finditer(desc_norm))
        if matches:
            # Prefer matches that come before the type keyword (i.e., are actually a series date)
            # Simple heuristic: use the first match in the string
            yr_m = matches[0]
            yr   = yr_m.group(1)
            suf  = (yr_m.group(2) or "").upper()
            series_year_parsed = yr + suf

    return dict(
        denomination_parsed = denomination_parsed,
        series_year_parsed  = series_year_parsed,
        type_parsed         = type_parsed,
        issuer_parsed       = issuer_parsed,
    )


# ── Step 3 : Dry-run parse ALL records ───────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3 — Dry-run parse (ALL items)")
print("=" * 70)

results = []
for doc_id, data in records:
    desc   = str(data.get("Description") or "").strip()
    parsed = parse_description(desc)
    results.append(dict(
        doc_id       = doc_id,
        description  = desc,
        **parsed,
        _data        = data,   # keep for write step
    ))

# success counters
def has_val(v): return bool(v and v.strip())

n_total     = len(results)
n_denom_ok  = sum(1 for r in results if has_val(r["denomination_parsed"]))
n_year_ok   = sum(1 for r in results if has_val(r["series_year_parsed"]))
n_type_ok   = sum(1 for r in results if has_val(r["type_parsed"]))
n_any_ok    = sum(1 for r in results if any(
                  has_val(r[k]) for k in
                  ["denomination_parsed","series_year_parsed","type_parsed"]))

print(f"\n{'#':>4}  {'DocID':<20}  {'Denomination':<14}  {'Series/Year':<12}  {'Type':<30}  {'Issuer':<35}  Description")
print("-" * 160)
for i, r in enumerate(results, 1):
    print(
        f"{i:>4}  "
        f"{r['doc_id'][:18]:<20}  "
        f"{r['denomination_parsed']:<14}  "
        f"{r['series_year_parsed']:<12}  "
        f"{r['type_parsed']:<30}  "
        f"{r['issuer_parsed'][:33]:<35}  "
        f"{r['description'][:70]}"
    )

print("\n--- Sample of 10 Descriptions with parsed results ---")
samples = [r for r in results if has_val(r["denomination_parsed"])][:5] + \
          [r for r in results if not has_val(r["denomination_parsed"])][:5]
for r in samples[:10]:
    print(f"  DESC  : {r['description'][:90]}")
    print(f"  PARSED: denom={r['denomination_parsed']!r:12}  year={r['series_year_parsed']!r:8}  type={r['type_parsed']!r:30}  issuer={r['issuer_parsed']!r}")
    print()

print("\n--- Parsing Coverage Summary ---")
print(f"  Total documents       : {n_total}")
print(f"  Denomination parsed   : {n_denom_ok:>4}  ({n_denom_ok/n_total*100:.1f}%)")
print(f"  Series/Year parsed    : {n_year_ok:>4}  ({n_year_ok/n_total*100:.1f}%)")
print(f"  Type parsed           : {n_type_ok:>4}  ({n_type_ok/n_total*100:.1f}%)")
print(f"  At-least-one field    : {n_any_ok:>4}  ({n_any_ok/n_total*100:.1f}%)")

# ── Step 4 : Save to CSV ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"STEP 4 — Saving CSV → {CSV_OUT}")
print("=" * 70)

with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "doc_id", "description",
        "denomination_parsed", "series_year_parsed",
        "type_parsed", "issuer_parsed",
    ])
    writer.writeheader()
    for r in results:
        writer.writerow({k: r[k] for k in writer.fieldnames})

print(f"  → {n_total} rows written to {CSV_OUT}")

# ── Step 5 : Write to Firestore ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 5 — Firestore update")
print("=" * 70)

coverage = n_any_ok / n_total if n_total else 0
if coverage < 0.80:
    print(f"  ✗ Coverage {coverage*100:.1f}% < 80% threshold.  Skipping Firestore write.")
    sys.exit(0)

print(f"  ✓ Coverage {coverage*100:.1f}% — proceeding.\n")

# Field mapping: parsed field → Firestore field to fill (only if currently blank)
FIELD_MAP = {
    "denomination_parsed": "Denomination",
    "series_year_parsed":  "Series",
    "type_parsed":         "currency_type_label",
}

def is_blank(v) -> bool:
    """Return True if a Firestore field value is empty / None / whitespace."""
    return v is None or str(v).strip() == ""


for dry_run in [True, False]:
    mode_label = "DRY RUN" if dry_run else "LIVE WRITE"
    print(f"\n--- {mode_label} ---")

    n_updated   = 0
    n_skipped   = 0
    n_no_change = 0
    errors      = []

    for r in results:
        doc_id      = r["doc_id"]
        data        = r["_data"]
        update_dict = {}

        for parsed_field, firestore_field in FIELD_MAP.items():
            new_val = r.get(parsed_field, "")
            if not has_val(new_val):
                continue                          # nothing to write
            existing = data.get(firestore_field)
            if is_blank(existing):                # only fill blank fields
                update_dict[firestore_field] = new_val

        # Year field
        yr_new = r.get("series_year_parsed", "")
        if has_val(yr_new) and is_blank(data.get("Year")):
            update_dict["Year"] = yr_new

        if not update_dict:
            n_no_change += 1
            continue

        if dry_run:
            n_updated += 1
            if n_updated <= 15:
                print(f"  Would update {doc_id[:20]}: {update_dict}")
        else:
            try:
                db.collection(COLLECTION).document(doc_id).update(update_dict)
                n_updated += 1
            except Exception as e:
                errors.append((doc_id, str(e)))
                n_skipped += 1

    print(f"\n  Documents that would be / were updated : {n_updated}")
    print(f"  Documents with no blank fields to fill : {n_no_change}")
    if errors:
        print(f"  Errors                                 : {len(errors)}")
        for eid, emsg in errors[:5]:
            print(f"    {eid}: {emsg}")

    if not dry_run:
        print("\n  ✓ Firestore write complete.")
        break

print("\n" + "=" * 70)
print("Done.")
print("=" * 70)
