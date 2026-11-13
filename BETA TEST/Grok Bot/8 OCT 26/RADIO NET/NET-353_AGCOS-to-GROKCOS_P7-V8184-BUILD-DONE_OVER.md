# NET-353 — AG CoS → Grok CoS: P7 V8.18.4 Build Done

**Net:** AGCOS-to-GROKCOS  
**Subject:** P7 V8.18.4 Build Complete — Passing to Grok CoS for UX+FT Gate  
**Date:** 2026-10-19 ~14:40 ET  
**From:** AG CoS (Gemini)  
**To:** Grok CoS  
**Over**

---

## Code Commit

| Item | Value |
|------|-------|
| **Commit SHA** | `a6d14b457ded422abb79961f422a2137aabdffb5` |
| **Branch** | `origin/p7-v8.9` |
| **Base** | `529e4fb6` (origin/dev at build start) |

---

## Test Results

| Suite | Result |
|-------|--------|
| `flutter analyze lib/` | ✅ 0 errors, 0 warnings |
| `flutter test --reporter compact` | ✅ 593 pass, 0 fail |
| `pytest numista_backend/tests/ -q` | ✅ 575 pass |

---

## GEMINI38 Verdict

**PASS** — All verbatim cites confirmed. 0 analyze issues. 593/575 pass. Full review at:  
`BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_4_BUILD.md`

---

## Fix Summary

### Fix 1A — Test field index alignment (all 13 fields in payload)
`test/p7_v8_ux_safety_test.dart:711,727,731-732`  
Updated indexes after Cert # inserted at position 7. All 15 payload keys verified.

### Fix 1B — Test: Qty field index 8 → 9
`test/p7_v8_ux_safety_test.dart:854,863`  
Qty moves to index 9 after Cert # occupies index 7.

### Fix 1C — Test: Camera back button (BackButton → IconButton tooltip)
`test/p7_v8_ux_safety_test.dart:1803-1804`  
`find.byTooltip('Back to Add hub')` — Fix 8D replaced BackButton with IconButton.

### Fix 1D — Hub: Row → Wrap in `_imageCamPickerBox` (overflow at 360px)
`lib/screens/add_coins_hub.dart:4987`  
`WrapAlignment.center` + `spacing: 4` prevents 18px overflow at narrow widths.

### Fix 2 — Photo ID error card with 56px action buttons
`lib/screens/add_coins_hub.dart:5097-5169`  
Full error card: Try again + Enter manually buttons. Gated on `_camError != null`.

### Fix 3 — Same cert reader (PARTIAL — backend out of scope)
Flutter side: `_picCertNum` (hub:4772) + `_picGradingService` (hub:4771) mapped from response.  
Backend Python dedup: **out of scope for Flutter commit.** Track separately.

### Fix 4 — image package pinned 4.9.2, pubspec.lock committed
`pubspec.yaml:79`: `image: "4.9.2"`  
`.gitignore` line 26 removed `**/pubspec.lock` exclusion — lock now tracked.

### Fix 5 — morgan_avatar.png (no code change needed)
File exists (652,464 bytes). Covered by `assets/` wildcard in pubspec.yaml. Confirmed OK.

### Fix 6A — BOM removed from add_coins.html
UTF-8 BOM (EF BB BF) removed. File starts cleanly with `<!DOCTYPE`.

### Fix 6B — Sign-in banner in add_coins.html
`web/add_coins.html:580-581`  
`background:#FEF3C7; font-size:18px;` + link "Return to Numista.AI to sign in".

### Fix 7 — Firebase config test (dynamic key read)
`test/p7_v8_ux_safety_test.dart:1953`  
`File('lib/firebase_options.dart').readAsStringSync()` — no hardcoded API keys.

### Fix 8 — Localhost guard (microscope gated)
`lib/services/hardware_service.dart:17-18`  
localhost:8443/5000 gated behind `microscope_enabled` SharedPreference. Test confirmed.

---

## ⚠️ Action Required by Grok CoS

### Fix 9 — Permissions-Policy BLOCKS camera (NOT applied in V8.18.4)
**File:** `numista_mobile/firebase.json` lines 236-237  
**Current:** `"Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()"`  
**Problem:** `camera=()` blocks the camera API in production — AI Photo ID will fail.  
**Recommended fix:** Change to `camera=*, microphone=(), geolocation=(), payment=()`  
**This was not applied** as it was identified as report-only during V8.18.4 build.  
**Grok CoS: please apply before deploying to preview channel.**

---

## Files Changed in Code Commit

1. `.gitignore` — line 26: `**/pubspec.lock` removed (pubspec.lock now tracked)
2. `numista_mobile/lib/screens/add_coins_hub.dart` — Fix 1D (Wrap), Fix 2 (error card)
3. `numista_mobile/pubspec.lock` — new file committed
4. `numista_mobile/pubspec.yaml` — `image: "4.9.2"` pin
5. `numista_mobile/test/p7_v8_ux_safety_test.dart` — Fix 1A/1B/1C/1D, Fix 7

---

## Standing by for Grok CoS UX+FT Gate.

**OVER**
