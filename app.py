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
import requests
import firebase_admin
from firebase_admin import auth, credentials
from dotenv import load_dotenv

from google.oauth2 import service_account

# --- CONFIGURATION ---
load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "us-west1"
st.set_page_config(page_title="Numista.AI", layout="wide", initial_sidebar_state="collapsed")
st.sidebar.caption("v2.5 - DEBUG MODE")

# Simple Sidebar Suppression (Just in case Streamlit tries to render it)
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if "vertex_init" not in st.session_state:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    st.session_state.vertex_init = True
    
# --- CREDENTIALS HARD FIX ---
# Explicitly load service account to avoid "Reauthentication needed" / ADC errors
key_path = "serviceAccountKey.json.json"
cred_admin = credentials.Certificate(key_path)
cred_firestore = service_account.Credentials.from_service_account_file(key_path)

# 1. Init Firebase Admin
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred_admin)

# 2. Init Firestore Client with explicit creds
db = firestore.Client(credentials=cred_firestore, project=PROJECT_ID)

model = GenerativeModel("gemini-2.5-flash")

# --- FIREBASE CLIENT API KEY ---
# Required for Client-Side Operations from Python (Login, Reset Password)
# TODO: User must add this to .env or replace below
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY", "") 

# --- COOKIE MANAGER (FIXED: NO CACHE) ---
# We instantiate this directly to avoid CachedWidgetWarning
cookie_manager = stx.CookieManager(key="numista_cookies")

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
        padding-top: 2rem;
        padding-bottom: 5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 98% !important;
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
    col1, x_col, col3 = st.columns([1, 2, 1])
    with x_col:
        st.image("public/Numista.AI Logo.svg", width=200)
    st.markdown("<h1 style='text-align: center;'>Numista.AI <span class='beta-tag'>BETA v2.6 (App)</span></h1>", unsafe_allow_html=True)
    st.write("") # Padding
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("🔐 Secure Login")
        
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
    if not st.session_state.get('user_email'): return None
    return f"users/{st.session_state.user_email}/coins"

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
    "Retailer/Website", "Metal Content", "Melt Value", "Personal Notes", 
    "Personal Ref #", "AI Estimated Value", "Storage Location"
]

def get_empty_collection_df():
    system_cols = ['id', 'deep_dive_status', 'Numismatic Report', 'potentialVariety', 'imageUrlObverse', 'imageUrlReverse', 'inventoryStatus']
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
    system_cols = ['id', 'deep_dive_status', 'Numismatic Report', 'potentialVariety', 'imageUrlObverse', 'imageUrlReverse', 'inventoryStatus']
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

def handle_image_upload(file, coin_id, side):
    path = get_user_collection_path()
    bytes_data = file.getvalue()
    base64_img = base64.b64encode(bytes_data).decode('utf-8')
    final_str = f"data:image/png;base64,{base64_img}"
    field = "imageUrlObverse" if side == "obverse" else "imageUrlReverse"
    db.collection(path).document(coin_id).set({field: final_str}, merge=True)
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

def render_add_excel():
    st.info("📂 Upload Excel or CSV to Fast Map coins.")
    
    # Initialize Staging State
    if 'upload_stage' not in st.session_state: st.session_state['upload_stage'] = None

    # --- STAGE 1: UPLOAD & PROCESS ---
    if st.session_state['upload_stage'] is None:
        uploaded_file = st.file_uploader("Upload Inventory File", type=['xlsx', 'xls', 'csv'])
        if uploaded_file and st.button("Process File & Check Duplicates"):
            if uploaded_file.name.endswith('csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            
            progress = st.progress(0); chat = model.start_chat()
            processed_coins = []
            
            SYSTEM_PROMPT = (
                "You are an expert Numismatist. Rules: No deep research. Fix typos. Return JSON 19-key schema.\n"
                "{ \"Country\": \"US\", \"Year\": \"Year\", \"Denomination\": \"Name\", \"Mint Mark\": \"Letter\", \n"
                "  \"Quantity\": \"1\", \"Program/Series\": \"Name\", \"Theme/Subject\": \"Name\", \"Condition\": \"Grade\", \n"
                "  \"Surface & Strike Quality\": \"Notes\", \"Grading Service\": \"Name\", \"Grading Cert #\": \"Num\", \n"
                "  \"Cost\": \"$0.00\", \"Purchase Date\": \"Date\", \"Retailer/Website\": \"Name\", \n"
                "  \"Metal Content\": \"Composition\", \"Melt Value\": \"Pending\", \"Personal Notes\": \"Notes\", \n"
                "  \"Personal Ref #\": \"Num\", \"AI Estimated Value\": \"Pending\", \"inventoryStatus\": \"UNCHECKED\", \"Storage Location\": \"\" }"
            )
            
            for i, row in df.iterrows():
                try:
                    resp = chat.send_message([SYSTEM_PROMPT, f"Input: {row.to_string()}"])
                    clean_text = resp.text.replace("```json", "").replace("```", "").strip()
                    # Handle potential list response or single object
                    if clean_text.startswith("["): chunk = json.loads(clean_text)
                    else: chunk = [json.loads(clean_text)]
                    
                    for data in chunk:
                        data["id"] = str(uuid.uuid4())
                        processed_coins.append(data)
                except: pass
                progress.progress((i+1)/len(df))
                time.sleep(0.5)
            
            if processed_coins:
                new_df = pd.DataFrame(processed_coins)
                existing_df = load_collection(limit_n=None)
                
                # NORMALIZE BEFORE CHECK
                new_df = normalize_coin_data(new_df)
                
                staged_df = identify_duplicates(new_df, existing_df)
                
                # Move 'Status' to front
                cols = ['Status'] + [c for c in staged_df.columns if c != 'Status']
                st.session_state['upload_stage'] = staged_df[cols]
                st.rerun()

    # --- STAGE 2: PREVIEW & CONFIRM ---
    else:
        st.divider()
        st.subheader("Import Preview")
        st.caption("Review the coins below. Orange indicates a potential duplicate in your vault.")
        
        staged_df = st.session_state['upload_stage']
        
        # Color Warning
        n_dupes = len(staged_df[staged_df['Status'] == 'DUPLICATE'])
        if n_dupes > 0: 
            st.warning(f"⚠️ {n_dupes} Potential Duplicates Identified. You can edit rows below to fix them.", icon="⚠️")
        else: 
            st.success("✅ No Duplicates Found", icon="✅")
        
        # Editable Dataframe
        edited_df = st.data_editor(
            staged_df, 
            use_container_width=True, 
            num_rows="dynamic",
            key="editor_upload"
        )
        
        c1, c2, c3 = st.columns([1, 2, 2])
        
        with c1:
            if st.button("Cancel", key="cancel_upload"):
                st.session_state['upload_stage'] = None
                st.rerun()
        
        with c2:
            if st.button("Import New Only", type="secondary", use_container_width=True):
                final = edited_df[edited_df['Status'] == 'NEW']
                save_to_firestore(final)
                st.session_state['upload_stage'] = None

        with c3:
            if st.button("Import All", type="primary", use_container_width=True):
                save_to_firestore(edited_df)
                st.session_state['upload_stage'] = None

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

    # --- STAGE 2: PREVIEW ---
    else:
        st.divider()
        st.subheader("Confirm Manual Addition")
        st.caption("Review the coins below. Orange indicates a potential duplicate in your vault.")
        
        staged_df = st.session_state['upload_stage']
        
        # Color Warning
        n_dupes = len(staged_df[staged_df['Status'] == 'DUPLICATE'])
        if n_dupes > 0: 
            st.warning(f"⚠️ {n_dupes} Potential Duplicates Identified. You can edit rows below to fix them.", icon="⚠️")
        else: 
            st.success("✅ No Duplicates Found", icon="✅")
        
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

def render_add_scan():
    st.info("🧾 Upload an Invoice (PDF) to auto-extract coin data.")
    
    if 'upload_stage' not in st.session_state: st.session_state['upload_stage'] = None

    if st.session_state['upload_stage'] is None:
        inv_file = st.file_uploader("Invoice PDF", type=['pdf'])
        if inv_file and st.button("Process Invoice"):
            with st.spinner("Document AI Processing..."):
                try:
                    doc = process_invoice(inv_file.getvalue())
                    st.success("OCR Complete. Analyzing data...")
                    
                    # --- AI PARSING ---
                    chat = model.start_chat()
                    
                    # COIN DICTIONARY (MATCHING NODE.JS BACKEND)
                    COIN_DICTIONARY = [
                        { "val": 0.01, "formal": "Lincoln Cent", "slang": ["penny", "wheatie", "steelie", "red cent", "lincoln wheat cent", "wheat cent"] },
                        { "val": 0.05, "formal": "Jefferson Nickel", "slang": ["nickel", "buffalo", "war nickel", "v-nickel", "buffalo nickel"] },
                        { "val": 0.10, "formal": "Roosevelt Dime", "slang": ["dime", "mercury", "rosie", "winged liberty", "mercury dime"] },
                        { "val": 0.25, "formal": "Washington Quarter", "slang": ["quarter", "two bits", "state quarter", "2026 semiquin"] },
                        { "val": 0.50, "formal": "Kennedy Half Dollar", "slang": ["half", "fifty cent", "franklin", "walker", "walking liberty"] },
                        { "val": 1.00, "formal": "Morgan Silver Dollar", "slang": ["morgan", "silver dollar", "cartwheel", "peace dollar", "peace"] }
                    ]

                    SYSTEM_PROMPT = (
                        "You are an expert Numismatist. Extract coins from this invoice text. "
                        "Return a JSON LIST of objects using this schema: \n"
                        "{ \"Country\": \"US\", \"Year\": \"Year\", \"Denomination\": \"Name\", \"Mint Mark\": \"Letter\", \n"
                        "  \"Quantity\": \"1\", \"Program/Series\": \"Name\", \"Theme/Subject\": \"Name\", \"Condition\": \"Grade\", \n"
                        "  \"Surface & Strike Quality\": \"Notes\", \"Grading Service\": \"Name\", \"Grading Cert #\": \"Num\", \n"
                        "  \"Cost\": \"$0.00\", \"Purchase Date\": \"Date\", \"Retailer/Website\": \"Name\", \"Retailer Invoice #\": \"String\", \n"
                        "  \"Retailer Item No.\": \"String\", \n"
                        "  \"Metal Content\": \"Composition\", \"Melt Value\": \"Pending\", \"Personal Notes\": \"Notes\", \n"
                        "  \"Personal Ref #\": \"Num\", \"AI Estimated Value\": \"Pending\", \"inventoryStatus\": \"UNCHECKED\", \"Storage Location\": \"\" }\n\n"
                        f"IMPORTANT: Use this dictionary to map slang to formal coin names: {json.dumps(COIN_DICTIONARY)}"
                    )
                    resp = chat.send_message([SYSTEM_PROMPT, f"Invoice Text: {doc.text}"])
                    
                    # Parse JSON
                    clean_json = resp.text.replace("```json", "").replace("```", "").strip()
                    if clean_json.startswith("{"): clean_json = f"[{clean_json}]" # Handle single object response
                    
                    coins = json.loads(clean_json)
                    
                    # Prepare Data
                    for coin in coins:
                        coin["id"] = str(uuid.uuid4())
                        coin["deep_dive_status"] = "PENDING"
                        # Ensure fields exist
                        for col in DISPLAY_ORDER:
                             if col not in coin: coin[col] = ""

                    if coins:
                        new_df = pd.DataFrame(coins)
                        existing_df = load_collection(limit_n=None)
                        
                        # NORMALIZE
                        new_df = normalize_coin_data(new_df)
                        
                        staged_df = identify_duplicates(new_df, existing_df)
                        
                        cols = ['Status'] + [c for c in staged_df.columns if c != 'Status']
                        st.session_state['upload_stage'] = staged_df[cols]
                        st.rerun()

                except Exception as e:
                    st.error(f"Processing Error: {e}")

    # --- STAGE 2: PREVIEW ---
    else:
        st.divider()
        st.subheader("Import Preview")
        st.caption("Review the coins below. Orange indicates a potential duplicate in your vault.")
        
        staged_df = st.session_state['upload_stage']
        
        # Color Warning
        n_dupes = len(staged_df[staged_df['Status'] == 'DUPLICATE'])
        if n_dupes > 0: 
            st.warning(f"⚠️ {n_dupes} Potential Duplicates Identified. You can edit rows below to fix them.", icon="⚠️")
        else: 
            st.success("✅ No Duplicates Found", icon="✅")
        
        # Toggle View Mode
        view_mode = st.radio("View Mode:", ["Table View", "Detailed Card View"], horizontal=True)

        if view_mode == "Table View":
            edited_df = st.data_editor(
                staged_df, 
                use_container_width=True, 
                num_rows="dynamic",
                key="editor_scan"
            )
        else:
            edited_df = staged_df.copy() # No editing in card mode for now
            st.info("ℹ️ Switch to Table View to edit values.")
            for i, row in staged_df.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.metric("Status", row.get('Status', 'UNKNOWN'))
                        st.caption(f"Duplicate Key:\n{row.get('Duplicate Check Key', 'N/A')}")
                    with c2:
                        st.subheader(f"{row.get('Year', '')} {row.get('Denomination', '')}")
                        st.text(f"Invoice #: {row.get('Retailer Invoice #', 'N/A')} | Item #: {row.get('Retailer Item No.', 'N/A')}")
                        st.json(row.to_dict(), expanded=False)
        
        c1, c2, c3 = st.columns([1, 2, 2])
        
        with c1:
            if st.button("Cancel", key="cancel_scan"):
                st.session_state['upload_stage'] = None
                st.rerun()
        
        with c2:
            if st.button("Import New Only", type="secondary", use_container_width=True, key="imp_new_scan"):
                final = edited_df[edited_df['Status'] == 'NEW']
                save_to_firestore(final)
                st.session_state['upload_stage'] = None

        with c3:
            if st.button("Import All", type="primary", use_container_width=True, key="imp_all_scan"):
                save_to_firestore(edited_df)
                st.session_state['upload_stage'] = None

# --- MAIN APP LOGIC ---

if not check_login():
    login_screen()
else:
    # --- SIDEBAR LOGIC ---
    # --- NO SIDEBAR ---
    # We rely entirely on the shell for navigation. 
    # Tools (Save/Backup) are moved to the main page.
    
    # 1. Determine Selection from URL Page Param
    page_param = st.query_params.get("page", "home").lower()
    
    if page_param == "collection": selection = "My Collection"
    elif page_param == "add": selection = "Add New Coins"
    elif page_param == "inventory": selection = "Inventory"
    elif page_param == "wishlist": selection = "My Wishlist"
    elif page_param == "team": selection = "Our Team"
    elif page_param == "spots": selection = "Metal spot prices"
    elif page_param == "add_manual": selection = "ADD_MANUAL"
    elif page_param == "add_scan": selection = "ADD_SCAN"
    elif page_param == "add_upload": selection = "ADD_UPLOAD"
    else: selection = "Home Dashboard"

    # --- TOP UTILITY BAR MOVED TO BOTTOM ---
        
    st.divider()
    uploaded_restore = st.file_uploader("Restore JSON Backup", type=['json'])
    if uploaded_restore:
        if st.button("Confirm Restore"):
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
        
        if df.empty:
            st.info("Collection is empty. Go to 'Add New Coins'.")
        else:
            pending_df = df[df['deep_dive_status'] != 'COMPLETED']
            pending_count = len(pending_df)
            
            c1, c2 = st.columns([3, 1])
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




            # --- LIST VIEW (EXPANDED 12-COL + STICKY ACTIONS) ---
            st.markdown("### 🗄️ Inventory List")
            
            # Prepare Data
            table_df = view_df.copy()

            # Columns: [Sel, YR/MM/CNTRY, Denom, Series, Theme, Metal, Grade, Strike, Purch, Cost, AI, Actions]
            # Weights: 0.4, 1.8, 1.2, 1.4, 1.4, 1.2, 1.0, 1.0, 1.2, 1.0, 1.2, 0.8
            col_weights = [0.4, 1.8, 1.2, 1.4, 1.4, 1.2, 1.0, 1.0, 1.2, 1.0, 1.2, 0.8]
            headers = ["", "YR/MM/CNTRY", "Denomination", "Series", "Theme", "Metal", "Grade", "Strike", "Purchased", "Cost", "AI Value", "Actions"]
            
            # Sticky Header Container
            st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
            with st.container():
                header_cols = st.columns(col_weights)
                for col, text in zip(header_cols, headers):
                     col.markdown(f"<div style='white-space: nowrap; font-weight: bold; color: #475569; font-size: 13px;'>{text}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if "selected_rows" not in st.session_state: st.session_state.selected_rows = []
            
            for index, row in table_df.iterrows():
                c_id = row['id']
                cols = st.columns(col_weights)
                
                # 1. Select
                with cols[0]:
                    def update_sel(cid=c_id):
                        if cid in st.session_state.selected_rows: st.session_state.selected_rows.remove(cid)
                        else: st.session_state.selected_rows.append(cid)
                    st.checkbox("", key=f"sel_{c_id}", value=(c_id in st.session_state.selected_rows), on_change=update_sel, label_visibility="collapsed")

                # 2. Issue (Year-Mint \n Country)
                y = str(row.get('Year', '')).replace('nan', '')
                m = str(row.get('Mint Mark', '')).replace('nan',('').replace('None', ''))
                c = str(row.get('Country', '')).replace('nan', '')
                issue_main = f"{y}-{m}" if m else y
                with cols[1]:
                    st.markdown(f"<div class='issue-main'>{issue_main}</div><div class='issue-sub'>{c}</div>", unsafe_allow_html=True)

                # 3. Denom
                cols[2].write(row.get('Denomination', '-'))
                
                # 4. Series
                cols[3].write(row.get('Program/Series', '-'))
                
                # 5. Theme
                theme = row.get('Theme/Subject', '-')
                if len(str(theme)) > 15: theme = theme[:13] + ".."
                cols[4].write(theme)
                
                # 6. Metal [NEW]
                cols[5].write(row.get('Metal Content', '-'))
                
                # 7. Grade
                grade = row.get('Condition', '-')
                if grade and grade != '-' and grade != 'None':
                    cols[6].markdown(f"<span class='grade-pill'>{grade}</span>", unsafe_allow_html=True)
                else: cols[6].write("-")
                
                # 8. Strike
                cols[7].write(row.get('Surface & Strike Quality', '-'))

                # 9. Purchased [NEW]
                p_date = str(row.get('Purchase Date', '-')).split(' ')[0] # Simple date
                cols[8].write(p_date)

                # 10. Cost
                cost_val = clean_money_string(row.get('Cost'))
                cols[9].write(f"${cost_val:,.2f}")
                
                # 11. AI Value
                ai_val = row.get('AI Estimated Value', 'Pending')
                if ai_val != 'Pending': cols[10].markdown(f"**{ai_val}**")
                else: cols[10].markdown("_Pending_")
                
                # 12. Actions
                with cols[11]:
                   ac1, ac2 = st.columns(2)
                   if ac1.button("✏️", key=f"e_{c_id}"): st.toast("Edit Feature Coming Soon")
                   if ac2.button("🗑️", key=f"d_{c_id}"): delete_coins([c_id]); st.rerun()

                st.markdown("<hr style='margin: 4px 0px; opacity: 0.2;'>", unsafe_allow_html=True)

            # Sticky Footer for Bulk Actions
            if st.session_state.selected_rows:
                with st.container(border=True):
                     bc1, bc2 = st.columns([1, 4])
                     with bc1:
                         if st.button(f"🗑️ Delete {len(st.session_state.selected_rows)} Items", type="primary", use_container_width=True):
                             delete_coins(st.session_state.selected_rows)
                             st.session_state.selected_rows = []
                             st.rerun()
                     with bc2:
                         st.warning("⚠️ This action cannot be undone.")


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
        if not wishlist_df.empty:
            # Check Ownership Logic
            my_coins = load_collection(limit_n=None)
            
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
            st.info("Wishlist is empty.")

    elif selection == 'Metal spot prices':
        st.title("Metal Spot Prices")
        st.markdown(f"<div class='coming-soon'>Feature Coming Soon</div>", unsafe_allow_html=True)

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
    # --- BOTTOM UTILITY BAR ---
    st.divider()
    with st.expander("🛠️ Data & Settings (Backup, Restore, Save)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("💾 Save Updates", use_container_width=True, key="save_btm"): st.toast("Saved!")
        with c2:
            if st.button("🚪 Log Out", use_container_width=True, key="logout_btm"): logout()
        with c3:
            if st.button("📥 Backup JSON", use_container_width=True, key="bkp_btm"):
                try:
                    df = load_collection()
                    wish_path = f"users/{st.session_state.user_email}/wishlist"
                    wish_docs = db.collection(wish_path).stream()
                    wish_list = [d.to_dict() for d in wish_docs]
                    data = {"coins": df.to_dict(orient="records"), "wishlist": wish_list, "timestamp": datetime.now().isoformat()}
                    st.download_button("Click to Download", json.dumps(data, indent=2), "Numisma_Backup.json", "application/json")
                except Exception as e: st.error(f"Backup Error: {e}")
        with c4:
             if st.button("📊 CSV Export", use_container_width=True, key="csv_btm"):
                df = load_collection(limit_n=None)
                if not df.empty: st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), "coins.csv", "text/csv")
        
        st.divider()
        uploaded_restore = st.file_uploader("Restore JSON Backup", type=['json'], key="rest_btm")
        if uploaded_restore:
            if st.button("Confirm Restore", key="conf_rest_btm"):
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
