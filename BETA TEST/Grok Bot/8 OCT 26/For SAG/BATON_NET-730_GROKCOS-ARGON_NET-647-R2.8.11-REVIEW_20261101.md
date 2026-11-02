# BATON NET-730 — GROK COS & ARGON — NET-647 R2.8.11 MINT FAIL-FIX PLAN REVIEW
**Date / Time:** 2026-11-01 19:55 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.11_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.11_20261101.md)  
**Status:** ACTIVE REVIEW BATON (Scoring threshold: >= 95 PASS required for Gate 2/3 Founder Eric typed YES)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments.  
**Locks:** `origin/main 9f04550a`, `origin/dev 32d4b42e`, Stripe OFF. Live site HTTP 200 OK.  

---

### Instructions for Grok CoS / Argon:
1. Verify all 4 Must-Fixes (`MF-A` through `MF-D`) and Should-Fixes from `COS_SCORE_NET-647_R2.8.10_77_REVISE_20261101-1930EST.md` / `COS_SCORE_NET-647-R2.8.10_84_REVISE_20261101-1921EST.md` / `GEMINI38_REVIEW_NET-647_R2.8.10_2026-11-01.md`:
   - `MF-A`: Section 7 verbatim code citations (7.1–7.5) against `origin/dev 32d4b42e`.
   - `MF-B`: Row 10 user microscope photo guard (`hasUserUploadedPhotos`) returns `null` so user photos are preserved.
   - `MF-C`: Gate 4 automated script asserts HTTP 200, `image/webp`, byte size, and `x-goog-hash` MD5.
   - `MF-D`: Matrix & 4.1.1 reconciliations (dime reverse MD5, Row 10 doc ID, Row 11 doc ID + MD5s, Row 03 fixture, 23RH live composites).
   - Should-Fixes & Nits: `'Program / Series'` key handling, stray fence removal, dev tip `32d4b42e`, Row 18 proof fallback note, footer `**END PLAN R2.8.11**`.
2. File score and radio broadcast.
3. Upon dual $\ge 95/100$ PASS, stage plan in `For SAG/` for Founder Eric morning typed `YES`.
