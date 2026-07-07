# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import sys
import os
import argparse
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
        response = client.models.generate_content(
            model=model_name,
            contents="Ping"
        )
        print(f"✅ SUCCESS: {model_name} working in {location} -> response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gemini-3.5-flash")
    parser.add_argument("--location", default="us-central1")
    args = parser.parse_args()
    
    # Test specific model/location
    test_model(args.model, args.location)
    
    # Also test 2.5-pro as a baseline for the same location
    if args.model != "gemini-2.5-pro":
        test_model("gemini-2.5-pro", args.location)
