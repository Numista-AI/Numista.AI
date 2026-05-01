# Numista.AI — Session Report, April 16, 2026

## Day Summary

Full day focused on Document AI checklist extractor training. Crossed the 10-document
Fine Tune threshold. Training can begin tomorrow morning.

---

## What Was Accomplished

### Document AI Fine-Tune Ready ✅
- **651 documents** confirmed in dataset (`261d6897c84ca28b`)
- **12 documents labeled** — exceeds the 10-document minimum
- `foundation-v2` (base: `v1.6-2026-01-13`) set as active Default version
- v4 schema deployed: `coin_entry { coin_subject, is_owned }` — one per checklist row

### Schema Design Clarified
Two schemas now formally defined for two different checklist layouts:

| Schema | For | Fields |
|---|---|---|
| **Schema A — v4** | One-row-per-mint (Littleton) | `coin_subject` + `is_owned` |
| **Schema B — Grouped** | One-row-per-year (Numista.AI native) | `coin_subject` + `has_p/d/s/s_slv` |

### Numista.AI Native Checklist Spec Written
`NUMISTA_AI_CHECKLIST_DESIGN_SPEC.md` — full design spec for a Numista.AI branded
checklist PDF optimized for older collectors and machine extraction.
Key design: grouped year rows with □P □D □S □S-SLV columns, standard square checkboxes,
no Wingdings fonts. Maps to Schema B. Closes the loop: Generate → Print → Scan → Ingest.

---

## Tomorrow's First Steps

### Step 1 — Trigger Fine Tuning (Do This First!)
```
Document AI → Processor 261d6897c84ca28b → Label & Build → Fine tune
  Version name: littleton-v1
  Base version: foundation-v2
  → Train
```
Training runs 1–4 hours on Google's servers. You'll get an email when done.

### Step 2 — While Training Runs
- Return to receipt ingestion pipeline (`auto_label_receipts.py`)
- Implement Gemini description parser in `main.py`
- Review Phase 2 ingestion scripts for readiness

### Step 3 — After Training Completes
```
Deploy & use → Manage versions → Deploy littleton-v1 → Set as Default
```
Then test accuracy against a Littleton checklist via API.

---

## Known Issues / Tech Debt

| Issue | Severity | Fix |
|---|---|---|
| `is_owned = null` for empty circles | Medium | `main.py`: treat `null` as `false` |
| First 4 labeled docs on old v3 schema | Low | Acceptable for v1; re-label for v2 |
| `has_d/p/s/s_slv` ghost fields in UI | Cosmetic | Click "Clear suggestions" in Label & Build |
| Presidential Dollars skipped | Low | Needs Schema B processor (future) |

---

## Key Reference Numbers

| Item | Value |
|---|---|
| Checklist Extractor Processor ID | `261d6897c84ca28b` |
| Receipt Extractor Processor ID | `c113e9bb62be1554` |
| Active model version | `foundation-v2` (Default) |
| Target fine-tuned version name | `littleton-v1` |
| GCP Project | `studio-9101802118-8c9a8` |

---

*April 16, 2026 — EOD*
