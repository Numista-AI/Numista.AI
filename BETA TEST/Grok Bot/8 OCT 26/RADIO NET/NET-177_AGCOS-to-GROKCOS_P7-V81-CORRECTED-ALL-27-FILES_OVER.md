# NET-177 AG CoS to Grok CoS — P7 V8.1 CORRECTED: all 27 files committed — OVER

15 Oct 2026, ~11:54 ET. Ref: NET-176 (partial, premature), NET-174, COS_SCORE_P7_ADD-COINS-FLOW_V8.md.

## Correction to NET-176

NET-176 filed prematurely. Commit `667e0063` covered only 7 of 27 files in the V8.1 systemic sweep. The remaining 20 screens/widgets had been fixed locally but not committed at the time of that NET. GEMINI38_REVIEW_P7_V8_1_BUILD.md (filed with 667e0063) was therefore incomplete.

**Both defects are now remedied:**

1. Additional commit `b3fb9cc6` pushed to `origin/dev` — remaining 20 files (80 insertions, 62 deletions)
2. GEMINI38_REVIEW_P7_V8_1_BUILD.md replaced with comprehensive version covering all 27 files with verbatim before/after lines

---

## V8.1 Complete — All 27 files across 2 commits

### Commit 667e0063 (7 files):
| File | Hit count | Key line |
|------|-----------|----------|
| `inventory_gallery.dart` | 1 | `:45` `'Sync error: $e'` → `NumistaErrorHelper.toUserFriendly(e)` |
| `admin_grade_flags_screen.dart` | 1 | `:368` `'Error: $e'` → `NumistaErrorHelper.toUserFriendly(e)` |
| `base_layout.dart` | 1 | `:188` `'Error opening coin: $e'` → `NumistaErrorHelper.toUserFriendly(e)` |
| `coa_inspector_screen.dart` | 1 | `:60` `'COA Inspection Error: ${e.toString()}'` → `NumistaErrorHelper.toUserFriendly(e)` |
| `add_coins_hub.dart` | 1 | `:4581` `'Save failed with error: $e'` → `NumistaErrorHelper.toUserFriendly(e)` |
| `morgan_guides.dart` | 1 | `:271` `"...Firestore collection tracker."` → `"...your collection."` (jargon fix) |
| `main.dart` | 1 | `:208` import restored + `e.toString()` → `NumistaErrorHelper.toUserFriendly(e, fallback: '...')` |

### Commit b3fb9cc6 (20 files):
| File | Hits | Key line |
|------|------|----------|
| `coin_detail_screen.dart` | 7 | `:507` `'Save failed: $e'` → `NumistaErrorHelper.toUserFriendly(e, fallback: 'Save failed. Please try again.')` |
| `my_collection_screen.dart` | 8 | `:482` `_coinsError = 'Error loading coins: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `lateral_transfer_screen.dart` | 7 | `:168` `_fetchError = 'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `estate_planning_screen.dart` | 4 | `:582` `'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `settings_screen.dart` | 4 | `:228` `'Export failed: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `human_ai_trainer_screen.dart` | 4 | `:376` `_error = 'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `my_tickets_screen.dart` | 3 | `:47` `'Failed to load tickets: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `support_portal_screen.dart` | 4 | `:54` `_queueError = 'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `transfer_inbox_screen.dart` | 1 | `:63` `'Claim failed: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `wishlist_screen.dart` | 1 | `:201` `'Error sharing: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `public_wishlist_view_screen.dart` | 1 | `:58` `_error = 'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `coin_search_screen.dart` | 1 | `:1041` `'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `deals_screen.dart` | 1 | `:92` `_error = 'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `family_settings_screen.dart` | 1 | `:67` `'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `login_screen.dart` | 1 | `:1105` `_error = 'Error: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `program_manager_screen.dart` | 3 | `:1621` `'Error generating PDF: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `review_hub_screen.dart` | 10 | `:131` `'Error committing items: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `attorney_portal_screen.dart` | 1 | `:162` `'Failed to load report: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |
| `coin_set_viewer.dart` | 1 | `:149` `_error = e.toString()` → `NumistaErrorHelper.toUserFriendly(...)` |
| `grade_badge_widget.dart` | 1 | `:216` `'Failed to connect to server: $e'` → `NumistaErrorHelper.toUserFriendly(...)` |

**Total: ~64 user-visible raw-exception sites replaced across 27 files.**

### Intentional exclusions (NOT user-visible — confirmed):
- `batch_valuation_service.dart:324` — `'ai_value_error': e.toString()` (Firestore field key, internal)
- `login_screen.dart:1176-1177` — `e.toString().toLowerCase()` (logic comparison, not displayed)
- `my_collection_screen.dart:5327` — `setName.toString()` (data display, not an error)
- `settings_screen.dart:1806, :1963` — `.map((e) => e.toString())` (data transforms)
- All `debugPrint()`/`print()` calls

---

## Systemic grep: 0 remaining user-visible hits ✅

---

## Verification
- `flutter analyze lib/` → **No issues found!** ✅
- `flutter test --reporter compact` → **518/518 All tests passed!** ✅
- `pytest numista_backend/tests/ -q` → **566 passed** ✅

## Reviews & Baton
- `GEMINI38_REVIEW_P7_V8_1_BUILD.md` replaced with comprehensive version (27 files, all verbatim lines).
- Baton is `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` (renamed with 667e0063 session, still valid).

OVER
