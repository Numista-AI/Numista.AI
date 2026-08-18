#!/usr/bin/env python3
"""
remediate_awq_themes_and_supplies.py

Legal System of Record metadata repair script for Numista.AI.
1. Deterministic, punctuation-normalized AWQ honoree matching against intake description fields.
2. Unmatched/ambiguous rows marked as theme_subject_status='needs_review' (zero guessing).
3. Conjunctive supply classifier with commemorative coin protection (Booker T. Washington guard).
4. Strict single-key writing ('theme_subject') with merge=True; zero deletion/modification of Personal Notes.
5. In-database audit trail stored in Firestore under `_migrations/20260818_awq_and_supplies/audit_logs/{coin_id}`.
6. Updates users/{identifier}/collection_stats with accurate aggregate metrics.
"""

import argparse
import datetime
import os
import re
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# Authoritative US Mint American Women Quarters (2022–2025)
AWQ_ROSTER = [
    # 2022
    "Maya Angelou",
    "Dr. Sally Ride",
    "Wilma Mankiller",
    "Nina Otero-Warren",
    "Anna May Wong",
    # 2023
    "Bessie Coleman",
    "Edith Kanaka'ole",
    "Eleanor Roosevelt",
    "Jovita Idar",
    "Maria Tallchief",
    # 2024
    "Rev. Dr. Pauli Murray",
    "Patsy Takemoto Mink",
    "Dr. Mary Edwards Walker",
    "Celia Cruz",
    "Zitkala-Sa",
    # 2025
    "Ida B. Wells",
    "Juliette Gordon Low",
    "Dr. Vera Rubin",
    "Stacey Park Milbern",
    "Althea Gibson",
]

def normalize_text(text: str) -> str:
    """Strip titles/dots/hyphens/apostrophes and normalize whitespace for robust full-phrase comparison."""
    if not text:
        return ""
    t = text.lower()
    # Normalize common abbreviations
    t = t.replace("dr.", "dr").replace("rev.", "rev")
    # Replace punctuation with single space
    t = re.sub(r"[\.,'’\-–—/]", " ", t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t

# Precompute normalized roster forms and known official aliases
NORMALIZED_ROSTER = {}
for name in AWQ_ROSTER:
    norm = normalize_text(name)
    NORMALIZED_ROSTER[norm] = name
    # Also support variant without titles (e.g., 'sally ride' for 'Dr. Sally Ride')
    without_titles = re.sub(r"^(dr|rev|rev dr)\s+", "", norm).strip()
    if without_titles and without_titles not in NORMALIZED_ROSTER:
        NORMALIZED_ROSTER[without_titles] = name

# Authoritative honoree aliases
HONOREE_ALIASES = {
    "patsy mink": "Patsy Takemoto Mink",
    "pauli murray": "Rev. Dr. Pauli Murray",
    "mary edwards walker": "Dr. Mary Edwards Walker",
    "mary walker": "Dr. Mary Edwards Walker",
    "sally ride": "Dr. Sally Ride",
    "vera rubin": "Dr. Vera Rubin",
}
for alias_phrase, canonical in HONOREE_ALIASES.items():
    NORMALIZED_ROSTER[normalize_text(alias_phrase)] = canonical

def match_honoree(doc_data: dict) -> tuple[str | None, str]:
    """
    Match candidate honoree strictly against designated intake fields.
    Returns (canonical_name, status) where status is 'matched', 'needs_review', or 'skipped_already_set'.
    """
    existing_theme = (doc_data.get("theme_subject") or "").strip()
    if existing_theme in AWQ_ROSTER:
        return existing_theme, "skipped_already_set"

    # Legacy copy: if Theme/Subject has an exact roster name
    legacy_theme = (doc_data.get("Theme/Subject") or "").strip()
    if legacy_theme in AWQ_ROSTER:
        return legacy_theme, "matched"

    # Search fields: Item Description, description, original_description, raw_text, and Personal Notes
    search_fields = [
        str(doc_data.get("Item Description") or ""),
        str(doc_data.get("description") or ""),
        str(doc_data.get("original_description") or ""),
        str(doc_data.get("raw_text") or ""),
        str(doc_data.get("Personal Notes") or ""),
        str(doc_data.get("personal_notes") or ""),
    ]
    combined_text = " ".join(search_fields)
    norm_text = normalize_text(combined_text)

    if not norm_text:
        return None, "needs_review"

    matches = set()
    for norm_phrase, canonical in NORMALIZED_ROSTER.items():
        # Match whole normalized phrase surrounded by word boundaries or space
        pattern = r"(?:^|\s)" + re.escape(norm_phrase) + r"(?:$|\s)"
        if re.search(pattern, norm_text):
            matches.add(canonical)

    if len(matches) == 1:
        return list(matches)[0], "matched"
    else:
        return None, "needs_review"

def is_supply_document(doc_data: dict) -> bool:
    """
    Conjunctive Supply Classifier:
    1. Explicit item_type == 'supply' or denomination == 'Supply' or program_series == 'Supplies & Books'.
    2. Missing/empty denomination AND missing/empty year AND supply keyword in title.
    3. Explicit 'U.S. Women\'s Quarter Book' title (protects against copied quarter years).
    NEVER tags any commemorative coin (e.g. 1946 Booker T. Washington Half Dollar) as supply.
    """
    item_type = str(doc_data.get("item_type") or "").strip().lower()
    denom = str(doc_data.get("Denomination") or doc_data.get("denomination") or "").strip()
    year = str(doc_data.get("Year") or doc_data.get("year") or "").strip()
    prog = str(doc_data.get("Program/Series") or doc_data.get("program_series") or "").strip()
    title = str(doc_data.get("Item Description") or doc_data.get("description") or doc_data.get("title") or "").strip()

    # Rule 1: Explicit supply tag
    if item_type == "supply" or denom.lower() == "supply" or prog.lower() in ["supplies & books", "supplies"]:
        return True

    # Rule 3: Explicit Quarter Book title
    if "women's quarter book" in title.lower() or "quarter book" in title.lower() or "quarter album" in title.lower():
        # Even if year is present due to invoice copy, ensure denomination is not a real coin
        if not denom or denom.lower() in ["none", "null", "supply", "0"]:
            return True

    # Rule 2: Conjunctive check (no coin denomination AND no year AND supply keyword)
    has_year = bool(re.search(r"\b(1[789]\d\d|20\d\d)\b", year))
    has_coin_denom = bool(denom and denom.lower() not in ["none", "null", "supply", "0"])

    if not has_year and not has_coin_denom:
        supply_keywords = ["book", "album", "folder", "binder", "holder", "capsule", "loupe", "scale", "storage box"]
        title_lower = title.lower()
        if any(re.search(r"\b" + re.escape(kw) + r"\b", title_lower) for kw in supply_keywords):
            return True

    return False

def init_firestore():
    if not firebase_admin._apps:
        # Check standard credential paths
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    return firestore.client()

def parse_num(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace("$", "").replace(",", "").replace("~", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0

def run_remediation(target_user: str, dry_run: bool = True):
    db = init_firestore()
    coins_col = db.collection(f"users/{target_user}/coins")
    docs = list(coins_col.stream())

    print(f"\n=======================================================")
    print(f"Numista.AI System of Record Remediation: {target_user}")
    print(f"Mode: {'DRY-RUN (No Writes)' if dry_run else 'APPLY (In-Place Live Repair)'}")
    print(f"Total Documents Found: {len(docs)}")
    print(f"=======================================================\n")

    matched_n = 0
    needs_review_n = 0
    supplies_tagged = 0
    skipped_already_set = 0
    needs_review_ids = []

    audit_records = []
    updates_to_apply = []

    # Totals accumulators
    total_items = len(docs)
    coin_count = 0
    supply_count = 0
    tot_face = 0.0
    tot_melt = 0.0
    tot_est = 0.0

    for doc in docs:
        d = doc.to_dict()
        doc_id = doc.id
        updates = {}

        # 1. Supply Classification
        is_supply = is_supply_document(d)
        if is_supply:
            supplies_tagged += 1
            supply_count += 1
            if d.get("item_type") != "supply" or not d.get("is_supply"):
                updates["item_type"] = "supply"
                updates["is_supply"] = True
                updates["category"] = "Supplies"
        else:
            coin_count += 1
            # Accumulate valuations for coins
            tot_face += parse_num(d.get("Face Value") or d.get("face_value"))
            tot_melt += parse_num(d.get("Melt Value") or d.get("melt_value"))
            
            # AI Value hierarchy
            est = parse_num(d.get("cpgRetail"))
            if est <= 0:
                est = parse_num(d.get("greysheetBid"))
            if est <= 0:
                est = parse_num(d.get("AI Estimated Value") or d.get("ai_value") or d.get("estimated_value"))
            tot_est += est

            # 2. Check if this is an AWQ or Washington Quarter record
            prog = str(d.get("Program/Series") or d.get("program_series") or d.get("Item Description") or "").lower()
            is_awq = "women" in prog or "awq" in prog or "american women" in prog

            if is_awq:
                canonical_name, status = match_honoree(d)
                if status == "matched":
                    matched_n += 1
                    updates["theme_subject"] = canonical_name
                elif status == "skipped_already_set":
                    skipped_already_set += 1
                elif status == "needs_review":
                    needs_review_n += 1
                    needs_review_ids.append(doc_id)
                    updates["theme_subject_status"] = "needs_review"

        if updates:
            audit_entry = {
                "doc_id": doc_id,
                "before": {k: d.get(k) for k in updates.keys()},
                "after": updates,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "actor": "remediate_awq_themes_and_supplies.py",
            }
            updates_to_apply.append((doc.reference, updates, audit_entry))

    print(f"--- Remediation Summary ---")
    print(f"Matched Honorees:       {matched_n}")
    print(f"Needs Review Honorees:  {needs_review_n} (IDs: {needs_review_ids})")
    print(f"Supplies Tagged:        {supplies_tagged}")
    print(f"Skipped (Already Set):  {skipped_already_set}")
    print(f"Total Updates Pending:  {len(updates_to_apply)}")
    print(f"---------------------------\n")

    print(f"--- Recalculated Collection Stats ---")
    print(f"Total Items:     {total_items}")
    print(f"Coins Count:     {coin_count}")
    print(f"Supplies Count:  {supply_count}")
    print(f"Face Value:      ${tot_face:,.2f}")
    print(f"Melt Value:      ${tot_melt:,.2f}")
    print(f"Estimated Value: ${tot_est:,.2f}")
    print(f"-------------------------------------\n")

    if not dry_run:
        print("Applying in-place live Firestore updates...")
        for doc_ref, updates, audit_entry in updates_to_apply:
            doc_ref.set(updates, merge=True)
            # In-database audit log
            audit_ref = db.collection(f"_migrations/20260818_awq_and_supplies/audit_logs").document(audit_entry["doc_id"])
            audit_ref.set(audit_entry, merge=True)

        # Upsert collection_stats document at users/{target_user}/metadata/collection_stats and merge into users/{target_user}
        stats_payload = {
            "item_count": total_items,
            "coin_count": coin_count,
            "supply_count": supply_count,
            "face_value": round(tot_face, 2),
            "melt_value": round(tot_melt, 2),
            "est_value": round(tot_est, 2),
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        stats_ref = db.document(f"users/{target_user}/metadata/collection_stats")
        stats_ref.set(stats_payload, merge=True)
        # Also merge into user root doc
        db.document(f"users/{target_user}").set({"collection_stats": stats_payload}, merge=True)
        print(f"Successfully upserted users/{target_user}/metadata/collection_stats and applied {len(updates_to_apply)} document updates.")
    else:
        print("DRY-RUN Complete. Zero database modifications performed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Numista.AI AWQ & Supply Remediation")
    parser.add_argument("--user", default="eric.seaman@yahoo.com", help="Target user email/identifier")
    parser.add_argument("--apply", action="store_true", help="Apply updates to Firestore (default is dry-run)")
    args = parser.parse_args()

    run_remediation(target_user=args.user, dry_run=not args.apply)
