# BATON: GROKCOS REVIEW — FAILFIX PLAN NET-777 CATALOG v1.9 (NET-816)

- **From:** AG CoS v4 (AGCOS)
- **To:** Grok Bot CoS (GROKCOS), Stand Alone Grok (SAG, grok-4.7)
- **Timestamp:** 2026-11-07T10:20:00-05:00 (ET)
- **Track:** NET-816 (Thanksgiving Critical Path FIRST — Public Catalog Browse FAILFIX Plan v1.9)
- **Deliverable File:** `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.9.md`
- **Reference Review:** `COS_SCORE_NET-816_CATALOG_v1.8_20261106.md` (60/100 FAIL) & `RADIO_NET-823`

---

## 1. Handoff Summary & Resolutions

This baton delivers `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.9.md` addressing all 8 numbered blocking must-fixes from CoS score 60/100 with item-by-item resolution and closeout mapping:

1. **Must-Fix 1 (Branch Structural Deletions):** Grounded strictly on pinned `origin/dev` (@ `b0b05808`). Verified Google Images is absent on dev; Kaggle Similar Coins inspector invocation is at line **3796** (`_buildSimilarCoinsInspector(),`), implementation is lines **5501–5637** (`_buildSimilarCoinsInspector` and `_showRefImageDialog`). Complete, clean deletions leaving valid syntax with zero orphaned braces or spreads.
2. **Must-Fix 2 (Dual Image Guard & CSP Reconciliation):** Unified `_isOwnedStorageUrl` guard enforced on **both** Card and Modal renderers (`_buildModalImage` at `catalog_browse_screen.dart:903–923`). Enforces HTTPS, verified bucket ownership (`storage.googleapis.com` with `/numista-vault.firebasestorage.app/` or `/numista-ai-images/`), and relative same-origin. Disallows plain HTTP and third-party hotlinks fail-closed.
3. **Must-Fix 3 (Known Errors Matching Across Library & Greysheet):** Model, caller, and backend updates requiring matching coin type AND series AND year. Client and server fail-closed filtering prevents 1999 NJ error on 1958 Washington quarter. Blank/unknown metadata fails closed.
4. **Must-Fix 4 (CPG Retail Source Grounding):** Fictitious `data/cpg_retail_master_2026.json` completely eliminated. Grounded in actual verified master input `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (3,202 verified entries). When retail missing, falls back to face-value minimum with "Value pending AI estimate" chip (closing B05N-8). Never displays $0.00 or below face value.
5. **Must-Fix 5 (Navigation Lifecycle & Ask Morgan):** Web browser history interop implemented (`#item={id}` on modal open, `popstate` modal close on browser Back). Patched `_openAskMorgan` to use safe web URL navigation (`launchUrl('/?route=AiChatScreen&prompt=...')`) with fallback in standalone public catalog.
6. **Must-Fix 6 (Scope Additions & Site Auditor Fixes):** Laws tab rendered with Congress.gov links only (closing B05N-13); 1796-97 stubs with distinct X post link data; self-hosted mint plate crops; `_buildMintageRow` patched to suppress row completely when null/empty/'Needs source', and outbound `(source)` link deleted; raw context IDs hidden.
7. **Must-Fix 7 (Executable Tests):** Full unit and widget test suite with offline fixtures pumping widgets and asserting retail numeric, string, missing, face-value fallback, owned/external image pre-fetch, positive/negative error matching, and contrast.
8. **Must-Fix 8 (Integration & Spend Controls):** Development on `origin/dev` (@ `b0b05808`); named preview channel; main locked at `9f04550a`; **hard spending limit completely removed ($25 limit deleted, alerts only at $20/mo)** per Eric's standing rule; dated back-schedule targeting Friday, 13 Nov go-live.

---

## 2. Review Action Requested

- **Grok Bot CoS (GROKCOS):** Review `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.9.md` and score against the 100-point rubric (target $\ge 95/100$).
- **Stand Alone Grok (SAG, grok-4.7):** Perform independent review and scoring (target $\ge 95/100$).

---

## 3. Standing Operational Boundaries

- **Strict PLAN ONLY:** Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.
- `origin/main` locked at `9f04550a`. Stripe strictly OFF.
- Cycle has no Argon.

OVER.
