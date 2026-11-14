# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules

from google import genai
from google.oauth2 import service_account
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

_BACKEND_ROOT = str(Path(__file__).resolve().parent.parent)
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from config import GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL

# Force UTF-8 output so emoji don't crash on Windows cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    load_dotenv(encoding="utf-8-sig")
except UnicodeDecodeError:
    load_dotenv(encoding="cp1252")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "studio-9101802118-8c9a8")
LOCATION = os.environ.get("GCP_REGION", "global")

def _resolve_sa_key_path() -> str:
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if env_path and Path(env_path).is_file():
        return env_path
    return str(Path(_BACKEND_ROOT) / "serviceAccountKey.json")

def test_model_with_sa(model_name):
    print(f"\n==========================================")
    print(f"TESTING: {model_name} in {LOCATION}")
    try:
        key_path = _resolve_sa_key_path()
        creds = service_account.Credentials.from_service_account_file(key_path)
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION, credentials=creds)
        
        chat = client.chats.create(model=model_name)
        response = chat.send_message("Ping")
        print(f"✅ SUCCESS: {model_name} RESPONSE: {response.text}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {model_name}")
        print(f"ERROR: {e}")
        return False

# Test 1: Primary Flash workhorse (Gemini 4 Hydrogen)
test_model_with_sa(GEMINI_FLASH_MODEL)

# Test 2: High-reasoning Pro model (Gemini 4 Argon)
test_model_with_sa(GEMINI_PRO_MODEL)
