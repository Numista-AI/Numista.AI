# BATON — NET-816 Catalog Chunk 1 FAIL-FIX ROUND 2 — PLAN ONLY
From: Grok Bot CoS, 10 Nov 2026 ~6:45 PM ET. To: AG CoS v5.
Trigger: Field Tester scored the p7-gate preview (a3d7dca2, release a47a275d1eb6b51f) 47/100 FAIL at 6:40 PM ET.
Report: C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\RADIO NET\FT_RESULT_NET816_CATALOG_CHUNK1_p7gate_20261110.md (+ shots_net816.tar.gz). Read it in full.
Track: new fail-fix track, attempt 1/10, writer AG CoS v5 try 1/4.

## Must fix (material)
- F1: #/catalog opens the signed-in home view, not the catalog. Direct /catalog works. Route #/catalog (and #/catalog/<id>) to the public catalog.
- F2: Catalog images: about 166 console errors from the CSP blocking Wikimedia images; only 1,213 of 2,965 coins pass "Photos only". Fix the CSP (firebase.json headers / index.html meta) to allow the image hosts the catalog actually uses, and list every host. Also report how many coins still have no image after the fix. Per Eric's 31 Oct rule, plan the next step to fill the gaps from gs://numista-reference-library and his collection photos before using any placeholder (plan only; scope it as a separate chunk if it's large).
- F3: Multi-coin sets show a single coin's face value (Morgan/Peace 2-coin set shows $1.00). Sum the face values of the components, or show the "No face value" chip when the components are unknown.
- F4: version.json has no git_commit. Stamp the commit SHA at build so Field Tester can pin the build.
- F5: Half dime melt can't be observed by Field Tester. Propose a read-only way to verify it (a unit test plus melt shown on the catalog detail, or a pre-seeded test coin in a test account that Eric approves separately). Use current spot in the test, not a fixed $1.09.

## Note, not scored
- Search: "1816" returns 0 and "Morgan dollar 1881" returns 0 on both preview and live. Say whether year-only and series+year search should match, and fix it if cheap.
- The Coin Search "Server error 500" Eric saw at 6:22 PM ET (Coin Reference Search screen, "Definitive Registry: 0 records") hasn't been reproduced. Name which backend call that screen makes and why it might 500.

## Limits
PLAN ONLY. No code, commits, deploys, Firestore, Stripe or Cloud Run. Holds 74611e05 and 41b8bd5f stand. 3 AM ET stand-down.
Deliver: PLAN_NET-816_FAILFIX-R2_v1_AGCOS-V5_20261110.md with name, size and SHA-256. Gate: CoS 95, then full-plan SAG 95, then Eric's scoped typed YES before any build or deploy.
