"""
parse_aj_currency_v2.py
=======================
Improved parser for AJ's 413 Firestore currency documents.

ACTUAL SCHEMA (from audit):
  Fields: Condition, Cost, Country, Denomination, Description,
          Personal Notes, Personal Ref #, Purchase Date, Quantity,
          Series/Issuer, Year, category, created_at, currency_type,
          currency_type_label, import_batch, inventoryStatus,
          source, source_file, user_email

Key improvements over v1
------------------------
- Year extraction from Description for the 15 blank-Year docs.
  Real descriptions like "1957 $1 Silver Certificate" → Year = 1957.
  Also handles FR# in parentheses: "(FR237)" → Friedberg_Number = "Fr. 237"
- Friedberg number → Friedberg_Number field.
- FRB-city issuer → Series/Issuer field (it's blank for all 413 docs).
- Grade upgrade: Condition already filled (404/413), but 9 are blank.
- Confederate series → currency_type_label if not already set.
- Denomination for 30 blank docs.
- currency_type_label for 112 blank docs.

Steps
-----
  1. Load all 413 documents.
  2. Audit current field coverage (before state).
  3. Parse descriptions → candidate values.
  4. Dry-run: show what would change.
  5. Live write (fills blank fields only).
  6. Post-write audit.
  7. Save CSV.

Usage
-----
    python parse_aj_currency_v2.py
"""

import csv
import os
import re
import sys

# ── UTF-8 console output ─────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Firestore config ─────────────────────────────────────────────────────────
KEY_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "serviceAccountKey.json.json")
USER_EMAIL = "jseaman1204@gmail.com"
COLLECTION = f"users/{USER_EMAIL}/currency"
CSV_OUT    = r"C:\Users\ericd\Documents\MyVertexProject\AJ_Currency_Parsed_v2.csv"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

import firebase_admin
from firebase_admin import credentials, firestore as fs_admin

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = fs_admin.client()

# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────
def is_blank(v) -> bool:
    return v is None or str(v).strip() == ""

def has_val(v) -> bool:
    return not is_blank(v)

def doc_has(data: dict, *keys) -> bool:
    return any(has_val(data.get(k)) for k in keys)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load all documents
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 70)
print("STEP 1 — Fetching currency documents …")
print("=" * 70)
raw_docs = list(db.collection(COLLECTION).stream())
print(f"  → {len(raw_docs)} documents retrieved\n")
records = [(d.id, d.to_dict() or {}) for d in raw_docs]

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Pre-parse field coverage audit
# ─────────────────────────────────────────────────────────────────────────────
# Maps: human label → list of Firestore field names (any populated counts)
AUDIT_FIELDS = {
    "Year":              ["Year"],
    "Denomination":      ["Denomination"],
    "Series/Issuer":     ["Series/Issuer"],
    "Friedberg_Number":  ["Friedberg_Number"],
    "Condition":         ["Condition"],
    "currency_type_label": ["currency_type_label"],
    "Description":       ["Description"],
}

print("=" * 70)
print("STEP 2 — Pre-parse field coverage audit (BEFORE)")
print("=" * 70)
print(f"\n{'Field':<25}  {'Populated':>10}  {'Blank':>8}  {'% filled':>9}")
print("-" * 58)

before_audit = {}
for label, field_names in AUDIT_FIELDS.items():
    populated = sum(1 for _, data in records
                    if any(has_val(data.get(fn)) for fn in field_names))
    blank = len(records) - populated
    pct   = populated / len(records) * 100 if records else 0
    before_audit[label] = populated
    print(f"{label:<25}  {populated:>10}  {blank:>8}  {pct:>8.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# PARSER DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# ── Currency type keywords (ordered most-specific first) ─────────────────────
TYPE_PATTERNS = [
    (r'\bCSA\b|\bConfederate\b',                             "Confederate"),
    (r'\bDemand\s+Note\b',                                   "Demand Note"),
    (r'\bInterest[\s-]Bearing\b',                            "Interest Bearing Note"),
    (r'\bRefunding\s+Cert',                                  "Refunding Certificate"),
    (r'\bCompound\s+Interest',                               "Compound Interest Note"),
    (r'\bTreasury\s+Note\b|\bCoin\s+Note\b',                "Treasury Note"),
    (r'\bGold\s+Cert',                                       "Gold Certificate"),
    (r'\bSilver\s+Cert',                                     "Silver Certificate"),
    (r'\bNational\s+Bank\b|\bNBN\b',                         "National Bank Note"),
    (r'\bFederal\s+Reserve\s+Bank\s+Note\b|\bFRBN\b',       "Federal Reserve Bank Note"),
    (r'\bFederal\s+Reserve\s+Note\b|\bFRN\b',               "Federal Reserve Note"),
    (r'\bFederal\s+Reserve\b',                               "Federal Reserve Note"),
    (r'\bFractional\b',                                      "Fractional Currency"),
    (r'\bLegal\s+Tender\b|\bUnited\s+States\s+Note\b',      "Legal Tender Note"),
    (r'\bEducational\b',                                     "Silver Certificate"),
    (r'\bBlack\s+Eagle\b',                                   "Silver Certificate"),
    (r'\bPorthole\b',                                        "Silver Certificate"),
    (r'\bMartha\s+Washington\b',                             "Silver Certificate"),
    (r'\bMilitary\s+Payment\b',                              "Military Payment Certificate"),
    (r'\bObsolete\b',                                        "Obsolete Currency"),
    (r'\bBank\s+Note\b',                                     "Bank Note"),
]

# ── Denomination ─────────────────────────────────────────────────────────────
DENOM_PATTERNS = [
    r'\$\s*(\d+(?:\.\d+)?)',
    r'\b(One|Two|Three|Four|Five|Ten|Twenty|Fifty|One\s+Hundred|Five\s+Hundred|'
    r'One\s+Thousand|Five\s+Thousand|Ten\s+Thousand|One\s+Hundred\s+Thousand|'
    r'Five\s+Cents|Ten\s+Cents|Fifteen\s+Cents|Twenty(?:-|\s)Five\s+Cents|'
    r'Fifty\s+Cents|Half)\s+(?:Dollar|Dollars|Cent|Cents|Dollar\s+Bill|Dollar\s+Note)\b',
    r'\b(\d+)\s+[Cc]ents?\b',
    r'\b(\d+)[Cc]\b',
    r'(½|1/2)\s+Dollar',
    # e.g. "25C Fractional Currency"
    r'^(\d+)C\b',
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

# ── Year patterns ────────────────────────────────────────────────────────────
# Valid US currency years: 1861–2026
# Also catches "1934A", "1963B" patterns
YEAR_RE = re.compile(
    r'(?<!\d)'
    r'(186[1-9]|18[7-9]\d|19\d{2}|20[01]\d|202[0-6])'
    r'\s*([A-Ha-h])?'
    r'(?!\d)',
    re.IGNORECASE,
)
SERIES_PREFIX_RE = re.compile(
    r'\bSeries\s+(186[1-9]|18[7-9]\d|19\d{2}|20[01]\d|202[0-6])\s*([A-Ha-h])?\b',
    re.IGNORECASE,
)

# ── Friedberg number ─────────────────────────────────────────────────────────
# Handles:
#   Fr. 1504   Fr.1504   Fr 1504   Friedberg 1504   F-1504
#   (FR237)   FR237   (FR-237)
FR_RE = re.compile(
    r'(?:'
    r'\b(?:Friedberg|Fr)\.?\s*(\d{1,4}[A-Za-z]?)\b'      # Fr. 1504 / Friedberg 237
    r'|'
    r'\(?\bFR-?(\d{1,4}[A-Za-z]?)\b\)?'                   # (FR237) / FR-237
    r'|'
    r'\bF-(\d{1,4}[A-Za-z]?)\b'                           # F-1504
    r')',
    re.IGNORECASE,
)

# ── Federal Reserve Banks ────────────────────────────────────────────────────
FRB_CITIES = [
    "Boston", "New York", "Philadelphia", "Cleveland", "Richmond",
    "Atlanta", "Chicago", "St. Louis", "Minneapolis", "Kansas City",
    "Dallas", "San Francisco",
]
FRB_RE = re.compile(
    r'Federal\s+Reserve\s+Bank\s+of\s+(' + '|'.join(re.escape(c) for c in FRB_CITIES) + r')',
    re.IGNORECASE,
)

# ── Confederate series ───────────────────────────────────────────────────────
CONF_SERIES_RE = re.compile(r'\b(?:CSA\s+)?T-?(\d{1,3})\b', re.IGNORECASE)

# ── Grade / Condition ────────────────────────────────────────────────────────
GRADE_PATTERNS = [
    re.compile(r'\b(PMG|PCGS)\s+(\d{1,2}(?:\s*(?:EPQ|PPQ))?)\b', re.IGNORECASE),
    re.compile(r'\b(VF|EF|XF|AU|UNC|MS|F|VG|G|AG|FR|PO|CU)\s*[-–]?\s*(\d{2})\b', re.IGNORECASE),
    re.compile(
        r'\b(Choice\s+Uncirculated|Gem\s+Uncirculated|About\s+Uncirculated|'
        r'Extremely\s+Fine|Very\s+Fine|Fine|Very\s+Good|Good|Fair|'
        r'Uncirculated|Circulated|Extra\s+Fine)\b',
        re.IGNORECASE,
    ),
]


def normalize_denom(raw: str) -> str:
    raw = raw.strip()
    m = re.match(r'^\$\s*(\d+(?:\.\d+)?)$', raw)
    if m:
        v = float(m.group(1))
        return f"${int(v) if v == int(v) else v}"
    lower = raw.lower().strip(".")
    if lower in WORD_TO_DENOM:
        return WORD_TO_DENOM[lower]
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
    """Extract all parseable fields from a currency description string."""
    empty = dict(
        denomination_parsed="", series_year_parsed="", year_parsed="",
        suffix_parsed="", type_parsed="", issuer_parsed="",
        friedberg_number="", confederate_series="", grade_parsed="",
    )
    if not desc or not desc.strip():
        return empty

    desc_norm = " ".join(desc.split())   # collapse whitespace

    # ── type ─────────────────────────────────────────────────────────────────
    type_parsed = ""
    for pattern, label in TYPE_PATTERNS:
        if re.search(pattern, desc_norm, re.IGNORECASE):
            type_parsed = label
            break

    # ── issuer (FRB city) ─────────────────────────────────────────────────────
    issuer_parsed = ""
    m_frb = FRB_RE.search(desc_norm)
    if m_frb:
        issuer_parsed = f"Federal Reserve Bank of {m_frb.group(1).title()}"

    # ── denomination ─────────────────────────────────────────────────────────
    denomination_parsed = ""
    m = re.search(r'\$\s*(\d+(?:\.\d+)?)', desc_norm)
    if m:
        v = float(m.group(1))
        denomination_parsed = f"${int(v) if v == int(v) else v}"
    if not denomination_parsed:
        for pattern in DENOM_PATTERNS[1:]:
            m = re.search(pattern, desc_norm, re.IGNORECASE)
            if m:
                raw_match = m.group(1) if m.lastindex else m.group(0)
                denomination_parsed = normalize_denom(raw_match)
                if denomination_parsed:
                    break

    # ── year / series ─────────────────────────────────────────────────────────
    yr, suf = "", ""
    m_sp = SERIES_PREFIX_RE.search(desc_norm)
    if m_sp:
        yr  = m_sp.group(1)
        suf = (m_sp.group(2) or "").upper()
    else:
        matches = list(YEAR_RE.finditer(desc_norm))
        if matches:
            yr  = matches[0].group(1)
            suf = (matches[0].group(2) or "").upper()

    year_parsed        = yr
    suffix_parsed      = suf
    series_year_parsed = (yr + suf) if yr else ""

    # ── Friedberg number ──────────────────────────────────────────────────────
    friedberg_number = ""
    m_fr = FR_RE.search(desc_norm)
    if m_fr:
        fr_num = m_fr.group(1) or m_fr.group(2) or m_fr.group(3)
        if fr_num:
            friedberg_number = f"Fr. {fr_num}"

    # ── Confederate series ────────────────────────────────────────────────────
    confederate_series = ""
    m_conf = CONF_SERIES_RE.search(desc_norm)
    if m_conf:
        confederate_series = f"T-{m_conf.group(1)}"

    # ── Grade ─────────────────────────────────────────────────────────────────
    grade_parsed = ""
    for gp in GRADE_PATTERNS:
        m_g = gp.search(desc_norm)
        if m_g:
            grade_parsed = m_g.group(0).strip()
            break

    return dict(
        denomination_parsed=denomination_parsed,
        series_year_parsed=series_year_parsed,
        year_parsed=year_parsed,
        suffix_parsed=suffix_parsed,
        type_parsed=type_parsed,
        issuer_parsed=issuer_parsed,
        friedberg_number=friedberg_number,
        confederate_series=confederate_series,
        grade_parsed=grade_parsed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Parse all records — dry-run analysis
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3 — Parsing all 413 records (dry-run analysis)")
print("=" * 70)

results = []
for doc_id, data in records:
    desc   = str(data.get("Description") or "").strip()
    parsed = parse_description(desc)
    results.append(dict(doc_id=doc_id, description=desc, **parsed, _data=data))

# ── Count what would be newly written ────────────────────────────────────────
would_fill = {
    "Year":              0,
    "Friedberg_Number":  0,
    "Series/Issuer":     0,
    "Condition":         0,
    "currency_type_label": 0,
    "Denomination":      0,
}

for r in results:
    data = r["_data"]
    if has_val(r["year_parsed"])        and is_blank(data.get("Year")):
        would_fill["Year"] += 1
    if has_val(r["friedberg_number"])   and is_blank(data.get("Friedberg_Number")):
        would_fill["Friedberg_Number"] += 1
    if has_val(r["issuer_parsed"])      and is_blank(data.get("Series/Issuer")):
        would_fill["Series/Issuer"] += 1
    if has_val(r["grade_parsed"])       and is_blank(data.get("Condition")):
        would_fill["Condition"] += 1
    if has_val(r["type_parsed"])        and is_blank(data.get("currency_type_label")):
        would_fill["currency_type_label"] += 1
    if has_val(r["denomination_parsed"])and is_blank(data.get("Denomination")):
        would_fill["Denomination"] += 1

print(f"\n{'Field':<25}  {'Would fill':>12}")
print("-" * 40)
for field, cnt in would_fill.items():
    print(f"{field:<25}  {cnt:>12}")

# ── Sample of 10 before/after ────────────────────────────────────────────────
print("\n--- Sample of 10 records: BEFORE → AFTER ---")
# Show a mix: some with Friedberg, some with issuer, some blank year
sample_fr   = [r for r in results if has_val(r["friedberg_number"])][:3]
sample_iss  = [r for r in results if has_val(r["issuer_parsed"])][:3]
sample_yr   = [r for r in results if has_val(r["year_parsed"])
               and is_blank(r["_data"].get("Year"))][:2]
sample_rest = [r for r in results if not has_val(r["friedberg_number"])
               and not has_val(r["issuer_parsed"])][:2]
samples = (sample_fr + sample_iss + sample_yr + sample_rest)[:10]

for r in samples:
    data = r["_data"]
    yr_before  = data.get("Year")  or "(blank)"
    fr_before  = data.get("Friedberg_Number") or "(blank)"
    iss_before = data.get("Series/Issuer") or "(blank)"
    den_before = data.get("Denomination") or "(blank)"
    print(f"\n  DOC  : {r['doc_id'][:24]}")
    print(f"  DESC : {r['description'][:90]}")
    print(f"  BEFORE → Year:{yr_before!r:12}  Fr#:{fr_before!r:12}  Issuer:{iss_before!r:30}  Denom:{den_before!r}")
    yr_after  = r["series_year_parsed"] or "(no match)"
    fr_after  = r["friedberg_number"]   or "(no match)"
    iss_after = r["issuer_parsed"]      or "(no match)"
    den_after = r["denomination_parsed"] or "(no match)"
    print(f"  AFTER  → Year:{yr_after!r:12}  Fr#:{fr_after!r:12}  Issuer:{iss_after!r:30}  Denom:{den_after!r}")

# ── Descriptions with NO parseable data ──────────────────────────────────────
unparsed = [r["description"] for r in results
            if not any(has_val(r[k]) for k in
                       ["year_parsed","denomination_parsed","type_parsed",
                        "friedberg_number","issuer_parsed"])
            and has_val(r["description"])]
print(f"\n--- Descriptions with NO fields parsed ({len(unparsed)}) ---")
for d in unparsed:
    print(f"  {d[:100]}")

# ── Show blank-Year docs and what we CAN fill ─────────────────────────────────
print("\n--- 15 blank-Year docs and parsed year result ---")
for r in results:
    if is_blank(r["_data"].get("Year")):
        yr = r["series_year_parsed"] or "(no match)"
        print(f"  {r['doc_id'][:24]}  yr_parsed={yr!r:12}  desc={r['description'][:70]!r}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Live write
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 4 — Live Firestore write (blank fields only)")
print("=" * 70)

# Proceed if ANY useful data to write
total_would_fill = sum(would_fill.values())
print(f"\n  Total field-fills available: {total_would_fill}")

if total_would_fill == 0:
    print("  Nothing to write. Skipping.")
    SKIP_WRITE = True
else:
    print(f"  Proceeding with live write …\n")
    SKIP_WRITE = False

# Mapping: (parsed_key, firestore_field, existing_keys_to_check)
FIELD_MAP = [
    ("denomination_parsed", "Denomination",        ["Denomination"]),
    ("series_year_parsed",  "Series",              ["Series"]),
    ("year_parsed",         "Year",                ["Year"]),
    ("type_parsed",         "currency_type_label", ["currency_type_label"]),
    ("issuer_parsed",       "Series/Issuer",       ["Series/Issuer"]),
    ("friedberg_number",    "Friedberg_Number",    ["Friedberg_Number"]),
    ("confederate_series",  "Confederate_Series",  ["Confederate_Series"]),
    ("grade_parsed",        "Condition",           ["Condition"]),
]

if not SKIP_WRITE:
    n_updated   = 0
    n_no_change = 0
    errors      = []

    for r in results:
        doc_id      = r["doc_id"]
        data        = r["_data"]
        update_dict = {}

        for parsed_key, fs_field, existing_keys in FIELD_MAP:
            new_val = r.get(parsed_key, "")
            if not has_val(new_val):
                continue
            if not doc_has(data, *existing_keys):
                update_dict[fs_field] = new_val

        if not update_dict:
            n_no_change += 1
            continue

        try:
            db.collection(COLLECTION).document(doc_id).update(update_dict)
            n_updated += 1
            if n_updated <= 15:
                print(f"  Updated {doc_id[:24]}: {list(update_dict.keys())}")
        except Exception as e:
            errors.append((doc_id, str(e)))

    print(f"\n  Documents updated    : {n_updated}")
    print(f"  Documents unchanged  : {n_no_change}")
    if errors:
        print(f"  Errors               : {len(errors)}")
        for eid, emsg in errors[:5]:
            print(f"    {eid}: {emsg}")
    print("\n  ✓ Firestore write complete.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Post-write coverage audit
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 5 — Post-write coverage audit (AFTER)")
print("=" * 70)

if not SKIP_WRITE:
    print("  Re-reading Firestore …")
    raw_docs2 = list(db.collection(COLLECTION).stream())
    records2  = [(d.id, d.to_dict() or {}) for d in raw_docs2]
else:
    records2 = records

print(f"\n{'Field':<25}  {'Before':>8}  {'After':>8}  {'Gain':>6}")
print("-" * 55)
for label, field_names in AUDIT_FIELDS.items():
    after_count = sum(1 for _, data in records2
                      if any(has_val(data.get(fn)) for fn in field_names))
    gain = after_count - before_audit[label]
    print(f"{label:<25}  {before_audit[label]:>8}  {after_count:>8}  {gain:>+6}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Save CSV
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"STEP 6 — Saving CSV → {CSV_OUT}")
print("=" * 70)

CSV_FIELDS = [
    "doc_id", "description",
    "year_parsed", "suffix_parsed", "denomination_parsed",
    "type_parsed", "friedberg_number", "confederate_series",
    "issuer_parsed", "grade_parsed",
]

with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for r in results:
        writer.writerow({k: r.get(k, "") for k in CSV_FIELDS})

print(f"  → {len(results)} rows written to {CSV_OUT}")

print("\n" + "=" * 70)
print("Done.")
print("=" * 70)
