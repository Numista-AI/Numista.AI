#!/usr/bin/env python3
"""
Phase 1A: Batch Greysheet via deployed Cloud Run API.

Uses firebase_admin for Firestore reads, calls Cloud Run for resolve+refresh.
Timeout = 300s per call (Gemini hybrid resolve is slow).

Usage:
  python batch_greysheet_cloudrun.py                  # dry-run
  python batch_greysheet_cloudrun.py --write --limit 3
  python batch_greysheet_cloudrun.py --write --stats
"""

import argparse
import os
import sys
import time
import json
import requests as http_req

import firebase_admin
from firebase_admin import credentials, firestore

TARGET_EMAIL = "grokbot@numista.ai"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SA_KEY_PATH = os.path.join(SCRIPT_DIR, "..", "serviceAccountKey.json")
PROJECT_ID = "studio-9101802118-8c9a8"

API_BASE = "https://numista-backend-568985927038.us-central1.run.app"
DELAY_S = 0.5
TIMEOUT = 300  # 5 min timeout for Gemini hybrid resolve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    mode = "WRITE" if args.write else "DRY-RUN"
    print(f"[{mode}] target: {TARGET_EMAIL}", flush=True)

    if not firebase_admin._apps:
        if os.path.exists(SA_KEY_PATH):
            cred = credentials.Certificate(SA_KEY_PATH)
            firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": PROJECT_ID})
    db = firestore.client()

    coins_ref = db.collection("users").document(TARGET_EMAIL).collection("coins")
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
    already_priced = 0

    for i, doc in enumerate(docs):
        data = doc.to_dict()
        coin_id = doc.id
        year = str(data.get("Year", "?")).replace(".0", "")
        denom = data.get("Denomination", "?")
        theme = data.get("Theme/Subject", "?")
        cpg = data.get("cpgRetail")

        if not args.write:
            gsid = data.get("greysheetGsid")
            has_gsid = f"GSID={gsid}" if gsid else "no-GSID"
            has_price = f"cpg=${cpg}" if cpg and float(str(cpg)) > 0 else "no-price"
            print(f"  [{i+1}/{len(docs)}] {year} {denom} ({theme}) -- {has_gsid} {has_price}", flush=True)
            continue

        if cpg and float(str(cpg)) > 0:
            already_priced += 1
            continue

        # Call refresh (which also resolves GSID if missing)
        print(f"  [{i+1}] Processing: {year} {denom} ({theme})...", flush=True)
        try:
            resp = http_req.post(
                f"{API_BASE}/api/greysheet/refresh",
                json={"user_id": TARGET_EMAIL, "coin_id": coin_id},
                timeout=TIMEOUT
            )
            if resp.status_code == 200:
                result = resp.json()
                cpg_val = result.get("cpgRetail", 0)
                gs_name = result.get("greysheetName", "")
                resolved_ok += 1
                if cpg_val and float(str(cpg_val)) > 0:
                    priced_ok += 1
                    print(f"         PRICED: {gs_name} cpg=${cpg_val}", flush=True)
                else:
                    print(f"         RESOLVED (no price): {gs_name}", flush=True)
            elif resp.status_code == 400:
                resolved_fail += 1
                print(f"         NOT RESOLVED: {resp.json().get('detail', '?')}", flush=True)
            else:
                resolved_fail += 1
                print(f"         ERROR {resp.status_code}: {resp.text[:200]}", flush=True)
        except http_req.exceptions.ReadTimeout:
            resolved_fail += 1
            print(f"         TIMEOUT (300s)", flush=True)
        except Exception as e:
            resolved_fail += 1
            print(f"         EXCEPTION: {e}", flush=True)

        time.sleep(DELAY_S)

        if (i + 1) % 25 == 0:
            print(f"  -- progress: {i+1}/{len(docs)} --", flush=True)

    print("\n" + "=" * 60, flush=True)
    print(f"Total: {total}, Resolved: {resolved_ok}, Failed: {resolved_fail}, Priced: {priced_ok}, Already: {already_priced}", flush=True)
    print("=" * 60, flush=True)

    if args.write and args.stats:
        print("\n-- Rebuilding collection_stats --", flush=True)
        stats_ref = db.collection("users").document(TARGET_EMAIL).collection("metadata").document("collection_stats")
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
                if raw:
                    try:
                        v = float(str(raw).replace("$", "").replace(",", ""))
                        if v > 0:
                            est_value += v
                            break
                    except (ValueError, TypeError):
                        continue
        stats_ref.set({"coin_count": coin_count, "est_value": round(est_value, 2), "last_rebuilt": firestore.SERVER_TIMESTAMP}, merge=True)
        print(f"  coin_count: {coin_count}, est_value: ${est_value:.2f}", flush=True)
        print("  [OK] rebuilt.", flush=True)

if __name__ == "__main__":
    main()
