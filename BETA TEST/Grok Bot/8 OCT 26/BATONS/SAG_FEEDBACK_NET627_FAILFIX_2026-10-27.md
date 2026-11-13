# SAG Feedback — NET-627 FAIL-FIX brief (pre Plan.v1)

- **Reviewer:** Stand Alone Grok (SAG)
- **DTG:** 2026-10-27 ~5:29 PM ET (America/New_York)
- **Inputs:** SAG_PASTE_PACKET_NET627_FAILFIX (FT FAIL + image/Greysheet trigger model)
- **Chain next:** AG Plan.v1 FAIL-FIX → Argon → GB CoS → SAG → Eric YES → EXECUTE preview only

---

## BLUF

**88 / 100 — CONDITIONAL GO** for AG to write FAIL-FIX Plan.v1. Two P0s correctly scoped. No Plan.v4 if locks below are in coding/EXECUTE brief.

---

## 1. P0 scope — confirmed

1. **I-07 / PM-01** — 26RJ post-Commit: no image + stuck $0 / Valuation Pending. Partial enrich (Theme+Condition) ran; image URLs + non-zero baseline never landed.
2. **I-04b** — 26SQRP Fee $0.00 vs invoice S&H $9.95; same build 26RJ Fee $9.95 PASS — pack/roll-specific, preserve set fee path.

Do not expand scope. Prior PASS items must stay green.

## 2. Mandatory coding locks

**On `/api/review/commit`:**
- Re-run `enrich_us_mint_item` (fill-missing-only) before vault write.
- If no market value after enrich → stamp baseline from catalog `issue_price` (or item cost); set `enrichment_status`.
- Kick async enrichment worker for committed IDs (Greysheet where mappable + reference images).
- Sets/rolls (26RJ, 26SQRP): Greysheet expected miss/skip; catalog issue-price + Mint product images = first-line. Do not wait for Greysheet.

**Images:**
- Confirm 26RJ catalog row has usable `image_url_obverse` / `image_url_reverse`; fill-missing copy must write before vault persist.
- If catalog missing URLs → complete catalog entry in this FAIL-FIX.
- Post-commit vault doc must have image URLs (or owner-photo fallback). “Image unavailable” after catalog match = wiring failure.

**Fee (26SQRP vs 26RJ):**
- Preserve 26RJ Fee $9.95 path.
- Pack/roll (qty>1 / from_set / pack-expanded): Hub Fee must reflect allocated/parent S&H when item should surface shipping. Do not zero display fee on rolls when invoice has non-zero S&H.
- Dual-write/read `shipping_fee` / `shipping_amount` / `allocated_fees` consistent for sets and rolls.

**Do not regress:** IG-1 dual-write dup amber; fill-missing-only; Theme/Condition; contrast; 20-coin wrap.

## 3. Retest proofs before founder

- (a) Commit new 26RJ → image + non-zero val (issue-price baseline OK if Greysheet N/A). No Pending/$0/Image unavailable.
- (b) 26SQRP Hub Fee = $9.95.
- (c) Prior PASS green: dup amber second 26RJ, 26RJ Fee $9.95, contrast, wrap.
- Firestore dump of committed 26RJ vault doc + 26SQRP Hub row in FT package.

## 4. Score note

Loses points only because exact failure point (missing catalog URLs vs copy skipped vs baseline omitted vs async never kicked) and 26SQRP fee root cause are still diagnostic — acceptable for Plan.v1 write; must be resolved in plan and proven next FT.

AG may write Plan.v1. Lock constraints into EXECUTE brief. No extra plan round unless next FT fails a P0.

## 5. Explicit locks

**NO EXECUTE / NO founder retest** until AG→Argon→GB→SAG + preview + FT PASS on both P0s + regressions.  
**Do not authorize live/main.** origin/main LOCKED. Preview `p7-gate` only.
