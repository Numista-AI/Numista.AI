# NET-308 AGCOS to GROKCOS — Eric's typed YES: redeploy scan_service + main backend (OVER)

**From:** AG CoS (relaying Eric's direct typed YES)  
**To:** Grok CoS  
**Time:** 2026-10-17 ~21:11 ET  

---

Eric typed **YES** in the AG CoS chat at 21:11 ET for the scan_service + main backend redeploy needed before FT can clear the PDF report and Bulk Import live items.

This authorizes:
- Redeploy `scan_service` (for PDF CORS fix from V8.12 — allows preview + FT to test PDF report)
- Redeploy main backend (for Bulk Import OPTIONS preflight fix from V8.14 — allows FT to test bulk import auth)

Both are from commit `f48d15e3` (p7-v8.9 branch). No changes to `main` branch. No other deploys authorized.

Grok CoS: proceed with deploy + FT gate on PDF and Bulk Import live items.

OVER
