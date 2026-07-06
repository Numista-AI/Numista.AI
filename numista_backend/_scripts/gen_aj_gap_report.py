# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
gen_aj_gap_report.py
──────────────────────────────────────────────────────────────────────────────
Generates a fresh image gap report for jseaman1204@gmail.com's collection.

Reads every coin from Firestore (post-restore), checks for:
  1. No personal photo (image_url_obverse / image_url_reverse)
  2. No reference image available in coin_image_index

Outputs:
  - aj_image_gap_report_<date>.csv  (coins with missing images)
  - Summary printed to console

Usage:
    python _scripts/gen_aj_gap_report.py
"""

import os, sys, csv
from datetime import datetime

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore

PROJECT      = "studio-9101802118-8c9a8"
TARGET_EMAIL = "jseaman1204@gmail.com"
OUTPUT_DIR   = r"C:\Users\ericd\Documents\MyVertexProject"

def has_url(val) -> bool:
    return bool(val) and str(val).startswith("http")

def check_index(db, year: str, program: str, mint: str) -> tuple[bool, bool]:
    """Returns (has_obverse, has_reverse) from coin_image_index."""
    if not year or not program:
        return False, False
    
    # Normalize: same logic as CoinImageService
    slug = (program.lower()
            .replace(" ", "-")
            .replace("/", "-")
            .replace("'", "")
            .replace(",", ""))
    
    base = f"{year}_{slug}"
    if mint and mint.strip():
        base_mint = f"{year}_{mint.strip()}_{slug}"
    else:
        base_mint = None

    has_obv = False
    has_rev = False

    for doc_id in [f"{base}_obverse", f"{base}_reverse",
                   *(([f"{base_mint}_obverse", f"{base_mint}_reverse"]) if base_mint else [])]:
        try:
            snap = db.collection("coin_image_index").document(doc_id).get()
            if snap.exists:
                if "obverse" in doc_id:
                    has_obv = True
                else:
                    has_rev = True
        except Exception:
            pass

    return has_obv, has_rev


def main():
    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT)

    print(f"Loading coins for {TARGET_EMAIL}...")
    coins = list(
        db.collection("users").document(TARGET_EMAIL).collection("coins").stream()
    )
    print(f"  {len(coins):,} coins loaded")

    gap_rows = []
    no_personal_photo = 0
    no_ref_image = 0
    no_images_at_all = 0
    fully_covered = 0

    for i, doc in enumerate(coins):
        data = doc.to_dict() or {}
        
        obv_url = str(data.get("image_url_obverse", "") or "")
        rev_url = str(data.get("image_url_reverse", "") or "")
        has_personal_obv = has_url(obv_url)
        has_personal_rev = has_url(rev_url)

        year    = str(data.get("Year", "") or "").replace(".0", "").strip()
        program = str(data.get("Program/Series", "") or "").strip()
        mint    = str(data.get("Mint Mark", "") or "").strip()
        denom   = str(data.get("Denomination", "") or "").strip()
        country = str(data.get("Country", "US") or "US").strip()
        cond    = str(data.get("Condition", "") or "").strip()
        cost    = str(data.get("Cost", "") or "").strip()

        if has_personal_obv and has_personal_rev:
            fully_covered += 1
            continue

        # Check reference index for missing sides
        has_ref_obv, has_ref_rev = check_index(db, year, program, mint)

        personal_status = (
            "Both" if (has_personal_obv and has_personal_rev) else
            "Obverse only" if has_personal_obv else
            "Reverse only" if has_personal_rev else
            "None"
        )
        ref_status = (
            "Both" if (has_ref_obv and has_ref_rev) else
            "Obverse only" if has_ref_obv else
            "Reverse only" if has_ref_rev else
            "None"
        )

        fully_missing = not has_personal_obv and not has_personal_rev and not has_ref_obv and not has_ref_rev

        gap_rows.append({
            "coin_id":         doc.id,
            "year":            year,
            "program":         program,
            "denomination":    denom,
            "mint_mark":       mint,
            "country":         country,
            "condition":       cond,
            "cost":            cost,
            "personal_photos": personal_status,
            "reference_imgs":  ref_status,
            "fully_missing":   "YES" if fully_missing else "no",
            "obverse_url":     obv_url[:80] + "..." if len(obv_url) > 80 else obv_url,
            "reverse_url":     rev_url[:80] + "..." if len(rev_url) > 80 else rev_url,
        })

        if not has_personal_obv and not has_personal_rev:
            no_personal_photo += 1
        if not has_ref_obv and not has_ref_rev:
            no_ref_image += 1
        if fully_missing:
            no_images_at_all += 1

        if (i + 1) % 500 == 0:
            print(f"  Checked {i+1:,}/{len(coins):,}...")

    # ── Write CSV ─────────────────────────────────────────────────────────
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(OUTPUT_DIR, f"AJ_image_gap_report_{date_str}.csv")

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=gap_rows[0].keys() if gap_rows else [])
        writer.writeheader()
        writer.writerows(gap_rows)

    # Sort by fully_missing first for easier reading
    gap_rows.sort(key=lambda r: (0 if r["fully_missing"] == "YES" else 1, r["year"], r["program"]))
    
    # Rewrite sorted
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=gap_rows[0].keys() if gap_rows else [])
        writer.writeheader()
        writer.writerows(gap_rows)

    print(f"\n{'='*55}")
    print(f"  AJ Image Gap Report — {date_str}")
    print(f"{'='*55}")
    print(f"  Total coins           : {len(coins):,}")
    print(f"  Fully covered (skip)  : {fully_covered:,}")
    print(f"  Coins in gap report   : {len(gap_rows):,}")
    print(f"    → No personal photo : {no_personal_photo:,}")
    print(f"    → No reference img  : {no_ref_image:,}")
    print(f"    → ZERO images total : {no_images_at_all:,}  ← Priority targets")
    print(f"\n  Output: {out_path}")

    # Show top 20 fully-missing
    fully = [r for r in gap_rows if r["fully_missing"] == "YES"]
    if fully:
        print(f"\n  Top priority (no images at all) — {len(fully)} coins:")
        for r in fully[:25]:
            print(f"    {r['year']:>6}  {r['program'][:40]:<40}  {r['denomination']}")


if __name__ == "__main__":
    main()
