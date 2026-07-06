# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import requests, time

base = "https://numista-backend-568985927038.us-central1.run.app"

# Step 1: Wake the service with the root ping
print("Pinging root to wake Cloud Run...")
try:
    r = requests.get(f"{base}/", timeout=45)
    print("Root status:", r.status_code, r.json())
except Exception as e:
    print("Root error:", e)

# Step 2: Hit mint_news
print("\nHitting mint_news...")
try:
    r2 = requests.get(f"{base}/api/mint_news", timeout=45)
    d = r2.json()
    print("Source:", d.get("source"))
    print("Article count:", len(d.get("news", [])))
    for a in d.get("news", [])[:5]:
        print(f"  [{a.get('published','')}] {a['title'][:70]}")
except Exception as e:
    print("mint_news error:", e)
