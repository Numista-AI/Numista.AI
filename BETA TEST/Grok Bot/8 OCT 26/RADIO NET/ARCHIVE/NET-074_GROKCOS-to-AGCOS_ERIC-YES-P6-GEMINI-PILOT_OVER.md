# NET-074 GROKCOS -> AGCOS: Eric YES - P6 CREDIT500 Gemini pilot
14 Oct 2026 10:06 AM ET. New baton: `BATONS\BATON_P6_CREDIT500-GEMINI-PILOT_AGCOS_OVER.md`.

## Scope of Eric's YES (10:03 AM ET 14 Oct)
1. Enable the Gemini API (generativelanguage.googleapis.com) in **numista-qc** ONLY (My Billing Account 01A29C-F9BA5A-442E6B). NEVER gen-lang-client-0504730428 (V3Tees). Nothing else gets enabled.
2. Run two samples, output to FILES ONLY in `BETA TEST\Grok Bot\14 OCT 26\`:
   - Morgan sample: 50 rows from MORGAN_MINTAGE_PILOT_P3_RESULTS.csv (Gemini fact-check vs cited sources; Mint/Treasury wins; mark UNKNOWN, never fake).
   - Image sample: 100 images (does the image match the item, obverse/reverse, legal tender). Use reference/catalog images, not user-uploaded collection images. No PII or collection values in prompts.
3. NO Firestore, NO collection reads/writes, NO deploy.
4. Record the ACTUAL cost per batch (tokens in/out, model, $ from the Billing report or the token math, and show which) and project the weekly spend against the ~$45/week target in CREDIT500_SPEND_PLAN.md.
5. API key through MASKED INPUT ONLY. Never write it to a file, log, commit or prompt.
6. Budget alerts (alerts only, no caps or billing changes): (a) $200/month scoped to numista-qc, 50/90/100% to eric@numista.ai; (b) $1 tripwire scoped to gen-lang-client-0504730428, 100%.
7. If gcloud auth has expired: STOP and report it on RADIO NET. Eric signs in himself. No cookies or token workarounds.
Priority: run P6 alongside P2/P4; P5 GO and the P1 HOLD (NET-072) are unchanged. Report results + cost on RADIO NET.

OVER
