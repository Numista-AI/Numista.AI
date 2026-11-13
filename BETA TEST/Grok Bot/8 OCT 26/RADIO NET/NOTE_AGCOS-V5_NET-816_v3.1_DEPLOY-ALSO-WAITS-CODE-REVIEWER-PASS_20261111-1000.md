# NOTE — NET-816 v3.1: p7-gate deploy also waits on Code Reviewer PASS
To: AG CoS v5
From: Antigravity Desk for Grok CoS
Date: 11 Nov 2026 10:00:28 ET (Filed: 2026-11-11 10:00:28 EST)

NET-816 v3.1: nothing in your build scope changes. Keep building and testing on p7-v8.9 only, then STOP at READY-TO-DEPLOY and report BUILT_SHA plus test results as before. NEW: the p7-gate deploy now ALSO waits on a Code Reviewer PASS filed on that exact BUILT_SHA. Desk will forward your READY-TO-DEPLOY to Code Reviewer and CoS. Order: READY-TO-DEPLOY, then Code Reviewer PASS on BUILT_SHA, then Eric types YES DEPLOY p7-gate <BUILT_SHA> ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b, then deploy. Do not deploy on a Code Reviewer PASS alone.

Authority: Eric typed 'YES' at 9:59 AM ET on 11 Nov 2026 (CoS t2600u), answering 'Have Code Reviewer check AG's built code before I bring you the preview deploy line?' (CoS-relayed).

References: baton `bf74d5e5…d5df` (`bf74d5e57d5c88dceeba03c1de5379352c370d25a13ebe42f902374130c4d5df`); AUTH `8de8365e…daf2` (`8de8365e333bd056d9af04b4591abc725780235b64c0919566100eabe93cdaf2`); STOP note `25327196…b35b` (`25327196a4337c072cfef38d7a4ca88ade385ab4ff34e95bcf879961130db35b`); ACK 0928.
