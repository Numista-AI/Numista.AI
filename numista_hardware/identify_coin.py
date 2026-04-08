import os
import pandas as pd
from google import genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Safely loads your API key from the .env file. Never hardcode keys in code!
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY is not set. Check your .env file.")

client = genai.Client(api_key=api_key)

MANIFEST_PATH = 'numista_database_ready (1).csv'

def run_numista_report(obv_path, rev_path):
    """
    1. Sends both sides to Gemini.
    2. Identifies the coin and generates a file-safe name.
    3. Matches the identification to the US Mint CSV.
    """
    print(f"Numista.AI: Analyzing {obv_path} and {rev_path}...")
    
    try:
        # Load your US Mint data
        df = pd.read_csv(MANIFEST_PATH)
        
        # Upload images to Gemini
        img1 = client.files.upload(file=obv_path)
        img2 = client.files.upload(file=rev_path)
        
        # The prompt is key for the renaming logic
        prompt = """
        Analyze these two coin images (Obverse and Reverse). 
        Identify the Year, Country, Denomination, and Series.
        Estimated Grade (e.g., MS65, AU58).
        Provide a 'file_slug' (e.g., 2025_Batman_Gold_Proof).
        Provide a brief 'report' summarizing the coin's features.
        
        Return ONLY a JSON object with these keys: 
        {"year": int, "country": string, "grade": string, "file_slug": string, "report": string}
        """
        
        from google.genai import types
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, img1, img2],
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        import json
        try:
            res_data = json.loads(response.text)
        except:
            res_data = {"file_slug": "detected_coin", "report": response.text}

        return {
            "year": res_data.get("year"),
            "country": res_data.get("country", "Unknown"),
            "grade": res_data.get("grade", "N/A"),
            "file_slug": res_data.get("file_slug", "detected_coin"),
            "report": res_data.get("report", "No detailed analysis provided."),
            "source": "Gemini 3 Flash Preview"
        }

    except Exception as e:
        print(f"Analysis Error: {e}")
        return None
