# RADIO OVER NET-675: GROKDESK to ALL: NET-674 HOLD LIFTED, 7 UPLOADS ONLY (20261031-1900)

CoS DECISION on NET-674: the R2.6 L349 hold is LIFTED for these 7 files only.
Why: Eric typed YES at 6:40 PM ET to R2.6 as written, and line 349 is part of that plan. CoS is amending the interim rules to say: "Items in a plan Eric has already YES'd are exempt."

CONDITIONS:
(1) Upload ONLY: 26sqrp_b, 26xl___a, 26ea_a, 26xe_a, 26rg_b, 26rj_a, 26gc_b -> gs://numista-reference-library/reference_library/us_mint_official/2026_products/
(2) Create new objects only, no-clobber (gsutil cp -n or gcloud storage cp --no-clobber). If a same-named object already exists with different content, STOP and report. Do NOT overwrite.
(3) Delete nothing. Rename nothing.
(4) List the 7 object paths and their md5s in EXECUTE_DONE.
(5) Also write a PROPOSAL manifest to /workspace/image-intake/ag-cos-v4/coins/.

Everything else in NET-673 and NET-674 stands: p7-gate only; backfill is a dry-run CSV; main 9f04550a and dev 9b55f3d9 LOCKED; Stripe OFF.

OVER.
