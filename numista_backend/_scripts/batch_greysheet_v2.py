#!/usr/bin/env python3
"""
Phase 1A: Batch Greysheet resolve + price fetch for grokbot@numista.ai.

Uses firebase_admin (service account key) for Firestore.
Calls CPG Greysheet API directly via requests (no google.cloud client needed).
Skips Gemini hybrid resolve -- uses deterministic denomination-based CPG search.

Usage:
  python batch_greysheet_v2.py                  # dry-run: show status
  python batch_greysheet_v2.py --write           # resolve + fetch pricing
  python batch_greysheet_v2.py --write --limit 5 # first 5 only
  python batch_greysheet_v2.py --write --stats   # + rebuild stats
"""

import argparse
import os
import sys
import time
import json
import re
import requests as http_requests

import firebase_admin
from firebase_admin import credentials, firestore

# ── Hard-coded safety rail ──
TARGET_EMAIL = "grokbot@numista.ai"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY_PATH = os.path.join(SCRIPT_DIR, "..", "serviceAccountKey.json")
PROJECT_ID = "studio-9101802118-8c9a8"

# CPG/Greysheet API
CPG_BASE = "https://cpgpublicapiv2.greysheet.com/api"
CPG_API_KEY = "1FCAE3B4-966A-4F25-AFA1-BE242C26856B"
CPG_API_TOKEN = "D876F1BA-DDC4-4F80-B155-509AB3B6B970"

DELAY_S = 0.5

# Denomination -> CPG category mapping (node IDs from Greysheet catalog)
DENOM_TO_CPG_CATEGORY = {
    "quarter": "Quarters",
    "quarter dollar": "Quarters",
    "half dollar": "Half Dollars",
    "dime": "Dimes",
    "nickel": "Nickels",
    "cent": "Cents",
    "penny": "Cents",
    "$1": "Dollars",
    "1": "Dollars",
    "dollar": "Dollars",
}


def cpg_search(year, denomination, theme="", mint_mark="", condition=""):
    """Search CPG API for pricing by denomination + year."""
    headers = {
        "Accept": "application/json",
        "PGS_API_KEY": CPG_API_KEY,
        "PGS_API_TOKEN": CPG_API_TOKEN,
    }

    # Build search query
    denom_lower = str(denomination).lower().strip()
    category = DENOM_TO_CPG_CATEGORY.get(denom_lower, "")

    # Clean year
    yr = str(year).replace(".0", "").strip()
    if not yr or not yr.isdigit():
        return None

    # Try GetPriceGuideByYear endpoint
    try:
        search_term = f"{yr} {denomination}"
        if theme and theme != "?":
            search_term = f"{yr} {theme} {denomination}"

        resp = http_requests.get(
            f"{CPG_BASE}/CoinFacts/GetCoins",
            headers=headers,
            params={"searchTerm": search_term, "top": 5},
            timeout=15
        )
        if resp.status_code == 200:
            results = resp.json()
            if results and isinstance(results, list) and len(results) > 0:
                # Find best match by checking year + denom
                for item in results:
                    item_name = str(item.get("Name", "")).lower()
                    item_gsid = item.get("GSID") or item.get("gsid")
                    if not item_gsid:
                        continue

                    # Verify year match
                    if yr in item_name:
                        return {
                            "gsid": item_gsid,
                            "name": item.get("Name", ""),
                            "prices": item
                        }

                # Fallback: return first result
                first = results[0]
                if first.get("GSID") or first.get("gsid"):
                    return {
                        "gsid": first.get("GSID") or first.get("gsid"),
                        "name": first.get("Name", ""),
                        "prices": first
                    }
    except Exception as e:
        print(f"    CPG search error: {e}", flush=True)

    return None


def cpg_get_prices(gsid):
    """Get pricing data for a specific GSID."""
    headers = {
        "Accept": "application/json",
        "PGS_API_KEY": CPG_API_KEY,
        "PGS_API_TOKEN": CPG_API_TOKEN,
    }
    try:
        resp = http_requests.get(
            f"{CPG_BASE}/CoinFacts/GetPrices/{gsid}",
            headers=headers,
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"    CPG price error: {e}", flush=True)
    return None


def extract_price(price_data, condition=""):
    """Extract best price from CPG response."""
    if not price_data:
        return 0.0, 0.0, 0.0

    prices = price_data if isinstance(price_data, list) else [price_data]

    for p in prices:
        cpg_val = 0.0
        gs_bid = 0.0
        gs_ask = 0.0

        # Try various field names
        for key in ("CPGValue", "CPG", "Value", "Price", "RetailPrice"):
            raw = p.get(key)
            if raw:
                try:
                    cpg_val = float(str(raw).replace("$", "").replace(",", ""))
                    if cpg_val > 0:
                        break
                except (ValueError, TypeError):
                    pass

        for key in ("GreyVal", "GreyVal1", "BidPrice", "Bid"):
            raw = p.get(key)
            if raw:
                try:
                    gs_bid = float(str(raw).replace("$", "").replace(",", ""))
                    if gs_bid > 0:
                        break
                except (ValueError, TypeError):
                    pass

        for key in ("GreyAskVal", "GreyAskVal1", "GreyAsk", "AskPrice", "Ask"):
            raw = p.get(key)
            if raw:
                try:
                    gs_ask = float(str(raw).replace("$", "").replace(",", ""))
                    if gs_ask > 0:
                        break
                except (ValueError, TypeError):
                    pass

        if cpg_val > 0 or gs_bid > 0:
            if gs_bid == 0:
                gs_bid = cpg_val * 0.80
            if gs_ask == 0:
                gs_ask = gs_bid * 1.15
            return cpg_val, gs_bid, gs_ask

    return 0.0, 0.0, 0.0


def main():
    parser = argparse.ArgumentParser(description="Batch Greysheet v2 for grokbot")
    parser.add_argument("--write", action="store_true", help="Actually resolve + write pricing")
    parser.add_argument("--stats", action="store_true", help="Rebuild collection_stats after")
    parser.add_argument("--limit", type=int, default=0, help="Limit to N coins (0=all)")
    args = parser.parse_args()

    mode = "WRITE" if args.write else "DRY-RUN"
    print(f"[{mode}] target: {TARGET_EMAIL}", flush=True)

    # Initialize Firebase Admin (service account key)
    if not firebase_admin._apps:
        if os.path.exists(SA_KEY_PATH):
            cred = credentials.Certificate(SA_KEY_PATH)
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": PROJECT_ID})

    db = firestore.client()

    user_ref = db.collection("users").document(TARGET_EMAIL)
    coins_ref = user_ref.collection("coins")

    print("Scanning coins...", flush=True)
    docs = list(coins_ref.stream())
    total = len(docs)
    print(f"Found {total} coin documents.\n", flush=True)

    if args.limit > 0:
        docs = docs[:args.limit]
        print(f"  (limited to first {args.limit})\n", flush=True)

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
        mint_mark = data.get("Mint Mark", "")
        condition = data.get("Condition", "")
        gsid = data.get("greysheetGsid")
        cpg = data.get("cpgRetail")

        if not args.write:
            has_gsid = f"GSID={gsid}" if gsid else "no-GSID"
            has_price = f"cpg=${cpg}" if cpg and float(str(cpg)) > 0 else "no-price"
            print(f"  [{i+1}/{len(docs)}] {year} {denom} ({theme}) -- {has_gsid} {has_price}", flush=True)
            continue

        # Already priced? Skip
        if cpg and float(str(cpg)) > 0:
            already_priced += 1
            continue

        # RESOLVE + PRICE
        result = cpg_search(year, denom, theme, mint_mark, condition)
        if result:
            new_gsid = str(result["gsid"])
            gs_name = result["name"]

            # Get detailed pricing
            price_data = cpg_get_prices(result["gsid"])
            cpg_val, gs_bid, gs_ask = extract_price(price_data, condition)

            if cpg_val <= 0 and gs_bid <= 0:
                # Try prices from search result itself
                cpg_val, gs_bid, gs_ask = extract_price(result.get("prices"), condition)

            update = {
                "greysheetGsid": new_gsid,
                "greysheetName": gs_name,
            }

            if cpg_val > 0 or gs_bid > 0:
                update["cpgRetail"] = round(cpg_val, 2)
                update["greysheetBid"] = round(gs_bid, 2)
                update["greysheetAsk"] = round(gs_ask, 2)
                update["priceLastUpdated"] = firestore.SERVER_TIMESTAMP
                update["AI Estimated Value"] = f"${gs_bid:.2f} - ${cpg_val:.2f}"
                priced_ok += 1
                print(f"  [{i+1}] PRICED: {year} {denom} ({theme}) -> {gs_name} cpg=${cpg_val:.2f}", flush=True)
            else:
                update["cpgRetail"] = 0.0
                update["greysheetBid"] = 0.0
                update["greysheetAsk"] = 0.0
                priced_fail += 1
                print(f"  [{i+1}] RESOLVED (no price): {year} {denom} ({theme}) -> {gs_name}", flush=True)

            coins_ref.document(coin_id).update(update)
            resolved_ok += 1
        else:
            resolved_fail += 1
            print(f"  [{i+1}] NOT FOUND: {year} {denom} ({theme})", flush=True)

        time.sleep(DELAY_S)

        if (i + 1) % 25 == 0:
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
            for val_key in ("cpgRetail", "greysheetBid"):
                raw = d.get(val_key)
                if raw is not None:
                    try:
                        v = float(str(raw).replace("$", "").replace(",", ""))
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
        print(f"  coin_count: {coin_count}", flush=True)
        print(f"  est_value:  ${est_value:.2f}", flush=True)
        print("  [OK] collection_stats rebuilt.", flush=True)


if __name__ == "__main__":
    main()
