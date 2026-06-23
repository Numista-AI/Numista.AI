#!/usr/bin/env python3
"""
jseaman_reverse_pass2.py
========================
Second-pass reverse image enrichment for jseaman1204@gmail.com.

Targets:
  - 83 coins from pass-1 that had result != 'success'
  - 40 unclassified coins skipped in pass-1 (loaded from the gap CSV)

Uses correct, verified Wikimedia Commons URLs for each US coin series.
"""

import csv
import io
import json
import os
import re
import sys
import time
from collections import defaultdict
from urllib.parse import quote

# Force line-buffered stdout
try:
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
except Exception:
    pass

# ─── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SA_KEY       = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
GAP_CSV      = os.path.join(SCRIPT_DIR, "jseaman_image_gaps.csv")
PASS1_LOG    = os.path.join(SCRIPT_DIR, "reverse_enrichment_log.json")
PASS2_LOG    = os.path.join(SCRIPT_DIR, "reverse_enrichment_pass2_log.json")
USER_EMAIL   = "jseaman1204@gmail.com"
BUCKET       = "numista-uploads-studio-9101802118-8c9a8"
WIKIMEDIA_UA = "NumistaAI/1.0 (eric@numista.ai)"
WIKIMEDIA_DELAY = 0.25  # seconds between Wikimedia requests

# ─── Verified Wikimedia Direct-File URLs ──────────────────────────────────────
# Each series → exact Wikimedia Commons file URL (verified to exist)
SERIES_DIRECT_URLS = {
    # Buffalo / Indian Head Nickel (1913-1938)
    "buffalo_nickel":         "File:Indian Head Buffalo Reverse.jpg",
    "indian_head_nickel":     "File:Indian Head Buffalo Reverse.jpg",
    # Roosevelt Dime (1946-present)
    "roosevelt_dime":         "File:2015-W proof Roosevelt dime reverse.jpg",
    # Mercury Dime (1916-1945) — re-use the Wikimedia search from pass-1, it worked
    # Walking Liberty Half Dollar (1916-1947)
    "walking_liberty":        "File:Walking Liberty Half Dollar 1945D Reverse.png",
    "walking_liberty_half":   "File:Walking Liberty Half Dollar 1945D Reverse.png",
    # Franklin Half Dollar (1948-1963)
    "franklin_half":          "File:Franklin Half 1963 D Reverse.png",
    "franklin_half_dollar":   "File:Franklin Half 1963 D Reverse.png",
    # Indian Head Cent (1859-1909)
    "indian_head_cent":       "File:1859 Indian Head cent reverse.png",
    # Washington Quarter (1932-present)
    "washington_quarter":     "File:Circulated Washington quarter reverse.jpg",
}

# ─── Coin type classifier (same logic as pass-1) ─────────────────────────────
def classify_coin(denomination: str, program: str, year: str) -> str | None:
    den = (denomination or "").lower().strip()
    prg = (program or "").lower().strip()
    yr  = str(year or "").strip()

    # Nickel types
    if "nickel" in den or "nickel" in prg or "5 cents" in den or "five cent" in prg:
        if "buffalo" in prg or "indian head" in prg or "bison" in prg:
            return "buffalo_nickel"
        try:
            y = int(yr)
            if 1913 <= y <= 1938:
                return "buffalo_nickel"
            elif 1938 <= y <= 2024:
                return "jefferson_nickel"
        except ValueError:
            pass
        if "jefferson" in prg:
            return "jefferson_nickel"
        if "buffalo" in prg or "indian" in prg:
            return "buffalo_nickel"
        return "nickel"

    # Dime types
    if "dime" in den or "dime" in prg or "10 cents" in den:
        if "barber" in prg:
            return "barber_dime"
        if "mercury" in prg or "liberty head" in prg and "dime" in prg:
            return "mercury_dime"
        if "roosevelt" in prg:
            return "roosevelt_dime"
        try:
            y = int(yr)
            if y < 1916:
                return "barber_dime"
            elif 1916 <= y <= 1945:
                return "mercury_dime"
            else:
                return "roosevelt_dime"
        except ValueError:
            pass
        return "roosevelt_dime"

    # Quarter types
    if "quarter" in den or "25 cent" in den or "quarter" in prg:
        if "barber" in prg:
            return "barber_quarter"
        if "standing liberty" in prg:
            return "standing_liberty_quarter"
        if "washington" in prg or "women" in prg or "america" in prg:
            return "washington_quarter"
        try:
            y = int(yr)
            if y < 1916:
                return "barber_quarter"
            elif 1916 <= y <= 1930:
                return "standing_liberty_quarter"
            else:
                return "washington_quarter"
        except ValueError:
            pass
        return "washington_quarter"

    # Half Dollar types
    if "half" in den or "50 cent" in den or "half" in prg:
        if "barber" in prg or "liberty head" in prg and "half" in prg:
            return "barber_half"
        if "walking liberty" in prg or "walking" in prg:
            return "walking_liberty"
        if "franklin" in prg:
            return "franklin_half"
        if "kennedy" in prg:
            return "kennedy_half"
        try:
            y = int(yr)
            if y < 1916:
                return "barber_half"
            elif 1916 <= y <= 1947:
                return "walking_liberty"
            elif 1948 <= y <= 1963:
                return "franklin_half"
            else:
                return "kennedy_half"
        except ValueError:
            pass
        return "half_dollar"

    # Cent / Penny types
    if "cent" in den or "penny" in den or "1c" in den or den == "1" or "cent" in prg:
        if "indian head" in prg or "indian" in prg:
            return "indian_head_cent"
        if "wheat" in prg or "lincoln" in prg and ("wheat" in prg or "memorial" in prg):
            if "memorial" in prg:
                return "memorial_cent"
            return "wheat_cent"
        if "memorial" in prg:
            return "memorial_cent"
        try:
            y = int(yr)
            if y <= 1909:
                return "indian_head_cent"
            elif 1909 <= y <= 1958:
                return "wheat_cent"
            else:
                return "memorial_cent"
        except ValueError:
            pass
        return "cent"

    # Dollar
    if "dollar" in den or "dollar" in prg:
        return "dollar"

    return None

# ─── Wikimedia lookup ─────────────────────────────────────────────────────────
import requests as _requests_module

_wiki_session = None
_url_cache: dict[str, str | None] = {}
_wiki_delay_last = 0.0

def _get_wiki_session() -> _requests_module.Session:
    global _wiki_session
    if _wiki_session is None:
        _wiki_session = _requests_module.Session()
        _wiki_session.headers.update({"User-Agent": WIKIMEDIA_UA})
    return _wiki_session

def _wiki_delay():
    global _wiki_delay_last
    elapsed = time.time() - _wiki_delay_last
    if elapsed < WIKIMEDIA_DELAY:
        time.sleep(WIKIMEDIA_DELAY - elapsed)
    _wiki_delay_last = time.time()

def get_file_url(file_title: str) -> str | None:
    """Resolve a 'File:...' title to its download URL via Wikimedia API."""
    if file_title in _url_cache:
        return _url_cache[file_title]
    _wiki_delay()
    s = _get_wiki_session()
    try:
        r = s.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"action": "query", "titles": file_title,
                    "prop": "imageinfo", "iiprop": "url", "format": "json"},
            timeout=20,
        )
        for page in r.json().get("query", {}).get("pages", {}).values():
            info = page.get("imageinfo", [])
            if info:
                url = info[0]["url"]
                _url_cache[file_title] = url
                return url
    except Exception as e:
        print(f"    [wiki-err] {file_title}: {e}")
    _url_cache[file_title] = None
    return None

def wiki_search(query: str, limit: int = 3) -> list[str]:
    """Search Wikimedia Commons for file titles matching query."""
    _wiki_delay()
    s = _get_wiki_session()
    try:
        r = s.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": query,
                    "srnamespace": "6", "srlimit": str(limit), "format": "json"},
            timeout=20,
        )
        return [h["title"] for h in r.json().get("query", {}).get("search", [])]
    except Exception as e:
        print(f"    [wiki-search-err] {query}: {e}")
        return []

def find_reverse_url(coin_type: str, denomination: str, program: str, year: str) -> tuple[str, str] | tuple[None, None]:
    """
    Returns (image_url, source_label) or (None, None).
    Priority:
      1. Direct SERIES_DIRECT_URLS lookup (verified file title → URL)
      2. Wikimedia search using series-appropriate query
    """
    # 1. Direct file lookup
    direct_file = SERIES_DIRECT_URLS.get(coin_type)
    if direct_file:
        url = get_file_url(direct_file)
        if url:
            return url, f"direct_file:{direct_file}"

    # 2. Series-specific Wikimedia search queries
    search_queries = _build_search_queries(coin_type, denomination, program, year)
    for q in search_queries:
        results = wiki_search(q, limit=5)
        for title in results:
            tl = title.lower()
            # Skip obverse/portrait images
            if any(k in tl for k in ["obverse","portrait","obv","front","face"]):
                continue
            # Prefer reverse
            is_reverse = any(k in tl for k in ["reverse","rev","back"])
            url = get_file_url(title)
            if url:
                return url, f"wikimedia_search:{title}"
        # If first search found something, return it
    return None, None

def _build_search_queries(coin_type: str, denomination: str, program: str, year: str) -> list[str]:
    queries = []
    prg = (program or "").strip()
    yr  = (year or "").strip()

    if coin_type == "buffalo_nickel":
        queries = ["buffalo nickel reverse bison five cents", "Indian Head nickel reverse 1936"]
    elif coin_type == "jefferson_nickel":
        queries = ["Jefferson nickel reverse Monticello", "US nickel reverse Monticello Jefferson"]
    elif coin_type == "barber_dime":
        queries = ["Barber dime reverse wreath", f"Barber dime reverse {yr}"]
    elif coin_type == "mercury_dime":
        queries = ["Mercury dime reverse fasces torch", "Liberty head dime reverse fasces"]
    elif coin_type == "roosevelt_dime":
        queries = ["Roosevelt dime reverse torch olive oak", "US dime reverse 2005"]
    elif coin_type == "barber_quarter":
        queries = ["Barber quarter reverse eagle", f"Barber quarter reverse {yr}"]
    elif coin_type == "standing_liberty_quarter":
        queries = ["Standing Liberty quarter reverse eagle", "standing liberty quarter reverse"]
    elif coin_type == "washington_quarter":
        queries = ["Washington quarter reverse eagle", "Circulated Washington quarter reverse"]
    elif coin_type == "barber_half":
        queries = ["Barber half dollar reverse eagle", "liberty head half dollar reverse"]
    elif coin_type == "walking_liberty":
        queries = ["Walking Liberty half dollar reverse eagle", "walking liberty half reverse 1945"]
    elif coin_type == "franklin_half":
        queries = ["Franklin half dollar reverse Liberty Bell", "Franklin Half 1963 reverse"]
    elif coin_type == "kennedy_half":
        queries = ["Kennedy half dollar reverse Presidential seal", "Kennedy half reverse eagle"]
    elif coin_type == "indian_head_cent":
        queries = ["Indian head cent reverse ONE CENT wreath", "1907 Indian head penny reverse"]
    elif coin_type == "wheat_cent":
        queries = ["Lincoln wheat cent reverse ONE CENT wheat", "wheat penny reverse 1909"]
    elif coin_type == "memorial_cent":
        queries = ["Lincoln Memorial cent reverse", "Lincoln penny Memorial reverse"]
    elif coin_type == "dollar":
        queries = [f"{prg} reverse", f"US dollar reverse {yr}"]
    else:
        queries = [f"{prg} reverse", f"{denomination} {yr} reverse United States coin"]

    return [q for q in queries if q.strip()]

# ─── GCS + Firestore ──────────────────────────────────────────────────────────
from google.oauth2 import service_account
from google.cloud import firestore, storage

def _init_clients():
    creds = service_account.Credentials.from_service_account_file(SA_KEY)
    db    = firestore.Client(project=creds.project_id, credentials=creds)
    gcs   = storage.Client(project=creds.project_id, credentials=creds)
    bucket = gcs.bucket(BUCKET)
    return db, bucket

def upload_image(bucket, doc_id: str, image_url: str) -> str | None:
    """Download image_url and upload to GCS. Returns public URL or None.

    NOTE: The bucket uses uniform bucket-level access (IAM), so we must NOT
    call blob.make_public() (which sets ACLs). Instead, we construct the
    storage.googleapis.com public URL directly — the bucket already has
    allUsers:storage.objectViewer set at the IAM level (evidenced by pass-1 working).
    """
    s = _get_wiki_session()
    try:
        resp = s.get(image_url, timeout=30, stream=True)
        if resp.status_code != 200:
            print(f"      ✗ HTTP {resp.status_code} from {image_url[:70]}")
            return None
        ext  = image_url.rsplit(".", 1)[-1].lower().split("?")[0] or "jpg"
        if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
            ext = "jpg"
        ct_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                  "png": "image/png",  "gif":  "image/gif",
                  "webp":"image/webp"}
        content_type = ct_map.get(ext, "image/jpeg")
        gcs_path = f"users/{USER_EMAIL}/coins/{doc_id}/reverse.{ext}"
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(resp.content, content_type=content_type)
        # Construct public URL without calling make_public() (bucket uses uniform IAM)
        public_url = f"https://storage.googleapis.com/{BUCKET}/{gcs_path}"
        return public_url
    except Exception as e:
        print(f"      ✗ Upload error: {e}")
        return None

def update_firestore(db, doc_id: str, public_url: str, source: str) -> bool:
    """Update the coin document's reverse image fields."""
    try:
        ref = db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id)
        ref.update({
            "image_url_reverse": public_url,
            "reverse_image_source": source,
            "reverse_image_enriched": True,
        })
        return True
    except Exception as e:
        print(f"      ✗ Firestore update error: {e}")
        return False

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("[init] Loading pass-1 log...")
    with open(PASS1_LOG, encoding="utf-8") as f:
        pass1_records = json.load(f)

    # 1. Failed records from pass-1
    failed_records = [r for r in pass1_records if r.get("result") != "success"]
    failed_doc_ids = {r["doc_id"] for r in failed_records}
    failed_map     = {r["doc_id"]: r for r in failed_records}
    print(f"[init] {len(failed_records)} failed/not-found records from pass-1")

    # 2. Unclassified (skipped) coins from the gap CSV
    print(f"[init] Loading gap CSV: {GAP_CSV}")
    unclassified_rows = []
    all_gap_doc_ids = set()
    with open(GAP_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status", "").strip() not in ("obverse_only", "missing_reverse", ""):
                continue
            doc_id = row.get("doc_id", "").strip()
            if not doc_id:
                continue
            all_gap_doc_ids.add(doc_id)
            # Already succeeded in pass-1? skip
            success_ids = {r["doc_id"] for r in pass1_records if r.get("result") == "success"}
            if doc_id in success_ids:
                continue
            # Already in failed list
            if doc_id in failed_doc_ids:
                continue
            # Skipped (unclassified) — include now
            denom   = row.get("denomination", "").strip()
            program = row.get("program", "").strip()
            year    = row.get("year", "").strip()
            mint    = row.get("mint_mark", "").strip()
            # If still looks unclassifiable (blank denom AND blank program), skip
            if not denom and not program:
                continue
            unclassified_rows.append({
                "doc_id": doc_id,
                "denomination": denom,
                "program": program,
                "year": year,
                "mint_mark": mint,
            })

    print(f"[init] {len(unclassified_rows)} unclassified coins to process")

    # Combine: failed + unclassified
    to_process = []
    # Add failed
    for r in failed_records:
        to_process.append({
            "doc_id":       r["doc_id"],
            "denomination": r.get("denomination", ""),
            "program":      r.get("program", ""),
            "year":         r.get("year", ""),
            "mint_mark":    r.get("mint_mark", ""),
        })
    # Add unclassified
    to_process.extend(unclassified_rows)

    total = len(to_process)
    print(f"[init] Total to process this pass: {total}")
    print()

    # Init clients
    print("[init] Connecting to Firestore + GCS...")
    db, bucket = _init_clients()
    print("[init] ✓ Ready")
    print()

    results = []
    n_success = 0
    n_not_found = 0
    n_dl_fail = 0
    n_fs_fail = 0
    by_source: dict[str, int] = defaultdict(int)

    for idx, coin in enumerate(to_process, 1):
        doc_id = coin["doc_id"]
        denom  = coin["denomination"]
        program= coin["program"]
        year   = coin["year"]
        mint   = coin["mint_mark"]

        coin_type = classify_coin(denom, program, year)
        label = f"{denom:<18} {year:<6} {mint:<3} {program:<30} type={coin_type or '?'}"
        print(f"[{idx:4}/{total}] {label}")

        # Find image URL
        image_url, source = find_reverse_url(coin_type or "", denom, program, year)

        if not image_url:
            print(f"    ✗ No reverse found")
            n_not_found += 1
            results.append({**coin, "result": "not_found", "source": "", "coin_type": coin_type})
            continue

        short_url = image_url[:80] + "…" if len(image_url) > 80 else image_url
        print(f"    ✓ {source.split(':')[0]}: {short_url}")

        # Upload to GCS
        public_url = upload_image(bucket, doc_id, image_url)
        if not public_url:
            n_dl_fail += 1
            results.append({**coin, "result": "download_failed", "source": source, "coin_type": coin_type})
            print(f"    ✗ Download/upload failed")
            continue

        short_pub = public_url[:80] + "…" if len(public_url) > 80 else public_url
        print(f"      ✓ Written: {short_pub}")

        # Update Firestore
        ok = update_firestore(db, doc_id, public_url, source)
        if not ok:
            n_fs_fail += 1
            results.append({**coin, "result": "firestore_failed", "source": source,
                             "gcs_url": public_url, "coin_type": coin_type})
            continue

        n_success += 1
        by_source[source.split(":")[0]] += 1
        results.append({**coin, "result": "success", "source": source,
                        "gcs_url": public_url, "coin_type": coin_type})

    # Write log
    with open(PASS2_LOG, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 72)
    print("DONE — Pass-2 LIVE RUN complete")
    print(f"  ✓ Success        : {n_success}")
    print(f"  ✗ Not found      : {n_not_found}")
    print(f"  ✗ Download failed: {n_dl_fail}")
    print(f"  ✗ Firestore fail : {n_fs_fail}")
    print()
    print("  By source:")
    for src, cnt in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"    {cnt:3}  {src}")
    print("=" * 72)
    print(f"Log: {PASS2_LOG}")

if __name__ == "__main__":
    main()
