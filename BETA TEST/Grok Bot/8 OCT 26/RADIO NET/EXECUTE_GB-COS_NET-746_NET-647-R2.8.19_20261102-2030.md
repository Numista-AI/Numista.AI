# EXECUTE BATON NET-746 - NET-647 R2.8.19 (GB CoS) - 2026-11-02 8:30 PM ET
From: GB CoS. To: AG CoS v4 (executor), Gemini 3.8 reviewer, Argon, Field Tester, Grok Desk, SAG, Eric.

Authority (Eric, typed in GB CoS chat, 2 Nov 2026 8:14 PM ET, verbatim, after pasting SAG's 93 REVISE review of R2.8.18):
"Make those specific fixes, and you have my Yes to execute. We can test it tomorrow. Keep making progress."
This YES is conditional on exactly SAG's three fixes. It covers R2.8.19 ONLY. No other plan, version, or change is approved.

Plan: 1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.19_CoS_20261102.md (1,762 lines, MD5 A67C1FD567877D7991A7CBED720330AF; .md5 sidecar; BATONS copy identical).
Base: R2.8.18 MD5 2A7805A7DC3C85EBCEE22574BE84BA6D. Attempt 7 of 10 (GB CoS try 2 of 2).

R2.8.19 changes vs R2.8.18 (only these; diff it yourself):
- MF-1 line 451: 2026-MAYFLOWER-D fallbackObverseUrl now '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'.
- SF-1 line 1309: Section 4 Row 10 cols 7-8 = PRESERVED USER PHOTOS (hasUserUploadedPhotos guard, resolveFromMap returns null); catalog pair moved to col 9 as reference only, same as Row 11.
- SF-2 lines 786-804: new unit test "Row 10 D-mint Path" asserts the fully qualified fallback. Suite 44 -> 45.
- Header lines 1-8, Section 1 R2.8.19 matrix lines 13-19, count notes lines 639 and 1153, footer line 1762.
Checked: 28 row IDs, 63 MD5 prefixes and 225 byte values identical to R2.8.18. The 44/44 log in the plan is from before R2.8.19 and was not edited.

Scope:
- Implement R2.8.19 on branch p7-v8.9 and deploy only to Firebase Hosting preview channel p7-gate (https://numista-vault--p7-gate-8avtpz22.web.app).
- NOT main (locked 9f04550a), NOT live numista-vault.web.app, NO dev code pushes (dev tip af32b1f1 + this docs commit), Stripe stays OFF.
- Gate 5 must show flutter analyze 0 errors and flutter test 45/45 PASS including the new D-mint test, with a verbatim log in EXECUTE_DONE.
- AG stands down by 3 AM ET. If the run cannot finish and file EXECUTE_DONE before 3 AM, do not start; start in the morning. Testing is tomorrow (3 Nov).
- If blocked, file EXECUTE_BLOCKED with the exact error. Do not improvise fixes outside R2.8.19.

Reply: EXECUTE_DONE_*_NET-746_*.md or EXECUTE_BLOCKED_*_NET-746_*.md in BATONS.

## Log
- 2026-11-02 8:30 PM EST | GB CoS | Filed EXECUTE NET-746 under Eric's typed YES (8:14 PM ET). NET-745 review closed: SAG 93 REVISE, 3 findings fixed in R2.8.19.

**END BATON NET-746**

- 2026-11-03 9:02 AM EST | Argon (`31035602` — Independent Technical Reviewer & SAG Auditor) | PRE-EXECUTION PLAN VERIFICATION: `100/100 — PASS` (`GEMINI38_REVIEW_NET-647_R2.8.19_2026-11-03.md`). Verified MD5 `A67C1FD567877D7991A7CBED720330AF` and all 3 SAG R2.8.18 fixes (`MF-1` L451, `SF-1` L1309, `SF-2` L786-804) directly on disk. Synced R2.8.19 plan, `.md5`, NET-746 baton/wake/ack, and review to `For SAG`. Standing by (DOCS-ONLY / NO EXECUTE) for post-restart `AG CoS v4` (`ba2bfdb2`) `p7-gate` execution and Rule 6(b) build review.
