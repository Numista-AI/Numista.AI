# BATON NET-813: GROK BOT CoS REVIEW OF UNIFIED COIN DETAILS VIEW v1.3
**Date:** 7 November 2026, 3:45 PM ET  
**From:** Antigravity CoS v4 Work / Catalog Night Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (Reviewer 1)  
**CC:** Stand Alone Grok (SAG, grok-4.7, Reviewer 2), Founder Eric  
**Priority:** THANKSGIVING CRITICAL PATH — UNIFIED COIN DETAILS VIEW (NET-813)  
**Deliverable Plan:**  
- `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md` (mirrored across `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`)  
**Target Score:** $\ge 95 / 100$ per standing review protocol (Argon dropped per Eric 5 Nov 18:07 YES).  

## Review Request
Please perform Grok Bot CoS independent audit and score of `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md` against `origin/p7-v8.9`.

### Comprehensive Must-Fix Closeout (Resolving all 7 Blocking Must-Fixes from CoS-74):

1. **MF-1: Deterministic Rollback & Kill-Switch Architecture (§2.5, §9.2, §9.3)**
   - Replaced broad range revert with reverse-topological ordered SHA revert (`git revert --no-edit <EXECUTE_COMMITS>`) and ancestry validation (`git merge-base --is-ancestor`).
   - Dynamic release ID capture prior to preview deploy; pre-recorded rollback release restore using `firebase hosting:clone numista-vault:<PRE_DEPLOY_RELEASE_ID> numista-vault:live`.
   - Production kill-switch via static remote JSON config (`assets/config/features.json` / CDN endpoint) or URL query override (`?unified_details=false`) — zero Firestore writers required.
   - Pinned `origin/main` strictly locked at `9f04550a`; zero main merges or pushes.

2. **MF-2: Immutable Parent Identity & Navigation Resolution (§3.1, §3.2, §3.3)**
   - Strict fail-closed on missing parent (`crw.isVirtualChild && parentDoc == null`); completely eliminates fallback to child data map `m`.
   - Immutable navigation contract via `UnifiedCoinNavigationContext`.
   - Standalone Parent Mode when opened parent is filtered out of list (`currentIndex = null`; prev/next disabled; informative banner displayed; zero index-0 mismatch).
   - Preserves explicit legacy fallback and all mutation/action callbacks without truncation (`...` eliminated).

3. **MF-3: Laws Provenance, URL Sanitization & Bounded Timeouts (§6.1, §6.2, §6.3)**
   - Provenance schema binding: checked status requires explicit `is_editorial_verified == true` in reviewed fixture/metadata; absent proof displays prominent `"From Congress.gov, not yet checked by us"` badge.
   - Strict `isValidCongressUrl` rejecting non-HTTPS, userinfo/credentials, lookalike domains, and off-host destinations.
   - Reconciled web semantic `<a>` anchor with target=`_blank`/rel=`noopener` vs mobile `launchUrl(..., mode: LaunchMode.externalApplication)`.
   - Bounded 4-second timeout (`.timeout(const Duration(seconds: 4))`) with mounted check; fail-closed empty state on error/timeout; backend writer strictly unexecuted.

4. **MF-4: Rich-Content & Morgan-Notes Safe Rendering (§6.4, §6.5)**
   - Sandboxed Markdown renderer suppressing all outbound links (or routing to internal views) and blocking remote markdown images (`imageDirectory: null`).
   - Prominent `"AI Analysis (Unverified Reference)"` label for AI-generated insights.
   - Theme-aware typography (using `Theme.of(context).colorScheme.onSurface`, eliminating hardcoded white text).
   - Strict `isOwnedStorageUrl` guard verifying origin, HTTPS, and approved Firebase Storage bucket path before any image fetch.

5. **MF-5: Value/Privacy Matrix & Catalog Public Integration (§4.2, §4.3, §5.1)**
   - Rigorous visibility matrix:
     - Owner Mode: financial metrics default-hidden until user taps "Show values" (reveals purchase price, melt value, and CPG retail).
     - Guest / Public Mode: positive CPG retail (`cpgRetail > 0`) is always visible on Overview surface; "Valuation Pending" gold badge only shown when retail is missing or `<= 0`.
   - Public entry adapter (`PublicCoinProjection`) consuming catalog models without private user fields.
   - Clean route binding into public `/catalog` without auth detours or extra clicks.

6. **MF-6: Implementable Offline Test Suite (§10.1, §10.2)**
   - Authored complete `UnifiedCoinDetailHarness` test suite covering:
     - Test 1: Flag-on and flag-off routing.
     - Test 2: Virtual parent missing fails closed.
     - Test 3: Filtered-out parent standalone mode.
     - Test 4: Zero Firestore write mutation assertion.
     - Test 5: Laws URL validator (hostile URLs rejected).
     - Test 6: Bounded Laws loader timeout handling.
     - Test 7: Safe Markdown rendering (no outbound links/remote images).
     - Test 8: CPG retail visibility in guest vs owner modes.
     - Test 9: Public coin projection field redaction.
     - Test 10: Touch target compliance ($\ge 52\times 52$ px).
     - Test 11: Color contrast audit ($\ge 7:1$ high-contrast compliance).

7. **MF-7: Standing Rules & Operational Gates Checklist (§9.1, §9.4, §11.1)**
   - Strict operational gates: independent Founder typed YES gates for any future Firestore writes, security rules, or live deployment.
   - US-only and strict zero-PII/zero-AJ-data protections across all fixtures, logs, and semantics.
   - Alerts only, never budget caps ($20/mo threshold).
   - Thanksgiving Critical Path alignment: Catalog live target ~13 Nov $\rightarrow$ Details View preview 10–16 Nov.

## Next Turn / Sequence
- Grok Bot CoS reviews `PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md` and files score ($\ge 95$).
- Stand Alone Grok (SAG, grok-4.7) reviews independently and files score ($\ge 95$).
- Upon dual $\ge 95$, Founder Eric reviews for typed YES.
- Meanwhile, AG CoS v4 / Catalog Night Team moves to next queued item: `NET-814` (Soft-404 v1.3) $\rightarrow$ `NET-810` (Mint product fields).
