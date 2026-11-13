# EXECUTE DONE BATON NET-780 - Split Failfix Plans Filed (v1)
**To:** Antigravity Desk, Grok CoS, Argon (Gemini 3.8)  
**From:** AG CoS v4  
**Date:** 2026-11-04 17:36 ET  
**Track:** NET-780 Split Failfix Plans (NET-780a, NET-780b, NET-780c, NET-780d)  
**Status:** PLAN ONLY COMPLETE - Awaiting Argon Review  

---

## 1. Execution Summary
Per Founder Eric's 4:58 PM ET split amendment and 4-tier Image Source Order directive, NET-780 has been divided into 4 small, surgical plans. All four plans have been authored, verified against verbatim codebase citations, and filed across `BATONS/`, `RADIO NET/`, and `INBOX/`:

1. **NET-780a: Build Stamp**
   - **File:** `FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md`
   - **Scope:** Injects `git_commit` and `build_time` into `/version.json` via post-build script `tools/stamp_build_version.py`.
   - **Verification:** Verified `firebase.json:181-188` already enforces `no-cache, no-store, must-revalidate` for `version.json`. Target verification: `curl -s $URL/version.json | jq .git_commit`.

2. **NET-780b: Broken Cards & Pending Price**
   - **File:** `FAILFIX_PLAN_NET-780b_CARDS_v1.md`
   - **Scope:** 
     - 2026 American Eagle One Ounce: fixes PascalCase `'Title'` and `'Name'` in `canonical_mint_asset_service.dart:110,162-165` to correctly extract SKU `26EA`.
     - 2023-D 5c Jefferson Nickel: maps `2023-NICKEL-D` and `2023-NICKEL-P` in `canonical_mint_asset_service.dart:485`.
     - AE Price 'Pending': adds Mint issue price fallback ($95.00) in `my_collection_screen.dart:3017-3024` and guards raw `'Pending'` string at line 3170.

3. **NET-780c: Images & CSP (Shared with NET-777)**
   - **File:** `FAILFIX_PLAN_NET-780c_IMAGES_v1.md`
   - **Scope:** Adheres strictly to Founder Eric's 4-tier Image Source Order:
     - Tier 1 (Own consolidated images): 28 of 30 coins matched (93.3%).
     - Tier 2 (Wikimedia/NNC mirror to GCS `numista-vault-assets/catalog/`): 2 of 30 coins (6.7%).
     - Tier 3 (Unmapped): 0 coins (0.0%).
     - Tier 4 (PII Gate): 0 personal receipts or user photos permitted; generic coin catalog assets only.
     - CSP: Eliminates 196 console CSP errors by proxying/serving exclusively from internal GCS domain.

4. **NET-780d: Splash Screen Latency (<1.5s vs 40s)**
   - **File:** `FAILFIX_PLAN_NET-780d_SPLASH_v1.md`
   - **Scope:**
     - Isolates root causes: `auth_gate.dart:128-130` synchronously awaiting `UiVariantService.refresh()`, which calls Cloud Run with a 30s timeout (`http_auth_client.dart:70`), plus 3.08 MB uncompressed `logo_owl.png`.
     - Decouples variant refresh (`unawaited(UiVariantService.refresh())`) with 1.5s timeout; optimizes splash asset decode footprint.
     - Target: < 1.5s total splash duration (down from ~42s worst-case).

---

## 2. Guardrails & Compliance
- **Zero code changes applied**: Strict PLAN ONLY.
- **Zero deploys**: `origin/main` locked at `9f04550a`.
- **Zero Firestore writes**: Step 1b live rules deploy and SKU dictionary seed remain on strict HOLD.
- **Rule 6 Verbatim Quotes**: All files cited with verified line numbers and verbatim code lines.
- **Rule 8 Commands**: Machine-checkable verification commands specified for every track.

---

## 3. Next Action
Handoff to Argon (Gemini 3.8) for scoring under baton `BATON_NET-780_ARGON_REVIEW_FAILFIX_SPLIT_v1.md`.
