"""
cert_image_scraper.py
=====================
Automated image scraper for AJ's graded currency collection.

Since no cert numbers are stored in Firestore (descriptions only say "PMG"/"PCGS"),
this script uses Heritage Auctions archive search to find representative images
for each graded note by searching with description keywords.

Steps:
1. Query Firestore for all 32 graded docs (PMG/PCGS mentioned in Description)
2. For each doc, build a search query from description keywords
3. Search Heritage Auctions currency archive
4. Find best matching image (thumbnail URL → high-res URL)
5. Download image
6. Upload to Firebase Storage → get public HTTPS URL
7. Update Firestore doc with image URLs and cert metadata
8. Write full Markdown report
"""

import os, sys, re, json, time, requests
from urllib.parse import urlencode, quote_plus
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Config ─────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
KEY_PATH    = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")
USER_EMAIL  = "jseaman1204@gmail.com"
COLLECTION  = f"users/{USER_EMAIL}/currency"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"
REPORT_DIR  = r"C:\Users\ericd\.gemini\antigravity\brain\26eebf0f-3c8f-47c1-940b-b41df002779f"
REPORT_PATH = os.path.join(REPORT_DIR, "cert_scraper_results.md")
SCRATCH_DIR = os.path.join(SCRIPT_DIR, "_cert_scraper_cache")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

# ── Firebase / Firestore ────────────────────────────────────────────────────
import firebase_admin
from firebase_admin import credentials, firestore as fs_admin
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))
db = fs_admin.client()

# ── GCS ────────────────────────────────────────────────────────────────────
from google.cloud import storage as gcs_storage
from google.oauth2 import service_account

sa_creds = service_account.Credentials.from_service_account_file(KEY_PATH)
gcs_client = gcs_storage.Client(credentials=sa_creds, project="studio-9101802118-8c9a8")
bucket = gcs_client.bucket(BUCKET_NAME)

# ── HTTP helper ────────────────────────────────────────────────────────────
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
})

def ha_search(query: str, max_results: int = 10) -> list[dict]:
    """Search Heritage Auctions currency archive; return list of {title, img_url, lot_url}."""
    url = f"https://currency.ha.com/c/search-results.zx?Nty=1&Ntt={quote_plus(query)}&N=790+231+4294967291"
    try:
        r = SESSION.get(url, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"    ⚠ HA search failed: {e}")
        return []

    # Extract all dyn1.heritagestatic.com image URLs + alt text
    img_pattern = re.compile(
        r'<img[^>]+src="(https://dyn1\.heritagestatic\.com/ha\?[^"]+)"[^>]*alt="([^"]*)"',
        re.IGNORECASE
    )
    results = []
    for m in img_pattern.finditer(r.text):
        thumb_url = m.group(1)
        alt_text  = m.group(2)
        if not alt_text.strip() or "logo" in alt_text.lower():
            continue
        # Build hi-res version: replace w=120&h=300 with w=900&h=600
        hi_res = re.sub(r'w=\d+', 'w=900', thumb_url)
        hi_res = re.sub(r'h=\d+', 'h=600', hi_res)
        results.append({"title": alt_text, "img_url": hi_res, "thumb_url": thumb_url})
        if len(results) >= max_results:
            break
    return results

def download_image(url: str, timeout: int = 30) -> bytes | None:
    """Download an image URL, return bytes or None."""
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code == 200 and len(r.content) > 2000:
            return r.content
    except Exception as e:
        print(f"      ⚠ Download error: {e}")
    return None

def upload_to_gcs(img_bytes: bytes, gcs_path: str, content_type: str = "image/jpeg") -> str | None:
    """Upload to GCS, make public, return HTTPS URL."""
    try:
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(img_bytes, content_type=content_type)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"      ⚠ GCS upload error: {e}")
        return None

def build_search_query(data: dict) -> str:
    """Build a Heritage Auctions search query from Firestore doc fields."""
    desc  = str(data.get("Description", "")).strip()
    year  = str(data.get("Year", "")).strip()
    denom = str(data.get("Denomination", "")).strip()
    cond  = str(data.get("Condition", "")).strip()

    # Remove noise words
    noise = re.compile(
        r'\b(PMG|PCGS|PPQ|EPQ|EDQ|large|size|Large|Size|note|Note|the|and|of|'
        r'previously|mounted|consecutive|serial|numbers?|consecutive)\b',
        re.IGNORECASE
    )
    clean_desc = noise.sub(" ", desc).strip()
    clean_desc = re.sub(r'\s{2,}', ' ', clean_desc)

    # Extract grade if visible in description or condition
    grade_match = re.search(r'(?:unc|AU|VF|EF|CU|gem)\s*[-]?\s*(\d{2})', desc + " " + cond, re.IGNORECASE)
    grade = grade_match.group(0).strip() if grade_match else ""

    parts = []
    if year:
        parts.append(year)
    parts.append(clean_desc[:60])
    if grade:
        parts.append(grade)

    return " ".join(p for p in parts if p).strip()

def score_result(result: dict, query: str, service: str) -> int:
    """Score a search result by relevance (higher=better)."""
    title = result["title"].lower()
    query_words = set(query.lower().split())
    score = sum(1 for w in query_words if w in title)
    if service.lower() in title:
        score += 3
    return score

def update_firestore(doc_id: str, fields: dict):
    """Update a Firestore document with the given fields."""
    try:
        db.collection(COLLECTION).document(doc_id).update(fields)
        return True
    except Exception as e:
        print(f"      ⚠ Firestore update error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

print("="*70)
print("CERT IMAGE SCRAPER – AJ's Graded Currency Collection")
print("="*70)

# ── Step 1: Pull graded docs ────────────────────────────────────────────────
print("\nSTEP 1: Fetching graded currency documents from Firestore ...")
raw_docs = list(db.collection(COLLECTION).stream())
print(f"  → {len(raw_docs)} total docs fetched")

graded = []
for doc in raw_docs:
    d = doc.to_dict() or {}
    all_text = " ".join(str(v) for v in d.values() if v).lower()
    if "pmg" in all_text:
        graded.append({"doc_id": doc.id, "data": d, "service": "PMG"})
    elif "pcgs" in all_text:
        graded.append({"doc_id": doc.id, "data": d, "service": "PCGS"})

print(f"  → {len(graded)} graded docs identified")
print(f"     PMG:  {sum(1 for g in graded if g['service']=='PMG')}")
print(f"     PCGS: {sum(1 for g in graded if g['service']=='PCGS')}")

# ── Step 2-5: Search, download, upload, update ──────────────────────────────
results_log = []
success_count = 0
no_image_count = 0
error_count = 0

print(f"\nSTEP 2-5: Processing {len(graded)} graded docs ...")
print("-"*70)

for idx, g in enumerate(graded, 1):
    doc_id  = g["doc_id"]
    data    = g["data"]
    service = g["service"]
    ref_num = data.get("Personal Ref #", "?")
    desc    = data.get("Description", "")
    year    = data.get("Year", "")
    denom   = data.get("Denomination", "")
    cond    = data.get("Condition", "")

    print(f"\n[{idx:2}/{len(graded)}] Ref#{ref_num}  {service}  {desc[:65]}")

    entry = {
        "doc_id":    doc_id,
        "ref_num":   ref_num,
        "service":   service,
        "description": desc,
        "year":      year,
        "denom":     denom,
        "condition": cond,
        "query":     "",
        "image_url": None,
        "gcs_path":  None,
        "public_url": None,
        "matched_title": None,
        "status":    "pending",
        "error":     None,
    }

    # Build search query
    query = build_search_query(data)
    entry["query"] = query
    print(f"  Search: {query!r}")

    # Search HA
    search_results = ha_search(query, max_results=15)
    if not search_results:
        # Try a simpler fallback query
        fallback = f"{year} {denom} {service}"
        print(f"  No results; trying fallback: {fallback!r}")
        search_results = ha_search(fallback, max_results=10)

    if not search_results:
        print(f"  ✗ No search results found")
        entry["status"] = "no_results"
        no_image_count += 1
        results_log.append(entry)
        time.sleep(1)
        continue

    # Score and pick best result
    scored = [(score_result(r, query, service), r) for r in search_results]
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best = scored[0]
    print(f"  Best match (score={best_score}): {best['title'][:80]}")
    entry["matched_title"] = best["title"]
    entry["image_url"] = best["img_url"]

    # Download image
    img_bytes = download_image(best["img_url"])
    if not img_bytes:
        # Try thumbnail
        img_bytes = download_image(best["thumb_url"])

    if not img_bytes:
        print(f"  ✗ Image download failed")
        entry["status"] = "download_failed"
        no_image_count += 1
        results_log.append(entry)
        time.sleep(1)
        continue

    print(f"  ✓ Downloaded {len(img_bytes):,} bytes")

    # Upload to GCS
    gcs_path = f"users/{USER_EMAIL}/currency/{doc_id}/obverse.jpg"
    public_url = upload_to_gcs(img_bytes, gcs_path)

    if not public_url:
        entry["status"] = "upload_failed"
        error_count += 1
        results_log.append(entry)
        time.sleep(1)
        continue

    entry["gcs_path"]   = gcs_path
    entry["public_url"] = public_url
    print(f"  ✓ Uploaded: {public_url}")

    # Parse grade from description / condition
    grade_str = cond.strip()

    # Build Firestore update
    cert_lookup_url = (
        f"https://currency.ha.com/c/search-results.zx?Nty=1&Ntt={quote_plus(query)}&N=790+231+4294967291"
    )
    firestore_update = {
        "image_url_obverse":  public_url,
        "cert_source":        service,
        "cert_lookup_url":    cert_lookup_url,
        "cert_matched_title": best["title"],
        "cert_image_source":  "heritage_auctions_archive",
    }
    if service == "PMG":
        firestore_update["pmg_grade"] = grade_str
    else:
        firestore_update["pcgs_grade"] = grade_str

    ok = update_firestore(doc_id, firestore_update)
    if ok:
        print(f"  ✓ Firestore updated")
        entry["status"] = "success"
        success_count += 1
    else:
        entry["status"] = "firestore_error"
        error_count += 1

    results_log.append(entry)
    time.sleep(2)  # Be polite to HA servers

# ── Step 6: Write report ────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("STEP 6: Writing report ...")

total_graded = len(graded)
total_docs   = len(raw_docs)

report = f"""# AJ's Graded Currency – Cert Scraper Results
_Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_

---

## Summary

| Metric | Count |
|--------|-------|
| Total currency documents | {total_docs} |
| Documents with PMG/PCGS label | {total_graded} |
| PMG graded | {sum(1 for g in graded if g['service']=='PMG')} |
| PCGS graded | {sum(1 for g in graded if g['service']=='PCGS')} |
| **Images successfully retrieved & uploaded** | **{success_count}** |
| No search results | {sum(1 for e in results_log if e['status']=='no_results')} |
| Download failed | {sum(1 for e in results_log if e['status']=='download_failed')} |
| Upload/Firestore errors | {error_count} |

---

## Key Finding: No Cert Numbers in Database

> **AJ's currency documents do NOT contain PMG or PCGS certification numbers.**
> The descriptions only indicate the grading *service* (e.g., `"$5 Legal Tender Note large size PMG"`
> or `"PCGS PPQ66"`), but no actual cert numbers (like `#12345678`) are stored in any field.
>
> Without cert numbers, direct cert lookup on [pmgnotes.com/certlookup](https://www.pmgnotes.com/certlookup/)
> (which requires cert# + grade) or [pcgs.com/cert](https://www.pcgs.com/cert/) is not possible.
>
> **Workaround used:** Heritage Auctions archive search was used to find representative images
> of similar graded notes matching the description keywords.

---

## All Graded Documents

### PMG Documents ({sum(1 for g in graded if g['service']=='PMG')} total)

| Ref# | Description | Year | Grade/Condition | Status |
|------|-------------|------|-----------------|--------|
"""

for e in results_log:
    if e["service"] == "PMG":
        status_icon = "✅" if e["status"] == "success" else "❌"
        report += f"| {e['ref_num']} | {e['description'][:60]} | {e['year']} | {e['condition'][:30]} | {status_icon} {e['status']} |\n"

report += f"""
### PCGS Documents ({sum(1 for g in graded if g['service']=='PCGS')} total)

| Ref# | Description | Year | Grade/Condition | Status |
|------|-------------|------|-----------------|--------|
"""

for e in results_log:
    if e["service"] == "PCGS":
        status_icon = "✅" if e["status"] == "success" else "❌"
        report += f"| {e['ref_num']} | {e['description'][:60]} | {e['year']} | {e['condition'][:30]} | {status_icon} {e['status']} |\n"

report += """
---

## Detailed Results

"""

for e in results_log:
    status_icon = "✅" if e["status"] == "success" else "❌"
    report += f"""### {status_icon} Ref#{e['ref_num']} – {e['service']} – {e['description'][:70]}

- **Doc ID:** `{e['doc_id']}`
- **Service:** {e['service']}
- **Description:** {e['description']}
- **Year:** {e['year']}
- **Denomination:** {e['denom']}
- **Condition/Grade:** {e['condition']}
- **Search Query Used:** `{e['query']}`
- **Status:** {e['status']}
"""
    if e['matched_title']:
        report += f"- **Matched Auction Title:** {e['matched_title']}\n"
    if e['public_url']:
        report += f"- **GCS Path:** `{e['gcs_path']}`\n"
        report += f"- **Public URL:** {e['public_url']}\n"
    if e['error']:
        report += f"- **Error:** {e['error']}\n"
    report += "\n"

report += """---

## Recommendations

1. **Add cert numbers to the database**: For each graded note, the PMG or PCGS
   certification number should be recorded. This can be done by:
   - Physically inspecting each note holder and entering the cert number
   - Scanning the QR code on each PMG/PCGS holder
   - For PMG: cert is in format `XXXXXXX-XXX` (printed on label)
   - For PCGS: cert is an 8-digit number on the label

2. **Once cert numbers are added**, this script can be re-run to get:
   - The exact note description from the grading service
   - Official grade designation
   - The actual graded-note images from PMG/PCGS

3. **Current images** were sourced from Heritage Auctions archive as representative
   examples of the same note type and grade — they are NOT photos of AJ's actual notes.

4. **Fields updated in Firestore** (for successfully processed docs):
   - `image_url_obverse`: Public GCS HTTPS URL
   - `cert_source`: 'PMG' or 'PCGS'
   - `pmg_grade` / `pcgs_grade`: Condition from Firestore record
   - `cert_lookup_url`: Heritage Auctions search URL used
   - `cert_matched_title`: Title of matched auction lot
   - `cert_image_source`: 'heritage_auctions_archive'
"""

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

print(f"  → Report saved to: {REPORT_PATH}")

# Also save JSON log
json_path = os.path.join(SCRATCH_DIR, "results_log.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(results_log, f, indent=2, ensure_ascii=False, default=str)
print(f"  → JSON log: {json_path}")

print(f"\n{'='*70}")
print(f"DONE")
print(f"  Total graded docs:     {total_graded}")
print(f"  Images retrieved:      {success_count}")
print(f"  No image available:    {no_image_count}")
print(f"  Errors:                {error_count}")
print(f"  Report: {REPORT_PATH}")
print("="*70)
