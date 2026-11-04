# BATON NET-780 - FAILFIX PLAN v1 (PLAN ONLY) - NET-748 v5 failed Field Tester on p7-gate
To: AG CoS v4   From: Antigravity Desk (for GB CoS)   4 Nov 2026 4:58 PM ET
QUEUE: after NET-778 (Plan C). Write it together with NET-777 (the catalog FAILFIX), because the two share the image fix.

FT result: OVERALL FAIL. Screenshots: RADIO NET\shots_net748.tar.gz

Plan these fixes:
a. Build stamp: /version.json has no git_commit, so c294fd3c can't be verified. Add git_commit plus the build time to version.json at build.
b. The 2026 American Eagle One... card and the 2023-D 5c card show broken images, and the AE price shows 'Pending'. Find the root cause per card.
c. 196 console errors: CSP connect-src blocks upload.wikimedia.org, thumb.wikimedia.org and numismatics.org. This is the SAME root cause as the catalog. Fold it into NET-777's image mirror approach (one-time copy to our own storage with license and attribution, served from our domain), so ONE fix covers both. The CSP edit is only an optional temporary bridge.
d. The splash screen takes about 40 seconds. Measure it and propose a fix with a target time.

Output: INBOX\FAILFIX_PLAN_NET-780_NET-748_v1.md. Quote only from real files with real line numbers, and add a test step for each fix.
Review cycle: Argon, then GB CoS 95+, then SAG, then Eric's typed YES. PLAN ONLY.

HOLD: the Step 1b live rules deploy and the SKU dictionary seed. Do NOT do them.
Locks: no Firestore, main stays 9f04550a, Stripe stays OFF.

---
## AMENDMENT - SPLIT (Eric typed, 4:58 PM ET 4 Nov 2026, per his cap rule)
NET-780 is now 4 SMALL tasks. Each gets its OWN plan and its own review cycle:
- NET-780a: build stamp (git_commit and build time in /version.json). Output: FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md
- NET-780b: the 2 broken cards (2026 AE One..., 2023-D 5c) and AE 'Pending'. Output: FAILFIX_PLAN_NET-780b_CARDS_v1.md
- NET-780c: images and CSP, using the IMAGE SOURCE ORDER below, shared with NET-777. Output: FAILFIX_PLAN_NET-780c_IMAGES_v1.md
- NET-780d: the 40-second splash. Output: FAILFIX_PLAN_NET-780d_SPLASH_v1.md
PLAN ONLY. The rules deploy and SKU seed stay on HOLD.
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
