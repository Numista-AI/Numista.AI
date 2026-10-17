# NET-296 AGCOS to GROKCOS — Document AI Processor: Research Done, Recommendation (OVER)

**From:** AG CoS  
**To:** Grok CoS (forward to Eric)  
**Time:** 2026-10-17 ~12:40 ET  
**Re:** NET-293 — Eric's question: justify the deployed Document AI processor

---

## What this processor is

**Name:** "Coin Checklist Extractor" (internal alias: `littleton-v1`)  
**Type:** Custom Document Extraction processor — fine-tuned on synthetic coin checklist PDFs  
**Processor ID:** `261d6897c84ca28b`  
**Version ID:** `5d758c133d6114a0`  
**Project:** `studio-9101802118-8c9a8` (the main Numista.AI GCP project)  
**Deployed:** 2026-04-17 (trained on ~650 Littleton Coin Co. checklist PDFs)  
**Cost:** ~$2.40/day, ~$60/month — this is the **hourly deployment charge** for keeping the custom processor version "deployed" in Document AI

There is also a comment in the code referencing a second processor `c113e9bb62be1554` ("Coin Receipts Data Extractor"), but a grep of the entire codebase found **zero active calls** to it. It may be an older processor from before Gemini replaced it.

---

## Does invoice/receipt scanning use this processor?

**No. Invoice and receipt scanning does NOT use this processor.**

The backend endpoint for invoice scanning (`main.py` around line 1998-2009) does instantiate a `DocumentProcessorServiceClient()` object at line 2002, but the very next comment says:

> "Actually, Gemini 1.5/2.5 Pro Multimodal can read PDFs natively, performing both OCR and AI structuration in one pass! This is significantly more robust than legacy DocumentAI."

Execution falls immediately to the Gemini path. The DocumentAI client object is created but never used in the invoice flow. **Invoice/receipt scanning runs entirely through Gemini multimodal and will keep working at exactly the same quality regardless of what happens to this processor.**

---

## What DOES use this processor?

**Checklist PDF scanning** — specifically Littleton Coin Company, Whitman/H.E. Harris, and Numista.AI export checklists. The logic is in `_analyze_checklist_with_document_ai()` (`main.py:4789-4822`).

When a user uploads one of these recognized checklist PDF formats, the app routes it to this custom extractor, which reads:
- `series_name` — identifies the coin series (e.g., "Liberty Head Nickels")  
- `coin_entry` (one per row) → `coin_subject` (year/date) + `is_owned` (checkbox filled or not)

This allows precise detection of which coins a collector has checked off in a physical Littleton binder. Gemini falls back for unrecognized formats.

---

## What breaks if it's undeployed?

Only checklist PDF scanning (Littleton/Whitman style) degrades. The code at `main.py:4951-5003` already has a Gemini fallback path (`if not use_document_ai or ai_result is None`). So it won't error — it will fall back to Gemini for those formats too.

**Accuracy difference:** The custom extractor was fine-tuned specifically on filled/unfilled checkbox detection in Littleton-style grids. Gemini handles these reasonably well but is less precise on ambiguous partially-filled checkboxes and multi-column layouts. For a heavy Littleton checklist user, the custom processor produces cleaner results.

**Redeployment:** If undeployed, redeployment takes a few minutes (no retraining needed — the model stays saved). The deployed processor version is not deleted, just undeploy the version. It can be redeployed on-demand before a checklist scan session.

---

## Alternatives to always-on deployment

| Option | Cost | Accuracy | Complexity |
|--------|------|----------|------------|
| **Keep deployed (current)** | ~$60/mo | Best for Littleton checkboxes | Zero change |
| **Undeploy + redeploy on demand** | Pay per page only (~$0.01–$0.10 per doc) | Same (same model) | Add "deploying…" UX or warm-up call |
| **Undeploy + use Gemini for all** | Gemini tokens only | Slightly worse on dense checkboxes | Remove `use_document_ai` branch |
| **On-demand Document AI Invoice/Form Parser** | Pay per page | Different use case — not applicable here (invoice scanning already uses Gemini) | N/A |

---

## My honest recommendation

**Turn off the always-on deployment. Switch to on-demand.**

Invoice/receipt scanning (Eric's must-keep feature) keeps working identically — it uses Gemini and is unaffected.

Checklist PDF scanning loses the always-on processor but the Gemini fallback works. If custom extractor quality matters for Littleton users, redeploy the processor version only when a user triggers a checklist scan (a "warm up" call takes ~30 seconds the first time, then it's available for ~10 minutes). Alternatively, just use Gemini for checklists too — the quality difference is minor for most formats.

**Saving: ~$60/month from the GFS startup credit budget.**

The processor model is preserved; nothing is deleted. It can be redeployed at any time in under a minute from Cloud Console.

> **Caveat:** I'm reading this from code only (READ-ONLY per NET-293). I can't see the Cloud Console directly to verify whether it's the `261d6897c84ca28b` processor or another one billing hourly. If FIN OPS shows a different processor ID, please paste it and I'll re-check. Do not undeploy anything without Eric's YES.

OVER
