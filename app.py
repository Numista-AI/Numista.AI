import streamlit as st
import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore
import json
import uuid
import time
from datetime import datetime, timedelta
import base64
import os
import extra_streamlit_components as stx
from contextlib import contextmanager
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.cloud import storage
import requests
import firebase_admin
from firebase_admin import auth, credentials
from dotenv import load_dotenv

from google.oauth2 import service_account

# --- CONFIGURATION ---
load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "us-central1"
st.set_page_config(page_title="Numista.AI", layout="wide", initial_sidebar_state="collapsed")

# --- HISTORY POPUP HANDLER (BEFORE SIDEBAR/AUTH) ---
if "program_history" in st.query_params:
    prog_id = st.query_params["program_history"]
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            header { visibility: hidden !important; }
            .stApp { background: white !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # We need US_PROGRAMS but it's defined later. Use basic search or move definition up.
    # Since we can't easily move 200 lines up without reading them, let's just define the handler here 
    # and execute it AFTER US_PROGRAMS is defined, by setting a flag.
    # OR better: Just put the handler block AFTER the imports and definitions, but BEFORE the main UI render loop.
    # Let's set a session state flag to trigger "Popup Mode" rendering later in the script.
    st.session_state['POPUP_MODE_ID'] = prog_id

st.sidebar.caption("v2.6 - DEBUG MODE")

# Simple Sidebar Suppression (Just in case Streamlit tries to render it)
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
# Use Explicit Service Account Key if available to avoid 403 errors on Vertex
key_path = "serviceAccountKey.json.json"
vertex_creds = None
if os.path.exists(key_path):
    try:
        vertex_creds = service_account.Credentials.from_service_account_file(key_path)
    except: pass

if "vertex_init" not in st.session_state:
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=vertex_creds)
    st.session_state.vertex_init = True
    
# --- CREDENTIALS (ADC) ---
# Use Application Default Credentials (works on Cloud Run & Local with `gcloud auth application-default login`)
import google.auth

# 1. Init Firebase Admin
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={'projectId': PROJECT_ID})

# 2. Init Firestore Client
# google.auth.default() automatically finds credentials
credentials, project = google.auth.default()
db = firestore.Client(credentials=credentials, project=PROJECT_ID)

model = GenerativeModel("gemini-2.5-flash")

# --- FIREBASE CLIENT API KEY ---
# Required for Client-Side Operations from Python (Login, Reset Password)
# TODO: User must add this to .env or replace below
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY", "") 

# --- COOKIE MANAGER (FIXED: NO CACHE) ---
# We instantiate this directly to avoid CachedWidgetWarning
# FIX: Only load if NO query params (Direct Access) to avoid iframe errors
if "user_email" in st.query_params:
    cookie_manager = None
else:
    try:
        cookie_manager = stx.CookieManager(key="numista_cookies")
    except:
        cookie_manager = None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* GLOBAL APP BACKGROUND & VIGNETTE */
    .stApp {
        background-color: #f8fafc; /* Light Slate-50 */
    }
    .stApp:before {
        content: "";
        position: fixed;
        inset: 0;
        background: radial-gradient(circle at top right, rgba(14, 165, 233, 0.15), transparent 40%),
                    radial-gradient(circle at bottom left, rgba(14, 165, 233, 0.15), transparent 40%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* MAXIMIZE SCREEN WIDTH */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 99% !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0f172a; /* Slate-900 */
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #94a3b8; /* Slate-400 */
        font-weight: 500;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    /* Force Radio Button Text Color in Sidebar */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #e2e8f0 !important; /* Slate-200 */
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        color: #e2e8f0 !important;
    }
    
    /* DASHBOARD HEADERS */
    .dash-title { 
        font-family: 'Inter', sans-serif;
        font-size: 28px; 
        font-weight: 800; 
        font-style: italic;
        color: #0f172a; /* Slate-900 */
        margin-bottom: 0px; 
        text-transform: uppercase;
        letter-spacing: -0.5px;
    }
    .dash-subtitle { 
        font-family: 'Inter', sans-serif;
        font-size: 14px; 
        font-weight: 600; 
        color: #64748b; /* Slate-500 */
        margin-top: -5px; 
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* PORTFOLIO WIDGET */
    .portfolio-label { 
        font-size: 14px; 
        font-weight: 600; 
        color: #64748b; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: right; 
    }
    .portfolio-value { 
        font-size: 32px; 
        font-weight: 800; 
        color: #10b981; /* Emerald-500 */
        text-align: right; 
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }

    /* CARDS & METRICS */
    .metric-box { 
        background-color: white; 
        padding: 24px; 
        border-radius: 24px; /* Highly rounded */
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
        text-align: center; 
        transition: transform 0.2s;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .metric-value { 
        font-size: 28px; 
        font-weight: 800; 
        color: #0f172a; 
    }

    /* BUTTONS */
    div.stButton > button {
        border-radius: 16px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    /* Primary / Generic buttons styling alignment */
    
    .beta-tag { 
        background-color: #3b82f6; /* Blue-500 */
        color: white; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-size: 10px; 
        font-weight: 700; 
        vertical-align: middle; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
    }
    
    .coming-soon { color: #888; font-style: italic; font-size: 12px; background: #f0f0f0; padding: 2px 6px; border-radius: 4px; }
    
    /* LOGO ANIMATION & GLOW */
    @keyframes pulse-glow {
        0% { filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.4)); opacity: 0.9; }
        50% { filter: drop-shadow(0 0 20px rgba(14, 165, 233, 0.8)); opacity: 1; }
        100% { filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.4)); opacity: 0.9; }
    }
    img[src*="Numista.AI"] {
        animation: pulse-glow 3s infinite ease-in-out;
    }

    /* Electric Blue & Sparkle Text Animation */
    @keyframes shine {
        0% { background-position: -200%; }
        100% { background-position: 200%; }
    }
    .electric-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(120deg, #3b82f6 30%, #bfdbfe 38%, #3b82f6 48%);
        background-size: 200% 100%;
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        animation: shine 4s linear infinite;
        text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }

    /* GRADE PILL & TABLE STYLES */
    .grade-pill {
        padding: 2px 8px; 
        border-radius: 12px; 
        background-color: #e1f5fe; 
        color: #01579b; 
        font-size: 12px; 
        font-weight: bold;
        border: 1px solid #01579b;
        display: inline-block;
        white-space: nowrap;
    }
    .issue-main {
        font-weight: 700;
        color: #0f172a;
        font-size: 14px;
        line-height: 1.2;
    }
    .issue-sub {
        font-size: 11px;
        color: #64748b;
        line-height: 1.2;
    }
    .condensed-row {
        margin: 0px; padding: 0px;
    }
    
    /* STICKY HEADER & FOOTER */
    .sticky-header {
        position: sticky;
        top: 0;
        background-color: #f8fafc; /* Match App BG */
        z-index: 100;
        padding-top: 10px;
        padding-bottom: 5px;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .sticky-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 15px;
        border-top: 1px solid #e2e8f0;
        z-index: 1000;
        box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
</style>
""", unsafe_allow_html=True)


# --- AUTHENTICATION LOGIC ---
def check_login():
    # 0. Check for URL Auth Parameters (Unified Auth)
    qp = st.query_params
    if 'user_email' in qp and 'auth_token' in qp:
        # Verify Token (Simple Shared Secret for now)
        if qp['auth_token'] == "1111":
            st.session_state.user_email = qp['user_email']
            if qp['user_email'] == "guest@numista.ai":
                st.session_state.guest_mode = True
            return True

    # 1. Check Session
    if st.session_state.get('user_email'):
        return True
    
    # 2. Check Cookie (Wait for it to load)
    if cookie_manager:
        try:
            cookies = cookie_manager.get_all()
            if "numista_auth_v1" in cookies:
                st.session_state.user_email = cookies["numista_auth_v1"]
                return True
        except:
            pass
    
    return False

def get_dummy_collection():
    data = [
        {"id": "guest_1", "Year": 1909, "Country": "USA", "Denomination": "Lincoln Cent", "Mint Mark": "S", "Condition": "VF-20", "Cost": "$45.00", "AI Estimated Value": "$150.00", "Numismatic Report": "Key date coin, famous VDB design.", "deep_dive_status": "COMPLETED"},
        {"id": "guest_2", "Year": 1881, "Country": "USA", "Denomination": "Morgan Dollar", "Mint Mark": "CC", "Condition": "MS-63", "Cost": "$250.00", "AI Estimated Value": "$650.00", "Numismatic Report": "Carson City mint, highly desirable.", "deep_dive_status": "COMPLETED"},
        {"id": "guest_3", "Year": 1916, "Country": "USA", "Denomination": "Mercury Dime", "Mint Mark": "D", "Condition": "G-4", "Cost": "$500.00", "AI Estimated Value": "$800.00", "Numismatic Report": "Key date, low mintage.", "deep_dive_status": "COMPLETED"},
        {"id": "guest_4", "Year": 1986, "Country": "USA", "Denomination": "Silver Eagle", "Mint Mark": "", "Condition": "Proof", "Cost": "$25.00", "AI Estimated Value": "$75.00", "Numismatic Report": "First year of issue.", "deep_dive_status": "COMPLETED"},
        {"id": "guest_5", "Year": 1794, "Country": "USA", "Denomination": "Flowing Hair Dollar", "Mint Mark": "", "Condition": "VF-25", "Cost": "$0.00", "AI Estimated Value": "$150,000.00", "Numismatic Report": "Museum quality replica for testing.", "deep_dive_status": "COMPLETED"}
    ]
    df = pd.DataFrame(data)
    # Ensure all columns exist
    system_cols = ['id', 'deep_dive_status', 'Numismatic Report', 'potentialVariety', 'imageUrlObverse', 'imageUrlReverse']
    final_cols = DISPLAY_ORDER + [c for c in system_cols if c not in DISPLAY_ORDER]
    for c in final_cols:
        if c not in df.columns: df[c] = None
    return df[final_cols]


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
        # st.error might not render if outside context, but okay here
        return None

def login_screen():
    # --- LOGO & TITLE BLOCK ---
    logo_path = "public/Numista.AI Logo.svg"
    try:
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        img_tag = f'<img src="data:image/svg+xml;base64,{data}" width="300" style="margin-bottom: 20px;">'
    except:
        img_tag = "" 

    st.markdown(f"""
        <div style='text-align: center;'>
            {img_tag}
            <h1 style='font-size: 60px; margin-bottom: 0px; margin-top: 10px;'><span class='electric-text'>Numista.AI</span></h1>
            <h3 style='margin-top: -15px; color: #475569;'>BETA v2.6</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #64748b; font-size: 14px;'>A Coin Collection Management System</p>", unsafe_allow_html=True)
    st.write("") # Padding
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # Removed Secure Login Info

        
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
        # Removed Default Beta PIN text
        pin = st.text_input("Enter Access PIN:", type="password")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Access System", use_container_width=True):
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
                        # Store auth data if needed for simple token verification later
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

def logout():
    cookie_manager.delete("numista_auth_v1")
    st.session_state.user_email = None
    st.session_state.guest_mode = False
    st.rerun()

# --- HELPER FUNCTIONS ---
def get_user_collection_path():
    if st.session_state.get('guest_mode'): return None
    email = st.session_state.get('user_email')
    if not email: return None
    return f"users/{email}/coins"

# --- GCS QUEUE HELPERS ---
from google.cloud import storage

def get_bucket():
    # Helper to get bucket object
    if vertex_creds:
        client = storage.Client(credentials=vertex_creds, project=PROJECT_ID)
    else:
        client = storage.Client(project=PROJECT_ID)
    # Assume default bucket is the project's appspot or defined one
    # For Cloud Run, 'PROJECT_ID.appspot.com' is standard default for Firebase
    # bucket_name = f"{PROJECT_ID}.appspot.com" 
    bucket_name = "numista-uploads-studio-9101802118-8c9a8"
    return client.bucket(bucket_name)

def list_queue_files(prefix="invoices/queue/"):
    try:
        bucket = get_bucket()
        blobs = list(bucket.list_blobs(prefix=prefix))
        # Filter out the folder itself if returned
        return [b for b in blobs if not b.name.endswith('/')]
    except Exception as e:
        print(f"Queue List Error: {e}")
        return []

def move_blob(blob, dest_name):
    try:
        bucket = get_bucket()
        bucket.rename_blob(blob, dest_name)
    except Exception as e:
        print(f"Move Error: {e}")

def upload_to_gcs_queue(file_obj):
    try:
        bucket = get_bucket()
        blob_name = f"invoices/queue/{uuid.uuid4()}_{file_obj.name}"
        blob = bucket.blob(blob_name)
        file_obj.seek(0)
        blob.upload_from_file(file_obj, content_type=file_obj.type)
        print(f"DEBUG: Successfully uploaded {blob_name}")
        return True, None
    except Exception as e:
        print(f"DEBUG: Upload failed: {e}")
        return False, str(e)

@contextmanager
def numista_loader(message="AI is analyzing data..."):
    placeholder = st.empty()
    with placeholder.container():
        st.write("")
        st.write("")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            # The CSS global rule img[src*="Numista.AI"] will apply the pulse automatically
            st.image("public/Numista.AI Logo.svg", width=150)
            st.markdown(f"<div style='text-align: center; color: #666; font-style: italic; margin-top: 10px;'>{message}</div>", unsafe_allow_html=True)
        st.write("")
        st.write("")
    try:
        yield
    finally:
        placeholder.empty()

COIN_STANDARDS = {
    "denominations": {
        "Penny": ["1c", "Cent", "One Cent", "Lincoln Cent", "Indian Head Cent"],
        "Nickel": ["5c", "Five Cents", "Half Dime", "V Nickel", "Buffalo Nickel", "Jefferson Nickel"],
        "Dime": ["10c", "Ten Cents", "Mercury Dime", "Roosevelt Dime"],
        "Quarter": ["25c", "Quarter Dollar", "Washington Quarter", "State Quarter"],
        "Half Dollar": ["50c", "Fifty Cents", "Kennedy Half", "Franklin Half", "Walking Liberty"],
        "Dollar": ["$1", "Silver Dollar", "Morgan Dollar", "Peace Dollar", "Eisenhower Dollar", "SBA Dollar", "Sacagawea"]
    },
    "metals": {
        "90% Silver": ["90% Silver, 10% Copper", "Fine Silver", "Silver Clad (.900)"],
        "40% Silver": ["40% Silver Clad", "Silver Clad (.400)"],
        "Cupro-Nickel": ["Copper-Nickel", "75% Copper, 25% Nickel", "Nickel Clad", "Clad"],
        "Copper-plated Zinc": ["97.5% Zinc, 2.5% Copper", "Zinc"],
        "Manganese-Brass": ["Golden Dollar Metal", "88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni"]
    }
}



US_PROGRAMS = {
    "Circulating Coin Programs": [
        {"id": "bicentennial", "name": "Bicentennial Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/bicentennial-coins", "years": "1976", "coins": ["Quarter", "Half Dollar", "Dollar"]},
        {"id": "50state", "name": "50 State Quarters Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/50-state-quarters", "years": "1999-2008", "coins": ['Delaware', 'Pennsylvania', 'New Jersey', 'Georgia', 'Connecticut', 'Massachusetts', 'Maryland', 'South Carolina', 'New Hampshire', 'Virginia', 'New York', 'North Carolina', 'Rhode Island', 'Vermont', 'Kentucky', 'Tennessee', 'Ohio', 'Louisiana', 'Indiana', 'Mississippi', 'Illinois', 'Alabama', 'Maine', 'Missouri', 'Arkansas', 'Michigan', 'Florida', 'Texas', 'Iowa', 'Wisconsin', 'California', 'Minnesota', 'Oregon', 'Kansas', 'West Virginia', 'Nevada', 'Nebraska', 'Colorado', 'North Dakota', 'South Dakota', 'Montana', 'Washington', 'Idaho', 'Wyoming', 'Utah', 'Oklahoma', 'New Mexico', 'Arizona', 'Alaska', 'Hawaii']},
        {"id": "dc_territories", "name": "District of Columbia and U.S. Territories Quarters", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/dc-and-us-territories", "years": "2009", "coins": ["District of Columbia", "Puerto Rico", "Guam", "American Samoa", "U.S. Virgin Islands", "Northern Mariana Islands"]},
        {"id": "westward", "name": "Westward Journey Nickel Series", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/westward-journey-nickel-series", "years": "2004-2005", "coins": ["Peace Medal", "Keelboat", "American Bison", "Ocean in View"]},
        {"id": "lincoln", "name": "Lincoln Bicentennial One-Cent Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/lincoln-bicentennial-one-cent", "years": "2009", "coins": ["Birth and Early Childhood", "Formative Years", "Professional Life", "Presidency"]},
        {"id": "sba", "name": "Susan B. Anthony Dollar", "url": "https://www.usmint.gov/coins/coin-medal-programs/circulating-coins/susan-b-anthony-dollar", "years": "1979-1981, 1999", "coins": ["1979-P", "1979-D", "1979-S", "1980-P", "1980-D", "1980-S", "1981-P", "1981-D", "1981-S", "1999-P", "1999-D"]},
        {"id": "sacagawea", "name": "Sacagawea Golden Dollar", "url": "https://www.usmint.gov/coins/coin-medal-programs/sacagawea-golden-dollar", "years": "2000-2008", "coins": ["2000-P", "2000-D", "2000-S", "2001-P", "2001-D", "2001-S", "2002-P", "2002-D", "2002-S", "2003-P", "2003-D", "2003-S", "2004-P", "2004-D", "2004-S", "2005-P", "2005-D", "2005-S", "2006-P", "2006-D", "2006-S", "2007-P", "2007-D", "2007-S", "2008-P", "2008-D", "2008-S"]},
        {"id": "atb", "name": "America the Beautiful Quarters Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/america-the-beautiful-quarters", "years": "2010-2021", "coins": ["Hot Springs", "Yellowstone", "Yosemite", "Grand Canyon", "Mount Hood", "Gettysburg", "Glacier", "Olympic", "Vicksburg", "Chickasaw", "El Yunque", "Chaco Culture", "Acadia", "Hawaii Volcanoes", "Denali", "White Mountain", "Perry's Victory", "Great Basin", "Fort McHenry", "Mount Rushmore", "Great Smoky Mountains", "Shenandoah", "Arches", "Great Sand Dunes", "Everglades", "Homestead", "Kisatchie", "Blue Ridge Parkway", "Bombay Hook", "Saratoga", "Shawnee", "Cumberland Gap", "Harpers Ferry", "Theodore Roosevelt", "Fort Moultrie", "Effigy Mounds", "Frederick Douglass", "Ozark", "Ellis Island", "George Rogers Clark", "Pictured Rocks", "Apostle Islands", "Voyageurs", "Cumberland Island", "Block Island", "Lowell", "American Memorial", "War in the Pacific", "San Antonio Missions", "Frank Church River of No Return", "National Park of American Samoa", "Weir Farm", "Salt River Bay", "Marsh-Billings-Rockefeller", "Tallgrass Prairie", "Tuskegee Airmen"]},
        {"id": "presidential", "name": "Presidential $1 Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/presidential-dollar-coin", "years": "2007-2016, 2020", "coins": ["Washington", "Adams", "Jefferson", "Madison", "Monroe", "J.Q. Adams", "Jackson", "Van Buren", "Harrison", "Tyler", "Polk", "Taylor", "Fillmore", "Pierce", "Buchanan", "Lincoln", "Johnson", "Grant", "Hayes", "Garfield", "Arthur", "Cleveland (1st)", "Harrison", "Cleveland (2nd)", "McKinley", "Roosevelt", "Taft", "Wilson", "Harding", "Coolidge", "Hoover", "F.D. Roosevelt", "Truman", "Eisenhower", "Kennedy", "Johnson", "Nixon", "Ford", "Reagan", "G.H.W. Bush"]},
        {"id": "native", "name": "Native American $1 Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/native-american-dollar-coins", "years": "2009-Present", "coins": ["Three Sisters (2009)", "Great Tree of Peace (2010)", "Wampanoag Treaty (2011)", "Trade Routes (2012)", "Delaware Treaty (2013)", "Native Hospitality (2014)", "Mohawk Ironworkers (2015)", "Code Talkers (2016)", "Sequoyah (2017)", "Jim Thorpe (2018)", "Space Program (2019)", "Elizabeth Peratrovich (2020)", "Military Service (2021)", "Ely S. Parker (2022)", "Maria Tallchief (2023)", "Indian Citizenship Act (2024)", "Northeast Tech (2025)"]},
        {"id": "innovation", "name": "American Innovation $1 Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-innovation-dollar-coins", "years": "2018-2032", "coins": ['Intro Coin', 'Delaware', 'Pennsylvania', 'New Jersey', 'Georgia', 'Connecticut', 'Massachusetts', 'Maryland', 'South Carolina', 'New Hampshire', 'Virginia', 'New York', 'North Carolina', 'Rhode Island', 'Vermont', 'Kentucky', 'Tennessee', 'Ohio', 'Louisiana', 'Indiana', 'Mississippi', 'Illinois', 'Alabama', 'Maine', 'Missouri', 'Arkansas', 'Michigan', 'Florida', 'Texas', 'Iowa', 'Wisconsin', 'California', 'Minnesota', 'Oregon', 'Kansas', 'West Virginia', 'Nevada', 'Nebraska', 'Colorado', 'North Dakota', 'South Dakota', 'Montana', 'Washington', 'Idaho', 'Wyoming', 'Utah', 'Oklahoma', 'New Mexico', 'Arizona', 'Alaska', 'Hawaii']},
        {"id": "women", "name": "American Women Quarters Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-women-quarters", "years": "2022-2025", "coins": ['Maya Angelou', 'Dr. Sally Ride', 'Wilma Mankiller', 'Adelina Otero-Warren', 'Anna May Wong', 'Bessie Coleman', 'Edith Kanakaʻole', 'Eleanor Roosevelt', 'Jovita Idar', 'Maria Tallchief', 'Rev. Dr. Pauli Murray', 'Patsy Takemoto Mink', 'Dr. Mary Edwards Walker', 'Celia Cruz', 'Zitkala-Ša']},
        {"id": "semiquin", "name": "2026 Semiquincentennial Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/semiquincentennial-coins", "years": "2026", "coins": ["Mayflower Compact Quarter (Pending)", "Revolutionary War Quarter (Pending)", "Declaration of Independence Quarter (Pending)", "U.S. Constitution Quarter (Pending)", "Gettysburg Address Quarter (Pending)"]}
    ],
    "Bullion and Investment Programs": [
        {"id": "ase", "name": "American Eagle Silver Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-eagle-silver-bullion-coins", "years": "1986-Present", "coins": ["Type 1 (1986-2021)", "Type 2 (2021-Present)"]},
        {"id": "age", "name": "American Eagle Gold Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-eagle-gold-bullion-coins", "years": "1986-Present", "coins": ["Type 1 (1986-2021)", "Type 2 (2021-Present)"]},
        {"id": "ape", "name": "American Eagle Platinum Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-eagle-platinum-bullion-coins", "years": "1997-Present", "coins": ["Proof Series", "Uncirculated Series", "Bullion"]},
        {"id": "apall", "name": "American Eagle Palladium Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-eagle-palladium-bullion-coins", "years": "2017-Present", "coins": ["Bullion", "Proof", "Reverse Proof", "Uncirculated"]},
        {"id": "buffalo", "name": "American Buffalo Gold Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-buffalo-coin", "years": "2006-Present", "coins": ["Bullion (1oz)", "Proof (1oz)", "Fractional (2008 Only)"]},
        {"id": "liberty", "name": "American Liberty High Relief Gold and Silver Medal Series", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/american-liberty-high-relief-gold-coins", "years": "2015-Present", "coins": ["2015 High Relief Gold", "2016 Silver Medal", "2017 Gold Coin", "2018 Gold Coin", "2019 High Relief Gold", "2019 Silver Medal", "2021 High Relief Gold", "2022 Silver Medal", "2023 High Relief Gold", "2024 Silver Medal"]},
        {"id": "spouse", "name": "First Spouse Gold Coin Program", "url": "https://www.usmint.gov/learn/coin-and-medal-programs/first-spouse-gold-coins", "years": "2007-2016, 2020", "coins": ["Martha Washington", "Abigail Adams", "Jefferson's Liberty", "Dolley Madison", "Elizabeth Monroe", "Louisa Adams", "Jackson's Liberty", "Van Buren's Liberty", "Anna Harrison", "Letitia Tyler", "Julia Tyler", "Sarah Polk", "Margaret Taylor", "Abigail Fillmore", "Jane Pierce", "Buchanan's Liberty", "Mary Todd Lincoln", "Eliza Johnson", "Julia Grant", "Lucy Hayes", "Lucretia Garfield", "Alice Paul", "Frances Cleveland (1st)", "Caroline Harrison", "Frances Cleveland (2nd)", "Ida McKinley", "Edith Roosevelt", "Helen Taft", "Ellen Wilson", "Edith Wilson", "Florence Harding", "Grace Coolidge", "Lou Hoover", "Eleanor Roosevelt", "Bess Truman", "Mamie Eisenhower", "Jacqueline Kennedy", "Lady Bird Johnson", "Pat Nixon", "Betty Ford", "Nancy Reagan", "Barbara Bush"]},
        {"id": "dc_comics", "name": "DC Comics Bullion Series", "url": "https://catalog.usmint.gov/", "years": "2025-2027", "coins": ["Superman (2025 Pending)", "Batman (2025 Pending)", "Wonder Woman (2025 Pending)", "2026 Release 1 (Pending)", "2026 Release 2 (Pending)", "2026 Release 3 (Pending)", "2027 Release 1 (Pending)", "2027 Release 2 (Pending)", "2027 Release 3 (Pending)"]}
    ],
    "Upcoming Officially Announced Programs": [
        {"id": "fifa", "name": "2026 FIFA World Cup Commemorative Coin Program", "url": "https://www.usmint.gov/", "years": "2026", "coins": ["$5 Gold Coin (Pending)", "$1 Silver Coin (Pending)", "Half Dollar Clad (Pending)"]},
        {"id": "youth_post_2026", "name": "Youth and Paralympic Sports Quarters and Half Dollars", "url": "https://www.usmint.gov/news/press-releases", "years": "Post-2026", "coins": ["Youth Sports Quarter 1 (Pending)", "Youth Sports Quarter 2 (Pending)", "Youth Sports Quarter 3 (Pending)", "Youth Sports Quarter 4 (Pending)", "Youth Sports Quarter 5 (Pending)", "Paralympic Half Dollar (Pending)"]},
        {"id": "youth_2027", "name": "2027 Youth and Paralympic Sports Program", "url": "https://www.usmint.gov/news/press-releases", "years": "2027", "coins": ["2027 Quarter 1 (Pending)", "2027 Quarter 2 (Pending)", "2027 Quarter 3 (Pending)", "2027 Quarter 4 (Pending)", "2027 Quarter 5 (Pending)", "2027 Half Dollar (Pending)"]}
    ]
}


# --- POPUP MODE FUNCTION ---
def render_popup_history_mode(prog_id):
    # Locate Program
    program = None
    for cat, progs in US_PROGRAMS.items():
        for p in progs:
            if p['id'] == prog_id:
                program = p
                break
        if program: break
    
    if not program:
        st.error("Program not found.")
        return

    st.markdown(f"## 📚 History: {program['name']}")
    st.caption(f"Years: {program['years']}")
    
    # Generate History
    with st.spinner("Consulting the archives..."):
        # Helper to generate history (duplicated or shared)
        prompt = f"Provide a brief, engaging history of the US Mint '{program['name']}' coin program. Include authorization (law), years, designer info if key, and purpose. Format with markdown."
        try:
             # Direct Gemini Call (Bypass collection check)
             chat_session = model.start_chat()
             max_retries = 3
             # Simple retry logic or just direct call
             response = chat_session.send_message(prompt)
             st.markdown(response.text)
        except Exception as e:
             st.error(f"AI Gemini Error: {e}")
    
    st.divider()
    st.markdown(f"**Official Source:** [{program['url']}]({program['url']})")
    # Close button for usability (closes tab)
    st.markdown("""
        <button onclick="window.close()" style="background-color:#f44336; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
            Close Window
        </button>
    """, unsafe_allow_html=True)





def render_programs():
    st.title("US Mint Coin Programs")
    st.markdown(f"<div class='beta-tag'>PROGRAM MANAGER</div>", unsafe_allow_html=True)
    st.caption("Track your progress on official US Mint series.")
    
    # 1. Load Collection
    df = load_collection(limit_n=None)
    
    # 2. Render UI
    selected_program_id = st.session_state.get('program_view_id')
    
    if not selected_program_id:
        # --- VIEW SETTINGS ---
        col_sort, col_gem = st.columns([1, 2])
        with col_sort:
            sort_order = st.selectbox("Sort Programs By:", ["Default (Release Date)", "Newest Release", "Oldest Release", "Most Complete", "Least Complete"])
            
        # CATEGORIZED GRID VIEW
        for category, programs in US_PROGRAMS.items():
            
            # --- SORTING LOGIC ---
            # Pre-calculate completion for sorting
            prog_data = []
            for p in programs:
                collected_count = 0
                for coin_name in p['coins']:
                    if "Pending" in coin_name: continue
                    match = df[df.astype(str).apply(lambda x: x.str.contains(coin_name, case=False, na=False)).any(axis=1)]
                    if not match.empty: collected_count += 1
                
                total = len([c for c in p['coins'] if "Pending" not in c])
                total = total if total > 0 else 1
                pct = int((collected_count / total) * 100)
                prog_data.append({**p, "count": collected_count, "total": total, "pct": pct})
            
            if sort_order == "Most Complete":
                prog_data.sort(key=lambda x: x['pct'], reverse=True)
            elif sort_order == "Least Complete":
                prog_data.sort(key=lambda x: x['pct'], reverse=False)
            elif sort_order == "Newest Release":
                # Extract first year
                def get_start_year(p):
                     import re
                     match = re.search(r'(\d{4})', p['years'])
                     return int(match.group(1)) if match else 0
                prog_data.sort(key=get_start_year, reverse=True)
            elif sort_order == "Oldest Release":
                def get_start_year(p):
                     import re
                     match = re.search(r'(\d{4})', p['years'])
                     return int(match.group(1)) if match else 0
                prog_data.sort(key=get_start_year, reverse=False)
            
            st.divider()
            st.subheader(category)
            
            # Dynamic Grid Layout
            cols = st.columns(3)
            
            for i, prog in enumerate(prog_data):
                with cols[i % 3]:
                    # CARD CONTAINER
                    with st.container(border=True):
                        # Title & Link Row
                        c_tit, c_lnk = st.columns([5, 1])
                        c_tit.markdown(f"**{prog['name']}**")
                        
                        # HISTORY POPUP LINK (Target Blank)
                        # We use the query param ?program_history=ID to trigger the popup mode
                        link_url = f"/?program_history={prog['id']}"
                        # If running under shell, it might be messy, but let's try relative link first.
                        # Since app.py is the iframe source, this opens app.py in a new tab with the param.
                        c_lnk.markdown(f'<a href="{link_url}" target="_blank" style="text-decoration:none; font-size:20px;">🔗</a>', unsafe_allow_html=True)
                        
                        st.caption(f"{prog['years']}")
                        
                        # Progress Bar
                        st.progress(prog['pct'] / 100)
                        st.caption(f"{prog['count']} / {prog['total']} Collected")
                        
                        # CLICKABLE AREA (Full Width Button)
                        if st.button("View Checklist", key=f"view_{prog['id']}", use_container_width=True):
                            st.session_state.program_view_id = prog['id']
                            if 'show_history_for' in st.session_state: del st.session_state.show_history_for
                            st.rerun()

    else:
        # CHECKLIST VIEW
        # Flat Search for the program dictionary
        prog = None
        for cat, progs in US_PROGRAMS.items():
             for p in progs:
                 if p['id'] == selected_program_id:
                     prog = p
                     break
             if prog: break
        
        col_back, col_title, col_action = st.columns([1, 4, 1])
        with col_back:
            if st.button("← Back"):
                del st.session_state.program_view_id
                if 'show_history_for' in st.session_state: del st.session_state.show_history_for
                st.rerun()
        with col_title:
             st.subheader(f"{prog['name']}")
             
        # GEMINI HISTORY & LINK
        # Auto-expand if triggered from the chain icon
        show_history = st.session_state.get('show_history_for') == prog['id']
        
        with st.expander("📚 Program History & Info", expanded=show_history):
            
            # Helper to generate history
            def get_history(p_name):
                prompt = f"Provide a brief, engaging history of the US Mint '{p_name}' coin program. Include authorization (law), years, designer info if key, and purpose. Format with markdown."
                try:
                    # Assuming ask_deepdive is defined elsewhere and can take a prompt and df
                    # If df is not needed for this specific prompt, pass None or an empty df
                    return ask_deepdive(prompt, df) # Reusing deepdive as it has context, or just generic model
                except Exception as e:
                    print(f"Error generating history: {e}")
                    return "AI History currently unavailable."

            # If triggered, generate automatically if not present? 
            # OR just show a button to generate. User asked for "Gemini powered history... where the hyperlink points to"
            # implying immediate view.
            
            if show_history:
                 if f"history_{prog['id']}" not in st.session_state:
                     with st.spinner(f"Generating history for {prog['name']}..."):
                         st.session_state[f"history_{prog['id']}"] = get_history(prog['name'])
            
            # Display History if available
            if f"history_{prog['id']}" in st.session_state:
                st.markdown(st.session_state[f"history_{prog['id']}"])
                st.caption(f"Source Reference: [{prog['url']}]({prog['url']})")
                if st.button("🔄 Refresh History", key=f"refresh_{prog['id']}"):
                    del st.session_state[f"history_{prog['id']}"]
                    st.rerun()
            else:
                st.info("Click below to generate a detailed history of this program provided by Vertex AI.")
                if st.button("✨ Generate AI History Summary", key=f"gen_{prog['id']}"):
                    st.session_state.show_history_for = prog['id'] # Set flag to auto-trigger next render logic logic via rerun or just run it now
                    st.session_state[f"history_{prog['id']}"] = get_history(prog['name'])
                    st.rerun()
                st.markdown(f"**Official Source:** [{prog['url']}]({prog['url']})")
        
        # EXPORT FEATURE
        with col_action:
             if st.button("📄 Export"):
                 # Generate Text List
                 txt = f"Checklist: {prog['name']}\n\n"
                 for c in prog['coins']:
                     txt += f"[ ] {c}\n"
                 b64 = base64.b64encode(txt.encode()).decode()
                 st.markdown(f'<a href="data:text/plain;base64,{b64}" download="{prog["id"]}_checklist.txt">Download Text</a>', unsafe_allow_html=True)

        # Calculate Logic
        collected_coins = []
        
        for coin in prog['coins']:
            match = df[
                df.astype(str).apply(lambda x: x.str.contains(coin, case=False, na=False)).any(axis=1)
            ]
            if not match.empty:
                first = match.iloc[0]
                collected_coins.append({"name": coin, "data": first})

        # CHECKLIST ONLY (Wishlist moved to main page)
        st.write("")
        st.markdown("### Program Checklist")
        
        for c in prog['coins']:
            is_collected = c in [x['name'] for x in collected_coins]
            is_pending = "Pending" in c
            
            if is_collected:
                data = next(x['data'] for x in collected_coins if x['name'] == c)
                with st.expander(f"✅ {c}", expanded=False):
                    st.caption(f"Found match: {data.get('Year')} {data.get('Denomination')}")
                    st.write(f"Grade: {data.get('Condition')}")
            elif is_pending:
                 st.markdown(f"🗓️ <span style='color:orange; font-style:italic;'>{c}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"⬜ <span style='color:grey'>{c}</span>", unsafe_allow_html=True)
                
        st.info("ℹ️ Missing items are automatically added to your 'My Wishlist' page.")

def normalize_coin_data(df):
    if df.empty: return df
    
    # helper for mapping
    def get_canonical(val, category):
        if not val: return val
        s_val = str(val).strip()
        for canonical, aliases in COIN_STANDARDS[category].items():
            if s_val.lower() == canonical.lower(): return canonical
            for alias in aliases:
                if s_val.lower() == alias.lower(): return canonical
        return val # no match found, keep original

    # 1. Normalize Denomination & Metal
    if 'Denomination' in df.columns:
        df['Denomination'] = df['Denomination'].apply(lambda x: get_canonical(x, 'denominations'))
    if 'Metal Content' in df.columns:
        df['Metal Content'] = df['Metal Content'].apply(lambda x: get_canonical(x, 'metals'))

    # 2. Date Cleanup (Purchase Date)
    if 'Purchase Date' in df.columns:
        def clean_date(d):
            if not d or str(d).lower() in ['nan', 'nat', 'none', '']: return datetime.today().strftime('%Y-%m-%d')
            try:
                # Try simple casting first
                return pd.to_datetime(d).strftime('%Y-%m-%d')
            except:
                return datetime.today().strftime('%Y-%m-%d')
        df['Purchase Date'] = df['Purchase Date'].apply(clean_date)

    # 3. Text Cleanup (Theme, etc) - N/A or Blank -> ""
    text_cols = ['Theme/Subject', 'Program/Series', 'Mint Mark']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: "" if str(x).lower().strip() in ['n/a', 'blank', 'nan', 'none'] else x)
            
    return df

DISPLAY_ORDER = [
    "Country", "Year", "Mint Mark", "Denomination", "Quantity", 
    "Program/Series", "Theme/Subject", "Condition", "Surface & Strike Quality", 
    "Grading Service", "Grading Cert #", "Cost", "Purchase Date", 
    "Retailer/Website", "Retailer Invoice #", "Retailer Item No.", "Metal Content", "Melt Value", "Personal Notes", 
    "Personal Ref #", "AI Estimated Value", "Storage Location"
]

def get_empty_collection_df():
    system_cols = ['id', 'deep_dive_status', 'Numismatic Report', 'potentialVariety', 'imageUrlObverse', 'imageUrlReverse', 'inventoryStatus', 'category', 'file_ref', 'source_file']
    final_cols = DISPLAY_ORDER + [c for c in system_cols if c not in DISPLAY_ORDER]
    return pd.DataFrame(columns=final_cols)

def load_collection(limit_n=None):
    if st.session_state.get('guest_mode'):
        return get_dummy_collection()
        
    path = get_user_collection_path()
    if not path: return get_empty_collection_df()
    
    ref = db.collection(path)
    if limit_n:
        # If limiting, we assume we want the most recent
        ref = ref.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit_n)
        
    docs = ref.stream()
    items = []
    for doc in docs:

        item = doc.to_dict()
        item['id'] = doc.id 
        for col in DISPLAY_ORDER:
            if col not in item: item[col] = None
        if 'deep_dive_status' not in item: item['deep_dive_status'] = 'PENDING'
        if 'Numismatic Report' not in item: item['Numismatic Report'] = ""
        if 'imageUrlObverse' not in item: item['imageUrlObverse'] = None
        if 'imageUrlReverse' not in item: item['imageUrlReverse'] = None
        if 'inventoryStatus' not in item: item['inventoryStatus'] = 'UNCHECKED'
        if 'Cost' not in item or not item['Cost']: item['Cost'] = "$0.00"
        items.append(item)
    
    if not items: return get_empty_collection_df()
    
    df = pd.DataFrame(items)
    system_cols = ['id', 'deep_dive_status', 'Numismatic Report', 'potentialVariety', 'imageUrlObverse', 'imageUrlReverse', 'inventoryStatus', 'category', 'file_ref', 'source_file']
    final_cols = DISPLAY_ORDER + [c for c in system_cols if c not in DISPLAY_ORDER]
    
    for c in final_cols:
        if c not in df.columns: df[c] = None
    return df[final_cols]

def clean_money_string(val):
    if not val: return 0.0
    try:
        s = str(val).replace('$', '').replace(',', '').strip()
        if not s: return 0.0
        return float(s)
    except: return 0.0

def calculate_portfolio_value(df):
    total = 0.0
    if df.empty: return 0.0
    for val in df['AI Estimated Value'].dropna():
        try:
            clean = str(val).replace('$', '').replace(',', '').strip()
            if any(x in clean for x in ["Pending", "N/A", ""]): continue
            if '-' in clean:
                parts = clean.split('-')
                avg = (float(parts[0].strip()) + float(parts[1].strip())) / 2
                total += avg
            else:
                total += float(clean)
        except: continue
    return total

def save_edits(edited_df, original_df):
    if st.session_state.get('guest_mode'):
        st.warning("🔒 Guest Mode is Read-Only. Sign up to save your collection.", icon="🚫")
        return
        
    path = get_user_collection_path()
    batch = db.batch(); count = 0
    for index, row in edited_df.iterrows():
        doc_id = row['id']
        ref = db.collection(path).document(doc_id)
        data = row.to_dict()
        batch.set(ref, data, merge=True)
        count += 1
        if count >= 400: batch.commit(); batch = db.batch(); count = 0
    if count > 0: batch.commit()

def delete_coins(coin_ids):
    path = get_user_collection_path()
    batch = db.batch()
    for cid in coin_ids:
        ref = db.collection(path).document(cid)
        batch.delete(ref)
    batch.commit()


# --- GCS UPLOAD HELPER ---
def upload_to_gcs(file_bytes, destination_blob_name, content_type="application/octet-stream"):
    """Uploads bytes to Google Cloud Storage and returns the GS URI."""
    try:
        storage_client = storage.Client()
        bucket_name = f"{PROJECT_ID}-uploads"
        
        # Create bucket if not exists
        try:
            bucket = storage_client.get_bucket(bucket_name)
        except:
            bucket = storage_client.create_bucket(bucket_name, location=LOCATION)
            
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(file_bytes, content_type=content_type)
        return f"gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        print(f"GCS Upload Failed: {e}")
        return None

def handle_image_upload(file, coin_id, side):
    path = get_user_collection_path()
    bytes_data = file.getvalue()
    
    # 1. Base64 for Instant Display (Legacy)
    base64_img = base64.b64encode(bytes_data).decode('utf-8')
    final_str = f"data:image/png;base64,{base64_img}"
    field = "imageUrlObverse" if side == "obverse" else "imageUrlReverse"
    
    # 2. GCS for Persistence (New)
    timestamp = int(time.time())
    gcs_path = f"images/{coin_id}_{side}_{timestamp}.png"
    gcs_uri = upload_to_gcs(bytes_data, gcs_path, content_type=file.type)
    
    update_data = {field: final_str}
    if gcs_uri:
        update_data[f"{field}_gcs"] = gcs_uri
        
    db.collection(path).document(coin_id).set(update_data, merge=True)
    st.toast("Image saved!", icon="📸"); time.sleep(1); st.rerun()

def process_invoice(file_content):
    # Processor ID: c113e9bb62be1554
    opts = ClientOptions(api_endpoint=f"us-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    name = client.processor_path(PROJECT_ID, "us", "c113e9bb62be1554")
    raw_document = documentai.RawDocument(content=file_content, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    return result.document

# --- RESEARCHER ENGINE ---
def generate_ai_reports(df_to_process, silver_p, gold_p):
    path = get_user_collection_path()
    status_box = st.status("Generating AI Numismatic Reports...", expanded=True)
    progress_bar = status_box.progress(0)
    chat = model.start_chat()
    
    RESEARCH_PROMPT = f"""
    You are an expert Numismatic Appraiser.
    Analyze the coin and generate a comprehensive JSON report.
    SPOT: Silver=${silver_p}, Gold=${gold_p}
    
    INSTRUCTIONS:
    1. Fill any missing technical data (Composition, Series, Theme).
    2. Melt Value: Calculate (Weight * Purity * Spot). Return formatted string (e.g. "$18.42"). If not precious, return "N/A".
    3. AI Estimated Value: Estimate fair market range for this specific coin condition.
    4. Numismatic Report: Brief history/significance.
    
    CRITICAL: OUTPUT VALID JSON ONLY matching this structure:
    {{
        "Melt Value": "string",
        "AI Estimated Value": "string",
        "Program/Series": "string",
        "Theme/Subject": "string",
        "Metal Content": "string (e.g. 90% Silver)",
        "Mint Mark": "string (guess if not provided but obvious, else null)",
        "Numismatic Report": "string",
        "potentialVariety": {{ "name": "string", "description": "string", "estimatedValue": "string" }} OR null
    }}
    """
    
    total = len(df_to_process)
    count = 0
    
    for index, row in df_to_process.iterrows():
        d = row.to_dict()
        coin_desc = f"{d.get('Year')} {d.get('Country')} {d.get('Denomination')} {d.get('Mint Mark')} {d.get('Condition')}"
        status_box.write(f"Analyzing: **{coin_desc}**")
        try:
            response = chat.send_message([RESEARCH_PROMPT, f"Known Data: {json.dumps(d, default=str)}"])
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(clean_text)
            
            doc_ref = db.collection(path).document(row['id'])
            
            # Merge AI data with existing data, preferring AI for empty fields
            update_data = {
                "Melt Value": ai_data.get("Melt Value", "N/A"),
                "AI Estimated Value": ai_data.get("AI Estimated Value", "Pending"),
                "Numismatic Report": ai_data.get("Numismatic Report", ""),
                "potentialVariety": ai_data.get("potentialVariety"),
                "deep_dive_status": "COMPLETED",
                "last_researched": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Enrich other fields if missing in original
            if not d.get('Program/Series') and ai_data.get('Program/Series'): update_data['Program/Series'] = ai_data['Program/Series']
            if not d.get('Theme/Subject') and ai_data.get('Theme/Subject'): update_data['Theme/Subject'] = ai_data['Theme/Subject']
            if not d.get('Metal Content') and ai_data.get('Metal Content'): update_data['Metal Content'] = ai_data['Metal Content']
            
            doc_ref.set(update_data, merge=True)
            time.sleep(1.0)
        except Exception as e: status_box.error(f"FAIL: {e}")
        count += 1
        progress_bar.progress(count / total)
    
    status_box.update(label="Syncing...", state="complete", expanded=False)
    time.sleep(2)
    st.rerun()

def generate_ai_report_single(coin_data, silver_p, gold_p):
    df_single = pd.DataFrame([coin_data])
    generate_ai_reports(df_single, silver_p, gold_p)

def ask_deepdive(query, df):
    if df.empty: return "Your collection is empty."
    summary_df = df[['Year', 'Country', 'Denomination', 'Condition', 'Cost', 'AI Estimated Value']].to_string()
    chat_prompt = f"User Question: '{query}'\nData:\n{summary_df}\nAnswer as an expert numismatist."
    try:
        with numista_loader("Numista AI is researching your collection..."):
            chat = model.start_chat()
            return chat.send_message(chat_prompt).text
    except Exception as e: return f"Error: {e}"

# --- POPUP EXECUTION (Placed here to ensure functions are defined) ---
if st.session_state.get('POPUP_MODE_ID'):
    render_popup_history_mode(st.session_state['POPUP_MODE_ID'])
    st.stop()

def confirm_variety(coin_data):
    path = get_user_collection_path()
    variety = coin_data['potentialVariety']
    new_desc = f"{coin_data.get('Numismatic Report', '')}\n\n[USER CONFIRMED VARIETY: {variety['name']}]"
    db.collection(path).document(coin_data['id']).set({
        "Numismatic Report": new_desc, 
        "AI Estimated Value": variety['estimatedValue'], 
        "potentialVariety": firestore.DELETE_FIELD
    }, merge=True)
    st.toast("Confirmed! Value Updated.", icon="🎉"); time.sleep(1); st.rerun()

def dismiss_variety(coin_data):
    path = get_user_collection_path()
    db.collection(path).document(coin_data['id']).set({"potentialVariety": firestore.DELETE_FIELD}, merge=True)
    st.toast("Dismissed.", icon="👍"); time.sleep(1); st.rerun()

def identify_duplicates(new_df, existing_df):
    if existing_df.empty:
        new_df['Status'] = 'NEW'
        new_df['Duplicate Check Key'] = 'No Existing Data'
        return new_df

    # --- Helper 1: Attribute Key (Legacy compatible) ---
    def get_attr_key(row):
        y = str(row.get('Year', '')).strip()
        m = str(row.get('Mint Mark', '')).strip().replace('None', '').replace('nan', '')
        d = str(row.get('Denomination', '')).strip()
        mt = str(row.get('Metal Content', '')).strip()

        # Condition Normalization (Remove CAC/Sticker noise)
        raw_c = str(row.get('Condition', '')).upper()
        c = raw_c.replace("CAC", "").replace("STICKER", "").replace("APPROVED", "").replace("CERTIFIED", "").strip()
        
        # Strike Normalization
        raw_s = str(row.get('Surface & Strike Quality', '')).upper()
        s = raw_s.replace("CAC", "").replace("APPROVED", "").replace("CERTIFIED", "").strip()

        # Aggressive Denomination Normalization
        d_lower = d.lower()
        if d_lower == "dollar":
            try:
                yi = int(y)
                if 1878 <= yi <= 1921: d = "Morgan Silver Dollar"
                elif 1921 < yi <= 1935: d = "Peace Silver Dollar"
            except: pass

        return f"{y}|{m}|{d}|{c}|{mt}|{s}".lower()

    # --- Helper 2: Invoice Key (New strict logic) ---
    def get_inv_key(row):
        inv = str(row.get('Retailer Invoice #', '')).strip().lower()
        item = str(row.get('Retailer Item No.', '')).strip().lower()
        
        if inv and item and inv != 'nan' and item != 'nan':
            return f"{inv}|{item}"
        return None

    # --- Build Indices ---
    existing_attr_keys = set(existing_df.apply(get_attr_key, axis=1))
    existing_inv_keys = set(existing_df.apply(get_inv_key, axis=1))
    # Remove None from set to avoid false positives
    existing_inv_keys.discard(None) 

    # --- Check New Rows ---
    def check_dupe(row):
        k_attr = get_attr_key(row)
        k_inv = get_inv_key(row)
        
        # HYBRID CHECK: If EITHER matches, it's a duplicate
        is_dupe_attr = k_attr in existing_attr_keys
        is_dupe_inv = (k_inv is not None) and (k_inv in existing_inv_keys)
        
        status = 'DUPLICATE' if (is_dupe_attr or is_dupe_inv) else 'NEW'
        
        # Debug String
        debug_str = f"ATTR: {k_attr}"
        if k_inv: debug_str += f" || INV: {k_inv}"
        if is_dupe_inv: debug_str += " [MATCH: INV]"
        elif is_dupe_attr: debug_str += " [MATCH: ATTR]"
        
        return pd.Series([status, debug_str])

    new_df[['Status', 'Duplicate Check Key']] = new_df.apply(check_dupe, axis=1)
    
    return new_df

def save_to_firestore(df_to_save):
    if df_to_save.empty: return
    path = get_user_collection_path()
    batch = db.batch(); count = 0
    
    for index, row in df_to_save.iterrows():
        # Ensure ID
        if 'id' not in row or not row['id']: row['id'] = str(uuid.uuid4())
        
        doc_data = row.to_dict()
        
        # Clean up temporary columns
        if 'Status' in doc_data: del doc_data['Status']
        if 'Duplicate Check Key' in doc_data: del doc_data['Duplicate Check Key']
        if '_index' in doc_data: del doc_data['_index'] # Streamlit editor artifact
        
        # Ensure critical fields
        if 'created_at' not in doc_data: doc_data['created_at'] = firestore.SERVER_TIMESTAMP
        if 'deep_dive_status' not in doc_data: doc_data['deep_dive_status'] = "PENDING"
        
        ref = db.collection(path).document(row['id'])
        batch.set(ref, doc_data, merge=True)
        count += 1
        if count >= 400: batch.commit(); batch = db.batch(); count = 0
        
    if count > 0: batch.commit()
    st.success(f"Successfully imported {count} coins!"); st.balloons(); time.sleep(1.5); st.rerun()

def get_column_mapping(source_columns):
    target_columns = DISPLAY_ORDER
    # We want to be smart about mapping.
    prompt = f"""
    You are an expert Data Engineer. Map the Source Columns from a user's spreadsheet to the Target Database Schema.
    
    Target Schema: {target_columns}
    Source Columns: {source_columns}
    
    INSTRUCTIONS:
    1. Return a JSON object where Key = Source Column, Value = Target Column.
    2. If a Source Column has NO clear match in Target, map it to "EXTRA_METADATA".
    3. Be generous with matching (e.g. "Date" -> "Purchase Date", "Grade" -> "Condition").
    4. "Cost" should map to "Cost".
    
    OUTPUT JSON ONLY.
    """
    try:
        chat = model.start_chat()
        response = chat.send_message(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        mapping = json.loads(text)
        return mapping
    except Exception as e:
        st.error(f"Mapping Failed: {e}")
        return {}

def process_row_with_mapping(row, mapping):
    """
    Applies strict mapping to a single row.
    Returns: (processed_dict, list_of_errors)
    """
    data = {}
    extra_metadata = {}
    errors = []
    
    # Initialize Defaults
    data['id'] = str(uuid.uuid4())
    for col in DISPLAY_ORDER:
        data[col] = "" # Default to empty string
    
    data['deep_dive_status'] = "PENDING"
    data['inventoryStatus'] = "UNCHECKED"
    data['AI Estimated Value'] = "Pending"
    if 'Cost' not in data or not data['Cost']: data['Cost'] = "$0.00"

    try:
        for source_col, val in row.items():
            # Handle NaN
            if pd.isna(val) or val == "" or str(val).lower() == 'nan':
                continue
                
            val_str = str(val).strip()
            
            target = mapping.get(source_col, "EXTRA_METADATA")
            
            if target == "EXTRA_METADATA":
                extra_metadata[source_col] = val_str
            elif target in DISPLAY_ORDER:
                data[target] = val_str
            else:
                extra_metadata[source_col] = val_str # Fallback
        
        # Add basic cleanup
        if 'Year' in data: 
            try: data['Year'] = int(float(data['Year']))
            except: pass
            
        data['extra_metadata'] = extra_metadata
        return data, errors
        
    except Exception as e:
        errors.append(str(e))
        return None, errors

def render_add_excel():
    st.info("📂 Upload Excel or CSV to Fast Map coins.")
    
    if 'excel_uploader_key' not in st.session_state: st.session_state['excel_uploader_key'] = 0
    if 'upload_stage' not in st.session_state: st.session_state['upload_stage'] = None
    if 'mapping_stage' not in st.session_state: st.session_state['mapping_stage'] = None
    if 'failed_rows' not in st.session_state: st.session_state['failed_rows'] = []

    # --- RESET FUNCTION ---
    def reset_upload_state():
        st.session_state['upload_stage'] = None
        st.session_state['mapping_stage'] = None
        st.session_state['failed_rows'] = []
        if 'current_file_gcs_uri' in st.session_state: del st.session_state['current_file_gcs_uri']
        if 'gcs_upload_done' in st.session_state: del st.session_state['gcs_upload_done']
        st.session_state['excel_uploader_key'] += 1
        st.rerun()

    # --- STAGE 1: UPLOAD & MAP ---
    if st.session_state['upload_stage'] is None:
        uploaded_file = st.file_uploader(
            "Upload Inventory File", 
            type=['xlsx', 'xls', 'csv'], 
            key=f"uploader_{st.session_state['excel_uploader_key']}"
        )
        
        if uploaded_file:
            if uploaded_file.name.endswith('csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            
            # --- PERSIST RAW FILE ---
            if 'gcs_upload_done' not in st.session_state:
                timestamp = int(time.time())
                blob_name = f"spreadsheets/{uuid.uuid4()}_{timestamp}_{uploaded_file.name}"
                gcs_uri = upload_to_gcs(uploaded_file.getvalue(), blob_name, content_type=uploaded_file.type)
                st.session_state['current_file_gcs_uri'] = gcs_uri
                st.session_state['gcs_upload_done'] = True
            
            # --- AUTO-PROCESS (Skip Confirmation) ---
            if st.button("Process & Import File", type="primary"):
                with st.spinner("AI is analyzing & mapping columns..."):
                    # 1. Map
                    columns = df.columns.tolist()
                    mapping = get_column_mapping(columns)
                    st.session_state['mapping_stage'] = mapping
                    
                    # 2. Process
                    processed_coins = []
                    failed_rows = []
                    gcs_ref = st.session_state.get('current_file_gcs_uri')
                    
                    progress = st.progress(0)
                    total = len(df)
                    
                    for i, row in df.iterrows():
                        data, errs = process_row_with_mapping(row, mapping)
                        if data:
                            if gcs_ref: data['file_ref'] = gcs_ref
                            processed_coins.append(data)
                        else:
                            failed_rows.append({"Row Index": i, "Data": str(row.to_dict()), "Error": str(errs)})
                        
                        if i % 10 == 0: progress.progress((i+1)/total)
                    
                    st.session_state['failed_rows'] = failed_rows
                    
                    if processed_coins:
                        new_df = pd.DataFrame(processed_coins)
                        existing_df = load_collection(limit_n=None)
                        new_df = normalize_coin_data(new_df)
                        staged_df = identify_duplicates(new_df, existing_df)
                        
                        cols = ['Status'] + [c for c in staged_df.columns if c != 'Status']
                        st.session_state['upload_stage'] = staged_df[cols]
                        st.rerun()
                    else:
                        st.error("No valid rows extracted.")

    # --- STAGE 2: PREVIEW & CONFIRM ---
    else:
        st.divider()
        st.subheader("Import Preview")
        
        # --- ERROR REPORTING ---
        failures = st.session_state['failed_rows']
        if failures:
            st.error(f"⚠️ {len(failures)} Rows Failed to Process")
            fail_df = pd.DataFrame(failures)
            csv = fail_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Failed Rows CSV", csv, "failed_rows.csv", "text/csv")
            st.divider()

        staged_df = st.session_state['upload_stage']
        
        # Color Warning
        n_dupes = len(staged_df[staged_df['Status'] == 'DUPLICATE'])
        if n_dupes > 0: 
            st.warning(f"⚠️ {n_dupes} Potential Duplicates Identified.", icon="⚠️")
        else: 
            st.success("✅ No Duplicates Found", icon="✅")
        
        # Editable Dataframe with Hidden Tech Cols
        column_config = {
            "id": None, 
            "extra_metadata": None, 
            "file_ref": None, 
            "Duplicate Check Key": None
        }
        
        edited_df = st.data_editor(
            staged_df, 
            use_container_width=True, 
            num_rows="dynamic", 
            key="editor_upload",
            column_config=column_config
        )
        
        c1, c2, c3 = st.columns([1, 2, 2])
        
        with c1:
            if st.button("Cancel", key="cancel_upload"):
                reset_upload_state()
        
        with c2:
            if st.button("🔄 Upload Another Spreadsheet", key="upload_another_excel"):
                reset_upload_state()
        
        with c2:
            if st.button("Import New Only", type="secondary", use_container_width=True):
                final = edited_df[edited_df['Status'] == 'NEW']
                save_to_firestore(final)
                st.success("Import Complete!"); time.sleep(1)
                # Don't rerun immediately, show buttons
                st.session_state['upload_complete'] = True

        with c3:
            if st.button("Import All", type="primary", use_container_width=True):
                save_to_firestore(edited_df)
                st.success("Import Complete!"); time.sleep(1)
                st.session_state['upload_complete'] = True

        # --- POST UPLOAD ACTIONS ---
        if st.session_state.get('upload_complete'):
            st.divider()
            st.balloons()
            st.subheader("🎉 Import Successful!")
            if st.button("📂 Upload Another Spreadsheet?", type="primary", use_container_width=True):
                del st.session_state['upload_complete']
                reset_upload_state()

def render_add_manual():
    st.info("📝 Manually add a coin to your collection.")
    
    if 'upload_stage' not in st.session_state: st.session_state['upload_stage'] = None

    # --- STAGE 1: FORM INPUT ---
    if st.session_state['upload_stage'] is None:
        with st.form("manual_add"):
            # Organized Input Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Key Details", "Grading & Condition", "Purchase Info", "Notes & Storage"])
            
            with tab1:
                c1, c2, c3 = st.columns(3)
                with c1:
                    year = st.text_input("Year")
                    country = st.text_input("Country", value="USA")
                    quantity = st.number_input("Quantity", min_value=1, value=1)
                with c2:
                    denom = st.text_input("Denomination")
                    mint = st.text_input("Mint Mark")
                    metal = st.text_input("Metal Content")
                with c3:
                    series = st.text_input("Program/Series")
                    theme = st.text_input("Theme/Subject")
                    variety_leg = st.text_input("Variety (Legacy)")

            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    cond = st.text_input("Condition (Grade)")
                    strike = st.text_input("Surface & Strike Quality")
                with c2:
                    grade_svc = st.text_input("Grading Service")
                    grade_cert = st.text_input("Grading Cert #")

            with tab3:
                c1, c2, c3 = st.columns(3)
                with c1:
                    cost = st.text_input("Cost", value="$0.00")
                    date_purch = st.date_input("Purchase Date", value=datetime.today())
                with c2:
                    retailer = st.text_input("Retailer/Website")
                    inv_num = st.text_input("Retailer Invoice #")
                with c3:
                    item_num = st.text_input("Retailer Item No.")

            with tab4:
                c1, c2 = st.columns(2)
                with c1:
                    storage = st.text_input("Storage Location")
                    ref_num = st.text_input("Personal Ref #")
                with c2:
                    notes = st.text_area("Personal Notes")
                    notes_leg = st.text_area("Notes (Legacy)", height=100)
            
            st.divider()
            uploaded_img = st.file_uploader("Upload Image (Optional)", type=['png', 'jpg'])
            submitted = st.form_submit_button("Preview & Check Duplicates", type="primary")
            
            if submitted:
                # 1. Create Data Dict
                uid = str(uuid.uuid4())
                data = {
                    "id": uid,
                    # Key Details
                    "Year": year, "Country": country, "Quantity": quantity,
                    "Denomination": denom, "Mint Mark": mint, "Metal Content": metal,
                    "Program/Series": series, "Theme/Subject": theme, "Variety (Legacy)": variety_leg,
                    # Grading
                    "Condition": cond, "Surface & Strike Quality": strike,
                    "Grading Service": grade_svc, "Grading Cert #": grade_cert,
                    # Purchase
                    "Cost": cost, "Purchase Date": str(date_purch),
                    "Retailer/Website": retailer, "Retailer Invoice #": inv_num, "Retailer Item No.": item_num,
                    # Storage & Notes
                    "Storage Location": storage, "Personal Ref #": ref_num,
                    "Personal Notes": notes, "Notes (Legacy)": notes_leg,
                    # Defaults
                    "Melt Value": "Pending", "AI Estimated Value": "Pending"
                }
                
                if not data['Cost']: data['Cost'] = "$0.00"
                
                # Image Handler
                if uploaded_img:
                    bytes_data = uploaded_img.getvalue()
                    b64 = base64.b64encode(bytes_data).decode('utf-8')
                    data['imageUrlObverse'] = f"data:image/png;base64,{b64}"
                
                if st.session_state.get('guest_mode'):
                    st.warning("🔒 Guest Mode - Cannot add coins.", icon="🚫")
                else:
                    # 2. Check Duplicates
                    new_df = pd.DataFrame([data])
                    existing_df = load_collection(limit_n=None)
                    
                    # NORMALIZE
                    new_df = normalize_coin_data(new_df)
                    
                    staged_df = identify_duplicates(new_df, existing_df)
                    
                    cols = ['Status'] + [c for c in staged_df.columns if c != 'Status']
                    st.session_state['upload_stage'] = staged_df[cols]
                    st.rerun()

# --- POPUP MODE CHECK ---
if st.session_state.get('POPUP_MODE_ID'):
    # Clear sidebar and other elements for a clean popup look if possible?
    # Or just render it.
    render_popup_history_mode(st.session_state['POPUP_MODE_ID'])
    st.stop() # Stop execution to only show the popup content
 

# ... (Existing code) ...

# ... (At the end of file or suitable location) ...

def render_popup_history_mode(prog_id):
    # Locate Program
    program = None
    for cat, progs in US_PROGRAMS.items():
        for p in progs:
            if p['id'] == prog_id:
                program = p
                break
        if program: break
    
    if not program:
        st.error("Program not found.")
        return

    st.markdown(f"## 📚 History: {program['name']}")
    st.caption(f"Years: {program['years']}")
    
    # Generate History
    with st.spinner("consulting the archives..."):
        # Helper to generate history (duplicated or shared)
        prompt = f"Provide a brief, engaging history of the US Mint '{program['name']}' coin program. Include authorization (law), years, designer info if key, and purpose. Format with markdown."
        try:
             # Basic load to get context if needed, or just None
             df = load_collection(limit_n=1) 
             response = ask_deepdive(prompt, df)
             st.markdown(response)
        except Exception as e:
             st.error(f"AI Error: {e}")
    
    st.divider()
    st.markdown(f"**Official Source:** [{program['url']}]({program['url']})")
    if st.button("Close Window"):
        st.markdown("<script>window.close();</script>", unsafe_allow_html=True)
        
# ... (Inside render_programs) ...
# replace the button with link
# c_lnk.markdown(f'<a href="/?program_history={prog["id"]}" target="_blank" style="text-decoration:none;">🔗</a>', unsafe_allow_html=True)
        
        edited_df = st.data_editor(
            staged_df, 
            use_container_width=True, 
            num_rows="dynamic",
            key="editor_manual"
        )
        
        c1, c2, c3 = st.columns([1, 2, 2])
        
        with c1:
            if st.button("Cancel", key="cancel_manual"):
                st.session_state['upload_stage'] = None
                st.rerun()
        
        with c2:
            if st.button("Import New Only", type="secondary", use_container_width=True, key="imp_new_man"):
                final = edited_df[edited_df['Status'] == 'NEW']
                save_to_firestore(final)
                st.session_state['upload_stage'] = None

        with c3:
            if st.button("Import All", type="primary", use_container_width=True, key="imp_all_man"):
                save_to_firestore(edited_df)
                st.session_state['upload_stage'] = None

def extract_invoice_data(file_bytes):
    """
    Helper to run DocAI OCR + Gemini Extraction and return raw items list.
    """
    # 1. OCR (DocAI)
    doc = process_invoice(file_bytes)
    
    # 2. AI Extraction (Gemini)
    chat = model.start_chat()
    
    COIN_DICTIONARY = [
        { "val": 0.01, "formal": "Lincoln Cent", "slang": ["penny", "wheatie", "steelie", "red cent", "lincoln wheat cent", "wheat cent"] },
        { "val": 0.05, "formal": "Jefferson Nickel", "slang": ["nickel", "buffalo", "war nickel", "v-nickel", "buffalo nickel"] },
        { "val": 0.10, "formal": "Roosevelt Dime", "slang": ["dime", "mercury", "rosie", "winged liberty", "mercury dime"] },
        { "val": 0.25, "formal": "Washington Quarter", "slang": ["quarter", "two bits", "state quarter", "2026 semiquin"] },
        { "val": 0.50, "formal": "Kennedy Half Dollar", "slang": ["half", "fifty cent", "franklin", "walker", "walking liberty"] },
        { "val": 1.00, "formal": "Morgan Silver Dollar", "slang": ["morgan", "silver dollar", "cartwheel", "peace dollar", "peace"] }
    ]

    SYSTEM_PROMPT = (
        "You are an expert Numismatist. Extract items from this invoice text. "
        "Return a JSON LIST of objects using this validation rules: \n"
        "1. CLASSIFY each item into 'category': 'US Coin', 'Paper Currency', 'Foreign Currency', 'Supply/Other'.\n"
        "2. CONFIDENCE SCORING: For each item, add:\n"
        "   - 'confidence_score': Float 0.0 to 1.0 (1.0 = perfect match, 0.0 = total guess)\n"
        "   - 'needs_manual_review': Boolean (true if Date/Mint/Denomination is ambiguous or missing)\n"
        "3. Use this schema for all items:\n"
        "{ \"category\": \"String\", \"confidence_score\": 0.9, \"needs_manual_review\": false, \n"
        "  \"Country\": \"US\", \"Year\": \"Year\", \"Denomination\": \"Name\", \"Mint Mark\": \"Letter\", \n"
        "  \"Quantity\": \"1\", \"Program/Series\": \"Name\", \"Theme/Subject\": \"Name\", \"Condition\": \"Grade\", \n"
        "  \"Surface & Strike Quality\": \"Notes\", \"Grading Service\": \"Name\", \"Grading Cert #\": \"Num\", \n"
        "  \"Cost\": \"$0.00\", \"Purchase Date\": \"Date\", \"Retailer/Website\": \"Name\", \"Retailer Invoice #\": \"String\", \n"
        "  \"Retailer Item No.\": \"String\", \n"
        "  \"Metal Content\": \"Composition\", \"Melt Value\": \"Pending\", \"Personal Notes\": \"Notes\", \n"
        "  \"Personal Ref #\": \"Num\", \"AI Estimated Value\": \"Pending\", \"inventoryStatus\": \"UNCHECKED\", \"Storage Location\": \"\" }\n\n"
        f"IMPORTANT: Use this dictionary to map slang to formal coin names: {json.dumps(COIN_DICTIONARY)}"
    )
    resp = chat.send_message([SYSTEM_PROMPT, f"Invoice Text: {doc.text}"])
    
    # 3. Parse JSON
    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
    if clean_json.startswith("{"): clean_json = f"[{clean_json}]"
    items = json.loads(clean_json)
    return items

def process_invoice_workflow(file_bytes, filename, user_email):
    try:
        # 1. Extract Data (Refactored)
        items = extract_invoice_data(file_bytes)
        
        process_list = []
        holding_list = []
        review_queue_list = []
        
        # 4. Filter & Route
        for item in items:
            cat = item.get('category', 'US Coin')
            item['id'] = str(uuid.uuid4())
            item['source_file'] = filename # Link to GCS file
            
            if cat == 'US Coin':
                conf = item.get('confidence_score', 0.0)
                needs_review = item.get('needs_manual_review', True)
                
                if conf >= 0.85 and not needs_review:
                    # High Confidence -> Main Collection
                    for col in DISPLAY_ORDER:
                        if col not in item: item[col] = ""
                    process_list.append(item)
                else:
                    # Low Confidence -> Review Queue
                    item['review_reason'] = f"Low Confidence ({conf})" if conf < 0.85 else "Flagged by AI"
                    review_queue_list.append(item)

            elif cat in ['Paper Currency', 'Foreign Currency']:
                holding_list.append(item)

        # 5. Batch Save
        batch = db.batch()
        
        # A. Staging (Paper/Foreign)
        if holding_list:
            stage_ref = db.collection('staging_area')
            for h_item in holding_list:
                h_item['user_email'] = user_email
                h_item['created_at'] = firestore.SERVER_TIMESTAMP
                new_doc = stage_ref.document()
                batch.set(new_doc, h_item)
                
        # B. Review Queue
        if review_queue_list:
            review_ref = db.collection('review_queue')
            for r_item in review_queue_list:
                r_item['user_email'] = user_email
                r_item['created_at'] = firestore.SERVER_TIMESTAMP
                new_doc = review_ref.document()
                batch.set(new_doc, r_item)
        
        # C. Main Collection (High Confidence)
        if process_list:
             path = f"users/{user_email}/coins"
             main_ref = db.collection(path)
             for p_item in process_list:
                 p_item['created_at'] = firestore.SERVER_TIMESTAMP
                 # Ensure defaults
                 if 'deep_dive_status' not in p_item: p_item['deep_dive_status'] = "PENDING"
                 new_doc = main_ref.document(p_item['id'])
                 batch.set(new_doc, p_item)

        batch.commit()
        return True, f"Imported {len(process_list)}, Review {len(review_queue_list)}, Staged {len(holding_list)}"

    except Exception as e:
        return False, str(e)

def render_review_hub():
    st.info("👀 Review Hub: Correct items that the AI wasn't 100% sure about.")
    email = st.session_state.get('user_email')
    
    if not email: return
    
    # 1. Fetch Queue
    reviews = []
    # Note: This query requires an index if ordering, but straightforward filtering usually works
    docs = db.collection('review_queue').where("user_email", "==", email).stream()
    for doc in docs:
        d = doc.to_dict()
        d['queue_id'] = doc.id
        reviews.append(d)
        
    if not reviews:
        st.success("🎉 Review Queue Empty! All items processed successfully.")
        return

    st.write(f"Pending Reviews: {len(reviews)}")
    
    df = pd.DataFrame(reviews)
    
    # Show Reason
    if 'review_reason' in df.columns:
        st.caption("Common Reasons: Low Confidence (<85%), Ambiguous Date/Mint.")
        
    # Editable
    column_config = {
            "queue_id": None, 
            "review_reason": "Reason",
            "confidence_score": "Conf.",
            "source_file": "Source Scan"
        }
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="review_editor", column_config=column_config)
    
    if st.button(f"✅ Approve & Import {len(edited_df)} Items", type="primary"):
        # 1. Save to Coins
        batch = db.batch()
        path = get_user_collection_path()
        coins_ref = db.collection(path)
        queue_ref = db.collection('review_queue')
        
        count = 0
        for i, row in edited_df.iterrows():
            # Clean up review fields
            if 'queue_id' in row: q_id = row['queue_id']; del row['queue_id']
            else: q_id = None
            
            if 'review_reason' in row: del row['review_reason']
            if 'confidence_score' in row: del row['confidence_score']
            if 'needs_manual_review' in row: del row['needs_manual_review']
            
            # Save Coin
            if not row.get('id'): row['id'] = str(uuid.uuid4())
            new_doc = coins_ref.document(row['id'])
            batch.set(new_doc, row.to_dict())
            
            # Delete from Queue
            if q_id:
                old_doc = queue_ref.document(q_id)
                batch.delete(old_doc)
            
            count += 1
            if count >= 400:
                batch.commit()
                batch = db.batch()
                count = 0
        
        if count > 0: batch.commit()
        
        st.balloons()
        st.success("Items Imported Successfully!")
        time.sleep(1)
        st.rerun()

def render_add_scan():
    st.info("🧾 Invoice Processor: Batch & Review")
    
    if 'scan_uploader_key' not in st.session_state: st.session_state['scan_uploader_key'] = 0
    if 'batch_processing' not in st.session_state: st.session_state['batch_processing'] = False
    
    # TABS
    tab_single, tab_upload, tab_batch, tab_review = st.tabs(["📄 Single Scan", "📤 Bulk Upload", "⚙️ Batch Processor", "👀 Review Hub"])
    
    # --- TAB 1: SINGLE SCAN (INTERACTIVE) ---
    with tab_single:
        st.subheader("Interactive Single Invoice Scan")
        inv_file = st.file_uploader("Upload One PDF", type=['pdf'], key=f"single_{st.session_state.scan_uploader_key}")
        
        if inv_file and st.button("Process & Preview"):
            with st.spinner("Analyzing Document..."):
                try:
                    # 1. Extract
                    items = extract_invoice_data(inv_file.getvalue())
                    
                    # 2. Filter Lists
                    process_list = []
                    holding_list = []
                    
                    for item in items:
                        item['id'] = str(uuid.uuid4())
                        item['source_file'] = inv_file.name
                        cat = item.get('category', 'US Coin')
                        
                        if cat == 'US Coin':
                            for col in DISPLAY_ORDER:
                                if col not in item: item[col] = ""
                            process_list.append(item)
                        elif cat in ['Paper Currency', 'Foreign Currency']:
                            holding_list.append(item)
                    
                    # 3. Save Staging Immediately
                    if holding_list:
                        batch = db.batch()
                        stage_ref = db.collection('staging_area')
                        for h_item in holding_list:
                            h_item['user_email'] = st.session_state.get('user_email', 'unknown')
                            h_item['created_at'] = firestore.SERVER_TIMESTAMP
                            new_doc = stage_ref.document()
                            batch.set(new_doc, h_item)
                        batch.commit()
                        st.session_state['holding_stage'] = holding_list
                        
                    # 4. Preview Main Items
                    if process_list:
                        new_df = pd.DataFrame(process_list)
                        existing_df = load_collection(limit_n=None)
                        new_df = normalize_coin_data(new_df)
                        staged_df = identify_duplicates(new_df, existing_df)
                        
                        cols = ['Status'] + [c for c in staged_df.columns if c != 'Status']
                        st.session_state['upload_stage'] = staged_df[cols]
                        st.rerun()
                    elif holding_list:
                        st.warning("Only non-coin items found (saved to Staging).")
                    else:
                        st.error("No items found.")
                        
                except Exception as e:
                    st.error(f"Error: {e}")

        # --- PREVIEW STAGE (REUSED FROM OLD LOGIC) ---
        if st.session_state.get('upload_stage') is not None:
             st.divider()
             st.subheader("Confirm & Import")
             staged_df = st.session_state['upload_stage']
             
             # Show Editor
             edited_df = st.data_editor(staged_df, num_rows="dynamic", use_container_width=True, key="single_editor")
             
             c1, c2 = st.columns(2)
             with c1:
                 if st.button("Cancel", key="cancel_single"):
                     st.session_state['upload_stage'] = None
                     st.rerun()
             with c2:
                 if st.button("Import All", type="primary", key="import_single"):
                     save_to_firestore(edited_df)
                     st.session_state['upload_stage'] = None
                     st.success("Import Complete!")
                     time.sleep(1)
                     st.rerun()
    with tab_upload:
        st.subheader("Bulk Upload to Queue")
        # Ensure we always get a fresh list
        files = st.file_uploader(
            "Select PDFs", 
            type=['pdf'], 
            accept_multiple_files=True, 
            key=f"u_{st.session_state.scan_uploader_key}"
        )
        
        if files:
            if st.button(f"🚀 Upload {len(files)} Invoices to Queue"):
                bar = st.progress(0)
                success_count = 0
                errors = []
                
                for i, f in enumerate(files):
                    ok, err = upload_to_gcs_queue(f)
                    if ok:
                        success_count += 1
                    else:
                        errors.append(f"{f.name}: {err}")
                    bar.progress((i+1)/len(files))
                
                if errors:
                    st.error(f"Failed to upload {len(errors)} files.")
                    with st.expander("Error Details"):
                        for e in errors: st.write(e)
                
                if success_count > 0:
                    st.success(f"Successfully uploaded {success_count} files!")
                    time.sleep(1)
                    st.session_state.scan_uploader_key += 1
                    st.rerun()

    # --- TAB 2: BATCH PROCESSOR ---
    with tab_batch:
        queue = list_queue_files()
        st.subheader(f"Batch Queue ({len(queue)} Files)")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("▶️ Start Batch Processing") or st.session_state.batch_processing:
                st.session_state.batch_processing = True
        with c2:
            if st.button("⏹️ Stop"): st.session_state.batch_processing = False; st.rerun()

        if st.session_state.batch_processing:
            if not queue:
                st.success("Queue Empty - Batch Complete!")
                st.session_state.batch_processing = False
                st.balloons()
                st.rerun()
            
            # PROCESS NEXT FILE
            blob = queue[0]
            st.info(f"Processing: {blob.name}...")
            
            try:
                content = blob.download_as_bytes()
                success, msg = process_invoice_workflow(content, blob.name, st.session_state.user_email)
                
                if success:
                    st.success(f"Done: {msg}")
                    # Move to processed
                    move_blob(blob, f"invoices/processed/{blob.name.split('/')[-1]}")
                else:
                    st.error(f"Failed: {msg}")
                    # Move to failed
                    move_blob(blob, f"invoices/failed/{blob.name.split('/')[-1]}")
                
                time.sleep(1)
                st.rerun() # LOOP
            except Exception as e:
                st.error(f"System Error: {e}")
                st.session_state.batch_processing = False

    # --- TAB 3: REVIEW HUB ---
    with tab_review:
        render_review_hub()
        
# --- MAIN APP LOGIC ---

if not check_login():
    login_screen()
else:
    # --- SIDEBAR LOGIC ---
    # Determine Default Index from URL
    page_param = st.query_params.get("page", "home").lower()
    
    # Check for History Popup Request (sets state and reruns to hit the top-level check)
    hist_req = st.query_params.get("program_history")
    if hist_req:
        st.session_state['POPUP_MODE_ID'] = hist_req
        # Remove param to prevent loop? Or keep it? 
        # If we keep it, we need to ensure we don't clear it. 
        # But st.stop() in the top check handles the view.
        # We should probably clear it from URL so refresh goes back?
        # For now, just set state.
        
    nav_options = ["Home Dashboard", "My Collection", "Coin Programs", "Add New Coins", "Inventory", "My Wishlist", "Settings & Backup", "Our Team", "Customer Service"]
    
    default_ix = 0
    if page_param == "collection": default_ix = 1
    elif page_param == "programs": default_ix = 2
    elif page_param == "add": default_ix = 3
    elif page_param == "inventory": default_ix = 4
    elif page_param == "wishlist": default_ix = 5
    elif page_param == "settings": default_ix = 6
    elif page_param == "team": default_ix = 7
    elif page_param == "support": default_ix = 8
    
    with st.sidebar:
        try:
            st.image("public/Numista.AI Logo.svg", width=220)
        except:
            st.title("Numista.AI")
            
        st.write(f"Vault: **{st.session_state.user_email}**")
        
        selection = st.radio(
            "Main Navigation",
            nav_options,
            index=default_ix,
            label_visibility="collapsed"
        )
        
        if selection == "Add New Coins":
            st.divider()
            st.caption("Select Entry Method:")
            add_method = st.radio(
                "Method",
                ["Scan Invoice", "Manual Entry", "Excel/CSV Upload"],
                label_visibility="collapsed"
            )
            if add_method == "Scan Invoice": selection = "ADD_SCAN"
            elif add_method == "Manual Entry": selection = "ADD_MANUAL"
            elif add_method == "Excel/CSV Upload": selection = "ADD_UPLOAD"

        st.divider()
        if st.button("Log Out"): 
             try: cookie_manager.delete("numista_auth_v1")
             except: pass
             st.session_state.user_email = None
             st.rerun()

    # --- MARKET DATA (Hidden/Default for now if not on dashboard) ---
    # We can move this to the dashboard or settings, for now set defaults if not visible
    silver_p = 72.56
    gold_p = 3100.00

    # --- 2. HOME DASHBOARD ---
    if selection == 'Home Dashboard':
        st.markdown(f"<div style='text-align:center; background:#FFF8DC; color:#856404; padding:5px; border-radius:5px; font-weight:bold; margin-bottom:10px;'>🚧 BETA TESTING MODE 🚧</div>", unsafe_allow_html=True)
        
        df = load_collection(limit_n=None)
        h1, h2 = st.columns([3, 1])
        with h1:
            st.markdown("""<div class="dash-title">DASHBOARD</div><div class="dash-subtitle">AI Powered Coin Collection Manager</div>""", unsafe_allow_html=True)
        with h2:
            est_value = calculate_portfolio_value(df)
            val_fmt = "{:,.2f}".format(est_value)
            st.markdown(f"""<div class="portfolio-label">AI Estimated Portfolio Value</div><div class="portfolio-value">${val_fmt}</div>""", unsafe_allow_html=True)

        # --- VERSION HISTORY SECTION ---
        VERSION_HISTORY = [
            {
                "version": "v2.5",
                "date": "2026-02-17",
                "desc": "Program Manager & AI History Integration",
                "changes": [
                    "Program Manager: Interactive Guide for US Mint Series",
                    "Gemini History: AI-powered historical context for each program",
                    "Wishlist Consolidation: Integrated directly into main app",
                    "Collection Export: Download your progress/checklists"
                ]
            },
            {
                "version": "v1.1",
                "date": "2026-02-01",
                "desc": "Major enhancements to Upload & Scan workflows.",
                "changes": [
                    "Introduced 'Staging Area' for non-currency items (Paper, Foreign).",
                    "Implemented Schema-First Excel Upload: Mapped headers + stored extra metadata.",
                    "Added Persistent File Storage: Raw files backed up to Google Cloud Storage.",
                    "Visual enhancements to Import Preview."
                ]
            },
            {
                "version": "v1.0",
                "date": "2026-01-20",
                "desc": "Initial Launch of Numista.AI",
                "changes": [
                    "Core Collection Management",
                    "AI Scan & Valuation",
                    "Market Data Integration"
                ]
            }
        ]

        with st.expander("🚀 System Updates & Release Notes", expanded=False):
            st.caption("Track the latest features deployed to Numista.AI")
            st.markdown("---")
            for release in VERSION_HISTORY:
                st.markdown(f"**{release['version']}** - *{release['date']}*")
                st.markdown(f"_{release['desc']}_")
                for change in release['changes']:
                    st.markdown(f"- {change}")
                st.markdown("---")

        st.write("")
        df['Cost_Clean'] = df['Cost'].apply(clean_money_string)
        total_cost = df['Cost_Clean'].sum()
        
        m1, m2 = st.columns(2)
        with m1: st.markdown(f"""<div class="metric-box"><div style="color:gray; font-size:14px;">Total Coins</div><div class="metric-value">{len(df)}</div></div>""", unsafe_allow_html=True)
        cost_fmt = "{:,.2f}".format(total_cost)
        with m2: st.markdown(f"""<div class="metric-box"><div style="color:gray; font-size:14px;">Acquisition Cost</div><div class="metric-value">${cost_fmt}</div></div>""", unsafe_allow_html=True)
            
        st.write(""); st.write("")

        c_analytics, c_intel = st.columns([1, 1])
        with c_analytics:
            st.subheader("Analytics Message Board")
            with st.container(border=True):
                if df.empty: st.info("Collection is empty.")
                else:
                    st.write("**Last 5 Coins Added:**")
                    sort_col = 'created_at' if 'created_at' in df.columns else 'Year'
                    try:
                        st.dataframe(df.sort_values(by=sort_col, ascending=False).tail(5)[['Year', 'Denomination', 'AI Estimated Value']], hide_index=True, width='stretch')
                    except:
                        st.dataframe(df.tail(5)[['Year', 'Denomination', 'AI Estimated Value']], hide_index=True, width='stretch')
        
        with c_intel:
            st.subheader("AI Numismatic Deepdive")
            with st.container(border=True):
                if "messages" not in st.session_state: st.session_state.messages = []
                
                st.caption("Suggested Questions:")
                q1, q2, q3 = st.columns(3)
                if q1.button("Most Valuable?"): 
                    prompt = "What is my most valuable coin?"
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = ask_deepdive(prompt, df)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                if q2.button("Coins from 2025?"):
                    prompt = "Show me my coins purchased in 2025"
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = ask_deepdive(prompt, df)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                if q3.button("Next Purchase?"):
                    prompt = "Suggestions for next coin to purchase based on my collection"
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = ask_deepdive(prompt, df)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                for message in st.session_state.messages:
                    with st.chat_message(message["role"]): st.markdown(message["content"])
                
                if prompt := st.chat_input("Ask about your collection..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        response = ask_deepdive(prompt, df)
                        st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

        st.write("")
        st.subheader("📰 US Mint News (Live Feed)")
        st.info("• **Just Released:** 2026 American Eagle Silver Proof Coin\n• **Upcoming:** Women's Quarter Series - Final Release\n• **Alert:** Gold Spot Price fluctuation affecting mint pricing.")

    # --- 3. MY COLLECTION ---
    elif selection == 'My Collection':
        st.title("My Collection")
        st.markdown(f"<div class='beta-tag'>BETA TESTING</div>", unsafe_allow_html=True)
        
        # --- VIEW SETTINGS ---
        col_view, col_spacer = st.columns([1, 4])
        with col_view:
            view_option = st.selectbox("Show:", ["Last 50", "Last 100", "Show All"], index=0)
            
        limit_val = None
        if view_option == "Last 50": limit_val = 50
        elif view_option == "Last 100": limit_val = 100
        
        
        
        df = load_collection(limit_n=limit_val)
        
        # --- LOAD STAGING ITEMS (Separate Collection) ---
        staging_items = []
        try:
             # Query global staging collection by user email
             s_docs = db.collection('staging_area').where("user_email", "==", st.session_state.get('user_email')).stream()
             for doc in s_docs:
                 d = doc.to_dict()
                 d['id'] = doc.id
                 staging_items.append(d)
        except Exception as e:
            pass
            
        staging_df = pd.DataFrame(staging_items)

        # --- STAGING AREA VIEWER ---

        # --- STAGING AREA VIEWER ---
        if not staging_df.empty:
            with st.expander(f"📦 Staging Area ({len(staging_df)} items - Paper/Foreign)", expanded=False):
                # Ensure columns exist before displaying to avoid KeyErrors
                display_cols = ['Year', 'Denomination', 'category', 'Retailer Invoice #', 'Retailer Item No.', 'Cost', 'Quantity']
                exist_cols = [c for c in display_cols if c in staging_df.columns]
                
                st.dataframe(
                    staging_df[exist_cols].astype(str), 
                    use_container_width=True,
                    hide_index=True
                )
                st.caption("These items are stored but separated from your main US Coin collection.")
        
        if df.empty:
            st.info("Collection is empty. Go to 'Add New Coins'.")
        else:
            pending_df = df[df['deep_dive_status'] != 'COMPLETED']
            pending_count = len(pending_df)
            
            c1, c2 = st.columns([1, 3])
            # ... kept search ...
            with c1: search = st.text_input("🔍 Search")
            with c2:
                if pending_count > 0:
                    if st.button(f"✨ Estimate Pending ({pending_count})", type="primary", width='stretch'):
                        generate_ai_reports(pending_df, silver_p, gold_p)
                else: st.success("All estimated.", icon="✅")

            st.divider()
            if search: view_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            else: view_df = df

            selected_coin_name = st.selectbox("Select Coin to Inspect:", options=view_df['id'].tolist(), format_func=lambda x: f"{view_df[view_df['id']==x].iloc[0].get('Year')} {view_df[view_df['id']==x].iloc[0].get('Denomination')} (ID: {str(x)[-4:]})")
            
            if selected_coin_name:
                coin_data = view_df[view_df['id'] == selected_coin_name].iloc[0]
                
                variety = coin_data.get('potentialVariety')
                if isinstance(variety, dict) and 'name' in variety:
                    st.warning(f"⚠️ **Potential Variety: {variety['name']}**")
                    st.write(variety['description'])
                    st.write(f"**Value if Confirmed:** {variety['estimatedValue']}")
                    col_conf, col_dismiss = st.columns(2)
                    with col_conf:
                        if st.button("✅ Yes, it matches!"): confirm_variety(coin_data)
                    with col_dismiss:
                        if st.button("❌ No, common version"): dismiss_variety(coin_data)
                
                with st.expander("📖 Coin Inspector", expanded=True):
                    ic1, ic2 = st.columns([2, 1])
                    with ic1:
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Value", coin_data.get('AI Estimated Value', 'Pending'))
                        m2.metric("Melt", coin_data.get('Melt Value', 'N/A'))
                        m3.metric("Grade", coin_data.get('Condition'))
                        st.info(coin_data.get('Numismatic Report', 'No report.'))
                        if st.button("✨ Generate AI Report Now"):
                            with numista_loader("analyzing coin details..."):
                                generate_ai_report_single(coin_data, silver_p, gold_p)
                    with ic2:
                        query = f"{coin_data.get('Year')} {coin_data.get('Country')} {coin_data.get('Denomination')}"
                        st.link_button("🔍 Search Google", f"https://www.google.com/search?tbm=isch&q={query}")
                        if coin_data.get('imageUrlObverse'): st.image(coin_data['imageUrlObverse'])
                        else: 
                            f1 = st.file_uploader("Front", type=['png','jpg'], key="f1")
                            if f1: handle_image_upload(f1, coin_data['id'], "obverse")




            # --- LIST VIEW (DATA GRID) ---
            st.markdown("### 🗄️ Inventory List")
            
            # Prepare Data for Grid
            grid_df = view_df.copy()
            
            # Ensure nice column ordering
            desired_columns = [
                "Year", "Denomination", "Mint Mark", "Country", "Quantity", 
                "Condition", "Surface & Strike Quality", "Grading Service", "Grading Cert #",
                "AI Estimated Value", "Cost", "Purchase Date", "Retailer/Website", 
                "Retailer Invoice #", "Retailer Item No.", "Program/Series", 
                "Theme/Subject", "Metal Content", "Melt Value", "Storage Location", 
                "Personal Notes", "Personal Ref #", "id"
            ]
            
            # Select only columns that exist
            final_cols = [c for c in desired_columns if c in grid_df.columns]
            grid_df = grid_df[final_cols]

            # Editable Dataframe (Like Preview)
            edited_grid = st.data_editor(
                grid_df,
                use_container_width=True,
                num_rows="dynamic",
                key="collection_grid",
                column_config={
                    "AI Estimated Value": st.column_config.TextColumn(help="AI Estimate"),
                    "Cost": st.column_config.TextColumn(help="Cost"),
                    "imageUrlObverse": st.column_config.ImageColumn("Front"),
                    "imageUrlReverse": st.column_config.ImageColumn("Back"),
                },
                disabled=["id"] # ID should not be editable
            )
            
            # Save Changes Button
            if st.button("💾 Save Grid Changes", type="primary"):
                # 1. Handle Deletions
                state = st.session_state.get('collection_grid')
                if state and state.get('deleted_rows'):
                    deleted_indices = state['deleted_rows']
                    # Use grid_df (the input to data_editor) to get IDs
                    ids_to_delete = []
                    for i in deleted_indices:
                        try:
                            ids_to_delete.append(grid_df.iloc[i]['id'])
                        except: pass
                    
                    if ids_to_delete:
                        delete_coins(ids_to_delete)

                # 2. Handle Updates (Edits)
                save_edits(edited_grid, view_df)
                st.toast("Changes Saved!", icon="✅")
                time.sleep(1)
                st.rerun()

            st.divider()
             # Bulk Actions Footer
            if st.session_state.get('collection_grid') and len(st.session_state['collection_grid'].get('deleted_rows', [])) > 0:
                 st.warning("⚠️ Rows deleted in grid. Click 'Save Grid Changes' to confirm.")

    elif selection == 'ADD_MANUAL':
        render_add_manual()
    elif selection == 'ADD_SCAN':
        render_add_scan()
    elif selection == 'ADD_UPLOAD':
        render_add_excel()

    elif selection == 'Add New Coins':
        st.title("Add New Coins")
        st.markdown(f"""<div class="beta-tag">AI COIN IDENTIFIER</div>""", unsafe_allow_html=True)
        st.write("")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Excel/CSV", "Manual Entry", "Camera Scan", "Invoice Scan"])
        
        with tab1: render_add_excel()
        with tab2: render_add_manual()
        with tab3:
            st.info("📷 Camera / Microscope Feature Coming Soon")
            st.caption("We are integrating WebRTC for live coin scanning.")
            st.markdown(f"<div class='coming-soon'>Feature Coming Soon</div>", unsafe_allow_html=True)
        with tab4: render_add_scan()

    elif selection == 'Coin Programs':
        render_programs()

    elif selection == 'Inventory':
        st.title("Inventory Manager")
        st.caption("Generate lists, track condition, and audit your collection.")

        # --- FILTERS ---
        df = load_collection(limit_n=None)
        if df.empty:
            st.info("Collection is empty.")
        else:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    countries = ["All"] + sorted(df['Country'].unique().tolist())
                    f_country = st.selectbox("Country", countries)
                with c2:
                    denoms = ["All"] + sorted(df['Denomination'].unique().tolist())
                    f_denom = st.selectbox("Denomination", denoms)
                with c3:
                    min_val = st.number_input("Min Value ($)", value=0)
                with c4:
                    max_val = st.number_input("Max Value ($)", value=100000)

            # Filter Logic
            filtered_df = df.copy()
            if f_country != "All": filtered_df = filtered_df[filtered_df['Country'] == f_country]
            if f_denom != "All": filtered_df = filtered_df[filtered_df['Denomination'] == f_denom]
            
            # Value Filter (Helper)
            def get_val(x):
                try: return float(str(x).replace('$','').replace(',',''))
                except: return 0.0
            
            filtered_df = filtered_df[filtered_df['AI Estimated Value'].apply(get_val).between(min_val, max_val)]
            
            # --- STATS ---
            total = len(filtered_df)
            accounted = len(filtered_df[filtered_df['inventoryStatus'] == 'ACCOUNTED'])
            missing = len(filtered_df[filtered_df['inventoryStatus'] == 'MISSING'])
            
            st.write("")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Items Listed", total)
            s2.metric("Accounted", accounted)
            s3.metric("Missing", missing)
            
            # --- DOWNLOAD REPORT ---
            with s4:
                st.write("")
                if st.button("📄 Download Report"):
                    # Generate HTML for PDF
                    html = f"""
                    <html>
                    <head>
                        <style>
                            body {{ font-family: sans-serif; padding: 20px; }}
                            table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
                            th {{ background: #f0f0f0; padding: 8px; border-bottom: 2px solid #333; text-align: left; }}
                            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                            .status-box {{ width: 15px; height: 15px; border: 1px solid #333; display: inline-block; }}
                        </style>
                    </head>
                    <body>
                        <h1>Inventory Audit - {datetime.now().strftime('%Y-%m-%d')}</h1>
                        <p>Total Items: {total} | Criteria: {f_country}/{f_denom}</p>
                        <table>
                            <thead>
                                <tr>
                                    <th>Check</th><th>Year/Mint</th><th>Denomination</th><th>Condition</th><th>Value</th><th>Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    for i, row in filtered_df.iterrows():
                        html += f"""
                            <tr>
                                <td style="text-align:center;"><span class="status-box"></span></td>
                                <td>{row['Year']} {row['Mint Mark']}</td>
                                <td>{row['Denomination']}</td>
                                <td>{row['Condition']}</td>
                                <td>{row['AI Estimated Value']}</td>
                                <td>{row.get('inventoryNotes', '')}</td>
                            </tr>
                        """
                    html += "</tbody></table></body></html>"
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64}" download="Inventory_Report.html" style="background:#2563eb;color:white;padding:8px 12px;text-decoration:none;border-radius:4px;">Save HTML (Print to PDF)</a>', unsafe_allow_html=True)

            st.divider()

            # --- LIST VIEW (CUSTOM ROW LAYOUT) ---
            st.markdown("### 🗄️ Inventory List")
            
            # Prepare Data
            table_df = view_df.copy()
            if 'Program/Series' not in table_df.columns: table_df['Program/Series'] = ''
            if 'Melt Value' not in table_df.columns: table_df['Melt Value'] = '$0.00'
            
            # --- HEADER ROW ---
            # Columns: [Select, Year/Mint, Denom, Series, Cond, Melt, Cost, Value, Storage, Actions]
            # Weights: [0.5,    1.5,       2,     2,      1,    1,    1,    1.5,   1,       2]
            header_cols = st.columns([0.5, 1.5, 2, 2, 1, 1, 1, 1.5, 1, 2])
            headers = ["", "Year/Mint", "Denomination", "Program/Series", "Condition", "Melt", "Cost", "Value (USD)", "Storage", "Actions"]
            for col, text in zip(header_cols, headers):
                col.markdown(f"**{text}**")
            
            st.divider()
            
            if "selected_rows" not in st.session_state: st.session_state.selected_rows = []
            
            # --- DATA ROWS ---
            for index, row in table_df.iterrows():
                c_id = row['id']
                
                # Format Year/Mint
                y = str(row.get('Year', '')).replace('nan', '')
                m = str(row.get('Mint Mark', '')).replace('nan', '').replace('None', '')
                year_mint = f"{y} ({m})" if m else y
                
                # Render Row
                cols = st.columns([0.5, 1.5, 2, 2, 1, 1, 1, 1.5, 1, 2])
                
                # 1. Select Checkbox
                with cols[0]:
                    is_sel = st.checkbox("", key=f"sel_{c_id}", value=(c_id in st.session_state.selected_rows))
                    if is_sel and c_id not in st.session_state.selected_rows:
                        st.session_state.selected_rows.append(c_id)
                        st.rerun()
                    elif not is_sel and c_id in st.session_state.selected_rows:
                        st.session_state.selected_rows.remove(c_id)
                        st.rerun()
                        
                # 2-9. Data Columns
                cols[1].write(year_mint)
                cols[2].write(row.get('Denomination', ''))
                cols[3].write(row.get('Program/Series', '-'))
                cols[4].write(row.get('Condition', ''))
                cols[5].write(row.get('Melt Value', '$0.00'))
                cols[6].write(f"${float(clean_money_string(row.get('Cost'))):,.2f}")
                
                val_str = row.get('AI Estimated Value', 'Pending')
                cols[7].markdown(f"**{val_str}**" if val_str != "Pending" else "_Pending_")
                
                cols[8].write(row.get('Storage Location', '-'))
                
                # 10. Actions [Deep Dive] [Edit] [Delete]
                with cols[9]:
                    ac1, ac2, ac3 = st.columns(3)
                    # Deep Dive (Book)
                    if ac1.button("📖", key=f"btn_dive_{c_id}", help="AI Deep Dive"):
                        st.session_state.messages.append({"role": "user", "content": f"Tell me about my {year_mint} {row.get('Denomination')}"})
                        selection = 'Home Dashboard' # Force nav? No, keep context.
                        # Ideally, open a modal or sidebar. For now, toast info.
                        st.toast(f"Researching {year_mint}...", icon="🤖")
                        # trigger deep dive logic here if needed
                        
                    # Edit (Pencil) - For now just toast "Edit Coming Soon" or implement basic
                    if ac2.button("✏️", key=f"btn_edit_{c_id}", help="Manual Edit"):
                        st.toast(f"Edit {year_mint} (Feature Coming Soon)", icon="✏️")
                        
                    # Delete (Trash)
                    if ac3.button("🗑️", key=f"btn_del_row_{c_id}", help="Delete Coin"):
                         delete_coins([c_id])
                         st.toast("Deleted!", icon="🗑️")
                         time.sleep(0.5)
                         st.rerun()
                
                st.divider()

            # Bulk Actions Footer
            if st.session_state.selected_rows:
                st.error(f"{len(st.session_state.selected_rows)} Items Selected")
                if st.button(f"🗑️ Delete {len(st.session_state.selected_rows)} Selected Items", type="primary"):
                    delete_coins(st.session_state.selected_rows)
                    st.session_state.selected_rows = []
                    st.success("Bulk Delete Complete")
                    st.rerun()

    elif selection == 'My Wishlist':
        st.title("My Wishlist")
        st.caption("Track coins you want to acquire. Items in green are already in your collection.")
        
        path = get_user_collection_path()
        if path:
            wish_ref = db.collection(path.replace("coins", "wishlist"))
            wish_docs = wish_ref.stream()
            wishlist = [d.to_dict() for d in wish_docs]
            wishlist_df = pd.DataFrame(wishlist)
        else:
            wishlist_df = pd.DataFrame()

        # --- CONTROLS ---
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info("💡 Tip: Matches are detected automatically based on Year and Denomination.")
        with c2:
            if st.button("➕ Add Item", type="primary"):
                st.session_state.show_add_wish = True

        if st.session_state.get('show_add_wish'):
            with st.form("add_wish"):
                st.subheader("Add to Wishlist")
                w_year = st.text_input("Year")
                w_denom = st.text_input("Denomination", placeholder="e.g. Quarter")
                w_series = st.text_input("Series", placeholder="e.g. American Women")
                w_price = st.number_input("Max Price ($)", value=0.0)
                w_prio = st.selectbox("Priority", ["High", "Medium", "Low"])
                
                if st.form_submit_button("Save Item"):
                    uid = str(uuid.uuid4())
                    new_item = {
                        "id": uid, "year": w_year, "denomination": w_denom, 
                        "series": w_series, "maxPrice": w_price, "priority": w_prio,
                        "created_at": firestore.SERVER_TIMESTAMP
                    }
                    db.collection(path.replace("coins", "wishlist")).document(uid).set(new_item)
                    st.session_state.show_add_wish = False
                    st.success("Added!"); st.rerun()
                
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_wish = False; st.rerun()

        # --- DISPLAY ---
        # --- DISPLAY ---
        
        # 1. Load Collection (Needed for both lists)
        my_coins = load_collection(limit_n=None)
        
        tab_custom, tab_programs = st.tabs(["My Picks", "From Coin Programs"])
        
        with tab_custom:
            if not wishlist_df.empty:
                for index, item in wishlist_df.iterrows():
                    # Simple Match: Year + Denom
                    matches = my_coins[
                        (my_coins['Year'] == item['year']) & 
                        (my_coins['Denomination'].str.contains(item['denomination'], case=False, na=False))
                    ]
                    is_owned = not matches.empty
                    
                    # Card Style
                    bg_color = "#ecfdf5" if is_owned else "white" # Emerald-50 or White
                    border_color = "#10b981" if is_owned else "#e2e8f0"
                    
                    with st.container(border=True):
                        cols = st.columns([4, 2, 1])
                        with cols[0]:
                            st.markdown(f"### {item.get('year')} {item.get('denomination')}")
                            st.caption(f"{item.get('series','')}")
                            if is_owned: st.success("✅ In Collection")
                        with cols[1]:
                            st.write(f"**Budget:** ${item.get('maxPrice',0)}")
                            st.write(f"**Priority:** {item.get('priority')}")
                        with cols[2]:
                            if st.button("🗑️", key=f"del_w_{item['id']}"):
                                db.collection(path.replace("coins", "wishlist")).document(item['id']).delete()
                                st.rerun()
            else:
                st.info("Your custom wishlist is empty.")

        with tab_programs:
            st.caption("Items automatically identified as missing from your tracked Programs.")
            
            missing_items = []
            
            for cat, progs in US_PROGRAMS.items():
                for p in progs:
                    for c in p['coins']:
                        # Skip if "Pending"
                        if "Pending" in c: continue
                        
                        # Check ownership
                        # Broad match same as render_programs
                        matches = my_coins[
                            my_coins.astype(str).apply(lambda x: x.str.contains(c, case=False, na=False)).any(axis=1)
                        ]
                        
                        if matches.empty:
                            missing_items.append({
                                "program": p['name'],
                                "coin": c,
                                "year": p.get('years', 'Unknown')
                            })
            
            if missing_items:
                st.write(f"**{len(missing_items)} Missing Items Found**")
                
                # Group by Program for cleaner display
                df_miss = pd.DataFrame(missing_items)
                
                for prog_name, group in df_miss.groupby("program"):
                    with st.expander(f"{prog_name} ({len(group)})", expanded=False):
                        for i, row in group.iterrows():
                             c1, c2 = st.columns([4, 1])
                             c1.markdown(f"**{row['coin']}**")
                             c1.caption(f"Year/Era: {row['year']}")
                             # Future: Add "Quick Add" button here?
                             # c2.button("Find", key=f"find_{row['coin']}")
            else:
                st.success("🎉 No missing items found in tracked programs!")

    elif selection == 'Metal spot prices':
        st.title("Metal Spot Prices")
        st.markdown(f"<div class='coming-soon'>Feature Coming Soon</div>", unsafe_allow_html=True)

    elif selection == 'Settings & Backup':
        st.title("Settings & Backup")
        st.markdown("Manage your collection data, export to backup file (JSON), or restore from a previous session.")
        st.divider()
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📤 Export Data")
            
            # JSON BACKUP
            try:
                df = load_collection()
                wish_path = f"users/{st.session_state.user_email}/wishlist"
                wish_docs = db.collection(wish_path).stream()
                wish_list = [d.to_dict() for d in wish_docs]
                data = {"coins": df.to_dict(orient="records"), "wishlist": wish_list, "timestamp": datetime.now().isoformat()}
                json_data = json.dumps(data, indent=2)
                st.download_button("📥 Backup JSON (Full)", json_data, "Numisma_Backup.json", "application/json", use_container_width=True)
            except Exception as e: st.error(f"Backup Error: {e}")
            
            st.write("")
            
            # CSV EXPORT
            df = load_collection(limit_n=None)
            if not df.empty: 
                st.download_button("📊 Export CSV (Coins Only)", df.to_csv(index=False).encode('utf-8'), "coins.csv", "text/csv", use_container_width=True)
            else:
                st.info("Collection empty, cannot export CSV.")
        
        with c2:
            st.subheader("📥 Restore Data")
            uploaded_restore = st.file_uploader("Restore JSON Backup", type=['json'], key="rest_page")
            if uploaded_restore:
                if st.button("⚠️ Confirm Restore", type="primary", key="conf_rest_page", use_container_width=True):
                    try:
                        data = json.load(uploaded_restore)
                        coins = data.get('coins', [])
                        wish = data.get('wishlist', [])
                        path = get_user_collection_path()
                        batch = db.batch(); count = 0
                        for c in coins:
                            ref = db.collection(path).document(c['id'])
                            batch.set(ref, c)
                            count += 1
                            if count > 400: batch.commit(); batch = db.batch(); count = 0
                        w_path = path.replace("coins", "wishlist")
                        for w in wish:
                            ref = db.collection(w_path).document(w['id'])
                            batch.set(ref, w)
                        batch.commit()
                        st.success("Restore Complete!"); st.rerun()
                    except Exception as e: st.error(f"Restore Failed: {e}")

        st.divider()
        st.subheader("Account Actions")
        if st.button("🚪 Log Out", key="logout_page"): logout()

    elif selection == 'Our Team':
        st.title("Our Team")
        st.markdown(f"<div class='beta-tag'>MEET THE TEAM</div>", unsafe_allow_html=True)
        st.write("")
        
        # Team Member: Eric Seaman
        c1, c2 = st.columns([1, 3])
        with c1:
            st.image("https://placehold.co/400x400?text=ES", caption="Eric Seaman", width='stretch')
        with c2:
            st.subheader("Eric Seaman")
            st.caption("Founder & Lead Developer")
            st.write("In May 2025 I retired after 26 years of service in the US Army. For 20 of those years property accountability was my primary focus; I was responsible for the tracking, managing and stewardship of millions of dollars in mission-critical assets.")
            st.write("After retiring, I took part in Google's Veteran's Launchpad and received training, and later certification, as a Generative AI (Artificial Intelligence) Leader. Subsequently, I was visiting a beloved family member at the time and took the Google AI training in their library, surrounded by their coin collection, 50+ years in the making. When that beloved family member asked me to help them organize their coin collection, my supply sergeant instincts (and newfound enthusiasm for AI), took over and I realized that the same discipline I used to manage military inventory could be powered by AI to help collectors intelligently catalog, research, and manage their treasures.")
            st.write("While coins are the focus of Numista.AI, the concept will be expanded to include the limitless amount of assets and collectibles out there; baseball cards, paintings, family heirlooms, just about anything that people love to collect and are passionate about.")
            st.write("LinkedIn Bio: www.linkedin.com/in/ericdseaman")
            st.link_button("Connect on LinkedIn", "https://www.linkedin.com/in/ericdseaman")
    elif selection == 'Customer Service':
        st.title("Customer Service")
        st.markdown(f"<div class='beta-tag'>SUPPORT & FEEDBACK</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown(
            "We're here to help! If you have any questions, want to report a bug, or have a feature request, "
            "please let us know. You can either email us directly or use the form below."
        )
        
        st.subheader("Direct Email")
        st.markdown("For immediate assistance or to send attachments, email Eric directly:")
        st.link_button("📧 Email eric@numista.ai", "mailto:eric@numista.ai", type="primary")
        
        st.divider()
        
        st.subheader("Send Feedback")
        with st.form("feedback_form"):
            feedback_type = st.selectbox("Topic", ["Bug Report", "Feature Request", "General Inquiry"])
            feedback_message = st.text_area("Message", placeholder="Describe your issue or suggestion here...")
            
            if st.form_submit_button("Submit"):
                if not feedback_message.strip():
                    st.error("Please enter a message before submitting.")
                else:
                    # Save to Firestore
                    try:
                        uid = str(uuid.uuid4())
                        user_email = st.session_state.get('user_email', 'unknown_user')
                        feedback_data = {
                            "id": uid,
                            "user_email": user_email,
                            "type": feedback_type,
                            "message": feedback_message,
                            "status": "New",
                            "created_at": firestore.SERVER_TIMESTAMP
                        }
                        # Create a 'feedback' collection at the root level
                        db.collection("feedback").document(uid).set(feedback_data)
                        st.success("Thank you for your feedback! Eric will review it shortly.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Failed to submit feedback. Please use the email link above. (Error: {e})")

    # --- BOTTOM UTILITY BAR REMOVED ---

