# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import os
import sqlite3
import json
import time
from google.cloud import firestore
from google import genai
from google.genai import types

# --- CONFIG ---
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "global"
USER_EMAIL = "eric@numista.ai"
MODEL_ID = "gemini-3.5-flash"

# Initialize clients
db = firestore.Client(project=PROJECT_ID)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def get_empty_coins(user_email):
    """Fetch coins for a specific user that are missing images."""
    print(f"Checking Firestore for {user_email}'s coins missing images...")
    # The collection path is users/eric@numista.ai/coins
    collection_path = f"users/{user_email}/coins"
    coins_ref = db.collection(collection_path)
    query = coins_ref.stream()
    
    empty_coins = []
    for doc in query:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        # Check if obverse or reverse is missing
        if not data.get("image_url_obverse") or not data.get("image_url_reverse"):
            empty_coins.append(data)
            
    print(f"Found {len(empty_coins)} coins needing enrichment.")
    return empty_coins

def search_wikimedia(coin_data):
    """Use Gemini to find the best Wikimedia Commons image URL for a coin."""
    year = coin_data.get("year", "Unknown")
    denom = coin_data.get("denomination", "")
    program = coin_data.get("program", "")
    mint = coin_data.get("mint", "")
    variety = coin_data.get("variety", "")
    
    search_query = f"{year} {mint} {denom} {program} {variety}".strip()
    print(f"  Searching for: {search_query}...")
    
    prompt = f"""
    Find the official Wikimedia Commons file URLs for the obverse and reverse of this US coin:
    Coin: {search_query}
    
    Instructions:
    1. Provide only direct links to upload.wikimedia.org (high res if possible).
    2. Ensure they are the correct coin type and year.
    3. Return JSON only in this format:
    {{
      "obverse_url": "...",
      "reverse_url": "...",
      "found": true
    }}
    If not found, set found to false.
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"    Error searching for {search_query}: {e}")
        return {"found": False}

def apply_fix(doc_id, obverse_url, reverse_url):
    """Update Firestore with the new URLs."""
    if not obverse_url and not reverse_url:
        return
        
    doc_ref = db.collection("coins").document(doc_id)
    update_data = {}
    if obverse_url:
        update_data["image_url_obverse"] = obverse_url
    if reverse_url:
        update_data["image_url_reverse"] = reverse_url
        
    if update_data:
        doc_ref.update(update_data)
        print(f"    Updated doc {doc_id} with new images.")

def main():
    coins = get_empty_coins(USER_EMAIL)
    
    for coin in coins:
        doc_id = coin['doc_id']
        result = search_wikimedia(coin)
        
        if result.get("found"):
            print(f"    Found matches for {doc_id}!")
            apply_fix(doc_id, result.get("obverse_url"), result.get("reverse_url"))
        else:
            print(f"    No Wikimedia match found for {doc_id}.")
        
        time.sleep(1) # Polite delay

if __name__ == "__main__":
    main()
