"""
Remediate Fake $0.50 Valuations
================================
One-time migration script that finds and fixes all coins with the
hardcoded $0.50 fake valuation.

For each affected coin:
  1. Try Greysheet lookup (fresh, no timeout pressure)
  2. Try US Mint Issue Price match
  3. If neither → set to Pending (null estimated_value)

Usage:
    python remediate_fake_valuations.py [--dry-run] [--user EMAIL]
"""

import os
import re
import sys
import logging
from datetime import datetime, timezone

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_DIR)

from google.cloud import firestore

PROJECT_ID = "studio-9101802118-8c9a8"

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("remediate")


def main():
    dry_run = "--dry-run" in sys.argv
    target_user = None
    for i, arg in enumerate(sys.argv):
        if arg == "--user" and i + 1 < len(sys.argv):
            target_user = sys.argv[i + 1]

    print(f"{'[DRY RUN] ' if dry_run else ''}Remediating fake $0.50 valuations...")

    db = firestore.Client(project=PROJECT_ID)

    # Get all users, or specific user
    if target_user:
        user_refs = [db.collection("users").document(target_user)]
        print(f"  Targeting user: {target_user}")
    else:
        user_refs = list(db.collection("users").stream())
        print(f"  Scanning {len(user_refs)} users...")

    # Try to import services
    try:
        from services.greysheet_service import GreysheetService
        gs_service = GreysheetService(db=db)
        has_greysheet = True
    except Exception as e:
        logger.warning(f"Greysheet service unavailable: {e}")
        gs_service = None
        has_greysheet = False

    try:
        from services.usmint_releases_scraper import get_mint_issue_price
        has_mint_price = True
    except Exception as e:
        logger.warning(f"US Mint price lookup unavailable: {e}")
        has_mint_price = False

    stats = {
        "total_scanned": 0,
        "fake_050_found": 0,
        "fixed_greysheet": 0,
        "fixed_mint_price": 0,
        "set_to_pending": 0,
        "errors": 0,
    }

    for user_ref in user_refs:
        if hasattr(user_ref, "id"):
            user_email = user_ref.id
        else:
            user_email = user_ref.path.split("/")[-1]

        coins_ref = db.collection("users").document(user_email).collection("coins")
        coins = list(coins_ref.stream())

        for coin_doc in coins:
            stats["total_scanned"] += 1
            data = coin_doc.to_dict() or {}

            # Check if this coin has the fake $0.50 valuation
            est_value = data.get("estimated_value")
            ai_val_str = data.get("AI Estimated Value", "")
            val_source = data.get("valuation_source", "")

            is_fake = (
                (est_value == 0.5 or est_value == 0.50) and
                val_source != "Greysheet Production API"
            ) or ai_val_str == "$0.50"

            if not is_fake:
                continue

            stats["fake_050_found"] += 1
            year = data.get("Year", "")
            denom = data.get("Denomination", "")
            mint_mark = data.get("Mint Mark", "")
            series = data.get("Program/Series", "")
            theme = data.get("Theme/Subject", "")

            coin_desc = f"{year} {denom} {mint_mark} ({coin_doc.id})"

            # 1. Try Greysheet (no timeout pressure)
            new_value = None
            new_source = None
            new_status = "pending"

            if has_greysheet and gs_service:
                try:
                    res = gs_service.resolve_coin_with_timeout(
                        year=year,
                        denom=denom,
                        series=series,
                        subject=theme,
                        mint=mint_mark,
                        timeout_ms=5000,  # More generous timeout
                    )
                    if res and res.get("gsid"):
                        cpg_val = res.get("cpg_retail") or res.get("ask")
                        if cpg_val and float(cpg_val) > 0:
                            new_value = float(cpg_val)
                            new_source = "Greysheet Production API (Remediation)"
                            new_status = "valued"
                            stats["fixed_greysheet"] += 1
                except Exception as e:
                    logger.debug(f"  Greysheet lookup failed for {coin_desc}: {e}")

            # 2. Try US Mint Issue Price
            if new_value is None and has_mint_price:
                try:
                    mint_price = get_mint_issue_price(
                        db=db,
                        year=year,
                        denomination=denom,
                        mint_mark=mint_mark,
                        theme=theme,
                    )
                    if mint_price and mint_price > 0:
                        new_value = mint_price
                        new_source = "US Mint Issue Price (Remediation)"
                        new_status = "valued"
                        stats["fixed_mint_price"] += 1
                except Exception as e:
                    logger.debug(f"  Mint price lookup failed for {coin_desc}: {e}")

            # 3. Set to Pending
            if new_value is None:
                stats["set_to_pending"] += 1

            # Build update payload
            update = {
                "estimated_value": new_value,
                "AI Estimated Value": f"${new_value:.2f}" if new_value else "Pending",
                "ai_value_status": new_status,
                "valuation_source": new_source or "Awaiting Valuation",
                "valuation_updated_at": datetime.now(timezone.utc).isoformat(),
            }

            if dry_run:
                action = "GREYSHEET" if new_source and "Greysheet" in new_source else \
                         "MINT_PRICE" if new_source and "Mint" in new_source else \
                         "PENDING"
                val_display = f"${new_value:.2f}" if new_value else "Pending"
                print(f"  [{action}] {coin_desc}: $0.50 → {val_display}")
            else:
                try:
                    coins_ref.document(coin_doc.id).update(update)
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"  Failed to update {coin_desc}: {e}")

    # Print summary
    print(f"\n{'═' * 60}")
    print(f"{'[DRY RUN] ' if dry_run else ''}REMEDIATION COMPLETE")
    print(f"{'═' * 60}")
    print(f"  Total coins scanned:    {stats['total_scanned']}")
    print(f"  Fake $0.50 found:       {stats['fake_050_found']}")
    print(f"  Fixed via Greysheet:    {stats['fixed_greysheet']}")
    print(f"  Fixed via Mint Price:   {stats['fixed_mint_price']}")
    print(f"  Set to Pending:         {stats['set_to_pending']}")
    print(f"  Errors:                 {stats['errors']}")
    print(f"{'═' * 60}")


if __name__ == "__main__":
    main()
