# Phase I — EXECUTE STAGING (prep only — do NOT run until 8:00 PM ET)

**Filed:** Wednesday, 28 Oct 2026 ~7:45 AM ET (America/New_York)  
**Status:** **STAGED / HOLD until night window.** Eric YES for Phase I ingest+wire ≤$30 under $50/night is ON.  
**Spend now:** **$0.** No Discovery import, no Layout Parser, no Check Grounding, no fold.  
**Night window:** 8:00 PM – 4:00 AM ET only.  
**Project:** `numista-morgan-pilot` (App Builder credit).  
**Ceiling:** ≤ **$30** list Discovery SKUs; stop at **80% (~$24)** without new Eric YES.  
**Cite style (Eric):** short primary — source name, URL, access/report date.  
**NAC:** use codes from `NAC_CODE_DESIGN_2026-10-28.md` on new baton rows when practical.

**Plans read:**  
- `/workspace/catalog-research/PHASE1_INDEX_WALL_INGEST_PLAN_2026-10-28.md`  
- `/workspace/roi/burn_plan_phase1_costcheck_20261028.md` (+ catalog-research copy)  
- `/workspace/catalog-research/INVENTORY_2026-10-28.md`

**Laptop mirror:**  
`C:\Users\ericd\Documents\MyVertexProject\Numismatics Catalog\00_CATALOG_RESEARCH\ingest\PHASE1_EXECUTE_STAGING_2026-10-28.md`

---

## BLUF staging board

| WP | Name | Ready? | Blocker |
|---|---|---|---|
| WP0 | Preflight (read-only) | **PARTIAL** | ADC OK; `gcloud` binary exists but **default project = `numista-qc`** — must `gcloud config set project numista-morgan-pilot` at 8pm before any call. PATH must include SDK bin. |
| WP1 | FRASER / Mint AR → docs | **READY** (reuse-first) | Local `/workspace/g1/ar` (~45 txt) + factcheck-src GCS path known; no live store list this morning ($0). |
| WP2 | BEP / FR materials | **READY** (curate) | Need curated excerpt set from NET-610 pack URLs at execute time — do not mass crawl. |
| WP3 | NNP / Fugio / colonial | **READY** (curate) | Pack cites + `/workspace/fugio-day1` seeds; rights = public cite extracts only. |
| WP4 | govinfo / Coinage Acts | **READY** (curate) | Pack URLs for 1792/1849/1903/Act 1564. |
| WP5 | smithsonian-nnc attach | **READY** (wire) | Store exists (~54k); attach only — **do not re-ingest**. |
| WP6 | Wire + smoke (no CG) | **READY** after WP1–5 | Adv Answers OFF; 2–3 Enterprise Search smokes only. |

**Overall:** Staging **READY for 8:00 PM ET execute** after WP0 project switch. **BLOCKED for morning spend** by design.

---

## Preflight status (this morning, $0)

| Check | Result |
|---|---|
| ADC file | Present `~/.config/gcloud/application_default_credentials.json` (authorized_user) |
| ADC token refresh | **OK** (`application-default print-access-token` succeeded) |
| `gcloud` binary | `/home/box/sdk/google-cloud-sdk/bin/gcloud` (SDK 590.0.0) — **not on default PATH** |
| Default project | **`numista-qc`** ← wrong for Phase I; switch to **`numista-morgan-pilot`** at execute |
| Discovery list / import | **NOT RUN** (would be execute-window work; morning = $0) |
| Check Grounding | **OFF / forbidden** this YES |
| Fold / Firestore write | **HOLD** |
| Clock | Confirm America/New_York; do not start ingest before **20:00 ET** |

---

## Reuse-first paths (do these before any Layout Parser)

| Asset | Path |
|---|---|
| Mint AR text | `/workspace/g1/ar/*.txt` (~45 files) |
| Verified mintage rows | `/workspace/g1/ar/docai_review/verified_mintage_rows.csv` (~1,152) |
| Factcheck GCS (existing) | `gs://numista-morgan-pilot-factcheck-src/` (~74 MB cited) |
| NET-610 evidence pack | `/workspace/roi/CATALOG_EVIDENCE_PACK_HOLD586-590_NET610_2026-10-27.md` (+ `.csv`); laptop `MORGAN_PILOT\out\` / catalog-research `net610/` |
| Option B outs | `/workspace/catalog-research/net610/` |
| Fugio seeds | `/workspace/fugio-day1/` |
| Ingest script **patterns** (do not blindly re-run) | laptop `MORGAN_PILOT\scripts\ingest_morgan_mint_batch_a.py`, `ingest_state_quarters_batch_b.py` |
| Smithsonian store | Discovery `smithsonian-nnc` — **attach only** |

Prefer **inline document import** (AWQ pilot pattern) over new GCS objects.

---

## Exact commands for 8:00 PM ET (DO NOT RUN NOW)

> Copy/paste at night only. Replace `ENGINE` with the engine chosen for smoke (`morgan-pilot-search` preferred; blended only if ≥2 stores).

### WP0 — project + sanity (still cheap / admin)

```bash
export PATH="/home/box/sdk/google-cloud-sdk/bin:$PATH"
gcloud config set project numista-morgan-pilot
gcloud config get-value project   # must print numista-morgan-pilot
gcloud auth application-default print-access-token >/dev/null && echo ADC_OK

# Read-only inventory (execute window OK; still $0-ish admin):
gcloud alpha discovery-engine data-stores list --location=global --project=numista-morgan-pilot
# Note doc counts for morgan-docs, morgan-factcheck, smithsonian-nnc; which engines attach which stores.
```

### WP1 — reuse AR extracts → unstructured docs

```bash
# 1) Build curated excerpt JSONL/docs on box from /workspace/g1/ar (local, $0)
# 2) Inline-import into morgan-docs OR sibling store (CoS choice at execute):
#    Prefer append vs new store — document choice in ingest manifest.
# Example shape (PLACEHOLDER — use actual import script from MORGAN_PILOT pattern):
# python3 scripts/inline_import_fraser_excerpts.py --project numista-morgan-pilot \
#   --data-store morgan-docs --src /workspace/catalog-research/ingest/excerpts_wp1/
```

**Only if gaps remain after reuse:** Layout Parser on **50–100 page sample** → FinOps spot-check → then bulk under remaining ceiling. **Do not** open with bulk LP.

### WP2–WP4 — curated public excerpts

```bash
# Curate ≤ ~20–50 BEP + ≤ ~20–40 NNP/Fugio + Coinage Act pages from NET-610 pack URLs only
# Inline import same as WP1; tag source=bep|nnp|govinfo, access_date=2026-10-28 (or actual)
```

### WP5 — attach Smithsonian (no re-ingest)

```bash
# Attach smithsonian-nnc to the search engine used for later CG path
# Prefer morgan-pilot-search / morgan-factcheck-search; if blended, keep ≥2 stores
# Est. $0 incremental for attach alone
```

### WP6 — smoke only (NO Check Grounding)

```bash
# Adv Answers OFF; observability/trace OFF
# 2–3 Enterprise Search queries proving hits on:
#   - Fugio / Journals or NNP excerpt
#   - Franklin or Walker Mint AR mintage passage
#   - BEP / Watermelon or FRBN vs FRN fact sheet
# STOP. Write ingest manifest + smoke log. Ask Phase I-C YES separately (≤$0.50 Option A).
```

---

## Cite-style note (Eric)

Every ingested / baton cite uses **short primary** form:

```
Source Name — https://example.gov/path — accessed 28 Oct 2026 (or report date YYYY)
```

Examples: FRASER Mint AR 1922; BEP fact sheet URL; Journals of Congress 6 Jul 1787; govinfo Coinage Act page.  
No Wikipedia-as-primary. No fabricated mintages. Sales ≠ mintage.

---

## Stop conditions

1. Clock outside **8:00 PM – 4:00 AM ET** → stop ingest.  
2. List spend approaches **~$24 (80% of $30)** → stop; ping FinOps + Eric.  
3. Layout Parser sample implies bulk would breach ceiling → stop; FinOps ping.  
4. Any urge to run Check Grounding / Adv Answers / Gemini / Cloud Run / fold → **STOP** (out of YES).  
5. New GCS bucket temptation → **STOP** unless FinOps storage-SKU sign-off.  
6. ADC/project wrong (`numista-qc`) → **STOP** until project fixed.

---

## Deliverables when night DONE (sandbox only)

1. Ingest manifest JSON under laptop `00_CATALOG_RESEARCH\ingest\` + box mirror  
2. Engine attach confirmation (smithsonian-nnc + new docs)  
3. Smoke-query log (2–3 hits)  
4. Desk EXECUTE_DONE baton + FinOps actuals note  
5. Separate ask for Phase I-C CG YES  

---

## FAIL → WP map (unchanged)

See `PHASE1_INDEX_WALL_INGEST_PLAN_2026-10-28.md` table (19 FAIL). Already SUPPORT: FG-586-04 — do not re-burn.

---

**Catalog Research staging · morning 28 Oct 2026 · $0 · execute at 8pm ET.**
