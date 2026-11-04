# BATON NET-768 - EXECUTE NET-747 Catalog Browse v5
To: AG CoS v4 Work (ba2bfdb2)   From: Antigravity Desk   4 Nov 2026 12:15 PM ET

AUTHORITY: Eric typed in the GB CoS chat at 12:07 PM ET on 4 Nov 2026: "Yes, except for #5. I want it live, so that Social Media can include a link to it in it's social media posts."
Plan: INBOX\AG_PLAN_NET-747_CATALOG-BROWSE_v5.md (MD5 81F888FD...). Scores: Argon 97, GB CoS 95, SAG 95.

CONDITIONS (all required):
- C1: The Pre-Federal badge is pre_federal==true ONLY, which is 9 records. The 1789 Washington medal does not get it.
- C2: Use ONE builder, ONE validator and ONE input path, with ONE script folder.
- C3: Rename BOUND_12 exactly as listed in section 3.2-3.
- C4: Put no personal-name tokens in code. The only name token is \bAJ\b. Do NOT add "eric".
- C5 (CHANGED by Eric): GO LIVE. Order:
  1. Build.
  2. Pass the validator and the planted-leak (C) gate on preview p7v12.
  3. Deploy the catalog live.
  4. Confirm the live catalog URL returns 200.
- STILL LOCKED: no Firestore rules deploy and no Firestore write without Eric's separate YES. No merge to main (main stays 9f04550a). Stripe stays OFF.
- Fold SAG's 9 should-fixes:
  - Use a single pre-federal rule throughout.
  - Define BOUND_12.
  - Use a real whitelist file path.
  - Use one input path.
  - Use one script folder.
  - Pin Newest at 24.
  - Define the Ask Morgan button.
  - Set the launch date to 27 Nov.
  - Name the public reference_images/ folder.

REPORT: file EXECUTE_DONE_NET-768 (or BLOCKED) in INBOX with:
- the commit and branch
- the validator and C-gate results
- the preview URL
- the LIVE catalog URL with its HTTP status
- the spend
If anything needs Firestore, STOP and file BLOCKED.
