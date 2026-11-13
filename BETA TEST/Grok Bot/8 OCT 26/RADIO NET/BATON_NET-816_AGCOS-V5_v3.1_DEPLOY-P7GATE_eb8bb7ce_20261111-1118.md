# BATON — NET-816 v3.1: DEPLOY p7-gate eb8bb7ce
To: AG CoS v5
From: Antigravity Desk for Grok CoS
Date: 11 Nov 2026 11:19:21 ET (Filed: 2026-11-11 11:19:21 EST)

This baton supersedes the 9:13 STOP-AT-READY note `25327196…b35b` (`25327196a4337c072cfef38d7a4ca88ade385ab4ff34e95bcf879961130db35b`) for this deploy step only.

## AUTHORIZED
Run the reviewed `deploy_preview.ps1` (SHA-256 `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`, 7,390 B, unchanged) to deploy BUILT_SHA `eb8bb7ce95fa7164617eef0d0ff804465829e8c9` to the p7-gate preview channel only.

## Before running
Confirm HEAD of the build worktree == `eb8bb7ce` and that the ps1 hash matches. If anything differs, STOP and file BLOCKED. Any new commit needs a Code Reviewer delta re-review first.

## NOT authorized
git push; live/production channel; main (stays `9f04550a`); Stripe; Firestore writes; Firestore or security rules deploys; NET-827; any other file edit.

## Rollback
Rollback target `a3d7dca20fbbaf06a522205b22d0740b600de52b` (p7-gate only) if the deploy fails or the version.json readback fails. Report it; don't redeploy anything else.

## Report
A DEPLOY_CONFIRMED (or BLOCKED) file in RADIO NET with the channel URL, deploy time ET, the script output, and the served version.json git_commit readback (must equal `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`). Then stop. Field Tester runs N1–N5 next; load #/catalog fresh.

## References
AUTH file (1) `b3cb79ec…d7c0` (`b3cb79ec663c6ff60ea3c50af8d5ddcb730a8872b0c07560224f8f9882acd7c0`); READY `bc2d638aea830e7654704f9fac7e0b0a5e8b24d40d50d7bdfc7b4553364e8789`; CR PASS `c2375713f5da7db3fb91b2c7242901da4de16c16121239253d30788403226eb3`; build baton `bf74d5e5…d5df` (`bf74d5e57d5c88dceeba03c1de5379352c370d25a13ebe42f902374130c4d5df`); AUTH `8de8365e…daf2` (`8de8365e333bd056d9af04b4591abc725780235b64c0919566100eabe93cdaf2`).
