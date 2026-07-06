# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import sys
import os
from dotenv import load_dotenv
from google import genai

# Force UTF-8 output so emoji don't crash on Windows cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"

def test_model(model_name, location):
    print(f"\n--- Testing {model_name} in {location} ---")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)
        chat = client.chats.create(model=model_name)
        response = chat.send_message("Ping")
        print(f"✅ SUCCESS: {model_name} working in {location} -> response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

# Test current model landscape
test_model("gemini-3.5-flash", "us-central1")
test_model("gemini-2.5-pro", "us-central1")
test_model("gemini-3.5-flash", "us-central1")
