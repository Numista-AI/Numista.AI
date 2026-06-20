import os
import logging
from dotenv import load_dotenv

# Setup logging for backend tracking/auditing
logger = logging.getLogger(__name__)

# Load environment variables from a .env file (if present)
load_dotenv()

def load_stripe_keys():
    """
    Safely loads Stripe API keys from the application environment (os.environ)
    or falls back to Streamlit's st.secrets if Streamlit is available in the current context.

    This function is designed to handle missing credentials gracefully by logging
    actionable warnings rather than crashing the application startup.

    Returns:
        dict: A dictionary containing 'publishable_key' and 'secret_key'.
              Values will be None if loading fails.
    """
    stripe_keys = {
        "publishable_key": None,
        "secret_key": None
    }
    
    # 1. Primary Attempt: Load from Environment Variables (standard backend/.env method)
    pub_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    sec_key = os.environ.get("STRIPE_SECRET_KEY")
    
    # 2. Secondary Attempt: Fallback to Streamlit st.secrets (if run in Streamlit context)
    is_streamlit_context = False
    streamlit_error = None
    
    if not (pub_key and sec_key):
        try:
            import streamlit as st
            is_streamlit_context = True
            
            # Retrieve keys if they exist in Streamlit secrets
            if "STRIPE_PUBLISHABLE_KEY" in st.secrets:
                pub_key = pub_key or st.secrets["STRIPE_PUBLISHABLE_KEY"]
            if "STRIPE_SECRET_KEY" in st.secrets:
                sec_key = sec_key or st.secrets["STRIPE_SECRET_KEY"]
                
        except ImportError:
            # Streamlit is not installed in this environment, which is expected on production Cloud Run
            is_streamlit_context = False
        except Exception as se:
            streamlit_error = se
            
    # 3. Validation and SDK Initialization
    if pub_key and sec_key:
        # Basic validation to ensure the values are not empty strings
        if not pub_key.strip() or not sec_key.strip():
            logger.warning("Stripe keys found, but one or both are empty strings.")
            return stripe_keys
            
        # Ensure they are set in os.environ for global library compatibility
        os.environ["STRIPE_PUBLISHABLE_KEY"] = pub_key.strip()
        os.environ["STRIPE_SECRET_KEY"] = sec_key.strip()
        
        stripe_keys["publishable_key"] = pub_key.strip()
        stripe_keys["secret_key"] = sec_key.strip()
        
        # Configure Stripe Python SDK if installed
        try:
            import stripe
            stripe.api_key = stripe_keys["secret_key"]
            logger.info("Successfully configured Stripe SDK api_key.")
        except ImportError:
            logger.debug("Stripe SDK is not installed. Skipping direct stripe.api_key assignment.")
            
        return stripe_keys
        
    else:
        # Construct error details
        missing_vars = []
        if not pub_key:
            missing_vars.append("STRIPE_PUBLISHABLE_KEY")
        if not sec_key:
            missing_vars.append("STRIPE_SECRET_KEY")
        
        error_msg = f"Missing Stripe keys in environment variables: {', '.join(missing_vars)}"
        logger.warning(error_msg)
        
        # If running in Streamlit, show the diagnostic warning in the UI
        if is_streamlit_context:
            try:
                import streamlit as st
                st.warning("⚠️ **Stripe Configuration Missing or Incomplete**")
                st.markdown(
                    f"""
                    We encountered an issue loading the Stripe API keys:
                    `Error: {error_msg}`
                    
                    Please ensure you have configured your local development secrets file:
                    1. Create or open the secrets file at `.streamlit/secrets.toml` in your project root.
                    2. Add the following key-value pairs using your Stripe test keys:
                    ```toml
                    STRIPE_PUBLISHABLE_KEY = "pk_test_..."
                    STRIPE_SECRET_KEY = "sk_test_..."
                    ```
                    3. Save the file and restart your Streamlit app.
                    """
                )
            except Exception as ui_err:
                logger.error(f"Failed to render Streamlit warning: {ui_err}")
                
        return stripe_keys

# Standalone validator entrypoint
if __name__ == "__main__":
    # Check if we can run Streamlit testing CLI/UI or fallback to basic terminal print
    try:
        import streamlit as st
        
        # Streamlit is available, run the visual validation dashboard
        st.set_page_config(page_title="Stripe Key Validator", page_icon="💳", layout="centered")
        st.title("💳 Stripe Key Validation Tool")
        st.write("Checking credentials in both environment variables (`.env`) and `st.secrets`...")
        
        st.divider()
        
        keys = load_stripe_keys()
        
        if keys["publishable_key"] and keys["secret_key"]:
            st.success("🎉 **Stripe keys loaded successfully!**")
            masked_pub = keys["publishable_key"][:12] + "..." + keys["publishable_key"][-8:]
            masked_sec = keys["secret_key"][:12] + "..." + keys["secret_key"][-8:]
            st.info(
                f"""
                **Loaded Keys (Masked):**
                - **STRIPE_PUBLISHABLE_KEY**: `{masked_pub}`
                - **STRIPE_SECRET_KEY**: `{masked_sec}`
                """
            )
    except ImportError:
        # Fallback to standard command-line validation (for FastAPI/Cloud Run environments)
        print("=" * 60)
        print("💳 Stripe Keys CLI Validator (FastAPI Backend)")
        print("=" * 60)
        keys = load_stripe_keys()
        if keys["publishable_key"] and keys["secret_key"]:
            masked_pub = keys["publishable_key"][:12] + "..." + keys["publishable_key"][-8:]
            masked_sec = keys["secret_key"][:12] + "..." + keys["secret_key"][-8:]
            print(f"[SUCCESS] Stripe keys loaded successfully!")
            print(f"  - STRIPE_PUBLISHABLE_KEY: {masked_pub}")
            print(f"  - STRIPE_SECRET_KEY:      {masked_sec}")
        else:
            print("[WARNING] Stripe keys are not configured. Check your '.env' file.")
        print("=" * 60)
