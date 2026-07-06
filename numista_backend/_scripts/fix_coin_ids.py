# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
#!/usr/bin/env python3
"""
fix_coin_ids.py — Assigns stable coin_id slugs to all user coins in Firestore.

Safe to re-run — skips coins that already have a coin_id.
Format: {year}_{mintmark}_{denomination}_{theme_slug}_{variety_slug}

Usage:
    python fix_coin_ids.py
    python fix_coin_ids.py --user eric@numista.ai
    python fix_coin_ids.py --dry-run
"""
import argparse, re
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_KEY = "serviceAccountKey.json.json"


def slugify(value: str) -> str:
    value = str(value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def clean(v) -> str:
    if v is None: return ""
    if isinstance(v, float): return str(int(v))
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none", "null", "") else s


def make_coin_id(data: dict) -> str:
    parts = []
    for field, max_len in [("Year", 6), ("Mint Mark", 4), ("Denomination", 20),
                            ("Theme/Subject", 40), ("Variety", 20)]:
        val = clean(data.get(field))
        if val:
            parts.append(slugify(val)[:max_len].rstrip("-"))
    if not parts:
        series = clean(data.get("Program/Series"))
        if series:
            parts.append(slugify(series)[:30].rstrip("-"))
    return "_".join(parts) if parts else "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="Limit to one user email")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    firebase_admin.initialize_app(credentials.Certificate(SERVICE_ACCOUNT_KEY))
    db = firestore.client()

    user_refs = ([db.collection("users").document(args.user)]
                 if args.user else list(db.collection("users").stream()))
    print(f"[fix_coin_ids] Users: {len(user_refs)}")

    updated = skipped = errors = 0

    for ur in user_refs:
        uid     = ur.id
        doc_ref = ur.reference if hasattr(ur, "reference") else ur
        print(f"\n── {uid} ──")
        coins = list(doc_ref.collection("coins").stream())
        used: dict[str, int] = {}

        for doc in coins:
            data = doc.to_dict() or {}
            if clean(data.get("coin_id")):
                skipped += 1
                continue
            try:
                base = make_coin_id(data)
                n    = used.get(base, 0)
                cid  = base if n == 0 else f"{base}_{n+1}"
                used[base] = n + 1
                if args.dry_run:
                    print(f"  [DRY] {doc.id[:24]} → {cid}")
                else:
                    doc.reference.update({"coin_id": cid})
                    print(f"  ✅ {doc.id[:24]} → {cid}")
                updated += 1
            except Exception as e:
                print(f"  ❌ {doc.id}: {e}")
                errors += 1

    print(f"\n{'='*50}")
    print(f"{'DRY RUN ' if args.dry_run else ''}DONE  updated={updated}  skipped={skipped}  errors={errors}")

if __name__ == "__main__":
    main()
