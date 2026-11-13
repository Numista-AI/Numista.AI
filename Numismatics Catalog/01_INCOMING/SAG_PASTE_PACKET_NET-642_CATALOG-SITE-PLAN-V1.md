# Stand Alone Grok — Paste Packet: NET-642 Argon Catalog→Site Plan.v1

**One-line ask:** Independently score Argon’s PLAN ONLY for US Numismatics Catalog site integration. Keep full independence from any GB CoS review — do not ask for or assume a GB score.

**DTG packet:** 2026-10-28 ~11:50 AM ET · **Status of subject:** PLAN ONLY — NO EXECUTE / NO FOLD / $0 · **Your role:** independent architecture / security / BF-cut grill.

---

## Board constraints (do not waive)

- `origin/main` **LOCKED**. Mint FAIL-FIX / **NET-641** Day #1 on branch `p7-gate` — catalog plan must **not** steal Mint execute.
- Production fold **HOLD** stack: **586 + 588 + 589 + 590**.
- **NET-640** = afternoon Phase I ≤$60 Discovery-only on `numista-morgan-pilot`, owned by Catalog Research — separate track; **$0** on NET-642.
- Review cycle only: Argon Plan.v1 → GB CoS → **you (SAG)** → founder Qs → Plan.v1.1/v2 if needed → **only then** any EXECUTE ask.
- Eric Seaman is golfing; four product questions are held for his return (listed below). Do not invent founder answers.

---

## Condensed plan summary (1 page)

**Title:** ARGON PLAN.v1 — US Numismatics Catalog Site Integration (1776–2026)  
**Architect:** Argon (AG System Architect / AG CoS) · **Filed:** 2026-10-28 ~11:45 AM ET  
**Full plan filename:** `ARGON_PLAN_V1_US_NUMISMATICS_CATALOG_2026-10-28.md`

**Vision:** Academic-grade reference for every coin, bank note, and medal used on USA territory 1776 → 2026 (Semiquincentennial arc). Priority: **Coins + Bank Notes Phase 1 (before Black Friday 27 Nov 2026)**; **Medals Phase 2 (after BF / Q1 2027)**.

**Data path:** Local staging (`02_STAGED_FOR_GCP` JSONL) → Discovery indexes on `numista-morgan-pilot` (research) → Firestore collection `us_numismatics_catalog` on `studio-9101802118` (production reference DB) → Flutter `numista_mobile` routes `/catalog` and `/catalog/:nac_code`.

**Identity:** Proprietary **NAC1** keys  
`NAC1.<KIND>.<CC>.<CLASS>.<SERIES>.<DATE>.<FAC>.<VAR>.<CHK>`  
(design doc `NAC_CODE_DESIGN_2026-10-28.md` exists under Catalog Research plans).

**Schema sketch (`CatalogItem`):** nac_code, kind CN|BN|MD|TK|ST, country US|PF, denomination_class, series, year, year_display, facility, variety, title, obverse/reverse image URLs + has_* flags, mintage_mint_primary (Tier A), mintage_trade_estimate (Tier B), mintage_proof, specifications{}, historical_authority_citations[], crosswalk{firestore_def_ref_id, smithsonian_id, pcgs_number, ngc_id, friedberg_number}.

**UI:** Master browse grid (year-sorted, Kind/Class/Mint/Series filters, era picker, image-presence filter); dual flippable thumbs with SVG placeholders when missing; NAC chip; Quick Add to Collection/Wishlist; detail screen with zoom dual viewer, citations, “Ask Morgan,” variety sub-table. Camera/Lens icon for visual match called out in browse chrome.

**Auth sketch:** Guest/public browse+search+basic specs; free registered → Add to Collection/Wishlist + export; Pro/subscriber → Discovery/Morgan + hi-res archival.

**Isolation:** Live `numista-vault.web.app` / `origin/main` locked; catalog work on `dev` + Firebase preview channels; code in decoupled `lib/screens/catalog/` + `lib/services/catalog/`.

**BF Phase 1 features claimed:** searchable chronological grid, full-text + faceted filters, dual-sided viewer + placeholders, one-click Add to Collection/Wishlist, “initial 3,000+ verified catalog cards.”  
**Phase 2:** Pre-Federal/colonial, official + private medals, world specie, **visual image search**, advanced Morgan on cards, user image contribution queue.

**Verification named:** `flutter analyze` on catalog paths; widget test; `test_catalog_schema.py`; `git status --porcelain`.

---

## Known technical / product flags to grill

1. Mint filter lists **Dahlonega (D)** and **Denver (D)** — letter collision. NAC design locks Dahlonega as **DD**.
2. Schema `country` only `"US"|"PF"` — if founder includes foreign legal-tender until 1857, enum must expand before Phase 1 ingest.
3. §1 sells **multi-modal / visual** search as a pillar; §7 puts visual search in Phase 2. Phase 1 should be text-only unless justified.
4. **3,000+ cards before BF** is aspirational — gate on Catalog Research throughput + fold HOLD, not a hard count.
5. Firestore: confirm **client read-only** + **admin/batch write only** for `us_numismatics_catalog`.
6. Quick Add: must reuse existing collection-add + auth (REQ_031), not a parallel write.
7. Coin card default face should be the **unique identity side** (e.g. president on Presidential $1), not a shared reverse.
8. Mintage Tier A = **U.S. Mint / Treasury only** — never PCGS/NGC as Tier A.
9. Catalog browse UX should be **desktop/tablet first**; mobile companion ~10%.
10. Philippines INCLUDE (`PF`) and Medals-after-BF are standing founder rules — confirm plan does not contradict.

---

## Four open questions for Eric (held — do not answer for him)

1. Pre-1792 state/colonial coins: group by state, or one “Pre-Federal / Continental” category? *(likely Phase 2 / deferrable)*
2. Include foreign coins legal tender in the US until 1857 (e.g. Spanish 8 Reales), or American issues only? *(schema-blocking)*
3. Collectors submit photos for placeholders, or images stay internal? *(Phase 2 / deferrable)*
4. `/catalog` browse+search fully public (SEO), paid tiers only for AI photo match + values? *(auth/SEO-blocking for Phase 1)*

---

## What SAG should return

1. **Score /100** and verdict: **GO / NO-GO / CONDITIONAL** (pick one).
2. **Must-edits** before any EXECUTE ask (actionable, numbered).
3. **Anything GB CoS (or Argon) likely missed** — architecture, security rules, BF cut realism, Mint isolation, auth, schema traps.
4. Explicit confirmation you treated this as PLAN ONLY (no spend, no code authorize).

**Do not** request or incorporate a GB CoS numeric score. Independence is the point.

---

## Full plan text (inline for paste convenience)

If your context window allows, also open/read the full markdown titled **ARGON PLAN.v1 — US Numismatics Catalog Site Integration (1776 – 2026)** with sections: (1) Executive Summary & Vision, (2) Data Path & Storage Architecture + CatalogItem typescript, (3) UI Surfaces & UX Layout, (4) Auth & Access Gating, (5) Preview vs Main Isolation, (6) Relationship to Existing Coin Cards / Checklists / Mint Catalog, (7) Shipping Roadmap Black Friday Cut, (8) Verification & Test Commands. Filename: `ARGON_PLAN_V1_US_NUMISMATICS_CATALOG_2026-10-28.md`.

Key excerpts already summarized above; grill the contradictions (multi-modal vs Phase 1; D vs DD; 3,000+; Quick Add; Firestore write surface) harder than the happy-path narrative.

**OVER — independent SAG review requested.**
