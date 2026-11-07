# FAILFIX PLAN: Public Catalog Browse — CHUNK 1 (NET-777 / NET-816 / NET-831 Items 1–2)

**Document Path:** `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.0.md`  
**Version:** `v2.0` (Chunk 1 of 6 — Scoped to `RADIO_NET-831` Items 1 & 2 Only)  
**Writer Lineage:**
- **Active Writer:** Fresh Antigravity Plan Writer (Catalog Chunk 1) — **New-Writer Attempt 1 of 4** (governed by the 4-try rule: stop and hand off after 4 failed tries).
- **Prior Lineage (preserved, not erased):** AG CoS v4 (`ba2bfdb2`) = 10+ attempts, parked under writer-cap hold; `v1.10` = 48/100 FAIL (`COS_SCORE_NET-816_CATALOG_v1.10_20261107.md`); `v1.11` = 58/100 FAIL (`COS_SCORE_NET-816_CATALOG_v1.11_20261107.md`).

**Filed DTG:** `2026-11-07T15:16:00-05:00` (3:16 PM EST, America/New_York — verified against system clock at filing)  
**Authority:** `BETA TEST/Grok Bot/8 OCT 26/OUTBOX/STARTER_CATALOG_FRESH-AG_CHUNK1_20261107.md`, `BETA TEST/Grok Bot/8 OCT 26/BATONS/RADIO_NET-831_GROKCOS-to-AGCOS_REVISE-816-v1.12_20261107.md` (items 1–2), and `BETA TEST/Grok Bot/8 OCT 26/BATONS/COS_SCORE_NET-816_CATALOG_v1.11_20261107.md` (lines 14, 17, 20, 23).

---

## 0. Standing Hard Rules & Gate Discipline

1. **PLAN ONLY:** Zero source code edits, zero builds, zero test executions, zero deploys, zero Firestore/database writes, zero GCS bucket uploads, and zero branch merges are performed in this delivery.
2. **Branch & Target Locks:**
   - Future authorized build/preview target: **`p7-v8.9` (`p7-gate` preview) only**.
   - Production lock: **`origin/main` is locked at `9f04550a` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`)** and must never be touched.
   - **Stripe:** Strictly **OFF**.
   - **Billing / Spend Controls:** **Alerts only, no spend caps.** Never modify billing or budget cap controls.
3. **Approval Chain:** GB CoS ≥ 95/100 → Independent SAG ≥ 95/100 → **Founder Eric's explicit typed `YES`** before any code execution. No Argon in the review cycle. An agent asserting approval is never approval.
4. **Scope Boundary:** This document covers **Chunk 1 only** (`RADIO_NET-831` #1 Face-Value Parser and #2 `_CatalogCard` minimal diff + Chunk 1 tests). Chunks 2–6 (#3 Images/CSP/CORS, #4 Known-Error Caller, #5 Greysheet, #6 Ask Morgan, #7 Web History, #8 Bundle C, #9 Congress.gov Key Rotation, #10 remaining tests, #11 full gate matrix) remain parked for subsequent chunks. Cards `NET-817` and all other queue items are untouched.

---

## 1. Read-Only Verified Repository Pins (`git rev-parse` / `git ls-tree` / `git show`)

Every pin reported in `STARTER_CATALOG_FRESH-AG_CHUNK1_20261107.md:17` and `COS_SCORE_NET-816_CATALOG_v1.11_20261107.md:10` was re-verified read-only on `2026-11-07`:

| Ref / Pin | Full Commit SHA | Status & Ancestry Reconciliation |
|---|---|---|
| Reported `dev` pin | `b0b058087f1492244a0c0b769e126b38ac1ba06c` | Verified ancestor of both local `dev` (`eb23e011d1e25446e256518e5065b4a989aaba17`) and `origin/dev` (`afbbbd45950c459c04a1e82b437dd346c522c3da`). Contains the Catalog source tree (`catalog_browse_screen.dart`, `catalog_public_v1.json`, `catalog_browse_test.dart`, `melt_value_service.dart`). |
| Reported `origin/dev` pin (`b15fdda1`) | `b15fdda1be1dc36bf94fd97ca1817b63992bb09d` | Verified ancestor of current `origin/dev`. Between `b15fdda1` and current `origin/dev` HEAD (`afbbbd45950c459c04a1e82b437dd346c522c3da`), three docs-only CoS commits landed (`cf622fb8`, `2de4dc93`, `afbbbd45`). Zero source files changed between `b0b05808`, `b15fdda1`, and `afbbbd45`. |
| Current `origin/dev` HEAD | `afbbbd45950c459c04a1e82b437dd346c522c3da` | Current remote `origin/dev` tip (`docs(cos): assign Antigravity Desk to NET-817 Cards/Images v1.9 (RADIO_NET-835)`). Local `dev` is at `eb23e011d1e25446e256518e5065b4a989aaba17` (ancestor of `origin/dev`). |
| Reported `p7` pin | `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` | Verified ancestor of current `p7-v8.9` / `origin/p7-v8.9` (`5fbff9afa23221e1bc9dc719f786618ac642cf03`). |
| Current `p7-v8.9` / `origin/p7-v8.9` HEAD | `5fbff9afa23221e1bc9dc719f786618ac642cf03` | Current working branch tip (`docs(plan): deliver NET-813 Unified Coin Details View Plan v1.3`). |
| Locked `origin/main` | `9f04550a45fa4da082ba8948c2d89a521a90fa45` | Verified intact at `9f04550a`. Untouched. |

### Verified Target File Blobs Across Pins

| File Path | Blob SHA (`git rev-parse`) | Presence & Identity Across Pins |
|---|---|---|
| `numista_mobile/lib/services/melt_value_service.dart` | `b210bff669d34f8a16bb63c79ea1e5b6a78db653` | **208 lines.** Byte-identical across `b0b05808` (`dev` pin), `4d17ca5e` (`p7` pin), `afbbbd45` (`origin/dev` HEAD), and `5fbff9af` (`p7-v8.9` HEAD). |
| `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` | `3a0d310936a1715034e65c7384476c19e2030ad7` | **1,232 lines.** Byte-identical on `b0b05808` (`dev` pin) and `afbbbd45` (`origin/dev` HEAD). Not yet present on `p7-v8.9` (`4d17ca5e` / `5fbff9af`). |
| `numista_mobile/test/catalog_browse_test.dart` | `3df197ca2cc0424b5dac7f1ad491a5ca9bb669af` | **91 lines.** Byte-identical on `b0b05808` (`dev` pin) and `afbbbd45` (`origin/dev` HEAD). Preserved untouched. |
| `numista_mobile/assets/catalog/catalog_public_v1.json` | `a018d13ad3a3aac2ae84afad704d53543fe2b5df` | **3,202 entries** (`2,965` `coin`, `181` `note`, `56` `medal`). Byte-identical on `b0b05808` and `afbbbd45`. |
| `numista_mobile/pubspec.yaml` | Line 1: `name: numista_ai` | Verified on both `b0b05808` and `5fbff9af` (`numista_mobile/pubspec.yaml:1`). |

---

## 2. Closeout Table for Chunk 1 (`RADIO_NET-831` Items 1–2)

| Item | CoS-58 / `RADIO_NET-831` Requirement | Verified Pinned Code Citation (`file:line` + SHA + verbatim line) | Planned Resolution in Chunk 1 (`v2.0`) | Section |
|---|---|---|---|---|
| **NET-831 #1a** | Patch `MeltValueService.parseFaceValue` (`:53–99`) in place — do not wrap it. Parse leading numerics first (`N Dollars`, `1,000 Dollars`, `10,000 Dollars`, `2 1/2 Dollars`, `3 cents`, `$1000`). Check `half dime` before `dime`. | `numista_mobile/lib/services/melt_value_service.dart:53-99` (`b0b05808` / `4d17ca5e`, blob `b210bff6`):<br>• `:53`: `static double parseFaceValue(String rawDenom, {int qty = 1}) {`<br>• `:66`: `else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }`<br>• `:74`: `else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }`<br>• `:80`: `else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }`<br>• `:81`: `else if (s.contains('half dime')) { value = 0.05; }`<br>• `:83`: `else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }`<br>• `:86`: `else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }`<br>• `:87`: `else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }` | Patch `MeltValueService.parseFaceValue` directly in `melt_value_service.dart:53-99`:<br>1. Normalize `\u00bd` (`½`) to `' 1/2'` and collapse whitespace.<br>2. Evaluate leading numeric & fractional patterns first: `^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$` (`'2 1/2 Dollars'` → `2.50`, `'G$2½'` → `2.50`), `^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$` (`'10 Dollars'` → `10.00`, `'1,000 Dollars'` → `1000.00`, `'10,000 Dollars'` → `10000.00`), `^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b` when not a range (`'3 cents'` / `'3 Cents'` → `0.03`), and `^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)` when not a multi-denomination slash/comma list (`'$1000'` → `1000.00`).<br>3. Check `$10,000`/`$10000` and `$1,000`/`$1000` before `$100`.<br>4. Move `half dime` (`0.05`) ahead of `dime` (`0.10`), and add `three cent` / `3 cent` (`0.03`) and `five cent` (`0.05`) ahead of generic `cent` (`0.01`). | §3 |
| **NET-831 #1b** | Re-count mis-valued entries directly from `catalog_public_v1.json` `denomination` values. | `numista_mobile/assets/catalog/catalog_public_v1.json` (`b0b05808`, blob `a018d13a`, 3,202 entries):<br>• `'Half dime'` (`coin` ×35) → `$0.10` instead of `$0.05`<br>• `'3 cents'` (`coin` ×6) + `'3 Cents'` (`coin` ×3) = 9 → `$0.01` instead of `$0.03`<br>• `'N Dollars'` ($N \neq 1$, 58 entries across 10 strings) → `$1.00`<br>• `'$1000'` (`note` ×1) → `$100.00` instead of `$1000.00`<br>• Plus `'G$2½'` (`coin` ×16, e.g. `NAC1.CN.US.GD2H.TURBANHEAD.1796.P.NOSTARS.2`) → `$2.00` via `:74` `s.contains(r'$2')` instead of `$2.50`. | Complete 70-row `(type, denomination)` audit table provided in §3.A. Confirms exact **103** entries in the 4 CoS-reported categories (`35 + 9 + 58 + 1 = 103`), plus **16** `'G$2½'` Quarter Eagle entries (`103 + 16 = 119` total entries corrected), and **2** non-single-USD strings (`'3¢–50¢'` fractional currency range ×1 and `'3.6 Candareens'` ×1) guarded to `0.0`. After patch, **0** mis-parses remain across all 3,202 entries. | §3.A |
| **NET-831 #1c** | State medal display (no face value) explicitly; correct contrast claim to `4.96:1` (`#856404` on `#FFF3CD`) or re-measure. | `numista_mobile/assets/catalog/catalog_public_v1.json` (`b0b05808`): all **56** entries with `"type": "medal"` have `"denomination": null` (e.g. `NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S`). | **Explicit Medal Display Rule:** Medals (`item['type'] == 'medal'`, 56/3,202 entries) are non-denominated exonumia and have no legal-tender face value. `_CatalogCard` never passes `item['name']` to `parseFaceValue` and never shows `'Face Value N/A'` or `'Value pending AI estimate'` on medals; instead, medal cards render `'No face value'` (`Color(0xFF6B6B6B)`, `fontSize: 13`).<br>**Re-measured Contrast:** `#856404` ($L = 0.141097$) on `#FFF3CD` ($L = 0.897690$) yields $(0.897690 + 0.05) / (0.141097 + 0.05) = 4.9592:1 \approx \mathbf{4.96:1}$ (passes WCAG 2.1 AA 4.5:1 threshold for normal text). | §3.B, §4 |
| **NET-831 #2** | Card patch: minimal diff to `_CatalogCard` in `catalog_browse_screen.dart`; keep pinned `1142–1149` `'type photo (date may differ)'` label and existing title/metadata styling; add `melt_value_service.dart` import at `:1–4`. No rewrite labelled "verbatim". | `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` (`b0b05808`, blob `3a0d3109`):<br>• `:1-4`: `import 'dart:convert';` / `import 'package:flutter/material.dart';` / `import 'package:flutter/services.dart';` / `import 'package:url_launcher/url_launcher.dart';`<br>• `:1123-1133`: `Text(item['name'] as String? ?? 'Coin', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0B2545), height: 1.2),)`<br>• `:1137-1140`: `Text([year, denom].where((s) => s.isNotEmpty).join(' · '), style: const TextStyle(fontSize: 15, color: Color(0xFF475569)),)`<br>• `:1142-1149`: `if (isTypeImage) const Padding(padding: EdgeInsets.only(top: 4), child: Text('type photo (date may differ)', style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),),),` | Minimal unified diff: adds `import '../../services/melt_value_service.dart';` at line 5, keeps lines `1122–1149` (title, metadata line, and `if (isTypeImage)` `'type photo (date may differ)'` block) completely unchanged, and appends the face-value / medal status row after line 1149. | §4 |
| **Chunk 1 Tests** | Planned tests (not run) in a NEW test file (keep 91-line `catalog_browse_test.dart`, package `numista_ai`) covering failing denominations, card `'type photo (date may differ)'` widget test, medal card display, and full-catalog 0-mis-parse check. | `numista_mobile/test/catalog_browse_test.dart:1-91` (`b0b05808`, blob `3df197ca`):<br>• `:1`: `import 'package:flutter/material.dart';`<br>• `:3`: `import 'package:numista_ai/screens/catalog/us_numismatics_catalog_screen.dart';`<br>• `:91`: `}` | Preserves `numista_mobile/test/catalog_browse_test.dart` (91 lines) untouched. Plans new file `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` importing `package:numista_ai/...` with unit tests for all required strings, full 3,202-entry `catalog_public_v1.json` regression check, and widget tests for `'type photo (date may differ)'` and medal `'No face value'`. | §5 |

---

## 3. Must-Fix #1: `MeltValueService.parseFaceValue` In-Place Patch & Full Catalog Re-Count

### A. Independent Re-Count of `catalog_public_v1.json` (`b0b05808`, 3,202 Entries)

Read-only inspection of `b0b05808:numista_mobile/assets/catalog/catalog_public_v1.json` (blob `a018d13ad3a3aac2ae84afad704d53543fe2b5df`) confirms **3,202 total entries**:
- `type == "coin"`: **2,965** entries
- `type == "note"`: **181** entries
- `type == "medal"`: **56** entries (100% have `"denomination": null`)
- Retail keys (`cpg_retail`, `retail`, `face_value`): **0** occurrences across all 3,202 entries.
- Primary join key `nac_code`: populated on **3,202 / 3,202** entries.

#### 1. Breakdown of the 103 CoS-Reported Mis-Valued Entries on Pinned `melt_value_service.dart:53-99`

| Failure Category | Raw `denomination` String in `catalog_public_v1.json` | Item `type` | Entry Count | Pinned `parseFaceValue` Output (`:53-99`) | Pinned Line Causing Defect | Correct Expected Output (USD) |
|---|---|---|---:|---:|---|---:|
| **1. `Half dime` shadowed by `dime`** | `'Half dime'` | `coin` | 35 | `$0.10` | `:80` `else if (s.contains('dime') ...)` executes before `:81` `else if (s.contains('half dime'))` | **`0.05`** |
| **2. `3 cents` falls through to `cent`** | `'3 cents'` | `coin` | 6 | `$0.01` | `:83` checks `'three cent'` or `'3c'` (no space), so `'3 cents'` falls through to `:86` `s.contains('cent')` | **`0.03`** |
| | `'3 Cents'` | `coin` | 3 | `$0.01` | Same as above (`toLowerCase()` → `'3 cents'`, hits `:86`) | **`0.03`** |
| **3. `N Dollars` ($N \neq 1$) falls through to `dollar`** | `'2 1/2 Dollars'` | `coin` | 1 | `$1.00` | `:73` checks `'$2.50'`, `'$2.5'`, `'quarter eagle'`, `'two and a half'`; misses `'2 1/2'`, falls through to `:87` `s.contains('dollar')` | **`2.50`** |
| | `'2 Dollars'` | `note` | 3 | `$1.00` | `:74` checks `'$2'` or `'two dollar'`; misses `'2 dollars'`, hits `:87` | **`2.00`** |
| | `'5 Dollars'` | `coin` (1), `note` (7) | 8 | `$1.00` | `:71` checks `'$5'`, `'five dollar'`, `'half eagle'`; misses `'5 dollars'`, hits `:87` | **`5.00`** |
| | `'10 Dollars'` | `note` | 11 | `$1.00` | `:70` checks `'$10'`, `'ten dollar'`, `'eagle'`; misses `'10 dollars'`, hits `:87` | **`10.00`** |
| | `'20 Dollars'` | `coin` (3), `note` (8) | 11 | `$1.00` | `:69` checks `'$20'`, `'twenty dollar'`, `'double eagle'`; misses `'20 dollars'`, hits `:87` | **`20.00`** |
| | `'50 Dollars'` | `note` | 6 | `$1.00` | `:67` checks `'$50'`, `'fifty dollar'`; misses `'50 dollars'`, hits `:87` | **`50.00`** |
| | `'100 Dollars'` | `note` | 7 | `$1.00` | `:66` checks `'$100'`, `'hundred dollar'`; misses `'100 dollars'`, hits `:87` | **`100.00`** |
| | `'500 Dollars'` | `note` | 3 | `$1.00` | `:65` checks `'$500'`, `'five hundred dollar'`; misses `'500 dollars'`, hits `:87` | **`500.00`** |
| | `'1,000 Dollars'` | `note` | 6 | `$1.00` | No thousand-dollar branch; hits `:87` `s.contains('dollar')` | **`1000.00`** |
| | `'10,000 Dollars'` | `note` | 2 | `$1.00` | No ten-thousand-dollar branch; hits `:87` `s.contains('dollar')` | **`10000.00`** |
| **4. `$1000` shadowed by `$100`** | `'$1000'` | `note` | 1 | `$100.00` | `:66` `s.contains(r'$100')` matches substring of `'$1000'` | **`1000.00`** |
| **Subtotal (CoS-Reported Categories)** | | | **103** | | `35 + 9 + 58 + 1 = 103` entries | |

#### 2. Additional Edge Cases Identified in Full 3,202-Entry Re-Count

Our exhaustive scan of all 70 distinct `(type, denomination)` combinations in `catalog_public_v1.json` identified **3 additional edge-case patterns** (18 entries) that the pinned parser also mishandles:

| Raw `denomination` String | Item `type` | Entry Count | Example `nac_code` & `name` | Pinned Output | Root Cause on Pin | Patched Output |
|---|---|---:|---|---:|---|---:|
| `'G$2½'` (`'G$2\u00bd'`) | `coin` | 16 | `NAC1.CN.US.GD2H.TURBANHEAD.1796.P.NOSTARS.2` (`1796 Turban Head (no stars)`) | `$2.00` | `:74` `s.contains(r'$2')` matches prefix of `'g$2½'` before any ½-fraction check | **`2.50`** |
| `'3¢–50¢'` (`'3\u00a2\u201350\u00a2'`) | `note` | 1 | `NAC1.BN.US.FRAC.FRAC.1862.BEP.BASE.3` (`Fractional Currency (five issues, 1862–1876)`) | `$3.00` | Multi-denomination range falls into `:91` `RegExp(r'\d+(?:\.\d+)?')` and parses `'3'` as `$3.00` | **`0.00`** (multi-value range → card displays `'—'`) |
| `'3.6 Candareens'` | `coin` | 1 | `NAC1.CN.US.36CANDAREE.EASTASIANC.1902.XX.BASE.X` (`3.6 Candareens, United States for China, 1902`) | `$3.60` | Non-USD trade pattern falls into `:91` plain numeric regex and parses `'3.6'` as `$3.60` USD | **`0.00`** (non-USD unit → card displays `'—'`) |

#### 3. Complete 70-Row `(type, denomination)` Audit Table Across All 3,202 Entries

| # | `type` | Raw `denomination` | Count | Pinned (`:53-99`) | Patched (`v2.0`) | Status |
|---:|---|---|---:|---:|---:|---|
| 1 | `coin` | `'$1 (1 oz silver)'` | 1 | `1.00` | `1.00` | Unchanged ✓ |
| 2 | `coin` | `'$10 eagle'` | 11 | `10.00` | `10.00` | Unchanged ✓ |
| 3 | `coin` | `'$100/$50/$25/$10 platinum'` | 1 | `100.00` | `100.00` | Unchanged ✓ |
| 4 | `coin` | `'$2.50 quarter eagle'` | 2 | `2.50` | `2.50` | Unchanged ✓ |
| 5 | `coin` | `'$20 double eagle'` | 15 | `20.00` | `20.00` | Unchanged ✓ |
| 6 | `coin` | `'$25 (1 oz palladium)'` | 1 | `25.00` | `25.00` | Unchanged ✓ |
| 7 | `coin` | `'$3'` | 3 | `3.00` | `3.00` | Unchanged ✓ |
| 8 | `coin` | `'$4 Stella'` | 2 | `4.00` | `4.00` | Unchanged ✓ |
| 9 | `coin` | `'$5 half eagle'` | 18 | `5.00` | `5.00` | Unchanged ✓ |
| 10 | `coin` | `'$50'` | 2 | `50.00` | `50.00` | Unchanged ✓ |
| 11 | `coin` | `'$50 (1 oz gold)'` | 1 | `50.00` | `50.00` | Unchanged ✓ |
| 12 | `coin` | `'$50/$25/$10/$5 gold'` | 1 | `50.00` | `50.00` | Unchanged ✓ |
| 13 | `coin` | `'1 Cent'` | 11 | `0.01` | `0.01` | Unchanged ✓ |
| 14 | `coin` | `'1 Dollar'` | 2 | `1.00` | `1.00` | Unchanged ✓ |
| 15 | `coin` | `'1 cent'` | 381 | `0.01` | `0.01` | Unchanged ✓ |
| 16 | `coin` | `'1$'` | 11 | `1.00` | `1.00` | Unchanged ✓ |
| 17 | `coin` | `'10 Cents'` | 4 | `0.10` | `0.10` | Unchanged ✓ |
| 18 | `coin` | `'2 1/2 Dollars'` | 1 | `1.00` | **`2.50`** | **Fixed (NET-831 #1)** |
| 19 | `coin` | `'20 Dollars'` | 3 | `1.00` | **`20.00`** | **Fixed (NET-831 #1)** |
| 20 | `coin` | `'3 Cents'` | 3 | `0.01` | **`0.03`** | **Fixed (NET-831 #1)** |
| 21 | `coin` | `'3 cents'` | 6 | `0.01` | **`0.03`** | **Fixed (NET-831 #1)** |
| 22 | `coin` | `'3.6 Candareens'` | 1 | `3.60` | **`0.00`** | **Fixed (non-USD guard)** |
| 23 | `coin` | `'5 Cents'` | 4 | `0.05` | `0.05` | Unchanged ✓ |
| 24 | `coin` | `'5 Dollars'` | 1 | `1.00` | **`5.00`** | **Fixed (NET-831 #1)** |
| 25 | `coin` | `'5 cents'` | 116 | `0.05` | `0.05` | Unchanged ✓ |
| 26 | `coin` | `'50 Cents'` | 3 | `0.50` | `0.50` | Unchanged ✓ |
| 27 | `coin` | `'50 cent coin planchet'` | 1 | `0.50` | `0.50` | Unchanged ✓ |
| 28 | `coin` | `'CC'` | 1 | `0.00` | `0.00` | Unchanged (`'—'`) ✓ |
| 29 | `coin` | `'D'` | 1 | `0.00` | `0.00` | Unchanged (`'—'`) ✓ |
| 30 | `coin` | `'Dime'` | 407 | `0.10` | `0.10` | Unchanged ✓ |
| 31 | `coin` | `'Dollar'` | 497 | `1.00` | `1.00` | Unchanged ✓ |
| 32 | `coin` | `'Dollar (two-coin set)'` | 1 | `1.00` | `1.00` | Unchanged ✓ |
| 33 | `coin` | `'G$2½'` | 16 | `2.00` | **`2.50`** | **Fixed (Quarter Eagle ½)** |
| 34 | `coin` | `'Gold dollar'` | 3 | `1.00` | `1.00` | Unchanged ✓ |
| 35 | `coin` | `'Half cent'` | 7 | `0.005` | `0.005` | Unchanged ✓ |
| 36 | `coin` | `'Half dime'` | 35 | `0.10` | **`0.05`** | **Fixed (NET-831 #1)** |
| 37 | `coin` | `'Half dollar'` | 431 | `0.50` | `0.50` | Unchanged ✓ |
| 38–42 | `coin` | `"New York World's Fair ... Commemorative Coin"` (5 strings) | 5 | `0.00` | `0.00` | Unchanged (`'—'`) ✓ |
| 43 | `coin` | `'O'` | 4 | `0.00` | `0.00` | Unchanged (`'—'`) ✓ |
| 44 | `coin` | `'Planchet for 1 Cent Coin'` | 1 | `0.01` | `0.01` | Unchanged ✓ |
| 45 | `coin` | `'Quarter'` | 943 | `0.25` | `0.25` | Unchanged ✓ |
| 46 | `coin` | `'Quarter (rolls/bags product)'` | 1 | `0.25` | `0.25` | Unchanged ✓ |
| 47 | `coin` | `'copper'` | 5 | `0.00` | `0.00` | Unchanged (`'—'`) ✓ |
| 48 | `coin` | `'half cent'` | 1 | `0.005` | `0.005` | Unchanged ✓ |
| 49 | `medal` | `null` | 56 | `0.00` | `0.00` | **Medal rule: `'No face value'`** |
| 50 | `note` | `'$1'` | 41 | `1.00` | `1.00` | Unchanged ✓ |
| 51 | `note` | `'$1, $2, $5, $10 (uncut sheet)'` | 1 | `10.00` | `10.00` | Unchanged ✓ |
| 52 | `note` | `'$10'` | 13 | `10.00` | `10.00` | Unchanged ✓ |
| 53 | `note` | `'$100'` | 6 | `100.00` | `100.00` | Unchanged ✓ |
| 54 | `note` | `'$1000'` | 1 | `100.00` | **`1000.00`** | **Fixed (NET-831 #1)** |
| 55 | `note` | `'$2'` | 20 | `2.00` | `2.00` | Unchanged ✓ |
| 56 | `note` | `'$20'` | 13 | `20.00` | `20.00` | Unchanged ✓ |
| 57 | `note` | `'$40'` | 1 | `40.00` | `40.00` | Unchanged ✓ |
| 58 | `note` | `'$5'` | 16 | `5.00` | `5.00` | Unchanged ✓ |
| 59 | `note` | `'$50'` | 6 | `50.00` | `50.00` | Unchanged ✓ |
| 60 | `note` | `'$500'` | 2 | `500.00` | `500.00` | Unchanged ✓ |
| 61 | `note` | `'1 Dollar'` | 7 | `1.00` | `1.00` | Unchanged ✓ |
| 62 | `note` | `'1,000 Dollars'` | 6 | `1.00` | **`1000.00`** | **Fixed (NET-831 #1)** |
| 63 | `note` | `'10 Dollars'` | 11 | `1.00` | **`10.00`** | **Fixed (NET-831 #1)** |
| 64 | `note` | `'10,000 Dollars'` | 2 | `1.00` | **`10000.00`** | **Fixed (NET-831 #1)** |
| 65 | `note` | `'100 Dollars'` | 7 | `1.00` | **`100.00`** | **Fixed (NET-831 #1)** |
| 66 | `note` | `'2 Dollars'` | 3 | `1.00` | **`2.00`** | **Fixed (NET-831 #1)** |
| 67 | `note` | `'20 Dollars'` | 8 | `1.00` | **`20.00`** | **Fixed (NET-831 #1)** |
| 68 | `note` | `'3¢–50¢'` | 1 | `3.00` | **`0.00`** | **Fixed (range guard)** |
| 69 | `note` | `'5 Dollars'` | 7 | `1.00` | **`5.00`** | **Fixed (NET-831 #1)** |
| 70 | `note` | `'50 Dollars'` | 6 | `1.00` | **`50.00`** | **Fixed (NET-831 #1)** |
| 71 | `note` | `'500 Dollars'` | 3 | `1.00` | **`500.00`** | **Fixed (NET-831 #1)** |

---

### B. Explicit Medal Display & Contrast Specification

1. **Medal Display (56 Entries, `item['type'] == 'medal'`):**
   - Every medal in `catalog_public_v1.json` (56/56) has `"denomination": null` and represents non-denominated historical/commemorative exonumia.
   - `_CatalogCard` checks `final isMedal = item['type'] == 'medal';` before calling `MeltValueService.parseFaceValue`.
   - `_CatalogCard` **never** falls back to `item['name']` for face-value parsing (preventing years or numbers in medal titles from being parsed as USD amounts).
   - When `isMedal == true`, `_CatalogCard` renders a single muted metadata label `'No face value'` (`TextStyle(fontSize: 13, color: Color(0xFF6B6B6B))`) and **does not** render `'Face Value N/A'` or the `'Value pending AI estimate'` chip.
2. **Non-Medal Unknown Denomination Display (18 Entries where `faceVal == 0.0`):**
   - For the 18 non-medal entries whose `denomination` string does not represent a single USD denomination (`'CC'` ×1, `'D'` ×1, `'O'` ×4, `'copper'` ×5, World's Fair commemorative coins ×5, `'3.6 Candareens'` ×1, `'3¢–50¢'` ×1), `parseFaceValue` returns `0.0`, and `_CatalogCard` displays `'—'` (em-dash, never `'$0.00'`) alongside the `'Value pending AI estimate'` amber chip.
3. **Amber Chip Contrast Ratio (Re-Measured WCAG 2.1):**
   - Foreground text `#856404` ($R=133, G=100, B=4$): relative luminance $L_2 = 0.141097$.
   - Background fill `#FFF3CD` ($R=255, G=243, B=205$): relative luminance $L_1 = 0.897690$.
   - Contrast ratio: $\frac{0.897690 + 0.05}{0.141097 + 0.05} = \frac{0.947690}{0.191097} = 4.9592:1 \approx \mathbf{4.96:1}$ (passes WCAG 2.1 AA minimum of `4.5:1` for normal text; replaces the erroneous `5.1:1` claim from `v1.11`).

---

### C. Pinned Before / Planned After Diff for `numista_mobile/lib/services/melt_value_service.dart:53-99`

#### Pinned Code (`b0b05808` / `4d17ca5e` / `origin/dev` `afbbbd45` / `p7-v8.9` `5fbff9af`, blob `b210bff669d34f8a16bb63c79ea1e5b6a78db653`, lines 53–99):
```dart
53:   static double parseFaceValue(String rawDenom, {int qty = 1}) {
54:     final count = qty > 0 ? qty : 1;
55:     if (rawDenom.trim().isEmpty) return 0.0;
56: 
57:     // Normalization pipeline: lowercase, collapse whitespace, strip parenthetical & ellipses
58:     String s = rawDenom.toLowerCase().trim();
59:     s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
60:     s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
61: 
62:     double value = 0.0;
63: 
64:     // 1. High Gold & Commemoratives
65:     if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
66:     else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
67:     else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
68:     else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
69:     else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
70:     else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
71:     else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
72:     else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
73:     else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
74:     else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }
75: 
76:     // 2. Sub-Dollar & Standard Silver/Base Denominations
77:     else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
78:     else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
79:     else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
80:     else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
81:     else if (s.contains('half dime')) { value = 0.05; }
82:     else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
83:     else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
84:     else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
85:     else if (s.contains('half cent')) { value = 0.005; }
86:     else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
87:     else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
88: 
89:     // 3. Fallback: plain numeric parse
90:     else {
91:       final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
92:       if (match != null) {
93:         final parsed = double.tryParse(match.group(0)!) ?? 0.0;
94:         value = parsed <= 1000.0 ? parsed : 0.0;
95:       }
96:     }
97: 
98:     return value * count;
99:   }
```

#### Planned Unified Diff (`numista_mobile/lib/services/melt_value_service.dart:53-99`):
```diff
--- a/numista_mobile/lib/services/melt_value_service.dart
+++ b/numista_mobile/lib/services/melt_value_service.dart
@@ -57,41 +57,67 @@ class MeltValueService {
     // Normalization pipeline: lowercase, collapse whitespace, strip parenthetical & ellipses
     String s = rawDenom.toLowerCase().trim();
     s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
     s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
+    s = s.replaceAll('\u00bd', ' 1/2');
+    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();
 
     double value = 0.0;
 
-    // 1. High Gold & Commemoratives
-    if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
+    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
+    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
+    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
+    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
+    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);
+
+    if (fracDollarMatch != null) {
+      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
+    } else if (leadDollarMatch != null) {
+      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
+    } else if (leadCentMatch != null && !RegExp(r'[\u2013\-/]').hasMatch(s)) {
+      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
+    } else if (leadSymDollarMatch != null && !RegExp(r'[/,]').hasMatch(s)) {
+      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
+    }
+
+    // 1. High Gold, Notes & Commemoratives
+    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
+    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
+    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
     else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
     else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
+    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
     else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
     else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
     else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
     else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
+    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
     else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
-    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
+    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
     else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }
 
-    // 2. Sub-Dollar & Standard Silver/Base Denominations
-    else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
-    else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
-    else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
-    else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
-    else if (s.contains('half dime')) { value = 0.05; }
-    else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
-    else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
-    else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
-    else if (s.contains('half cent')) { value = 0.005; }
+    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
+    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
+    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
+    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
+    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
+    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
+    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
+    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
+    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
+    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
     else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
     else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
 
-    // 3. Fallback: plain numeric parse
-    else {
+    // 3. Fallback: plain numeric parse (only when not a range or non-USD trade unit)
+    else if (!s.contains('candareen') && !RegExp(r'[\u2013\-]').hasMatch(s)) {
       final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
       if (match != null) {
         final parsed = double.tryParse(match.group(0)!) ?? 0.0;
         value = parsed <= 1000.0 ? parsed : 0.0;
       }
     }
```

---

## 4. Must-Fix #2: Minimal Diff to `_CatalogCard` (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`)

### A. Pinned Code Verification (`b0b05808` / `origin/dev` `afbbbd45`, blob `3a0d310936a1715034e65c7384476c19e2030ad7`)

#### Pinned Lines 1–5 (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:1-5`):
```dart
1: import 'dart:convert';
2: import 'package:flutter/material.dart';
3: import 'package:flutter/services.dart';
4: import 'package:url_launcher/url_launcher.dart';
5: 
```

#### Pinned Lines 1069–1154 (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:1069-1154`):
```dart
1069: class _CatalogCard extends StatelessWidget {
1070:   final Map<String, dynamic> item;
1071:   final VoidCallback onTap;
1072: 
1073:   const _CatalogCard({
1074:     required this.item,
1075:     required this.onTap,
1076:   });
1077: 
1078:   @override
1079:   Widget build(BuildContext context) {
1080:     final primaryImg = item['primary_image'] as Map?;
1081:     final typeImg = item['type_image'] as Map?;
1082:     final imgMap = primaryImg ?? typeImg;
1083:     final isTypeImage = primaryImg == null && typeImg != null;
1084: 
1085:     final badge = item['status_badge'] as String?;
1086:     final year = item['year']?.toString() ?? 'Undated';
1087:     final denom = item['denomination']?.toString() ?? '';
1088: 
1089:     return InkWell(
1090:       onTap: onTap,
1091:       borderRadius: BorderRadius.circular(12),
1092:       child: Container(
1093:         padding: const EdgeInsets.all(16),
1094:         decoration: BoxDecoration(
1095:           color: Colors.white,
1096:           border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
1097:           borderRadius: BorderRadius.circular(12),
1098:         ),
1099:         child: Column(
1100:           crossAxisAlignment: CrossAxisAlignment.start,
1101:           children: [
1102:             // Image
1103:             Expanded(
1104:               child: Center(
1105:                 child: imgMap != null && imgMap['url'] != null
1106:                     ? Image.network(
1107:                         imgMap['url'] as String,
1108:                         fit: BoxFit.contain,
1109:                         errorBuilder: (c, e, s) => _buildPlaceholder(),
1110:                       )
1111:                     : _buildPlaceholder(),
1112:               ),
1113:             ),
1114:             const SizedBox(height: 10),
1115: 
1116:             // Badge
1117:             if (badge != null) ...[
1118:               _CatalogBadge(badgeText: badge),
1119:               const SizedBox(height: 8),
1120:             ],
1121: 
1122:             // Title
1123:             Text(
1124:               item['name'] as String? ?? 'Coin',
1125:               maxLines: 2,
1126:               overflow: TextOverflow.ellipsis,
1127:               style: const TextStyle(
1128:                 fontSize: 18,
1129:                 fontWeight: FontWeight.bold,
1130:                 color: Color(0xFF0B2545),
1131:                 height: 1.2,
1132:               ),
1133:             ),
1134:             const SizedBox(height: 6),
1135: 
1136:             // Metadata line
1137:             Text(
1138:               [year, denom].where((s) => s.isNotEmpty).join(' · '),
1139:               style: const TextStyle(fontSize: 15, color: Color(0xFF475569)),
1140:             ),
1141: 
1142:             if (isTypeImage)
1143:               const Padding(
1144:                 padding: EdgeInsets.only(top: 4),
1145:                 child: Text(
1146:                   'type photo (date may differ)',
1147:                   style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
1148:                 ),
1149:               ),
1150:           ],
1151:         ),
1152:       ),
1153:     );
1154:   }
```

### B. Planned Minimal Unified Diff (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`)

This minimal diff adds the `melt_value_service.dart` import at line 5, preserves lines `1122–1149` (existing title styling, metadata line styling, and the `1142–1149` `'type photo (date may differ)'` block) byte-for-byte, and appends the face-value / medal display row after line 1149:

```diff
--- a/numista_mobile/lib/screens/catalog/catalog_browse_screen.dart
+++ b/numista_mobile/lib/screens/catalog/catalog_browse_screen.dart
@@ -1,4 +1,5 @@
 import 'dart:convert';
 import 'package:flutter/material.dart';
 import 'package:flutter/services.dart';
 import 'package:url_launcher/url_launcher.dart';
+import '../../services/melt_value_service.dart';
@@ -1085,4 +1086,9 @@ class _CatalogCard extends StatelessWidget {
     final badge = item['status_badge'] as String?;
     final year = item['year']?.toString() ?? 'Undated';
     final denom = item['denomination']?.toString() ?? '';
+    final isMedal = item['type'] == 'medal';
+    final faceVal = isMedal ? 0.0 : MeltValueService.parseFaceValue(denom);
+    final faceValText = faceVal > 0
+        ? (faceVal == 0.005 ? r'$0.005' : '\$${faceVal.toStringAsFixed(2)}')
+        : '—';
 
     return InkWell(
@@ -1146,5 +1152,44 @@ class _CatalogCard extends StatelessWidget {
                   'type photo (date may differ)',
                   style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
                 ),
               ),
+
+            const SizedBox(height: 6),
+            if (isMedal)
+              const Text(
+                'No face value',
+                style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
+              )
+            else
+              Row(
+                children: [
+                  Text(
+                    faceValText,
+                    style: const TextStyle(
+                      fontSize: 15,
+                      fontWeight: FontWeight.bold,
+                      color: Color(0xFF1F5FAD),
+                    ),
+                  ),
+                  const SizedBox(width: 8),
+                  Flexible(
+                    child: Container(
+                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
+                      decoration: BoxDecoration(
+                        color: const Color(0xFFFFF3CD),
+                        border: Border.all(color: const Color(0xFFFFEEBA)),
+                        borderRadius: BorderRadius.circular(4),
+                      ),
+                      child: const Text(
+                        'Value pending AI estimate',
+                        overflow: TextOverflow.ellipsis,
+                        style: TextStyle(
+                          fontSize: 11,
+                          fontWeight: FontWeight.w600,
+                          color: Color(0xFF856404),
+                        ),
+                      ),
+                    ),
+                  ),
+                ],
+              ),
           ],
         ),
```

---

## 5. Planned Tests (Not Run) in New Test File (`numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`)

- **Existing Test Preserved:** `numista_mobile/test/catalog_browse_test.dart` (91 lines, blob `3df197ca2cc0424b5dac7f1ad491a5ca9bb669af`, testing `UsNumismaticsCatalogScreen`) is kept intact without modification.
- **Package Name Verified:** `numista_mobile/pubspec.yaml:1` declares `name: numista_ai`. All imports in the new test file use `package:numista_ai/...`.
- **New Test File Path:** `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`

### Planned Contents of `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`

```dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/services/melt_value_service.dart';

void main() {
  group('NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1)', () {
    test('parses previously mis-valued catalog denomination strings and preserves existing tokens', () {
      const expectedByDenom = <String, double>{
        // Required CoS / Starter Prompt cases
        'Half dime': 0.05,
        '3 cents': 0.03,
        '3 Cents': 0.03,
        '10 Dollars': 10.00,
        '2 1/2 Dollars': 2.50,
        '1,000 Dollars': 1000.00,
        '10,000 Dollars': 10000.00,
        r'$1000': 1000.00,
        'Dime': 0.10,
        // All remaining N Dollars & catalog variants
        '1 Dollar': 1.00,
        '2 Dollars': 2.00,
        '5 Dollars': 5.00,
        '20 Dollars': 20.00,
        '50 Dollars': 50.00,
        '100 Dollars': 100.00,
        '500 Dollars': 500.00,
        'G\$2\u00bd': 2.50,
        r'$40': 40.00,
        r'$4 Stella': 4.00,
        'Half cent': 0.005,
        'half cent': 0.005,
        '1 Cent': 0.01,
        '1 cent': 0.01,
        '5 Cents': 0.05,
        '5 cents': 0.05,
        '10 Cents': 0.10,
        'Quarter': 0.25,
        '50 Cents': 0.50,
        'Half dollar': 0.50,
        'Dollar': 1.00,
        'Gold dollar': 1.00,
        r'1$': 1.00,
        // Canonical multi-word names
        'Five Cents': 0.05,
        'Ten Cents': 0.10,
        'Fifty Cents': 0.50,
        'Three Cent Nickel': 0.03,
        // Non-single-USD / exonumia guards
        '3\u00a2\u201350\u00a2': 0.0,
        '3.6 Candareens': 0.0,
        '': 0.0,
      };

      expectedByDenom.forEach((raw, expected) {
        expect(
          MeltValueService.parseFaceValue(raw),
          closeTo(expected, 1e-6),
          reason: 'Failed for denomination "$raw"',
        );
      });
    });

    test('full catalog_public_v1.json check: 0 of the re-counted mis-parses remain across 3,202 entries', () {
      final file = File('assets/catalog/catalog_public_v1.json');
      final List<dynamic> rawList = json.decode(file.readAsStringSync()) as List<dynamic>;
      expect(rawList.length, 3202);

      const expectedCatalogDenomValues = <String, double>{
        r'$1 (1 oz silver)': 1.00,
        r'$10 eagle': 10.00,
        r'$100/$50/$25/$10 platinum': 100.00,
        r'$2.50 quarter eagle': 2.50,
        r'$20 double eagle': 20.00,
        r'$25 (1 oz palladium)': 25.00,
        r'$3': 3.00,
        r'$4 Stella': 4.00,
        r'$5 half eagle': 5.00,
        r'$50': 50.00,
        r'$50 (1 oz gold)': 50.00,
        r'$50/$25/$10/$5 gold': 50.00,
        '1 Cent': 0.01,
        '1 Dollar': 1.00,
        '1 cent': 0.01,
        r'1$': 1.00,
        '10 Cents': 0.10,
        '2 1/2 Dollars': 2.50,
        '20 Dollars': 20.00,
        '3 Cents': 0.03,
        '3 cents': 0.03,
        '3.6 Candareens': 0.00,
        '5 Cents': 0.05,
        '5 Dollars': 5.00,
        '5 cents': 0.05,
        '50 Cents': 0.50,
        '50 cent coin planchet': 0.50,
        'CC': 0.00,
        'D': 0.00,
        'Dime': 0.10,
        'Dollar': 1.00,
        'Dollar (two-coin set)': 1.00,
        'G\$2\u00bd': 2.50,
        'Gold dollar': 1.00,
        'Half cent': 0.005,
        'Half dime': 0.05,
        'Half dollar': 0.50,
        "New York World's Fair Billy Rose's Aquacade Commemorative Coin": 0.00,
        "New York World's Fair Frank Buck's Jungleland Commemorative Coin": 0.00,
        "New York World's Fair George Washington Commemorative Coin": 0.00,
        "New York World's Fair George Washington Inauguration Commemorative Coin": 0.00,
        "New York World's Fair Stack's Coin Dealers Commemorative Coin": 0.00,
        'O': 0.00,
        'Planchet for 1 Cent Coin': 0.01,
        'Quarter': 0.25,
        'Quarter (rolls/bags product)': 0.25,
        'copper': 0.00,
        'half cent': 0.005,
        r'$1': 1.00,
        r'$1, $2, $5, $10 (uncut sheet)': 10.00,
        r'$10': 10.00,
        r'$100': 100.00,
        r'$1000': 1000.00,
        r'$2': 2.00,
        r'$20': 20.00,
        r'$40': 40.00,
        r'$5': 5.00,
        r'$50': 50.00,
        r'$500': 500.00,
        '1,000 Dollars': 1000.00,
        '10 Dollars': 10.00,
        '10,000 Dollars': 10000.00,
        '100 Dollars': 100.00,
        '2 Dollars': 2.00,
        '3\u00a2\u201350\u00a2': 0.00,
        '50 Dollars': 50.00,
        '500 Dollars': 500.00,
      };

      int misParses = 0;
      int medalCount = 0;
      for (final rawItem in rawList) {
        final item = Map<String, dynamic>.from(rawItem as Map);
        final type = item['type'] as String?;
        final denom = item['denomination'] as String?;
        if (type == 'medal') {
          medalCount++;
          expect(denom, isNull, reason: 'Medals have no face value denomination');
          continue;
        }
        expect(denom, isNotNull);
        final expected = expectedCatalogDenomValues[denom!];
        expect(expected, isNotNull, reason: 'Unmapped catalog denomination: $denom');
        final actual = MeltValueService.parseFaceValue(denom);
        if ((actual - expected!).abs() > 1e-6) {
          misParses++;
        }
      }
      expect(medalCount, 56);
      expect(misParses, 0);
    });
  });

  group('NET-816 Chunk 1 — _CatalogCard Widget Tests (#2)', () {
    testWidgets('shows "type photo (date may differ)" when isTypeImage is true and renders parsed face value + pending chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 960));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      // 1842 Liberty Seated dollar in catalog_public_v1.json has primary_image: null, type_image != null, denomination: "Dollar"
      await tester.pumpWidget(
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: '1842 Liberty Seated dollar'),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('1842 Liberty Seated dollar'), findsOneWidget);
      expect(find.text('1842 \u00b7 Dollar'), findsOneWidget);
      expect(find.text('type photo (date may differ)'), findsOneWidget);
      expect(find.text(r'$1.00'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    testWidgets('medal cards display "No face value" and omit "Value pending AI estimate"', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 960));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: 'Libertas Americana medal'),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Medals (56)'));
      await tester.pumpAndSettle();

      expect(find.textContaining('Libertas Americana medal'), findsOneWidget);
      expect(find.text('No face value'), findsOneWidget);
      expect(find.text('Face Value N/A'), findsNothing);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });
  });
}
```

---

## 6. History-Preserving Rollback & Docs Sync Procedure

1. **Future Code Landing & Rollback on `p7-v8.9` Only (After GB CoS ≥95, SAG ≥95, and Eric's Typed YES):**
   - Future code implementation for Chunk 1 lands as its own atomic commit on `p7-v8.9` (`p7-gate`) only.
   - **History-Preserving Rollback:** If rollback is ever required, execute:
     ```bash
     git revert --no-edit <chunk1_code_commit_sha>
     git push origin p7-v8.9
     ```
   - Never use `git reset --hard`, `git checkout <old_sha>`, or `git push --force`.
2. **Docs Sync to `origin/dev` via Temporary Worktree + `git checkout <sha> -- <paths>` (No `cherry-pick -- <paths>`, No Force):**
   - Because `git cherry-pick` does not accept pathspecs when cherry-picking across divergent trees, documentation commits are synced from `p7-v8.9` onto `origin/dev` using a temporary worktree and `git checkout <p7_doc_commit_sha> -- <doc_paths>`:
     ```powershell
     git fetch origin dev
     git worktree add ..\temp-dev-docs origin/dev
     Push-Location ..\temp-dev-docs
     git checkout -B dev origin/dev
     git checkout <p7_doc_commit_sha> -- "docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.0.md" "BETA TEST/Grok Bot/8 OCT 26/BATONS/BATON_NET-816_GROKCOS_REVIEW_CATALOG_CHUNK1_20261107-1516.md"
     git add "docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.0.md" "BETA TEST/Grok Bot/8 OCT 26/BATONS/BATON_NET-816_GROKCOS_REVIEW_CATALOG_CHUNK1_20261107-1516.md"
     git commit -m "docs(net-816): deliver Catalog Chunk 1 failfix plan v2.0 and review baton (attempt 1/4)"
     git pull --rebase origin dev
     git push origin dev
     Pop-Location
     git worktree remove ..\temp-dev-docs
     ```
