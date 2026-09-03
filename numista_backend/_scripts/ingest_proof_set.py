#!/usr/bin/env python3
"""
ingest_proof_set.py -- Reusable US Proof Set ingestion script.

Writes item_type=set and 10 dual-key set_contents children onto a
Firestore parent doc (merge=True). Dry-run by default; pass --execute to write.

Usage (dry-run):
    python ingest_proof_set.py --year 2002 --metal clad
        --parent-doc-id 6199ef81-1f96-45c1-bde1-149961125361
        --uid eric.seaman@yahoo.com

Usage (execute -- after Eric writes Proceed):
    python ingest_proof_set.py --year 2002 --metal clad
        --parent-doc-id 6199ef81-1f96-45c1-bde1-149961125361
        --uid eric.seaman@yahoo.com --execute

Usage (2003+ find-or-create):
    python ingest_proof_set.py --year 2003 --metal clad
        --uid eric.seaman@yahoo.com --execute
"""

import argparse
import json
import sys
import uuid

# ---------------------------------------------------------------------------
# Year -> five State Quarter themes, 1999-2008
# ---------------------------------------------------------------------------
YEAR_STATES = {
    1999: ["Delaware", "Pennsylvania", "New Jersey", "Georgia", "Connecticut"],
    2000: ["Massachusetts", "Maryland", "South Carolina", "New Hampshire", "Virginia"],
    2001: ["New York", "North Carolina", "Rhode Island", "Vermont", "Kentucky"],
    2002: ["Tennessee", "Ohio", "Louisiana", "Indiana", "Mississippi"],
    2003: ["Illinois", "Alabama", "Maine", "Missouri", "Arkansas"],
    2004: ["Michigan", "Florida", "Texas", "Iowa", "Wisconsin"],
    2005: ["California", "Minnesota", "Oregon", "Kansas", "West Virginia"],
    2006: ["Nevada", "Nebraska", "Colorado", "North Dakota", "South Dakota"],
    2007: ["Montana", "Washington", "Idaho", "Wyoming", "Utah"],
    2008: ["Oklahoma", "New Mexico", "Arizona", "Alaska", "Hawaii"],
}

# Fixed denominations (before + after the five quarters)
FIXED_BEFORE = [
    ("cent",   "Cent",   "Lincoln Cent",    "Lincoln Memorial Cents"),
    ("nickel", "Nickel", "Jefferson Nickel", "Jefferson Nickels"),
    ("dime",   "Dime",   "Roosevelt Dime",   "Roosevelt Dimes"),
]
FIXED_AFTER = [
    ("half dollar", "Half Dollar", "Kennedy Half",     "Kennedy Half Dollars"),
    ("dollar",      "Dollar",      "Sacagawea Dollar", "Sacagawea & Native American Dollars"),
]


def _child(year, denom_snake, denom_pascal, theme, series, metal_content, parent_doc_id):
    """Build one dual-key set_contents child (snake_case + PascalCase mirrors)."""
    return {
        # snake_case primary (Firestore SoR)
        "year":           year,
        "denomination":   denom_snake,
        "mint_mark":      "S",
        "theme_subject":  theme,
        "program_series": series,
        "strike_type":    "PROOF",
        "metal_content":  metal_content,
        "condition":      "Proof",
        "cost":           "$0.00",
        "item_type":      "coin",
        "from_set":       parent_doc_id,   # legal record -- estate PDF / BQ
        # PascalCase mirrors (Founder write contract -- Flutter _field() reads these)
        "Year":           year,
        "Denomination":   denom_pascal,
        "Mint Mark":      "S",
        "Theme/Subject":  theme,
        "Program/Series": series,
        "Strike Type":    "PROOF",
        "Metal Content":  metal_content,
        "Condition":      "Proof",
    }


def build_set_contents(year, metal, parent_doc_id):
    """Return 10 dual-key child dicts for the given proof-set year and metal."""
    states = YEAR_STATES[year]
    metal_content = "" if metal == "clad" else "90% Silver"
    year_str = str(year)
    children = []
    for d_s, d_p, theme, series in FIXED_BEFORE:
        children.append(_child(year_str, d_s, d_p, theme, series, metal_content, parent_doc_id))
    for state in states:
        children.append(_child(year_str, "quarter", "Quarter", state,
                               "50 State Quarters", metal_content, parent_doc_id))
    for d_s, d_p, theme, series in FIXED_AFTER:
        children.append(_child(year_str, d_s, d_p, theme, series, metal_content, parent_doc_id))
    return children  # always 10


def _find_or_create_parent(year, metal, uid, execute):
    """For 2003+ runs: query for an existing Set parent, or create one."""
    try:
        import firebase_admin
        from firebase_admin import firestore as fs
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = fs.client()
    except Exception as e:
        print(f"ERROR: Firestore connection failed: {e}", file=sys.stderr)
        sys.exit(1)
    docs = (db.collection(f"users/{uid}/coins")
              .where("Year", "==", str(year))
              .where("Denomination", "==", "Set")
              .where("Mint Mark", "==", "S")
              .get())
    if len(docs) == 1:
        print(f"Found existing parent: {docs[0].id}")
        return docs[0].id
    elif len(docs) == 0:
        new_id = str(uuid.uuid4())
        print(f"No parent found for {year}. Will create: {new_id}")
        if execute:
            db.collection(f"users/{uid}/coins").document(new_id).set({
                "doc_id": new_id, "item_type": "set",
                "Year": str(year), "year": str(year),
                "Denomination": "Set", "denomination": "set",
                "Mint Mark": "S", "mint_mark": "S",
                "Theme/Subject": f"{year} United States Proof Set",
                "theme_subject": f"{year} United States Proof Set",
            })
        return new_id
    else:
        ids = [d.id for d in docs]
        print(f"ERROR: Multiple Set parents found for {year}: {ids}\n"
              f"Provide --parent-doc-id explicitly.", file=sys.stderr)
        sys.exit(1)


def run(args):
    year = args.year
    metal = args.metal
    uid = args.uid
    execute = args.execute
    parent_doc_id = args.parent_doc_id

    if year not in YEAR_STATES:
        print(f"ERROR: Year {year} not in YEAR_STATES table (1999-2008).", file=sys.stderr)
        sys.exit(1)

    # --parent-doc-id REQUIRED for 2002 -- never find-or-create the live SKU
    if year == 2002 and not parent_doc_id:
        print(
            "ERROR: --parent-doc-id is required for --year 2002.\n"
            "  The live parent is: 6199ef81-1f96-45c1-bde1-149961125361\n"
            "  Re-run with: --parent-doc-id 6199ef81-1f96-45c1-bde1-149961125361",
            file=sys.stderr,
        )
        sys.exit(1)

    if not parent_doc_id:
        parent_doc_id = _find_or_create_parent(year, metal, uid, execute)

    set_contents = build_set_contents(year, metal, parent_doc_id)

    # Wrong-metal guard
    if metal == "silver" and execute:
        try:
            import firebase_admin
            from firebase_admin import firestore as fs
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            db = fs.client()
            snap = db.collection(f"users/{uid}/coins").document(parent_doc_id).get()
            if snap.exists:
                d = snap.to_dict() or {}
                theme = (d.get("Theme/Subject") or d.get("theme_subject") or "").upper()
                if "SILVER" not in theme and "90%" not in theme:
                    print(
                        f"ERROR: --metal silver requested but parent theme '{theme}' "
                        f"contains no SILVER or 90%. Use --metal clad for this SKU.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
        except ImportError:
            pass  # allow dry-run without firebase_admin

    # ---- WOULD_WRITE (always printed) --------------------------------------
    print("=" * 70)
    print("WOULD_WRITE")
    print(f"  Collection : users/{uid}/coins")
    print(f"  Document   : {parent_doc_id}")
    print(f"  merge=True")
    print()
    print(f"  item_type  : coin  ->  set")
    print(f"  set_contents: {len(set_contents)} children")
    print()
    for i, child in enumerate(set_contents):
        print(f"  [{i:2d}] {child['denomination']:12s} | {child['theme_subject']:30s} | "
              f"mint={child['mint_mark']} | strike={child['strike_type']} | "
              f"metal='{child['metal_content']}' | from_set={child['from_set'][:8]}...")
    print()
    # Full JSON of Louisiana (third quarter, index 5 in 2002)
    quarter = next(c for c in set_contents if c["theme_subject"] == YEAR_STATES[year][2])
    print("Full JSON of Louisiana child (verify dual-key + from_set):")
    print(json.dumps(quarter, indent=2))
    print("=" * 70)

    if not execute:
        print()
        print("Dry-run complete. No Firestore writes made.")
        print("Review diff above. If correct, re-run with --execute.")
        return

    # ---- EXECUTE -----------------------------------------------------------
    try:
        import firebase_admin
        from firebase_admin import firestore as fs
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = fs.client()
    except ImportError:
        print("ERROR: firebase_admin not installed.", file=sys.stderr)
        sys.exit(1)

    db.collection(f"users/{uid}/coins").document(parent_doc_id).set(
        {"item_type": "set", "set_contents": set_contents},
        merge=True,
    )
    print()
    print(f"OK  merge=True -> users/{uid}/coins/{parent_doc_id}")
    print(f"    item_type  -> set")
    print(f"    set_contents -> {len(set_contents)} children (from_set on each)")
    print()
    print("Next steps:")
    print("  1. Install Flutter dev build (includes expander + screen edits).")
    print("  2. Open 50 State Quarters detail view -- confirm 90 -> 95 / 200.")
    print("  3. Generate personalized progress PDF -- confirm 5 S-Proof rows checked.")
    print("  (Grid card % may lag -- expected, deferred.)")


def main():
    p = argparse.ArgumentParser(description="Ingest a US Proof Set into Firestore.")
    p.add_argument("--year",          type=int,  required=True,
                   help="Proof set year (1999-2008)")
    p.add_argument("--metal",         choices=["clad", "silver"], required=True)
    p.add_argument("--uid",           required=True,
                   help="Firestore user email (e.g. eric.seaman@yahoo.com)")
    p.add_argument("--parent-doc-id", dest="parent_doc_id", default=None,
                   help="Firestore doc id. Required for --year 2002.")
    p.add_argument("--execute",       action="store_true",
                   help="Write to Firestore. Omit for dry-run only.")
    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
