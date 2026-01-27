import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta
import extra_streamlit_components as stx

# --- CONFIGURATION ---
load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"

st.set_page_config(page_title="Numista.AI", layout="wide", initial_sidebar_state="expanded")

# --- CREDENTIALS HARD FIX ---
# Explicitly load service account to avoid "Reauthentication needed" / ADC errors
key_path = "serviceAccountKey.json.json"
try:
    cred_admin = credentials.Certificate(key_path)
    cred_firestore = service_account.Credentials.from_service_account_file(key_path)

    # 1. Init Firebase Admin
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred_admin)

    # 2. Init Firestore Client with explicit creds
    db = firestore.Client(credentials=cred_firestore, project=PROJECT_ID)
except Exception as e:
    # Fallback if file missing (though we verified it exists)
    print(f"Auth Init Error: {e}")
    if not firebase_admin._apps: firebase_admin.initialize_app()
    db = firestore.Client(project=PROJECT_ID)

# --- FIREBASE CLIENT API KEY ---
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY", "")

# --- CSS STYLING ---
st.markdown("""
<style>
    /* 1. BRANDING: Font & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Dark Navy Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a; /* Slate-900 */
        border-right: 1px solid #1e293b;
    }
    
    /* Sidebar Text Colors */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #94a3b8; /* Slate-400 */
        font-weight: 500;
        font-size: 14px;
    }
    
    /* Hide Default Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden;}

    /* Logo Pulse Animation */
    @keyframes pulse-glow {
        0% { filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.4)); opacity: 0.9; }
        50% { filter: drop-shadow(0 0 20px rgba(14, 165, 233, 0.8)); opacity: 1; }
        100% { filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.4)); opacity: 0.9; }
    }
    img[src*="Numista.AI"] {
        animation: pulse-glow 3s infinite ease-in-out;
    }

    /* 2. LAYOUT FIXES (Flush Iframe) */
    [data-testid="stSidebar"] + section { padding: 0; }
    .main .block-container { padding: 0; max-width: 100%; }
    iframe { border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- URL CONSTANTS (With ?embed=true) ---
# Main App serves for Dashboard, Collection, Inventory, wishlist
MAIN_APP_URL = "https://numista-app-568985927038.us-west1.run.app/" # Base URL

# Add New Coins Sub-Apps (Nested)
# We will append ?page=... &user_email=... dynamically
SCAN_INVOICE_URL = MAIN_APP_URL 
MANUAL_ENTRY_URL = MAIN_APP_URL
EXCEL_UPLOAD_URL = MAIN_APP_URL

# --- SIDEBAR NAV ---
import extra_streamlit_components as stx

# --- LOGIN & COOKIE LOGIC ---
# We instantiate this directly to avoid CachedWidgetWarning
cookie_manager = stx.CookieManager(key="numista_shell_cookies")

def check_login_shell():
    # 1. Check Session
    if st.session_state.get('user_email'):
        return True
    
    # 2. Check Cookie
    try:
        cookies = cookie_manager.get_all()
        if "numista_auth_v1" in cookies:
            st.session_state.user_email = cookies["numista_auth_v1"]
            return True
    except:
        pass
    
    return False

# --- AUTHENTICATION HELPERS ---
def send_password_reset_email(email):
    if not FIREBASE_WEB_API_KEY:
        st.error("Missing Firebase Web API Key. Cannot send reset email.")
        return False
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
    payload = {"requestType": "PASSWORD_RESET", "email": email}
    resp = requests.post(url, json=payload)
    
    if resp.status_code == 200:
        return resp.json()
    else:
        try:
            err = resp.json()['error']['message']
        except:
            err = str(resp.status_code)
        st.error(f"Error sending email: {err}")
        return False

def verify_firebase_login(email, password):
    if not FIREBASE_WEB_API_KEY:
        st.error("Missing Firebase Web API Key. Cannot verify login.")
        return False
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    resp = requests.post(url, json=payload)
    
    if resp.status_code == 200:
        return True, resp.json()
    else:
        return False, None

def update_user_pin(email, new_pin):
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, password=new_pin)
        return True, "Success"
    except Exception as e:
        err_msg = str(e)
        # If user not found, create them
        if "No user record found" in err_msg or "NOT_FOUND" in err_msg:
            try:
                auth.create_user(email=email, password=new_pin)
                return True, "Account Created & PIN Set"
            except Exception as e2:
                return False, f"Creation Failed: {str(e2)}"
        return False, err_msg

def get_collection_csv(email):
    path = f"users/{email}/coins"
    try:
        # Use existing firestore client 'db'
        docs = db.collection(path).stream()
        items = []
        for doc in docs:
            item = doc.to_dict()
            items.append(item)
        
        if not items:
            return None
            
        df = pd.DataFrame(items)
        return df.to_csv(index=False).encode('utf-8')
    except Exception as e:
        return None

def login_screen_shell():
    col1, x_col, col3 = st.columns([1, 2, 1])
    with x_col:
        try:
            st.image("public/Numista.AI Logo.svg", width=200)
        except:
             st.title("Numista.AI")
    st.markdown("<h1 style='text-align: center;'>Numista.AI <span class='beta-tag'>BETA v2.6 (Shell)</span></h1>", unsafe_allow_html=True)
    st.write("") # Padding
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("🔐 Secure Login (Shell)")
        
        # --- PASSWORD RESET FLOW ---
        if st.session_state.get('forgot_pin_mode'):
            st.subheader("Reset PIN")
            reset_email = st.text_input("Enter your account email:", key="reset_email_input")
            if st.button("Send Reset Link", use_container_width=True):
                if "@" in reset_email:
                    if send_password_reset_email(reset_email):
                        st.success("✅ A reset link has been sent to your email. Click it to set a new 6-digit PIN.")
                        st.info("Once set, come back here and log in with your new PIN.")
                else:
                    st.error("Please enter a valid email.")
            
            if st.button("Back to Login", type="secondary", use_container_width=True):
                st.session_state.forgot_pin_mode = False
                st.rerun()
            return
            
        # --- GUEST BUTTON ---
        if st.button("👤 Continue as Guest", use_container_width=True):
            st.session_state.user_email = "guest@numista.ai"
            st.session_state.guest_mode = True
            st.rerun()
        
        st.write("--- OR ---")
        
        # --- SECURITY UPDATE FLOW (TRANSITION) ---
        if st.session_state.get('security_update_mode'):
            st.warning("⚠️ Security Update Required")
            st.write("We are moving to secure 6-digit PINs. Please set your new PIN now.")
            
            new_pin = st.text_input("Create New 6-Digit PIN:", type="password", max_chars=6)
            confirm_pin = st.text_input("Confirm PIN:", type="password", max_chars=6)
            
            # --- BACKUP FEATURE ---
            email_pending = st.session_state.get('pending_email')
            if email_pending:
                csv_data = get_collection_csv(email_pending)
                if csv_data:
                    st.download_button(
                        label="📂 Backup My Collection (CSV)",
                        data=csv_data,
                        file_name=f"numista_backup_{email_pending}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        help="Download your full collection data before updating.",
                        use_container_width=True,
                        key="backup_csv_btn"
                    )
            
            if st.button("Update PIN & Login", type="primary", use_container_width=True):
                if len(new_pin) < 6:
                    st.error("PIN must be at least 6 digits.")
                elif new_pin != confirm_pin:
                    st.error("PINs do not match.")
                else:
                    email = st.session_state.get('pending_email')
                    success, msg = update_user_pin(email, new_pin)
                    if success:
                        st.balloons()
                        st.success("PIN Updated Successfully!")
                        
                        # Log them in
                        st.session_state.user_email = email
                        st.session_state.security_update_mode = False
                        st.session_state.pending_email = None
                        
                        cookie_manager.set("numista_auth_v1", email, expires_at=datetime.now() + timedelta(days=30))
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Update Failed: {msg}")
            
            if st.button("Cancel"):
                st.session_state.security_update_mode = False
                st.rerun()
            return

        # --- NORMAL LOGIN ---
        email = st.text_input("Enter your verified email address:")
        st.caption("ℹ️ Default Beta PIN: 1111")
        pin = st.text_input("Enter Access PIN:", type="password")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Access Vault", use_container_width=True):
                clean_email = email.lower().strip()
                
                # 1. LEGACY/TRANSITION CHECK
                if pin == "1111" and "@" in email:
                    # Trigger Security Update
                    st.session_state.pending_email = clean_email
                    st.session_state.security_update_mode = True
                    st.rerun()
                
                # 2. REAL AUTH CHECK
                elif "@" in clean_email and len(pin) >= 6:
                    success, auth_data = verify_firebase_login(clean_email, pin)
                    if success:
                        st.session_state.user_email = clean_email
                         # Store auth data if needed
                        if auth_data and 'idToken' in auth_data:
                            st.session_state.auth_token = auth_data['idToken']
                            
                        if not st.session_state.get('guest_mode'):
                            cookie_manager.set("numista_auth_v1", clean_email, expires_at=datetime.now() + timedelta(days=30))
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Incorrect Email or PIN.")
                
                else:
                    st.error("Invalid Login Credentials.")
        
        with c2:
            if st.button("Forgot PIN?", type="secondary", use_container_width=True):
                st.session_state.forgot_pin_mode = True
                st.rerun()

def logout_shell():
    cookie_manager.delete("numista_auth_v1")
    st.session_state.user_email = None
    st.session_state.guest_mode = False
    st.rerun()

# --- MAIN LOGIC ---
if not check_login_shell():
    login_screen_shell()
else:
    # --- AUTH PARAMETER CONSTRUCTION ---
    user_email = st.session_state.user_email
    # Simple 'shared secret' auth token for now (matching the PIN)
    auth_token = "1111" 
    
    # helper to ensure we always have the right params
    def build_auth_query():
        return f"&user_email={user_email}&auth_token={auth_token}&embed=true"

    auth_params = build_auth_query()

    # --- SIDEBAR NAV ---
    with st.sidebar:
        try:
            st.image("public/Numista.AI Logo.svg", width=220)
        except:
            st.title("Numista.AI") # Fallback
            
        st.write(f"Vault: **{user_email}**")
        
        # 2. Unified Sidebar Structure
        main_nav = st.radio(
            "Menu",
            ["Home Dashboard", "My Collection", "Add New Coins", "Check Inventory", "My Wishlist", "Our Team"],
            label_visibility="collapsed"
        )
        
        # 3. Nested Navigation Logic
        if main_nav == "Add New Coins":
            st.divider()
            st.caption("Select Entry Method:")
            # Sub-selection
            add_method = st.radio(
                "Method",
                ["Scan Invoice", "Manual Entry", "Excel/CSV Upload"],
                label_visibility="collapsed"
            )
            
            if add_method == "Scan Invoice": final_url = f"{SCAN_INVOICE_URL}?page=add_scan{auth_params}"
            elif add_method == "Manual Entry": final_url = f"{MANUAL_ENTRY_URL}?page=add_manual{auth_params}"
            elif add_method == "Excel/CSV Upload": final_url = f"{EXCEL_UPLOAD_URL}?page=add_upload{auth_params}"
            
        elif main_nav == "Home Dashboard": final_url = f"{MAIN_APP_URL}?page=home{auth_params}"
        elif main_nav == "My Collection": final_url = f"{MAIN_APP_URL}?page=collection{auth_params}"
        elif main_nav == "Check Inventory": final_url = f"{MAIN_APP_URL}?page=inventory{auth_params}"
        elif main_nav == "My Wishlist": final_url = f"{MAIN_APP_URL}?page=wishlist{auth_params}"
        elif main_nav == "Our Team": final_url = f"{MAIN_APP_URL}?page=team{auth_params}"
        else: final_url = f"{MAIN_APP_URL}?page=home{auth_params}"
    
        st.divider()
        if st.button("Log Out"): logout_shell()

    # --- MAIN CONTENT ---
    components.iframe(final_url, height=1000, scrolling=True)
