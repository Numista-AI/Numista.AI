# Walkthrough — Beta Checklist Auto-Detection & EPN Query Hardening

## Overview & Execution Summary

- **Branch:** `dev`
- **Commits:**
  - `a1ea7d65`: `feat(checklist): auto-detect beta progress & harden EPN query syntax`
  - `1229c2a5`: `chore(release): bump version to v4.367`
- **Remote Status:** Confirmed pushed to `origin/dev`.
- **Target Platform:** Desktop Web (`kIsWeb`, 1920x1080 shell). Zero mobile dependencies.

---

## 1. Resolved Issues

### A. Beta Checklist Counter Freeze (`CHECKLIST_COUNTER_STALE`)
- **Root Cause:** Auto-detectable user actions lacked dispatch hooks to `autoCompleteTask`, and account boot lacked a retrospective sync engine to detect prior user activities across collections.
- **Implemented Fixes:**
  - **Broadcast Stream & Event Hub:** Added `BetaChecklistService.onTaskCompleted` event stream.
  - **Retrospective Startup Sync Engine:** Added `syncExistingAccountProgress()` in [beta_checklist_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/beta_checklist_service.dart), running once per session on `home_dashboard.dart` boot using single-read `.limit(1)` existence queries.
  - **Atomic Bootstrap:** Combined schema default initialization and detected tasks into a single atomic `set()` on `!doc.exists`, eliminating the bootstrap race condition.
  - **Toast Deduplication:** Added `Set<String> _displayedToastTaskIds` in [beta_checklist_widget.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/beta_checklist_widget.dart) to eliminate duplicate toasts across multiple open tabs or quick actions.
  - **Action Hooks Connected:**
    - Manual coin entry (`task_3_manual_entry`) in `add_coins_hub.dart`.
    - CSV spreadsheet import (`task_4_csv_upload`) in `add_coins_hub.dart`.
    - Invoice PDF upload (`task_5_invoice_pdf`) in `add_coins_hub.dart`.
    - PCGS cert verification (`task_6_pcgs_cert`) in `add_coins_hub.dart`.
    - Roll entry wizard (`task_7_roll_batch`) in `add_coins_hub.dart`.
    - Foreign coin / exonumia (`task_13_world_items`) in `add_coins_hub.dart` & `world_item_service.dart`.
    - Paper currency entry (`task_12_currency`) in `world_item_service.dart`.
    - Wishlist addition (`task_14_wishlist`) in `wishlist_service.dart`.
    - Public wishlist sharing (`task_15_public_wishlist`) in `wishlist_screen.dart`.
    - Estate planning PDF receipt (`task_16_estate_report`) in `estate_planning_screen.dart`.
    - Ask Morgan AI Deepdive (`task_18_ai_chat`) in `ai_chat_screen.dart`.
    - Beta feedback submission (`task_20_overall_feedback`) in `beta_feedback_service.dart`.

### B. eBay EPN Query Syntax Error & Category Restriction
- **Root Cause:** Raw queries included user/catalog parentheticals (e.g. `(1965-Date)`, `(Uncirculated)`), and appended grader tokens wrapped in parentheses `(PCGS, NGC, CAC)`, which crashed eBay's Boolean query parser.
- **Implemented Fixes:**
  - Stripped all input parentheticals `RegExp(r'\([^)]*\)')`.
  - Stripped punctuation and quotes while preserving numismatic hyphens (`1909-S`, `1916-D`).
  - Appended unparenthesized space-separated grader tokens (`PCGS NGC CAC` for coins, `PMG PCGS` for currency).
  - Defaulted affiliate tracking to `customid=numista_wishlist`.
  - Forced eBay Coins & Paper Money category `_sacat=11116`.

---

## 2. Test Verification & Results

### A. EPN Query Sanitizer Golden Vector Suite
Executed command:
```bash
flutter test test/services/epn_service_test.dart
```
**Results:** All 7 golden test vectors passed (Exit code 0):
1. `2022 P American Women Quarters - Maya Angelou Quarter (1965-Date) coin` → `2022 P American Women Quarters - Maya Angelou Quarter coin`
2. `1909-S VDB Lincoln Cent` → `1909-S VDB Lincoln Cent PCGS NGC CAC`
3. `1921 Peace Dollar (Uncirculated)` → `1921 Peace Dollar PCGS NGC CAC`
4. `$10 1928 Gold Certificate (PMG, 'PCGS Banknote')` → `$10 1928 Gold Certificate PMG PCGS`
5. `1916-D Mercury Dime Fine` → `1916-D Mercury Dime Fine PCGS NGC CAC`
6. `2026 Morgan Silver Dollar (Proof)` → `2026 Morgan Silver Dollar`
7. `1893-S Morgan Silver Dollar Raw` → `1893-S Morgan Silver Dollar Raw PCGS NGC CAC`

### B. Beta Checklist Service Invariants
Executed command:
```bash
flutter test test/services/beta_checklist_service_test.dart
```
**Results:** All 5 tests passed (Exit code 0):
- Exactly 20 distinct tasks defined.
- Strict `snake_case` IDs verified (`task_<num>_<slug>`).
- Auto-detectable and skip properties confirmed.
- Session latch reset verified.

### C. Static Analysis
Executed command:
```bash
flutter analyze lib
```
**Results:**
- `No issues found! (ran in 217.9s)` (Exit code 0).

---

## 3. Files Modified
- [`numista_mobile/lib/services/epn_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/epn_service.dart)
- [`numista_mobile/lib/services/beta_checklist_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/beta_checklist_service.dart)
- [`numista_mobile/lib/widgets/beta_checklist_widget.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/widgets/beta_checklist_widget.dart)
- [`numista_mobile/lib/screens/home_dashboard.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/home_dashboard.dart)
- [`numista_mobile/lib/screens/add_coins_hub.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/add_coins_hub.dart)
- [`numista_mobile/lib/services/world_item_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/world_item_service.dart)
- [`numista_mobile/lib/services/wishlist_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/wishlist_service.dart)
- [`numista_mobile/lib/screens/wishlist_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/wishlist_screen.dart)
- [`numista_mobile/lib/screens/estate_planning_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/estate_planning_screen.dart)
- [`numista_mobile/lib/screens/ai_chat_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/ai_chat_screen.dart)
- [`numista_mobile/lib/services/beta_feedback_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/beta_feedback_service.dart)
- [`numista_mobile/firestore.indexes.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/firestore.indexes.json)
- [`numista_mobile/test/services/epn_service_test.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/epn_service_test.dart)
- [`numista_mobile/test/services/beta_checklist_service_test.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/beta_checklist_service_test.dart)
