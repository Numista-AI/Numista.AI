# _scripts/

One-time data ingestion, migration, audit, and debugging scripts used during
the initial build of the Numista.AI coin database. These are **not part of the
running application** and are not deployed to Cloud Run.

## Categories

| Prefix | Purpose | Count |
|---|---|---|
| `run_phase2_*.py` | Phase 2 image generation runs per coin series | 30 |
| `patch_*.py` | Firestore data patches (one-time fixes) | 14 |
| `audit_*.py` | Collection auditing and verification scripts | 7 |
| `inspect_*.py` | Ad-hoc data inspection scripts | 10 |
| `debug_*.py` | Connectivity and API debugging | 6 |
| `fix_*.py` | Data/encoding fix scripts | 8 |
| `check_*.py` | Data quality checks | 6 |
| `verify_*.py` | Post-fix verification | 6 |
| `test_*.py` | Feature-specific API tests | 13 |
| Misc | Various one-off utilities | ~20 |

## Safe to Archive?
Yes. All data these scripts created now lives in Firestore and GCS.
If you ever need to re-run a migration, use these as reference — but they
should **not** be executed blindly as the data schema may have evolved.

## Last Use
Most scripts were last used Jan–Apr 2026 during initial database population.
