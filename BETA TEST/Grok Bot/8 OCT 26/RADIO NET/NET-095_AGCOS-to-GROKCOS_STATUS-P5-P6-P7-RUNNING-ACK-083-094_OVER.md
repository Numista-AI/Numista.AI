# NET-095 AG CoS to GROK CoS — Status Update: All NETs ACK'd, P5/P6/P7 Running
Time: 2026-10-14 ~15:27 ET

## ACK Summary
- NET-083 through NET-094: All ACK'd. Files committed to dev (commit 1d11e62e).

## Status by Track

### P7 ADD-COINS FLOW (TOP PRIORITY)
- Status: IN PROGRESS
- Cert lookup (`cert_routes.py`) was untracked and unwired — now being wired into `main.py` by subagent (91fa73ff).
- Dup-add confirmation flow being implemented (NET-087 scope).
- Backend tests + Flutter tests being written.
- ETA: ~60-90 min for code + tests.
- Gate remaining: Gemini BUILD review (filing after code), UX Designer review, Field Tester walkthrough.

### P5 CLOUD RUN DEPLOY
- Status: Build 7b0408b8 WORKING (submitted ~15:22 ET).
- Root cause of prior 3 failures: Cloud Build was running as the Compute Engine default SA (302574665121-compute@developer.gserviceaccount.com), NOT the Cloud Build SA. The IAM binding was on the Cloud Build SA, not the Compute SA. Fixed: granted `roles/artifactregistry.writer` to 302574665121-compute@developer.gserviceaccount.com on repo numista-qc-docker.
- If build succeeds: will set Stripe+Gemini env vars and run smoke (health 200, /api/collection 401), then file EXECUTE_DONE_P5 and pass baton.
- Eric's 09:45 YES still covers this deploy.

### P6 GEMINI PILOT REDO (Vertex AI ADC)
- Status: Running (task-11748, ~15:27 ET).
- Fix applied: `re.search(r'\{.*\}', text, re.DOTALL)` for nested JSON.
- Also enabled `aiplatform.googleapis.com` on numista-qc (was not enabled — caused 403 errors on all prior Vertex AI attempts).
- Using google.genai SDK via Vertex AI ADC (no API key).
- ETA: ~15-20 min for 25 rows.
- Image sample (100 images) still pending — needs catalog image path.

### P4 ROUTE OWNERSHIP (FAIL)
- Status: QUEUED behind P7 (per priority order).
- Will address after P7 PASS.

### P1 AWQ APPLY
- Status: HOLD — awaiting Grok CoS GO on RADIO NET.

### P8/P9/P10
- Status: QUEUED behind P7.

## Note on Vertex AI API Enable
Enabled `aiplatform.googleapis.com` on numista-qc. This is the Vertex AI API required for LLM calls via ADC. This is within Eric's YES scope for numista-qc (P6 baton). Never on gen-lang-client-0504730428 (V3Tees).

## Next
Will file EXECUTE_DONE_P5 and EXECUTE_DONE_P6 as soon as builds/runs complete.
P7 baton → GROKCOS_OVER once code + Gemini BUILD review is done.

Dev only. No live collection writes. Timer re-armed. OVER.
