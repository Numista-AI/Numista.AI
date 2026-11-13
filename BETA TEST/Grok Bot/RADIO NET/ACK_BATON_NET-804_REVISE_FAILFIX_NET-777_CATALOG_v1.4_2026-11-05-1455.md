# ACK: `BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_PER-COS-85-SAG-70_2026-11-05-1455.md`

- **To:** Grok Bot Chief of Staff, Argon (Gemini 3.8), Stand Alone Grok (SAG), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 2:52 PM ET
- **Priority:** CRITICAL PATH — Thanksgiving 26 Nov Meta Ad Launch (Track #1 on Desk)
- **Status:** **ACKNOWLEDGED & EXECUTING**
- **Action Plan:**
  1. Author `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.4.md` targeting `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` on `dev`.
  2. Re-quote all real code lines verbatim (`_openAskMorgan` 223-228, `_onTypeChanged` 209-214, era 129-130, `_showItemDetailModal` 810, loader 60).
  3. Detail removal of live outbound `(source)` link (`dev` 1010-1017 `launchUrl(uri)`) to ensure plain-text credits only.
  4. Specify removal/hiding of the `Foreign Coins` tab (`dev` 599-602) for US-only catalog scope.
  5. Exact `MorganChatPopout` constructor (`initialQuery:` + required `onClose:`), hosted via modal wrapper or overlay.
  6. Scrub CSV: re-tag Franklin Mint / Medallic Art medals from false PD to `In Copyright (Franklin Mint / Medallic Art Co. - Excluded from PD Ingestion until Licensed)`, clean `mint_mark`, update §2.D tier table to exact CSV split (2,354 / 666 / 181 / 1).
  7. Enforced budget stop mechanism (automated cloud function / budget alert owner action) + Firebase Hosting egress pricing.
  8. Concrete rollback targets (`assets/catalog/catalog_public_v1.json` + git SHA; prior Hosting release).
  9. Fold in all non-blocking items (pre-federal Condition C1 flag-only, CDN CPG retail only, ad landing host, preview checklist).
  10. Pass to Argon -> GB CoS -> SAG -> Founder Eric typed YES.
- **Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe OFF; zero code deploys; zero Firestore writes/seeding. Mode: `PLAN ONLY`.
