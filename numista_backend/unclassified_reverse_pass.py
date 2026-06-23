#!/usr/bin/env python3
"""
unclassified_reverse_pass.py  (v3 — verified Wikimedia filenames)
=================================================================
Reverse image enrichment for the 28 coins with blank denomination+program.

These coins have AI-generated obverse images. Their filenames encode the
series (e.g. 'barber_silver_coin', 'morgan_1888', 'indian-head-quarter-eagle').

Key corrections vs v2:
- All Wikimedia filenames are verified to exist (ends in .jpeg not .jpg for some)
- 'barber_silver_coin' with years 1865-1891 → Seated Liberty (not Barber, which
  starts 1892). Years 1892+ → Barber silver.
- morgan_1888, morgan_1890 → Morgan Dollar (verified file used)
- 1908 indian-head-quarter-eagle → Indian Head Quarter Eagle
"""

import csv
import io
import json
import os
import sys
import time
from collections import defaultdict
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
except Exception:
    pass

# ─── Config ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SA_KEY       = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
GAP_CSV      = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")
PASS1_LOG    = os.path.join(SCRIPT_DIR, "reverse_enrichment_log.json")
PASS2_LOG    = os.path.join(SCRIPT_DIR, "reverse_enrichment_pass2_log.json")
OUTPUT_LOG   = os.path.join(SCRIPT_DIR, "unclassified_reverse_log.json")
USER_EMAIL   = "jseaman1204@gmail.com"
BUCKET_NAME  = "numista-uploads-studio-9101802118-8c9a8"
WIKIMEDIA_UA = "NumistaAI/1.0 (eric@numista.ai)"
WIKIMEDIA_DELAY  = 0.5
REQUEST_TIMEOUT  = 25

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage

# ─── Verified Wikimedia filenames (all verified to exist via API) ────────────
SERIES_WIKI = {
    # Silver dollars — all verified OK
    "morgan_dollar":            "File:1893-S Morgan dollar reverse.jpg",
    "morgan_dollar_late":       "File:1889-p-morgan-dollar-reverse.jpg",
    "seated_liberty_dollar":    "File:Liberty Seated dollar reverse.jpg",
    # Quarters — all verified OK
    "barber_quarter":           "File:Barber quarter reverse.jpeg",
    "seated_liberty_quarter":   "File:1877-CC Seated Liberty quarter reverse.jpg",
    "washington_quarter":       "File:Circulated Washington quarter reverse.jpg",
    # Half dollars — all verified OK
    "barber_half":              "File:Barber half reverse.jpg",
    "walking_liberty":          "File:Walking Liberty Half Dollar 1945D Reverse.png",
    "franklin_half":            "File:Franklin Half 1963 D Reverse.png",
    # Dimes — all verified OK
    "barber_dime":              "File:Barber dime reverse.jpeg",
    "roosevelt_dime":           "File:2015-W proof Roosevelt dime reverse.jpg",
    # Nickels — all verified OK
    "buffalo_nickel":           "File:Indian Head Buffalo Reverse.jpg",
    # Cents — all verified OK
    "indian_head_cent":         "File:1859 Indian Head cent reverse.png",
    # Gold — all verified OK
    "indian_head_quarter_eagle": "File:1911-D Indian Head quarter eagle reverse.jpg",
    "indian_head_half_eagle":    "File:1916-S half eagle reverse.jpg",
    "indian_head_eagle":         "File:1911 Indian Head eagle reverse.jpg",
    # Generic groups (verified OK)
    "barber_silver":             "File:Barber quarter reverse.jpeg",         # Barber 1892-1916
    "seated_liberty_silver":     "File:1877-CC Seated Liberty quarter reverse.jpg",  # Seated Liberty era
}

def _year_to_series(yr: int, fname: str) -> str:
    """
    Infer the coin series from year + obverse filename.

    Important note: The AI-generated obverse images for these blank coins
    used the label 'barber_silver_coin' even for pre-Barber years (before 1892).
    The actual Barber series started in 1892. Pre-1892 'barber_silver_coin'
    images represent Seated Liberty era coins.

    Morgan dollar (1878-1921) images labeled 'morgan_YYYY' are correct.
    The 1908 S-mint coin has 'indian-head-quarter-eagle' in its URL (gold coin).
    """
    # Morgan dollar: explicit in filename
    if "morgan" in fname:
        return "morgan_dollar"
    # Indian Head gold quarter eagle: 1908-1929
    if "quarter_eagle" in fname:
        return "indian_head_quarter_eagle"
    # Indian Head gold half eagle: 1908-1929
    if "half_eagle" in fname and "quarter" not in fname:
        return "indian_head_half_eagle"
    # Indian Head gold eagle: 1907-1933
    if "indian_head_eagle" in fname and "quarter" not in fname and "half" not in fname:
        return "indian_head_eagle"
    # 'barber_silver_coin' — year determines actual era:
    if "barber_silver" in fname:
        if yr >= 1892:
            return "barber_silver"          # True Barber coinage 1892-1916
        elif yr >= 1840:
            return "seated_liberty_silver"  # Seated Liberty era (pre-1892)
        else:
            return "seated_liberty_silver"  # Earlier still
    # Walking Liberty half
    if "walking_liberty" in fname:
        return "walking_liberty"
    # Franklin half
    if "franklin" in fname:
        return "franklin_half"
    # Kennedy half
    if "kennedy" in fname:
        return "kennedy_half"
    # Buffalo/Indian Head nickel
    if "buffalo" in fname or "bison" in fname:
        return "buffalo_nickel"
    # Indian head cent
    if "indian_head_cent" in fname:
        return "indian_head_cent"
    # Year-based pure fallback (no filename hint)
    if yr == 0:
        return ""  # Cannot infer without year
    if 1878 <= yr <= 1921:
        return "morgan_dollar"   # Most common US silver dollar 1878-1921
    if 1892 <= yr <= 1916:
        return "barber_silver"
    if 1840 <= yr < 1892:
        return "seated_liberty_silver"
    if yr < 1840:
        return "seated_liberty_silver"  # or earlier, use same image
    return ""

def pick_series(year_str: str, obv_url: str) -> tuple:
    """Returns (series_key, wiki_filename) or ('', '')."""
    fname = obv_url.lower().replace("-", "_").replace(" ", "_")
    # Extract year
    try:
        yr = int(str(year_str).strip())
    except ValueError:
        yr = 0

    series = _year_to_series(yr, fname)
    if series and series in SERIES_WIKI:
        return series, SERIES_WIKI[series]
    return "", ""


# ─── Wikimedia helpers ────────────────────────────────────────────────────────

def resolve_wikimedia_url(filename: str) -> str:
    api_url = (
        "https://commons.wikimedia.org/w/api.php"
        "?action=query"
        f"&titles={quote(filename)}"
        "&prop=imageinfo"
        "&iiprop=url"
        "&format=json"
    )
    req = Request(api_url, headers={"User-Agent": WIKIMEDIA_UA})
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read())
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            if pid == "-1":
                return ""
            ii = page.get("imageinfo", [{}])
            return ii[0].get("url", "") if ii else ""
    except Exception as e:
        print(f"    [WARN] resolve error: {e}")
        return ""


def download_image(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": WIKIMEDIA_UA})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read()


def upload_to_gcs(bucket, doc_id: str, image_bytes: bytes, content_type: str) -> str:
    ext = "png" if "png" in content_type.lower() else "jpg"
    gcs_path = f"users/{USER_EMAIL}/coins/{doc_id}/reverse.{ext}"
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(image_bytes, content_type=content_type)
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{gcs_path}"


def _init_clients():
    cred = credentials.Certificate(SA_KEY)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    gcs_client = gcs_storage.Client.from_service_account_json(SA_KEY)
    bucket = gcs_client.bucket(BUCKET_NAME)
    return db, bucket


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print(f"UNCLASSIFIED REVERSE PASS v3 — {USER_EMAIL}")
    print("=" * 72)

    # Step 1: find candidates
    print(f"\n[1] Reading gap CSV...")
    processed_ids = set()
    for lp in [PASS1_LOG, PASS2_LOG]:
        if os.path.exists(lp):
            with open(lp, encoding="utf-8") as f:
                try:
                    for r in json.load(f):
                        if r.get("result") == "success":
                            processed_ids.add(r["doc_id"])
                except Exception:
                    pass

    candidates = []
    with open(GAP_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status", "").strip().upper() != "MISSING_REVERSE":
                continue
            doc_id = row.get("doc_id", "").strip()
            if not row.get("denomination", "").strip() and not row.get("program", "").strip():
                candidates.append(doc_id)

    print(f"    Blank denom+program MISSING_REVERSE: {len(candidates)}")
    print(f"    Already processed (pass1+pass2):     {len(processed_ids)}")

    # Step 2: Firestore fetch
    print(f"\n[2] Init clients...")
    db, bucket = _init_clients()
    print("    Ready")

    print(f"\n[2] Fetching {len(candidates)} docs from Firestore...")
    eligible = []
    skipped = defaultdict(int)

    for doc_id in candidates:
        ref = db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id)
        try:
            snap = ref.get()
        except Exception as e:
            skipped["fs_error"] += 1
            continue

        if not snap.exists:
            skipped["not_found"] += 1
            continue

        data = snap.to_dict()
        rev = (data.get("image_url_reverse") or "").strip()
        obv = (data.get("image_url_obverse") or "").strip()

        if rev:
            skipped["has_reverse"] += 1
            continue
        if not obv:
            skipped["no_obverse"] += 1
            continue

        eligible.append({
            "doc_id":   doc_id,
            "year":     str(data.get("Year") or data.get("year") or ""),
            "mint":     str(data.get("Mint Mark") or data.get("mint_mark") or ""),
            "denom":    str(data.get("Denomination") or data.get("denomination") or ""),
            "program":  str(data.get("Program/Series") or data.get("program") or ""),
            "obv":      obv,
        })

    print(f"    Eligible:          {len(eligible)}")
    for k, v in skipped.items():
        print(f"    Skipped ({k}): {v}")

    if not eligible:
        print("\n  Nothing to process.")
        with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        return

    # Steps 3-6
    print(f"\n[3-6] Processing {len(eligible)} coins...")
    results = []
    n_ok = n_skip = n_fail = 0
    by_series = defaultdict(int)

    for i, coin in enumerate(eligible, 1):
        doc_id = coin["doc_id"]
        year   = coin["year"]
        obv    = coin["obv"]

        print(f"\n  [{i:>2}/{len(eligible)}] {doc_id}")
        print(f"         year={year}  obv=...{obv[-55:]}")

        # Pick series + Wikimedia file
        series, wiki_file = pick_series(year, obv)
        if not wiki_file:
            print(f"         [SKIP] Cannot infer series")
            results.append({
                "doc_id": doc_id, "year": year,
                "result": "skipped_unidentifiable",
                "source": "", "gcs_url": "",
            })
            n_skip += 1
            continue

        print(f"         series={series!r}  file={wiki_file}")

        # Resolve URL
        time.sleep(WIKIMEDIA_DELAY)
        wiki_url = resolve_wikimedia_url(wiki_file)
        if not wiki_url:
            print(f"         [FAIL] URL resolve failed for {wiki_file}")
            results.append({
                "doc_id": doc_id, "year": year,
                "result": "url_resolve_failed",
                "source": wiki_file, "gcs_url": "",
            })
            n_fail += 1
            continue

        print(f"         resolved: {wiki_url[:80]}")

        # Download
        try:
            img = download_image(wiki_url)
        except Exception as e:
            print(f"         [FAIL] Download: {e}")
            results.append({
                "doc_id": doc_id, "year": year,
                "result": "download_failed",
                "source": wiki_file, "gcs_url": "", "error": str(e),
            })
            n_fail += 1
            continue

        ct = "image/png" if wiki_url.lower().endswith(".png") else "image/jpeg"

        # Upload GCS
        try:
            gcs_url = upload_to_gcs(bucket, doc_id, img, ct)
        except Exception as e:
            print(f"         [FAIL] GCS: {e}")
            results.append({
                "doc_id": doc_id, "year": year,
                "result": "gcs_failed", "source": wiki_file,
                "gcs_url": "", "error": str(e),
            })
            n_fail += 1
            continue

        # Firestore update
        try:
            ref = db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id)
            ref.update({
                "image_url_reverse":    gcs_url,
                "image_source_reverse": "wikimedia_commons",
            })
        except Exception as e:
            print(f"         [FAIL] Firestore: {e}")
            results.append({
                "doc_id": doc_id, "year": year,
                "result": "firestore_failed", "source": wiki_file,
                "gcs_url": gcs_url, "error": str(e),
            })
            n_fail += 1
            continue

        print(f"         OK -> {gcs_url}")
        results.append({
            "doc_id": doc_id, "year": year,
            "inferred_series": series,
            "result": "success",
            "source": f"direct_file:{wiki_file}",
            "gcs_url": gcs_url,
        })
        by_series[series] += 1
        n_ok += 1

    # Save log
    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 72)
    print("DONE — Unclassified Reverse Pass v3")
    print("=" * 72)
    print(f"  Candidates:                {len(candidates)}")
    print(f"  Eligible:                  {len(eligible)}")
    print(f"  Successful:                {n_ok}")
    print(f"  Skipped (unidentifiable):  {n_skip}")
    print(f"  Failures:                  {n_fail}")
    print()
    if by_series:
        print("  Series breakdown:")
        for s, c in sorted(by_series.items(), key=lambda x: -x[1]):
            print(f"    {c:>4}  {s}")
    print(f"\n  Log: {OUTPUT_LOG}")
    print("=" * 72)


if __name__ == "__main__":
    main()
