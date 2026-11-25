# SOP: Banknote Reference Image System & Taxonomy

**Standard Operating Procedure**  
**Document Version:** 2.0.0  
**Effective Date:** November 25, 2026 (Supersedes v1.0.0 August 10, 2026 AI render ban for catalog gap-fills only)  
**Target Repository:** `Numista.AI`  
**Status:** Approved Standard (Wave 2 `cc9d2916` / Eric 25 Nov 2026 ruling)  

---

## 1. Overview & Purpose

This Standard Operating Procedure (SOP) defines the canonical architecture, naming conventions, licensing rules, Firestore indexing schemas, and security policies for banknote reference imagery across Numista.AI.

Paper currency imagery is divided strictly into two tiers:
1. **Shared Public Reference Imagery**: Stored in `gs://numista-reference-library/reference_library/us_banknotes/`. Indexed in Firestore `currency_image_index` and accessible to all users and public web applications (`numista-vault.web.app`).
2. **Personal User Collection Photos**: Stored under `users/{email}/currency/{id}/` in user storage buckets. Strictly private to the individual account holder.

---

## 2. Mandatory Storage Bucket Taxonomy

| Storage Bucket | Allowed Use | Access Level |
|---|---|---|
| `gs://numista-reference-library` | Public reference library (Coins & Banknotes) | Public Read (`GET`/`HEAD` with CORS) |
| `gs://numista-uploads-...` | User-uploaded personal collection photos | Authenticated User Read/Write |
| `gs://studio-...-uploads` | Hardware / Microscope raw agent uploads | Backend Processing Only |

> [!CAUTION]
> **No Reference Assets in Uploads**: Reference library images MUST NEVER be uploaded directly into `users/{email}/currency/` or `numista-uploads-...`. Shared reference images must only land in `gs://numista-reference-library`.

---

## 3. 6-Tier Naming Taxonomy & Keying Schema

Every banknote reference image requires a **human-readable GCS filename** and a **machine catalog key** used directly as the Firestore Document ID.

### A. Taxonomy Structure Summary

```
gs://numista-reference-library/reference_library/us_banknotes/
├── federal/
│   ├── silver_certificates/
│   ├── legal_tender/
│   ├── frn/
│   └── gold_certificates/
├── confederate/
├── fractional/
├── obsolete/
├── errors/
└── uncut_sheets/
```

### B. Detailed Keying & Filename Rules by Category

#### 1. Federal Notes (Standard & Variants)
- **GCS Filename**: `{year}_{description}_{side}.jpg`
- **Firestore Document ID / Machine Key**: `fr_{friedberg}[_{variant}][_{star|norm}]_{obv|rev}`
- **Examples**:
  - Normal Note: `1923_fr237_silver_certificate_1_obverse.jpg` → `fr_237_norm_obv`
  - Variant Note: `1928e_fr1613n_silver_certificate_1_obverse.jpg` → `fr_1613_n_norm_obv`
  - Star Replacement Note: `1928e_fr1613n_star_silver_certificate_1_obverse.jpg` → `fr_1613_n_star_obv`

#### 2. Fractional Currency
- **GCS Filename**: `{year}_frac_fr{friedberg}_{description}_{side}.jpg`
- **Firestore Document ID / Machine Key**: `frac_fr{friedberg}_norm_{obv|rev}`
- **Example**: `1863_frac_fr1230_3_cents_obverse.jpg` → `frac_fr1230_norm_obv`

#### 3. Confederate States of America (CSA) Notes
- **GCS Filename**: `{year}_csa_t{t_number}_{denomination}_{side}.jpg`
- **Firestore Document ID / Machine Key**: `csa_t{t_number}_{obv|rev}`
- **Example**: `1864_csa_t64_500_obverse.jpg` → `csa_t64_obv`

#### 4. Obsolete / Broken Bank Notes
- **GCS Filename**: `{year}_obs_{state}_{city}_{bank_slug}_{denom}_{side}.jpg`
- **Firestore Document ID / Machine Key**: `obs_{state}_{city}_{bank_slug}_{denom}_{obv|rev}`
- **Example**: `1850_obs_va_richmond_merchants_bank_5_obverse.jpg` → `obs_va_richmond_merchants_5_obv`

#### 5. Error Notes
- **GCS Filename**: `{year}_err_{base_fr}_{error_slug}_{side}.jpg`
- **Firestore Document ID / Machine Key**: `err_{base_fr}_{error_slug}_{obv|rev}`
- **Example**: `1907_err_fr91_pcblic_spelling_reverse.jpg` → `err_fr91_pcblic_rev`

#### 6. Uncut Sheets
- **GCS Filename**: `{year}_sheet_{issuer_slug}_{layout}_{side}.jpg`
- **Firestore Document ID / Machine Key**: `sheet_{issuer_slug}_{layout}_{obv|rev}`
- **Example**: `1899_sheet_fr226_4subject_obverse.jpg` → `sheet_fr226_4sub_obv`

---

## 4. Firestore Document Schema (`currency_image_index/{doc_id}`)

To guarantee **$O(1)$ point-read performance** in client applications (`CurrencyImageService`), Firestore document paths MUST equal the catalog key string (e.g., `currency_image_index/fr_1613_n_star_obv`).

### JSON Document Schema
```json
{
  "catalog_key": "fr_1613_n_star_obv",
  "catalog_tier": "federal",
  "friedberg": "1613",
  "variant": "N",
  "is_star_note": true,
  "denomination_str": "$1.00",
  "denomination_num": 1.00,
  "series": "1928-E",
  "side": "obverse",
  "gcs_path": "gs://numista-reference-library/reference_library/us_banknotes/federal/silver_certificates/1928e_fr1613n_star_obverse.jpg",
  "public_url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/federal/silver_certificates/1928e_fr1613n_star_obverse.jpg",
  "source": "Wikimedia Commons / NNC",
  "attribution": "National Numismatic Collection, National Museum of American History",
  "license": "Public Domain",
  "is_reference_fallback": true,
  "created_at": "2026-08-10T16:00:00Z",
  "updated_at": "2026-08-10T16:00:00Z"
}
```

> [!IMPORTANT]
> **BigQuery Dual Denomination Field Requirement**:
> Documents MUST store both `"denomination_str": "$1.00"` (for Flutter UI display) and `"denomination_num": 1.00` (for BigQuery `numista_bq_loader_job` numeric aggregation).

---

## 5. Sourcing, Attribution & Licensing Policy

### A. Permitted Reference Image Sources
1. **Public Domain / Wikimedia Commons**: Specifically National Numismatic Collection (NNC) uploads from the Smithsonian Institution.
2. **Official Government Archives**: U.S. Bureau of Engraving and Printing (BEP), U.S. Treasury, or Library of Congress public domain archives.
3. **Attributed User Contributions**: Direct user submissions where explicit copyright waiver / Creative Commons license is granted.

### B. Prohibited Sources, Scraper Quarantine & 31 CFR § 411.1 AI Gap-Fill Rules
- **Auction Scrapers**: Heritage Auctions, Stack's Bowers, or PCGS/PMG scrapers are strictly prohibited for reference library building due to Terms of Service and copyright risks.
- **Public-Domain Scans First**: Authentic Smithsonian NNC, Bureau of Engraving and Printing (BEP), U.S. Treasury, or Wikimedia Commons public-domain scans ALWAYS take precedence over AI illustrations.
- **AI Banknote Gap-Fills (v2.0.0 — Strictly Bounded by 31 CFR § 411.1 & 18 U.S.C. §§ 475, 504)**:
  When no authentic public-domain scan is available for a catalog banknote row, an AI-generated illustration MAY enter `gs://numista-reference-library` ONLY after passing **SAG 95+ AND Gemini 95+ AND Muse 95+** and satisfying all five mandatory controls:
  1. **One-Sided Color Obverse Only**: `side == "obverse"` ONLY (`build_public_catalog.py` fails closed and drops any AI banknote reverse).
  2. **Strictly `< 75%` Linear Print Size + Raw Download Disabled**: UI caps rendered dimensions strictly below 75% of real U.S. currency linear dimensions (`< 4.60" × 1.95"` for small-size notes; `< 5.56" × 2.34"` for large-size notes), disables zoom past cap, and `GET /api/v1/catalog/{nac_code}/image-download` returns HTTP `403 AI_BANKNOTE_DOWNLOAD_DISABLED` even for signed-in users.
  3. **Immediate Destruction of Working Intermediates**: All temporary/working AI banknote generation files MUST be deleted immediately after placing the final approved asset.
  4. **Zero Marketing / Ad Usage (`18 U.S.C. § 475`)**: Every AI banknote record carries `"allow_marketing_use": false` and is excluded from all ads, landing-page heroes, and promotional graphics.
  5. **Mandatory Burned-In Watermark & UI Caption**: Every AI banknote image MUST carry a small legible **`"AI Generated"`** watermark in the **lower-right corner** AND render the fixed UI disclosure **`"AI-generated illustration of the note — not a genuine specimen"`**.

### C. Mandatory `MANIFEST.json` Schema
Every intake batch directory submitted to `_scripts/intake_banknote_images.py` must include a valid `MANIFEST.json`:

```json
{
  "batch_id": "2026-08-10_priority1_star_notes",
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
    }
  ]
}
```

---

## 6. Client Fallback, Watermarking & UI Badging Contract

When a user's banknote item document (`users/{email}/currency/{id}`) has empty `image_url_obverse` or `image_url_reverse` fields:

1. **Client Lookup Service**: `CurrencyImageService` queries `currency_image_index` using a 3-stage fallback cascade:
   - **Stage 1 (Exact Match)**: `fr_1613_n_star_obv` $\rightarrow$ UI Badge: `"CATALOG REFERENCE (EXACT)"`
   - **Stage 2 (Closest Star Match)**: `fr_1613_star_obv` $\rightarrow$ UI Badge: `"CATALOG REFERENCE (CLOSEST STAR MATCH)"`
   - **Stage 3 (Generic Type Match)**: `fr_1613_norm_obv` $\rightarrow$ UI Badge: `"CATALOG REFERENCE (CLOSEST TYPE MATCH)"`
2. **System of Record Data Contract**: All reference lookup responses MUST return `is_reference_fallback: true`.
3. **Legal Watermarking**:
   - **PDF Collection Passports** (`passport_pdf_generator.py`) and **Attorney Portals** (`attorney_portal_screen.dart`) MUST overlay a high-contrast watermark when `is_reference_fallback == true`:  
     `"CATALOG REFERENCE PHOTO — NOT INDIVIDUAL ASSET PHOTO"`

---

## 7. Cloud Storage CORS Configuration

To allow Flutter Web (`numista-vault.web.app`) to fetch reference images directly without browser CORS errors, `gs://numista-reference-library` must maintain the following CORS configuration (`cors_reference_library.json`):

```json
[
  {
    "origin": [
      "https://numista.ai",
      "https://numista-vault.web.app",
      "http://localhost:*"
    ],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
```

Deploying CORS:
```bash
gcloud storage buckets update gs://numista-reference-library --cors-file=numista_backend/cors_reference_library.json
```
