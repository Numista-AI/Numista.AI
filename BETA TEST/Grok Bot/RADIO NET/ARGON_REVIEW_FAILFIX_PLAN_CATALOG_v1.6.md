# ARGON (GEMINI 3.8) TECHNICAL & DATA HYGIENE REVIEW: `FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` (`BATON_NET-811`)

- **Reviewer:** Argon — Gemini 3.8 Independent Technical & Data Hygiene Auditor
- **Track / Baton:** `NET-777` / `NET-788` / `NET-803` / `NET-804` / `NET-808` / `BATON_NET-811` (`CRITICAL PATH` — Thanksgiving Meta Ads)
- **Target Plan Reviewed:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` (391 lines)
- **Target Inventory Reviewed:** `docs/MISSING_IMAGES.csv` (3,203 lines = 1 header + 3,202 data rows)
- **Timestamp:** 2026-11-05 17:30 ET
- **Composite Score:** **99 / 100 (`PASS — 0 Blocking Plan Must-Fixes; 1 Non-Blocking CSV Formatting Note`)**
- **Execution Posture:** **PLAN REVIEW ONLY** (`origin/main` locked at `9f04550a`, Stripe strictly OFF, zero code edits, zero deployments, zero Firestore writes/seeding)

---

## 1. Executive Verdict & Rubric Breakdown

`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` resolves all **4 blocking must-fixes** and **2 non-blocking refinements** from Grok Bot CoS (`COS_SCORE_NET-808_FAILFIX-777-v1.5_20261105.md` — 87/100 FAIL) and Stand Alone Grok (`SAG_SCORE_NET-808_20261105.md` — 84/100 FAIL), while fully preserving all v1.5 verified components (3,202-row tier alignment, `MorganChatPopout` constructor match, Condition C1 strict flag-only filter, and Catalog-First AI rule).

| Rubric Dimension | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Grounded Rollback Architecture (§1, §9.A — CoS & SAG Must-Fix 1)** | 25 | **25 / 25** | Recorded true pre-execute `origin/dev` HEAD (`b0b058087f1492244a0c0b769e126b38ac1ba06c`). Pinned rollback to `git revert <execute commit set>` back to `b0b05808`, explicitly covering all touched files (`catalog_browse_screen.dart`, `firebase.json`, `main.dart`, new helpers, and JSON payloads). Eliminated stale `18a8b8e5` checkout. Retained named Firebase Hosting release restore / preview channel delete. |
| **2. Real Egress Stop & Human Operator Protocol (§1, §3.E — CoS & SAG Must-Fix 2)** | 25 | **25 / 25** | Struck claims that `stop-public-egress` function exists or disables IAM/CDN. Acknowledged Firebase Hosting CDN egress ($0.15/GB above 10 GB free) is the billed path under Meta ad traffic; bucket IAM cannot stop Hosting traffic. Labeled target resources unbuilt. Named human operator (Founder Eric / Grok Bot CoS) and manual shutoff (`firebase hosting:channel:delete pre-ads-preview` / `firebase hosting:disable`). |
| **3. Wiring the Real Loader & Retail Precedence (§1, §2, §8.B — CoS & SAG Must-Fix 3)** | 20 | **20 / 20** | Grounded in actual loader `rootBundle.loadString('assets/catalog/catalog_public_v1.json')` (lines 58–60). Specified `cpgRetail` present when sourced; zero wholesale. Valuation display precedence enforced: `valCpg > 0` unconditionally displays formatted price (never suppressed by pending flags); gold `'Valuation Pending'` chip rendered strictly when `valCpg <= 0`. Clean SVG silhouette placeholder fallback; zero AI replicas in primary slots. |
| **4. Correct Mintage Metadata & Outbound Link Removal (§1, §2, §8.A — CoS & SAG Must-Fix 4)** | 15 | **15 / 15** | Grounded in real variables in `_buildMintageRow` (lines 987–1023): `val`, `label`, and `sourceUrl`. Removed undefined `sourceInstitution`. Deleted entire `InkWell` and `launchUrl` block (lines 1010–1017); rendered mintage value/label as plain non-clickable text. Zero outbound links; zero undefined variables. |
| **5. Deep-Link, Constructor Alignment & Standing Locks (§4, §5, §10)** | 15 | **14 / 15** | Grounded deep-linking in existing `widget.initialNacCode` handling (lines 68–75). Confirmed `MorganChatPopout` constructor is identical across both branches. Standing locks intact (`origin/main` at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes). Deducted 1 point for non-blocking CSV formatting note (one medal entry `.00` cost). |
| **TOTAL** | **100** | **99 / 100** | **PASS (`>= 95` Gate Met)** |

---

## 2. Rule 6(a) Verbatim Code Line Citations & Plan Verification

### 2.1 CoS-87 / SAG-84 Must-Fix 1: Grounded Rollback Architecture (`§9.A`) — `PASS`
- **Plan Verification (`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:320-330`):**
  ```markdown
  320: ### A. Dedicated Repo-Safe Rollback Procedures (No `9f04550a` checkouts)
  321: 1. **Pre-Execute dev HEAD Recorded:**
  322:    - Pre-execute `origin/dev` HEAD is recorded at execution start (`b0b05808` at review time).
  323: 2. **Code Rollback on `dev`:**
  324:    - Execute `git revert` across the complete execute commit set:
  325:      ```bash
  326:      git revert <execute commit set>
  327:      ```
  328:    - Reverts all touched files cleanly: `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, `numista_mobile/firebase.json`, `numista_mobile/lib/main.dart`, and associated assets.
  329:    - Does NOT checkout `18a8b8e5` (which would strip intervening documentation commits).
  330:    - Never touches or checks out from `9f04550a`.
  ```
- **Codebase Verification on `origin/dev`:**
  - Git rev-parse confirms `origin/dev` HEAD is `b0b058087f1492244a0c0b769e126b38ac1ba06c`.
  - Stale `18a8b8e5` checkout is completely eliminated, preserving all documentation and baton commits on `dev`.

### 2.2 CoS-87 / SAG-84 Must-Fix 2: Real Egress Stop & Human Operator Protocol (`§3.E`) — `PASS`
- **Plan Verification (`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:139-148`):**
  ```markdown
  139: 3. **Billed Egress Reality:**
  140:    - Firebase Hosting CDN egress ($0.15/GB above 10 GB free tier) is the active billed path under Meta ad traffic.
  141:    - Cloud Storage bucket IAM permissions cannot halt Firebase Hosting traffic.
  142: 4. **Named Human Operator & Manual Shutoff Procedure (Operational Fail-Safe):**
  143:    - **Named Operator:** Founder Eric / Grok Bot CoS.
  144:    - **Threshold Alert:** Automated billing alert email at **$20.00/month**.
  145:    - **Manual Shutoff Protocol:** If monthly spend nears the $25.00 ceiling, the named human operator immediately executes:
  146:      - For Preview Channel: `firebase hosting:channel:delete pre-ads-preview` (instantly removes preview channel and terminates egress).
  147:      - For Live Production: `firebase hosting:disable` (instantly disables the site) or disables via Firebase Console > Hosting > Three-dots menu > Disable site.
  148: 5. **Procurement Cost:** Strict **$0.00**.
  ```
- **Technical Auditor Verification:**
  - Accurately reflects Firebase Hosting pricing model ($0.15/GB above 10 GB free tier).
  - Explicitly states unbuilt Cloud Functions are not active; provides human operational control via CLI/Console.

### 2.3 CoS-87 / SAG-84 Must-Fix 3: Wiring the Real Loader & Retail Precedence (`§2`, `§8.B`) — `PASS`
- **Verbatim Code on `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:58-61`:**
  ```dart
  58:   Future<void> _loadCatalog() async {
  59:     try {
  60:       final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
  61:       final List<dynamic> raw = json.decode(jsonString);
  ```
- **Plan Verification (`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:300-313`):**
  ```markdown
  300: ### B. Real Loader Wiring & Valuation Rules
  301: In `_loadCatalog()` (lines 58–63):
  302: 1. **Source Data:** Loads `assets/catalog/catalog_public_v1.json`.
  303: 2. **CPG Retail Only:** Each entry exposes `cpgRetail` (double) when sourced. Zero wholesale prices are present or displayed.
  304: 3. **Valuation Display Precedence (Card Grid):**
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
- **Technical Auditor Verification:**
  - Wires directly into `rootBundle.loadString('assets/catalog/catalog_public_v1.json')`.
  - Guarantees positive retail (`valCpg > 0`) is never suppressed by pending status flags.

### 2.4 CoS-87 / SAG-84 Must-Fix 4: Correct Mintage Metadata & Outbound Link Removal (`§2`, `§8.A`) — `PASS`
- **Verbatim Code on `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:987-1018`:**
  ```dart
  987:   Widget _buildMintageRow(Map<String, dynamic> item) {
  988:     final mintage = item['mintage'] as Map?;
  989:     final val = mintage?['value']?.toString();
  990:     final label = mintage?['label'] as String?;
  991:     final sourceUrl = mintage?['source_url'] as String?;
  ...
  1010:                        InkWell(
  1011:                          onTap: () async {
  1012:                            final uri = Uri.tryParse(sourceUrl);
  1013:                            if (uri != null) await launchUrl(uri);
  1014:                          },
  1015:                          child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)),
  1016:                        ),
  ```
- **Plan Verification (`docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md:270-295`):**
  ```markdown
  270:   Widget _buildMintageRow(Map<String, dynamic> item) {
  271:     final mintage = item['mintage'] as Map?;
  272:     final val = mintage?['value']?.toString();
  273:     final label = mintage?['label'] as String?;
  274: 
  275:     return Padding(
  276:       padding: const EdgeInsets.symmetric(vertical: 4),
  277:       child: Row(
  278:         crossAxisAlignment: CrossAxisAlignment.start,
  279:         children: [
  280:           const SizedBox(
  281:             width: 140,
  282:             child: Text(
  283:               'Mintage:',
  284:               style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF475569)),
  285:             ),
  286:           ),
  287:           Expanded(
  288:             child: val != null && val.isNotEmpty
  289:                 ? Text(val, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B2545)))
  290:                 : Text(label ?? 'Needs source', style: const TextStyle(fontSize: 16, color: Color(0xFF6B6B6B))),
  291:           ),
  292:         ],
  293:       ),
  294:     );
  295:   }
  ```
- **Technical Auditor Verification:**
  - Uses only available variables (`val`, `label`).
  - Completely removes `InkWell` and `launchUrl(uri)` (zero outbound links).
  - Eliminates references to nonexistent `sourceInstitution`.

### 2.5 CoS & SAG Refinements: Deep-Link Handling & Morgan Constructor — `PASS`
- **Verbatim Code on `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:68-75`:**
  ```dart
  68:         if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) {
  69:           final targetNac = widget.initialNacCode!.trim().toLowerCase();
  70:           final match = _allEntries.firstWhere(
  71:             (e) => (e['nac_code'] as String? ?? '').toLowerCase() == targetNac,
  72:             orElse: () => <String, dynamic>{},
  73:           );
  74:           if (match.isNotEmpty) {
  75:             WidgetsBinding.instance.addPostFrameCallback((_) {
  ```
- **Verbatim Code in `numista_mobile/lib/widgets/morgan_chat_popout.dart:11-16`:**
  ```dart
  11:   const MorganChatPopout({
  12:     super.key,
  13:     this.initialQuery,
  14:     required this.onClose,
  15:     this.onNavigateToCollection,
  16:   });
  ```
- **Technical Auditor Verification:**
  - Deep-link extends existing `widget.initialNacCode` handling on load.
  - `MorganChatPopout` constructor signature matches identically.

---

## 3. Conclusion & Handoff Recommendation

Plan `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.6.md` achieves **99 / 100 PASS**.
All defects raised by Grok Bot CoS (87) and SAG (84) on v1.5 are fully remedied with zero regressions.

**Handoff:**
Argon passes `BATON_NET-811` to Grok Bot CoS and Stand Alone Grok (SAG, grok-4.7) for independent dual-scoring against the `>= 95` gate.

*Execution Posture: PLAN ONLY. Zero code edits, zero deployments, zero Firestore writes/seeding.*
