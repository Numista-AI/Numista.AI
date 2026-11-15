# PRE-LAUNCH SCAN REPORT ($Mode Mode)

- **Status:** **🔴 FAIL**
- **Scan Timestamp:** 2026-11-14 16:30:44
- **Git Branch / SHA:** `agent/prelaunch-scan-v1.1` @ `182c7fbfa0ab0b2ad3ea82ebf5b8a4ffe1a48310`
- **Automated Score:** **15 / 85** (Full Gate 9 adds 5 pts manual Eric Sign-Off = 100 pts)

| Gate | Domain | Status | Score | Duration | Detail |
|---|---|---|---|---:|---|
| **Gate 0** | Git Hygiene, origin/dev Sync & .env/.venv | 🟢 PASS | 5 / 5 | 8.2s | All assertions passed |
| **Gate 1** | Gemini 4 Model Governance & Config Parity | 🟢 PASS | 10 / 10 | 26.4s | All assertions passed |
| **Gate 2** | Security, Route Parity, Auth & Firestore/Storage | 🔴 FAIL | 0 / 20 | 82.3s | Gate 2 backend security pytest exited with code 1 |
| **Gate 3** | Backend Pytest, Hardware Filter & Container Parity | 🔴 FAIL | 0 / 15 | 451.6s | numista_backend/tests/ exited with code 1 |
| **Gate 4** | Flutter Analyze, Track Suites & Release Web Build | 🔴 FAIL | 0 / 15 | 259.1s | flutter analyze exited with code 1 |
| **Gate 5** | Domain Invariants (35 Programs, 2-Field Mint, CPG, Estate) | 🔴 FAIL | 0 / 10 | 13.8s | Gate 5 backend domain tests exited with code 1 |
| **Gate 6** | Cloud Run Secret Bindings & Live Endpoint Probes | 🔴 FAIL | 0 / 10 | 9.7s | numista-scan-service has 0 valid env/secret bindings |

## Holds & Caveats
- Cloud Run numista-backend missing pre-launch bindings: STRIPE_SECRET_KEY, CRON_SECRET (must be bound in GCP before -Mode Full Launch Gate)

