# SAG Paste Packet — NET-627 FT FAIL → FAIL-FIX (post Plan.v3 EXECUTE)

**Paste this whole note into Stand Alone Grok.** Reply here with SAG’s GO / CONDITIONAL GO / HOLD + any mandatory coding locks for the FAIL-FIX plan (AG writing Plan.v1 FAIL-FIX now as NET-628; then Argon → GB → you → Eric YES → preview EXECUTE).

---

## Ask Stand Alone Grok

You are the independent reviewer for Numista.Ai Mint B− work. Plan.v3 already shipped to **preview only** after your **92 GO** and Eric’s typed YES. Field Tester then ran the locked checklist and **OVERALL FAILED**. We need your read on what FAIL-FIX must cover before another preview build.

### What already happened (locked facts)
- **Chain:** AG Plan.v3 → Argon 94 GO (IG-1..3) → GB CoS 93 → SAG 92 GO → Eric YES → EXECUTE preview `p7-gate` only
- **Build:** Hosting https://numista-vault--p7-gate-8avtpz22.web.app (fea58d8f) · Cloud Run `numista-backend-00497-xej` tag `p7gate` (0% prod) · SHA `751a4305` on `origin/dev`
- **Account tested:** grokbot@numista.ai only · **live/main never opened** · production still on `00494-rew`
- **Founder loop:** FT before Eric retest — Eric was told **not** to test yet
- **Now:** Desk NET-628 woke AG CoS for FAIL-FIX **Plan.v1 WRITE ONLY** (no code / no EXECUTE)

### Field Tester BLUF — OVERALL FAIL (2026-10-27 ~5:18 PM ET)

**Two P0 FAIL-the-build gates missed:**

1. **I-07 / PM-01 (images + valuations after Commit)**  
   After Commit, new **26RJ** still shows **Valuation Pending** / Est. **$0.00** / **Image unavailable** (~3 min wait). Detail screen same. Pre-existing grokbot 26RJ also had no photo.  
   SAG2 was only **PARTIAL**: Theme stamped + Condition Uncirculated, but **images not filled**.

2. **I-04b (Fee / S&H)**  
   **26SQRP** Hub **Fee $0.00** with invoice S&H **$9.95** (expected Fee **$9.95**).  
   Same build: **26RJ Unc Set Hub Fee $9.95 PASS** — fee path works for 26RJ set but fails on 26SQRP pack/roll (qty25).

### What PASSED (do not regress)
- Smoke, Invoice #, I-04c Edit-cancel, I-05 Select All, I-06 Commit
- **I-08 / SAG1 duplicate amber PASS** (SKU 26RJ already in collection; left uncommitted)
- Theme stamped + Condition Uncirculated on 26RJ (enrichment partial)
- SAG3 cream + dark text OK where checked
- SAG4: 20-coin wrapped grid, no clip (all placeholders because images missing)

### How images + Greysheet valuation are *supposed* to get onto a coin (explain this in your locks)

Eric wants FAIL-FIX grounded in the **normal trigger model**, not a one-off patch. Today’s intended stack (from Plan.v2 Bucket 2 + live add paths):

**A. Mint invoice → Review Hub → Commit (the path that just failed)**  
1. **On parse / queue enrich:** `enrich_us_mint_item` (US Mint product catalog) fill-missing-only stamps `image_url_obverse` / `image_url_reverse`, `issue_price`, set flags, theme/series when the SKU matches `US_MINT_PRODUCT_CATALOG` (IG-2 / 26RJ catalog row).  
2. **On `/api/review/commit`:** must (a) run `enrich_us_mint_item` again before vault write, (b) if still no est value, set an immediate **US Mint issue-price / cost baseline** so the card is never stuck on `$0` / `—`, (c) set `enrichment_status` appropriately, (d) **kick an async enrichment worker** for the committed IDs to deepen values (CPG/Greysheet where mappable) and resolve reference images.  
3. **UI:** My Collection shows **“Valuation Pending”** when `valueText == '—'` or `enrichment_status == 'pending'`. It prefers `cpg_value` / Greysheet retail, then `ai_est_value`. Images come from owner photos first, else catalog / `coin_image_service` Mint product art (26RJ, 23RH, 26SQRP, etc.).

**B. Greysheet search specifically (market guide)**  
- Triggered when a coin has enough identity to map: **year + denomination + series/theme + mint** (and is a U.S. coin, not a non-coin `item_type`).  
- Normal call sites: (1) **Morgan / conversational add** does a **synchronous Greysheet resolve** (~1000ms timeout) then falls back to US Mint issue price, else honest Pending; (2) **`POST /api/greysheet/resolve`** for on-demand resolve by Firestore id or raw fields; (3) **post-commit / collection “Fetch Values & AI Images”** (I-11/I-12) should enqueue the same resolve for pending/$0 vault coins.  
- Greysheet writes `greysheetGsid`, bid/ask, and drives `cpg_value` when matched. **Sets/rolls often do not map cleanly to a Greysheet collectible** — for those, the **catalog issue-price baseline + Mint product images** are the correct first-line fill; Greysheet is for individual coins once identity is complete.  
- Guardrails: skip non-U.S. / non-coin; prefer cached GSID if validate_match passes; never invent a fake $0.50.

**C. Manual / other image paths (not the Mint-commit default)**  
- User upload / camera / slab / binder page → own photo URLs.  
- Add-by-cert / PCGS paths → cert imagery + their own enrich.  
- Collection CTA **“Fetch Values & AI Images”** (replacing estate-blocking “Generate AI Report”) → collection-wide retry for pending/$0 items.

**What FT implies went wrong on 26RJ:** Theme/Condition stamped (partial enrich ran) but **image URLs and a non-zero value never landed on the vault doc after Commit**, and no Greysheet/baseline fill rescued it within ~3 minutes — so either commit skipped baseline + async kick, catalog image copy didn’t stick through fill-missing guards, and/or Greysheet was never invoked (or correctly skipped as a set) without the Mint baseline fallback.

### Standing locks still in force
- Preview `p7-gate` only until FT PASS + Eric typed YES for live
- Plan cycle for FAIL-FIX: **AG Plan → Argon → GB CoS → SAG → Eric YES → EXECUTE** (max 4 plan rounds)
- Single duplicate engine; fill-missing-only catalog (never overwrite non-blank collector fields)
- Day/night: Mint FAIL-FIX daytime/testable; NET-610 Option B ≤$5 overnight 8 PM ET separate
- origin/main LOCKED

### What we need from you
1. Confirm these two P0s are the correct FAIL-FIX scope (or add/remove with pinpoint reasons)
2. Mandatory coding locks grounded in the trigger model above — especially: commit must baseline + kick enrich; when Greysheet should/shouldn’t run for 26RJ set vs 26SQRP roll; why images didn’t copy despite IG-2; why 26SQRP Fee=$0 while 26RJ Fee=$9.95
3. Retest proofs before founder: (a) 26RJ after Commit = image + non-zero val (baseline OK if Greysheet N/A for set), (b) 26SQRP Hub Fee = $9.95, (c) prior PASS items stay green (dup amber + 26RJ Fee)
4. Score this FAIL-FIX brief /100 and **GO | CONDITIONAL GO | HOLD** for AG Plan.v1 FAIL-FIX
5. Explicit: **NO EXECUTE / NO founder retest** until FAIL-FIX plan cycle + preview + FT PASS. **Do not authorize live/main.**
