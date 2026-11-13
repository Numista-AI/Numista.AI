# BATON NET-804 - To: AG CoS v4 - PLAN ONLY: FAILFIX NET-777 Catalog v1.4 (CoS 85 / SAG 70 FAIL on v1.3)
Source: GB CoS ~2:55 PM ET 5 Nov. Argon 98 PASS, but CoS **85 FAIL** and SAG **70 FAIL** after read-only checks against the real repo. Eric's YES is blocked.
Score file: `COS_SCORE_NET-803_FAILFIX-777-v1.3_20261105.md` (RADIO NET + BATONS). **Priority: CRITICAL PATH — Thanksgiving 26 Nov Meta ad launch. Take first.**

**AG CoS v4:** File `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` (+ corrected `docs/MISSING_IMAGES.csv`). Fix:
1. **Real target:** `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` on `dev` (not p7-v8.9). Re-quote verbatim: `_openAskMorgan` 223-228, `_onTypeChanged` 209-214, era 129-130, `_showItemDetailModal` 810, loader 60.
2. **Remove the live outbound `(source)` link** (dev 1010-1017 `launchUrl(uri)`); plain-text credits only.
3. **US-only:** remove/hide the `Foreign Coins` tab (dev 599-602).
4. **MorganChatPopout spec:** `initialQuery:` + required `onClose:`; say how it is hosted (overlay per `base_layout.dart:1094` or a sized wrapper). Drop "Gemini 3.5 Flash" unless cited.
5. **CSV truth:** fix false `Public Domain (US Govt / Pre-1929)` on Franklin Mint (1969-73) / Medallic Art medals and exclude from PD ingest until licensed; move non-mark text out of `mint_mark`; update §2.D to 2,354 / 666 / 181 / 1; drop "100% clean".
6. **Real $ stop:** alerts don't stop spend — add an enforced stop or named owner+action; price on Firebase Hosting egress incl. image bytes.
7. **Real rollback target:** `assets/catalog/catalog_public_v1.json` + git SHA; prior Hosting release, not `HEAD~1`.
8. Non-blocking: pre-federal use C1 flag only; one line "CDN CPG retail only, no wholesale"; confirm ad landing host (`numista.ai`); add Foreign-tab / zero-`launchUrl` checks to the preview checklist.
**Plan A caps apply.** Locks unchanged: `origin/main` `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII, no AJ data. PLAN ONLY — no execute/deploy/merge without Eric's separate YES.
**Chain:** AG files revision → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
