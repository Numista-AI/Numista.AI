# ARGON (GEMINI 3.8) TECHNICAL & DATA HYGIENE REVIEW: `FAILFIX_PLAN_NET-777_CATALOG_v1.5.md` (`BATON_NET-808`)

- **Reviewer:** Argon — Gemini 3.8 Independent Technical & Data Hygiene Auditor
- **Track / Baton:** `NET-777` / `NET-788` / `NET-803` / `NET-804` / `BATON_NET-808` (`CRITICAL PATH` — Thanksgiving Meta Ads)
- **Target Plan Reviewed:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md` (412 lines)
- **Target Inventory Reviewed:** `docs/MISSING_IMAGES.csv` (3,203 lines = 1 header + 3,202 data rows)
- **Timestamp:** 2026-11-05 16:28 ET
- **Composite Score:** **98 / 100 (`PASS — 0 Blocking Plan Must-Fixes; 1 Non-Blocking CSV Data Hygiene Note CSV-v1.5-1 Logged`)**
- **Execution Posture:** **PLAN REVIEW ONLY** (`origin/main` locked at `9f04550a`, Stripe strictly OFF, zero code edits, zero deployments, zero Firestore writes/seeding)

---

## 1. Executive Verdict & Rubric Breakdown

`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md` resolves all **3 blocking must-fixes** and all **3 non-blocking refinements** from Grok Bot CoS (`COS_SCORE_NET-804_FAILFIX-777-v1.4_20261105.md` — 89/100 FAIL) and Stand Alone Grok (`SAG_SCORE_NET-804_FAILFIX-777-v1.4_20261105.md` — 85/100 FAIL), while preserving all v1.4 fixes (`§3.C–3.D` 3,202-row tier alignment, `MorganChatPopout` constructor match, Condition C1 strict flag-only filter, and Catalog-First AI rule).

| Rubric Dimension | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. CoS-89 / SAG-85 Blocking Must-Fix 1 (Repo-Safe Rollback without `9f04550a` Checkouts)** | 25 | **25 / 25** | `§9.A` (lines 336–361) deletes all `9f04550a` file checkouts, pins code rollback on `dev` to pre-execute SHA `18a8b8e5` (`git revert <execute SHA>` / `git checkout 18a8b8e5 -- ...`), and pairs it with Firebase Hosting channel delete (`firebase hosting:channel:delete pre-ads-preview`) and live release clone (`firebase hosting:clone numista-vault:<prior-release-version-id> numista-vault:live`). |
| **2. CoS-89 / SAG-85 Blocking Must-Fix 2 (Grounded `$25.00/mo` Spend Stop & Hosting Egress Shutoff)** | 25 | **25 / 25** | `§3.E` (lines 134–155) covers Firebase Hosting CDN egress (`$0.15/GB` above 10 GB), identifies the active studio bucket (`numista-uploads-studio-9101802118-8c9a8`), marks `gs://numista-catalog-assets` and `projects/numista-ai/topics/billing-budget-alerts` as *"to be provisioned by Cloud Infrastructure Owner (Founder Eric / Grok Bot CoS)"*, and specifies the human owner + manual shutoff (`firebase hosting:channel:delete pre-ads-preview` / `firebase hosting:disable`). |
| **3. CoS-89 / SAG-85 Blocking Must-Fix 3 (Accurate Status Wording for `dev` Code)** | 20 | **20 / 20** | `§2` (lines 58–63) and `§11` (lines 407–409) replace false "Removed / RESOLVED" claims with **`SPECIFIED — to be removed at execute`** for both the outbound `(source)` link (`dev:1010-1017`) and the `Foreign Coins` tab (`dev:599-603`). |
| **4. CoS / SAG Refinements 1–3 (`_onTypeChanged` Cite, CPG Retail Policy, Ad Host)** | 15 | **15 / 15** | `_onTypeChanged` corrected to `dev:209-214` (`§2` line 61, `§6.A` line 249); explicit policy line added (`§1` line 19, `§3.B` line 89, `§8.B` line 315) that public catalog valuations display strictly CDN CPG retail (`cpgRetail`) only with zero wholesale values; ad landing host `https://numista.ai` confirmed (`§1` line 20). |
| **5. CSV Data Hygiene (`docs/MISSING_IMAGES.csv`) & Standing Locks** | 15 | **13 / 15** | 3,202 rows verified (`2,354 + 639 + 181 + 1 + 27 = 3,202`). Deducted 2 points for non-blocking `CSV-v1.5-1`: line 1691 (`NAC1.MD.US.AMERICANGY.MEDAL.1976.XX.BASE.G`) still has `.00` instead of `$0.00` in `estimated_cost`. |
| **TOTAL** | **100** | **98 / 100** | **PASS (`>= 95` Gate Met)** |

---

## 2. Rule 6(a) / `NET-767` Verbatim Code & Plan Verification (All Files Read via `read_file` in This Turn)

### 2.1 CoS-89 / SAG-85 Must-Fix 1: Repo-Safe Rollback (`§9.A`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md:336-356`:**
  ```markdown
  336: ### A. Dedicated Repo-Safe Rollback Procedures (No `9f04550a` checkouts)
  337: 1. **Code Rollback on `dev`:**
  338:    - Neither `catalog_public_v1.json` nor `catalog_browse_screen.dart` exist at `9f04550a`. `9f04550a` is not an ancestor of `dev`.
  339:    - Code rollback is pinned directly to pre-execute `dev` SHA (currently commit `18a8b8e5`):
  340:      ```bash
  341:      git revert <execute SHA>
  342:      ```
  343:    - Or if uncommitted working tree changes need to be discarded:
  344:      ```bash
  345:      git checkout 18a8b8e5 -- numista_mobile/lib/screens/catalog/catalog_browse_screen.dart numista_mobile/firebase.json
  346:      ```
  347: 2. **Firebase Hosting Rollback:**
  348:    - If executed on preview channel:
  349:      ```bash
  350:      firebase hosting:channel:delete pre-ads-preview
  351:      ```
  352:    - If deployed to live production:
  353:      Restore previous live release via Firebase Console (Hosting > Release History > Rollback to prior release) or via CLI:
  354:      ```bash
  355:      firebase hosting:clone numista-vault:<prior-release-version-id> numista-vault:live
  356:      ```
  ```

### 2.2 CoS-89 / SAG-85 Must-Fix 2: Grounded `$25.00/mo` Spend Cap, Hosting Egress & Manual Shutoff (`§3.E`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md:137-155`:**
  ```markdown
  137: 1. **Hard Monthly Cap:** **$25.00 / month** covering GCS storage + Cloud CDN + Firebase Hosting egress.
  ...
  141: 2. **Infrastructure Identification & Provisioning Scope:**
  142:    - Active studio storage bucket today: `numista-uploads-studio-9101802118-8c9a8`.
  143:    - Dedicated catalog storage bucket `gs://numista-catalog-assets` and Pub/Sub topic `projects/numista-ai/topics/billing-budget-alerts` are **to be provisioned by Cloud Infrastructure Owner (Founder Eric / Grok Bot CoS)**. No unverified IDs are assumed active in code.
  ...
  152:    - **Manual Shutoff Protocol:** If monthly spend reaches the $20.00 warning threshold without manual intervention, the human owner immediately disables public egress:
  153:      - For Preview Channel: Run `firebase hosting:channel:delete pre-ads-preview` (instant termination of preview endpoint).
  154:      - For Live Site: Run `firebase hosting:disable` or disable the site via Firebase Console > Hosting > Three-dots menu > Disable site.
  ```

### 2.3 CoS-89 / SAG-85 Must-Fix 3 & Refinements 1–3 (`§1`, `§2`, `§5.C`, `§6.A`, `§8.B`, `§11`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.5.md:19-20` & `58-63`:**
  ```markdown
  19: 5. **Public Catalog Valuations Display Strictly CDN CPG Retail (`cpgRetail`) Only; Zero Wholesale Values.**  
  20: 6. **Confirmed Ad Landing Host:** `https://numista.ai` (with SPA rewrite routing to `CatalogBrowseScreen`).
  ```
  ```markdown
  58: | **Outbound `(source)` Link** | Lines 1010–1017 | `InkWell(onTap: () async { final uri = Uri.tryParse(sourceUrl); if (uri != null) await launchUrl(uri); }, child: const Text('(source)', ...))` | **Delete `InkWell` / `launchUrl`.** Render source metadata strictly as plain non-clickable text: `Text('Source: $sourceInstitution', style: TextStyle(color: Color(0xFF6B6B6B)))`. | **SPECIFIED — to be removed at execute** |
  59: | **Foreign Coins Tab** | Lines 599–603 | `_TypeTab(label: 'Foreign Coins', isSelected: _selectedType == 'foreign', onTap: () => _onTypeChanged('foreign'))` | **Delete `Foreign Coins` `_TypeTab`.** Public catalog is strictly 100% US Coins, Notes, and Medals for Thanksgiving ad launch. | **SPECIFIED — to be removed at execute** |
  ...
  61: | **Era State Persistence** | Lines 209–214 | `void _onTypeChanged(String type) { setState(() { _selectedType = type; _applyFilters(); }); }` | **Reset era on tab switch:** Add `_selectedEra = 'all';` inside `setState`. | **SPECIFIED — to be updated at execute** |
  ```
- **Verified `MorganChatPopout` Constructor (`numista_mobile/lib/widgets/morgan_chat_popout.dart:11-16`) & CSP (`numista_mobile/firebase.json:275-276`):**
  ```dart
  11:   const MorganChatPopout({
  12:     super.key,
  13:     this.initialQuery,
  14:     required this.onClose,
  15:     this.onNavigateToCollection,
  16:   });
  ```
  ```json
  275:             "key": "Content-Security-Policy",
  276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; ... img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; ..."
  ```

---

## 3. Non-Blocking Data Hygiene Note (`CSV-v1.5-1`)

- **`CSV-v1.5-1` (`docs/MISSING_IMAGES.csv:1691` Missing Leading `$` on `estimated_cost`):**
  - **Verified in `docs/MISSING_IMAGES.csv:1691`:**
    ```csv
    1691: NAC1.MD.US.AMERICANGY.MEDAL.1976.XX.BASE.G,medal,,1976,,,"American Gynecological Society medal, United States, 1976",MISSING,MISSING,Tier 5 (Excluded - Private Mint / Awaiting License),Private Mint Archive / Excluded,In Copyright (Private Mint / Post-1929 - Excluded from PD Ingestion until Licensed),PASSED_GENERIC_ONLY,.00
    ```
  - **Non-Blocking Action at Execute:** Normalize `.00` to `$0.00` on line 1691 so all 3,202 rows use identical `$0.00` formatting.

---

## 4. Proactive No-Silo Site & Product Observations (`RADIO_NET-790`)

1. **Cross-Plan Consistency with `NET-807` (`PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1.md`):** Both `NET-808` (`v1.5`) and `NET-807` (`v1.1`) now reference the exact same 3,202 master US catalog count (`2,965` coins + `181` notes + `56` medals), the same `CatalogBrowseScreen` on `origin/dev` (`18a8b8e5`), the same CDN CPG retail (`cpgRetail`)-only valuation policy, and the same `$25.00/mo` hard egress budget cap + manual Hosting shutoff.
2. **Preview Channel First-Paint Verification:** During the `pre-ads-preview` gate (`§9.B` line 368), verify that `catalog_index_v20261105.json` is served with `Content-Encoding: br` or `gzip` from Firebase Hosting so first-load payload transfer stays under ~60 KB over the wire (< 2.0s first paint on mobile 4G).
