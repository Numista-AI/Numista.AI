import urllib.request
import json
import subprocess

# Get auth token
token = subprocess.check_output('gcloud auth print-access-token', shell=True).decode('utf-8').strip()

# Fetch list of objects
url = "https://storage.googleapis.com/storage/v1/b/numista-training-docs/o?prefix=Numista.AI%20Training%20Data/US%20Mint%20Coin%20Programs/"
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {token}')

response = urllib.request.urlopen(req)
data = json.loads(response.read())

with open('gcs_files.txt', 'w', encoding='utf-8') as f:
    for item in data.get('items', []):
        f.write(item['name'] + '\n')
