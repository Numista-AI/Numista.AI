#!/usr/bin/env python3
"""
reconcile_numismatic_strike_fields.py
MF2 -- Numismatic Collectibles Migration
========================================
Patches existing Firestore coin docs that are missing 'Strike Type' and 'Variety'
fields.  These fields are required by SlotResolver.matchesVariety() to resolve
isProof / isReverseProof / isEnhancedUnc, and were omitted by the add_coins
endpoint prior to the Plan.v1.1 fix.

Also normalizes 'Mint Mark' == "EU" -> "" on existing docs (MF1-B legacy cleanup).

Because add_coins never persisted 'variety_id', the derive logic uses a
Theme/Subject (coin_name) fallback hierarchy instead of variety_id.

Usage
-----
Dry-run (default -- no writes):
    python reconcile_numismatic_strike_fields.py \
        --program_id 2026_semiquincentennial_collectibles \
        --user_emails grokbot@numista.ai

Apply updates:
    python reconcile_numismatic_strike_fields.py \
        --program_id 2026_semiquincentennial_collectibles \
        --user_emails grokbot@numista.ai \
        --write

NEVER runs without --user_emails to prevent accidental full-collection sweeps.
"""

import argparse
import sys
from collections import defaultdict

import firebase_admin
from firebase_admin import credentials, firestore

# -- Firebase init ---------------------------------------------------------------
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

db = firestore.client()


# -- Strike field derive (mirrors _derive_strike_fields in main.py) --------------

def derive_from_variety_id(variety_id):
    """Derive Strike Type + Variety from variety_id if present on the doc."""
    if not variety_id:
        return None
    vid = variety_id.upper()
    if "REVERSE" in vid:
        return {"Strike Type": "Reverse Proof", "Variety": "Reverse Proof"}
    if vid in ("EU", "W-EU"):
        return {"Strike Type": "Enhanced Uncirculated", "Variety": "Enhanced Uncirculated"}
    if "CONG" in vid:
        return {"Strike Type": "Proof", "Variety": "Congratulations Set"}
    if "SILVER" in vid:
        return ({"Strike Type": "Proof", "Variety": "Silver Proof"} if "PROOF" in vid
                else {"Strike Type": "Uncirculated", "Variety": "Silver"})
    if "PROOF" in vid:
        return {"Strike Type": "Proof", "Variety": "Proof"}
    if vid == "SMS":
        return {"Strike Type": "SMS", "Variety": "SMS"}
    if "PRIVY" in vid:
        return {"Strike Type": "Uncirculated", "Variety": "July 4th Privy Mark"}
    return {"Strike Type": "Uncirculated", "Variety": "Uncirculated"}


def derive_from_theme(theme, mint_mark):
    """
    MF2 fallback: derive Strike Type + Variety from Theme/Subject text.
    Used when variety_id is absent (all docs written by add_coins before Plan.v1.1).
    """
    t = theme.lower()

    if "reverse proof" in t:
        return {"Strike Type": "Reverse Proof", "Variety": "Reverse Proof", "_bucket": "reverse_proof"}

    if "enhanced uncirculated" in t:
        return {"Strike Type": "Enhanced Uncirculated", "Variety": "Enhanced Uncirculated", "_bucket": "enhanced_unc"}

    if "congratulations" in t:
        return {"Strike Type": "Proof", "Variety": "Congratulations Set", "_bucket": "congratulations"}

    # Peace/Morgan Proof explicit in name
    if "proof" in t:
        return {"Strike Type": "Proof", "Variety": "Proof", "_bucket": "proof"}

    # Default Uncirculated (Gold Eagle, Silver Eagle, Buffalo, Innovation, Trump)
    return {"Strike Type": "Uncirculated", "Variety": "Uncirculated", "_bucket": "uncirculated"}


def needs_update(doc_data):
    """Return True if this doc is missing Strike Type or has Mint Mark == 'EU'."""
    return not doc_data.get("Strike Type") or doc_data.get("Mint Mark") == "EU"


def build_update(doc_data):
    """Build the Firestore update dict for a single doc."""
    update = {}

    vid   = doc_data.get("variety_id", "")
    theme = doc_data.get("Theme/Subject", doc_data.get("name", ""))

    if vid:
        fields = derive_from_variety_id(vid) or {}
        bucket = "variety_id"
    else:
        fields = derive_from_theme(theme, doc_data.get("Mint Mark", ""))
        bucket = fields.get("_bucket", "uncirculated")

    update["Strike Type"] = fields.get("Strike Type", "Uncirculated")
    update["Variety"]     = fields.get("Variety", "Uncirculated")
    update["_bucket"]     = bucket  # stripped before Firestore write -- dry-run report only

    # MF1-B: normalize bad mint mark
    if doc_data.get("Mint Mark") == "EU":
        update["Mint Mark"] = ""

    return update


# -- Main ------------------------------------------------------------------------

def run(program_id, user_emails, write):
    mode = "WRITE" if write else "DRY-RUN"
    print("\n" + "="*60)
    print(f"reconcile_numismatic_strike_fields  [{mode}]")
    print(f"program_id  : {program_id}")
    print(f"user_emails : {', '.join(user_emails)}")
    print("="*60 + "\n")

    grand_total = 0
    grand_updated = 0

    for email in user_emails:
        print(f"-- User: {email} --")
        coins_ref = db.collection("users").document(email).collection("coins")

        try:
            docs = list(coins_ref.where("program_id", "==", program_id).stream())
        except Exception as e:
            print(f"  ERROR fetching docs: {e}")
            continue

        total = len(docs)
        to_update = [(d, build_update(d.to_dict())) for d in docs if needs_update(d.to_dict())]
        grand_total  += total
        grand_updated += len(to_update)

        print(f"  Total docs for program  : {total}")
        print(f"  Docs needing update     : {len(to_update)}")

        if not to_update:
            print("  Nothing to patch -- already up to date.\n")
            continue

        # Bucket summary
        buckets = defaultdict(int)
        for _, upd in to_update:
            buckets[upd.get("_bucket", "?")] += 1
        print("  By derived-strike bucket:")
        for bucket, count in sorted(buckets.items()):
            print(f"    {bucket:<25} {count}")

        # Sample rows (up to 5)
        print("  Sample docs to patch (up to 5):")
        for d, upd in to_update[:5]:
            data    = d.to_dict()
            theme   = data.get("Theme/Subject", data.get("name", "(no theme)"))
            mint    = data.get("Mint Mark", "")
            vid     = data.get("variety_id", "(none)")
            new_st  = upd.get("Strike Type")
            new_var = upd.get("Variety")
            new_mm  = upd.get("Mint Mark", mint)
            print(f"    doc={d.id[:12]}...  theme={theme!r:<55}  mint={mint!r}  vid={vid!r}")
            print(f"      -> Strike Type={new_st!r}  Variety={new_var!r}  Mint Mark={new_mm!r}")

        if not write:
            print("  [DRY-RUN] No writes performed.\n")
            continue

        # -- Batch write --
        BATCH_SIZE = 400
        written = 0
        for i in range(0, len(to_update), BATCH_SIZE):
            batch = db.batch()
            chunk = to_update[i:i + BATCH_SIZE]
            for d, upd in chunk:
                clean = {k: v for k, v in upd.items() if k != "_bucket"}
                batch.update(d.reference, clean)
            batch.commit()
            written += len(chunk)
            print(f"  Batch committed: {written}/{len(to_update)} docs")

        print(f"  DONE -- {written} docs patched for {email}\n")

    print("="*60)
    print(f"Grand total docs scanned : {grand_total}")
    print(f"Grand total docs updated : {grand_updated} ({'written' if write else 'dry-run only'})")
    print("="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Patch missing Strike Type/Variety on Numismatic Collectibles coin docs."
    )
    parser.add_argument(
        "--program_id",
        default="2026_semiquincentennial_collectibles",
        help="Firestore program_id to target",
    )
    parser.add_argument(
        "--user_emails",
        nargs="+",
        required=True,
        help="One or more user email addresses to patch (space-separated).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="Apply updates to Firestore. Without this flag, runs dry-run.",
    )
    args = parser.parse_args()

    if not args.user_emails:
        print("ERROR: --user_emails is required. Refusing to run without a target.")
        sys.exit(1)

    run(program_id=args.program_id, user_emails=args.user_emails, write=args.write)
