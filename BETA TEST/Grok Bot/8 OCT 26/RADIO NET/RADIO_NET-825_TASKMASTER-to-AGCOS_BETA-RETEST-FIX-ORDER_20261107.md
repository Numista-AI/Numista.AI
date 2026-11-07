# RADIO NET-825 | TASKMASTER -> AG CoS | BETA RETEST FIX ORDER | 7 Nov 2026

**Authority (Eric's own words, verbatim):**
- 10:14 AM ET to GB CoS: "Delegate out as much as you can, but get my site updated so I can retry this Beta Test!"
- 10:17 AM ET to Task Master: "YES, file the beta retest fix order"

**Limits (binding):**
- PLAN ONLY. Fold into the in-flight revisions: NET-816 v1.9, NET-817 v1.6, NET-813 v1.3, NET-814 v1.3, NET-810 v1.1. No separate competing plans.
- KEEP Live eBay Check. This REVERSES NET-813 v1.2's removal of the eBay control.
- Build target: p7-gate PREVIEW only, and only after plans pass review at 95+ (CoS and SAG) AND Eric types YES. NO deploy to live.
- Main stays locked. Stripe stays off. No Firestore writes. Alerts only, NO caps.
- Source ledger: RADIO NET\ERIC_BETA_ISSUE_TRACKER_20261107.md
- Filed does NOT mean fixed. Only a Field Tester PASS on preview, with evidence, closes an item.

**ACTION:** AG CoS, ACK on RADIO with an ETA for the folded revisions.

---
# BETA RETEST FIX ORDER

**FILED as RADIO NET-825 by Task Master on Eric's typed YES. PLAN ONLY - no execution authority.**
From: GB CoS. Intended recipient: AG CoS. 7 Nov 2026 EST.
Purpose: converge the 5 Nov and 7 Nov beta findings into the fewest coordinated revision bundles, then produce a reviewable p7-gate preview for Eric's clean retest. Eric requested the site updated, but this draft itself remains PLAN ONLY. No git writes/pushes, deployment or Firestore writes are authorized here.

## Three coordinated bundles, no parallel duplicate plans
A. **Cert intake + owner detail workflow**, new explicit sections in NET-813 v1.3: provider/OCR distinction, one primary lookup action, feedback, canonical fill, next-step visibility, purchase fields, save navigation, Inspector Edit, real click baseline and KEEP eBay affiliate check. This closes B05N-1/2/3/4/5/6/11/16/18 and B07N-1/2/3. Provider integration limitations must be researched and disclosed; no fabricated successful lookup.
B. **Cards/photos/contrast**, NET-817 Cards/Images v1.6 plus NET-813 call-site integration: B05N-7/10/12/15. Coordinate the single removal owner for Google/Kaggle with NET-816; preserve all user-photo aliases, immediate state refresh and orientation correction. No new competing image plan.
C. **Catalog identity, composition, valuation, errors and Laws**, NET-816 v1.9 plus NET-813 integration: B05N-8/9/13/14/17. Carry explicit face-value requirement rather than substituting only a pending chip. NET-814 v1.3 owns public catalog/pricing/route prerequisites only; NET-810 v1.1 owns optional Mint-product fields only. Keep cost/issue price distinct from market value. Those two existing revisions are dependencies where genuinely needed, not excuses to postpone Cert Add behind unrelated scope.

## Required acceptance matrix (all open items)
|Rank|ID / repeats|Eric recorded words|Current status / proposed owner|Acceptance|
|---|---|---|---|---|
|1|B05N-1; B07N-2|Page said it can't look up NGC certs, but the ngccoin.com link worked. Confusing. Grade C- overall.|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|NGC 8321797-003 and CACG 663261171 resolve inside the app when a provider is supported; otherwise explicitly say lookup unavailable, preserve OCR fields and allow correction without claiming a provider record was not found. No invented provider result.|
|2|B05N-2; B07N-1/2|Clicking Look Up seemed to do something, but nothing visibly changed|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|One visible pending/result/error state per lookup; double-click cannot duplicate requests or collection entries; distinguish unavailable, timeout and genuine not-found.|
|3|B05N-4; B07N-3|Coin Name / Description left blank; denomination showed 25C — not US Mint canonical|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|Quarter name is Washington Quarter (Proof), denomination Quarter Dollar; nickel name is catalog-verified Jefferson nickel wording, denomination Five Cents; preserve year/grade/cert; unknown mint mark remains explicitly unknown, not invented.|
|4|B05N-3|Next step is below the fold; nothing tells you to scroll|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|At each step, the next action is visible or automatically scrolled into view on the tested laptop viewport; no hunting below the fold.|
|5|B05N-5|No purchase price / date / bought-from on Add by Cert form — put price in Notes; Cost $0.00|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|Enter and persist Price paid, Date bought and Bought from in the Add-by-Cert form; reopen and verify all three, separately from market value.|
|6|B05N-6|After Confirm, left on same page with no next step; Add by Cert # back-link text does nothing (only arrow works)|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|Confirm adds exactly one item and opens that coin in My Collection with Coin added banner and Add another; full back-link text and arrow both work.|
|7|B05N-7|Uploaded photo not used as coin image — says No Obverse photo yet|In plan, not built; B: NET-817 Cards/Images + NET-813 surfaces|Uploaded obverse/reverse survive save, reopen and refresh; catalog fallback used only as appropriate, never overwriting a user photo; test camelCase and snake_case aliases.|
|8|B05N-10|Reverse photo didn't show in Inspector, then upside-down on card; obverse missing|In plan, not built; B: NET-817 Cards/Images + NET-813 surfaces|Upload each side and see it immediately in the open Inspector without closing/reopening; both sides display upright on card and Inspector; test the supplied upside-down nickel rear photo with rotation correction.|
|9|B05N-17|Metal typed by hand and misspelled Silve; cannot edit Metal from Inspector. Site should have known 1958 quarter = 90% Silver from NGC + Catalog|Unplanned / implementation unknown; C: NET-816 Catalog + NET-813 integration|Catalog year/type supplies metal composition automatically (1958 quarter 90% silver); correction can be made in Inspector with provenance; refresh persists and melt uses corrected validated composition.|
|10|B05N-9|Melt Value N/A on a 90% silver 1958 quarter|Unplanned / implementation unknown; C: NET-816 Catalog + NET-813 integration|1958 quarter catalog composition and weight feed melt calculation against timestamped current silver quote; show units, source/time and stale/unavailable state; do not invent silver content for the 1952 nickel.|
|11|B05N-8|Est. Value $0.00 and no AI Value even after cost entered|In plan, not built; C: NET-816 Catalog + NET-813 integration|Positive grade-appropriate CDN retail takes precedence; absent retail displays at least face value with Value pending AI estimate; no blank/zero/below-face value; cost and mint issue price never masquerade as market value.|
|12|B05N-11|Can only edit coin by switching Cards → Table and clicking pencil|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|Inspector has a usable Edit action; edit permitted metal/purchase fields, save, reopen and verify persistence without switching Cards to Table.|
|13|B05N-12|White text on off-white background in coin detail view — unreadable|In plan, not built; B: NET-817 Cards/Images + NET-813 surfaces|All affected light/dark surfaces meet WCAG AA 4.5:1 normal text and 3:1 large text; test Inspector, details, financials and pending chips on real rendered backgrounds.|
|14|B05N-16; B07N-1/3|Too many clicks overall (C-). 25 and 30 were placeholders — did not count|Unplanned / implementation unknown; A: Cert intake/retest section (NET-813 dependency)|Field Tester records actual baseline and after-fix clicks from logged-in dashboard through upload, review, purchase entry, save, inspect and edit for BOTH cert fixtures, with per-action list, scrolls, retries, elapsed time and viewport. No invented 25/30 baseline; after-fix fewer clicks for same completed tasks, no loss of accuracy.|
|15|B05N-14|Known Errors shows 1999 NJ quarter clipped-planchet example on a 1958 Washington quarter|In plan, not built; C: NET-816 Catalog + NET-813 integration|Known Errors requires matching coin type AND series AND applicable year; 1999 NJ example cannot appear for 1958 Washington; missing metadata fails closed; positive same-series fixture passes.|
|16|B05N-13|History tab is generic; no Legislation / Laws tab|In plan, not built; C: NET-816 Catalog + NET-813 integration|Relevant authorizing Act/verified source appears in Laws, with Congress.gov links only for that tab; unknown data is labelled, not generic fabricated history; test quarter and nickel plus empty/error states.|
|17|B05N-15|Google Images button + Similar in Reference Library / Kaggle panel (Tap to Expand spins forever) — remove; don't send users off-site for photos|In plan, not built; B: NET-817 Cards/Images + NET-813 surfaces|No Google Images action or Kaggle/Similar panel/spinner on Inspector or its clones; fetch failure/timeout reaches a bounded terminal state; no off-site photo sends.|
|18|B05N-18|Live eBay Check — KEEP. Already in eBay Affiliate program. Verify every eBay link carries our affiliate tag|Unplanned / implementation unknown; A: NET-813 KEEP eBay correction|KEEP Live eBay Check; every generated eBay outbound URL has the configured affiliate campaign/tag and correct coin query; test actual URLs without a purchase. Never expose affiliate credentials.|


## Field Tester handoff and hard gates
1. Plan must map EVERY B05N-1..18 and B07N-1..3 to exact files, actual target branch/ref, code-level design, behavioral tests and one owner. Provide before/after screenshots and failure-path tests, not comment-only tests. No identity inferred from unrelated notes; do not invent mint marks, catalog source files or prices.
2. Use the real fixtures: NGC 8321797-003 (1958 PF67 quarter) and CACG 663261171 (1952 MS64 nickel). Count real clicks before changes and after on the same viewport and task definition; log every action, scroll, retry and elapsed time. No claimed numerical reduction without measured baseline. Tester checks preservation and single save in an authorized test account, not destructive writes in Eric's account.
3. No new code/build execution under this draft. First revise plans and obtain CoS >=95 and SAG >=95 plus Eric's explicit typed authorization for the scoped preview build/necessary test writes. Specify any test-data writes separately; current no-Firestore-write restriction stays in force until authorized.
4. Target the **p7-gate preview**, with exact URL/build SHA visible, so Eric can retry. Plan must reconcile p7-v8.9 vs dev, preview branch naming, target dependencies and rollback; no assumption that main changes equal live deployments.
5. **Live deployment is a separate gate**: reviews >=95, build/test evidence, and Eric's typed YES for live. Main stays locked, Stripe OFF. Alerts only, no spending caps. No provider terms acceptance or paid service setup under this order.
6. Do not ask Eric to repeat the full beta until Field Tester has passed this acceptance matrix on the exact preview build and GB CoS gives him the URL, SHA and known exceptions. Today's partial form is evidence of failure/ambiguity, not a successful retest.

## Required response to this order if later approved and filed
Return one coverage table, bundle dependency order, exact preview path, test strategy, unknown provider/API restrictions, and realistic ETA. A plan-only DONE is not code DONE; code DONE is not preview PASS; preview PASS is not live deployment.

## Explicit contradiction to resolve
KEEP Live eBay Check (B05N-18). NET-813 v1.2's proposed deletion of _onSearchEbay contradicts Eric's recorded instruction. Remove that deletion from the revised plan and verify affiliate tags; Congress.gov-only restriction is scoped to Laws links.
