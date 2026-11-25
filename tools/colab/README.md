# Numista.AI — Google AI Ultra Colab GPU Batch Pipeline (`tools/colab/`)

Authorized BUILD (`25 Nov 2026, 11:34 AM ET`, pinned `PLAN_COLAB_GPU_PIPELINE_v1.0.md` `SHA8 d0322dc7`).
Review Gates Passed: **SAG 97 PASS**, **Gemini 98 PASS**, **Muse 96 PASS**.

## Hard Safety Boundaries
- **Pilots & Offline Staging Only:** Zero live Firestore writes, zero live GCS writes, zero GCP service-account keys or ADC on Colab VMs.
- **Tooling:** Exclusively `google-colab-cli` (`colab run` without `--keep` so every GPU VM auto-destroys immediately on exit).
- **Drive Staging:** All job outputs, `manifest.json` (SHA-256 checksums), `summary.md`, and `cu_receipt.json` go strictly to `Google Drive -> Numista.Ai -> Colab_Staging/<job_id>/` (`1yAEA7ob4eUY_pkWqCj2m9ipXgvB5okcA`).
- **Budgets:** L4 default (`T4` fallback; `A100`+ blocked); **25 CU** pilot cap, **150 CU** full-scale cap, **500 CU** hard stop floor; **45 min** pilot / **120 min** full wall-clock timeouts.
- **Promotion:** Any move from `Colab_Staging/` into GCS, Firestore, or production backend requires a separate `DEPLOY` authorization.

## Reviewer Conditions Implemented
1. **M1 Framing (`m1_framing.py`):** Numerically measures and enforces the **75% target / 73% minimum** framing ratio on `framing_metrics.json` and `contact_sheet.html`.
2. **M2 Advisory Flags (`m2_embeddings.py`):** Outputs `advisory_flags.json` (`advisory_only: true`, `mutated_catalog: false`, routed to `TRK-002 SAG/Muse Review Queue`).
3. **M3 Cropper (`m3_cropper.py`):** Defaults to **Apache-2.0 `RT-DETR`**, blocks AGPL `YOLOv11`, and enforces `annotation_count >= 150` before training.
4. **M4 OCR (`m4_ocr.py`):** Requires `>= 5` hand-checked sample pages and reports numeric **CER** and **WER** in `ocr_error_report.json`.
5. **Timeout Enforcement (`runner.py`):** `run_with_timeout` kills subprocesses exceeding wall-clock bounds and is unit-tested in `test_colab_pipeline.py`.

## One-Time Interactive OAuth Setup (Eric's Workstation)
```powershell
C:\Users\ericd\.colab-cli-venv\Scripts\colab.exe usage
```
Follow the browser OAuth prompt once to verify your **1,531.77 CU** balance.

## Running Verification Tests
```powershell
python -m pytest tools/colab/tests/test_colab_pipeline.py -v
```

## Kill Switch
```powershell
C:\Users\ericd\.colab-cli-venv\Scripts\colab.exe sessions
C:\Users\ericd\.colab-cli-venv\Scripts\colab.exe stop --session <session_name>
```
