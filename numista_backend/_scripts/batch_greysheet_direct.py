#!/usr/bin/env python3
"""
Phase 1A: Batch Greysheet resolve + price fetch for grokbot@numista.ai.

Calls GreysheetService DIRECTLY (no HTTP overhead).
Dry-run by default; --write to apply changes.

Usage:
  python batch_greysheet_direct.py                  # dry-run: show status
  python batch_greysheet_direct.py --write           # resolve + fetch pricing
  python batch_greysheet_direct.py --write --limit 5 # first 5 only
  python batch_greysheet_direct.py --write --stats   # + rebuild stats
"""

import argparse
import os
import sys
import time
import traceback

# Add parent dir to path so we can import services
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import firebase_admin
from firebase_admin import credentials, firestore as fb_firestore
from google.cloud import firestore

# ── Hard-coded safety rail ──
TARGET_EMAIL = "grokbot@numista.ai"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY_PATH = os.path.join(SCRIPT_DIR, "..", "serviceAccountKey.json")
PROJECT_ID = "studio-9101802118-8c9a8"

DELAY_S = 0.5  # 500ms between API calls (CoS directive)
CHUNK_SIZE = 25  # batch logging every N coins


def main():
    parser = argparse.ArgumentParser(description="Batch Greysheet direct for grokbot")
    parser.add_argument("--write", action="store_true", help="Actually resolve + write pricing")
    parser.add_argument("--stats", action="store_true", help="Rebuild collection_stats after")
    parser.add_argument("--limit", type=int, default=0, help="Limit to N coins (0=all)")
    args = parser.parse_args()

    mode = "WRITE" if args.write else "DRY-RUN"
    print(f"[{mode}] target: {TARGET_EMAIL}", flush=True)

    # Initialize Firebase Admin
    if not firebase_admin._apps:
        if os.path.exists(SA_KEY_PATH):
            cred = credentials.Certificate(SA_KEY_PATH)
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": PROJECT_ID})

    db = firestore.Client(project=PROJECT_ID)

    # Import the service
    from services.greysheet_service import GreysheetService
    gs_svc = GreysheetService(db=db)

    # Setup Gemini client for hybrid resolve
    genai_client = None
    primary_model = None
    if args.write:
        try:
            from google import genai
            genai_client = genai.Client(
                vertexai=True,
                project=PROJECT_ID,
                location="us-central1"
            )
            primary_model = "gemini-2.5-flash"
            print(f"  Gemini client ready (model: {primary_model})", flush=True)
        except Exception as e:
            print(f"  WARNING: Gemini init failed: {e}", flush=True)
            print(f"  Resolve will fall back to non-AI matching only.", flush=True)

    # Scan coins
    print("Scanning coins...", flush=True)
    user_ref = db.collection("users").document(TARGET_EMAIL)
    coins_ref = user_ref.collection("coins")
    docs = list(coins_ref.stream())
    total = len(docs)
    print(f"Found {total} coin documents.\n", flush=True)

    if args.limit > 0:
        docs = docs[:args.limit]
        print(f"  (limited to first {args.limit})\n", flush=True)

    # Counters
    resolved_ok = 0
    resolved_fail = 0
    priced_ok = 0
    priced_fail = 0
    already_priced = 0

    for i, doc in enumerate(docs):
        data = doc.to_dict()
        coin_id = doc.id
        year = str(data.get("Year", "?")).replace(".0", "")
        denom = data.get("Denomination", "?")
        theme = data.get("Theme/Subject", "?")
        gsid = data.get("greysheetGsid")
        cpg = data.get("cpgRetail")

        if not args.write:
            has_gsid = f"GSID={gsid}" if gsid else "no-GSID"
            has_price = f"cpg=${cpg}" if cpg and float(str(cpg)) > 0 else "no-price"
            print(f"  [{i+1}/{len(docs)}] {year} {denom} ({theme}) -- {has_gsid} {has_price}", flush=True)
            continue

        # Check if already priced
        if cpg and float(str(cpg)) > 0:
            already_priced += 1
            if (i + 1) % CHUNK_SIZE == 0:
                print(f"  [{i+1}/{len(docs)}] already priced, skipping...", flush=True)
            continue

        # ── STEP 1: RESOLVE GSID ──
        if not gsid:
            try:
                result = gs_svc.resolve_gsid_hybrid(
                    coin_data=data,
                    genai_client=genai_client,
                    primary_model=primary_model
                )
                if result:
                    gsid_int, gs_name = result
                    gsid = str(gsid_int)
                    coin_ref = coins_ref.document(coin_id)
                    coin_ref.update({
                        "greysheetGsid": gsid,
                        "greysheetName": gs_name
                    })
                    resolved_ok += 1
                    print(f"  [{i+1}] RESOLVED: {year} {denom} ({theme}) -> GSID {gsid} ({gs_name})", flush=True)
                else:
                    resolved_fail += 1
                    print(f"  [{i+1}] NOT RESOLVED: {year} {denom} ({theme})", flush=True)
                    time.sleep(DELAY_S)
                    continue
            except Exception as e:
                resolved_fail += 1
                print(f"  [{i+1}] RESOLVE ERROR: {year} {denom} -- {e}", flush=True)
                time.sleep(DELAY_S)
                continue

            time.sleep(DELAY_S)

        # ── STEP 2: FETCH PRICING ──
        try:
            gsid_int = int(gsid)
            prices = gs_svc.get_prices_by_gsid(gsid_int)
            if prices:
                # Find best grade match
                condition = data.get("Condition", "")
                grade_str = data.get("Strike Type", "")

                # Pick the first price entry (or best match)
                best_price = prices[0] if isinstance(prices, list) else prices
                if isinstance(prices, list) and len(prices) > 0:
                    # Try to match grade
                    for p in prices:
                        p_grade = str(p.get("Grade", "")).lower()
                        if condition.lower() in p_grade or "ms-65" in p_grade or "unc" in p_grade:
                            best_price = p
                            break

                cpg_retail = float(best_price.get("CPGValue", 0) or best_price.get("CPG", 0) or 0)
                gs_bid = float(best_price.get("GreyVal", 0) or best_price.get("GreyVal1", 0) or 0)
                gs_ask = float(best_price.get("GreyAskVal", 0) or best_price.get("GreyAsk", 0) or 0)

                if gs_bid == 0 and cpg_retail > 0:
                    gs_bid = cpg_retail * 0.80
                if gs_ask == 0 and gs_bid > 0:
                    gs_ask = gs_bid * 1.15

                if cpg_retail > 0 or gs_bid > 0:
                    coin_ref = coins_ref.document(coin_id)
                    coin_ref.update({
                        "cpgRetail": round(cpg_retail, 2),
                        "greysheetBid": round(gs_bid, 2),
                        "greysheetAsk": round(gs_ask, 2),
                        "greysheetGrade": best_price.get("Grade", ""),
                        "priceLastUpdated": fb_firestore.SERVER_TIMESTAMP,
                        "AI Estimated Value": f"${gs_bid:.2f} - ${cpg_retail:.2f}"
                    })
                    priced_ok += 1
                    print(f"  [{i+1}] PRICED: {year} {denom} ({theme}) -> cpg=${cpg_retail:.2f} bid=${gs_bid:.2f}", flush=True)
                else:
                    priced_fail += 1
                    print(f"  [{i+1}] NO PRICE DATA: {year} {denom} ({theme})", flush=True)
            else:
                priced_fail += 1
                print(f"  [{i+1}] NO PRICES RETURNED: {year} {denom} ({theme})", flush=True)
        except Exception as e:
            priced_fail += 1
            print(f"  [{i+1}] PRICE ERROR: {year} {denom} -- {e}", flush=True)

        time.sleep(DELAY_S)

        # Progress ping
        if (i + 1) % CHUNK_SIZE == 0:
            print(f"  -- progress: {i+1}/{len(docs)} (resolved={resolved_ok}, priced={priced_ok}) --", flush=True)

    # Summary
    print("\n" + "=" * 60, flush=True)
    print(f"Total coins:       {total}", flush=True)
    if not args.write:
        print("DRY-RUN complete. Use --write to apply changes.", flush=True)
    else:
        print(f"Already priced:    {already_priced}", flush=True)
        print(f"Resolved OK:       {resolved_ok}", flush=True)
        print(f"Resolve failed:    {resolved_fail}", flush=True)
        print(f"Priced OK:         {priced_ok}", flush=True)
        print(f"Price failed:      {priced_fail}", flush=True)
    print("=" * 60, flush=True)

    # Stats rebuild
    if args.write and args.stats:
        print("\n-- Rebuilding collection_stats --", flush=True)
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
                        v = float(str(raw).replace("$", "").replace(",", "").strip().split("-")[0].strip())
                        if v > 0:
                            est_value += v
                            break
                    except (ValueError, TypeError):
                        continue

        stats_data = {
            "coin_count": coin_count,
            "est_value": round(est_value, 2),
            "last_rebuilt": fb_firestore.SERVER_TIMESTAMP,
        }
        stats_ref.set(stats_data, merge=True)
        print(f"  coin_count: {coin_count}", flush=True)
        print(f"  est_value:  ${est_value:.2f}", flush=True)
        print("  [OK] collection_stats rebuilt.", flush=True)


if __name__ == "__main__":
    main()
