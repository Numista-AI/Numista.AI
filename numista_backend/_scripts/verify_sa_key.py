# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules

from google import genai
from google.oauth2 import service_account
import os
import sys
from dotenv import load_dotenv

# Force UTF-8 output so emoji don't crash on Windows cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "us-central1"

def test_model_with_sa(model_name):
    print(f"\n==========================================")
    print(f"TESTING: {model_name} in {LOCATION}")
    try:
        key_path = "serviceAccountKey.json.json"
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

# Test 1: 2.5 Flash
test_model_with_sa("gemini-3.5-flash")

# Test 2: 3.0 Flash (Check if name is correct)
test_model_with_sa("gemini-3.5-flash")
