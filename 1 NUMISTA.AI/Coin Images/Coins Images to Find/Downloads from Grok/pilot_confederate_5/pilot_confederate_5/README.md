# Numista.AI Pilot Package — Confederate Currency (5 notes)

**Created:** 2026-06-21 22:12
**Purpose:** End-to-end test of sourcing high-quality images → clean file delivery with dual naming → upload to Google Cloud Storage → integration in Antigravity / Numista.AI

## What's Included
- `images/` folder containing the completed high-quality renders (obverse + reverse)
- `manifest.csv` with full details for all 5 items (doc_id, filenames, status, suggested GCS paths)
- This README with step-by-step instructions

## Completed Items (Ready to Upload)
1. **$500 1864 T-64 (Stonewall Jackson)** — Professional straight-on full-frame renders for both sides
2. **50¢ 1863 T-63 (Jefferson Davis)** — Professional straight-on full-frame renders for both sides

The other three items in this pilot have placeholder entries in the manifest and will be completed next.

## File Naming (Dual System)
- **Master / Internal (for linking):** Uses the `doc_id` from your collection (e.g. `2ea45a00-908d-477b-8eeb-20a127ae6db2_obverse.jpg`). This is the recommended version for Firestore / backend linking.
- **Descriptive (human readable):** e.g. `T-64_1864_500_Stonewall_Jackson_Obverse.jpg`

Both versions are provided for the completed items.

## Recommended Upload to Google Cloud Storage
1. Upload the `images/` folder (or the whole `pilot_confederate_5` folder) to your bucket.
2. Suggested path:
   ```
   gs://[your-bucket]/numista_reference_images/confederate_pilot/
   ```
3. After upload, each image will have a URL like:
   ```
   https://storage.googleapis.com/[your-bucket]/numista_reference_images/confederate_pilot/2ea45a00-908d-477b-8eeb-20a127ae6db2_obverse.jpg
   ```

## How to Use These Images in Antigravity
1. Copy the GCS URLs after uploading.
2. In your Antigravity app, add Image components or bind them to your data models (recommended fields: `obverse_image_url` and `reverse_image_url` on coin/currency records).
3. Store the URLs in Firestore. Because the filenames are based on `doc_id`, it will be straightforward to match and update records later (manually or with a small script/Cloud Function).

## Next Steps After This Test
- I will complete high-quality renders for the remaining three items in this pilot.
- We will repeat the process for the rest of the Confederate notes (8 more).
- We can then expand to National Bank Notes, Gold Certificates, Obsolete Currency, etc.
- I can add `gcs_obverse_url` and `gcs_reverse_url` columns to the main Image_Sourcing_Tracker.xlsx if helpful.

This pilot validates the entire chain from sourcing to usable assets in your production Numista.AI environment.

If you need any refinements to the current renders, different styling, or help with upload scripts, let me know.
