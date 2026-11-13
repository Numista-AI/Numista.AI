# BATON NET-777 - FAILFIX PLAN v1 (PLAN ONLY, no execute) - Live catalog failed Field Tester
To: AG CoS v4   From: Antigravity Desk (for GB CoS)   4 Nov 2026 4:28 PM ET
QUEUE: start AFTER NET-772 is done.

Field Tester's browser pass of https://numista-vault.web.app/catalog was an OVERALL FAIL. Screenshots are on the box at /workspace/catalog_ft/shots/.

Plan the fixes in this order:
1. Images: the CSP connect-src blocks upload.wikimedia.org, so every card shows 'No photo yet' (166 console errors).
2. Deep links: records open as a pop-up and the URL never changes. Each record needs a real shareable URL.
3. Ask Morgan does nothing when signed out.
4. The era filter stays applied when changing tabs, so results look empty.
5. The Washington Indian Peace Medal (ca. 1789) shows in the Pre-Federal filter but has no badge. Pick one consistent rule (C1: pre_federal==true, 9 records).
6. First load takes 7-9 seconds. Propose a speed fix with a target time.

Output: INBOX\FAILFIX_PLAN_NET-777_CATALOG_v1.md
- Quote only from real files with real line numbers.
- Add a test step for each fix.

Review cycle: Argon, then GB CoS 95+, then SAG, then Eric's typed YES. PLAN ONLY: no code, no deploy.
Locks are unchanged: no Firestore, main stays 9f04550a, Stripe stays OFF. Social Media does NOT get the link yet.

---
## AMENDMENT A1 - 4 Nov 2026 4:38 PM ET (Desk, for GB CoS) - replaces Fix 1
1. Images, PRIMARY fix: plan a ONE-TIME mirror of the Wikimedia Commons images we use into our own GCS/Firebase Storage, served from our domain.
   - Keep the license and attribution metadata for each image (author, license, source URL) and show it.
   - Include a storage and egress COST ESTIMATE: image count, total GB, and dollars per month.
   - The CSP connect-src edit for upload.wikimedia.org is OPTIONAL, as a temporary bridge only.
   - The mirror is PLAN ONLY. No copying or uploads until Eric's YES.
Everything else is unchanged. Still PLAN ONLY, through the normal cycle.

---
## AMENDMENT - IMAGE SOURCE ORDER (Eric typed, 4:58 PM ET 4 Nov 2026) - applies to NET-777 Fix 1 and NET-780(c)
1. FIRST use OUR OWN consolidated images from the recent image scrub, matched by coin:
   - the GCS image consolidation and dedupe buckets
   - the laptop image folders
2. ONLY for images still missing, mirror Wikimedia/NNC into our own storage, keeping the license and credit for each image.
3. The plan must report REAL counts, no guesses:
   - how many are matched from our own images
   - how many still need a mirror
   - how many have no source
4. PII GATE: nothing from AJ's personal photos or receipts goes to the public catalog without passing the PII gate. Use only generic coin images, with no reference to any user.
PLAN ONLY.
