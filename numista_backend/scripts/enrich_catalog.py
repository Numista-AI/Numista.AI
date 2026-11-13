"""Phase 2 catalog enrichment script for numista_coins.db.

Safely promotes eligible un-enriched `coins` rows into `definitive_reference`
without deleting any rows from either table. Defaults to --dry-run and --scope us-only.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent
_REPO_ROOT = _BACKEND_DIR.parent
for _p in (str(_REPO_ROOT), str(_BACKEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from services.mint_helpers import resolve_two_field_mint

# Paths are relative to the script's own location so the utility works regardless of CWD.
DB_PATH = str(_BACKEND_DIR / "database" / "numista_coins.db")
BACKUP_DIR = str(_BACKEND_DIR / "database" / "backups")

US_TERRITORIES = {
    "Philippines",
    "Puerto Rico",
    "Hawaii",
    "Panama Canal Zone",
    "Danish West Indies",
    "Guam",
}

YEAR_RE = re.compile(r"\b(1[7-9]\d{2}|20[0-2]\d|2030)\b")

# Mainland US mint marks per mint_helpers.py:167-184 (CC, D, S, P, W, O, C).
# 'M' (Manila Mint) is excluded for mainland US coins and allowed only for Philippines issues.
# Requires an explicit hyphen (e.g. '1921-S') or parentheses (e.g. '1921 (P)') and
# negative lookahead (?![.\w]) so initials like '1839 W. Scott' never match.
US_MINT_RE = re.compile(
    r"\b(1[7-9]\d{2}|20[0-2]\d|2030)(?:-(CC|D|S|P|W|O|C)|\s+\((CC|D|S|P|W|O|C)\))(?![.\w])"
)
PHILIPPINES_MINT_RE = re.compile(
    r"\b(1[7-9]\d{2}|20[0-2]\d|2030)(?:-(CC|D|S|P|W|O|C|M)|\s+\((CC|D|S|P|W|O|C|M)\))(?![.\w])"
)

NON_COIN_TITLE_RE = re.compile(
    r"\b(token|hard\s+times|civil\s+war|counterstamp|counterstamped|overstruck|medal|exonumia|pattern|play\s+money)\b",
    re.IGNORECASE,
)
NON_COIN_CATEGORIES = {
    "token",
    "tokens",
    "medal",
    "medals",
    "exonumia",
    "banknote",
    "banknotes",
    "paper money",
    "currency",
    "world_items",
}


def get_issuer_bucket(issuer: str) -> str:
    if issuer == "United States":
        return "United States"
    if issuer in US_TERRITORIES:
        return "US Territory"
    return "Foreign / Other"


def is_excluded_non_coin(title: str, category: str = "") -> bool:
    """Return True if the candidate row is a token, medal, counterstamp, overstrike, or non-coin category."""
    cat_clean = (category or "").strip().lower()
    if cat_clean in NON_COIN_CATEGORIES:
        return True
    if NON_COIN_TITLE_RE.search(title or ""):
        return True
    return False


def parse_year_and_mint(title: str, issuer: str = "United States") -> tuple[str, str]:
    """Extract (year, raw_mint_mark) using strict hyphenated or parenthesized syntax."""
    is_philippines = (issuer or "").strip().lower() == "philippines"
    pattern = PHILIPPINES_MINT_RE if is_philippines else US_MINT_RE
    mint_match = pattern.search(title or "")
    if mint_match:
        year = mint_match.group(1)
        mark = mint_match.group(2) or mint_match.group(3) or ""
        return year, mark
    year_match = YEAR_RE.search(title or "")
    if year_match:
        return year_match.group(1), ""
    return "", ""


def backup_database(db_path: str, backup_dir: str) -> str:
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = os.path.join(backup_dir, f"numista_coins_{ts}.db.bak")
    shutil.copy2(db_path, bak_path)
    return bak_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich definitive_reference from coins.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview changes without writing (default).")
    mode.add_argument("--execute", action="store_true", help="Backup DB and commit promotions.")
    parser.add_argument(
        "--scope",
        choices=["us-only", "all"],
        default="us-only",
        help="Scope of coins to promote (default: us-only).",
    )
    args = parser.parse_args()
    execute = args.execute

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    existing_doc_ids = {
        r[0] for r in cur.execute("SELECT doc_id FROM definitive_reference WHERE doc_id IS NOT NULL").fetchall()
    }
    existing_tuples = {
        (
            (r[0] or "").strip(),
            (r[1] or "").strip().lower(),
            (r[2] or "").strip().upper(),
            (r[3] or "").strip().lower(),
            (r[4] or "").strip().lower(),
        )
        for r in cur.execute(
            "SELECT year, denomination, mint_mark, variety, series FROM definitive_reference"
        ).fetchall()
    }

    candidates = cur.execute(
        "SELECT id, title, issuer, value, composition, category FROM coins"
    ).fetchall()

    to_insert = []
    skipped_scope = 0
    skipped_non_coin = 0
    skipped_doc_id = 0
    skipped_no_year = 0
    skipped_no_denom = 0
    skipped_dup_tuple = 0

    for cid, title, issuer, value, composition, category in candidates:
        title = (title or "").strip()
        issuer = (issuer or "").strip()
        if not title or not issuer:
            continue

        bucket = get_issuer_bucket(issuer)
        if args.scope == "us-only" and bucket not in ("United States", "US Territory"):
            skipped_scope += 1
            continue

        if is_excluded_non_coin(title, category):
            skipped_non_coin += 1
            continue

        doc_id = f"ref_coin_type_{cid}"
        if doc_id in existing_doc_ids:
            skipped_doc_id += 1
            continue

        year, raw_mint_mark = parse_year_and_mint(title, issuer=issuer)
        if not year:
            skipped_no_year += 1
            continue

        # Fix enrich_catalog.py:120,122 bug: never fall back from missing `value` to `category`
        denomination = (value or "").strip()
        if not denomination:
            skipped_no_denom += 1
            continue

        variety = title
        series = title
        # Resolve via Two-Field Mint helper; unpack `resolved_mm` into definitive_reference.mint_mark
        # (definitive_reference has 12 columns per load_definitive_catalog.py:779-793, storing mint_mark TEXT).
        _mint_facility, resolved_mm, _rule_id = resolve_two_field_mint(
            raw_mint_mark=raw_mint_mark,
            year=year,
            series=series,
            denomination=denomination,
            variety=variety,
            country=issuer,
        )
        # Preserve Philippines 'M' (Manila) when country='Philippines' since resolve_two_field_mint
        # treats Philippines as non-US Rule 11 and returns mm='M' uppercased.
        mint_mark = resolved_mm

        dedup_key = (year, denomination.lower(), mint_mark.upper(), variety.lower(), series.lower())
        if dedup_key in existing_tuples:
            skipped_dup_tuple += 1
            continue

        existing_tuples.add(dedup_key)
        to_insert.append(
            (
                year,
                denomination,
                mint_mark,
                variety,
                f"Promoted from coins.id={cid}",
                series,
                "coin",
                doc_id,
                "",
                "",
                (composition or "").strip(),
            )
        )

    print(f"Mode: {'EXECUTE' if execute else 'DRY-RUN'} | Scope: {args.scope}")
    print(f"Eligible rows to insert: {len(to_insert)}")
    print(
        f"Skipped -> scope: {skipped_scope}, non_coin: {skipped_non_coin}, "
        f"existing_doc_id: {skipped_doc_id}, no_parsable_year: {skipped_no_year}, "
        f"no_denomination: {skipped_no_denom}, duplicate_tuple: {skipped_dup_tuple}"
    )

    if execute and to_insert:
        bak_path = backup_database(DB_PATH, BACKUP_DIR)
        print(f"Backup created: {bak_path}")
        cur.executemany(
            """
            INSERT INTO definitive_reference (
                year, denomination, mint_mark, variety, note, series,
                category, doc_id, design_obverse, design_reverse, composition
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            to_insert,
        )
        conn.commit()
        print(f"Committed {len(to_insert)} rows into definitive_reference.")

    conn.close()


if __name__ == "__main__":
    main()
