# ARGON (GEMINI 3.8) TECHNICAL & DATA HYGIENE REVIEW: `FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` (`BATON_NET-811`)

- **Reviewer:** Argon — Gemini 3.8 Independent Technical & Data Hygiene Auditor
- **Track / Baton:** `NET-777` / `NET-788` / `NET-803` / `NET-804` / `NET-808` / `BATON_NET-811` (`CRITICAL PATH` — Thanksgiving Meta Ads)
- **Target Plan Reviewed:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` (391 lines)
- **Target Inventory Reviewed:** `docs/MISSING_IMAGES.csv` (3,203 lines = 1 header + 3,202 data rows)
- **Timestamp:** 2026-11-05 18:07 ET
- **Composite Score:** **96 / 100 (`PASS — 0 Blocking Plan Must-Fixes; 2 Non-Blocking Execution Safeguards EX-811-1..EX-811-2 & 1 CSV Note CSV-v1.6-1 Logged`)**
- **Execution Posture:** **PLAN REVIEW ONLY** (`origin/main` locked at `9f04550a`, Stripe strictly OFF, zero code edits, zero deployments, zero Firestore writes/seeding)

---

## 1. Executive Verdict & Rubric Breakdown

`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` resolves the **4 blocking must-fixes** from Grok Bot CoS (`COS_SCORE_NET-808_FAILFIX-777-v1.5_20261105.md` — 87/100 FAIL) and Stand Alone Grok (`SAG_SCORE_NET-808_20261105.md` — 84/100 FAIL):
1. **Rollback (`§1` lines 37–41, `§9.A` lines 319–340):** Replaces the stale `18a8b8e5` file checkout with `git revert <execute commit set>` pinned to the actual pre-execute `origin/dev` HEAD (`b0b05808` at review time), covering `catalog_browse_screen.dart`, `firebase.json`, `main.dart`, and associated assets, paired with Firebase Hosting release restore / preview channel deletion.
2. **Real Egress Stop (`§1` lines 43–47, `§3.E` lines 130–148):** Removes the present-tense claim that `stop-public-egress` exists or halts Hosting bandwidth, acknowledges Firebase Hosting CDN egress (`$0.15/GB` above 10 GB) is the billed path, marks `gs://numista-catalog-assets`, the Pub/Sub topic, and programmatic Cloud Functions as *"Unbuilt — to be provisioned by Cloud Infrastructure Owner"*, and relies on the named human operator (`Founder Eric / Grok Bot CoS`) executing `firebase hosting:channel:delete pre-ads-preview` or `firebase hosting:disable`.
3. **Real Loader Wiring & Retail Precedence (`§2` line 74, `§8.B` lines 299–314):** Wires directly into `assets/catalog/catalog_public_v1.json` in `_loadCatalog()`, specifies CDN CPG retail (`cpgRetail`) only (zero wholesale), and enforces that positive retail (`valCpg > 0`) is never hidden behind pending status flags.
4. **Mintage Metadata & Outbound Link Removal (`§2` line 72, `§8.A` lines 256–297):** Removes undefined `sourceInstitution`, uses actual `_buildMintageRow` variables (`val` and `label`), and deletes the `InkWell` / `launchUrl(uri)` block (`dev:1010-1017`).

| Rubric Dimension | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Grounded Rollback Architecture (`§1`, `§9.A` — Must-Fix 1)** | 25 | **25 / 25** | Records pre-execute `origin/dev` HEAD (`b0b05808` at review), uses `git revert <execute commit set>` across all touched files (`catalog_browse_screen.dart`, `firebase.json`, `main.dart`, and assets), removes `18a8b8e5` and `9f04550a` checkouts, and retains Hosting release restore / channel delete. |
| **2. Real Egress Stop & Human Operator Protocol (`§1`, `§3.E` — Must-Fix 2)** | 25 | **24 / 25** | Removes active `stop-public-egress` claims, identifies Firebase Hosting CDN egress (`$0.15/GB` over 10 GB) as the billed path, and names human operator + manual `firebase hosting:disable` / channel delete. Logged `EX-811-2` (-1 pt) to treat `numista-uploads-studio-9101802118-8c9a8` and the `$20.00/mo` email alert as to-be-verified/configured rather than assumed active. |
| **3. Wiring the Real Loader & Retail Precedence (`§2`, `§8.B` — Must-Fix 3)** | 20 | **18 / 20** | Wires into `assets/catalog/catalog_public_v1.json`, enforces `valCpg > 0` display precedence over pending flags, and forbids AI replicas in primary slots. Logged `EX-811-1` (-2 pts) to include explicit unit/widget tests proving positive `cpgRetail` is never hidden by pending flags and to note the 1-line offset on `_loadCatalog()` (`dev:59-63` vs `58-63`) and `initialNacCode` (`dev:72-100` vs `68-75`). |
| **4. Mintage Metadata & Outbound Link Removal (`§2`, `§8.A` — Must-Fix 4)** | 15 | **15 / 15** | Uses real variables `val` (`mintage?['value']?.toString()`) and `label` (`mintage?['label'] as String?`) in `_buildMintageRow`, deletes `InkWell` and `launchUrl`, and eliminates undefined `sourceInstitution`. |
| **5. Deep-Link, `MorganChatPopout` Constructor & CSV Hygiene (`§3.C`, `§4`, `§5`)** | 15 | **14 / 15** | `MorganChatPopout` constructor (`lib/widgets/morgan_chat_popout.dart:11-16`) verified identical; 3,202 CSV rows verified (`2,354 / 639 / 181 / 1 / 27`). Logged `CSV-v1.6-1` (-1 pt) for `docs/MISSING_IMAGES.csv:1691` (`.00` -> `$0.00`). |
| **TOTAL** | **100** | **96 / 100** | **PASS (`>= 95` Gate Met)** |

---

## 2. Rule 6(a) / `NET-767` Verbatim Code & Plan Verification (All Files Read via `read_file` in This Turn)

### 2.1 Grounded Rollback Architecture (`§9.A`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:319-339`:**
  ```markdown
  319: ### A. Dedicated Repo-Safe Rollback Procedures (No `9f04550a` checkouts)
  320: 1. **Pre-Execute dev HEAD Recorded:**
  321:    - Pre-execute `origin/dev` HEAD is recorded at execution start (`b0b05808` at review time).
  322: 2. **Code Rollback on `dev`:**
  323:    - Execute `git revert` across the complete execute commit set:
  324:      ```bash
  325:      git revert <execute commit set>
  326:      ```
  327:    - Reverts all touched files cleanly: `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, `numista_mobile/firebase.json`, `numista_mobile/lib/main.dart`, and associated assets.
  328:    - Does NOT checkout `18a8b8e5` (which would strip intervening documentation commits).
  329:    - Never touches or checks out from `9f04550a`.
  ```

### 2.2 Real Egress Stop & Human Manual Shutoff (`§3.E`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:136-148`:**
  ```markdown
  138:    - Dedicated catalog storage bucket `gs://numista-catalog-assets`, Pub/Sub topic `projects/numista-ai/topics/billing-budget-alerts`, and programmatic IAM spend-stop Cloud Functions are **Unbuilt — to be provisioned by Cloud Infrastructure Owner (Founder Eric / Grok Bot CoS)**. No unbuilt resources are treated as active in code.
  139: 3. **Billed Egress Reality:**
  140:    - Firebase Hosting CDN egress ($0.15/GB above 10 GB free tier) is the active billed path under Meta ad traffic.
  141:    - Cloud Storage bucket IAM permissions cannot halt Firebase Hosting traffic.
  142: 4. **Named Human Operator & Manual Shutoff Procedure (Operational Fail-Safe):**
  143:    - **Named Operator:** Founder Eric / Grok Bot CoS.
  ...
  146:      - For Preview Channel: `firebase hosting:channel:delete pre-ads-preview` (instantly removes preview channel and terminates egress).
  147:      - For Live Production: `firebase hosting:disable` (instantly disables the site) or disables via Firebase Console > Hosting > Three-dots menu > Disable site.
  ```

### 2.3 Real Loader Wiring, Retail Precedence & `_buildMintageRow` (`§8.A` & `§8.B`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:270-313`:**
  ```markdown
  270:   Widget _buildMintageRow(Map<String, dynamic> item) {
  271:     final mintage = item['mintage'] as Map?;
  272:     final val = mintage?['value']?.toString();
  273:     final label = mintage?['label'] as String?;
  ...
  305:    ```dart
  306:    final double? valCpg = (entry['cpgRetail'] as num?)?.toDouble();
  307:    if (valCpg != null && valCpg > 0) {
  308:      // Display formatted CPG Retail price: fmt.format(valCpg)
  309:      // NEVER hidden by pending AI or enrichment flags
  310:    } else {
  311:      // Render gold 'Valuation Pending' chip strictly when valCpg <= 0 or null
  312:    }
  313:    ```
  ```

---

## 3. Non-Blocking Execution Safeguards (`EX-811-1`, `EX-811-2`, `CSV-v1.6-1`)

1. **`EX-811-1` (Loader & Deep-Link Line Offsets on `origin/dev` + Positive Retail Unit Test):**
   - On `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, `Future<void> _loadCatalog() async` starts at line **59** (`rootBundle.loadString('assets/catalog/catalog_public_v1.json')` at line **61**), and the `if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty)` block spans lines **72–100** (plan cites `58–63` and `68–75`).
   - At execution time, include a widget/unit test in `numista_mobile/test/` asserting that when `entry['cpgRetail'] > 0` (even if `enrichment_status == 'pending'` or `aiValue == 'Pending'`), the formatted CPG retail price renders and `'Valuation Pending'` is not shown, and that `primary_image_url` is validated against the internal own-origin allowlist before rendering.
2. **`EX-811-2` (Verify Studio Bucket & `$20.00/mo` Billing Alert Before Marking Active):**
   - Treat `numista-uploads-studio-9101802118-8c9a8` (`§3.E` line 137) and the `$20.00/month` billing alert email (`§3.E` line 144) as cloud configuration items to be verified/enabled by the Cloud Infrastructure Owner (`Founder Eric / Grok Bot CoS`) rather than assumed pre-existing in repo code.
3. **`CSV-v1.6-1` (`docs/MISSING_IMAGES.csv:1691`):**
   - Verified in `docs/MISSING_IMAGES.csv:1691`:
     ```csv
     1691: NAC1.MD.US.AMERICANGY.MEDAL.1976.XX.BASE.G,medal,,1976,,,"American Gynecological Society medal, United States, 1976",MISSING,MISSING,Tier 5 (Excluded - Private Mint / Awaiting License),Private Mint Archive / Excluded,In Copyright (Private Mint / Post-1929 - Excluded from PD Ingestion until Licensed),PASSED_GENERIC_ONLY,.00
     ```
   - Normalize `.00` to `$0.00` on line 1691 at execute.

---

## 4. Proactive No-Silo Site & Product Observations (`RADIO_NET-790`)

1. **Pre-Federal Flag Verification in `assets/catalog/catalog_public_v1.json`:** When wiring `assets/catalog/catalog_public_v1.json` (`§7` lines 244–250 & `§8.B` lines 300–313), verify that the 9 Condition C1 pre-federal records in `catalog_public_v1.json` carry `"is_pre_federal": true` or `"pre_federal": true` in the bundled JSON asset so the flag-only filter returns all 9 items immediately on load.
