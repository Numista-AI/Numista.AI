
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = "studio-9101802118-8c9a8"

def test_model(model_name, location):
    print(f"\n--- Testing {model_name} in {location} ---")
    try:
        vertexai.init(project=PROJECT_ID, location=location)
        model = GenerativeModel(model_name)
        chat = model.start_chat()
        response = chat.send_message("Ping")
        print(f"✅ SUCCESS: {model_name} working in {location}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

# STRICTLY TESTING 2.5+ MODELS ONLY

# 1. Preferred Region (us-east4)
test_model("gemini-3.0-flash", "us-east4")
# test_model("gemini-2.5-flash", "us-east4") # Commented out as likely same result, but can uncomment if needed

# 2. Most likely valid region (us-central1)
test_model("gemini-3.0-flash", "us-central1")
test_model("gemini-2.5-flash", "us-central1")
test_model("gemini-2.5-pro", "us-central1")
