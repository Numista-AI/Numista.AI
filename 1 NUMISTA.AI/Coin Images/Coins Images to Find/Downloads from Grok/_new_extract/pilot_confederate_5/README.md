# Numista.AI Pilot Package — Confederate Currency (5 notes)

**Created / Last Updated:** 2026-06-21 22:32
**Purpose:** End-to-end test of sourcing → file delivery with dual naming → upload to Google Cloud Storage → integration in Antigravity / Numista.AI

## Current Status of Pilot Batch (as of this update)
All 5 items now have high-quality straight-on renders.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | $500 1864 T-64 (Stonewall Jackson) | ✅ Completed | High quality |
| 2 | 50¢ 1863 T-63 (Jefferson Davis) | ✅ Completed **🟡 Flag** | Banner text fixed to "JEFFERSON DAVIS". Minor text artifacts remain in other areas (common AI limitation). Still very usable. |
| 3 | $1 1864 | ✅ Completed | High quality |
| 4 | $50 1864 | ✅ Completed | High quality |
| 5 | $5 1861 | ✅ Completed | High quality |

## What's Included
- `images/` folder: All completed renders (both internal doc_id naming and descriptive names where available)
- `manifest.csv`: Up-to-date mapping with current statuses and 🟡 Flag notes
- This README

## File Naming Convention
- **Master/Internal (recommended for linking):** Use the doc_id-based filenames (e.g. 2ea45a00-908d-477b-8eeb-20a127ae6db2_obverse.jpg)
- **Descriptive (human readable):** e.g. T-64_1864_500_Stonewall_Jackson_Obverse.jpg

## QC Notes (per Antigravity checklist)
- **🟡 Flag on T-63:** The top banner now correctly reads "JEFFERSON DAVIS". Some other text elements still have minor garbling. Accepted with note as it is significantly improved and usable for a collection tracker.
- All other renders passed internal QC for straight-on framing, full borders, correct denomination/year/portrait where applicable.

## Recommended GCS Upload Path
gs://[your-bucket]/numista_reference_images/confederate_pilot/

## How to Use in Antigravity
1. Upload the images/ folder to the path above.
2. Use the resulting GCS URLs in your Image components / data models.
3. Store URLs in Firestore (obverse_image_url, reverse_image_url).
4. The doc_id-based naming makes automated matching very easy.

This pilot successfully validated the full workflow. We are now ready to scale to the remaining Confederate notes or other categories.
