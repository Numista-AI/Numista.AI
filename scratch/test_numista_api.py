import requests
import json

API_KEY = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe'
BASE_URL = 'https://api.numista.com/v3'
HEADERS = {'Numista-API-Key': API_KEY}

def main():
    coin_id = 1429 # Try standard coin ID
    url = f"{BASE_URL}/types/{coin_id}"
    print(f"Calling: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        print("Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            # Print keys of data
            print("Keys:", list(data.keys()))
            # Print obverse/reverse keys if they exist
            print("Obverse:", {k: data.get(k) for k in data if 'obv' in k or 'front' in k})
            print("Reverse:", {k: data.get(k) for k in data if 'rev' in k or 'back' in k})
            # Save response to file
            with open('scratch/numista_api_sample.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print("Saved response to scratch/numista_api_sample.json")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
