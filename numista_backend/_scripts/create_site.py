import os, requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SA_KEY = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
PROJECT_ID = 'studio-9101802118-8c9a8'
SITE_ID = 'numista-vault'
SCOPES = ['https://www.googleapis.com/auth/cloud-platform',
          'https://www.googleapis.com/auth/firebase']

print('Authenticating...')
creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
creds.refresh(Request())
headers = {'Authorization': f'Bearer {creds.token}', 'Content-Type': 'application/json'}

BASE = 'https://firebasehosting.googleapis.com/v1beta1'
url = f'{BASE}/projects/{PROJECT_ID}/sites?siteId={SITE_ID}'
print(f"Creating site '{SITE_ID}' for project '{PROJECT_ID}'...")
r = requests.post(url, headers=headers, json={})
print("Status:", r.status_code)
print("Response:")
print(r.text)
