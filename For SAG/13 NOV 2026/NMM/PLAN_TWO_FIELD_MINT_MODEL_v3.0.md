# PLAN: Two-Field Mint Model (`mint` + `mint_mark`) — Follow-on to NET-810

- **Version:** v3.0 *(execution-ready: adds §11 Verbatim Live Code Pastes, §12 Canonical 15-Case Fixture Table, expanded Rule 10 Python predicates, and concrete Phase 7 GCP Cloud Logging telemetry query)*
- **Date:** 2026-11-13
- **Status:** **PLAN ONLY — FOR REVIEW** (Zero code changes, zero Firestore writes, zero deploys)
- **Target Review Folder:** `For SAG/13 NOV 2026/NMM/`
- **Baseline Branch:** `dev` (strictly no `main` touches; `origin/main` locked)

---

## Changelog (v2.0 → v3.0)
1. **Verbatim Live Code Pastes (§11):** Added exact `file:line-line` verbatim code blocks of all current implementations to be modified across Dart (`CoinModel`, `SlotResolver`, `coin_detail_screen.dart`, `pcgs_import_service.dart`, `add_coins_hub.dart`, `program_manager_screen.dart`, `inventory_gallery.dart`, `backup_export_service.dart`) and Python (`checklist_parser.py`, `duplicate_check.py`, `mint_nomenclature_service.py`, `import_routes.py`, `main.py`).
2. **Concrete Canonical Fixture Table (§12):** Added 15 deterministic test fixtures covering Rules #1–#11, historical Dahlonega/Charlotte vs. Denver, War Nickel 1942–1945, pre-1980 Philadelphia NMM, 1950–1964 Proof NMM, 2026 West Point Enhanced Unc NMM (`26XE`/`26XH`), 2026 Philadelphia Reverse Proof NMM (`26XF`/`26XL`), dirty legacy placeholders (`"None"`, `"NMM"`, `"Philadelphia"`), non-US coin with blank mint mark, and unmigrated document fallback.
3. **Expanded Rule 10 Python Predicates (§2.3):** Replaced abstract predicates `not is_war_nickel_1942_1945_p` and `strike_type_or_variety_is_philly_nmm` with exact Python string/integer expressions.
4. **Concrete Phase 7 Telemetry Query (§8):** Specified exact GCP Cloud Logging / Logs Explorer filter query and log-based metric for verifying the 14-day zero-write window on `syncLegacyMintMarkOnUpdate`.

---

## 1. Executive Summary & Architectural Goal

In NET-810 (`docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.7.md`, §5.2 / §7.1), `MintProductLookupService.lookupForCoin` had to special-case blank `CoinModel.mintMark == ''` → `'Philadelphia'` (and gate on `mint_mark_on_coin`) because `CoinModel` and the Firestore coin schema conflated **mint facility** and **on-coin mint mark** into a single `'Mint Mark'` / `mintMark` field. Similarly, `SlotResolver`, collection grouping, and backend duplicate/checklist logic contain ad-hoc `mintMark.isEmpty || mintMark == 'NONE' || mintMark == 'PHILADELPHIA'` branches.

This plan introduces the **two-field mint model** (snake_case golden schema):
1. **`mint`** *(facility string)*: Official mint facility name, e.g. `"Philadelphia"`, `"Denver"`, `"San Francisco"`, `"West Point"`, `"New Orleans"`, `"Carson City"`, `"Dahlonega"`, `"Charlotte"`, or `""` when unknown / non-US / unentered.
2. **`mint_mark`** *(on-coin mark)*: Exact mark stamped on the coin, e.g. `"P"`, `"D"`, `"S"`, `"W"`, `"O"`, `"CC"`, `"C"`, or `""` for No Mint Mark (NMM).

**Core Invariants:**
- **Never invent a mint mark:** A 1921 Morgan Dollar, 1965–1979 Lincoln Cent, 1936–1964 Proof, or 2026 unmarked Morgan/Peace Reverse Proof has `mint = "Philadelphia"` and `mint_mark = ""` (never `mint_mark = "P"`).
- **CoinModel / Firestore collection documents remain the source of truth:** No client-side silent overrides of persisted coin data.
- **Zero PII** in migration logs, dry-run reports, or test fixtures.
- **Standing Locks:** No `main` branch merges/pushes; no live Firestore writes without Founder Eric's explicit typed `YES`.

---

## 2. Deliverable 1: Schema & Model Changes

### 2.1 Golden Firestore Schema (snake_case + transitional compatibility)
Each coin document in `users/{userId}/coins/{coinId}` will carry:
- `mint`: `String` (e.g. `"Philadelphia"`, `"Denver"`, `"San Francisco"`, `"West Point"`, `""`)
- `mint_mark`: `String` (e.g. `"P"`, `"D"`, `"S"`, `"W"`, `""`)
- `'Mint Mark'`: `String` — transitional dual-write kept in sync with `mint_mark` during Phases 1–6, then removed in **Phase 7 (Technical Debt Sunset)**.

### 2.2 `CoinModel` (`numista_mobile/lib/models/coin_model.dart`)
- **Current state:** `CoinModel` has `final String mintMark;` (line 7) defaulting to `''` (line 84), read in `fromMap` (lines 171–174) via `data['Mint Mark'] ?? data['mintMark'] ?? data['MintMark'] ?? ''`, and written in `toFirestore` (line 251) as `'Mint Mark': mintMark`. (See §11.1 for verbatim lines.)
- **Planned changes:**
  1. Add `final String mint;` to `CoinModel` fields and constructor (`this.mint = ''`).
  2. Update `CoinModel.fromMap` to use `MintHelpers.readMintFacility(data)` and `MintHelpers.readMintMark(data)`, reading `mint` and `mint_mark` first before falling back to `'Mint Mark'`, `'mintMark'`, `'MintMark'`.
  3. Update `CoinModel.toFirestore()` (Phases 1–6) to emit:
     ```dart
     'mint': mint,
     'mint_mark': mintMark,
     'Mint Mark': mintMark, // transitional dual-write; removed in Phase 7
     ```
  4. Update `_splitYearMint(String rawYear, String rawMint)` so combined strings like `"2006D"` extract `mint_mark = "D"` without mutating `mint` silently on read.

### 2.3 Canonical Mint Normalization Table (Deterministic Python Rules)
Evaluated in top-to-bottom order on write, import, and migration.
Pre-computed normalized locals:
```python
is_us = country.strip().lower() in {"usa", "us", "united states", ""}
denom_lower = denomination.strip().lower()
series_lower = series.strip().lower()
series_or_denom_lower = f"{series_lower} {denom_lower}"
strike_lower = strike_type.strip().lower()
variety_lower = variety.strip().lower()
metal_lower = metal_content.strip().lower()
item_no_upper = retailer_item_no.strip().upper()
```

| # | `mint_mark` (normalized) | Exact Deterministic Predicate | Derived `mint` (facility) |
|---|---|---|---|
| 1 | `"P"` | `is_us` | `"Philadelphia"` |
| 2 | `"D"` | `is_us and int_year is not None and 1838 <= int_year <= 1861` | `"Dahlonega"` |
| 3 | `"D"` | `is_us and (int_year is None or int_year >= 1906)` | `"Denver"` |
| 4 | `"C"` | `is_us and int_year is not None and 1838 <= int_year <= 1861` | `"Charlotte"` |
| 5 | `"S"` | `is_us` | `"San Francisco"` |
| 6 | `"W"` | `is_us` | `"West Point"` |
| 7 | `"O"` | `is_us` | `"New Orleans"` |
| 8 | `"CC"` | `is_us` | `"Carson City"` |
| 9 | `""` (blank) | **West Point NMM:** `is_us and (item_no_upper in {"26XE", "26XH"} or (year == "2026" and ("morgan" in series_or_denom_lower or "peace" in series_or_denom_lower) and ("enhanced" in strike_lower or "enhanced" in variety_lower or strike_lower.strip() == "eu" or variety_lower.strip() == "eu")))` | `"West Point"` (`mint_mark` stays `""`) |
| 10 | `""` (blank) | **Philadelphia NMM:** `is_us and not rule_9 and (unique_catalog_match(mint_facility="Philadelphia", mint_mark_on_coin in {False, None, ""}) or (int_year is not None and int_year <= 1979 and not (1942 <= int_year <= 1945 and any(k in series_or_denom_lower for k in ("nickel", "jefferson", "5c", "5 cent")) and ("war" in variety_lower or "silver" in metal_lower or int_year >= 1943))) or (any(tok in strike_lower or tok in variety_lower for tok in ("reverse proof", "congratulations")) or (strike_lower.strip() in {"proof", "pr", "pf"} and (int_year is None or int_year <= 1964 or item_no_upper in {"26XF", "26XL", "26RF"}))))` | `"Philadelphia"` (`mint_mark` stays `""`) |
| 11 | `""` (blank) | Non-US coin (`not is_us`), or US coin with insufficient/ambiguous metadata | `""` (`mint_mark` stays `""`) |

*Sanitization rule for legacy dirty values:* Before evaluating rules 1–11, if `raw_mint_mark.strip().lower()` is in `{"none", "(none)", "null", "n/a", "nmm", "no mint mark", "philadelphia"}`:
- Set `mint_mark = ""`.
- If raw value was `"nmm"`, `"no mint mark"`, or `"philadelphia"` (and `is_us` is `True`), pass `raw_mint = "Philadelphia"` so `mint` resolves to `"Philadelphia"` even if series/year is sparse.

---

## 3. Deliverable 2: Dual-Key Reader Helpers & Legacy Overwrite Protection

### 3.1 Dart Helper (`numista_mobile/lib/utils/mint_helpers.dart` — new utility)
All Dart readers will call centralized, null-safe helpers:

```dart
class MintHelpers {
  /// Dual-key reader for on-coin mint mark.
  /// Priority: `mint_mark` -> `'Mint Mark'` -> `mintMark` -> `MintMark`.
  /// Sanitizes placeholder strings ("none", "(none)", "null", "n/a", "nmm", "no mint mark", "philadelphia") to "".
  static String readMintMark(Map<String, dynamic> data) { ... }

  /// Dual-key reader for mint facility.
  /// Priority: `mint` -> `mint_facility`. Returns "" if absent.
  static String readMintFacility(Map<String, dynamic> data) { ... }

  /// Display formatter:
  /// - compact=true (badges/chips/table): "NMM" when mint=="Philadelphia" && mint_mark=="", else mint_mark
  /// - compact=false (detail view): "No Mint Mark" when mint=="Philadelphia" && mint_mark==""
  static String formatMintMarkForDisplay(String mint, String mintMark, {bool compact = false}) { ... }
  static String formatMintFacilityAndMark(String mint, String mintMark) { ... }
}
```

### 3.2 Python Helper (`numista_backend/services/mint_helpers.py` — new module)
Mirrors the exact priority order and §2.3 normalization table:

```python
def read_mint_mark(doc: dict) -> str: ...
def read_mint_facility(doc: dict) -> str: ...

def is_west_point_nmm(
    year: str = "",
    series: str = "",
    denomination: str = "",
    variety: str = "",
    strike_type: str = "",
    retailer_item_no: str = "",
    country: str = "United States",
) -> bool:
    """Exact programmatic implementation of Table §2.3 Rule 9."""

def resolve_two_field_mint(
    raw_mint_mark: str = "",
    raw_mint: str = "",
    year: str = "",
    series: str = "",
    denomination: str = "",
    country: str = "United States",
    variety: str = "",
    strike_type: str = "",
    metal_content: str = "",
    retailer_item_no: str = "",
) -> tuple[str, str, int]:
    """Returns (mint_facility, mint_mark, rule_id) per Table §2.3 (rule_id in 1..11)."""
```

### 3.3 Legacy Overwrite Hazard Mitigation (Firestore Write-Sync)
**Hazard:** Mobile clients (`coin_detail_screen.dart:4546, 4600`) write directly to Firestore `users/{userId}/coins/{coinId}`. If an older app version updates `'Mint Mark'` on a document that *already* has `mint_mark` (from migration or a newer client), `mint_mark` would become stale and shadow the newer `'Mint Mark'` because `readMintMark` prefers `mint_mark`.

**Mitigation (Two-Layer Defense — Sunset in Phase 7):**
1. **Firestore Cloud Function Trigger (`syncLegacyMintMarkOnUpdate` on `users/{userId}/coins/{coinId}`):**
   - Fires on `onDocumentUpdated`.
   - Compares `before` and `after` snapshots:
     - **Case A (Legacy client write):** `after['Mint Mark'] != before['Mint Mark']` **AND** `after['mint_mark'] == before['mint_mark']` (meaning `'Mint Mark'` changed without touching `mint_mark`).
       - Action: Recompute `(new_mint, new_mm) = resolve_two_field_mint(raw_mint_mark=after['Mint Mark'], ...)` and perform a single idempotent `after.ref.update({'mint_mark': new_mm, 'mint': new_mint})`, emitting a structured JSON log `{"event": "legacy_mint_mark_sync_count", "rule_hit": <rule_id>}` at `INFO` severity (zero PII).
     - **Case B (New client write):** `mint_mark` changed alongside `'Mint Mark'`, or both are equal → **no-op** (prevents infinite trigger loops).
2. **Backend Route Interceptor (`main.py` / `import_routes.py`):**
   - Any backend endpoint that updates a coin document must write `mint`, `mint_mark`, and `'Mint Mark'` together via `resolve_two_field_mint()`.
3. **Rollout Order:** Deploy the Cloud Function *before* running Phase 5 migration so any legacy client edits during or after migration are immediately synchronized.

---

## 4. Deliverable 3: Write & Import Path Updates

Every write and import path must populate **both** `mint` and `mint_mark` at ingestion time:
1. **Manual Entry & Edit** (`numista_mobile/lib/screens/add_coins_hub.dart`, `coin_detail_screen.dart` `_saveEdits`):
   - Add facility selector/auto-fill alongside Mint Mark input; if user leaves Mint Mark blank for a US Philadelphia NMM year/series, set `mint = "Philadelphia"`, `mint_mark = ""`.
2. **CSV Import** (`numista_mobile/lib/screens/add_coins_hub.dart` CSV wizard lines 6204–6220, `numista_backend/main.py` Golden Schema mapping):
   - Accept optional `Mint` / `Mint Facility` column in addition to `Mint Mark`. Run `resolve_two_field_mint` per row.
3. **PCGS Import** (`numista_mobile/lib/services/pcgs_import_service.dart` `mapToFirestoreSchema` lines 225–260):
   - Read `pcgsData['MintMark']` → `mint_mark` (leave blank if blank), derive `mint` via `resolveTwoFieldMint` using `year`, `seriesName`, `denomination`, `country`.
4. **Checklist / Program Batch Add** (`numista_mobile/lib/screens/program_manager_screen.dart` lines 2113–2133, `numista_backend/main.py` lines 8913–8940, `numista_backend/services/checklist_parser.py` lines 310–370):
   - Stop defaulting blank checklist varieties to `mint_mark = "P"` in `checklist_parser.py:312`! Set `mint = "Philadelphia"`, `mint_mark = ""` for NMM slots, and `mint = "West Point"`, `mint_mark = ""` for `EU` slots.
5. **Backend Ingestion & AI Identify** (`numista_backend/routes/import_routes.py`, `numista_backend/services/mint_nomenclature_service.py`, `numista_backend/main.py`):
   - Update `resolve_coin_catalog_metadata` to return both `mint` and `mint_mark`, and write all three keys (`mint`, `mint_mark`, `'Mint Mark'`) to Firestore during Phases 1–6.

---

## 5. Deliverable 4: Migration Script (Dry-Run & Rollback Capable)

**Target Path:** `numista_backend/scripts/migrate_two_field_mint.py`

### 5.1 Behavior & Safety Controls
- **Default mode is `--dry-run`** (zero Firestore writes). Live writes require explicit `--execute --confirm-token=YES` AND Founder Eric's typed `YES` prior to invocation.
- **Idempotent:** Skips documents that already have both `mint` and `mint_mark` keys present unless `--force-recheck` is passed.
- **Zero PII:** Logs only anonymized counters, document IDs (never user emails, names, notes, costs, or storage locations — hash or omit user segment in console output), and aggregate rule-hit breakdowns.
- **Scope:** Queries Firestore `db.collection_group("coins")` (covering `users/{userId}/coins/{coinId}`), optionally scoped by `--limit N` for canary verification.

### 5.2 Forward Migration Algorithm (`--dry-run` / `--execute`)
1. Read `raw_mm = read_mint_mark(doc)` and `raw_mint = read_mint_facility(doc)`.
2. Read `year`, `program_series`, `denomination`, `country`, `variety`, `strike_type`, `metal_content`, `retailer_item_no`.
3. Compute `(new_mint, new_mm) = resolve_two_field_mint(...)` per Table §2.3.
4. **Dry-Run Report Output:**
   - Total documents scanned
   - Already migrated (skipped)
   - Would update (broken down by rule #1–#11: explicit mark → facility, Philly NMM, West Point NMM, dirty `mint_mark` sanitized, ambiguous/non-US left `mint = ""`)
   - Sample anonymized before/after pairs (up to 10 per category, zero PII).
5. **Batching (`--execute`):** Writes via Firestore `WriteBatch` (max 400 ops/batch) after appending each pre-mutation record `{doc_path, had_mint, prev_mint, had_mint_mark, prev_mint_mark, prev_legacy_mint_mark}` to `scratch/mint_migration_backup_<timestamp>.jsonl` (gitignored).

### 5.3 Rollback Mode (`--rollback`)
- **CLI Arguments:** `python migrate_two_field_mint.py --rollback --backup-file=<path> --confirm-token=YES` (dry-run if `--confirm-token=YES` is omitted).
- **File-Reading Loop & Restoration Logic:**
  1. Validate `--backup-file` exists and is readable JSONL.
  2. Stream lines from the JSONL file; for each record:
     - Resolve `doc_ref = db.document(record["doc_path"])`.
     - Build `restore_payload`:
       - If `had_mint` is `True`, set `'mint': record['prev_mint']`; else set `'mint': firestore.DELETE_FIELD`.
       - If `had_mint_mark` is `True`, set `'mint_mark': record['prev_mint_mark']`; else set `'mint_mark': firestore.DELETE_FIELD`.
       - Restore `'Mint Mark': record['prev_legacy_mint_mark']` if present.
     - Queue `batch.update(doc_ref, restore_payload)`.
  3. Commit `WriteBatch` every 400 operations and flush remainder at EOF.
  4. Print summary: total records read, restored count, and any missing/failed doc paths.

---

## 6. Deliverable 5: List of Files Needing Reader / Logic Updates

### 6.1 Flutter / Dart (`numista_mobile/lib/`)
| File | Current Usage | Planned Update |
|---|---|---|
| `models/coin_model.dart` | Single `mintMark` field; `fromMap` / `toFirestore` (lines 7, 84, 171–174, 251) | Add `mint` field; dual-key readers in `fromMap`; write `mint` + `mint_mark` (+ `'Mint Mark'` until Phase 7) in `toFirestore` |
| `utils/mint_helpers.dart` *(new)* | N/A | Centralized `readMintMark`, `readMintFacility`, `formatMintMarkForDisplay`, `formatMintFacilityAndMark` |
| `utils/slot_resolver.dart` | `_mintMark()` + 15+ `mintMark.isEmpty \|\| mintMark == 'NONE'` branches (lines 198, 742–844) | Read both `mint` and `mint_mark`; match Philadelphia NMM slots via `mint == 'Philadelphia' && mintMark.isEmpty` |
| `services/mint_product_lookup_service.dart` *(NET-810)* | Blank `mintMark` → `'Philadelphia'` heuristic (§5.2 / §7.1) | **Phase 6:** Remove blank→Philly heuristic; join directly on `coin.mint` (`mint_facility`) |
| `screens/coin_detail_screen.dart` | Displays `coin.mintMark` only (lines 368, 1540); edits `'Mint Mark'` (lines 434, 477–483) | Display facility + NMM/mark (see §7); edit both `mint` and `mint_mark` |
| `screens/my_collection_screen.dart` | `_F.mintMark`, `_rowField(m, 'mint_mark', _F.mintMark)`, composite dedup key (lines 52, 578, 691, 879, 1038, 2999, 3243, 3431, 4167, 4439) | Use `MintHelpers.readMintMark` / `readMintFacility`; show facility & NMM in table/cards |
| `inventory_gallery.dart` | `data['Mint Mark']` (lines 143–172) | Use `MintHelpers.readMintMark` + `readMintFacility`; render NMM/facility cleanly |
| `screens/home_dashboard.dart` | `data['Mint Mark']` (line 800) | Use `MintHelpers.readMintMark` |
| `screens/program_manager_screen.dart` | `variety.label == 'No Mint Mark' ? 'NMM'`, batch-add payload `mint_mark` (lines 1481, 2113–2132) | Send both `mint` and `mint_mark` on batch-add; use `MintHelpers` |
| `screens/add_coins_hub.dart` | Manual, camera, cert, CSV import paths (lines 6208, 6218) | Populate both `mint` and `mint_mark` on all write/import paths |
| `services/pcgs_import_service.dart` | `mapToFirestoreSchema` sets `'Mint Mark': mintMark` (lines 231, 251) | Emit `mint` + `mint_mark` (+ `'Mint Mark'` until Phase 7) |
| `services/backup_export_service.dart` | CSV export reads `map['Mint Mark'] ?? map['mint_mark']` (lines 261, 267) | Export `Mint` (facility) column + `Mint Mark` (via `MintHelpers`) |
| `services/coin_search_service.dart` | Search/filter on mint mark | Dual-key read `mint` and `mint_mark` |
| `services/set_expansion_helper.dart` & `set_grouping_service.dart` | Set child mint inheritance / grouping | Preserve/propagate `mint` + `mint_mark` |
| `services/epn_service.dart` & `wishlist_service.dart` | Query/match coins | Dual-key read via `MintHelpers` |

### 6.2 Python Backend & Cloud Functions (`numista_backend/`)
| File | Current Usage | Planned Update |
|---|---|---|
| `services/mint_helpers.py` *(new)* | N/A | `read_mint_mark`, `read_mint_facility`, `is_west_point_nmm`, `resolve_two_field_mint` |
| `services/mint_nomenclature_service.py` | `resolve_coin_catalog_metadata` returns `mint_mark` only (line 132) | Return both `mint` and `mint_mark` |
| `services/checklist_parser.py` | Defaults missing `mint_mark` to `"P"` (line 312) | Use `resolve_two_field_mint` (blank stays `""`, `mint = "Philadelphia"`) |
| `services/duplicate_check.py` | Queries `Mint Mark` / `mint_mark` (lines 43, 54, 71) | Use `read_mint_mark` + `read_mint_facility` for duplicate matching |
| `routes/import_routes.py` | Reads `mint_mark` / `Mint Mark` (lines 126, 177) | Populate and normalize `mint`, `mint_mark` (+ `'Mint Mark'` until Phase 7) |
| `main.py` | Golden schema mapping, batch-add (lines 8913–8938), cert lookup, AI identify, CSV export, `execute_add_coin` | Use `mint_helpers.py` on all read/write/export endpoints |
| `services/greysheet_service.py`, `us_mint_catalog_service.py`, `catalog_verifier.py` | Lookup by `mint_mark` | Accept `mint` + `mint_mark` |
| `scan_service/collection_inventory.py`, `estate_pdf_builder.py`, `services/passport_pdf_generator.py` | Render coin mint in reports/PDFs | Use `read_mint_facility` + `read_mint_mark` (render NMM when Philly + blank) |
| `scripts/migrate_two_field_mint.py` *(new)* | N/A | Dry-run, execute, `--rollback`, and Phase 7 `--prune-legacy-key` |
| Cloud Function `syncLegacyMintMarkOnUpdate` *(new)* | N/A | Syncs legacy `'Mint Mark'` updates into `mint` + `mint_mark` (§3.3); sunset in Phase 7 |

---

## 7. Deliverable 6: Display Layer Note — Rendering `NMM` & Facility

**Rule:** Always show the facility when known; when `mint_mark` is blank (`""`) and `mint` is `"Philadelphia"`, render `"NMM"` (compact) or `"No Mint Mark"` (detail).

- **Detail Screen (`DetailsTab` in `coin_detail_screen.dart`):**
  - Show two distinct, clear tiles:
    - `Mint Facility`: `coin.mint` (e.g. `"Philadelphia"`, `"Denver"`) — shown whenever `coin.mint.isNotEmpty`.
    - `Mint Mark`: `coin.mintMark.isNotEmpty ? coin.mintMark : (coin.mint == 'Philadelphia' ? 'No Mint Mark' : '')`.
  - In prose/summary headers (e.g. `coin_detail_screen.dart:368, 729, 2907` and `inventory_gallery.dart:163`):
    - If `mintMark.isNotEmpty`: `1921-D Morgan Dollar` (or `Denver (D)`).
    - If `mintMark.isEmpty && mint == 'Philadelphia'`: `1921 (NMM) Morgan Dollar` / `Philadelphia (NMM)` (never `1921-P`!).
    - If `mintMark.isEmpty && mint.isEmpty`: `1921 Morgan Dollar` (omit mark & facility cleanly).
- **Compact Chips / Table Columns (`my_collection_screen.dart`, `program_manager_screen.dart`):**
  - Mint column / variety chip: show `"NMM"` when `mint == "Philadelphia" && mint_mark == ""`, otherwise `mint_mark`. Tooltip or secondary label shows `"Philadelphia (No Mint Mark)"`.

---

## 8. Phased Execution, NET-810 Cleanup & Technical Debt Sunset

1. **Phase 1 — Helpers & Schema:** Add `mint_helpers.dart`, `mint_helpers.py`, and update `CoinModel` (`mint` + `mint_mark` with dual-key readers and transitional dual-write).
2. **Phase 2 — Write, Import & Legacy-Sync Paths:** Update manual entry, CSV, PCGS, checklist/batch-add, backend ingest, and deploy `syncLegacyMintMarkOnUpdate` (§3.3).
3. **Phase 3 — Readers, Counting, Matching & Display:** Update `SlotResolver`, collection screens, duplicate check, and UI display (`NMM` / `No Mint Mark` + facility).
4. **Phase 4 — Migration Dry-Run:** Run `migrate_two_field_mint.py --dry-run`; review counts and anonymized sample diffs with Founder Eric.
5. **Phase 5 — Migration Execute (Gated):** Only after Founder Eric's explicit typed `YES`, run `migrate_two_field_mint.py --execute --confirm-token=YES` with JSONL backup snapshot. Verify 100% coverage of US coins.
6. **Phase 6 — Remove NET-810 Workaround:** Remove the blank `mintMark == ''` → `'Philadelphia'` fallback in `MintProductLookupService.lookupForCoin` (NET-810 §5.2 / §7.1) and join directly on `coin.mint` (`mint_facility`). Remove legacy `mintMark.isEmpty` Philadelphia assumptions in `SlotResolver`.
7. **Phase 7 — Technical Debt Sunset (Decommission Dual-Write & Cloud Function):**
   - **Entry Gate (all 3 required):**
     1. Minimum mobile app version supporting two-field mint is enforced / all active clients upgraded.
     2. Cloud Function `syncLegacyMintMarkOnUpdate` emits **0** sync events for **14 consecutive days**, verified via GCP Cloud Logging (Logs Explorer):
        ```text
        resource.type="cloud_function"
        resource.labels.function_name="syncLegacyMintMarkOnUpdate"
        jsonPayload.event="legacy_mint_mark_sync_count"
        severity="INFO"
        timestamp>="<UTC_ISO_14_DAYS_AGO>"
        ```
        *(Log-based metric `custom.googleapis.com/numista/legacy_mint_mark_sync_count` sum over 14d == `0`.)*
     3. `migrate_two_field_mint.py --dry-run` reports **0** documents missing `mint` or `mint_mark`.
   - **Sunset Actions:**
     1. Remove `'Mint Mark'` from `CoinModel.toFirestore()` and all backend/import writers (`main.py`, `import_routes.py`, `pcgs_import_service.dart`, `add_coins_hub.dart`).
     2. Delete / undeploy `syncLegacyMintMarkOnUpdate` Cloud Function to eliminate unnecessary compute.
     3. *(Optional, gated by Founder Eric's typed `YES`)* Run `migrate_two_field_mint.py --prune-legacy-key --confirm-token=YES` to `firestore.DELETE_FIELD` the deprecated `'Mint Mark'` key from existing documents. (Dual-key readers in `MintHelpers` remain safe no-ops if any historical export/backup still has `'Mint Mark'`.)

---

## 9. Deliverable 7: Rollback Notes

- **Code Rollback (Phases 1–3, 6):**
  - Because Phase 1–3 readers are **dual-key**, reverting any UI, `SlotResolver`, or NET-810 commit via `git revert <sha>` on `dev` is safe and non-destructive — legacy `'Mint Mark'` remains intact on existing and newly written documents during Phases 1–6.
  - Phase 6 (removing NET-810's blank→Philly heuristic) MUST NOT be merged until Phase 5 migration is verified; if an issue is found post-Phase 6, `git revert` of the Phase 6 commit immediately restores the heuristic.
- **Data Rollback (Phase 5 Migration):**
  - `migrate_two_field_mint.py --execute` writes `scratch/mint_migration_backup_<timestamp>.jsonl` before any mutation.
  - Running `migrate_two_field_mint.py --rollback --backup-file=<path> --confirm-token=YES` (§5.3) restores every modified document in `WriteBatch` chunks (400 ops/batch) and deletes `mint` / `mint_mark` via `firestore.DELETE_FIELD` if they were not present pre-migration.
- **Branch Safety:** All work stays on `dev` (or a feature branch off `dev`); `main` is never touched.

---

## 10. Execution-Readiness Verification Matrix

Before each phase is declared complete, the following machine-checkable commands must exit `0`:
- **Dart / Flutter (Phases 1–3, 6, 7):**
  - `flutter analyze` (in `numista_mobile/`) → 0 errors.
  - `flutter test test/mint_helpers_test.dart test/slot_resolver_phase4a_test.dart test/slot_resolver_washington_test.dart` → 100% pass (covering `MintHelpers` dual-key priority, dirty value sanitization, NMM display formatting, and `26XE`/`26XH` West Point NMM vs `1921` Morgan Philadelphia NMM).
- **Python Backend (Phases 1–5):**
  - `pytest numista_backend/tests/test_mint_helpers.py numista_backend/tests/test_checklist_parser.py numista_backend/tests/test_migrate_two_field_mint.py` → 100% pass (covering Rules 1–11, `--dry-run` zero-write guarantee, `--execute` backup JSONL creation, and `--rollback` field restoration).
- **Pre-Migration Live Gate (Phase 4 → Phase 5):**
  - `python numista_backend/scripts/migrate_two_field_mint.py --dry-run` completes with 0 unhandled exceptions and zero PII in output.

---

## 11. Verbatim Live Code Pastes (Current Implementations)

All excerpts below were read directly from `dev` on 2026-11-13 with exact `file:line-line` ranges.

### 11.1 `numista_mobile/lib/models/coin_model.dart` (lines 4–10, 81–87, 149–157, 169–179, 248–256)
```dart
// lines 4-10
class CoinModel {
  final String id;
  final String year;
  final String mintMark;
  final String denomination;
  final String programSeries;
  final String themeSubject;

// lines 81-87
  CoinModel({
    required this.id,
    this.year = '',
    this.mintMark = '',
    this.denomination = '',
    this.programSeries = '',
    this.themeSubject = '',

// lines 149-157
  static (String year, String mint) _splitYearMint(String rawYear, String rawMint) {
    if (rawMint.isNotEmpty) return (rawYear, rawMint); // already split
    final trimmed = rawYear.trim();
    // Matches 4-digit year (with optional bicentennial suffix) + single uppercase letter
    final re = RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);
    final m = re.firstMatch(trimmed);
    if (m != null) return (m.group(1)!, m.group(2)!.toUpperCase());
    return (trimmed, rawMint);
  }

// lines 169-179
  factory CoinModel.fromMap(Map<String, dynamic> data, String id) {
    // Split combined Year+Mint before assigning (e.g. "2006D" → year='2006' mint='D')
    final (year, mintMark) = _splitYearMint(
      data['Year']?.toString().trim() ?? data['year']?.toString().trim() ?? '',
      data['Mint Mark']?.toString().trim() ?? data['mintMark']?.toString().trim() ?? data['MintMark']?.toString().trim() ?? '',
    );
    return CoinModel(
      id: id,
      year: year,
      mintMark: mintMark,
      denomination: TextSanitizer.fixMojibake(data['Denomination']?.toString() ?? data['denomination']?.toString() ?? ''),

// lines 248-256
  Map<String, dynamic> toFirestore() {
    return {
      'Year': year,
      'Mint Mark': mintMark,
      'Denomination': denomination,
      'Program/Series': programSeries,
      'Theme/Subject': themeSubject,
      'Variety': variety,
      'Condition': condition,
```

### 11.2 `numista_mobile/lib/utils/slot_resolver.dart` (lines 198–199, 740–847)
```dart
// lines 198-199
  static String _mintMark(Map<String, dynamic> item) =>
      _field(item, ['Mint Mark', 'mint_mark', 'Mint', 'mint']);

// lines 740-847
    // ── Reverse Proof — mint-specific ────────────────────────────────────────
    // P-REVERSE-PROOF: Philadelphia RP (Morgan 26XF, Peace 26XL)
    if (vId == 'P-REVERSE-PROOF') {
      return (mintMark == 'P' || mintMark.isEmpty) && isReverseProof;
    }
    // S-REVERSE-PROOF: San Francisco RP (Innovation dollars)
    if (vId == 'S-REVERSE-PROOF') {
      return mintMark == 'S' && isReverseProof;
    }
    // W-REVERSE-PROOF: West Point RP (reserved)
    if (vId == 'W-REVERSE-PROOF') {
      return mintMark == 'W' && isReverseProof;
    }
    // Generic REVERSE-PROOF legacy catch-all
    if (vId == 'REVERSE-PROOF') {
      return isReverseProof;
    }

    // ── Enhanced Uncirculated — mint-specific ─────────────────────────────────
    // EU: struck at West Point; coin may bear no mint mark (Morgan/Peace 2026 26XE/26XH)
    if (vId == 'EU') {
      return isEnhancedUnc && (mintMark == 'W' || mintMark.isEmpty);
    }
    // W-EU: Enhanced Unc, West Point marked (ASE 26EG, AGE 26EH)
    if (vId == 'W-EU') {
      return isEnhancedUnc && mintMark == 'W';
    }

    // ── West Point Uncirculated (Kennedy 2019-W/2020-W; AWQ W mint) ──────────
    if (vId == 'W-UNC') {
      return mintMark == 'W' && !isProof && !isEnhancedUnc;
    }

    // ── Congratulations Set Proof — Philadelphia (26RF) ───────────────────────
    // Separate row from W-PROOF (26EA). Requires 'congratulations' in variety/title.
    if (vId == 'P-PROOF-CONG') {
      final title = _field(item, ['Title', 'title', 'official_us_mint_title']);
      final isCongrats = varField.contains('CONGRATUL') || title.contains('CONGRATUL');
      return (mintMark == 'P' || mintMark.isEmpty) && isProof && isCongrats;
    }

    // ── S-SILVER (1976-S 40% silver BU only — NOT proof) ─────────────────────
    if (vId == 'S-SILVER') {
      return mintMark == 'S' && isSilver && !isProof;
    }

    // ── S-SILVER-PROOF (1976-S / 1992-1998 S silver proof) ───────────────────
    if (vId == 'S-SILVER-PROOF') {
      return mintMark == 'S' && isSilver && isProof;
    }

    // ── S-PROOF (S-mint clad proof only) ─────────────────────────────────────
    if (vId == 'S-PROOF' || vId == 'S-CLAD' || vId.startsWith('S-PROOF-')) {
      return mintMark == 'S' && isProof && !isSilver;
    }

    // ── Philadelphia Proof (1936-1942, 1950-1964) — id: 'PROOF' ──────────────
    if (vId == 'PROOF') {
      final isPhillyOrUnmarked = mintMark.isEmpty || mintMark == 'NONE' ||
                                  mintMark == 'P'  || mintMark == 'PHILADELPHIA';
      return isProof && isPhillyOrUnmarked && !isSMS;
    }

    // ── P-PROOF: Philadelphia Proof (Morgan 1895-P, proof-only dated coins) ───
    // isReverseProof guard prevents P-REVERSE-PROOF coins landing here.
    if (vId == 'P-PROOF') {
      return (mintMark == 'P' || mintMark.isEmpty) && isProof && !isReverseProof;
    }

    // ── Generic mint+PROOF (W-PROOF: ASE 26EA, AGE 26EB, Buffalo 26EL) ───────
    // isReverseProof guard: Reverse Proof coins must not land in W-PROOF.
    if (vId.contains('PROOF') && !isReverseProof) {
      final baseMint = vId.split('-').first;
      if (baseMint.isNotEmpty && baseMint != 'S') {
        return mintMark == baseMint && isProof;
      }
      return isProof;
    }

    // ── SMS (Special Mint Set) — 1965, 1966, 1967 ────────────────────────────
    if (vId == 'SMS') {
      return isSMS;
    }

    // ── Uncirculated standard mint marks (P, D, W, S, CC, O) ────────────────
    // !isProof, !isSMS, !isEnhancedUnc: each handled above.
    final baseMint = vId.split('-').first;
    if (mintMark == baseMint && !isProof && !isSMS && !isEnhancedUnc) return true;
    if (baseMint == 'P' &&
        (mintMark.isEmpty || mintMark == 'NONE' || mintMark == 'PHILADELPHIA') &&
        !isProof && !isSMS && !isEnhancedUnc) { return true; }

    // ── Annual uncirculated set — D-UNC blank-mint guard ─────────────────────
    // Sets (e.g. 26RJ) store no Mint Mark field but contain both P and D cards.
    // The P blank-mint guard above already covers P-UNC.
    // This guard covers D-UNC: allow match when the item is a kept set and
    // mintMark is absent. Individual coins with Mint Mark 'D' are already caught
    // by the exact-match branch above; this branch is a set-only fallback.
    if (baseMint == 'D' &&
        (mintMark.isEmpty || mintMark == 'NONE') &&
        !isProof && !isSMS && !isEnhancedUnc) {
      final isAnnualSet = (item['is_set'] as bool? ?? false) ||
          (item['Denomination']?.toString() ?? '').toLowerCase() == 'set';
      if (isAnnualSet) return true;
    }

    return false;
```

### 11.3 `numista_mobile/lib/screens/coin_detail_screen.dart` (lines 363–372, 430–438, 474–485, 1538–1542)
```dart
// lines 363-372
  String _buildAiPrompt() {
    final c = _coin;
    final denom = _fmtDenomination(c.denomination);
    final coinId = [
      if (c.year.isNotEmpty) c.year.replaceAll(RegExp(r'\.0$'), ''),
      if (c.mintMark.isNotEmpty) '(${c.mintMark})',
      if (denom.isNotEmpty) denom,
      if (c.programSeries.isNotEmpty) c.programSeries,
    ].join(' ');

// lines 430-438
  void _enterEditMode() {
    _editCtrl.clear();
    final fields = {
      'Year': _coin.year,
      'Mint Mark': _coin.mintMark,
      'Denomination': _coin.denomination,
      'Quantity': _coin.quantity.isEmpty ? '1' : _coin.quantity,
      'Program/Series': _coin.programSeries,

// lines 474-485
    // ── Auto-split combined Year+Mint (e.g. "2006D" typed into Year field) ────
    final ymRe = RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);
    final rawYear = (updates['Year'] as String? ?? '').trim();
    final rawMint = (updates['Mint Mark'] as String? ?? '').trim();
    bool yearMintSplit = false;
    if (rawYear.isNotEmpty && rawMint.isEmpty) {
      final m = ymRe.firstMatch(rawYear);
      if (m != null) {
        updates['Year']      = m.group(1)!;
        updates['Mint Mark'] = m.group(2)!.toUpperCase();
        // Also update the in-memory controllers so the UI reflects the split
        _editCtrl['Year']?.text      = m.group(1)!;

// lines 1538-1542
    final fields = <(String, String, bool)>[
      ('Year', coin.year.replaceAll(RegExp(r'\.0$'), ''), false),
      ('Mint Mark', coin.mintMark, false),
      ('Denomination', _fmtDenomination(coin.denomination), false),
```

### 11.4 `numista_mobile/lib/services/pcgs_import_service.dart` (lines 230–254)
```dart
// lines 230-254
    final year        = pcgsData['Year']?.toString() ?? '';
    final mintMark    = pcgsData['MintMark']?.toString() ?? '';
    // Grade field from API is the full grade string e.g. "PR70DCAM"
    final gradeStr    = grade
        ?? pcgsData['Grade']?.toString()
        ?? pcgsData['GradeString']?.toString()
        ?? '';
    final pcgsNo      = pcgsData['PCGSNo']?.toString() ?? '';
    final priceGuide  = pcgsData['PriceGuideValue'];
    final isNFC       = pcgsData['IsNFCSecure'] as bool? ?? false;
    final population  = pcgsData['Population']?.toString() ?? '';
    final metalContent = pcgsData['MetalContent']?.toString() ?? '';
    final dieVariety  = pcgsData['DieVariety']?.toString() ?? '';
    final seriesName  = pcgsData['SeriesName']?.toString() ?? '';

    // Denomination: use the raw field if available, else parse from name
    String denomination = pcgsData['Denomination']?.toString()
        ?? _parseDenomination(coinName.isNotEmpty ? coinName : designation);

    return {
      'Year':                     year,
      'Mint Mark':                mintMark,
      'Denomination':             denomination,
      'Program/Series':           coinName.isNotEmpty ? coinName : designation,
```

### 11.5 `numista_mobile/lib/screens/add_coins_hub.dart` (lines 6204–6220) & `backup_export_service.dart` (lines 260–268)
```dart
// add_coins_hub.dart lines 6204-6220
                    for (final r in rawRows) {
                      final itemData = {
                        // PascalCase keys matching _F.* UI constants
                        'Year': getValue(r, selectedYearHeader),
                        'Mint Mark': getValue(r, selectedMintHeader),
                        'Denomination': getValue(r, selectedDenomHeader),
                        'Condition': getValue(r, selectedGradeHeader),
                        'Cost': getValue(r, selectedCostHeader),
                        'Variety': getValue(r, selectedVarietyHeader),
                        'Retailer/Website': getValue(r, selectedRetailerHeader),
                        'Retailer Invoice #': getValue(r, selectedInvoiceHeader),
                        'Personal Notes': getValue(r, selectedNotesHeader),
                        // Legacy lowercase keys for backward compat
                        'year': getValue(r, selectedYearHeader),
                        'mint_mark': getValue(r, selectedMintHeader),
                        'denomination': getValue(r, selectedDenomHeader),
                        'condition': getValue(r, selectedGradeHeader),

// backup_export_service.dart lines 260-268
    final StringBuffer csv = StringBuffer();
    csv.writeln('Year,Mint Mark,Denomination,Program/Series,Theme/Subject,Condition,Qty,Cost,AI Estimated Value,Certification Number,Retailer,Invoice,Storage Location,Notes,Owner Photo URLs,Added');

    for (final c in coins) {
      final map = c as Map<String, dynamic>;
      csv.writeln([
        _cleanCsvCell(_formatYear(map['Year'] ?? map['year'])),
        _cleanCsvCell(map['Mint Mark'] ?? map['mint_mark']),
        _cleanCsvCell(map['Denomination'] ?? map['denomination']),
```

### 11.6 `numista_mobile/lib/screens/program_manager_screen.dart` (lines 1480–1486, 2113–2133) & `inventory_gallery.dart` (lines 143–172)
```dart
// program_manager_screen.dart lines 1480-1486
                                // Abbreviate long labels for compact display
                                final chipLabel = variety.label == 'No Mint Mark'
                                    ? 'NMM'
                                    : variety.label.isEmpty
                                        ? coin.name
                                        : variety.label;

// program_manager_screen.dart lines 2113-2133
      String parsedMint = '';
      if (varietyId.isNotEmpty && varietyId != 'P') {
        final firstSegment = varietyId.split('-').first;
        if (RegExp(r'^[A-Z]{1,2}$').hasMatch(firstSegment) &&
            firstSegment != 'P' &&
            firstSegment != 'EU' &&
            firstSegment != 'RP') {
          parsedMint = firstSegment;
        }
      }

      slots.add({
        'coin_name':    seriesName,
        'year':         parsedYear,
        'mint_mark':    parsedMint,
        'denomination': parsedDenom,
        'variety_id':   varietyId,
        'quantity':     1,
        'Quantity':     1,
      });

// inventory_gallery.dart lines 143-145, 161-172
              final rawMint = data['Mint Mark']?.toString().trim() ?? '';
              final mintMark = (rawMint.toLowerCase() == 'null' || rawMint.toLowerCase() == 'nan') ? '' : rawMint;
...
              // Headline Logic: Skip missing Year/Mint Mark
              String titleText = '';
              if (year.isNotEmpty && mintMark.isNotEmpty) {
                titleText = '$year-$mintMark $denomination';
              } else if (year.isNotEmpty) {
                titleText = '$year $denomination';
              } else if (mintMark.isNotEmpty) {
                titleText = '$mintMark $denomination';
              } else {
                titleText = denomination;
              }
```

### 11.7 `numista_backend/services/checklist_parser.py` (lines 310–365) & `duplicate_check.py` (lines 42–74)
```python
# checklist_parser.py lines 310-316, 356-365
        for idx, coin in enumerate(raw_coins):
            year = int(coin.get("year", 0)) if str(coin.get("year", "")).isdigit() else 0
            mint_mark = str(coin.get("mint_mark", "P")).upper().strip()
            theme_subject = str(coin.get("theme_subject", "")).strip()
            denom = str(coin.get("denomination", "Quarter")).strip()
            series = str(coin.get("program_series", program_series)).strip()
            official_title = get_official_us_mint_title(year, theme_subject)
...
            item = {
                "item_type": "coin",
                "Country": "United States",
                "country": "United States",
                "is_foreign": False,
                "Year": year or "",
                "year": year,
                "Mint Mark": mint_mark,
                "mint_mark": mint_mark,

# duplicate_check.py lines 42-74
    year_val = str(coin_dict.get("Year") or coin_dict.get("year") or "").strip()
    mint_val = str(coin_dict.get("Mint Mark") or coin_dict.get("mint_mark") or "").strip()
...
        q = (
            coins_ref
            .where("Year", "==", year_val)
            .where("Mint Mark", "==", mint_val)
            .where("Denomination", "in", denom_variants[:10])
            .limit(5)
            .get()
        )
...
            q_lc = (
                coins_ref
                .where("year", "==", year_val)
                .where("mint_mark", "==", mint_val)
                .limit(5)
                .get()
            )
```

### 11.8 `numista_backend/services/mint_nomenclature_service.py` (lines 129–134), `routes/import_routes.py` (lines 125–129, 175–178), & `main.py` (lines 8913–8938)
```python
# mint_nomenclature_service.py lines 129-134
    # Default result (unmapped / fail-closed baseline)
    result = {
        "year": str(year).strip(),
        "mint_mark": (mint_mark or "").strip().upper(),
        "denomination": norm_denom or "Quarter Dollar",
        "program_series": raw_series or "Unmapped / General Collection",

# import_routes.py lines 125-129, 175-178
            y = str(data.get("year") or data.get("Year") or "").strip()
            mm = str(data.get("mint_mark") or data.get("Mint Mark") or "").strip().upper()
            den = _normalize_us_denomination(str(data.get("denomination") or data.get("Denomination") or ""))
...
        cert = str(norm_coin.get("cert_number") or norm_coin.get("cert") or "").strip().lower()
        year = str(norm_coin.get("year") or "").strip()
        mint = str(norm_coin.get("mint_mark") or norm_coin.get("mint") or "").strip().upper()

# main.py lines 8913-8938
    for slot in req.slots:
        doc_ref = coins_ref.document(str(uuid.uuid4()))

        # Derive Strike Type + Variety from variety_id so SlotResolver.matchesVariety()
        # can evaluate isProof / isReverseProof / isEnhancedUnc correctly.
        # MF1-B: if the Flutter client sent mint_mark="EU" (finish token, not a mint),
        # normalise to "" — slot_resolver EU gate requires mintMark=='W'||mintMark.isEmpty.
        strike_fields = _derive_strike_fields(slot.variety_id)
        normalized_mint = "" if slot.mint_mark == "EU" else slot.mint_mark

        batch.set(doc_ref, {
            # Identity fields — program_id is mandatory on all new checklist writes
            'program_id':     req.program_id,          # snake_case, exact
            'Program/Series': req.program_name,         # display name for legacy compatibility

            # Slot fields
            'Theme/Subject':  slot.coin_name,
            'Year':           slot.year,
            'Mint Mark':      normalized_mint,          # "EU" normalised to "" (MF1-B)
            'Denomination':   slot.denomination,
            'variety_id':     slot.variety_id,          # persisted for future audit/migration

            # Strike / finish — required by SlotResolver.matchesVariety()
            'Strike Type':    strike_fields['Strike Type'],
            'Variety':        strike_fields['Variety'],
```

---

## 12. Canonical Fixture Table (15 Deterministic Test Cases)

Every fixture below is **zero-PII** and must be encoded verbatim in `numista_backend/tests/test_mint_helpers.py` and `numista_mobile/test/mint_helpers_test.dart`:

| ID | Input Fields (`year`, `raw_mm`, `raw_mint`, `series`, `denom`, `strike`, `variety`, `metal`, `item_no`, `country`) | Rule Hit | Expected `mint` | Expected `mint_mark` | Compact Display (`NMM`) | Detail Display (`No Mint Mark`) | `SlotResolver` Match Outcome |
|---|---|---|---|---|---|---|---|
| F01 | `1921`, `""`, `""`, `"Morgan Dollars"`, `"Dollar"`, `""`, `""`, `""`, `""`, `"United States"` | #10 | `"Philadelphia"` | `""` | `"NMM"` | `"No Mint Mark"` | Matches `P` / `P-UNC` (not `D`) |
| F02 | `1921`, `"D"`, `""`, `"Morgan Dollars"`, `"Dollar"`, `""`, `""`, `""`, `""`, `"United States"` | #3 | `"Denver"` | `"D"` | `"D"` | `"D"` | Matches `D` / `D-UNC` |
| F03 | `1943`, `"P"`, `""`, `"Jefferson Nickels"`, `"5 Cents"`, `""`, `""`, `"35% Silver"`, `""`, `"United States"` | #1 | `"Philadelphia"` | `"P"` | `"P"` | `"P"` | Matches `P` / `P-UNC` |
| F04 | `1943`, `""`, `""`, `"Jefferson Nickels"`, `"5 Cents"`, `""`, `"War Nickel"`, `"35% Silver"`, `""`, `"United States"` | #11 | `""` | `""` | `""` | `""` | Ambiguous war nickel w/ missing mark; does NOT invent `P` or Philly NMM |
| F05 | `1942`, `""`, `""`, `"Jefferson Nickels"`, `"5 Cents"`, `""`, `"Type 1"`, `"Copper-Nickel"`, `""`, `"United States"` | #10 | `"Philadelphia"` | `""` | `"NMM"` | `"No Mint Mark"` | Matches `P` / `P-UNC` (1942 Type 1 NMM) |
| F06 | `1974`, `""`, `""`, `"Lincoln Cents"`, `"Cent"`, `""`, `""`, `""`, `""`, `"United States"` | #10 | `"Philadelphia"` | `""` | `"NMM"` | `"No Mint Mark"` | Matches `P` / `P-UNC` |
| F07 | `1958`, `""`, `""`, `"Franklin Half Dollars"`, `"Half Dollar"`, `"Proof"`, `""`, `""`, `""`, `"United States"` | #10 | `"Philadelphia"` | `""` | `"NMM"` | `"No Mint Mark"` | Matches `PROOF` (not `S-PROOF`) |
| F08 | `1980`, `"P"`, `""`, `"Washington Quarters"`, `"Quarter"`, `""`, `""`, `""`, `""`, `"United States"` | #1 | `"Philadelphia"` | `"P"` | `"P"` | `"P"` | Matches `P` / `P-UNC` |
| F09 | `1849`, `"D"`, `""`, `"Liberty Head Gold"`, `"$5 Half Eagle"`, `""`, `""`, `""`, `""`, `"United States"` | #2 | `"Dahlonega"` | `"D"` | `"D"` | `"D"` | Matches `D` (facility `"Dahlonega"`, not `"Denver"`) |
| F10 | `1849`, `"C"`, `""`, `"Liberty Head Gold"`, `"$5 Half Eagle"`, `""`, `""`, `""`, `""`, `"United States"` | #4 | `"Charlotte"` | `"C"` | `"C"` | `"C"` | Matches `C` |
| F11 | `2026`, `""`, `""`, `"Morgan Dollars"`, `"Dollar"`, `"Enhanced Uncirculated"`, `"Enhanced Uncirculated"`, `""`, `"26XE"`, `"United States"` | #9 | `"West Point"` | `""` | `""` | `""` | Matches `EU` (not `P-UNC`, not `W-EU`) |
| F12 | `2026`, `""`, `""`, `"Morgan Dollars"`, `"Dollar"`, `"Reverse Proof"`, `"Reverse Proof"`, `""`, `"26XF"`, `"United States"` | #10 | `"Philadelphia"` | `""` | `"NMM"` | `"No Mint Mark"` | Matches `P-REVERSE-PROOF` (not `EU`, not `S-REVERSE-PROOF`) |
| F13 | `1964`, `"None"`, `""`, `"Roosevelt Dimes"`, `"Dime"`, `""`, `""`, `""`, `""`, `"United States"` | Sanitize + #10 | `"Philadelphia"` | `""` | `"NMM"` | `"No Mint Mark"` | Dirty `"None"` sanitized to `""`; matches `P` |
| F14 | `2015`, `""`, `""`, `"Canadian Maple Leaf"`, `"$5 CAD"`, `""`, `""`, `""`, `""`, `"Canada"` | #11 | `""` | `""` | `""` | `""` | Non-US coin; never forced to Philadelphia |
| F15 | *Unmigrated doc:* `{'Year': '1921', 'Mint Mark': 'D', 'Denomination': 'Dollar', 'Program/Series': 'Morgan Dollars'}` (no `mint` / `mint_mark` keys) | Dual-key fallback | `readMintFacility`=`""` (pre-migration) | `readMintMark`=`"D"` | `"D"` | `"D"` | `CoinModel.fromMap` reads legacy `'Mint Mark': 'D'` via fallback; matches `D` / `D-UNC` |
