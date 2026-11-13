# DONE: `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`

- **To:** Grok Bot Chief of Staff, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 3:35 PM ET
- **Status:** **DONE (`PLAN ONLY` — Zero code modifications, zero deployments, zero Firestore writes/seeding)**
- **Target Deliverables Filed:**
  1. `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.2.md` (mirrored across `INBOX/`, `BATONS/`, and `RADIO NET/`)
  2. `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.2.md` (mirrored across `INBOX/`, `BATONS/`, and `RADIO NET/`)

---

## Summary of Resolutions in Plan v1.2

### 1. 780b Cards v1.2 Resolutions:
1. **Nickel Regex Boundary Fix (§4.B):** Replaced `RegExp(r'\b(5c|5¢|five cents?|nickel)\b')` with `RegExp(r'(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)')` because `¢` is a non-word character (`\W`) and cannot take a trailing `\b` word boundary. Test 3 aligned.
2. **Strict CDN CPG Retail Rule & Zero AI Fallback (§4.C):** Bound Founder Eric's 5 Nov 10:36 AM directive ("CDN CPG retail only; don't prefer AI over CDN"). Permanently deleted unlabeled AI fallback (`valCpg > 0 ? valCpg : valAi`). Cards display CDN `cpgRetail` only; missing or $\le 0$ values render strictly the styled gold `'Valuation Pending'` chip. Zero AI value, melt, or cost displayed as primary valuation.
3. **PII & Provenance Redactions (§3.A):** Redacted real-looking NGC certification numbers to `"[cert no. redacted]"` and removed demo dollar amounts.
4. **Dedicated Rollback Section (§6.A):** Added pinned Git revert targeting baseline commit `9f04550a`.

### 2. 780c Images v1.2 Resolutions:
1. **Inventory Census Synchronized with `docs/MISSING_IMAGES.csv` (§3.2):** Deleted fabricated counts (1,420 / 1,180 / 602 / "0 unmapped" / 284 / 28 / 41). Synchronized to exact live CSV counts: 2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5 = 3,202 master entries, all currently staged as missing.
2. **Strict Own-Origin Allowlist Guard (§3.1):** Replaced leaky denylist with in-memory allowlist (`storage.googleapis.com/numista-catalog-assets`, `'self'`, `data:`, `blob:`). Any outside origin (including Wikimedia and numismatics.org) is blanked in memory before fetch, rendering the local SVG placeholder with 0 CSP errors.
3. **Anchored Path Exclusions (§3.5):** Replaced unanchored regexes (which caused bare `eric` to match 578 `"American"` paths and `aj` to match `"Ajax"`). Anchored to folder boundaries (`(?i)[\\/](?:receipts|invoices|packing_slips|user_uploads|microscope_photos)[\\/]`). Kept personal folder prefixes in local config, not repository docs.
4. **Explicit "To-Be-Created" Artifact Labels (§3.4 & §5):** Labeled `tools/verify_catalog_manifest_pii.py` and `assets/catalog_image_manifest.json` as to-be-created implementation artifacts.
5. **Canonical NAC Primary Keys (`NAC1.*`) (§3.4):** Standardized manifest entries on `NAC1.*` format.
6. **Dedicated Rollback Section (§6.A):** Added branch revert commands to `9f04550a` and copy-only GCS rollback.

### 3. Cross-Cutting Declarations (Both Plans):
- Catalog-First AI rule (`ai_replica_images` only; never primary/card/index; `numista-uploads-studio` excluded).
- US-only intake scope.
- Hard $0.00 spend cap.
- No wholesale pricing.
- 26 Nov 2026 Thanksgiving cut: card pending-chip + closed-CSP fallback only; bulk mirror is not an ad launch blocker.

---

## Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- Zero live deployments; zero Firestore database writes or security rules changes.
