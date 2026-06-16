
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "us-central1"

def test_model_with_sa(model_name):
    print(f"\n==========================================")
    print(f"TESTING: {model_name} in {LOCATION}")
    try:
        key_path = "serviceAccountKey.json.json"
        creds = service_account.Credentials.from_service_account_file(key_path)
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)
        
        model = GenerativeModel(model_name)
        chat = model.start_chat()
        response = chat.send_message("Ping")
        print(f"✅ SUCCESS: {model_name} RESPONSE: {response.text}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {model_name}")
        print(f"ERROR: {e}")
        return False

# Test 1: 2.5 Flash
test_model_with_sa("gemini-2.5-flash")

# Test 2: 3.0 Flash (Check if name is correct)
test_model_with_sa("gemini-3.0-flash")
