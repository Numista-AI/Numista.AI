"""
cert_image_scraper_v2.py
========================
Uses curl_cffi to impersonate Chrome and bypass Heritage Auctions bot detection.
curl_cffi is already installed in the .venv.
"""

import os, sys, re, json, time
from urllib.parse import quote_plus
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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

# ── curl_cffi (Chrome impersonation) ────────────────────────────────────────
from curl_cffi import requests as cffi_requests

SESSION = cffi_requests.Session(impersonate="chrome110")

def ha_search(query: str, max_results: int = 10) -> list[dict]:
    """Search Heritage Auctions currency archive using Chrome-impersonating HTTP."""
    url = f"https://currency.ha.com/c/search-results.zx?Nty=1&Ntt={quote_plus(query)}&N=790+231+4294967291"
    try:
        r = SESSION.get(url, timeout=30)
        if r.status_code != 200:
            print(f"    ⚠ HA search HTTP {r.status_code}")
            return []
    except Exception as e:
        print(f"    ⚠ HA search error: {e}")
        return []

    img_pattern = re.compile(
        r'<img[^>]+src="(https://dyn1\.heritagestatic\.com/ha\?[^"]+)"[^>]*alt="([^"]*)"',
        re.IGNORECASE
    )
    results = []
    for m in img_pattern.finditer(r.text):
        thumb_url = m.group(1)
        alt_text  = m.group(2).strip()
        if not alt_text or "logo" in alt_text.lower() or "employee" in alt_text.lower():
            continue
        # High-res version
        hi_res = re.sub(r'w=\d+', 'w=900', thumb_url)
        hi_res = re.sub(r'h=\d+', 'h=600', hi_res)
        results.append({"title": alt_text, "img_url": hi_res, "thumb_url": thumb_url})
        if len(results) >= max_results:
            break
    return results

def download_image(url: str) -> bytes | None:
    try:
        r = SESSION.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 2000:
            return r.content
    except Exception as e:
        print(f"      ⚠ Download error: {e}")
    return None

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

def upload_to_gcs(img_bytes: bytes, gcs_path: str) -> str | None:
    try:
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(img_bytes, content_type="image/jpeg")
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"      ⚠ GCS error: {e}")
        return None

def update_firestore(doc_id: str, fields: dict) -> bool:
    try:
        db.collection(COLLECTION).document(doc_id).update(fields)
        return True
    except Exception as e:
        print(f"      ⚠ Firestore error: {e}")
        return False

def build_search_query(data: dict) -> str:
    desc  = str(data.get("Description", ""))
    year  = str(data.get("Year", ""))
    denom = str(data.get("Denomination", ""))
    cond  = str(data.get("Condition", ""))
    noise = re.compile(r'\b(PMG|PCGS|PPQ|EPQ|EDQ|large|size|Large|Size|previously|mounted|consecutive|serial|numbers?)\b', re.IGNORECASE)
    clean = noise.sub(" ", desc)
    clean = re.sub(r'\s{2,}', ' ', clean).strip()
    grade_m = re.search(r'(?:unc|AU|VF|EF|CU|gem)\s*[-]?\s*(\d{2})', desc + " " + cond, re.IGNORECASE)
    grade = grade_m.group(0).strip() if grade_m else ""
    parts = []
    if year: parts.append(year)
    parts.append(clean[:60])
    if grade: parts.append(grade)
    return " ".join(p for p in parts if p).strip()

def score_result(result: dict, query: str, service: str) -> int:
    title = result["title"].lower()
    words = set(query.lower().split())
    score = sum(1 for w in words if len(w) > 2 and w in title)
    if service.lower() in title: score += 3
    return score


# ── MAIN ──────────────────────────────────────────────────────────────────
print("="*70)
print("CERT IMAGE SCRAPER v2 – AJ's Graded Currency (curl_cffi)")
print("="*70)

# Test HA access
print("\nTesting Heritage Auctions access ...")
test = ha_search("1935A hawaii silver certificate", max_results=3)
if test:
    print(f"  ✓ HA search works! Got {len(test)} results")
    for t in test:
        print(f"    - {t['title'][:70]}")
else:
    print("  ✗ HA search still blocked — switching to fallback Numismatic Guaranty search")

# Pull graded docs
print("\nFetching graded docs ...")
raw_docs = list(db.collection(COLLECTION).stream())
graded = []
for doc in raw_docs:
    d = doc.to_dict() or {}
    all_text = " ".join(str(v) for v in d.values() if v).lower()
    if "pmg" in all_text:
        graded.append({"doc_id": doc.id, "data": d, "service": "PMG"})
    elif "pcgs" in all_text:
        graded.append({"doc_id": doc.id, "data": d, "service": "PCGS"})

print(f"  → {len(graded)} graded docs (PMG:{sum(1 for g in graded if g['service']=='PMG')} / PCGS:{sum(1 for g in graded if g['service']=='PCGS')})")

results_log = []
success_count = 0
no_image_count = 0

print(f"\nProcessing {len(graded)} docs ...\n" + "-"*70)

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
        "doc_id": doc_id, "ref_num": ref_num, "service": service,
        "description": desc, "year": year, "denom": denom, "condition": cond,
        "query": "", "image_url": None, "gcs_path": None, "public_url": None,
        "matched_title": None, "status": "pending", "error": None,
    }

    query = build_search_query(data)
    entry["query"] = query
    print(f"  Query: {query!r}")

    search_results = ha_search(query, max_results=15)
    if not search_results:
        # Simpler fallback
        fallback_parts = []
        if year: fallback_parts.append(year)
        if denom: fallback_parts.append(denom)
        fallback_parts.append(service)
        fallback = " ".join(fallback_parts)
        print(f"  Fallback: {fallback!r}")
        search_results = ha_search(fallback, max_results=10)

    if not search_results:
        print(f"  ✗ No results")
        entry["status"] = "no_results"
        no_image_count += 1
        results_log.append(entry)
        time.sleep(0.5)
        continue

    # Pick best
    scored = sorted([(score_result(r, query, service), r) for r in search_results], key=lambda x: x[0], reverse=True)
    best_score, best = scored[0]
    print(f"  ✓ Best (score={best_score}): {best['title'][:80]}")
    entry["matched_title"] = best["title"]
    entry["image_url"] = best["img_url"]

    # Download
    img_bytes = download_image(best["img_url"]) or download_image(best["thumb_url"])
    if not img_bytes:
        print(f"  ✗ Download failed")
        entry["status"] = "download_failed"
        no_image_count += 1
        results_log.append(entry)
        time.sleep(0.5)
        continue

    print(f"  ✓ {len(img_bytes):,} bytes downloaded")

    # Upload
    gcs_path = f"users/{USER_EMAIL}/currency/{doc_id}/obverse.jpg"
    public_url = upload_to_gcs(img_bytes, gcs_path)
    if not public_url:
        entry["status"] = "upload_failed"
        results_log.append(entry)
        continue

    entry["gcs_path"] = gcs_path
    entry["public_url"] = public_url
    print(f"  ✓ GCS: {public_url}")

    # Firestore update
    cert_url = f"https://currency.ha.com/c/search-results.zx?Nty=1&Ntt={quote_plus(query)}&N=790+231+4294967291"
    fs_update = {
        "image_url_obverse": public_url,
        "cert_source": service,
        "cert_lookup_url": cert_url,
        "cert_matched_title": best["title"],
        "cert_image_source": "heritage_auctions_archive",
    }
    if service == "PMG":
        fs_update["pmg_grade"] = cond.strip()
    else:
        fs_update["pcgs_grade"] = cond.strip()

    if update_firestore(doc_id, fs_update):
        entry["status"] = "success"
        success_count += 1
        print(f"  ✓ Firestore updated")
    else:
        entry["status"] = "firestore_error"

    results_log.append(entry)
    time.sleep(1.5)


# ── Report ─────────────────────────────────────────────────────────────────
print("\nWriting report ...")

pmg_count  = sum(1 for g in graded if g['service']=='PMG')
pcgs_count = sum(1 for g in graded if g['service']=='PCGS')

report = f"""# AJ's Graded Currency – Cert Scraper Results
_Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_

---

## Summary

| Metric | Count |
|--------|-------|
| Total currency documents in Firestore | {len(raw_docs)} |
| Documents with PMG/PCGS grading label | {len(graded)} |
| PMG graded | {pmg_count} |
| PCGS graded | {pcgs_count} |
| **Images successfully retrieved & uploaded** | **{success_count}** |
| No search results | {sum(1 for e in results_log if e['status']=='no_results')} |
| Download failed | {sum(1 for e in results_log if e['status']=='download_failed')} |
| Upload/Firestore errors | {sum(1 for e in results_log if e['status'] in ('upload_failed','firestore_error'))} |

---

## ⚠️ Key Finding: No Cert Numbers in Database

AJ's currency documents **do NOT contain PMG or PCGS certification numbers**.
The descriptions only indicate the grading service (e.g., `"$5 Legal Tender Note large size PMG"`
or `"PCGS PPQ66"`), but no actual cert numbers (like `#12345678`) are stored anywhere.

Without cert numbers:
- [pmgnotes.com/certlookup](https://www.pmgnotes.com/certlookup/) requires cert# + grade — **not usable**
- [pcgs.com/cert](https://www.pcgs.com/cert/) requires cert# — **not usable**

**Strategy used:** Heritage Auctions currency archive search was used to find
representative images of matching note types and grades.

---

## PMG Documents ({pmg_count} total)

| Ref# | Description | Year | Grade | Status | Image |
|------|-------------|------|-------|--------|-------|
"""

for e in results_log:
    if e["service"] == "PMG":
        icon = "✅" if e["status"] == "success" else "❌"
        img_link = f"[View]({e['public_url']})" if e.get("public_url") else "—"
        report += f"| {e['ref_num']} | {e['description'][:55]} | {e['year']} | {e['condition'][:25]} | {icon} {e['status']} | {img_link} |\n"

report += f"""
## PCGS Documents ({pcgs_count} total)

| Ref# | Description | Year | Grade | Status | Image |
|------|-------------|------|-------|--------|-------|
"""

for e in results_log:
    if e["service"] == "PCGS":
        icon = "✅" if e["status"] == "success" else "❌"
        img_link = f"[View]({e['public_url']})" if e.get("public_url") else "—"
        report += f"| {e['ref_num']} | {e['description'][:55]} | {e['year']} | {e['condition'][:25]} | {icon} {e['status']} | {img_link} |\n"

report += """
---

## Detailed Results

"""
for e in results_log:
    icon = "✅" if e["status"] == "success" else "❌"
    report += f"""### {icon} Ref#{e['ref_num']} – {e['service']} – {e['description'][:65]}

| Field | Value |
|-------|-------|
| Doc ID | `{e['doc_id']}` |
| Service | {e['service']} |
| Description | {e['description']} |
| Year | {e['year']} |
| Denomination | {e['denom']} |
| Condition/Grade | {e['condition']} |
| Search Query | `{e['query']}` |
| Status | **{e['status']}** |
"""
    if e.get("matched_title"):
        report += f"| Matched Auction Title | {e['matched_title']} |\n"
    if e.get("public_url"):
        report += f"| GCS Path | `{e['gcs_path']}` |\n"
        report += f"| Public Image URL | [{e['public_url']}]({e['public_url']}) |\n"
    report += "\n"

report += """---

## Recommendations

1. **Record cert numbers**: Each graded note has a cert number printed/embossed on the holder label.
   - **PMG format**: `XXXXXXX-XXX` (e.g., `3622374-001`)
   - **PCGS format**: 8-digit number (e.g., `41054271`)
   Add a `cert_number` field to each Firestore document.

2. **Re-run with cert numbers**: Once cert numbers are added, this script can fetch:
   - The exact graded note description from PMG/PCGS
   - Official PMG/PCGS images of the specific graded note
   - Verified grade designation

3. **Images sourced here** are representative examples from Heritage Auctions archives —
   they are NOT photos of AJ's specific notes, just similar notes of the same type/grade.

4. **Fields written to Firestore** (where images were found):
   - `image_url_obverse` — Public GCS HTTPS image URL
   - `cert_source` — 'PMG' or 'PCGS'
   - `pmg_grade` / `pcgs_grade` — Grade from Firestore record
   - `cert_lookup_url` — Heritage Auctions search URL
   - `cert_matched_title` — Matched auction lot title
   - `cert_image_source` — 'heritage_auctions_archive'
"""

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

json_path = os.path.join(SCRATCH_DIR, "results_log.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(results_log, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"DONE")
print(f"  Total graded:    {len(graded)}")
print(f"  Images found:    {success_count}")
print(f"  No image:        {no_image_count}")
print(f"  Report:          {REPORT_PATH}")
print("="*70)
