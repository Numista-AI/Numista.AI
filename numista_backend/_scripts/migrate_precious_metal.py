# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
#!/usr/bin/env python3
"""
migrate_precious_metal.py — Standardizes Metal Content for all coins.

Infers the correct metal composition from denomination + year and writes
a standardized value if the field is missing or empty.

Standardized values (used by the melt value calculator):
  '90% Silver'     — pre-1965 dimes, quarters, halves, Morgan/Peace dollars
  '40% Silver'     — 1965-1970 Kennedy halves
  '35% Silver'     — 1942-1945 War Nickels
  'Copper-Nickel'  — post-1965 circulation coins
  'Copper (95%)'   — pre-1982 pennies
  'Zinc (97.5%)'   — 1983+ pennies
  'Gold (90%)'     — pre-1933 gold coins
  'Gold (91.67%)' — American Eagle gold bullion
  'Silver (99.9%)' — American Eagle silver bullion

Usage:
    python migrate_precious_metal.py
    python migrate_precious_metal.py --user eric@numista.ai
    python migrate_precious_metal.py --dry-run
"""
import argparse, re
import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT_KEY = "serviceAccountKey.json.json"


def clean(v) -> str:
    if v is None: return ""
    if isinstance(v, float): return str(int(v))
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none", "null", "") else s


def infer_metal(data: dict):
    year_raw = clean(data.get("Year"))
    try:
        year = int(re.sub(r"[^\d]", "", year_raw)[:4])
    except (ValueError, TypeError):
        year = 0

    denom   = clean(data.get("Denomination")).lower()
    program = clean(data.get("Program/Series")).lower()
    theme   = clean(data.get("Theme/Subject")).lower()
    variety = clean(data.get("Variety")).lower()
    mint    = clean(data.get("Mint Mark")).upper()

    # ── Gold bullion ──────────────────────────────────────────────────────────
    if "american eagle" in program and "gold" in program:
        return "Gold (91.67%)"
    if "american buffalo" in program:
        return "Gold (99.99%)"
    # Pre-1933 gold
    gold_kw = ["eagle", "double eagle", "quarter eagle", "half eagle",
               "saint gaudens", "liberty head gold"]
    if any(k in program or k in theme for k in gold_kw):
        return "Gold (90%)"

    # ── Silver bullion ────────────────────────────────────────────────────────
    if "american eagle" in program and "silver" in program:
        return "Silver (99.9%)"

    # ── Morgan / Peace dollars ────────────────────────────────────────────────
    if "morgan" in program or "morgan" in theme:
        return "90% Silver"
    if "peace dollar" in program or "peace dollar" in theme or "peace" in program:
        return "90% Silver"

    # ── Eisenhower dollars ────────────────────────────────────────────────────
    if "eisenhower" in program or "ike" in program:
        if "silver" in variety or "proof" in clean(data.get("Strike Type")).lower():
            return "40% Silver"
        return "Copper-Nickel"

    # ── Kennedy half dollars ──────────────────────────────────────────────────
    half_denoms = ("half", "0.5", "50 cents", "half dollar")
    if "kennedy" in program or denom in half_denoms:
        if 0 < year <= 1964:
            return "90% Silver"
        if 1965 <= year <= 1970:
            return "40% Silver"
        return "Copper-Nickel"

    # ── Quarters ──────────────────────────────────────────────────────────────
    if denom in ("quarter", "0.25", "25 cents", "quarter dollar"):
        if 0 < year <= 1964:
            return "90% Silver"
        return "Copper-Nickel"

    # ── Dimes ─────────────────────────────────────────────────────────────────
    if denom in ("dime", "0.10", "10 cents"):
        if 0 < year <= 1964:
            return "90% Silver"
        return "Copper-Nickel"

    # ── Nickels / War Nickels ─────────────────────────────────────────────────
    if denom in ("nickel", "0.05", "5 cents"):
        if 1942 <= year <= 1945 and mint == "P":
            return "35% Silver"
        return "Copper-Nickel"

    # ── Cents / Pennies ───────────────────────────────────────────────────────
    if denom in ("cent", "penny", "0.01", "1 cent"):
        if year == 1943:
            return "Steel (Wartime)"
        if 0 < year < 1982:
            return "Copper (95%)"
        if year == 1982:
            return "Copper or Zinc"   # transition year
        return "Zinc (97.5%)"

    # ── Generic dollars ───────────────────────────────────────────────────────
    if denom in ("dollar", "1", "1 dollar", "$1"):
        if 0 < year <= 1935:
            return "90% Silver"
        return "Copper-Nickel"

    return None  # cannot determine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="Limit to one user email")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    firebase_admin.initialize_app(credentials.Certificate(SERVICE_ACCOUNT_KEY))
    db = firestore.client()

    user_refs = ([db.collection("users").document(args.user)]
                 if args.user else list(db.collection("users").stream()))

    updated = has_value = unknown = errors = 0

    for ur in user_refs:
        uid     = ur.id
        doc_ref = ur.reference if hasattr(ur, "reference") else ur
        print(f"\n── {uid} ──")

        for doc in doc_ref.collection("coins").stream():
            data = doc.to_dict() or {}
            existing = clean(data.get("Metal Content")).lower()
            if existing and existing not in ("n/a",):
                has_value += 1
                continue

            metal = infer_metal(data)
            if not metal:
                print(f"  ⚠️  Cannot infer: year={clean(data.get('Year'))} "
                      f"denom={clean(data.get('Denomination'))}")
                unknown += 1
                continue

            try:
                if args.dry_run:
                    print(f"  [DRY] {doc.id[:24]} → {metal}")
                else:
                    doc.reference.update({"Metal Content": metal})
                    print(f"  ✅ {doc.id[:24]} → {metal}")
                updated += 1
            except Exception as e:
                print(f"  ❌ {doc.id}: {e}")
                errors += 1

    print(f"\n{'='*50}")
    print(f"{'DRY RUN ' if args.dry_run else ''}DONE  "
          f"updated={updated}  had_value={has_value}  unknown={unknown}  errors={errors}")

if __name__ == "__main__":
    main()
