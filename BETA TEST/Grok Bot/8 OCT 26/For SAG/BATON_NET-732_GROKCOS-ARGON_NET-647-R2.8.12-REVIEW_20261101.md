# BATON NET-732 — GROK COS & ARGON — NET-647 R2.8.12 MINT FAIL-FIX PLAN REVIEW
**Date / Time:** 2026-11-01 21:15 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.12_20261101.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.12_20261101.md)  
**Status:** ACTIVE REVIEW BATON (Scoring threshold: >= 95 PASS required for Gate 2/3 Founder Eric typed YES)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments.  
**Locks:** `origin/main 9f04550a`, `origin/dev 32d4b42e`, Stripe OFF. Live site HTTP 200 OK.  

---

### Instructions for Grok CoS / Argon:
1. Verify all 3 Must-Fixes (`MF-1` through `MF-3`) and Should-Fixes from `COS_SCORE_NET-647_R2.8.11_88_REVISE_20261101-2020EST.md`:
   - `MF-1`: Gate 4 Python script now explicitly parses `x-goog-hash` MD5, decodes base64, converts to hex, and asserts match against expected hex MD5 for all 4 staged assets.
   - `MF-2`: Section 1 Resolution Matrix lines 21 & 29 updated (Row 10 doc ID `0172d0ee64284a12a8aa269ce805ec07`; Dime reverse MD5 `8533943d7d88a011adaf372476bfe1f3`).
   - `MF-3`: Gate 6 updated with `origin/dev` tip at `32d4b42e` (catalog at `9b55f3d9`).
   - `SF-1` through `SF-3` & `Nit 1`: Stale version labels updated to R2.8.12; `primaryTitle` reads `'Program / Series'`; Section 7.4 cite updated to 2282-2289; line 8 queue text updated.
2. File score and radio broadcast.
3. Upon dual $\ge 95/100$ PASS, stage plan in `For SAG/` for Founder Eric morning typed `YES`.

---
**Grok CoS part CLOSED 2026-11-01 9:25 PM EST:** scored 92 REVISE (COS_SCORE_NET-647_R2.8.12_92_REVISE_20261101-2125EST.md). Do NOT stage for Eric's YES. Superseded by BATON_NET-733 (AG fix-only R2.8.13).

