# BATON NET-803 - PLAN ONLY: FAILFIX NET-777 / NET-788 Catalog v1.3 (SAG 75 FAIL)
Source: GB CoS ~1:42 PM ET 5 Nov. CoS scored FAILFIX v1.2 **96 PASS**; SAG scored **75 FAIL**, so Eric's YES is blocked.
Score file: `COS_SCORE_NET-788_FAILFIX-777-v1.2_20261105.md` (CoS OUTBOX + RADIO NET).

**AG CoS v4:** File `FAILFIX_PLAN_NET-777_CATALOG_v1.3.md` (plan-only). Fix these five things from the SAG fail:

1. **Bind the catalog-first rule:** AI replicas go only in a labeled `ai_replica_images` field — never primary, card, or index.
2. **Add rollback plus preview-before-live** for all six fixes and any GCS ingest.
3. **CSV hygiene:** reclassify the 81 blank-source `EXTERNAL_MIRROR_PENDING` rows (keep them out of public GCS); scrub the ~11–12 album titles; fix `mint_mark='True'`; restore the `.00` cost column.
4. **Hard monthly $ cap plus an alert** on GCS egress under Meta ad traffic.
5. **Rewrite Fix 3 signed-in route;** `/?route=AiChatScreen` repeats the unregistered-route bug.

**Queue:** AG is idle/standing by now — take NET-803 immediately. (Argon continues in parallel on 791 / 798 / 801 reviews.) After v1.3 is filed, Argon scores v1.3 (not v1.2), then GB CoS 95+, then SAG, then Eric's typed YES.
**Plan A caps apply.** Locks unchanged: `origin/main` `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII, no AJ data. No execute/deploy/merge without Eric's separate YES.
