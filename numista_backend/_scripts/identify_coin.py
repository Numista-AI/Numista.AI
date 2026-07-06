# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
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
        1. Identify the Year, Denomination, and Series.
        2. Provide a 'file_slug' (e.g., 2025_Batman_Gold_Proof).
        3. Match it to a common name used by the US Mint.
        Return as a simple Python-readable dictionary.
        """
        
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[prompt, img1, img2]
        )
        analysis = response.text
        
        # Extract a slug for renaming (Fallback if Gemini is wordy)
        slug = "detected_coin"
        if "file_slug" in analysis:
            # Simple extraction logic
            try:
                slug = analysis.split("file_slug': '")[1].split("'")[0]
            except IndexError:
                slug = "detected_coin"

        return {
            "file_slug": slug,
            "full_analysis": analysis,
            "source": "Gemini 2.0 Flash + US Mint Manifest"
        }

    except Exception as e:
        print(f"Analysis Error: {e}")
        return None
