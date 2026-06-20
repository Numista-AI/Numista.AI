# Migration of Stripe Billing Infrastructure to FastAPI

This plan outlines the steps required to migrate the billing infrastructure in `numista_backend` from Streamlit secrets to environment variables, refactor the core configuration files, implement FastAPI-compatible error handling for subscription limits, and verify the changes.

## Proposed Changes

### Configuration & Credentials

#### [NEW] [stripe_config.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/stripe_config.py)
- Create a new config loader using `python-dotenv` and `os.getenv` to pull Stripe keys.
- Safely check for required keys (`STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`) and raise a detailed `ValueError` if any are missing or empty.
- Configure `stripe.api_key` programmatically if `stripe` is installed.

#### [MODIFY] [.env](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/.env)
- Append the following Stripe test credentials to the existing `.env` file in the `numista_backend` folder:
  - `STRIPE_PUBLISHABLE_KEY="pk_test_REPLACE_ME"`
  - `STRIPE_SECRET_KEY="sk_test_REPLACE_ME"`

---

### Billing & Gatekeeping Logic

#### [MODIFY] [tier_gatekeeper.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py)
- Completely remove Streamlit (`st.secrets` and `import streamlit`) dependencies.
- Import `load_stripe_keys` from `stripe_config.py` and call it to initialize Stripe credentials.
- Update `check_and_increment_daily_usage` and `check_and_enforce_coin_limit` to check if the user profile document has `power_user: true` and bypass the daily usage counts and coin limits if so.
- Refactor `check_and_enforce_coin_limit` to enforce standard coin limits and, if a user is blocked, raise a FastAPI `HTTPException` with status code `403 Forbidden` returning a structured JSON detail containing:
  - User's subscription tier
  - Coin count and limit stats
  - A custom Stripe checkout link generated with `allow_promotion_codes=True`.

---

### Verification & Testing

#### [MODIFY] [test_tier_gatekeeper.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/test_tier_gatekeeper.py)
- Replace legacy Streamlit mocking with setting environment variables directly via `os.environ` before importing modules under test.
- Add test coverage for `check_and_enforce_coin_limit` asserting:
  - Access is allowed under limits.
  - Access is allowed for power users.
  - An `HTTPException(status_code=403)` is raised when standard limits are exceeded, containing correct detail structure.

---

## Verification Plan

### Automated Tests
We will execute the unit tests from the `numista_backend` directory using python's built-in `unittest` runner:
- `python -m unittest test_tier_gatekeeper.py`
