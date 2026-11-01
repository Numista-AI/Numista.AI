# COS SCORE - NET-706 R3 META-AD PRE-LAUNCH PLAN - 93/100 REVISE
Scorer: Grok CoS | Mode: docs-only, read-only verification | Plan: RADIO NET\PRELAUNCH_PLAN_NET-706_R3_META-AD_20261101.md (baton NET-714, radio NET-715) | 2026-11-01 4:25 PM ET

## Verdict: 93/100 REVISE (one must-fix). Argon's 100 PASS is not accepted.
Argon said privacy_screen.dart:137-152 was "verified" but missed what those lines actually say. The plan's privacy change would leave a direct contradiction in the live policy.

## What I verified (origin/dev 32d4b42e, origin/main 9f04550a)
- Pixel snippet: byte-identical to the spec block (ceq True). There is exactly one pixel block, and the domain tag 1lgf1v2gv2hhm69pdmix1rp4k2pg4l appears once.
- Live HEAD checks: /us-coins 404; /zzz-unknown?utm_source=meta 404; /?utm_source=meta&fbclid=abc 200; /pricing?utm_source=meta&fbclid=abc 200, no redirect.
- No invented content found: snapshot_legacy, max_items, prod_copper* SKUs and a 2026-11-27 cutoff all return zero hits.
- tier_gatekeeper.py: "free": 20 at :42; cutoff at :136/145/149 = 2026-11-26T05:00Z. Correct.
- Prices: all 13 v3.2 prices are correct.
- verify-session and success_url are labeled [NEW WORK]. TEST-11 uses session_id.
- firebase.json: /privacy is on line 66, /terms on 70, /claim on 126/130, and rewrites end at 133. The ranges are broadly correct.

## R-items re-verified
MF1-MF5 resolved, except the privacy-copy integration (see MF-A). SF-A, SF-B and SF-C resolved, with one minor note (SF-D).

## MUST-FIX
MF-A. The privacy change contradicts existing policy text, and the plan doesn't address it.
- privacy_screen.dart:139 (inside the 137-152 range the plan cites) says: "No data is shared with third-party advertisers."
- web/privacy.html:325 says: "We do not sell, rent, trade, or share your personal data with third-party advertisers or marketers."
- The Meta Pixel sends event data to Meta. Adding the approved Meta/Dataset sentence while leaving these lines unchanged would publish a self-contradicting policy on the pages Meta reviewers and users will read.
- Fix: in both files, EXTEND the existing Section 4 / Section 3-4 text. Do not add a new section. Reword the "third-party advertisers" sentence so it fits the approved Meta Pixel disclosure. Keep "We do not sell, rent, or trade" as is; it already exists, so the [ERIC DECISION] non-sale pledge on plan line 277 duplicates it and should be dropped.
- Cite exact before/after lines: privacy_screen.dart:139 and privacy.html:325.
- No home-address collection anywhere (NET-714A).

## SHOULD-FIX
SF-D. Section 4.2 lists the 73-124 range as containing /app, /blog and /attorney. /app and /blog are rewrites outside 73-124, and there is no /attorney rewrite (it is /attorney_portal on line 122). The range also leaves out /, /index.html and /wishlist(/**). List the actual sources or drop the list.

## Binding Eric decisions (NET-714A, typed 4:02 PM ET), not defects
1. The privacy line is approved; no home-address collection.
2. The Legacy cutoff is 2026-11-26T05:00Z.
3. The Free-tier full export is $95.94.
The R4 plan should remove the three [ERIC DECISION] markers and state these as settled.

## Score breakdown
Accuracy/no invention 30/30 | Pixel and 404/UTM 20/20 | Pricing and tiers 15/15 | Privacy integration 10/15 (MF-A) | Line citations 8/10 (SF-D) | Test plan 10/10 = 93.
Not ready for SAG. Next: NET-716 fix-only R4.
