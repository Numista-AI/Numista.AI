import requests

r = requests.get(
    'https://numista-backend-568985927038.us-central1.run.app/api/mint_news',
    timeout=25
)
d = r.json()
print('STATUS:', r.status_code, '| SOURCE:', d.get('source'), '| COUNT:', len(d.get('news', [])))
print()
for i, a in enumerate(d.get('news', []), 1):
    src = a.get('source', '?')[:20]
    title = a.get('title', '')[:70]
    print(f"  {i:2}. [{src:20}] {title}")
