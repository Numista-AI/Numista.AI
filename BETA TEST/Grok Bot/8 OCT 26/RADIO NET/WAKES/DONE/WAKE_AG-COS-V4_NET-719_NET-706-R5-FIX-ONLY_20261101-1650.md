# WAKE - AG CoS v4 - NET-719 - NET-706 R5 FIX-ONLY
From: Grok CoS | 2026-11-01 4:46 PM ET | Docs only. Do not commit code, push or deploy.
R4 scored 92 REVISE (COS_SCORE_NET-706-R4_92_REVISE_20261101-1650EST.md). Produce RADIO NET\PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md and change ONLY:
1. MF-B: Section 7.2. BEFORE must match privacy_screen.dart:139 byte-for-byte (it has Cloud\'s). In AFTER, escape every apostrophe as \' (collection\'s, Cloud\'s) so it compiles.
2. MF-C: Section 7.3. In the privacy.html:325 AFTER, change "We do not sell, rent, trade, or share your personal data or coin collection details with third parties." to "We do not sell, rent, or trade your personal data or coin collection details to third parties." Keep the rest.
3. SF-E: Section 4.2. Use the real firebase.json line numbers listed in the COS_SCORE (each is +2 from R4; /app 23, /blog 28, plus /signin 33, /forgot 38, /reset 43), or cite the block range only.
Change nothing else. File the plan, a radio note, then BATON_NET-719 for review. Queue after this: NET-718 security plan, then NET-647 R2.8.10, then NET-705.
