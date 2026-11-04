# BATON NET-772 - EXECUTE NET-748 v5 on the p7-gate PREVIEW ONLY
To: AG CoS v4 Work (ba2bfdb2)   From: Antigravity Desk   4 Nov 2026 3:40 PM ET
QUEUE: start only AFTER NET-768 (Catalog Browse live) is DONE.

AUTHORITY: Eric typed at 3:33 PM ET on 4 Nov 2026: "YES, execute NET-748 v5 to p7-gate preview only".
Scores: SAG 96, Argon 96, both with 0 must-fixes.

SCOPE:
1. Follow INBOX\NET-748_v5_PLAN.md, starting with the Step 0 re-read stop. The baseline drift is p7-v8.9 at ca4e3d33.
2. Fold in Argon's 4 implementer notes (INBOX\ARGON_REVIEW_NET-748_v5.md). Pin the preview deploy:
   cd numista_mobile ; firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8
3. Run the LOCAL rules emulator test. If it fails, STOP and file BLOCKED.

NOT AUTHORIZED:
- The Firestore rules deploy. It needs Eric's separate YES naming the folder, the project, the SHA-256 and the rollback.
- Any Firestore write.
- Any merge to main (main stays 9f04550a).
- Stripe (stays OFF).

REPORT: file EXECUTE_DONE_NET-748 (or BLOCKED) in INBOX with:
- the commit and branch
- the emulator result
- the p7-gate URL
- what wasn't tested
