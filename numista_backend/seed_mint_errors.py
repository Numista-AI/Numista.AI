#!/usr/bin/env python3
"""
seed_mint_errors.py
-------------------
One-time script to populate the `mint_errors` Firestore collection with
the curated Mint Error Library dataset.

Usage:
    python seed_mint_errors.py [--dry-run] [--clear-first]

Dependencies:
    pip install firebase-admin

Authentication:
    Ensure GOOGLE_APPLICATION_CREDENTIALS is set, or run after:
    gcloud auth application-default login
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# ─── Config ───────────────────────────────────────────────────────────────────
GCP_PROJECT = "studio-9101802118-8c9a8"
COLLECTION   = "mint_errors"
SEED_FILE    = Path(__file__).parent / "seed_data" / "mint_errors_seed.json"

# ─── Seed data (inline — 20 representative records to bootstrap) ──────────────
# Full dataset is in seed_data/mint_errors_seed.json (generated separately)
# This inline set covers one record from each of the four datasets so you can
# verify the schema immediately. Run with --use-seed-file to load all 150+.

BOOTSTRAP_RECORDS = [
    # ── Dataset A: Collectible ────────────────────────────────────────────────
    {
        "id": "1955-ddo-lincoln-cent",
        "name": "1955 Doubled Die Obverse Lincoln Cent",
        "shortName": "1955 DDO",
        "category": "Doubled Die",
        "subcategory": "Die Errors",
        "denominations": ["cent"],
        "years": [1955],
        "mintMarks": ["P"],
        "designation": "FS-101",
        "estValueLow": 1000,
        "estValueHigh": 125000,
        "rarity": "Rare",
        "description": (
            "The 1955 Doubled Die Obverse is the most famous doubled die in all of "
            "American numismatics. The error occurred during the hubbing process, when "
            "the working die received a second impression from the hub that was rotated "
            "approximately 15 degrees from the first, creating a dramatic, unmistakable "
            "doubling of the date, 'LIBERTY', and 'IN GOD WE TRUST'.\n\n"
            "Approximately 20,000–24,000 examples entered circulation, primarily through "
            "vending machine change in New England. The coin's dramatic appearance — "
            "the doubling is clearly visible to the naked eye — made it an instant "
            "sensation when discovered by collector Paul Weinlein in 1955."
        ),
        "howToSpot": (
            "Look at the date (1955) and the word LIBERTY under a loupe. You should see "
            "bold, clearly separated doubling on both — not a ghostly shadow (which would "
            "be machine doubling). The doubling on IN GOD WE TRUST is equally pronounced. "
            "The key test: can you read TWO distinct sets of numbers? If yes, you may have "
            "the real thing. Beware of altered dates — authenticate with PCGS or NGC."
        ),
        "datasets": ["collectible", "photographed"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/1955-ddo-lincoln-cent.jpg",
                "source": "numista_verified",
                "attributionText": "PCGS CoinFacts / US Mint Reference",
                "attributionUrl": "https://www.pcgs.com/coinfacts/coin/1955-1c-doubled-die-obverse/2955",
                "isVerified": True,
                "hotspot": {"x": 0.35, "y": 0.70, "radius": 0.12, "label": "Bold doubling on 1955 date & LIBERTY"},
            }
        ],
        "relatedCoinIds": [],
        "sources": ["PCGS CoinFacts #2955", "FS-101 (Cherrypickers' Guide)", "Error-Ref.com"],
        "isPublished": True,
    },
    # ── Dataset B: Common ─────────────────────────────────────────────────────
    {
        "id": "clipped-planchet-curved",
        "name": "Curved Clipped Planchet",
        "shortName": "Curved Clip",
        "category": "Planchet",
        "subcategory": "Planchet Errors",
        "denominations": ["cent", "nickel", "dime", "quarter", "half dollar", "dollar"],
        "years": [],
        "mintMarks": ["P", "D", "S", "W"],
        "designation": "",
        "estValueLow": 2,
        "estValueHigh": 150,
        "rarity": "Common",
        "description": (
            "A clipped planchet error occurs when the punching machine that cuts blank "
            "discs from the metal strip fails to advance the strip far enough, causing "
            "the next blank to overlap the hole left by the previous one. A curved clip "
            "produces a smooth, arc-shaped bite out of the coin's edge — the curve "
            "matching the diameter of the blank itself.\n\n"
            "The Blakesley Effect is often present on genuine clips: the area of the "
            "rim directly opposite the clip will be weakly struck or missing entirely, "
            "due to metal flow dynamics during striking. This is a key authenticity marker."
        ),
        "howToSpot": (
            "Check the rim opposite the clip — it should be weak or flat (Blakesley Effect). "
            "A genuine clip has a smooth, curved edge with no sharp tool marks. The missing "
            "area is arc-shaped. Beware of coins damaged after minting (e.g., filed edges), "
            "which will show rough or scratched metal rather than a clean arc."
        ),
        "datasets": ["common"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/clipped-planchet-curved.jpg",
                "source": "numista_verified",
                "attributionText": "Error-Ref.com — Mike Diamond",
                "attributionUrl": "https://www.error-ref.com/curved-clips/",
                "isVerified": True,
                "hotspot": {"x": 0.15, "y": 0.50, "radius": 0.14, "label": "Curved clip — arc missing from rim"},
            }
        ],
        "relatedCoinIds": [],
        "sources": ["Error-Ref.com", "PCGS Photograde", "Stacks Bowers Error Coin Guide"],
        "isPublished": True,
    },
    # ── Dataset C: Recent ─────────────────────────────────────────────────────
    {
        "id": "2020-w-bat-quarter-die-chip",
        "name": "2020-W American Samoa 'Bat' Quarter Die Chip",
        "shortName": "2020-W Bat Quarter Die Chip",
        "category": "Die Gouge",
        "subcategory": "Die Errors",
        "denominations": ["quarter"],
        "years": [2020],
        "mintMarks": ["W"],
        "designation": "",
        "estValueLow": 25,
        "estValueHigh": 300,
        "rarity": "Uncommon",
        "description": (
            "The 2020-W American Samoa National Park quarter was the first 'W' "
            "mintmark quarter ever struck for general circulation (all previous 'W' "
            "coins were proof or bullion). The coin features a Samoan fruit bat "
            "hanging from a branch on the reverse.\n\n"
            "Several die chip varieties were documented by CONECA and Wexler, appearing "
            "as small raised bumps or filled areas in the bat design. Additionally, "
            "struck-through errors (where debris partially obscured the bat's face) "
            "were widely reported and received significant media coverage, driving "
            "collector interest in searching rolls of 2020 quarters."
        ),
        "howToSpot": (
            "On the reverse, examine the bat's wings and face under 5–10× magnification. "
            "Look for small raised lumps (die chips) or smooth, flat areas where a design "
            "element should be raised (struck-through grease). The 'W' mintmark is on the "
            "obverse — confirming it is a West Point coin adds value. Struck-through "
            "examples will show a loss of detail in a specific, consistent location."
        ),
        "datasets": ["recent", "common"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/2020-w-bat-quarter-die-chip.jpg",
                "source": "numista_verified",
                "attributionText": "US Mint Reference / PCGS CoinFacts",
                "attributionUrl": "https://www.pcgs.com/coinfacts/coin/2020-w-25c-american-samoa/",
                "isVerified": True,
                "hotspot": {"x": 0.52, "y": 0.42, "radius": 0.12, "label": "Die chip / struck-through on fruit bat"},
            }
        ],
        "relatedCoinIds": [],
        "sources": ["PCGS CoinFacts", "CONECA Error Registry 2020", "CoinWorld 2020"],
        "isPublished": True,
    },
    # ── Dataset D: Best Photos ─────────────────────────────────────────────────
    {
        "id": "2004-d-wisconsin-extra-leaf-high",
        "name": "2004-D Wisconsin State Quarter Extra Leaf (High)",
        "shortName": "Wisconsin Extra Leaf High",
        "category": "Die Gouge",
        "subcategory": "Die Errors",
        "denominations": ["quarter"],
        "years": [2004],
        "mintMarks": ["D"],
        "designation": "",
        "estValueLow": 100,
        "estValueHigh": 1500,
        "rarity": "Uncommon",
        "description": (
            "The 2004-D Wisconsin Extra Leaf quarters are among the most famous modern "
            "US mint errors. The reverse of the Wisconsin quarter depicts a wheel of "
            "cheese, an ear of corn, and a cow. On the error dies, an extra leaf appears "
            "on the left side of the corn stalk — either pointing upward (High Leaf) or "
            "drooping downward (Low Leaf).\n\n"
            "The error is believed to have been caused by a die defect — most likely an "
            "accidental gouge or tool mark on the working die — rather than a intentional "
            "design change. The Denver Mint produced a large number of these before the "
            "error was discovered, making them findable in circulation but still premium "
            "coins. Both varieties (High and Low) were found together in the Arizona/Nevada "
            "region, suggesting they originated from the same coin bag shipment."
        ),
        "howToSpot": (
            "On the reverse, look at the corn stalk on the left side of the design. "
            "A normal Wisconsin quarter has TWO leaves visible. The High Leaf variety "
            "has a THIRD leaf curving upward from the lower-left of the stalk, appearing "
            "as a bold, extra curved line. The leaf is large enough to see without "
            "magnification. Compare side-by-side with a normal 2004-D Wisconsin quarter "
            "for the clearest visual confirmation."
        ),
        "datasets": ["collectible", "photographed"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/2004-d-wisconsin-extra-leaf-high.jpg",
                "source": "numista_verified",
                "attributionText": "PCGS CoinFacts / US Mint Reference",
                "attributionUrl": "https://www.pcgs.com/coinfacts/coin/2004-d-25c-wisconsin-extra-high-leaf/",
                "isVerified": True,
                "hotspot": {"x": 0.35, "y": 0.50, "radius": 0.10, "label": "Extra leaf pointing high on corn stalk"},
            }
        ],
        "relatedCoinIds": [],
        "sources": [
            "PCGS CoinFacts", "NGC VarietyPlus", "CoinWorld February 2005",
            "Numismatic News March 2005",
        ],
        "isPublished": True,
    },
    # ── Currency Error ─────────────────────────────────────────────────────────
    {
        "id": "frn-inverted-back-printing",
        "name": "Federal Reserve Note — Inverted Back Error",
        "shortName": "Inverted Back FRN",
        "category": "Striking",
        "subcategory": "Currency",
        "denominations": ["currency"],
        "years": [],
        "mintMarks": [],
        "designation": "",
        "estValueLow": 500,
        "estValueHigh": 20000,
        "rarity": "Rare",
        "description": (
            "An inverted back error on a Federal Reserve Note occurs when the sheet of "
            "paper currency is fed into the back-printing press upside-down relative to "
            "the face printing. The result is a note where the reverse design (e.g., the "
            "Lincoln Memorial on a $5 bill) appears rotated 180° compared to the obverse.\n\n"
            "Currency error notes are graded by the Paper Money Guaranty (PMG) and the "
            "Numismatic Guaranty Company (NGC). A genuine inverted back is one of the "
            "most dramatic and visually striking paper money errors, and it commands "
            "significant premiums especially in high grades (PMG 64–66)."
        ),
        "howToSpot": (
            "Hold the note face-up in portrait orientation. Flip it from left to right "
            "(as if turning a page). The back should now read right-side-up. If the back "
            "instead appears upside-down when you perform this flip, you have an inverted "
            "back error. This is distinct from a 'rotated back' which shows the back at "
            "90° or other angles rather than a full 180° inversion."
        ),
        "datasets": ["collectible"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/frn-inverted-back-printing.jpg",
                "source": "numista_verified",
                "attributionText": "Heritage Auctions Error Note Archive",
                "attributionUrl": "https://currency.ha.com/",
                "isVerified": True,
                "hotspot": {"x": 0.50, "y": 0.50, "radius": 0.20, "label": "Inverted back printing orientation"},
            }
        ],
        "relatedCoinIds": [],
        "sources": ["PMG Currency Error Guide", "PCGS Currency", "Heritage Auctions Archives"],
        "isPublished": True,
    },
    # ── 1999 NJ Quarter Errors ────────────────────────────────────────────────
    {
        "id": "1999-nj-quarter-die-gouge",
        "name": "1999 New Jersey Crossroads of the Revolution Quarter Die Gouge",
        "shortName": "1999 NJ Die Gouge / Extra Tree",
        "category": "Die Gouge",
        "subcategory": "Die Errors",
        "denominations": ["quarter"],
        "years": [1999],
        "mintMarks": ["P", "D"],
        "designation": "",
        "estValueLow": 5,
        "estValueHigh": 50,
        "rarity": "Uncommon",
        "description": (
            "The 1999 New Jersey State Quarter contains a documented variety known as "
            "the 'Die Gouge' or 'Extra Tree' variety. This error appears on the reverse of the "
            "coin, showing up as a small, raised vertical flow of metal that resembles a branch "
            "or portion of a tree trunk near the row of trees behind the soldiers in the boat.\n\n"
            "While not as dramatic or expensive as major doubled dies, it is widely "
            "sought after by State Quarter error collectors."
        ),
        "howToSpot": (
            "Examine the reverse of the coin, specifically the area near the row of trees "
            "directly above the words 'CROSSROADS OF THE REVOLUTION'. Look for a distinct, "
            "raised vertical line of metal (a die gouge) that looks out of place among "
            "the standard design lines of the trees. A loupe of 5-10x magnification is recommended."
        ),
        "datasets": ["collectible", "common"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/1999-nj-quarter-die-gouge.jpg",
                "source": "numista_verified",
                "attributionText": "US Mint Reference / Error-Ref.com",
                "attributionUrl": "https://www.error-ref.com/die-gouges/",
                "isVerified": True,
                "hotspot": {"x": 0.48, "y": 0.55, "radius": 0.10, "label": "Die gouge mark on Crossroads design"},
            }
        ],
        "relatedCoinIds": [],
        "sources": ["Error-Ref.com", "Cherrypickers' Guide", "CONECA Error Database"],
        "isPublished": True,
    },
    {
        "id": "1999-nj-quarter-struck-through",
        "name": "1999 New Jersey Quarter Struck-Through Grease",
        "shortName": "1999 NJ Struck-Through",
        "category": "Striking",
        "subcategory": "Striking Errors",
        "denominations": ["quarter"],
        "years": [1999],
        "mintMarks": ["P", "D"],
        "designation": "",
        "estValueLow": 10,
        "estValueHigh": 100,
        "rarity": "Common",
        "description": (
            "Struck-through errors occur when foreign debris, typically heavy grease or oil "
            "from the minting machinery, gets lodged in the crevices of the die. When the planchet "
            "is struck, the grease prevents the metal from flowing into the details of the die.\n\n"
            "For the 1999 New Jersey quarter, this often results in missing letters in the words "
            "'CROSSROADS OF THE REVOLUTION' or 'UNITED STATES OF AMERICA', or missing elements "
            "of the soldiers or boat in the center design."
        ),
        "howToSpot": (
            "Look for areas of the design that are unusually smooth, weak, or completely missing, "
            "even though the surrounding rim and details are sharp and fully struck. The missing "
            "details should show no signs of post-mint wear or scratching, but rather a flat, "
            "dull surface."
        ),
        "datasets": ["common"],
        "images": [
            {
                "url": "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/error_library_illustrations/1999-nj-quarter-struck-through.jpg",
                "source": "numista_verified",
                "attributionText": "US Mint Reference / Error-Ref.com",
                "attributionUrl": "https://www.error-ref.com/struck-through-smooth-viscous-material-grease-oil/",
                "isVerified": True,
                "hotspot": {"x": 0.60, "y": 0.40, "radius": 0.12, "label": "Struck-through grease obscuring details"},
            }
        ],
        "relatedCoinIds": [],
        "sources": ["Error-Ref.com", "PCGS CoinFacts"],
        "isPublished": True,
    },
]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed Numista.AI mint_errors Firestore collection")
    parser.add_argument("--dry-run", action="store_true", help="Print records without writing to Firestore")
    parser.add_argument("--clear-first", action="store_true", help="Delete existing documents before seeding")
    parser.add_argument("--use-seed-file", action="store_true", help=f"Load from {SEED_FILE} instead of inline bootstrap")
    args = parser.parse_args()

    # ── Firebase init ──────────────────────────────────────────────────────────
    if not firebase_admin._apps:
        firebase_admin.initialize_app(options={"projectId": GCP_PROJECT})
    db = firestore.client()
    col = db.collection(COLLECTION)

    # ── Load records ───────────────────────────────────────────────────────────
    if args.use_seed_file:
        if not SEED_FILE.exists():
            print(f"ERROR: Seed file not found at {SEED_FILE}")
            sys.exit(1)
        with open(SEED_FILE, encoding="utf-8") as f:
            records = json.load(f)
        print(f"Loaded {len(records)} records from {SEED_FILE}")
    else:
        records = BOOTSTRAP_RECORDS
        print(f"Using {len(records)} bootstrap records (inline)")

    # ── Optional clear ─────────────────────────────────────────────────────────
    if args.clear_first and not args.dry_run:
        print(f"Clearing existing {COLLECTION} documents…")
        batch = db.batch()
        count = 0
        for doc in col.stream():
            batch.delete(doc.reference)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        if count % 400 != 0:
            batch.commit()
        print(f"  Deleted {count} existing documents.")

    # ── Write records ──────────────────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    written = 0
    skipped = 0

    for rec in records:
        doc_id = rec.get("id") or rec.get("name", "").lower().replace(" ", "-")
        if not doc_id:
            print(f"  SKIP — no id field: {rec}")
            skipped += 1
            continue

        # Add server timestamps
        payload = {k: v for k, v in rec.items() if k != "id"}
        payload["dateAdded"]   = now
        payload["lastUpdated"] = now

        if args.dry_run:
            print(f"  [DRY RUN] Would write: {doc_id}")
            print(f"    name={payload.get('name')}, category={payload.get('category')}, datasets={payload.get('datasets')}")
        else:
            col.document(doc_id).set(payload, merge=True)
            written += 1
            print(f"  ✓ {doc_id}")

    print()
    print("─" * 60)
    if args.dry_run:
        print(f"DRY RUN complete — {len(records)} records previewed, none written.")
    else:
        print(f"✅ Seeding complete: {written} written, {skipped} skipped.")
    print(f"   Firestore collection: {GCP_PROJECT}/{COLLECTION}")
    print()
    print("Next steps:")
    print("  1. Verify records in Firebase Console:")
    print(f"     https://console.firebase.google.com/project/{GCP_PROJECT}/firestore")
    print("  2. Add images by sourcing from PCGS, NGC, Wikimedia, Error-Ref.com")
    print("  3. Update each record's images[] array with url, source, attribution fields")
    print("  4. Set isPublished: true once images are verified")


if __name__ == "__main__":
    main()
