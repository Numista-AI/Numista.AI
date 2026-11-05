# DONE BATON NET-806: `DONE_BATON_NET-806_REVISE_UNIFIED-COIN-DETAILS-VIEW_v1.1_2026-11-05-1550.md`

- **To:** Grok Bot CoS, Stand Alone Grok (SAG), Argon (Gemini 3.8), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 3:50 PM ET
- **Subject:** COMPLETION OF `BATON_NET-806` (Unified Coin Details View Plan Revision v1.1)
- **Delivered Artifact:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` (mirrored to `BATONS/`, `RADIO NET/`, and `INBOX/`)
- **Status:** **PLAN ONLY** (Zero code modifications, zero deployments, zero Firestore writes/seeding).

---

## Summary of Must-Fix Resolutions in v1.1:

1. **Storage Location & PIN Service (Must-Fix #1):**
   - Completely dropped fictional `StorageLocationPinService`.
   - Explicitly specified that physical storage location is strictly suppressed and hidden in all unified views.
   - It will remain hidden until a dedicated PIN architecture, data protection model, and UI design are separately specified, reviewed, and approved via Founder Eric's typed YES.
   - Guaranteed that physical storage location and valuation figures never share a viewport.

2. **Accurate Verbatim Call Sites (Must-Fix #2):**
   - Corrected and verified all five call sites in `my_collection_screen.dart`:
     - Line 2736: Table cell tap (`onTap` col 0)
     - Line 2761: Virtual child parent set info tap (`CoinDetailScreen.show`)
     - Line 2773: Regular coin info tap (`CoinDetailScreen.show`)
     - Line 3044: Card tap (`_showCoinInspectorDialog`, preserving line 3043 `setState`)
     - Line 3122: Parent set card container tap (`_showCoinInspectorDialog`)
   - Re-quoted lines verbatim with surrounding context.
   - Corrected contrast defect citation in `coin_detail_screen.dart`: lines 892–894 (`_kDark(context)` evaluates to `#F4F4F2` in light mode [line 59]) paired with lines 918–922 (`color: Colors.white`), yielding ~1.1:1 unreadable text.

3. **Strict Public / Guest Mode Hide-List (Must-Fix #3):**
   - Defined `isPublicGuestMode: true` for Public Catalog, unauthenticated sessions, or shared links.
   - Hard-suppressed from widget tree: Purchase price, cost basis, purchase date, invoice number, retailer/seller, physical storage location, PIN controls, personal notes, personal reference number, and the private `"Show values"` toggle.
   - Suppressed ownership actions in the bottom action bar: Edit, Delete, Verify, and Wishlist.

4. **Valuation Source Hygiene (Must-Fix #4):**
   - Valuation source is strictly CDN CPG retail (`cpgRetail`).
   - Zero wholesale prices.
   - AI valuation is labeled `"AI Estimate (Experimental)"` and never prioritized or unlabeled.
   - Live eBay tile dropped as a price guide tile.

5. **Congress.gov-Only Laws Tab (Eric Typed AMEND 5 Nov 2:44 PM ET):**
   - Outbound links permitted strictly to Congress.gov via plain `<a href>` text links (`target=_blank`, `rel=noopener`).
   - Zero PCGS, NGC, or third-party links. External cert lookups render in-app plain text citations only (`[cert no. redacted]`).
   - Zero hotlinked images from Congress.gov.
   - Catalog legislation wins when present (`Source: Numista.AI catalog (checked)`). Unchecked Congress.gov text carries prominent disclaimer: `"From Congress.gov, not yet checked by us"`.
   - US-only scope for statutory records.
   - Hard $0.00 spend cap on external API queries; fail-closed behavior (0 paid calls).

6. **Rollback, Feature Flag, & Code Freeze (Must-Fix #5):**
   - Governed by `kUnifiedCoinDetailsEnabled` in `feature_flags.dart`.
   - Legacy views (`_showCoinInspectorDialog` and `CoinDetailScreen`) are preserved untouched during the 10–16 Nov build; flag-off restores them immediately.
   - Pinned rollback baseline commit `9f04550a`.
   - Mandatory Firebase Preview Channel verification before production release.
   - Strict code freeze before 26 Nov 2026 Meta ad launch.

7. **Firestore Writes Segregation (Must-Fix #6 & #7):**
   - Edit, Wishlist, Delete, and Ask Morgan research request logging are Firestore writes.
   - Explicitly segregated to a separate, subsequent typed YES from Founder Eric.
   - Initial unified view operates in read-only mode with zero Firestore writes, zero schema modifications, and zero rules changes.

8. **Automated Testing Suite (Must-Fix #2, #3, #5):**
   - Tests defined for: all five call sites, mutual privacy gate, session persistence of values until modal Close, guest mode hide-list, CPG retail-only pricing, and feature flag fallback.
