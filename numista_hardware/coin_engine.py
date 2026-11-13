import os
import pandas as pd
from google import genai
from google.genai import types as genai_types
import kagglehub

# --- CONFIGURATION ---
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
GEMINI_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-4-hydrogen")
genai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# File Paths (Matching your current folder structure)
MANIFEST_PATH = 'numista_database_ready (1).csv'
CAPTURES_DIR = 'captures/'
REFERENCES_DIR = 'references/kaggle/'

# --- 1. DATA LOADER ---
def get_us_mint_data():
    """Loads the US Mint image manifest you uploaded."""
    if os.path.exists(MANIFEST_PATH):
        return pd.read_csv(MANIFEST_PATH)
    print(f"Error: {MANIFEST_PATH} not found!")
    return None

# --- 2. KAGGLE SYNC ---
def sync_kaggle_training_set():
    """Downloads real-world coin images for AI reference."""
    print("Fetching Kaggle datasets...")
    # Creating the folder if it doesn't exist
    os.makedirs(REFERENCES_DIR, exist_ok=True)
    # Download the set (e.g., US Coins dataset)
    path = kagglehub.dataset_download("guibf/us-coins-dataset")
    print(f"Kaggle images ready at: {path}")
    return path

# --- 3. THE "BRAIN" (Gemini 3 + Manifest) ---
def identify_coin_and_link_official(image_filename):
    """
    Takes a photo from your 'captures' folder, identifies it via Gemini 3,
    and returns the US Mint official image link.
    """
    manifest = get_us_mint_data()
    image_path = os.path.join(CAPTURES_DIR, image_filename)

    if not os.path.exists(image_path):
        return "Image not found."

    # Send to Gemini 4
    print(f"Gemini 4 is analyzing {image_filename}...")
    if genai_client is None:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY not set")
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    prompt = "Identify this US coin. Provide only the common name (e.g., 'American Eagle Gold Proof')."
    response = genai_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, genai_types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")],
    )
    detected_name = response.text.strip()

    # Match with your CSV
    # We look for the detected name within the 'original' filename column
    match = manifest[manifest['original'].str.contains(detected_name, case=False, na=False)]
    
    if not match.empty:
        official_url = match.iloc[0]['image_url']
        return {
            "Identification": detected_name,
            "Official_Reference_URL": official_url,
            "Attribution": "United States Mint image"
        }
    
    return {"Identification": detected_name, "Official_Reference_URL": "No manifest match."}

# --- TEST EXECUTION ---
# Uncomment the lines below to run a test if you have an image in 'captures/'
# if __name__ == "__main__":
#     # sync_kaggle_training_set()
#     # result = identify_coin_and_link_official('test_coin.jpg')
#     # print(result)