# WAKE - AG CoS v4 - NET-716 - NET-706 R4 FIX-ONLY
From: Grok CoS | 2026-11-01 4:25 PM ET | Docs only. Do not commit, push or deploy.
R3 scored 93 REVISE (COS_SCORE_NET-706-R3_93_REVISE_20261101-1625EST.md). Produce RADIO NET\PRELAUNCH_PLAN_NET-706_R4_META-AD_20261101.md and change ONLY the following:
1. MF-A: In Section 7, extend the existing text; do not duplicate it.
   - Reword privacy_screen.dart:139 ("No data is shared with third-party advertisers.") and web/privacy.html:325 ("...share your personal data with third-party advertisers or marketers") so they are consistent with the approved Meta Pixel/Dataset sentence. Show exact before/after for each line.
   - Drop the duplicate non-sale pledge (plan line 277); "We do not sell, rent, or trade" already exists.
   - No home-address collection.
2. SF-D: In Section 4.2, fix the firebase.json route list. /app and /blog are outside 73-124; there is no /attorney (it is /attorney_portal :122); add /, /index.html and /wishlist(/**).
3. Replace the three [ERIC DECISION] markers with the settled NET-714A decisions: privacy line approved, no home address; cutoff 2026-11-26T05:00Z; Free export $95.94.
Change nothing else. The pixel block must remain byte-identical. File the plan, then a radio note, then BATON_NET-716 for review.
