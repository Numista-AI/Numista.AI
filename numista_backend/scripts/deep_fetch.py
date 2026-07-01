
import requests
import json
import time

NUMISTA_API_KEY = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe'
headers = {
    'Numista-API-Key': NUMISTA_API_KEY,
    'Accept': 'application/json'
}

ISSUERS = [
    'etats-unis',
    'united-states-pre-federal',
    'us_military_bases',
    'usa_pacific_territories',
    'confederate-states'
]

def fetch_all(category):
    results = []
    for issuer in ISSUERS:
        page = 1
        while True:
            url = f'https://api.numista.com/v3/types?issuer={issuer}&category={category}&page={page}'
            print(f"Fetching {category} for {issuer} Page {page}...")
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200: break
                data = resp.json()
                types = data.get('types', [])
                if not types: break
                results.extend(types)
                page += 1
                time.sleep(0.1)
                if page > 50: break
            except:
                break
    return results

if __name__ == "__main__":
    bn = fetch_all('banknote')
    with open('scratch/all_us_banknotes_deep.json', 'w', encoding='utf-8') as f:
        json.dump(bn, f, indent=2)
    print(f"Total Banknotes: {len(bn)}")
    
    ex = fetch_all('exonumia')
    with open('scratch/all_us_medals_deep.json', 'w', encoding='utf-8') as f:
        json.dump(ex, f, indent=2)
    print(f"Total Exonumia: {len(ex)}")
