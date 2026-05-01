# Numista.AI — Session Report
## Date: April 11, 2026
## Session Duration: ~3 hours (approx. 9:30 AM – 3:24 PM EDT)

---

## 🏆 What We Accomplished Today

### 1. Silver Detection & PCGS Integration — COMPLETE ✅

The entire silver detection pipeline is now live end-to-end.

**Files Modified/Created:**
- `numista_hardware/.env` — Added `PCGS_ACCESS_TOKEN`
- `numista_hardware/pcgs_service.py` *(NEW)* — Full PCGS Public API client with:
  - Local year/denomination silver rule engine (no network required)
  - Melt value estimator (~$32.50/troy oz spot hardcoded; upgrade to live feed later)
  - PCGS CoinFacts API lookup via `GetCoinFactsByPCGSNo`
  - Graceful fallback — scan never fails if PCGS is unreachable
- `numista_hardware/identify_coin.py` — Updated Gemini prompt to return `is_silver` (bool) and `metal_content` (string) as structured JSON fields
- `numista_hardware/auto_capture.py` — Wired `PCGSService.enrich_coin()` into the scan pipeline after Gemini identification; added `Is Silver`, `PCGS Number`, `Melt Value` to Firestore coin document
- `numista_hardware/requirements.txt` — Added `requests`
- `numista_mobile/lib/services/pcgs_service.dart` *(NEW)* — Flutter data model + quick silver-check utility
- `numista_mobile/lib/screens/microscope_scan_screen.dart` — Added **Metal Intelligence Panel** to scan result UI:
  - 🥈 SILVER / 🔵 NOT SILVER badge
  - Metal composition string
  - Melt value estimate + troy oz
  - PCGS catalog number (when matched)
  - PCGS price guide & population (when API returns data)

**Verified Working:**
- PCGSService smoke test: `1964 Roosevelt Dime` → `90% Silver, 10% Copper` ✅
- Flutter analyze: 0 errors ✅
- Scanned a coin and it worked! ✅

**PCGS Credentials (stored in .env):**
- Email: eric@numista.ai
- Token stored in: `numista_hardware/.env` as `PCGS_ACCESS_TOKEN`
- API base: `https://api.pcgs.com/publicapi`
- Rate limit: 1,000 calls/day (free tier)

---

### 2. My Collection Data Table — All Bugs Fixed ✅

The inventory grid was showing data in completely wrong columns, condition as a raw number, and location as "Pending"/"N/A".

**Root Cause:** A positional `fieldValues[]` array was in a different order than the column definitions — every column from `Mint` onward showed the wrong field.

**Files Modified:**
- `numista_mobile/lib/screens/my_collection_screen.dart`
  - Replaced broken positional array with a `switch` statement that maps each column directly to its own declared Firestore field key
  - Fixed `_F.cost` constant: `'Purchase Cost'` → `'Cost'` (hardware agent writes `'Cost'`)
  - Fixed `_F.personalNotes`: `'Personal Notes I'` → `'Personal Notes'`
  - Added `_conditionLabel()` helper: converts numeric Sheldon codes (`1` → `P-1`, `58` → `AU-58`, `65` → `MS-65`, etc.)
  - Storage Location: reads both `'Storage Location'` and `'storage_location'` fallback; suppresses `'Hardware Scan'` default placeholder

**Result:** All columns now show correct data. Condition "1" now displays as "P-1". ✅

---

### 3. Kaggle Reference Image Library — COMPLETE ✅

Built and executed a full pipeline to download, attribute, and upload ~6,000 reference coin images to GCS + Firestore.

**Kaggle Account Setup:**
- Username: `ericseaman`
- API Token: stored in `C:\Users\ericd\.kaggle\kaggle.json`

**Datasets Downloaded (all in `C:\Users\ericd\.cache\kagglehub\datasets\`):**

| Dataset | Kaggle Slug | Images | License |
|---|---|---|---|
| US Coins Subset from Wikimedia | `kaggerator/us-coins-subset-from-wikimedia` | 2,273 | CC BY-SA |
| Count Coins Image Dataset | `balabaskar/count-coins-image-dataset` | 1,444 | Kaggle terms |
| Rare US Coin Image Dataset | `jaronfralick/rare-us-coin-image-dataset` | 2,202 | Kaggle terms |
| **TOTAL** | | **5,919** | |

**Infrastructure Created:**
- GCS Bucket: `gs://numista-reference-library` *(new, separate from `us_mint_coin_images`)*
- Firestore Collection: `reference_library` — one doc per image with:
  - `denomination`, `year`, `side` (parsed from filenames)
  - `source`, `attribution`, `license`, `license_url`, `kaggle_url`
  - `category`, `tags`, `gcs_url`, `gcs_path`
- Upload Script: `numista_hardware/upload_reference_library.py`
  - Idempotent (safe to re-run — skips already-uploaded files)
  - Supports `--dry-run`, `--limit N`, `--source [source_key]` flags

**Upload Result:** 5,919 uploaded, 0 errors, 0 skipped ✅

---

## 📁 Key File Locations

```
numista_hardware/
  ├── .env                          ← PCGS_ACCESS_TOKEN + GOOGLE_API_KEY
  ├── pcgs_service.py               ← PCGS API client + silver detection engine
  ├── identify_coin.py              ← Gemini identification (now returns is_silver, metal_content)
  ├── auto_capture.py               ← Hardware agent (PCGS enrichment now wired in)
  ├── upload_reference_library.py   ← Kaggle → GCS → Firestore pipeline
  └── requirements.txt              ← requests added

numista_mobile/lib/
  ├── services/pcgs_service.dart    ← Flutter PCGS data model
  ├── screens/microscope_scan_screen.dart  ← Metal Intelligence Panel added
  └── screens/my_collection_screen.dart   ← Column mapping fixed

C:\Users\ericd\.kaggle\
  └── kaggle.json                   ← Kaggle API credentials

GCS:
  gs://us_mint_coin_images/         ← US Mint images (untouched)
  gs://numista-reference-library/   ← Kaggle reference images (new today)

Firestore:
  reference_library/                ← 5,919 indexed image documents (new today)
```

---

## 🌙 Known Issues / Watch Items

- **PCGS silver spot price** is hardcoded at $32.50/troy oz in `pcgs_service.py`. Should eventually be fetched from a live metals API (e.g., metals-api.com or Gold-API.com).
- **PCGS API rate limit**: 1,000 calls/day on the free tier. If we scan more than ~1,000 coins/day, we'll hit this. For now it's fine.
- **`balabaskar` dataset** has hash-named files (`01207e3d7e.jpg`) with no denomination info in the filename — they'll be tagged as `denomination: Unknown`. This is fine for now; they still serve as visual variety data.
- **Flutter hot restart** was the recommended deploy method today. No production build was run.

---

---

# 🗡️ Attack Plan — April 12, 2026

## Priority 1: "Similar Coins" Reference Feature (Big Ticket)
**Goal:** After a coin scan, automatically surface matching reference images from the library we just built.

### Steps:
1. **Create `ReferenceLibraryService` in Flutter** (`numista_mobile/lib/services/reference_library_service.dart`)
   - Query Firestore `reference_library` collection by `denomination` + `year` range (±5 years)
   - Return top 6 matching images (sorted by year proximity)
   - Cache results locally to avoid repeat Firestore reads

2. **Add "Similar Coins" panel to `microscope_scan_screen.dart`**
   - Appears below the Metal Intelligence Panel after scan completes
   - Horizontal scroll row of reference coin thumbnails (GCS URLs)
   - Tap to expand for full image + attribution caption

3. **Wire same feature into `my_collection_screen.dart` Coin Inspector**
   - "Similar in Library" row in the inspector detail grid
   - Shows reference images matching the selected coin's denomination/year

4. **Python side: Few-Shot AI Context** (Option 2)
   - In `identify_coin.py`, before calling Gemini, query Firestore for 2-3 reference images of the expected denomination
   - Include those images in the Gemini prompt as visual ground-truth
   - Expected accuracy improvement: significant for rare/unusual varieties

---

## Priority 2: Live Silver Spot Price
**Goal:** Replace the hardcoded `$32.50` in `pcgs_service.py` with a live feed.

- Sign up for a free metals API (metals-api.com has a free 100 req/month tier)
- Add `METALS_API_KEY` to `.env`
- Cache the spot price for 1 hour (it doesn't need to be real-time)
- Update `_estimate_melt_value()` in `pcgs_service.py`

---

## Priority 3: My Collection UI Polish
**Goal:** Fix minor issues noticed during today's session.

- **Is Silver badge** — Add a 🥈 silver indicator column to the inventory data table (currently only shows in the scan result, not the collection view)
- **Melt Value column** — Currently stores `~$1.83` format; should be sortable numerically
- **PCGS Number column** — Add to the `_columns` list in `my_collection_screen.dart` so it's visible in the data grid

---

## Priority 4: Session Report Automation
**Goal:** Auto-generate a session report at the end of every work session.

- Small Python script `generate_session_report.py` that reads today's Firestore writes and summarizes what was added/changed
- Output to `NUMISTA_AI_SESSION_REPORT_[DATE].md`
- Could be triggered by the launch script on exit

---

## Stretch: Kaggle Dataset Enrichment
- The `balabaskar` dataset has ~1,444 images with hash filenames — no metadata.
  Run a batch Gemini identification job against them overnight to label denomination/year and update their Firestore docs.
- Script skeleton: `numista_hardware/batch_label_reference_images.py` (to be created)

---

## Launch Reminder
```powershell
# From C:\Users\ericd\Documents\MyVertexProject
.\launch_numista.ps1

# Then open Chrome → http://localhost:8080
# Hardware agent: http://localhost:5000
```

---

*Report written: April 11, 2026 at end of session.*
*Next session target: April 12, 2026.*
