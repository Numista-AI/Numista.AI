# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import requests, google.auth, google.auth.transport.requests

creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
req = google.auth.transport.requests.Request()
creds.refresh(req)
token = creds.token

op_name = 'projects/568985927038/locations/us/operations/3311179667860068173'
url = f'https://us-documentai.googleapis.com/v1beta3/{op_name}'
r = requests.get(url, headers={'Authorization': f'Bearer {token}'})
data = r.json()
print(f'HTTP Status: {r.status_code}')
print(f'Done:        {data.get("done", False)}')
if 'error' in data:
    print(f'Error: {data["error"]}')
elif data.get('done'):
    print('Import COMPLETED successfully!')
else:
    print('Still running on Google servers...')
