#!/usr/bin/env python3
"""
Phase 1A: Batch Greysheet resolve + refresh for grokbot@numista.ai.

Calls the deployed Cloud Run API for each coin:
  1. POST /api/greysheet/resolve  (assigns GSID)
  2. POST /api/greysheet/refresh  (fetches live pricing)

Rate-limited: 25 coins per batch, 500ms delay between calls.
Dry-run by default.

Usage:
  python batch_greysheet_grokbot.py                # dry-run: list coins
  python batch_greysheet_grokbot.py --resolve      # resolve GSIDs only
  python batch_greysheet_grokbot.py --resolve --refresh  # resolve + refresh pricing
  python batch_greysheet_grokbot.py --resolve --refresh --stats  # + rebuild stats
"""

import argparse
import os
import sys
import time
import json
import requests

import firebase_admin
from firebase_admin import credentials, firestore

# ── Hard-coded safety rail ──
TARGET_EMAIL = "grokbot@numista.ai"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY_PATH = os.path.join(SCRIPT_DIR, "..", "serviceAccountKey.json")
PROJECT_ID = "studio-9101802118-8c9a8"

# Backend API base URL (Cloud Run)
API_BASE = "https://numista-backend-568985927038.us-central1.run.app"

DELAY_MS = 500  # ms between API calls


def main():
    parser = argparse.ArgumentParser(description="Batch Greysheet for grokbot")
    parser.add_argument("--resolve", action="store_true", help="Resolve GSIDs")
    parser.add_argument("--refresh", action="store_true", help="Refresh pricing (requires GSID)")
    parser.add_argument("--stats", action="store_true", help="Rebuild collection_stats after")
    parser.add_argument("--limit", type=int, default=0, help="Limit to N coins (0=all)")
    args = parser.parse_args()

    is_dry_run = not args.resolve and not args.refresh
    mode = "DRY-RUN" if is_dry_run else ("RESOLVE" + ("+REFRESH" if args.refresh else ""))
    
    # Initialize Firebase
    if not firebase_admin._apps:
        if os.path.exists(SA_KEY_PATH):
            cred = credentials.Certificate(SA_KEY_PATH)
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": PROJECT_ID})
    db = firestore.client()

    user_ref = db.collection("users").document(TARGET_EMAIL)
    coins_ref = user_ref.collection("coins")

    print(f"[{mode}] target: {TARGET_EMAIL}")
    print(f"Scanning coins...")

    docs = list(coins_ref.stream())
    total = len(docs)
    print(f"Found {total} coin documents.\n")

    if args.limit > 0:
        docs = docs[:args.limit]
        print(f"  (limited to first {args.limit})")

    # Counters
    already_resolved = 0
    resolved_ok = 0
    resolved_fail = 0
    refreshed_ok = 0
    refreshed_fail = 0
    skipped_no_gsid = 0

    for i, doc in enumerate(docs):
        data = doc.to_dict()
        coin_id = doc.id
        year = data.get("Year", "?")
        denom = data.get("Denomination", "?")
        theme = data.get("Theme/Subject", "?")
        gsid = data.get("greysheetGsid")
        cpg = data.get("cpgRetail")

        if is_dry_run:
            has_gsid = "GSID" if gsid else "no-GSID"
            has_price = f"cpg=${cpg}" if cpg and float(str(cpg)) > 0 else "no-price"
            print(f"  [{i+1}/{len(docs)}] {year} {denom} ({theme}) -- {has_gsid} {has_price}")
            if gsid:
                already_resolved += 1
            continue

        # ── RESOLVE ──
        if args.resolve and not gsid:
            try:
                resp = requests.post(
                    f"{API_BASE}/api/greysheet/resolve",
                    json={"user_id": TARGET_EMAIL, "coin_id": coin_id},
                    timeout=30
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("status") == "success":
                        resolved_ok += 1
                        gsid = str(result.get("gsid", ""))
                        print(f"  [{i+1}] RESOLVED: {year} {denom} ({theme}) -> GSID {gsid}")
                    else:
                        resolved_fail += 1
                        print(f"  [{i+1}] NOT RESOLVED: {year} {denom} ({theme})")
                else:
                    resolved_fail += 1
                    print(f"  [{i+1}] RESOLVE ERROR {resp.status_code}: {year} {denom}")
            except Exception as e:
                resolved_fail += 1
                print(f"  [{i+1}] RESOLVE EXCEPTION: {e}")
            
            time.sleep(DELAY_MS / 1000.0)
        elif gsid:
            already_resolved += 1

        # ── REFRESH ──
        if args.refresh:
            # Re-read to get updated GSID if we just resolved
            if args.resolve and not gsid:
                skipped_no_gsid += 1
                continue
            
            try:
                resp = requests.post(
                    f"{API_BASE}/api/greysheet/refresh",
                    json={"user_id": TARGET_EMAIL, "coin_id": coin_id},
                    timeout=30
                )
                if resp.status_code == 200:
                    refreshed_ok += 1
                    result = resp.json()
                    cpg_val = result.get("cpgRetail", 0)
                    print(f"  [{i+1}] REFRESHED: {year} {denom} -> cpg=${cpg_val}")
                else:
                    refreshed_fail += 1
                    print(f"  [{i+1}] REFRESH ERROR {resp.status_code}: {year} {denom}")
            except Exception as e:
                refreshed_fail += 1
                print(f"  [{i+1}] REFRESH EXCEPTION: {e}")
            
            time.sleep(DELAY_MS / 1000.0)

        # Progress ping every 25
        if (i + 1) % 25 == 0:
            print(f"  -- progress: {i+1}/{len(docs)} --")

    # Summary
    print("\n" + "=" * 60)
    print(f"Total coins:       {total}")
    if is_dry_run:
        print(f"Already have GSID: {already_resolved}")
        print(f"Need resolve:      {total - already_resolved}")
    else:
        print(f"Already resolved:  {already_resolved}")
        print(f"Resolved OK:       {resolved_ok}")
        print(f"Resolve failed:    {resolved_fail}")
        if args.refresh:
            print(f"Refreshed OK:      {refreshed_ok}")
            print(f"Refresh failed:    {refreshed_fail}")
            print(f"Skipped (no GSID): {skipped_no_gsid}")
    print("=" * 60)

    # Stats rebuild
    if args.stats:
        print("\n-- Rebuilding collection_stats --")
        stats_ref = user_ref.collection("metadata").document("collection_stats")
        coins_snap = list(coins_ref.stream())
        coin_count = 0
        est_value = 0.0

        for doc in coins_snap:
            d = doc.to_dict()
            if d.get("item_type") == "supply" or d.get("is_supply") is True:
                continue
            coin_count += 1
            for val_key in ("cpgRetail", "cpg_retail", "greysheetBid", "AI Estimated Value"):
                raw = d.get(val_key)
                if raw is not None:
                    try:
                        v = float(str(raw).replace("$", "").replace(",", "").strip())
                        if v > 0:
                            est_value += v
                            break
                    except (ValueError, TypeError):
                        continue

        stats_data = {
            "coin_count": coin_count,
            "est_value": round(est_value, 2),
            "last_rebuilt": firestore.SERVER_TIMESTAMP,
        }
        stats_ref.set(stats_data, merge=True)
        print(f"  coin_count: {coin_count}")
        print(f"  est_value:  ${est_value:.2f}")
        print("  [OK] collection_stats rebuilt.")


if __name__ == "__main__":
    main()
