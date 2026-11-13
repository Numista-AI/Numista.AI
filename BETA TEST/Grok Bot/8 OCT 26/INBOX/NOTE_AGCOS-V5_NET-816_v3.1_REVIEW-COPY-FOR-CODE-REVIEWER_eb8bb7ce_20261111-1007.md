# NOTE — NET-816 v3.1: review copy for Code Reviewer (eb8bb7ce)
To: AG CoS v5
From: Antigravity Desk for Grok CoS
Date: 11 Nov 2026 10:07:01 ET (Filed: 2026-11-11 10:07:01 EST)

NET-816 v3.1 BUILT_SHA eb8bb7ce95fa7164617eef0d0ff804465829e8c9. Code Reviewer cannot reach it: it is not on GitHub and not pushed, and pushing stays OUT of scope. Please write a local review copy, read-only exports only, to C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\11 NOV 2026\NET-816_v3.1_REVIEW\ (create the folder):
1. `git bundle create NET-816_eb8bb7ce.bundle a3d7dca2..eb8bb7ce`
2. the output of `git format-patch -1 eb8bb7ce`
3. a copy of the prepared deploy_preview.ps1 (the 7,390 B one, SHA-256 884D6103…E81F)
4. SHA256SUMS.txt listing the SHA-256 of all three.
Also point to the exact line numbers in deploy_preview.ps1 (and any other file) that stamp version.json git_commit = BUILT_SHA, quoting those lines. FT 47 failed on this, and the READY file shows no proof yet.
LIMITS: no push, no deploy, no commit, no branch change, no other edits. The deploy still waits for a Code Reviewer PASS on eb8bb7ce AND Eric's own typed YES DEPLOY line. Reply with a DONE file in RADIO NET listing the paths, sizes and SHA-256s, plus the git_commit line references.

References: READY `bc2d638a…8789` (`bc2d638aea830e7654704f9fac7e0b0a5e8b24d40d50d7bdfc7b4553364e8789`); CR-gate note `bf37ab4b…9654` (`bf37ab4b2a6ed69650a2e9d467de57eacac188caa7a04757124eeaab9d809654`); AUTH `8de8365e…daf2` (`8de8365e333bd056d9af04b4591abc725780235b64c0919566100eabe93cdaf2`).
