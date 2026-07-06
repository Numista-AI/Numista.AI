# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
autofill_aj_denominations.py
──────────────────────────────────────────────────────────────────────────────
For AJ's coins that have a Program/Series but no Denomination, auto-fills the
denomination based on the program name using a lookup table.

Only touches records where Denomination is blank/null.
Does NOT touch records that already have a denomination.

Usage:
    python _scripts/autofill_aj_denominations.py --dry-run
    python _scripts/autofill_aj_denominations.py
"""

import os, sys, argparse
from datetime import datetime, timezone

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore

PROJECT      = "studio-9101802118-8c9a8"
TARGET_EMAIL = "jseaman1204@gmail.com"
BATCH_SIZE   = 400

# Program name → Denomination lookup (case-insensitive substring match)
PROGRAM_DENOM_MAP = [
    # Half Dollars
    ("franklin half",        "Half Dollar"),
    ("kennedy half",         "Half Dollar"),
    ("walking liberty",      "Half Dollar"),
    ("liberty walking",      "Half Dollar"),
    ("barber half",          "Half Dollar"),
    ("barber silver half",   "Half Dollar"),
    ("capped bust half",     "Half Dollar"),
    ("liberty seated half",  "Half Dollar"),
    ("seated half",          "Half Dollar"),
    ("20th century silver",  "Half Dollar"),   # some collection names
    ("silver half",          "Half Dollar"),
    # Dollars
    ("morgan",               "Dollar"),
    ("peace dollar",         "Dollar"),
    ("peace silver",         "Dollar"),
    ("american eagle silver","Dollar"),
    ("american eagle gold",  "Dollar"),
    (" ase ",                "Dollar"),     # ASE abbreviation
    ("ase t-",               "Dollar"),     # 2021 ASE Type 1/2 notation
    ("eisenhower",           "Dollar"),
    ("susan b anthony",      "Dollar"),
    ("sacagawea",            "Dollar"),
    ("native american dollar","Dollar"),
    ("presidential dollar",  "Dollar"),
    ("innovation dollar",    "Dollar"),
    ("liberty seated dollar","Dollar"),
    ("trade dollar",         "Dollar"),
    ("flowing hair dollar",  "Dollar"),
    ("gobrecht dollar",      "Dollar"),
    ("silver dollar",        "Dollar"),
    ("gold dollar",          "Dollar"),
    ("commemorative",        "Dollar"),     # most US commemoratives are dollars
    # Quarters
    ("state quarter",        "Quarter"),
    ("50 state",             "Quarter"),
    ("america the beautiful","Quarter"),
    ("national park quarter","Quarter"),
    ("american women quarter","Quarter"),
    ("women quarter",        "Quarter"),
    ("washington silver quarter","Quarter"),
    ("washington quarter",   "Quarter"),
    ("barber quarter",       "Quarter"),
    ("standing liberty",     "Quarter"),
    ("liberty seated quarter","Quarter"),
    ("capped bust quarter",  "Quarter"),
    # Dimes
    ("mercury dime",         "Dime"),
    ("barber dime",          "Dime"),
    ("roosevelt dime",       "Dime"),
    ("liberty seated dime",  "Dime"),
    ("seated dime",          "Dime"),
    ("capped bust dime",     "Dime"),
    ("silver dime",          "Dime"),
    # Nickels
    ("buffalo nickel",       "Nickel"),
    ("jefferson nickel",     "Nickel"),
    ("liberty nickel",       "Nickel"),
    ("shield nickel",        "Nickel"),
    ("jamul copper nickel",  "Nickel"),
    # Cents / Pennies
    ("lincoln cent",         "Penny"),
    ("lincoln head",         "Penny"),
    ("wheaties",             "Penny"),
    ("wheat",                "Penny"),
    ("indian head cent",     "Penny"),
    ("flying eagle",         "Penny"),
    ("braided hair large",   "Large Cent"),
    ("large cent",           "Large Cent"),
    ("coronet cent",         "Large Cent"),
    ("matron head",          "Large Cent"),
    # Half dimes
    ("half dime",            "Half Dime"),
    ("capped bust half dime","Half Dime"),
    ("liberty seated half dime","Half Dime"),
    # Half cents
    ("half cent",            "Half Cent"),
    ("classic head half",    "Half Cent"),
    ("braided hair half cent","Half Cent"),
    # Twenty cents
    ("twenty cent",          "20 Cents"),
    # Gold
    ("saint-gaudens",        "Gold Eagle ($20)"),
    ("st. gaudens",          "Gold Eagle ($20)"),
    ("saint gaudens",        "Gold Eagle ($20)"),
    ("gold eagle",           "Gold Eagle ($20)"),
    ("liberty head gold",    "Gold Coin"),
    ("american liberty",     "Gold Coin"),
]


def infer_denomination(program: str) -> str | None:
    p = program.lower()
    for keyword, denom in PROGRAM_DENOM_MAP:
        if keyword.lower() in p:
            return denom
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print("⚠️  DRY RUN\n")

    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)
    col_ref = db.collection("users").document(TARGET_EMAIL).collection("coins")

    print(f"Loading coins for {TARGET_EMAIL}...")
    coins = list(col_ref.stream())
    print(f"  {len(coins):,} loaded\n")

    batch      = db.batch()
    batch_ct   = 0
    filled     = 0
    skipped    = 0
    no_match   = 0
    no_match_programs = []

    for doc in coins:
        data = doc.to_dict() or {}
        denom   = str(data.get("Denomination", "") or "").strip()
        program = str(data.get("Program/Series", "") or "").strip()

        if denom:
            skipped += 1
            continue

        if not program:
            no_match += 1
            continue

        inferred = infer_denomination(program)
        if not inferred:
            no_match += 1
            no_match_programs.append(program)
            continue

        filled += 1
        print(f"  {program[:50]:<50} → {inferred}")

        if not args.dry_run:
            batch.update(col_ref.document(doc.id), {
                "Denomination":    inferred,
                "denom_auto_fill": True,
                "updated_at":      datetime.now(tz=timezone.utc),
            })
            batch_ct += 1
            if batch_ct >= BATCH_SIZE:
                batch.commit()
                batch = db.batch()
                batch_ct = 0

    if not args.dry_run and batch_ct > 0:
        batch.commit()

    print(f"\n{'DRY RUN ' if args.dry_run else ''}Results:")
    print(f"  Already had denomination : {skipped:,}")
    print(f"  Auto-filled              : {filled:,}")
    print(f"  No match (no program)    : {no_match:,}")

    if no_match_programs:
        unique = sorted(set(no_match_programs))
        print(f"\n  Programs with no denomination match ({len(unique)}):")
        for p in unique[:20]:
            print(f"    {p}")

    if not args.dry_run and filled > 0:
        print(f"\n  ✅  {filled} denominations auto-filled for {TARGET_EMAIL}")


if __name__ == "__main__":
    main()
