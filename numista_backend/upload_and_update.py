"""
upload_and_update.py
====================
Takes collected_images.json (Heritage Auctions image URLs for 32 graded docs),
downloads each image, uploads to Firebase GCS, and updates Firestore.
"""
import os, sys, re, json, time, requests
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
CACHE_DIR   = os.path.join(SCRIPT_DIR, "_cert_scraper_cache")
COLLECTED   = os.path.join(CACHE_DIR, "collected_images.json")

os.makedirs(REPORT_DIR, exist_ok=True)
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)

import firebase_admin
from firebase_admin import credentials, firestore as fs_admin
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))
db = fs_admin.client()

from google.cloud import storage as gcs_storage
from google.oauth2 import service_account
sa_creds = service_account.Credentials.from_service_account_file(KEY_PATH)
gcs_client = gcs_storage.Client(credentials=sa_creds, project="studio-9101802118-8c9a8")
bucket = gcs_client.bucket(BUCKET_NAME)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Referer": "https://currency.ha.com/",
})

def download_image(url):
    try:
        r = SESSION.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
    except Exception as e:
        print(f"    ⚠ Download error: {e}")
    return None

def upload_gcs(img_bytes, gcs_path):
    try:
        blob = bucket.blob(gcs_path)
        blob.upload_from_string(img_bytes, content_type="image/jpeg")
        # Bucket uses uniform IAM access with allUsers objectViewer — no ACL needed
        return blob.public_url
    except Exception as e:
        print(f"    ⚠ GCS error: {e}")
        return None

def update_firestore(doc_id, fields):
    try:
        db.collection(COLLECTION).document(doc_id).update(fields)
        return True
    except Exception as e:
        print(f"    ⚠ Firestore error: {e}")
        return False

# Load collected images
with open(COLLECTED, encoding="utf-8") as f:
    collected = json.load(f)

print(f"="*70)
print(f"UPLOAD & UPDATE – {len(collected)} docs")
print(f"="*70)

results = []
success = 0
failed  = 0

for idx, item in enumerate(collected, 1):
    doc_id    = item["doc_id"]
    ref_num   = item["ref_num"]
    service   = item["service"]
    desc      = item["desc"]
    img_url   = item["img_url"]
    img_title = item["img_title"]
    cond      = item["cond"]

    print(f"\n[{idx:2}/{len(collected)}] Ref#{ref_num}  {service}  {desc[:55]}")
    print(f"  Img: {img_url}")

    # Download
    img_bytes = download_image(img_url)
    if not img_bytes:
        print(f"  ✗ Download failed")
        item["status"] = "download_failed"
        item["public_url"] = None
        results.append(item)
        failed += 1
        time.sleep(0.5)
        continue

    print(f"  ✓ Downloaded {len(img_bytes):,} bytes")

    # Upload
    gcs_path   = f"users/{USER_EMAIL}/currency/{doc_id}/obverse.jpg"
    public_url = upload_gcs(img_bytes, gcs_path)
    if not public_url:
        item["status"] = "upload_failed"
        item["public_url"] = None
        results.append(item)
        failed += 1
        time.sleep(0.5)
        continue

    print(f"  ✓ GCS: {public_url}")

    # Firestore
    cert_search_url = f"https://currency.ha.com/c/search/results.zx?term={quote_plus(desc)}&mode=archive"
    fs_fields = {
        "image_url_obverse":   public_url,
        "cert_source":         service,
        "cert_lookup_url":     cert_search_url,
        "cert_matched_title":  img_title,
        "cert_image_source":   "heritage_auctions_archive",
    }
    if service == "PMG":
        fs_fields["pmg_grade"]  = cond
    else:
        fs_fields["pcgs_grade"] = cond

    ok = update_firestore(doc_id, fs_fields)
    if ok:
        print(f"  ✓ Firestore updated")
        item["status"]     = "success"
        item["public_url"] = public_url
        success += 1
    else:
        item["status"]     = "firestore_error"
        item["public_url"] = public_url
        failed += 1

    results.append(item)
    time.sleep(1.0)

# ── Report ─────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"RESULTS: {success} success, {failed} failed")

# Identify missing docs (those not in collected)
raw_docs = list(db.collection(COLLECTION).stream())
all_graded_ids = set()
for doc in raw_docs:
    d = doc.to_dict() or {}
    all_text = " ".join(str(v) for v in d.values() if v).lower()
    if "pmg" in all_text or "pcgs" in all_text:
        all_graded_ids.add(doc.id)

collected_ids = {item["doc_id"] for item in collected}
missing_ids   = all_graded_ids - collected_ids
print(f"  {len(missing_ids)} docs had no image collected (rate-limited)")

# Build full report
report = f"""# AJ's Graded Currency – Cert Scraper Results
_Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_

---

## Summary

| Metric | Count |
|--------|-------|
| Total currency documents in Firestore | 413 |
| Documents with PMG/PCGS grading label | 32 |
| PMG graded | 13 |
| PCGS graded | 19 |
| **Images found via Heritage Auctions** | **{len(collected)}** |
| **Successfully uploaded to GCS** | **{success}** |
| Failed (download/upload/Firestore) | {failed} |
| Docs with no image (rate-limited) | {len(missing_ids)} |

---

## ⚠️ Key Finding: No Cert Numbers in Database

AJ's currency collection documents **do NOT contain PMG or PCGS certification numbers**.
The `Description` field mentions the grading service but no cert numbers are stored:

> Example: `"$5 Legal TenderNote large size PMG"` — no cert number.

Without cert numbers:
- **PMG** [certlookup](https://www.pmgnotes.com/certlookup/) requires both cert# + grade → **not usable**
- **PCGS** [cert lookup](https://www.pcgs.com/cert/) requires cert# → **not usable**

**Workaround used:** Heritage Auctions currency archive searched by description keywords.
Representative images of the same note type were used.

> ⚠️ Images are NOT photos of AJ's specific notes — they are representative examples
> from Heritage Auctions auction archives of the same note type and grade level.

---

## PMG Documents (13 total)

| Ref# | Description | Year | Grade/Condition | Status | Image |
|------|-------------|------|-----------------|--------|-------|
"""

collected_by_ref = {item["ref_num"]: item for item in results}
no_img_pmg  = []
no_img_pcgs = []

# PMG docs in order
pmg_refs = [("291","$5 Legal TenderNote large size PMG","1880","choice AU 58"),
            ("231","1 silver certificate Hawaii (FR2300) (SC Block) PMG CU64 EPQ","1935A","CU64"),
            ("364","$1000 3rd Bank of the United States PMG","","Select Unc 6"),
            ("203","$500 confederate note PMG","1864","Very Fine"),
            ("357","50C Fractional Currency PMG EPQ CHUNC 63","1869-75","Unc-63"),
            ("366","10 Silver Certificate Yellow Seal BA Block PMG EPQ65","1934A","Unc 65"),
            ("280","Federal Reserve Note Hawaii LB Block PMG","1934A","V Fine/E F"),
            ("348","$20 Federal Reserve Note Inverted Back error FR1978 PMG","1985","Unc-64 Prem"),
            ("324","$10 Falls Village Iron Bank PMG EDQ63","1850s","gem"),
            ("250","$1 Federal Reserve Bank Note Large size PMG EPQ 65","1918","gem unc"),
            ("320","$1 Bank of Windsor Vermont PMG","1830s","gem unc-66"),
            ("229","$10 National Bank Note Waynesboro PA PMG EPQ 64","1929","unc 64 Prem"),
            ("267","Federal Reserve Bank Note Large size PMG","1918","very fine 35")]

for ref_num, desc, year, cond in pmg_refs:
    item = collected_by_ref.get(ref_num)
    if item and item.get("status") == "success":
        icon = "✅"
        img_link = f"[View]({item['public_url']})"
    elif item:
        icon = "⚠️"
        img_link = f"[HA]({item['img_url']})"
    else:
        icon = "❌"
        img_link = "—"
        no_img_pmg.append(ref_num)
    report += f"| {ref_num} | {desc[:55]} | {year} | {cond[:20]} | {icon} | {img_link} |\n"

report += f"""
## PCGS Documents (19 total)

| Ref# | Description | Year | Grade/Condition | Status | Image |
|------|-------------|------|-----------------|--------|-------|
"""

pcgs_refs = [("354","$1 Silver Certificate (FR237) PCGS","1923","choice AU-58"),
             ("384","$1 silver certificate (FR237) PCGS","1923","about unc 53"),
             ("235","$1 Federal Reserve Bank Note PCGS 65PPQ","1918","unc 65 Prem"),
             ("212","$1 Silver Certificate PPQ66 (FR237) PCGS","1923","unc 66 prem"),
             ("290","$1 Legal Tender Note large size PCGS","1917","about unc 50"),
             ("270","$1 Silver Certificate PPQ63 (FR238) PCGS","1923","unc 63 Prem"),
             ("326","$1 Silver certificate PPQ64 (FR238) PCGS","1923","unc 64 Prem"),
             ("126","$1 Silver Certificate Large Size PCGS","1923","Ch about UNC"),
             ("202","$5 legal tender note PCGS PPQ58","1907","AU 58"),
             ("199","5 cents fractional currency PCGS","1864-69","select unc 60"),
             ("234","$1 Legal Tender Note PCGS","1917","Au53 Premium"),
             ("374","$500 3rd Bank of US Philadelphia PCGS","","Very Fine"),
             ("197","$1 Federal Reserve Bank Note PCGS PPQ35","1918","very fine 35"),
             ("405","$1 silver certificate PCGS PPQ64","1923","UNC 64 Prem"),
             ("227","$1 Silver Certificate PCGS PPQ64","1923","unc 64 Prem"),
             ("226","$5 Silver Certificate Yellow Seal PCGS PPQ","1934A","unc 65 Prem"),
             ("325","$1 Silver certificate PCGS PPQ63 (FR237)","1923","unc 63 Prem"),
             ("233","1 silver certificate Yellow Seal PCGS PPQ","1935A","unc 64 Prem"),
             ("339","$1 Silver Certificate PCGS PPQ65 (FR238)","1923","Unc-65 Prem")]

for ref_num, desc, year, cond in pcgs_refs:
    item = collected_by_ref.get(ref_num)
    if item and item.get("status") == "success":
        icon = "✅"
        img_link = f"[View]({item['public_url']})"
    elif item:
        icon = "⚠️"
        img_link = f"[HA]({item['img_url']})"
    else:
        icon = "❌"
        img_link = "—"
        no_img_pcgs.append(ref_num)
    report += f"| {ref_num} | {desc[:55]} | {year} | {cond[:20]} | {icon} | {img_link} |\n"

report += f"""
---

## Uploaded Images

These images were sourced from Heritage Auctions archive search results.
They are **representative examples** of the same note type — not photos of AJ's actual notes.

"""

for item in results:
    if item.get("public_url"):
        report += f"- **Ref#{item['ref_num']}** {item['service']}: [{item['img_title'][:80]}]({item['public_url']})\n"

report += f"""
---

## Missing Images (No Cert Number Available)

These docs had no image retrieved due to rate limiting or search misses:
"""
for ref in no_img_pmg + no_img_pcgs:
    report += f"- Ref#{ref}\n"

report += f"""
---

## Recommendations

### 🔑 Add Cert Numbers to the Database

For each graded note, the PMG or PCGS certification number should be recorded by
physically inspecting each note's holder label:

| Service | Label Format | Example |
|---------|-------------|---------|
| PMG | `XXXXXXX-XXX` (printed on label) | `3622374-001` |
| PCGS | 8-digit number | `41054271` |

Once cert numbers are in Firestore, run:
```
python cert_scraper_step1.py   # will find them
python cert_image_scraper.py   # will fetch real images
```

### 📷 Fields Written to Firestore (for successful docs)

- `image_url_obverse` — Public GCS HTTPS URL (900×600 image)
- `cert_source` — `'PMG'` or `'PCGS'`
- `pmg_grade` / `pcgs_grade` — Grade from Firestore record
- `cert_lookup_url` — Heritage Auctions search URL
- `cert_matched_title` — Title of the matching auction lot
- `cert_image_source` — `'heritage_auctions_archive'`

### 🗂️ Storage Location

Images uploaded to GCS bucket: `{BUCKET_NAME}`  
Path pattern: `users/{USER_EMAIL}/currency/{{doc_id}}/obverse.jpg`
"""

os.makedirs(REPORT_DIR, exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

# Save results log
log_path = os.path.join(CACHE_DIR, "final_results.json")
with open(log_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

print(f"\n  Report: {REPORT_PATH}")
print(f"  Log:    {log_path}")
print(f"{'='*70}")
print(f"DONE: {success}/{len(collected)} images uploaded to GCS and Firestore updated")
print(f"{'='*70}")
