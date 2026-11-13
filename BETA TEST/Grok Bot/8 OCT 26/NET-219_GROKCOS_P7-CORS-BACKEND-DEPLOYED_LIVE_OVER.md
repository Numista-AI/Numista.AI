# NET-219 GROKCOS: P7 backend CORS fix DEPLOYED (Eric YES 15 Oct) - closes NET-218 block

- Source: branch deploy/cors-preview-20261015 @ b611eaca = origin/main 3c1bacf5 + CORS lines only (main.py + test). No frontend/hosting/rules, no 578b374a.
- Image: Cloud Build ebd6d0e4 SUCCESS -> us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:cors-b611eaca (no local docker; same Dockerfile).
- Cloud Run numista-backend (project studio-9101802118-8c9a8, us-central1): OLD numista-backend-00464-4fv -> NEW numista-backend-00465-xx7 (100% traffic). Rollback target: 00464-4fv.
- Verify (OPTIONS /api/checklist/add_coins): preview p7-v8-gate-ibg4oycd 200 + ACAO echoed + credentials true; https://evil.com 400 no ACAO; numista-vault--x.web.app.evil.com 400 no ACAO.
- Smoke: numista.ai 200, /api/spot_prices 200, /api/collection 401. No rollback needed.
- Follow-up: main does not contain b611eaca yet; next main deploy must include it or CORS regresses.
OVER
