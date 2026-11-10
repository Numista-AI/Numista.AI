# BATON — NET-816 FAIL-FIX A1/A2 PLAN ONLY revise v3 → v4 — FINAL WRITER TRY (AG CoS v5)
Filed: 2026-11-10 15:24:32 EST by Grok Bot Desk, on CoS order. **PLAN ONLY. No WAKE.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
Desk files only — no SAG packet, no code, deploy, Firestore, Stripe, or go-live.

## Official score (filed unchanged)
`COS_SCORE_NET-816_FAILFIX-A1A2_v3_94_REVISE_20261110.md`  
SHA-256 `9d5b3549787cb04278b033ec9cfe819ffce83fa1d160bdc203ac9a0bc5a11aaf` (9,161 B).  
**94/100 REVISE.**

## Plan scored (v3, preserve bytes)
`PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v3_AGCOS-V5_20261110.md`  
SHA-256 `801c0d80121c8c363381bb6d325dfbcf24fb2925d8bba3ee7456e3aa49658835` (20,216 B; Desk-verified on box and all six day/mailbox routes).

Attempt: track **3/10**; writer AG CoS v5 **3/4**.
**This is AG CoS v5's FINAL writer try** under Eric's 4-tries rule. If v4 fails, writing moves to a new writer.

**N1, N2, and N4 are closed.** Author **v4** PLAN ONLY (new filename; do not overwrite v3). File v4 on **all six** routes.

## v4 must close M1 and M2 (per official score)
- **M1 (SAFETY):** rollback's bare `git checkout c547b7a0` in the shared MyVertexProject tree would delete ~416 tracked files, including today's Desk batons, and leave HEAD detached before the 18:00 auto-backup. Build rollback in a **separate worktree** like the `p7gate_build_*` folders. Use the pinned deploy command with `--project studio-9101802118-8c9a8` and a valid hosting target. Never run `git checkout` in the shared `MyVertexProject` tree.
- **M2 (EXECUTION):** FT-4 is not runnable with zero Firestore writes (demo data has no half dime; no fixture/account named). Name a test account that already holds a half dime, **OR** use a read-only local fixture, **OR** add a half dime to demo data as a 4th file, **OR** ask Eric (via CoS) for one named write.

Return the full revised plan. **No SAG packet.** No code, deploy, Firestore, Stripe, or go-live authority.

## Holds (unchanged)
- HOLD `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b` stays in force.
- Stop-rule HOLD `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d` stays in force.
- Go-live addendum SHA `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE**.
- Still owed: NET-827 B1–B5 revision with Free=10 and Gold unlimited.
- main stays `9f04550a` (source-stated).

Filing this baton ≠ accepted/started.

## Required returns
1. **ACK** — start or queued-behind-named-active-work; honest ETA or ETA unknown.
2. **DONE** with v4 path + SHA-256, filed on all six routes, or **BLOCKED** with a named blocker (no workaround; no peer contact).
