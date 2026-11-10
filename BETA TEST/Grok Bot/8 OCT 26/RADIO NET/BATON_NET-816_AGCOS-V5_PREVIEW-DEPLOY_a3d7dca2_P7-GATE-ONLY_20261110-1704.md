# BATON - NET-816 PREVIEW DEPLOY a3d7dca2 to p7-gate ONLY (AG CoS v5)
Filed: 2026-11-10 17:04 EST by Grok CoS.
Owner: AG CoS v5. Next authorized action: deploy build a3d7dca2 to the p7-gate preview channel only, then report.

## Authority (Eric's own words, card t2517s9662, 5:03 PM ET)
"YES. Deploy build a3d7dca20fbbaf06a522205b22d0740b600de52b to the p7-gate preview channel only. Rollback target RT-B, no redeploy. No live, no main, no Stripe, no Firestore."
Plan gates: CoS 100 PASS (a19a799c...20fa), SAG 97 PASS (347743f2...2deb) on plan v5 SHA 0a7543af...3f52. Build DONE verified by CoS: 3 files, 129+/6- ignoring CR/LF.

## Steps
1. In an isolated worktree (not the shared MyVertexProject tree), check out exactly a3d7dca20fbbaf06a522205b22d0740b600de52b. Confirm `git rev-parse HEAD` equals it.
2. Build the web app from numista_mobile (flutter build web, same build mode the plan specifies).
3. Deploy ONLY to the preview channel: `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` (set an expiry, e.g. --expires 7d). Never `firebase deploy`, never `--only hosting` to live.
4. Read back `firebase hosting:channel:list --project studio-9101802118-8c9a8`: live channel release time must be unchanged (2026-06-24 20:10:45); p7-gate present.
5. Smoke check over HTTP: preview URL root, /catalog and /catalog/x return 200 (SPA rewrite). Report status codes.

## Rollback (RT-B)
No redeploy. If anything is wrong, delete the preview: `firebase hosting:channel:delete p7-gate --project studio-9101802118-8c9a8 --force`. c547b7a0 is NEVER deployed.

## Hard stops
No live channel, no main (stays 9f04550a), no Firestore reads/writes/rules/indexes, no Stripe, no backend/Cloud Run deploy, no checkout in the shared tree. HOLDs 74611e05 and 41b8bd5f stay in force; go-live addendum stays NOT ACTIVE. If Firebase auth fails, STOP and report BLOCKED with the exact error (Eric reauthed ~4:22 PM ET).

## DONE report must include
Deployed commit SHA (full), preview URL, channel expiry, channel-list readback (live unchanged), smoke HTTP codes, and any deviations. Field Tester runs next after CoS verifies.
