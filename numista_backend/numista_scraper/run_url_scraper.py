#!/usr/bin/env python3
"""
run_url_scraper.py
==================
CLI entry point for the URL-targeted coin ingestion engine.

Usage:
    python -m numista_scraper.run_url_scraper --url <url> [--dry-run]

Examples:
    # Dry-run: show what would happen, write nothing
    python -m numista_scraper.run_url_scraper \\
        --url "https://en.wikipedia.org/wiki/United_States_Semiquincentennial_coinage" \\
        --dry-run

    # Live run: create records, download images, update Firestore + SQLite
    python -m numista_scraper.run_url_scraper \\
        --url "https://en.wikipedia.org/wiki/United_States_Semiquincentennial_coinage"

    # US Mint product page (uses stored cookie for bypass)
    python -m numista_scraper.run_url_scraper \\
        --url "https://www.usmint.gov/coins/coin-programs/semiquincentennial/"
"""

import sys
import json
import argparse
import io
from pathlib import Path
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

# Add parent to path for direct invocation
sys.path.insert(0, str(Path(__file__).parent.parent))

from numista_scraper.url_scraper import scrape_url

LOG_FILE = Path(__file__).parent.parent / "url_scraper_log.json"


def main():
    parser = argparse.ArgumentParser(
        description="Ingest coin data and images from any URL into Firestore + SQLite."
    )
    parser.add_argument(
        "--url", required=True,
        help="URL to scrape (Wikipedia, US Mint, or any coin reference page)."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview all actions without writing anything to the database."
    )
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY-RUN MODE — nothing will be written to the database")
        print("=" * 60)

    results = scrape_url(args.url, dry_run=args.dry_run)

    # Save run log
    results["cli_args"] = {"url": args.url, "dry_run": args.dry_run}
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[LOG] Run log saved → {LOG_FILE}")

    if not args.dry_run and results.get("missing_images"):
        print(f"\n💡 TIP: Run manual_image_intake.py to ingest any images you have locally:")
        print(f"        .venv\\Scripts\\python.exe manual_image_intake.py --dry-run")


if __name__ == "__main__":
    main()
