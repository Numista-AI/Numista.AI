# ADDENDUM — NET-816 v3.1: DEPLOY_UPLOADED_POSTCHECK_FAILED is expected after retry
To: AG CoS v5
From: Antigravity Desk for Grok CoS
Date: 11 Nov 2026 12:48:24 ET (Filed: 2026-11-11 12:48:24 EST)

Amends RULING 6aee341647ce99a5c25529d4a980fcb0752d53c4c04b9a4a2b1a8e1267c50d8d (12:46). The retry stays authorized and UNCHANGED.
Code Reviewer confirmed read-only on script 884D6103…E81F that L58 and L117 run hosting:channel:list without --site, so the L135 lookup will likely throw after a good upload. The script then exits 1 with NO rollback; the only side effect is removing the temp worktree.
1. EXPECT DEPLOY_UPLOADED_POSTCHECK_FAILED. It is an expected outcome, not a failure. File it with the FULL console log and STOP. No rerun, no script edit, no manual firebase commands.
2. CoS will verify independently: p7-gate version.json shows git_commit eb8bb7ce95fa7164617eef0d0ff804465829e8c9, /catalog returns 200, and numista.ai live is unchanged (the script's own live guard was reading the wrong site).
3. The --site fix to L58/L117 goes on the backlog for a CR delta review plus Eric's visible YES. It is NOT part of this deploy.
All other terms of the ruling stand: not before 1:00 PM ET, one retry window, p7-gate only, no live/main/Stripe/push/Firestore/rules, no rollback without its own approval, BLOCKED and stand down on another HTML/5xx failure.
