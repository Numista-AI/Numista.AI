import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Listing available models from Gemini API...")
try:
    for model in client.models.list():
        print(f"Model Name: {model.name}")
        print(f"Supported Methods: {model.supported_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error listing models: {e}")
