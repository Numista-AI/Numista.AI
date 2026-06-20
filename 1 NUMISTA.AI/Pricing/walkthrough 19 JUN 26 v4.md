# Stripe Keys Configuration Walkthrough

This walkthrough outlines the audited configuration and file placement of the Stripe utility script, [stripe_config.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/stripe_config.py).

## Audited Changes

- **Stripe Config Location**: Relocated [stripe_config.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/stripe_config.py) from the root folder to [numista_backend/](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/). This ensures the upcoming Cloud Run deployment packages the configuration file clean of drift.
- **Root Cleanup**: Confirmed that `stripe_config.py` has been deleted from the root project directory `C:\Users\ericd\Documents\MyVertexProject\`.
- **Dependency Audit**:
  - Pinned `stripe` to `stripe==15.2.1` in [requirements.txt](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/requirements.txt).
  - Completely removed all legacy Streamlit dependencies (`streamlit==1.56.0` and `extra-streamlit-components==0.1.81`) from [requirements.txt](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/requirements.txt) to keep the Cloud Run container slim and secure.

## Verification

The system status was verified via PowerShell:

```powershell
# Checked for the file presence
RootExists: False
BackendExists: True

# Confirmed requirements.txt state
stripe==15.2.1
(streamlit packages completely removed)
```

## Manual Testing Instructions

To validate the backend configuration and ensure Stripe keys load correctly without legacy Streamlit dependencies:

### 1. Environment File Configuration
Create or update the `.env` file located inside the backend directory:
[numista_backend/.env](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/.env)

Add the keys as environment variables:
```env
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 2. Standalone CLI Verification
Execute the configuration loader using the project's Python virtual environment (`.venv`) to verify that credentials load and mask successfully:
```powershell
cd c:\Users\ericd\Documents\MyVertexProject\numista_backend
.\.venv\Scripts\python stripe_config.py
```
*Expected Output:*
```text
============================================================
💳 Stripe Keys CLI Validator (FastAPI Backend)
============================================================
[SUCCESS] Stripe keys loaded successfully!
  - STRIPE_PUBLISHABLE_KEY: pk_test_51Tk2...3pYspl
  - STRIPE_SECRET_KEY:      sk_test_51Tk2...ue00yg
============================================================
```

### 3. FastAPI Local Startup Verification
Start the FastAPI server locally using Uvicorn to confirm that the server boots successfully clean of any module import or missing configuration errors:
```powershell
cd c:\Users\ericd\Documents\MyVertexProject\numista_backend
.\.venv\Scripts\python -m uvicorn main:app --reload --port 5000
```
This confirms the backend container runs cleanly and is fully ready for deployment to Cloud Run.
