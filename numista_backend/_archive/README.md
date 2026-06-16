# _archive/

This directory contains **legacy files** that are no longer active in production
but are preserved for historical reference.

## Contents

### `app.py` (archived June 16, 2026)
- **What it was:** The original Streamlit-based UI for Numista.AI (~4,022 lines)
- **Why archived:** Replaced by the Flutter (`numista_mobile/`) frontend + FastAPI (`main.py`) backend architecture
- **Why kept:** Contains reference implementations for `US_PROGRAMS`, normalization dictionaries (`COIN_NICKNAMES`, `CONDITION_MAP`), and some rendering logic that may be useful for future reference
- **Do not run:** Imports the `vertexai` (old Python SDK, shut down June 24, 2026) and `streamlit` — neither are in `requirements.txt` and it is not deployed to Cloud Run

### `functions/` (if present)
- Early Node.js/Express backend — replaced by Python FastAPI
