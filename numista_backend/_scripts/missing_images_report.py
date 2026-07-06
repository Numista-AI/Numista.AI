# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
missing_images_report.py
─────────────────────────────────────────────────────────────────────────────
Cross-references a user's Numista.AI coin collection against the Firestore
coin_image_index and reports which coins have images and which don't.

Usage:
    python missing_images_report.py --user JSeaman1204@gmail.com
    python missing_images_report.py --user JSeaman1204@gmail.com --csv
    python missing_images_report.py --all-users

Output:
    - Console summary with counts
    - Optional CSV export: missing_images_{email}_{date}.csv
    - Stores results in Firestore: users/{uid}/image_audit/{date}
"""

import os
import re
import csv
import argparse
from datetime import date
from collections import defaultdict
import google.auth
from google.cloud import firestore

# ─── Config ───────────────────────────────────────────────────────────────────

PROJECT = "studio-9101802118-8c9a8"
os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json"
)

# Map Firestore coin "Series" / "Program" names → canonical image index program slugs
# Add more as needed — lowercase matching, partial match OK
SERIES_TO_SLUG = {
    # ── American Eagle series ──────────────────────────────────────────────────
    "silver eagle":                       "american-eagle-silver",
    "american silver eagle":              "american-eagle-silver",
    "american eagle silver":              "american-eagle-silver",
    "american silver eagle program":      "american-eagle-silver",
    "american eagle 25th anniversary":    "american-eagle-silver",
    "american eagle two-coin set":        "american-eagle-silver",
    "destination silver eagle":           "american-eagle-silver",
    "silver eagles":                      "american-eagle-silver",
    "gold eagle":                         "american-eagle-gold",
    "american gold eagle":                "american-eagle-gold",
    "gold american eagle":                "american-eagle-gold",
    "indian head gold eagle":             "american-eagle-gold",
    "indian head gold half eagle":        "american-eagle-gold",
    "liberty head gold half eagle":       "american-eagle-gold",
    "liberty head half eagle":            "american-eagle-gold",
    "platinum eagle":                     "american-eagle-platinum",
    "american eagle platinum":            "american-eagle-platinum",
    "palladium eagle":                    "american-eagle-palladium",
    "american eagle palladium":           "american-eagle-palladium",

    # ── Quarters ──────────────────────────────────────────────────────────────
    "50 state quarters":                  "50-state-quarters",
    "state quarters":                     "50-state-quarters",
    "state and territory quarters":       "50-state-quarters",
    "america the beautiful quarters":     "america-the-beautiful",
    "national park quarters":             "america-the-beautiful",
    "american women quarters program":    "american-women-quarters",
    "american women quarters":            "american-women-quarters",
    "us women's quarters":                "american-women-quarters",
    "us women quarters":                  "american-women-quarters",
    "washington silver quarter":          "quarter",
    "washington quarter":                 "quarter",
    "standing liberty silver quarter":    "quarter",
    "standing liberty quarter":           "quarter",
    "standing liberty silver quarter (type 1)": "quarter",
    "standing liberty silver quarter (type 2)": "quarter",
    "standing liberty silver quarter set": "quarter",
    "barber silver quarters":             "quarter",
    "capped bust silver quarter series":  "quarter",
    "liberty seated quarter":             "quarter",
    "liberty seated silver quarter":      "quarter",
    "draped bust silver quarter series":  "quarter",
    "american innovation":                "american-innovation",
    "american innovation dollar":         "american-innovation",
    "american innovation dollars":        "american-innovation",
    "u.s. innovation dollar":             "american-innovation",
    "u.s. innovation dollar program":     "american-innovation",

    # ── Dollars ───────────────────────────────────────────────────────────────
    "morgan silver dollar":               "morgan-dollar",
    "morgan silver dollars":              "morgan-dollar",
    "morgan silver dollar set":           "morgan-dollar",
    "morgan dollar series":               "morgan-dollar",
    "morgan silver dollar set":           "morgan-dollar",
    "morgan":                             "morgan-dollar",
    "modern morgan dollar":               "morgan-dollar",
    "modern morgan and peace silver dollar collection": "morgan-dollar",
    "the ultimate modern morgan and peace silver dollar collection": "morgan-dollar",
    "ultimate modern morgan and peace silver dollar collection": "morgan-dollar",
    "peace dollar":                       "peace-dollar",
    "modern peace dollar":                "peace-dollar",
    "native american dollar":             "native-american-dollar",
    "sacagawea":                          "native-american-dollar",
    "sacagawea dollar":                   "native-american-dollar",
    "native american dollar program":     "native-american-dollar",
    "native american dollar series":      "native-american-dollar",
    "native american $1 coin program":    "native-american-dollar",
    "presidential dollar":                "presidential-dollars",
    "presidential dollars":               "presidential-dollars",
    "eisenhower dollar":                  "presidential-dollars",
    "1971-1978 ike dollar set":           "presidential-dollars",
    "susan b. anthony dollar":            "dollar",
    "trade dollar":                       "dollar",
    "schoolgirl dollar":                  "dollar",
    "indian head pattern dollar":         "dollar",
    "american liberty":                   "american-liberty",

    # ── Half Dollars ──────────────────────────────────────────────────────────
    "kennedy half dollar":                "kennedy-half-dollar",
    "kennedy half dollar series":         "kennedy-half-dollar",
    "franklin half dollar":               "kennedy-half-dollar",
    "silver franklin half dollar":        "kennedy-half-dollar",
    "the half dollar club":               "kennedy-half-dollar",
    "the half dollar club selection":     "kennedy-half-dollar",
    "half dollar club selection":         "kennedy-half-dollar",
    "half dollar clib":                   "kennedy-half-dollar",
    "historic u.s. silver half-dollars":  "kennedy-half-dollar",
    "barber half dollar":                 "kennedy-half-dollar",
    "seated liberty half dollar":         "kennedy-half-dollar",
    "walking liberty half dollar":        "walking-liberty",
    "liberty walking half dollar":        "walking-liberty",
    "walking liberty":                    "walking-liberty",
    "capped bust half dollar":            "commemorative",
    "2.50 american sesquicentennial gold": "commemorative",

    # ── Dimes ─────────────────────────────────────────────────────────────────
    "roosevelt dimes":                    "dime",
    "roosevelt dime":                     "dime",
    "roosevelt dime series":              "dime",
    "roosevelt dime set":                 "dime",
    "roosevelt silver dime":              "dime",
    "roosevelt":                          "dime",
    "mercury dime":                       "mercury-dime",
    "mercury silver dime":                "mercury-dime",
    "mercury":                            "mercury-dime",
    "winged liberty":                     "mercury-dime",
    "barber dimes":                       "dime",
    "barber dime":                        "dime",
    "liberty seated silver dime":         "dime",
    "capped bust dime":                   "dime",

    # ── Nickels ───────────────────────────────────────────────────────────────
    "jefferson nickel":                   "jefferson-nickel",
    "jefferson nickel series":            "jefferson-nickel",
    "jefferson wartime nickel":           "jefferson-nickel",
    "the u.s. nickel collection":         "jefferson-nickel",
    "return to monticello":               "jefferson-nickel",
    "wartime nickel":                     "jefferson-nickel",
    "buffalo nickel":                     "buffalo-nickel",
    "buffalo nickel series":              "buffalo-nickel",
    "buffalo nickel type 1":              "buffalo-nickel",
    "last seven philadelphia buffalo nickels": "buffalo-nickel",
    "liberty head nickel":                "nickel",
    "shield nickel":                      "nickel",
    "three-cent nickel":                  "nickel",

    # ── Cents ─────────────────────────────────────────────────────────────────
    "lincoln cent":                       "lincoln-cent",
    "lincoln cent series":                "lincoln-cent",
    "lincoln wheat cent series":          "lincoln-cent",
    "lincoln wheat cent":                 "lincoln-cent",
    "lincoln wheat cents":                "lincoln-cent",
    "lincoln head penny":                 "lincoln-cent",
    "lincoln head cent":                  "lincoln-cent",
    "lincoln memorial cent":              "lincoln-cent",
    "lincoln shield cent":                "lincoln-cent",
    "lincoln bicentennial cent":          "lincoln-cent",
    "lincoln cent (wheat reverse)":       "lincoln-cent",
    "lincoln cent (steel)":               "lincoln-cent",
    "lincoln cent vdb":                   "lincoln-cent",
    "lincoln head wheat cents":           "lincoln-cent",
    "lincoln steel cent":                 "lincoln-cent",
    "wheat cents":                        "lincoln-cent",
    "lincoln":                            "lincoln-cent",
    "vdb":                                "lincoln-cent",
    "steel cent":                         "lincoln-cent",
    "pds reprocessed steel cents":        "lincoln-cent",
    "indian head cent":                   "cent",
    "indian head cents":                  "cent",
    "flying eagle cent":                  "cent",
    "large cent":                         "cent",
    "braided hair large cents":           "cent",
    "matron head large cent":             "cent",
    "coronet head large cent":            "cent",
    "classic head":                       "cent",

    # ── Seated Liberty / Bust ─────────────────────────────────────────────────
    "liberty seated":                     "commemorative",
    "liberty seated silver dime":         "dime",
    "liberty seated silver quarter":      "quarter",
    "liberty seated quarter":             "quarter",
    "seated liberty half dollar":         "kennedy-half-dollar",

    # ── Barber (generic catch) ────────────────────────────────────────────────
    "barber":                             "commemorative",
    "barber series":                      "commemorative",
    "barber silver quarters":             "quarter",

    # ── Bicentennial ──────────────────────────────────────────────────────────
    "bicentennial":                       "bicentennial",
    "u.s. bicentennial":                  "bicentennial",

    # ── Commemoratives / sets / misc ──────────────────────────────────────────
    "commemorative":                      "commemorative",
    "saint-gaudens":                      "saint-gaudens",
    "saint gaudens":                      "saint-gaudens",
    "double eagle":                       "saint-gaudens",
    "flowing hair":                       "flowing-hair",
    "celebrating america coin collection": "commemorative",
    "the celebrating america coin collection": "commemorative",
    "the world war ii u.s. coin collection": "commemorative",
    "historic u.s. silver coins":         "commemorative",
    "america revisited":                  "commemorative",
    "time capsule year set":              "commemorative",
    "6-coin prestige proof set":          "commemorative",
    "proof set":                          "commemorative",
    "clad proof set":                     "commemorative",
    "birth year coin and silver commemorative set": "commemorative",
    "founding father commemorative":      "commemorative",
    "us commemorative gold coinage":      "commemorative",
    "mixed us coin programs":             "commemorative",
    "20 cent piece":                      "commemorative",
    "capped bust":                        "commemorative",
    "america's first small-size":         "commemorative",

    # ── Generic fallbacks (MUST be last) ──────────────────────────────────────
    "silver eagle":                       "american-eagle-silver",
    "gold":                               "american-eagle-gold",
    "dollar":                             "dollar",
    "quarter":                            "quarter",
    "half dollar":                        "kennedy-half-dollar",
    "dime":                               "dime",
    "nickel":                             "nickel",
    "cent":                               "cent",
    "penny":                              "lincoln-cent",
}



def normalize(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def series_to_slug(series_name):
    """Map a coin's series name to a canonical program slug."""
    s = normalize(series_name)
    # Exact match first
    if s in SERIES_TO_SLUG:
        return SERIES_TO_SLUG[s]
    # Partial match
    for key, slug in SERIES_TO_SLUG.items():
        if key in s or s in key:
            return slug
    return None


def sanitize_key(key):
    """Remove characters that are invalid in Firestore document IDs."""
    return re.sub(r"[/\\]", "-", key).strip("-")

def build_image_index_cache(db):
    """
    Load the entire coin_image_index into memory.
    Returns:
        exact_keys: set of all document IDs (e.g. '1964_kennedy-half-dollar_obverse')
        program_index: dict of program_slug → list of doc IDs that have that program
    """
    print("  Loading image index into cache...", flush=True)
    all_docs = list(db.collection("coin_image_index").stream())
    exact_keys  = {doc.id for doc in all_docs}
    program_index = defaultdict(list)
    for doc in all_docs:
        prog = doc.to_dict().get("program", "")
        if prog:
            program_index[prog].append(doc.id)
    print(f"  Cached {len(exact_keys)} image index entries across {len(program_index)} programs", flush=True)
    return exact_keys, program_index


def check_image_exists(exact_keys, program_index, year, mint, program_slug):
    """
    3-tier lookup against the pre-loaded image index cache:
      1. Exact: year + mint + program  (e.g. 1964_D_kennedy-half-dollar_obverse)
      2. Year-only: year + program     (e.g. 1964_kennedy-half-dollar_obverse)
      3. Program-level fallback:       any image exists for this program slug
    Returns: (found: bool, matched_key: str, tier: int)
    """
    if not program_slug:
        return False, None, 0

    # Tier 1: exact year + mint
    if year and mint:
        for side in ("obverse", "reverse"):
            k = sanitize_key(f"{year}_{mint}_{program_slug}_{side}")
            if k in exact_keys:
                return True, k, 1

    # Tier 2: year, no mint
    if year:
        for side in ("obverse", "reverse"):
            k = sanitize_key(f"{year}_{program_slug}_{side}")
            if k in exact_keys:
                return True, k, 2

    # Tier 3: program-level — any image for this program exists
    if program_slug in program_index and program_index[program_slug]:
        return True, f"[program:{program_slug}]", 3

    return False, None, 0





def audit_user(db, user_email, exact_keys, program_index, export_csv=False, verbose=False):
    print(f"\n{'='*65}")
    print(f"  Image Audit: {user_email}")
    print(f"{'='*65}")

    # Coins live at: users/{user_email}/coins/{coin_id}
    coins_ref = db.collection("users").document(user_email).collection("coins")
    coins = list(coins_ref.stream())
    total = len(coins)

    if total == 0:
        print(f"  WARNING: No coins found at users/{user_email}/coins")
        print(f"  Check that the email is spelled correctly and the user has coins entered.")
        return {}

    print(f"  Total coins in collection: {total}")


    has_image    = []
    missing_image = []

    for coin_doc in coins:
        coin = coin_doc.to_dict()

        # Extract key fields — field names match actual Firestore schema
        year        = str(coin.get("Year") or coin.get("year") or "").split("-")[0].strip()
        mint        = str(coin.get("Mint Mark") or coin.get("mint_mark") or coin.get("mintMark") or "").strip().upper()
        series      = str(coin.get("Program/Series") or coin.get("Series") or coin.get("series") or coin.get("Program") or "")
        name        = str(coin.get("Coin Name") or coin.get("Name") or coin.get("name") or coin.get("Denomination") or "")
        denom       = str(coin.get("Denomination") or coin.get("denomination") or "")
        est_value   = coin.get("AI Estimated Value") or coin.get("ai_estimated_value") or coin.get("estimatedValue") or "0"
        img_obv     = coin.get("image_url_obverse") or coin.get("Image URL Obverse") or coin.get("imageUrlObverse") or ""
        img_rev     = coin.get("image_url_reverse") or coin.get("Image URL Reverse") or coin.get("imageUrlReverse") or ""

        # Parse estimated value to number for sorting
        try:
            raw_val = str(est_value).replace("$", "").replace(",", "").split("-")[0].strip()
            sort_val = float(raw_val) if raw_val else 0.0
        except (ValueError, AttributeError):
            sort_val = 0.0

        coin_info = {
            "id":         coin_doc.id,
            "year":       year,
            "mint":       mint if mint not in ("", "NONE") else "",
            "series":     series,
            "name":       name or f"{year} {series}",
            "denom":      denom,
            "est_value":  est_value,
            "sort_val":   sort_val,
            "has_stored": bool(img_obv or img_rev),
        }

        # Check index — 3-tier: exact year+mint → year-only → any program image
        program_slug = series_to_slug(series) or series_to_slug(name)
        found, matched_key, tier = check_image_exists(
            exact_keys, program_index,
            year,
            mint if mint not in ("", "NONE") else None,
            program_slug
        )

        coin_info["index_match"] = found
        coin_info["index_key"]   = matched_key or ""
        coin_info["match_tier"]  = tier

        if found or coin_info["has_stored"]:
            has_image.append(coin_info)
        else:
            missing_image.append(coin_info)

    # Sort missing by value descending (highest value coins = highest priority)
    missing_image.sort(key=lambda x: x["sort_val"], reverse=True)

    coverage = len(has_image) / total * 100 if total > 0 else 0
    print(f"\n  Images found:   {len(has_image):>4} ({coverage:.1f}%)")
    print(f"  Images MISSING: {len(missing_image):>4} ({100-coverage:.1f}%)")

    # Group missing by series
    by_series = defaultdict(list)
    for c in missing_image:
        by_series[c["series"] or "Unknown Series"].append(c)

    print(f"\n  Missing by series:")
    for series, coins_list in sorted(by_series.items(), key=lambda x: -len(x[1])):
        print(f"    {len(coins_list):>4}  {series}")

    print(f"\n  Top 20 missing (by estimated value):")
    print(f"  {'Year':6} {'Mint':4} {'Est. Value':12} Name")
    print(f"  {'-'*55}")
    for c in missing_image[:20]:
        mint_str = c["mint"] if c["mint"] else " "
        print(f"  {c['year']:6} {mint_str:4} {str(c['est_value']):12} {c['name'][:45]}")

    # Export CSV
    if export_csv:
        filename = f"missing_images_{user_email.replace('@','_')}_{date.today()}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "year", "mint", "series", "name", "denom", "est_value",
                "index_key", "coin_id"
            ])
            writer.writeheader()
            for c in missing_image:
                writer.writerow({
                    "year":       c["year"],
                    "mint":       c["mint"],
                    "series":     c["series"],
                    "name":       c["name"],
                    "denom":      c["denom"],
                    "est_value":  c["est_value"],
                    "index_key":  c["index_key"],
                    "coin_id":    c["id"],
                })
        print(f"\n  CSV exported: {filename}")

    return {
        "email":        user_email,
        "total":        total,
        "has_image":    len(has_image),
        "missing":      len(missing_image),
        "missing_list": missing_image,
    }


def main():
    parser = argparse.ArgumentParser(description="Numista.AI missing coin images report")
    parser.add_argument("--user",      help="User email to audit")
    parser.add_argument("--all-users", action="store_true", help="Audit all users")
    parser.add_argument("--csv",       action="store_true", help="Export missing list to CSV")
    parser.add_argument("--verbose",   action="store_true", help="Show all matched coins too")
    args = parser.parse_args()

    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)

    # Build image index cache once — reused for all users
    exact_keys, program_index = build_image_index_cache(db)

    if args.all_users:
        users = list(db.collection("users").stream())
        for u in users:
            data = u.to_dict()
            email = data.get("email", u.id)
            audit_user(db, email, exact_keys, program_index, export_csv=args.csv, verbose=args.verbose)
    elif args.user:
        audit_user(db, args.user, exact_keys, program_index, export_csv=args.csv, verbose=args.verbose)
    else:
        # Default: run for both Eric and his aunt
        for email in ["eric@numista.ai", "JSeaman1204@gmail.com"]:
            audit_user(db, email, exact_keys, program_index, export_csv=args.csv, verbose=args.verbose)


if __name__ == "__main__":
    main()
