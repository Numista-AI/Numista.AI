"""
seed_littleton_skus.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Littleton Coin Company — Static SKU Seed Script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE:
    Populates the 'littleton_sku_dictionary' table in numista.db with a
    curated set of known Littleton Coin Company SKUs and their canonical
    Numista.AI Golden Schema mappings.

    This is a DEPLOY-TIME script — run it locally or in a Cloud Build step
    before publishing numista.db to GCS. The resulting SQLite file is the
    static Layer-1 lookup asset bundled into the container image.

WORKFLOW:
    1.  Edit KNOWN_LITTLETON_SKUS below to add confirmed mappings.
    2.  Run:  python seed_littleton_skus.py
    3.  The script writes to numista_backend/database/numista.db
    4.  Re-deploy the backend (Cloud Run will include the updated db file).

USAGE:
    python numista_backend/seed_littleton_skus.py
    (Run from the project root OR from inside numista_backend/)

NOTE:
    Do NOT run this against numista_coins.db — that file is the read-only
    reference catalog managed by load_definitive_catalog.py and overwritten
    during GCS catalog refresh cycles.
"""

import os
import sqlite3
import sys

# ─── Resolve path to numista.db ───────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_SCRIPT_DIR, "database", "numista.db")


# ─── Known static SKU mappings ────────────────────────────────────────────────
# Format per entry:
#   littleton_sku    : str  — Exact Littleton catalog SKU (will be stored UPPERCASE)
#   description      : str  — Human-readable product name for reference
#   canonical_ref_id : str  — Short normalized token (LCC-SERIES-YEAR-MINT-GRADE)
#   implied_condition: str  — Standard grade as sold by Littleton
#   program_series   : str  — Golden Schema "Program/Series" value
#   year             : str  — 4-digit year or "" for date-range / assorted sets
#   mint_mark        : str  — "P", "D", "S", "W", "CC", "O", or ""
#   denomination     : str  — "Dollar", "Half Dollar", "Quarter", "Dime", etc.
#   item_type        : str  — "coin" | "medal" | "paper_currency" | "supply"
#
# Add new rows here as SKUs are confirmed from AJ's scanned receipts.

KNOWN_LITTLETON_SKUS: list[dict] = [

    # ── Morgan Silver Dollars ─────────────────────────────────────────────────
    {
        "littleton_sku":     "ME-6100",
        "description":       "1921 Morgan Silver Dollar BU",
        "canonical_ref_id":  "LCC-MORGAN-1921-P-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Morgan Silver Dollar",
        "year":              "1921",
        "mint_mark":         "P",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "ME-6100D",
        "description":       "1921-D Morgan Silver Dollar BU",
        "canonical_ref_id":  "LCC-MORGAN-1921-D-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Morgan Silver Dollar",
        "year":              "1921",
        "mint_mark":         "D",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "ME-6100S",
        "description":       "1921-S Morgan Silver Dollar BU",
        "canonical_ref_id":  "LCC-MORGAN-1921-S-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Morgan Silver Dollar",
        "year":              "1921",
        "mint_mark":         "S",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Peace Dollars ─────────────────────────────────────────────────────────
    {
        "littleton_sku":     "ME-6110",
        "description":       "1922 Peace Silver Dollar BU",
        "canonical_ref_id":  "LCC-PEACE-1922-P-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Peace Dollar",
        "year":              "1922",
        "mint_mark":         "P",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "ME-6115",
        "description":       "1923 Peace Silver Dollar AU",
        "canonical_ref_id":  "LCC-PEACE-1923-P-AU",
        "implied_condition": "About Uncirculated",
        "program_series":    "Peace Dollar",
        "year":              "1923",
        "mint_mark":         "P",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Kennedy Half Dollars ──────────────────────────────────────────────────
    {
        "littleton_sku":     "CD-9950",
        "description":       "1964 Kennedy Half Dollar Proof",
        "canonical_ref_id":  "LCC-KENNEDY-1964-P-PROOF",
        "implied_condition": "Proof",
        "program_series":    "Kennedy Half Dollar",
        "year":              "1964",
        "mint_mark":         "P",
        "denomination":      "Half Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "CD-9952",
        "description":       "1964-D Kennedy Half Dollar BU",
        "canonical_ref_id":  "LCC-KENNEDY-1964-D-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Kennedy Half Dollar",
        "year":              "1964",
        "mint_mark":         "D",
        "denomination":      "Half Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "CD-9960",
        "description":       "Kennedy Half Dollar 40% Silver - Circulated Set (1965-1969)",
        "canonical_ref_id":  "LCC-KENNEDY-40PCT-CIRC-SET",
        "implied_condition": "Circulated",
        "program_series":    "Kennedy Half Dollar",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Half Dollar",
        "item_type":         "coin",
    },

    # ── Eisenhower Dollars ────────────────────────────────────────────────────
    {
        "littleton_sku":     "CD-1100",
        "description":       "Eisenhower Dollar - 1971-D BU",
        "canonical_ref_id":  "LCC-IKE-1971-D-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Eisenhower Dollar",
        "year":              "1971",
        "mint_mark":         "D",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "CD-1104S",
        "description":       "1971-S Eisenhower Silver Dollar Proof",
        "canonical_ref_id":  "LCC-IKE-1971-S-PROOF",
        "implied_condition": "Proof",
        "program_series":    "Eisenhower Dollar",
        "year":              "1971",
        "mint_mark":         "S",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Walking Liberty Half Dollars ──────────────────────────────────────────
    {
        "littleton_sku":     "ME-3200",
        "description":       "Walking Liberty Half Dollar Fine+",
        "canonical_ref_id":  "LCC-WALKER-CIRC-FINE",
        "implied_condition": "Fine",
        "program_series":    "Walking Liberty Half Dollar",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Half Dollar",
        "item_type":         "coin",
    },

    # ── Franklin Half Dollars ─────────────────────────────────────────────────
    {
        "littleton_sku":     "ME-3310",
        "description":       "Franklin Half Dollar BU",
        "canonical_ref_id":  "LCC-FRANKLIN-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Franklin Half Dollar",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Half Dollar",
        "item_type":         "coin",
    },

    # ── American Eagle Silver Dollars ─────────────────────────────────────────
    {
        "littleton_sku":     "ME-8500",
        "description":       "American Eagle Silver Dollar BU - 1 oz .999 Fine Silver",
        "canonical_ref_id":  "LCC-ASE-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "American Eagle Silver Dollar",
        "year":              "",
        "mint_mark":         "P",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "ME-8500W",
        "description":       "American Eagle Silver Dollar Proof - West Point",
        "canonical_ref_id":  "LCC-ASE-W-PROOF",
        "implied_condition": "Proof",
        "program_series":    "American Eagle Silver Dollar",
        "year":              "",
        "mint_mark":         "W",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Lincoln Cents ─────────────────────────────────────────────────────────
    {
        "littleton_sku":     "CD-0100",
        "description":       "Lincoln Wheat Cent BU - 1909-S",
        "canonical_ref_id":  "LCC-WHEAT-1909-S-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Lincoln Wheat Cent",
        "year":              "1909",
        "mint_mark":         "S",
        "denomination":      "Cent",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "CD-0105",
        "description":       "Lincoln Wheat Cents Fine - 10 Coin Assortment",
        "canonical_ref_id":  "LCC-WHEAT-ASSORTED-FINE",
        "implied_condition": "Fine",
        "program_series":    "Lincoln Wheat Cent",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Cent",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "CD-0200",
        "description":       "1943 Lincoln Steel Cent BU",
        "canonical_ref_id":  "LCC-STEEL-1943-P-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Lincoln Steel Cent",
        "year":              "1943",
        "mint_mark":         "P",
        "denomination":      "Cent",
        "item_type":         "coin",
    },

    # ── Buffalo Nickels ───────────────────────────────────────────────────────
    {
        "littleton_sku":     "ME-2100",
        "description":       "Buffalo Nickel Fine - Date Visible",
        "canonical_ref_id":  "LCC-BUFFALO-FINE-DATED",
        "implied_condition": "Fine",
        "program_series":    "Buffalo Nickel",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Nickel",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "ME-2105",
        "description":       "Buffalo Nickel Good - No Date",
        "canonical_ref_id":  "LCC-BUFFALO-GOOD-NODATE",
        "implied_condition": "Good",
        "program_series":    "Buffalo Nickel",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Nickel",
        "item_type":         "coin",
    },

    # ── Mercury Dimes ─────────────────────────────────────────────────────────
    {
        "littleton_sku":     "ME-4100",
        "description":       "Mercury Dime Fine",
        "canonical_ref_id":  "LCC-MERC-FINE",
        "implied_condition": "Fine",
        "program_series":    "Mercury Dime",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Dime",
        "item_type":         "coin",
    },
    {
        "littleton_sku":     "ME-4100BU",
        "description":       "Mercury Dime BU",
        "canonical_ref_id":  "LCC-MERC-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Mercury Dime",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Dime",
        "item_type":         "coin",
    },

    # ── Washington Quarters ───────────────────────────────────────────────────
    {
        "littleton_sku":     "CD-5100",
        "description":       "Washington Silver Quarter BU - 1964",
        "canonical_ref_id":  "LCC-WASH-1964-P-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Washington Quarter",
        "year":              "1964",
        "mint_mark":         "P",
        "denomination":      "Quarter",
        "item_type":         "coin",
    },

    # ── 50 State Quarters ─────────────────────────────────────────────────────
    {
        "littleton_sku":     "QC-5001",
        "description":       "50 State Quarters Complete Set BU - P&D 100 Coins",
        "canonical_ref_id":  "LCC-50STATE-COMPLETE-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "50 State Quarters Program",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Quarter",
        "item_type":         "coin",
    },

    # ── Presidential Dollars ──────────────────────────────────────────────────
    {
        "littleton_sku":     "DC-7700",
        "description":       "Presidential Dollar Complete Set BU - P&D",
        "canonical_ref_id":  "LCC-PRES-DOLLAR-COMPLETE-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Presidential $1 Coin Program",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Sacagawea / Native American Dollars ───────────────────────────────────
    {
        "littleton_sku":     "DC-7500",
        "description":       "2000-P Sacagawea Dollar BU",
        "canonical_ref_id":  "LCC-SAC-2000-P-BU",
        "implied_condition": "Uncirculated",
        "program_series":    "Sacagawea Dollar",
        "year":              "2000",
        "mint_mark":         "P",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Commemorative Coins ───────────────────────────────────────────────────
    {
        "littleton_sku":     "CO-9001",
        "description":       "Statue of Liberty Commemorative Silver Dollar Proof",
        "canonical_ref_id":  "LCC-COMMEM-SOL-1986-PROOF",
        "implied_condition": "Proof",
        "program_series":    "Commemorative",
        "year":              "1986",
        "mint_mark":         "S",
        "denomination":      "Dollar",
        "item_type":         "coin",
    },

    # ── Supplies ──────────────────────────────────────────────────────────────
    {
        "littleton_sku":     "LCF-2X2",
        "description":       "Littleton 2x2 Coin Holders - 100 Count",
        "canonical_ref_id":  "LCC-SUPPLY-2X2-100",
        "implied_condition": "",
        "program_series":    "",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "",
        "item_type":         "supply",
    },
    {
        "littleton_sku":     "LCF-ALBUM",
        "description":       "Littleton Coin Folder - US Type Coins",
        "canonical_ref_id":  "LCC-SUPPLY-FOLDER-TYPE",
        "implied_condition": "",
        "program_series":    "",
        "year":              "",
        "mint_mark":         "",
        "denomination":      "",
        "item_type":         "supply",
    },
]


# ─── Main seed runner ─────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Numista.AI — Littleton SKU Dictionary Seed Script")
    print("=" * 60)
    print(f"\nTarget database: {DB_PATH}")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        # Create table if not present (idempotent)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS littleton_sku_dictionary (
                littleton_sku     TEXT PRIMARY KEY,
                description       TEXT NOT NULL DEFAULT '',
                canonical_ref_id  TEXT NOT NULL DEFAULT '',
                implied_condition TEXT NOT NULL DEFAULT 'Uncirculated',
                program_series    TEXT NOT NULL DEFAULT '',
                year              TEXT NOT NULL DEFAULT '',
                mint_mark         TEXT NOT NULL DEFAULT '',
                denomination      TEXT NOT NULL DEFAULT '',
                item_type         TEXT NOT NULL DEFAULT 'coin'
            )
        """)
        conn.commit()
        print(f"  Table 'littleton_sku_dictionary' ready.")

        inserted = 0
        updated  = 0
        errors   = 0

        for entry in KNOWN_LITTLETON_SKUS:
            sku = str(entry.get("littleton_sku", "")).strip().upper()
            if not sku:
                print("  WARNING: Skipping entry with empty SKU.")
                errors += 1
                continue

            try:
                # Check if row exists
                cur = conn.cursor()
                cur.execute(
                    "SELECT littleton_sku FROM littleton_sku_dictionary WHERE littleton_sku = ?",
                    (sku,)
                )
                exists = cur.fetchone() is not None

                conn.execute(
                    """
                    INSERT OR REPLACE INTO littleton_sku_dictionary
                        (littleton_sku, description, canonical_ref_id, implied_condition,
                         program_series, year, mint_mark, denomination, item_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sku,
                        str(entry.get("description",       "") or ""),
                        str(entry.get("canonical_ref_id",  "") or ""),
                        str(entry.get("implied_condition",  "Uncirculated") or "Uncirculated"),
                        str(entry.get("program_series",    "") or ""),
                        str(entry.get("year",              "") or ""),
                        str(entry.get("mint_mark",         "") or ""),
                        str(entry.get("denomination",      "") or ""),
                        str(entry.get("item_type",         "coin") or "coin"),
                    )
                )
                if exists:
                    updated += 1
                    print(f"  UPDATED  {sku}")
                else:
                    inserted += 1
                    print(f"  INSERTED {sku}")

            except Exception as exc:
                print(f"  ERROR    {sku}: {exc}")
                errors += 1

        conn.commit()

        # Final report
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM littleton_sku_dictionary")
        total = cur.fetchone()[0]

        print("\n" + "=" * 60)
        print(f"  Seed complete: {inserted} inserted, {updated} updated, {errors} errors")
        print(f"  Total rows in littleton_sku_dictionary: {total}")
        print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
