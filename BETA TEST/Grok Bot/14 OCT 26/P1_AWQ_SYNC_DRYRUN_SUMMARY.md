# P1 AWQ Firestore Sync DRY-RUN Summary

**Date:** 2026-10-14
**Mode:** DRY-RUN ONLY (READ-ONLY, ZERO Firestore writes)
**Safety Guard:** `FIRESTORE_WRITES_ENABLED = False` (Verified)
**Database Project:** `studio-9101802118-8c9a8`

---

## Executive Summary

- **Total Firestore Coins Scanned:** 12,448
- **Total AWQ Coins Identified:** 290
- **Total Unique Documents that WOULD Change:** 62
- **Total Field-Level Changes (CSV Rows):** 64
- **Firestore Writes Made:** **0 (ZERO)**
- **Status:** **DRY-RUN COMPLETE — APPLY ON HOLD**

---

## Breakdown by Field

| Field Name | Proposed Change Description | Count |
|------------|-----------------------------|-------|
| `Theme/Subject` | F1 Name Fix (Pauli Murray, Patsy Mink, Zitkala-Ša, Edith Kanakaʻole, Stacey Milbern) | 60 |
| `official_us_mint_title` | F1 Official Title Fix (okina, Š diacritic, full title) | 2 |
| `Mint Mark` | Purge invalid W mint mark (W-UNC variety removed in F1) | 2 |

---

## Breakdown by User Collection

| User Email | Documents / Fields Affected |
|------------|-----------------------------|
| `beta@numista.ai` | 27 |
| `jseaman1204@gmail.com` | 25 |
| `eric.seaman@yahoo.com` | 5 |
| `grokbot@numista.ai` | 4 |
| `ericdcman@gmail.com` | 3 |

---

## Sample of First 10 Proposed Changes

| Document Path | Field | Current Value | Proposed Value | User |
|---------------|-------|---------------|----------------|------|
| `users/beta@numista.ai/coins/14d39768-575a-477a-85b9-4e09152b2834` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/180aee64-c14a-4dc2-b6aa-cafdae8cfb90` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/4541ed1d-e86e-441f-8f27-4782dffcb227` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/47c5e078-b9cf-40d2-a9be-b90bf590d9d1` | `Theme/Subject` | `Pauli Murray` | `Rev. Dr. Pauli Murray` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/4ae475ad-7da6-4e53-a43b-1dca9d788c45` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/52af4782-53de-439d-91ed-75d86498dfd4` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/5679674c-4fc2-4bb4-acf2-f0284370fb76` | `Theme/Subject` | `Pauli Murray` | `Rev. Dr. Pauli Murray` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/6014278f-fb2a-421f-9769-36cbd5680017` | `Theme/Subject` | `Pauli Murray` | `Rev. Dr. Pauli Murray` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/614db907-40a5-4fbd-aa6c-f58bbbea8cdf` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |
| `users/beta@numista.ai/coins/69284190-1c28-41ec-bc06-cc0f1ac18352` | `Theme/Subject` | `Zitkala-Sa` | `Zitkala-Ša` | `beta@numista.ai` |

---

## Catalog Mapping Reference (F1 Changes Verified)

1. **Slugs:**
   - `awq_2024_zitkala__a` → `awq_2024_zitkala_sa`
2. **Names:**
   - `Dr. Pauli Murray` / `Pauli Murray` → `Rev. Dr. Pauli Murray`
   - `Patsy Mink` → `Patsy Takemoto Mink`
   - `Edith Kanaka'ole` (ASCII quote) → `Edith Kanakaʻole` (U+02BB okina)
   - `Zitkala-Sa` / `Zitkala-a` → `Zitkala-Ša`
   - `Stacey Milbern` → `Stacey Park Milbern`
3. **Varieties / Labels:**
   - `W-UNC` purged (West Point never struck circulating or collector AWQ quarters)
   - `S-SILVER-PROOF` added ("S Silver Proof (99.9% silver)")
   - `S` → "S Uncirculated"
   - `S-PROOF` → "S Proof (clad)"

---

**Note:** LIVE APPLY IS ON HOLD per Grok CoS and Eric. No modifications will be executed until Eric finishes adding coins and Grok CoS issues a separate GO on RADIO NET.
