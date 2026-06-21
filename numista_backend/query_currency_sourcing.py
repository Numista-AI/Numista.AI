"""
Query AJ's Firestore currency collection and produce a manual sourcing list.
Outputs:
  - CSV: AJ_Manual_Image_Sourcing_Currency.csv
  - Markdown: manual_sourcing_currency.md
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import csv
import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# ── Config ────────────────────────────────────────────────────────────────────
SERVICE_ACCOUNT = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
FIRESTORE_PATH  = "users/jseaman1204@gmail.com/currency"

CSV_OUT = r"C:\Users\ericd\Documents\MyVertexProject\AJ_Manual_Image_Sourcing_Currency.csv"
MD_OUT  = r"C:\Users\ericd\.gemini\antigravity\brain\26eebf0f-3c8f-47c1-940b-b41df002779f\manual_sourcing_currency.md"

# ── Target type labels ─────────────────────────────────────────────────────────
NATIONAL_BANK   = {"national bank note"}
CONFEDERATE     = {"confederate currency", "confederate", "csa"}
OBSOLETE        = {"obsolete currency", "obsolete", "broken bank note", "colonial"}
GOLD_CERT       = {"gold certificate"}
SILVER_CERT     = {"silver certificate"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get(doc: dict, *keys, default=""):
    """Try multiple field name variants and return the first match."""
    for k in keys:
        v = doc.get(k)
        if v is not None and str(v).strip() != "":
            return v
    return default

def classify(label: str):
    """Return category string for a type label."""
    l = label.strip().lower()
    if l in NATIONAL_BANK:   return "National Bank Note"
    if l in CONFEDERATE:     return "Confederate"
    if l in OBSOLETE:        return "Obsolete"
    if l in GOLD_CERT:       return "Gold Certificate"
    if l in SILVER_CERT:     return "Silver Certificate"
    if l == "":              return "Blank/Missing"
    return None  # not a target type

IMAGE_SOURCES = {
    "National Bank Note":  "Heritage Auctions / eBay photo search by bank name + year",
    "Confederate":         "Heritage Auctions / Newman Numismatic Portal by CSA type number",
    "Obsolete":            "Heritage Auctions / PCGS CoinFacts / eBay by state + bank name",
    "Gold Certificate":    "Heritage Auctions / Fr. number lookup",
    "Blank/Missing":       "Unknown — verify type first",
}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Init Firebase
    cred = credentials.Certificate(SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Load all docs
    col_ref = db.document(FIRESTORE_PATH.rsplit("/", 1)[0]).collection(
        FIRESTORE_PATH.rsplit("/", 1)[1]
    )
    # FIRESTORE_PATH is users/jseaman1204@gmail.com/currency  (parent doc + subcollection)
    # But it's actually a collection under a user doc:
    parts = FIRESTORE_PATH.split("/")
    # parts = ['users', 'jseaman1204@gmail.com', 'currency']
    col_ref = db.collection(parts[0]).document(parts[1]).collection(parts[2])

    print("Fetching all currency documents …")
    docs = list(col_ref.stream())
    print(f"  -> Retrieved {len(docs)} documents")

    # ── Buckets ───────────────────────────────────────────────────────────────
    buckets = {
        "National Bank Note":  [],
        "Confederate":         [],
        "Obsolete":            [],
        "Gold Certificate":    [],
        "Blank/Missing":       [],
        "Silver Certificate (no year)": [],
        "Silver Certificate":  [],   # all silver certs (for no-year filter)
    }

    all_rows = []  # for CSV

    for doc in docs:
        d   = doc.to_dict() or {}
        did = doc.id

        raw_label = str(get(d, "currency_type_label", default="")).strip()
        category  = classify(raw_label)

        year = str(get(d, "Year", "year", "DATE", "Date", default="")).strip()

        denom    = get(d, "denomination_parsed", "Denomination", "denomination", default="")
        desc     = get(d, "Description", "description", "desc", default="")
        friedberg= get(d, "Friedberg_Number", "friedberg_number", "Friedberg", "Fr.", "Fr", default="")
        grade    = get(d, "Grade", "grade", "Condition", "condition", default="")
        cost     = get(d, "Cost", "cost", "Purchase Cost", "purchase_cost", "Purchase_Cost", default="")
        series   = get(d, "Series", "series", default="")
        serial   = get(d, "Serial_Number", "serial_number", "Serial", "serial", default="")
        bank     = get(d, "Bank", "bank", "Issuing_Bank", "issuing_bank", "Bank_Name", default="")
        state    = get(d, "State", "state", default="")
        note_type= get(d, "Note_Type", "note_type", "Type", default="")

        row = {
            "doc_id":      did,
            "description": desc,
            "denomination":denom,
            "type":        raw_label,
            "year":        year,
            "friedberg":   friedberg,
            "grade":       grade,
            "cost":        cost,
            "series":      series,
            "serial":      serial,
            "bank":        bank,
            "state":       state,
            "note_type":   note_type,
            "category":    category or "Other",
        }

        # Silver Certificate with no year — special sub-list
        if raw_label.lower() == "silver certificate":
            buckets["Silver Certificate"].append(row)
            if not year:
                buckets["Silver Certificate (no year)"].append(row)

        # Primary target buckets
        if category and category != "Silver Certificate":
            buckets[category].append(row)
            all_rows.append(row)
        elif category == "Silver Certificate":
            pass  # tracked above, not in sourcing CSV
        else:
            pass  # "Other" — skip

        # Also include blank/missing in CSV
        if category in ("National Bank Note", "Confederate", "Obsolete",
                         "Gold Certificate", "Blank/Missing"):
            if row not in all_rows:
                all_rows.append(row)

    # ── Print summary to console ──────────────────────────────────────────────
    print("\n" + "="*70)
    print("SOURCING CATEGORIES — DOCUMENT COUNTS")
    print("="*70)
    for cat in ["National Bank Note", "Confederate", "Obsolete",
                "Gold Certificate", "Blank/Missing"]:
        print(f"  {cat:35s}: {len(buckets[cat]):>4d} docs")
    print(f"  {'Silver Certificate (no year)':35s}: {len(buckets['Silver Certificate (no year)']):>4d} docs")
    print(f"  {'Silver Certificate (all)':35s}: {len(buckets['Silver Certificate']):>4d} docs")
    total_target = sum(len(buckets[c]) for c in
                       ["National Bank Note","Confederate","Obsolete","Gold Certificate","Blank/Missing"])
    print(f"\n  {'TOTAL SOURCING ROWS':35s}: {total_target:>4d}")
    print("="*70)

    # ── Detailed print per bucket ─────────────────────────────────────────────
    for cat in ["National Bank Note", "Confederate", "Obsolete",
                "Gold Certificate", "Blank/Missing"]:
        items = buckets[cat]
        print(f"\n{'─'*70}")
        print(f"  {cat.upper()}  ({len(items)} items)")
        print(f"{'─'*70}")
        for r in items:
            print(f"  doc_id      : {r['doc_id']}")
            print(f"  Description : {r['description']}")
            print(f"  Denomination: {r['denomination']}")
            print(f"  Type Label  : {r['type']}")
            print(f"  Year        : {r['year']}")
            print(f"  Friedberg#  : {r['friedberg']}")
            print(f"  Grade       : {r['grade']}")
            print(f"  Cost        : {r['cost']}")
            if r['series']:   print(f"  Series      : {r['series']}")
            if r['serial']:   print(f"  Serial#     : {r['serial']}")
            if r['bank']:     print(f"  Bank        : {r['bank']}")
            if r['state']:    print(f"  State       : {r['state']}")
            if r['note_type']:print(f"  Note Type   : {r['note_type']}")
            print()

    print("\nSILVER CERTIFICATES WITH NO YEAR:")
    print("─"*70)
    for r in buckets["Silver Certificate (no year)"]:
        print(f"  {r['doc_id']} | {r['denomination']} | {r['description'][:60]}")

    print("\nALL GOLD CERTIFICATES:")
    print("─"*70)
    for r in buckets["Gold Certificate"]:
        print(f"  {r['doc_id']} | {r['year']} | {r['denomination']} | Fr.{r['friedberg']} | {r['grade']} | {r['description'][:60]}")

    # ── Write CSV ─────────────────────────────────────────────────────────────
    csv_cols = ["doc_id","description","denomination","type","year",
                "friedberg","grade","cost"]
    Path(CSV_OUT).parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\n[OK] CSV written -> {CSV_OUT}")

    # ── Write Markdown ────────────────────────────────────────────────────────
    Path(MD_OUT).parent.mkdir(parents=True, exist_ok=True)

    md_cats = ["National Bank Note", "Confederate", "Obsolete", "Gold Certificate"]

    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write("# AJ's Currency — Manual Image Sourcing List\n\n")
        f.write(f"_Generated from Firestore: `{FIRESTORE_PATH}` — {len(docs)} total docs_\n\n")
        f.write("---\n\n")

        for cat in md_cats:
            items = buckets[cat]
            img_src = IMAGE_SOURCES[cat]
            f.write(f"## {cat} ({len(items)} items)\n\n")
            if not items:
                f.write("_No items in this category._\n\n")
                f.write("---\n\n")
                continue

            f.write("| Year | Denomination | Description | Friedberg # | Grade | Where to Find Image |\n")
            f.write("|------|-------------|-------------|-------------|-------|---------------------|\n")
            for r in items:
                year_  = r["year"] or "—"
                denom_ = str(r["denomination"]).replace("|", "\\|") or "—"
                desc_  = str(r["description"])[:80].replace("|", "\\|").replace("\n", " ") or "—"
                fr_    = str(r["friedberg"]).replace("|", "\\|") or "—"
                grade_ = str(r["grade"]).replace("|", "\\|") or "—"
                f.write(f"| {year_} | {denom_} | {desc_} | {fr_} | {grade_} | {img_src} |\n")
            f.write("\n---\n\n")

        # Silver cert no-year appendix
        f.write(f"## Silver Certificates — Missing Year ({len(buckets['Silver Certificate (no year)'])} items)\n\n")
        if buckets["Silver Certificate (no year)"]:
            f.write("| doc_id | Denomination | Description | Grade | Cost |\n")
            f.write("|--------|-------------|-------------|-------|------|\n")
            for r in buckets["Silver Certificate (no year)"]:
                f.write(f"| {r['doc_id']} | {r['denomination'] or '—'} | {str(r['description'])[:70].replace('|','\\|')} | {r['grade'] or '—'} | {r['cost'] or '—'} |\n")
        else:
            f.write("_None found._\n")
        f.write("\n---\n\n")

        # Blank/missing appendix
        f.write(f"## Blank / Missing Type Label ({len(buckets['Blank/Missing'])} items)\n\n")
        if buckets["Blank/Missing"]:
            f.write("| doc_id | Year | Denomination | Description | Grade |\n")
            f.write("|--------|------|-------------|-------------|-------|\n")
            for r in buckets["Blank/Missing"]:
                f.write(f"| {r['doc_id']} | {r['year'] or '—'} | {r['denomination'] or '—'} | {str(r['description'])[:70].replace('|','\\|')} | {r['grade'] or '—'} |\n")
        else:
            f.write("_None found._\n")

    print(f"[OK] Markdown written -> {MD_OUT}")
    print("\nDone.")


if __name__ == "__main__":
    main()
