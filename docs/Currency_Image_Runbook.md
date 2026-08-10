# Banknote Reference Image Runbook

**Operator & Maintenance Runbook**  
**Target System:** Banknote Reference System (`Numista.AI`)  
**Document Version:** 1.0.0  
**Effective Date:** August 10, 2026  

---

## Executive Summary

This runbook provides step-by-step instructions for non-technical operators, image sourcing specialists, and backend developers to stage, validate, ingest, index, and audit banknote reference imagery.

---

## Workflow Overview

```
1. Staging Batch ──► 2. MANIFEST Attestation ──► 3. Dry-Run Intake ──► 4. Ingestion & GCS Upload ──► 5. Firestore Indexing ──► 6. Coverage Audit
```

---

## 1. Staging & Preparing Banknote Images

1. Create a local staging folder under `scratch/banknote_staging/<batch_name>/`.
2. Save obverse and reverse images using the human-readable GCS naming standard specified in [`SOPs/banknote_image_sop.md`](../SOPs/banknote_image_sop.md):
   - **Federal**: `1923_fr237_silver_certificate_1_obverse.jpg`
   - **Federal Star Note**: `1928e_fr1613n_star_silver_cert_1_obverse.jpg`
   - **Fractional**: `1863_frac_fr1230_3_cents_obverse.jpg`
   - **Confederate**: `1864_csa_t64_500_obverse.jpg`
   - **Obsolete**: `1850_obs_va_richmond_merchants_bank_5_obverse.jpg`
   - **Error**: `1907_fr91_pcblic_spelling_error_reverse.jpg`
   - **Uncut Sheet**: `1899_sheet_fr226_4subject_obverse.jpg`

3. Verify image quality:
   - High resolution (minimum 1200px width).
   - Clean crop, no background clutter, no artificial distortion.
   - Genuine physical note photography (NO AI renders).

---

## 2. Creating the `MANIFEST.json`

Inside the staging directory, create a `MANIFEST.json` describing every file in the batch.

### Template:
```json
{
  "batch_id": "2026-08-10_priority1_batch01",
  "operator": "Numista-AI Sourcing Team",
  "items": [
    {
      "filename": "1928e_fr1613n_star_silver_cert_1_obverse.jpg",
      "side": "obverse",
      "catalog_key": "fr_1613_n_star_obv",
      "source": "Wikimedia Commons / National Numismatic Collection",
      "attribution": "National Numismatic Collection, National Museum of American History",
      "license": "Public Domain",
      "is_ai_generated": false
    },
    {
      "filename": "1928e_fr1613n_star_silver_cert_1_reverse.jpg",
      "side": "reverse",
      "catalog_key": "fr_1613_n_star_rev",
      "source": "Wikimedia Commons / National Numismatic Collection",
      "attribution": "National Numismatic Collection, National Museum of American History",
      "license": "Public Domain",
      "is_ai_generated": false
    }
  ]
}
```

---

## 3. Running Intake & Validation

### Step 3.1: Dry-Run Inspection
Always perform a dry-run first to validate filenames, MANIFEST schemas, and catalog key formatting without modifying GCS or Firestore:

```bash
python numista_backend/_scripts/intake_banknote_images.py --staging-dir ./scratch/banknote_staging/2026-08-10_priority1_batch01 --dry-run
```

### Step 3.2: (Optional) Gemini AI Screening
To run automated Gemini vision screening using `google-genai` SDK (`gemini-3.5-flash`):

```bash
python numista_backend/_scripts/intake_banknote_images.py --staging-dir ./scratch/banknote_staging/2026-08-10_priority1_batch01 --ai-screening --dry-run
```

### Step 3.3: Execute Intake
Once dry-run passes cleanly, execute the live intake:

```bash
python numista_backend/_scripts/intake_banknote_images.py --staging-dir ./scratch/banknote_staging/2026-08-10_priority1_batch01
```

This script:
1. Uploads validated images to `gs://numista-reference-library/reference_library/us_banknotes/...`.
2. Triggers `build_currency_image_index.py` to write/update Firestore records at `currency_image_index/{doc_id}`.

---

## 4. Rebuilding / Rescanning Firestore Index

If images were manually uploaded or reorganized directly in GCS, rebuild the Firestore `currency_image_index`:

### Dry-Run Indexer:
```bash
python numista_backend/_scripts/build_currency_image_index.py --dry-run
```

### Live Indexer Run:
```bash
python numista_backend/_scripts/build_currency_image_index.py
```

---

## 5. Auditing Coverage & Gap Reporting

To generate a full report of catalog items vs reference image coverage:

```bash
python numista_backend/_scripts/currency_gap_report.py
```

Output highlights:
- Total banknote catalog varieties (`banknotes_expanded.json`).
- Obverse & Reverse coverage percentages.
- Priority 1 missing items list exported to `numista_backend/data/currency_image_gaps.csv`.

---

## 6. Emergency Recovery & Troubleshooting

### Issue: Image fails to load on `numista-vault.web.app` (CORS Error)
**Cause**: Missing or expired CORS configuration on `gs://numista-reference-library`.  
**Fix**: Redeploy CORS configuration:
```bash
gcloud storage buckets update gs://numista-reference-library --cors-file=numista_backend/cors_reference_library.json
```

### Issue: Duplicate or Wrong Document ID in Firestore
**Cause**: Manual write bypass without using catalog key as Document ID.  
**Fix**: Run index cleanup tool:
```bash
python numista_backend/_scripts/build_currency_image_index.py --clean-stale
```

### Issue: Reference photo rendered on legal PDF passport without watermark
**Cause**: API response omitted `is_reference_fallback: true`.  
**Fix**: Check `currency_image_service.dart` and `passport_pdf_generator.py` for fallback metadata propagation.
