import os, requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SA_KEY = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
PROJECT_ID = 'studio-9101802118-8c9a8'
SCOPES = ['https://www.googleapis.com/auth/cloud-platform',
          'https://www.googleapis.com/auth/firebase']

print('Authenticating...')
creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
creds.refresh(Request())
headers = {'Authorization': f'Bearer {creds.token}', 'Content-Type': 'application/json'}

BASE = 'https://firebasehosting.googleapis.com/v1beta1'
url = f'{BASE}/projects/{PROJECT_ID}/sites'
print(f"Listing sites for project: {PROJECT_ID}")
r = requests.get(url, headers=headers)
print("Status:", r.status_code)
if r.status_code == 200:
    sites = r.json().get('sites', [])
    for site in sites:
        print(f"- Site ID: {site.get('name', '').split('/')[-1]}")
        print(f"  Default URL: {site.get('defaultUrl')}")
        print(f"  Type: {site.get('type')}")
else:
    print(r.text)
