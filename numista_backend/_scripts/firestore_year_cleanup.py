"""
firestore_year_cleanup.py
─────────────────────────────────────────────────────────────────────────────
Scans all coin documents for eric@numista.ai and attempts to extract
missing Year and Mint Mark data from Condition / Personal Notes / fields.

Firestore field names (Title Case with spaces):
  Year, Mint Mark, Condition, Personal Notes, Program/Series, Denomination

Run with --dry-run first to preview all proposed changes.
Run without --dry-run to write changes to Firestore.

Usage:
    python _scripts/firestore_year_cleanup.py --dry-run
    python _scripts/firestore_year_cleanup.py
"""

import os, re, sys, json, argparse
from datetime import datetime

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore

PROJECT    = "studio-9101802118-8c9a8"
USER_DOC   = "eric@numista.ai"

# ── Extraction patterns ───────────────────────────────────────────────────────

YEAR_RE = re.compile(r"\b(1[789]\d{2}|20[012]\d)\b")
# Matches: "1891CC", "1921-D", "1879 O", "(CC)", "Mint: S" etc.
MINT_RE = re.compile(
    r"(?:^|[-\s(])([PDSWpdswOo]|CC|cc)(?:[-\s)]|$)|"
    r"\b(1[789]\d{2}|20[012]\d)[-\s]*(CC|O|S|W|D|P)\b",
    re.I,
)

def extract_from_text(text):
    """Return (year_str, mint_str) or (None, None)."""
    if not text:
        return None, None

    # Combined: year immediately adjacent to mint (1891CC, 1921-D, 1879O)
    m = re.search(r"\b(1[789]\d{2}|20[012]\d)[-\s]*(CC|O|S|W|D|P)\b", text, re.I)
    if m:
        return m.group(1), m.group(2).upper()

    # Year alone
    m = YEAR_RE.search(text)
    if m:
        year = m.group(0)
        # look for a mint mark within 8 chars of the year
        ctx   = text[max(0, m.start()-8) : m.end()+8]
        mm    = re.search(r"\b(CC|O|S|W|D|P)\b", ctx, re.I)
        mint  = mm.group(1).upper() if mm else None
        return year, mint

    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--user",    default=USER_DOC)
    args = ap.parse_args()

    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)

    coins_ref = db.collection("users").document(args.user).collection("coins")
    all_coins = list(coins_ref.stream())
    print(f"Loaded {len(all_coins)} coins for {args.user}\n")

    proposed       = []
    already_year   = 0
    no_year_found  = []

    for coin_doc in all_coins:
        data = coin_doc.to_dict() or {}

        current_year = str(data.get("Year", "") or "").strip()
        current_mint = str(data.get("Mint Mark", "") or "").strip()

        # Already has a valid year
        if current_year and current_year not in ("None", "null", "0", "Unknown", ""):
            already_year += 1
            continue

        # Mine text fields in priority order
        fields_to_check = [
            data.get("Condition", ""),
            data.get("Personal Notes", ""),
            data.get("Theme/Subject", ""),
            data.get("Denomination", ""),
            data.get("Program/Series", ""),
        ]
        combined = " ".join(str(f) for f in fields_to_check if f)

        year_found, mint_found = extract_from_text(combined)

        if not year_found:
            no_year_found.append({
                "id":      coin_doc.id,
                "program": data.get("Program/Series", "?"),
                "cond":    str(data.get("Condition", ""))[:80],
                "notes":   str(data.get("Personal Notes", ""))[:80],
            })
            continue

        proposed.append({
            "doc_ref": coin_doc.reference,
            "doc_id":  coin_doc.id,
            "year":    year_found,
            "mint":    mint_found or current_mint,
            "program": data.get("Program/Series", "?"),
            "source":  combined[:90],
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"{'=' * 65}")
    print(f"  Already have Year          : {already_year}")
    print(f"  Year extracted from text   : {len(proposed)}")
    print(f"  No year found anywhere     : {len(no_year_found)}")
    print(f"{'=' * 65}\n")

    if no_year_found:
        print("--- COINS WITH NO YEAR FOUND (manual review needed) ---")
        for c in no_year_found:
            print(f"  {c['id'][:30]}  program={c['program']}")
            if c["cond"]:
                print(f"    Condition: {c['cond']}")
            if c["notes"]:
                print(f"    Notes:     {c['notes']}")
        print()

    if proposed:
        print("--- PROPOSED YEAR UPDATES ---")
        for p in proposed:
            mint_str = f"  MintMark={p['mint']}" if p["mint"] else ""
            print(f"  {p['doc_id'][:30]}  Year={p['year']}{mint_str}")
            print(f"    [{p['program']}] from: \"{p['source'][:70]}\"")
        print()

    if args.dry_run:
        print(f"[DRY RUN] {len(proposed)} records would be updated. Re-run without --dry-run to apply.")
        return

    if not proposed:
        print("Nothing to update.")
        return

    print(f"Writing {len(proposed)} updates to Firestore...")
    batch   = db.batch()
    n       = 0
    updated = []
    for p in proposed:
        update = {
            "Year": p["year"],
            "_year_auto_extracted":  True,
            "_year_extracted_from":  p["source"][:120],
            "_year_extracted_at":    datetime.now().isoformat(),
        }
        if p["mint"]:
            update["Mint Mark"] = p["mint"]
        batch.update(p["doc_ref"], update)
        n += 1
        updated.append(p)
        if n % 400 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()

    print(f"Done. Updated {n} coin records:")
    for p in updated:
        print(f"  {p['doc_id'][:30]}  Year={p['year']}")

if __name__ == "__main__":
    main()
