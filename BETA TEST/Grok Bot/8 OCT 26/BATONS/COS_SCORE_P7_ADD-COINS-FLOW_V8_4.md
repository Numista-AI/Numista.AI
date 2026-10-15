# COS SCORE - P7 ADD-COINS-FLOW V8.4 BUILD
Scorer: Grok CoS | 2026-10-15 16:40 ET | Reviewed: commit e8b978f2 on origin/dev + GEMINI38_REVIEW_P7_V8_4_BUILD.md + NET-209 (AG) + independent spot-check on EDS_Laptop against COS_SCORE_P7_ADD-COINS-FLOW_V8_4_PLAN_V1.md conditions.
Verdict: **PASS (code).** Gates next: V8.4 preview channel, then UX Designer + Field Tester. No Eric deploy YES yet. Dev only.

| # | Item | Score | Notes |
|---|------|-------|-------|
| 1 | Phone checklist labels / checkbox / header / PDF wrap | **PASS** | Spot-check e8b978f2: years/pct/Collected/Advances/subtitle → fontSize 16; checkbox SizedBox 48x48 + materialTapTargetSize.shrinkWrap; header program.name maxLines:2 + ellipsis; Print+PDF in Wrap(spacing:8, runSpacing:8). |
| 2 | View Checklist + Advances overflow | **PASS** | Both grids childAspectRatio `isNarrow ? 2.6 : 1.6`; View Checklist minimumSize Size(double.infinity, 48); tests p7_v84_program_card_no_overflow_at_389px and _1025px present. |
| 3 | Cost decimal + Qty digitsOnly (line correction) | **PASS** | Cert field ~2909 still `decimal: false` (NOT touched — condition met). Cost Paid camera (_picCost), purchase-cost dialog costCtrl, mint-set Purchase Price all `numberWithOptions(decimal: true)` + `^\d*\.?\d{0,2}` formatter. Manual form Cost already decimal; Quantity digitsOnly. Soft: camera path has no Qty TextField (Quantity hardcoded elsewhere). |
| 4 | Manual Entry CTA polish | **PASS** | Subtitle fontSize 16; Open Manual Entry label fontSize 16. |
| 6 | Login IndexedStack | **PASS** | AnimatedSize+fixed SizedBox+TabBarView removed; IndexedStack(index: _tabCtrl.index); _tabCtrl.addListener setState; header Flexible; stats FittedBox; _divider Flexible(flex:10)+ellipsis; call sites SizedBox(width: infinity); test p7_v84_login_sign_in_button_visible_at_360x680. |
| 7 | mint-releases per-endpoint guard | **PASS** | Set<String> _attempted + _cacheKeyFor(endpoint); fetchUpcoming/fetchAll independent; resetForTest/wasAttempted; unit test present. No leftover _fetchAttempted. |
| Gates | analyze / p7 suite / GEMINI38 | **PASS** | AG+Gemini: flutter analyze 0; p7_v8_ux_safety_test 12/12; GEMINI38 has verbatim before/after + per-item checklists and correctly notes 2906/cert not touched. |

## Next (GROKCOS holds)
1. Deploy **preview only** channel for V8.4 (e8b978f2 lineage) on numista-vault — no live, no backend CORS, no firestore.rules.
2. UX Designer + Field Tester re-gate on that preview (checklist phone layout, login at 360, Manual Entry, Cost decimal keyboard).
3. After gates PASS → Eric typed YES for cherry-pick deploy from main. Not before.

## Housekeeping
- Baton stays **GROKCOS_OVER** (AWAITING V8.4 PREVIEW + UX/FT). Do not pass to AG or ERIC yet.
- Rule 8: P1 HOLD; P5/P6 WAIT; P4/P8/P9/P10 queued — not stalls. No ERIC baton. No deploy YES.
- Commit only baton/score/NET paths. No numista_mobile/.firebase caches.
