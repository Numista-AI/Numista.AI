# Walkthrough — Upcoming US Mint Releases & Valuation Integrity

## Overview & Execution Summary

- **Branch:** `dev`
- **Commits:**
  - `9fa3e380`: `feat(mint-releases): add Upcoming US Mint Releases page + eliminate fake $0.50 valuation fallback`
  - `ea71ed50`: `test(mint-releases): add automated test suites and harden migration/seed scripts`
- **Remote Status:** Confirmed pushed to `origin/dev`.
- **Target Platform:** Flutter Desktop Web / Mobile + FastAPI Backend.

---

## 1. Verified Systems & Automated Test Suites

### A. Scraper & Catalog Service Tests (`test_usmint_releases_scraper.py`)
Executed command:
```bash
pytest numista_backend/tests/test_usmint_releases_scraper.py -v
```
**Results:** 9/9 tests passed (Exit code 0):
- `test_parse_price_valid`: Parses clean prices (`$169.00`, `$1,250.50`, `5740`, `$24.95`).
- `test_parse_price_invalid_and_empty`: Safely handles `"TBD"`, `"N/A"`, `"PENDING"`, `""`, and `None`.
- `test_badge_to_status`: Canonical status mapping for `New`, `Coming Soon`, `Pre-Order`, `Sold Out`.
- `test_load_local_catalog`: Confirmed loading 74 verified items from `usmint_2026_catalog.json`.
- `test_normalize_product`: Proper Firestore schema projection.
- `test_detect_changes`: Change delta identification (price, badge, status).
- `test_get_mint_issue_price_exact_item`: Exact item number retrieval from Firestore.
- `test_get_mint_issue_price_fuzzy_search`: Fuzzy theme/denomination fallback match.
- `test_get_mint_issue_price_ignores_non_20xx`: Ignores non-current year items.

### B. Valuation Integrity Tests (`test_valuation_integrity.py`)
Executed command:
```bash
pytest numista_backend/tests/test_valuation_integrity.py -v
```
**Results:** 4/4 tests passed (Exit code 0):
- `test_add_coin_valuation_integrity_greysheet_hit`: Greysheet `cpg_retail` takes precedence.
- `test_add_coin_valuation_integrity_fallback_to_mint_price`: US Mint issue price used when Greysheet fails.
- `test_add_coin_valuation_integrity_honest_pending`: Both fail -> status is `"pending"`, value is `None`/`"Pending"`, never `$0.50`.
- `test_remediation_detection_logic`: Accurately distinguishes fake `$0.50` baseline placeholders from legitimate values.

### C. Flutter Service Tests (`upcoming_releases_service_test.dart`)
Executed command:
```bash
flutter test test/services/upcoming_releases_service_test.dart
```
**Results:** 4/4 tests passed (Exit code 0):
- Model `fromJson` parses all 14 fields including specifications and limits.
- Model `toJson` serializes cleanly.
- Model defaults missing optional fields cleanly.
- Fallback service returns verified 2026 US Mint products on network failure/offline.

### D. Flutter Widget Tests (`upcoming_releases_screen_test.dart`)
Executed command:
```bash
flutter test test/upcoming_releases_screen_test.dart
```
**Results:** 1/1 widget test passed (Exit code 0):
- AppBar title renders.
- Filter ChoiceChips (`All`, `Coming Soon`, `Available`, `Sold Out`) render and interact.
- Hero card and list view render product data.

### E. Frontend Static Analysis
Executed command:
```bash
flutter analyze --no-fatal-infos
```
**Results:** 0 errors, 0 warnings in new/modified codebase.

---

## 2. Dry-Run Migration & Seeding Verification

### A. Seed Script (`seed_upcoming_releases.py --dry-run`)
- Verified reading all 74 items from `usmint_2026_catalog.json`.
- Verified credentials fallback via `serviceAccountKey.json`.
- Verified enrichment via `us_mint_catalog_service.py`.

### B. Valuation Remediation Script (`remediate_fake_valuations.py --dry-run`)
- Scanned 5,486 total coins across 15 real Firestore users.
- Accurately identified 24 coins with fake `$0.50` baseline valuations.
- Confirmed remediation path -> updates to honest `"Pending"` (or US Mint Issue Price once seeded).
- 0 execution errors.

---

## 3. Files Created & Modified

### Backend:
- [`numista_backend/services/usmint_releases_scraper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/services/usmint_releases_scraper.py)
- [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py)
- [`numista_backend/_scripts/remediate_fake_valuations.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/remediate_fake_valuations.py)
- [`numista_backend/tests/test_usmint_releases_scraper.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tests/test_usmint_releases_scraper.py)
- [`numista_backend/tests/test_valuation_integrity.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tests/test_valuation_integrity.py)

### Frontend:
- [`numista_mobile/lib/services/upcoming_releases_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/upcoming_releases_service.dart)
- [`numista_mobile/lib/screens/upcoming_releases_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/upcoming_releases_screen.dart)
- [`numista_mobile/lib/screens/home_dashboard.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/home_dashboard.dart)
- [`numista_mobile/lib/screens/base_layout.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/base_layout.dart)
- [`numista_mobile/lib/widgets/header_stats_bar.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/header_stats_bar.dart)
- [`numista_mobile/test/services/upcoming_releases_service_test.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/upcoming_releases_service_test.dart)
- [`numista_mobile/test/upcoming_releases_screen_test.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/upcoming_releases_screen_test.dart)

### Documentation & Seed:
- [`1 NUMISTA.AI/BETA TEST/Grok Bot/15 SEPT 26/Upcoming US Mint releases/seed_upcoming_releases.py`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/BETA%20TEST/Grok%20Bot/15%20SEPT%2026/Upcoming%20US%20Mint%20releases/seed_upcoming_releases.py)
- [`1 NUMISTA.AI/BETA TEST/Grok Bot/15 SEPT 26/Upcoming US Mint releases/README.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/BETA%20TEST/Grok%20Bot/15%20SEPT%2026/Upcoming%20US%20Mint%20releases/README.md)
