# Catalog Research — Initial Brief (Eric, 28 Oct 2026)

## Goal
Academic-standard US Numismatics Catalog (references, citations) that rivals U.S. Mint and Smithsonian quality. Searchable by users and by Numista.Ai Morgan AI.

## Scope order
1. Every USA coin, bank note, and medal — Fugio through latest Oct/Nov 2026 U.S. Mint offerings (images, histories, mintages/print figures from primary sources).
2. Then popular foreign currency and notes.

## Burn rules
- Credit: GenAI App Builder / Agent Builder on Numista.Ai (~$999.88 left late Oct 2026; expires 23 Jan 2027). Use every cent.
- Target: ≥85% of remaining credit used before Black Friday 2026 (Fri 27 Nov 2026).
- Night window only: 8:00 PM – 4:00 AM America/New_York (do not interfere with daytime site build).
- Nightly ceiling: $50 per night (Eric YES 28 Oct 2026).
- Coordinate ceilings with FIN OPS before spend; still no fold/production without Eric typed YES.
- Discovery / Check Grounding / Enterprise Search SKUs only on numista-morgan-pilot — never Vertex Gemini, Cloud Run, studio/qc Gemini for this burn.

## Do not duplicate
Know everything already in Google Cloud / GCS / Firestore / Numista-Brain before ingest. Review first.

## Standing related locks (unchanged)
- NET-639 Phase I index-wall ingest = PREP/STANDBY until FinOps-cleared YES for Phase I ingest+wire (separate from nightly ceiling).
- No Check Grounding until corpus ingest + separate YES.
- Fold HOLD; live/main locked for catalog.

Filed by Catalog Research ~7:40 AM ET 28 Oct 2026 from Eric brief + $50/night confirmation.

---

## Clarifiers appended (Catalog Research, 28 Oct 2026 ~7:45 AM ET)

### Phase I YES â€” tonight
Eric typed YES for **Phase I index-wall ingest+wire <= $30** on **numista-morgan-pilot** Discovery SKUs only, under the **$50/night** ceiling. Night window **8:00 PM â€“ 4:00 AM ET**. Reuse extracts first; Layout Parser only after 50â€“100 page sample; **Adv Answers OFF**; attach **smithsonian-nnc** OK; **no Gemini**; **no catalog fold**. Staging: `00_CATALOG_RESEARCH\ingest\PHASE1_EXECUTE_STAGING_2026-10-28.md`. **Do not execute ingest in the morning.**

### Cite style
Short primary cites only: **source name, URL, access/report date**. No Wikipedia-as-primary. No fabricated mintages (sales â‰  mintage).

### Medals scope
Medals = **official U.S. Mint** (Presidential / Congressional / Assay / Mint medals) **+ common private commemoratives** users may add. Do **not** reinvent the ~113 existing studio `definitive_reference` medal rows â€” attach/crosswalk first.

### NAC code request (Eric)
Develop proprietary **Numista.Ai Catalog (NAC)** item codes for org sharing â€” Greysheet/GSID-inspired conceptually, **not** a copy of Greysheet numbering. Design filed: `00_CATALOG_RESEARCH\plans\NAC_CODE_DESIGN_2026-10-28.md` (scheme **NAC1.KIND.CC.CLASS.SERIES.DATE.FAC.VAR.CHK**).

### Nightly burn ceiling
**$50 per night** (Eric YES 28 Oct 2026). Phase I tonight hard-capped at **<= $30**. Coordinate with FinOps; App Builder credit ~$999.88 left (exp 23 Jan 2027); target ~85% used before Black Friday 2026 (Fri 27 Nov).

