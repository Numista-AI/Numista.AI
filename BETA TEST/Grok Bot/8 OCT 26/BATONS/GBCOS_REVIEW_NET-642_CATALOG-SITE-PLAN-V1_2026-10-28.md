# GB CoS REVIEW — NET-642 Argon Plan.v1 US Numismatics Catalog Site Integration

| Field | Value |
|---|---|
| **Document ID** | `GBCOS_REVIEW_NET-642_CATALOG-SITE-PLAN-V1_2026-10-28` |
| **Scorer** | GB CoS / Chief of Staff (Grok Bot) |
| **DTG** | 2026-10-28 ~11:50 AM ET (America/New_York) |
| **Ref Plan** | `ARGON_PLAN_V1_US_NUMISMATICS_CATALOG_2026-10-28.md` |
| **Ref Baton** | NET-642 (Desk → AG CoS / Argon) |
| **Also read** | `ACK_NET-642_AGCOS.md`, `DESK_NOTE_NET-642_PLANV1_LANDED_2026-10-28.md` |
| **NAC dependency** | `NAC_CODE_DESIGN_2026-10-28.md` **CONFIRMED** present (`Numismatics Catalog\00_CATALOG_RESEARCH\plans\` + box `/workspace/catalog-research/`) |
| **Status** | **SCORE ONLY — NO EXECUTE / NO FOLD / NO SPEND** |

---

## BLUF

Argon Plan.v1 is a strong architectural first cut for the US Numismatics Catalog (1776–2026) on studio Firestore + Flutter `/catalog`, with correct board hygiene (main locked, Mint FAIL-FIX untouched, $0 this baton, fold HOLD kept). **Score: 83/100. Verdict: CONDITIONAL GO.** Direction is right for Plan.v1 → review cycle; it is **not** executable as written. Fold the MUST-EDITS below into Plan.v1.1 or v2 after Stand Alone Grok and Eric’s answers to Q2/Q4. Do **not** open an EXECUTE ask until Mint FAIL-FIX / NET-641 clears Day #1 on `p7-gate`, or Eric explicitly parallel-YES.

---

## Score breakdown (100)

| Dimension | /20 | Notes |
|---|---:|---|
| **Architecture** | 16 | Clear staging → Discovery (`numista-morgan-pilot`) → studio `us_numismatics_catalog` → Flutter routes; NAC1 wired; dual-sided placeholders. Deduct: §1 multi-modal vs Phase 1 text-only conflict; facility filter letter collision. |
| **Isolation (Mint / main)** | 19 | `origin/main` LOCKED stated; Mint FAIL-FIX / NET-641 Day #1 protected; catalog on `dev` + preview channels; decoupled `lib/screens/catalog/` + `lib/services/catalog/`. Near-full marks. |
| **Schema** | 14 | Solid `CatalogItem` + Tier-A field name `mintage_mint_primary`. Deduct: `country: "US"\|"PF"` only (Q2 may force expand); Mint filter lists Dahlonega (D) and Denver (D); FAC not yet aligned to NAC locked `DD` + `mint_mark_on_coin`. |
| **UX / Auth** | 14 | Browse + detail screens sensible; public/guest/registered/pro tiers sketched. Deduct: Quick Add not locked to existing collection-add + REQ_031 auth; coin-card default-face rule absent; desktop/tablet-first vs mobile-companion ~10% not stated; Q4 unresolved for Phase 1 SEO. |
| **BF roadmap realism** | 12 | Coins+notes before BF / medals after = correct priority. Deduct: “3,000+ verified cards before BF” aspirational — must gate on Catalog Research throughput + fold HOLD stack; visual search correctly Phase 2 in §7 but sold in §1 as pillar. |
| **Risk** | 15 | PLAN ONLY / $0 / no file changes = excellent. Deduct: Firestore security rules (client read-only + admin/batch write) not spelled as a hard requirement; no explicit “do not steal Mint execute” test gate in §8. |
| **TOTAL** | **83** | **CONDITIONAL GO** |

---

## What is strong

- Board locks respected in writing: main locked, fold HOLD `586+588+589+590`, NET-641 Mint FAIL-FIX Day #1, NET-640 Discovery spend left with Catalog Research, **$0 on NET-642**.
- Correct product split: **Coins + Bank Notes before Black Friday; Medals Phase 2 after BF** (matches Eric standing rule).
- Philippines already in schema as `country: "PF"` — aligns with INCLUDE.
- NAC1 as universal key; design doc **confirmed present** (not a blocking missing dependency).
- Dual-sided assets + SVG placeholders when imagery missing — protects catalog completeness and UI.
- Non-destructive overlap with personal collection (`nac_code` FK) — right model.
- Preview / `dev` isolation and package decoupling reduce Mint-track blast radius.
- Auth sketch (guest SEO → registered collection → Pro research) is a workable starting frame pending Q4.

---

## MUST-EDITS before Plan.v2 / EXECUTE ask

Numbered, actionable. Plan.v1.1 or v2 must absorb these before any EXECUTE ask.

1. **Coin card default face = unique identity side** (Eric standing rule 2026-10-15). Default thumbnail / card face must show the side that uniquely identifies the type (e.g. Presidential $1 → president portrait, **not** the shared Statue of Liberty reverse). Document in Catalog card UX + any `PlaceholderCoinCard` / flippable mini-thumbnail defaults.

2. **Mintage Tier A = U.S. Mint / Treasury figures only** (Eric 2026-10-05). Keep `mintage_mint_primary` as Tier A sourced only from Mint/Treasury/primary government figures. **Never** treat PCGS/NGC (or other third-party) counts as Tier A — they stay in `crosswalk` / Tier B estimate fields only. State this as a hard ingest rule in the crosswalk enrichment step.

3. **Firestore write path locked:** live site may use studio `us_numismatics_catalog` **only** with (a) **client read-only** security rules and (b) **admin / batch write** path for ingest. No client SDK writes to the catalog collection. Spell rules + admin pipeline in Plan.v1.1.

4. **Quick Add must reuse existing collection-add path + auth (REQ_031 lockdown).** `+ Add to My Collection` / Wishlist must call the current collection write stack under existing auth — **not** a parallel catalog write path. Call out REQ_031 explicitly.

5. **Desktop / tablet first for catalog browse.** Catalog UX is a big browse job; design for desktop/web + tablet first. Mobile companion effort ~**10%** (Eric standing). Do not optimize Phase 1 grid primarily for phone 2-column.

6. **Disambiguate Dahlonega vs Denver facility codes.** Plan §3 Mint filter lists both as `(D)`. Align to NAC locked FAC: Dahlonega = **`DD`**, Denver = **`D`** (per `NAC_CODE_DESIGN_2026-10-28.md` §0.1). Update filter rail labels and `facility` examples. Also adopt `mint_mark_on_coin` / `mint_mark` separation (no-mark Philadelphia = `FAC=P` + `mint_mark_on_coin:false`).

7. **Clarify search phases.** Phase 1 = **full-text / faceted search only**. Visual / multi-modal / Microscope photo-match = **Phase 2** (already in §7 — remove or demote the §1 “Multi-Modal Search” pillar language so it does not imply BF scope).

8. **Gate “3,000+ cards before BF” as aspirational.** Ship criterion = Catalog Research verified throughput + fold HOLD clearance, not a hard card count. Phrase BF cut as “maximum verified cards CR can stage under fold HOLD,” with a minimum viable series set named in Plan.v1.1 (e.g. evidence-pack series first).

9. **Schema `country` contingency for Eric Q2.** If founder YES to foreign legal-tender until 1857 (Spanish 8 Reales etc.), expand `country` beyond `"US"|"PF"` (or add a separate circulating-specie kind/flag) **before** Phase 1 ingest locks the enum. If NO, keep US|PF and document World Specie as Phase 2 only (already sketched).

10. **Auth contingency for Eric Q4.** Phase 1 guest/public browse+search vs gated browse must be decided before SEO and route guards are built. Hold implementation of paywall boundaries until Q4 answered; do not hard-code Pro-only browse.

11. **Philippines INCLUDE + Medals Phase 2** — affirm explicitly in Plan.v1.1 (already directionally correct; make standing-rule citations visible so later agents do not “fix” them).

12. **§8 verification: add Mint-isolation smoke.** Before any catalog preview merge claim: confirm `p7-gate` / Mint FAIL-FIX files untouched; `git status` clean of Mint paths; no AB/Discovery spend on this baton.

---

## SHOULD-EDITS (non-blocking)

- Name the minimum BF series set from the 25 evidence packs (AWQ, ASE, ATB, Innovation $1, etc.) as the P0 checklist spine.
- Add `gsid_xref` optional opaque FK note (NAC design already forbids inventing GSIDs).
- Era picker: confirm Colonial bucket stays Phase 2 content even if UI chrome ships earlier.
- Document CDN/GCS image URL auth (public thumbs vs signed hi-res for Pro) when Q4 lands.
- Variety sub-table (VAMs etc.): Phase 1 show BASE only; deep variety grid Phase 2 unless CR already verified.
- Explicit “Catalog Research owns NET-640 Discovery ≤$60; this plan never bills morgan-pilot” one-liner in §2.

---

## Eric Qs 1–4 (held for golf return)

| # | Question | Blocks now? | Guidance |
|---|---|---|---|
| **Q1** | Pre-1792 state/colonial: group by state vs one Pre-Federal/Continental category? | **Deferrable (Phase 2)** | Pre-Federal is Phase 2 post-BF. Does not block Phase 1 schema. Prefer answering before Phase 2 UI chrome. |
| **Q2** | Foreign legal-tender until 1857 (e.g. Spanish 8 Reales) include? | **BLOCKS schema** | Affects `country` enum / kind model. Need answer before Phase 1 ingest locks types. |
| **Q3** | Collectors submit photos for placeholders vs internal-only images? | **Deferrable (Phase 2)** | Plan already puts community ingestion in Phase 2. Safe to hold. |
| **Q4** | `/catalog` browse+search fully public; paid only for AI match + values? | **BLOCKS auth / SEO for Phase 1** | Guest tier and route guards depend on this. Hold paywall implementation until answered. |

Relay Qs when Eric is back from golf. Do **not** invent answers.

---

## Next steps

1. **Stand Alone Grok (SAG)** independent review — use `SAG_PASTE_PACKET_NET-642_CATALOG-SITE-PLAN-V1.md` (Eric pastes; keep independence from this GB CoS score).
2. **Eric answers Q2 + Q4** (and optionally Q1/Q3) when back from golf.
3. Argon / AG CoS folds GB MUST-EDITS + SAG findings + founder answers → **Plan.v1.1 or v2**.
4. Re-score (GB CoS + SAG) if material changes.
5. **NO EXECUTE** until Mint FAIL-FIX / NET-641 Day #1 on `p7-gate` is clear, **or** Eric explicitly types parallel-YES for catalog preview work on `dev`. Fold HOLD stack `586+588+589+590` remains. No AB spend on this baton.

---

## Explicit board unchanged

- **NET-640** afternoon Phase I ≤$60 Discovery-only on `numista-morgan-pilot` — still owned by Catalog Research; untouched by this score.
- **NET-641** Mint FAIL-FIX on `p7-gate` — still Day #1; catalog must not steal execute.
- **Fold HOLD** `586+588+589+590` — kept.
- **$0** this baton (NET-642 score/plan cycle only).
- **NAC_CODE_DESIGN_2026-10-28.md** — confirmed present; not a missing blocker.

**OVER — SCORE ONLY.**
