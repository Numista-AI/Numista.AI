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

### Manual Testing Instructions
To test this configuration loader locally:
1. Navigate to the project root.
2. In your terminal, run:
   ```bash
   python -m streamlit run numista_backend/stripe_config.py
   ```
3. Verify that the diagnostics page correctly loads your masked Stripe credentials from `.streamlit/secrets.toml`.
