# ARGON TECHNICAL REVIEW: `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md`

- **Reviewer:** Argon (`31035602` — Gemini 3.8 Code & Data Auditor, Review-Only)
- **Baton:** `BATON_NET-762_ARGON_REVIEW_NET-747-v5_20261104-0937.md`
- **Target Plan:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v5.md`
  - **Lines:** `419`
  - **MD5 Verified:** `81F888FD623D71C97C34B6F4ADD45F34` (matches `BATON_NET-762` line 3)
- **Attempt Counter:** Attempt 5 of 10 (Fix-Only against `INBOX/SAG_SCORE_NET-747_v4.md` + GB CoS v4 conditions)
- **Date:** 2026-11-04 10:48 ET
- **Score:** **97 / 100 — PASS (0 Blocking Must-Fixes; 4 Non-Blocking Implementation Clarifications Resolved Below)**

---

## 1. Executive Summary & Rubric Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. SAG v4 Must-Fixes `V5-1`..`V5-3` + GB CoS v4 Conditions (Unified Exact Whitelist `§3.3-W`, `reference_images/` Only, 12 `nac_code` Album Renames, `--negative-test`)** | 35 | **34 / 35** | Confirmed via full 3,202-record Python dry-run on `entries_master_20261103.jsonl`: applying `§3.1` + `§3.2-1..6` + `§3.3-W` yields **0 non-whitelisted hits** across all 3,202 records. (-1 non-blocking: `§3.3` line 195 should explicitly use `\beric\b` from `§0` line 50 so `"americanhistory.si.edu"` is not matched as a raw `"eric"` substring). |
| **2. SAG v4 Must-Fixes `V5-4`..`V5-8` (590-Row Tie-Break, No Email Field, Strip `varieties`/`sources` Internal Keys, Badge Priority, `--dry-run`)** | 35 | **34 / 35** | All 5 items are cleanly resolved in `§4.1-2` (line 208), `§4.7` (line 276), `§3.1` (lines 125, 136, 149, 375), `§4.3` (line 239), and `§3.3-D` / `§8.2-1` (lines 197, 382). (-1 non-blocking: `§2` Table row line 90 still describes input `Varieties in Master` keys `source`/`status`, though `§3.1` lines 125, 136, 149, 375 strip them on output). |
| **3. Resolution of `BATON_NET-762` Open Question (Pre-Federal Count 9 vs 10 — `1789` Washington Medal)** | 15 | **15 / 15** | Audited `entries_master_20261103.jsonl` lines 1–10: `pre_federal == true` is **9** (lines 1–9, `1778`–`1787`); `year < 1792` is **10** because line 10 (`NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3`) has `"year": 1789` and `"pre_federal": false`. Resolved below: use `pre_federal == true` (**9** records). |
| **4. Argon-Flagged Items on `v5` Line 30 ("One Input Path" & "Ask Morgan Route")** | 15 | **14 / 15** | Both verified against workspace and `numista_mobile` source below (-1 non-blocking: use `AiChatScreen(initialQuery: ...)` / `onAskMorganWithQuery` rather than a `/chat` named route). |
| **TOTAL** | **100** | **97 / 100** | **PASS — Ready for SAG & GB CoS Scoring** |

---

## 2. Definitive Answer to `BATON_NET-762` Open Question: Pre-Federal Count (`9` vs `10`)

- **Question (`BATON_NET-762` line 4 & `v5` `§8.2-4` line 401):**
  > *"Resolve the open question on line 401: is the Pre-Federal count 9 or 10? The 1789 Washington medal has pre_federal=false."*

- **Direct Verification Against `entries_master_20261103.jsonl` (Lines 1–10):**
  - **Lines 1–9 (`pre_federal: true`, `year` `1778`–`1787` — 9 records total: 1 banknote, 1 medal, 7 coins):**
    1. Line 1: `NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2` (`year: 1778`, `pre_federal: true`, `type: "banknote"`)
    2. Line 2: `NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S` (`year: 1782`, `pre_federal: true`, `type: "medal"`, `"Libertas Americana medal"`)
    3. Line 3: `NAC1.CN.US.1C.NOVACONST.1783.XX.CONF.M` (`year: 1783`, `pre_federal: true`, `type: "coin"`)
    4. Line 4: `NAC1.CN.US.1C.CONNCOPPER.1785.XX.CT.C` (`year: 1785`, `pre_federal: true`, `type: "coin"`)
    5. Line 5: `NAC1.CN.US.1C.VERMCOPPER.1785.XX.VT.G` (`year: 1785`, `pre_federal: true`, `type: "coin"`)
    6. Line 6: `NAC1.CN.US.1C.NJCOPPER.1786.XX.NJ.6` (`year: 1786`, `pre_federal: true`, `type: "coin"`)
    7. Line 7: `NAC1.CN.US.1C.FUGIO.1787.XX.BASE.1` (`year: 1787`, `pre_federal: true`, `type: "coin"`)
    8. Line 8: `NAC1.CN.US.1C.MASSCENT.1787.XX.MA.C` (`year: 1787`, `pre_federal: true`, `type: "coin"`)
    9. Line 9: `NAC1.CN.US.HC.MASSHALF.1787.XX.MA.1` (`year: 1787`, `pre_federal: true`, `type: "coin"`)
  - **Line 10 (`pre_federal: false`, `year: 1789` — 10th record with `year < 1792`):**
    - `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl:10`:
      ```json
      {"nac_code": "NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3", "name": "George Washington, Indian Peace Medal, United States, ca 1789", "type": "medal", "denomination": null, "year": 1789, "era": "Pre-Federal & Founding (to 1792)", "mint_facility": null, "mint_mark_on_coin": null, "series": null, "designer": null, "composition": "metal, silver, shell beads", "weight_g": null, "diameter_mm": 76.0, "mintage": {"value": null, "label": "not yet sourced", "source_url": null}, "varieties": [], "history": null, "pre_federal": false, "pre_federal_state": null, "primary_image": null, "sources": [{"label": "Smithsonian NMAH / National Numismatic Collection record", "url": "https://americanhistory.si.edu/collections/object/nmah_962562"}], "social_posts": [], "published_on_x": false, "record_status": "PREVIEW_DRAFT", "needs_fact_check": [], "measurement_note": "Specimen measurement from the NNC record: medal: .6 cm x 7.6 cm; 1/4 in x 3 in", "figures": {"mintage": {"value": null, "label": "not yet sourced", "status": "NOT_YET_SOURCED"}}, "proposal_status": "PROPOSAL", "fold_source": "entries_20261103"}
      ```

- **Why Line 10 has `"pre_federal": false`:**
  - The U.S. Federal government under President George Washington took office in **1789** under the ratified U.S. Constitution (3 years before the Coinage Act of 1792 established the Philadelphia Mint). Thus, the 1789 George Washington Indian Peace Medal is a **Federal presidential medal** (`pre_federal: false`), whereas lines 1–9 (`1778`–`1787`) are Continental Congress / Confederation / State / Colonial pre-federal issues (`pre_federal: true`).
- **Argon's Ruling:**
  - **The Pre-Federal count is `9`.**
  - In `catalog_public_builder.py` (`§3.1` line 144) and `catalog_browse_screen.dart` (`§4.3` line 236 & `§8.2-4` line 401), evaluate **strictly `entry.preFederal == true` (`pre_federal == true`)** without the `|| (year != null && year < 1792)` fallback. That respects the master dataset's explicit `"pre_federal": false` on `NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3` and makes `§2` line 84 (`9 entries`), `§3.1` line 144 (`true on 9 entries`), `§4.3` line 236 (`9 entries`), and `§8.2-4` line 401 (`returns 9 records`) 100% consistent.

---

## 3. Audit of All 8 SAG `v4` Must-Fixes (`V5-1`..`V5-8`) & GB CoS `v4` Conditions

### 3.1 `V5-1` (SAG MF1 + GB CoS Condition 1): Single Unified Exact Case-Sensitive Whitelist (`§3.3-W`) — **FIXED (`PASS`)**

- **Plan Citations (`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v5.md`):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:179-193`:
    ```markdown
    **§3.3-W — Exact case-sensitive whitelist (single source of truth for §0, §3.3, and §8.1):**
    Before scanning for the bare word `collection` / `collector`, the validator masks ONLY these exact case-sensitive substrings (no bare-word exemption):
    1. `si.edu/collections/` (Smithsonian URL path — 173 hits after §3.2-1 rewrite)
    2. `si.edu/collection/` (defensive singular path)
    3. `metmuseum.org/art/collection/` (Met URL path — 2 hits)
    4. `numismatics.org/collection/` (ANS URL path — 1 hit)
    5. `numismatics.org/collectionimages/` (ANS image URL path — 1 hit)
    6. `coin collection; public domain` (Wikimedia Commons license/credit line — 3 hits)
    7. `Josiah K. Lilly Jr. Collection` (proper-noun museum provenance — 1 hit in `series` on `NAC1.CN.US.20DOLLARS.JOSIAHKLIL.1927.XX.BASE.J`)
    8. `acquired with the Lilly Collection` (proper-noun museum provenance in 1822 $5 `history` — 1 hit)
    9. `collectors still hunt` (numismatic narrative phrase in 1982-D 1c `history` — 1 hit)
    10. `a-collectors-guide` (CoinWeek URL slug on 1795 $5 — 1 hit)
    ```
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:172-174`:
    ```markdown
    6. **2 residual `collection` occurrences (rewritten in builder so no loose exemption is needed):**
       - `NAC1.CN.US.20DOLLARS.COINS.1849.P.BASE.S` (`history`): rewrite `"This large collection includes"` → `"This large holding includes"`.
       - `NAC1.CN.US.20DOLLARS.COINS.1849.P.BASE.S` (or whichever record carries `https://coinweek.com/heritage-auctions-to-present-the-harvey-b-jacobson-jr-collection-of-early-half-eagles-at-fun-2026/` in `sources[].url`): drop that secondary CoinWeek URL from `sources[]` (primary Smithsonian NMAH source remains).
    ```
- **Dry-Run Verification Against All 3,202 Records of `entries_master_20261103.jsonl`:**
  - Verified that `NAC1.CN.US.20DOLLARS.COINS.1849.P.BASE.S` (line 199) carries `"This large collection includes"` in `history`, while **Line 27 (`NAC1.CN.US.5D.CAPBUST.1795.P.V2.4`)** carries `"url": "https://coinweek.com/heritage-auctions-to-present-the-harvey-b-jacobson-jr-collection-of-early-half-eagles-at-fun-2026/"` in `sources[]`:
    - `entries_master_20261103.jsonl:27` (excerpt):
      ```json
      {"nac_code": "NAC1.CN.US.5D.CAPBUST.1795.P.V2.4", "name": "1795-dated $5 half eagle, heraldic eagle (struck c.1797-98)", ... "sources": [{"label": "americanhistory.si.edu", "url": "https://americanhistory.si.edu/collections/object/nmah_835253", "tier": "primary-museum", "note": null}, {"label": "SECONDARY: coinweek.com", "url": "https://coinweek.com/heritage-auctions-to-present-the-harvey-b-jacobson-jr-collection-of-early-half-eagles-at-fun-2026/", "tier": "secondary", "note": null}, ...]}
      ```
  - Because `§3.2-6` line 174 specifies `(or whichever record carries https://coinweek.com/heritage-auctions-to-present-the-harvey-b-jacobson-jr-collection-of-early-half-eagles-at-fun-2026/ in sources[].url)`, matching by the URL string drops it on `NAC1.CN.US.5D.CAPBUST.1795.P.V2.4` and produces **0 non-whitelisted leaks** across all 3,202 records.
  - **Implementation Note 1 (`\beric\b` Word Boundary):** In `pii_gate_validator.py`, implement `eric` as word-bounded regex `\beric\b` (as specified in `§0` line 50: `word-bounded \beric\b`), NOT raw substring `"eric"` (`§3.3` line 195), because raw substring `"eric"` matches `"americanhistory.si.edu"` (`1,059` URLs) and `"America"`.

---

### 3.2 `V5-2` (SAG MF2 + GB CoS Condition 2): `reference_images/<basename>` Only & Zero `seed_images/` Leaks — **FIXED (`PASS`)**

- **Plan Citations (`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v5.md`):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:42`:
    ```markdown
    - Zero PII / internal-codename / internal-status / internal-path leakage in shipped bundle (verified by automated build-time gate + pytest against a concrete forbidden-token list, with **zero non-whitelisted hits**).
    ```
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:171`:
    ```markdown
    5. **`local_path` → `local`:** strip `/workspace/image-intake/catalog-research/catalog-preview/` and `seed_images/`; emit `reference_images/<basename>` (or `assets/catalog/reference_images/<basename>`) ONLY. Any residual `seed_images/`, `/workspace`, `gs://`, `users/`, or `googleapis` in any image field is rewritten or dropped; `fold_source` is never emitted.
    ```

---

### 3.3 `V5-3` (SAG MF3): Exact 12 `nac_code` Album/Series Renames, `pii_gate_validator.py` on Built JSON, and `--negative-test` — **FIXED (`PASS`)**

- **Plan Citations (`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v5.md`):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:156-169`:
    ```markdown
    3. **12 U.S. Mint product-title entries containing `"Collection"` in `name` / `series`** — rewrite `"Coin Collection"` → `"Coin Set"`, `"Nickel Collection"` → `"Nickel Set"`, and `"Dollar Collection"` → `"Dollar Set"` in public `name` and `series` ONLY on these exact 12 `nac_code`s (`nac_code` is never altered):
       1. `NAC1.CN.US.1C.THEWORLDWA.1942.S.BASE.1` — `"1942-S The World War II U.S. Coin Collection 1 cent"` → `"1942-S World War II U.S. Coin Set 1 cent"` (`series`: `"World War II U.S. Coin Set"`)
       2. `NAC1.CN.US.50C.THEWORLDWA.1942.S.BASE.K` — `"1942-S The World War II U.S. Coin Collection half dollar"` → `"1942-S World War II U.S. Coin Set half dollar"` (`series`: `"World War II U.S. Coin Set"`)
       3. `NAC1.CN.US.25C.THEWORLDWA.1942.S.BASE.H` — `"1942-S The World War II U.S. Coin Collection quarter"` → `"1942-S World War II U.S. Coin Set quarter"` (`series`: `"World War II U.S. Coin Set"`)
       4. `NAC1.CN.US.5C.THEUSNICKE.1975.XX.BASE.2` — `"1975 The U.S. Nickel Collection"` → `"1975 U.S. Nickel Set"` (`series`: `"U.S. Nickel Set"`)
       5. `NAC1.CN.US.5C.THEUSNICKE.1993.XX.BASE.J` — `"1993 The U.S. Nickel Collection"` → `"1993 U.S. Nickel Set"` (`series`: `"U.S. Nickel Set"`)
       6. `NAC1.CN.US.5C.THEUSNICKE.1998.XX.BASE.T` — `"1998 The U.S. Nickel Collection"` → `"1998 U.S. Nickel Set"` (`series`: `"U.S. Nickel Set"`)
       7. `NAC1.CN.US.1D.MODERNMORG.2023.XX.BASE.S` — `"2023 Modern Morgan and Peace Silver Dollar Collection"` → `"2023 Modern Morgan and Peace Silver Dollar Set"` (`series`: `"Modern Morgan and Peace Silver Dollar Set"`)
       8. `NAC1.CN.US.1D.MODERNMORG.2023.XX.MORGANDOLL.Q` — `"2023 Modern Morgan and Peace Silver Dollar Collection (Morgan Dollar)"` → `"2023 Modern Morgan and Peace Silver Dollar Set (Morgan Dollar)"` (`series`: `"Modern Morgan and Peace Silver Dollar Set"`)
       9. `NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACE.B` — `"2023 The Ultimate Modern Morgan and Peace Silver Dollar Collection"` → `"2023 Ultimate Modern Morgan and Peace Silver Dollar Set"` (`series`: `"Ultimate Modern Morgan and Peace Silver Dollar Set"`)
       10. `NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACESILVE.0` — `"2023 The Ultimate Modern Morgan and Peace Silver Dollar Collection"` → `"2023 Ultimate Modern Morgan and Peace Silver Dollar Set"` (`series`: `"Ultimate Modern Morgan and Peace Silver Dollar Set"`)
       11. `NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACEDOLLA.Y` — `"2023 The Ultimate Modern Morgan and Peace Silver Dollar Collection (Peace Dollar)"` → `"2023 Ultimate Modern Morgan and Peace Silver Dollar Set (Peace Dollar)"` (`series`: `"Ultimate Modern Morgan and Peace Silver Dollar Set"`)
       12. `NAC1.CN.US.25C.CELEBRATIN.2024.XX.DRMARYEDWA.6` — `"2024 Celebrating America Coin Collection quarter (Dr. Mary Edwards Walker)"` → `"2024 Celebrating America Coin Set quarter (Dr. Mary Edwards Walker)"` (`series`: `"Celebrating America Coin Set"`)
    ```
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:371-373`:
    ```bash
    python numista_backend/scripts/pii_gate_validator.py --in numista_mobile/assets/catalog/catalog_public_v1.json
    python numista_backend/scripts/pii_gate_validator.py --in numista_mobile/assets/catalog/catalog_public_v1.json --negative-test
    python -c "import json; d=open('numista_mobile/assets/catalog/catalog_public_v1.json', encoding='utf-8').read().splitlines(); assert sum(1 for l in d if 'americanhistory.si.edu/collections/object/nmah_' in l or 'https://www.si.edu/object/nmah_' in l) == 1070"
    ```
- **Verification:** Confirmed all 12 `nac_code`s match lines `1250, 1251, 1252, 1659, 1920, 1996, 3081, 3082, 3084, 3085, 3086, 3123` of `entries_master_20261103.jsonl` verbatim.

---

### 3.4 `V5-4`..`V5-8` (SAG MF4..MF8): 590-Row Tie-Break, Email Removal, `varieties`/`sources` Strip, Badge Priority, `--dry-run` — **FIXED (`PASS`)**

- **`V5-4` (Deterministic tie-break on the 590 `entries_20261103` rows):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:208-213`:
    ```markdown
    2. **Recently Added — 24 Cards:**
       - Selected from records originally folded from `entries_20261103.jsonl` (590 records, identified at build time BEFORE `fold_source` is stripped) with deterministic tie-break: **(1) file date (3 Nov 2026, i.e., `fold_source == "entries_20261103"`), (2) `year` descending (nulls last), (3) `nac_code` ascending**, preferring entries that have a valid image (`primary_image != null`) and `record_status == "PUBLISHED_ON_X"`, then filling remaining slots up to 24 in that exact tie-break order.
    ```
- **`V5-5` (Email input removed from Suggest-a-Correction):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:276`:
    ```markdown
    - **Fields:**
      - `nac_code` (read-only, prefilled)
      - `field_name` (dropdown: Mintage, Composition / Weight / Diameter, Designer, Variety / Error, History, Image, Source URL, Other)
      - `suggested_correction` (required text, 10–1,000 chars)
      - `source_citation` (required text/URL — e.g., Red Book page, Mint report, PCGS CoinFacts, Smithsonian link; **no email field (PII)**)
    ```
- **`V5-6` (Strip `source` & `status` from `varieties[]`, strip `tier` & `kind` from `sources[]`):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:125, 136, 149`:
    ```markdown
      "varieties": [
        {"name": "J-10", "attribution": null, "reference_work": null}
      ],
    ...
      "sources": [
        {"label": "Smithsonian NMAH (National Numismatic)", "url": "https://americanhistory.si.edu/collections/object/nmah_1075136", "title": null}
      ],
    ...
    - **`varieties[].source` and `varieties[].status`** (`SAG_PROPOSED`) AND **`sources[].tier` and `sources[].kind`** — stripped inside every variety/source object (`varieties` items keep ONLY `{name, attribution, reference_work}`; `sources` items keep ONLY `{label, url, title}`).
    ```
- **`V5-7` (Single status badge priority order):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:239`:
    ```markdown
    - **Badge Priority Order (at most 1 status badge per card):** **Pre-Federal > Details coming > Needs source** (resolving the 1 overlap record `NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2` which is both Pre-Federal and `STUB` in favor of **Pre-Federal**). The **Featured on @NumistaAi** badge is an orthogonal social-link pill rendered in the card footer / detail header.
    ```
- **`V5-8` (`--dry-run` on `entries_master_20261103.jsonl` post-rewrite projection):**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v5.md:197, 382`:
    ```markdown
    **§3.3-D — Pre-build dry-run on `entries_master_20261103.jsonl`:** `pii_gate_validator.py --dry-run --in "1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl"` runs the §3.1/§3.2 projection in memory and verifies 0 non-whitelisted forbidden hits across all 3,202 records before writing any output file.
    ```

---

## 4. Verification of Argon's Two Flagged Items (`v5` Line 30)

1. **"One Input Path" (`v5` line 30 / `§3` line 111 vs `§8.1` line 365):**
   - Verified on disk: `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\NET-747_inputs\entries_master_20261103.jsonl` exists (`3,202` lines), whereas repo-root `NET-747_inputs\entries_master_20261103.jsonl` does not exist.
   - `§8.1` lines 365–366 already pass `--in "1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl"` and `--images-in "1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/seed_images"`. Set those exact paths as the default CLI arguments in `catalog_public_builder.py` and `pii_gate_validator.py`.

2. **"Ask Morgan Route" (`v5` line 30 / `§5` line 294):**
   - Verified in `numista_mobile/lib/screens/base_layout.dart:327-355` and `numista_mobile/lib/screens/ai_chat_screen.dart:31-45`:
     - `numista_mobile/lib/screens/base_layout.dart:327-343`:
       ```dart
               return HomeDashboard(
                 onAskMorgan: () => _navigateTo('AI Deepdive'),
                 onAskMorganWithQuery: (query) {
                   if (MediaQuery.of(context).size.width >= 800) {
                     setState(() {
                       _isMorganPopoutOpen = true;
                       _popoutInitialQuery = query;
                     });
                     WidgetsBinding.instance.addPostFrameCallback((_) {
                       _popoutInitialQuery = null;
                     });
                   } else {
                     setState(() {
                       _aiInitialQuery = query;
                       _activeRoute = 'AI Deepdive';
                     });
                   }
                 },
       ```
     - `numista_mobile/lib/screens/ai_chat_screen.dart:31-35`:
       ```dart
       class AiChatScreen extends StatefulWidget {
         /// Optional pre-populated query (from "AI Deep Dive" button on a coin).
         final String? initialQuery;
         final bool isPopout;
         final bool isMinimized;
       ```
   - When wiring "Ask Morgan about this coin" in `catalog_detail_screen.dart` (`§5` line 294), use `Navigator.push(context, MaterialPageRoute(builder: (_) => AiChatScreen(initialQuery: 'Tell me about ${entry.name} (${entry.nacCode}).')))` (or `onAskMorganWithQuery` callback when hosted inside `BaseLayout`), rather than `Navigator.pushNamed(context, '/chat', ...)`.

---

## 5. Summary of Non-Blocking Implementation Notes for Build Step

1. **Pre-Federal Count (`§2` line 84, `§3.1` line 144, `§4.3` line 236, `§8.2-4` line 401):** Use `pre_federal == true` (**9 records**; excludes line 10 `NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3` which has `pre_federal: false`).
2. **`\beric\b` Word Boundary (`§0` line 50 vs `§3.3` line 195):** Use regex `\beric\b` in `pii_gate_validator.py` so `"americanhistory.si.edu"` (`1,059` URLs) and `"America"` are not false-flagged.
3. **CoinWeek URL Drop (`§3.2-6` line 174):** Drop `https://coinweek.com/heritage-auctions-to-present-the-harvey-b-jacobson-jr-collection-of-early-half-eagles-at-fun-2026/` by matching the URL substring across all records (it resides on Line 27 `NAC1.CN.US.5D.CAPBUST.1795.P.V2.4`).
4. **Ask Morgan Navigation (`§5` line 294):** Route to `AiChatScreen(initialQuery: ...)` / `onAskMorganWithQuery`.

- **Final Verdict:** **97 / 100 (`PASS`)** — Zero Blocking Must-Fixes.
