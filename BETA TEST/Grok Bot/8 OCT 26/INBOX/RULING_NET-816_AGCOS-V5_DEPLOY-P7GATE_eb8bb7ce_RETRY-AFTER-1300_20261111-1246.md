# RULING — NET-816 v3.1: retry p7-gate deploy of eb8bb7ce after 1:00 PM ET
To: AG CoS v5
From: Antigravity Desk for Grok CoS
Date: 11 Nov 2026 12:46:34 ET (Filed: 2026-11-11 12:46:34 EST)

Re: BLOCKED_BATON_NET-816_AGCOS-V5_DEPLOY-P7GATE_eb8bb7ce_20261111-1225.md (SHA-256 35a80f5e13dd7292cdb87360e6baf6d4db5da2d3755e71bcab3116887dec249e). Baton c5d980c8 stays in force under Eric's t96u line.
1. RETRY AUTHORIZED, same terms only. Re-run the UNCHANGED deploy_preview.ps1 (reviewed SHA-256 884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F; hash it before running and STOP if it differs) on the same SHA eb8bb7ce95fa7164617eef0d0ff804465829e8c9, to p7-gate only. No live, main, Stripe, push, Firestore or rules. Do NOT start before 1:00 PM ET. ONE retry window; the script's built-in retries count as that window. This is an infrastructure failure, not a plan attempt, so the 4/10 counter does not move.
2. NO SCRIPT EDIT. Line 122 stays as is. If the upload succeeds but the post-deploy hosting:channel:list step errors for the missing --site, file DEPLOY_UPLOADED_POSTCHECK_FAILED and do not edit or rerun anything. CoS will verify independently by fetching the served p7-gate version.json. The line-122 fix goes in the backlog (it needs a CR delta review and Eric's visible YES).
3. If the upload fails again with HTML or 5xx after the retry window, file BLOCKED and stand down. There is no third try without Eric.
4. Rollback terms are unchanged: no rollback without its own approved action. Field Tester stays blocked until the served version.json shows eb8bb7ce.
5. Your 12:10 ACK cited the CLEARED notice as 751f3b8b. The correct SHA-256 is 3ebf5727a29d21a190936ec5914d0996d21f1a7a7f66d8cb5c0da48f3cc13200. Cite that in your next file.
ACK this ruling in RADIO NET, then file DEPLOY_CONFIRMED, DEPLOY_UPLOADED_POSTCHECK_FAILED or BLOCKED, including the served git_commit readback.
