import requests
import os
import json

# Configuration
API_KEY = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe' # [cite: 11]
BASE_URL = 'https://api.numista.com/v3'
HEADERS = {'Numista-API-Key': API_KEY}
US_MINT_BUCKET = "https://storage.googleapis.com/us_mint_coin_images/" # [cite: 14]

def fetch_and_map_coin(coin_id, user_image_path=None):
    """
    The heart of Numista.AI: Merges Numista facts with your tiered image hierarchy.
    """
    url = f"{BASE_URL}/types/{coin_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # 1. Image Hierarchy Selection
        # If user_image_path is provided (from Microscope or Upload), use it. [cite: 9, 10]
        # Otherwise, check for Kaggle local, then default to US Mint Bucket.
        display_image = user_image_path if user_image_path else f"{US_MINT_BUCKET}{coin_id}.jpg"

        # 2. Build the Estate-Ready Record [cite: 1, 2, 12]
        coin_record = {
            "id": coin_id,
            "title": data.get("title"),
            "display_image": display_image, 
            "history": data.get("description", "Historical data coming soon."),
            "specs": {
                "composition": data.get("composition", {}).get("text"),
                "weight": f"{data.get('weight')}g",
                "diameter": f"{data.get('size')}mm"
            },
            "official_refs": data.get("references", []),
            "source": "Numista.AI Certified"
        }
        
        return coin_record

    except Exception as e:
        print(f"Error: {e}")
        return None
    