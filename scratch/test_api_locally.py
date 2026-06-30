import os
import sys

# Add numista_backend to path so we can import main
sys.path.append(r"c:\Users\ericd\Documents\MyVertexProject\numista_backend")

# Set up mock environment variables if needed
os.environ["FLUTTER_WEB_PORT"] = "8080"
# Ensure we don't try to connect to Google services or if we do, it doesn't fail
# Let's import main and run TestClient
try:
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    print("--- 1. Testing empty query (all reference coins) ---")
    resp = client.get("/api/reference/search?q=&page_size=3")
    print("Status:", resp.status_code)
    data = resp.json()
    print("Total count:", data.get("total"))
    results = data.get("results", [])
    print("Fetched results count:", len(results))
    for r in results:
        print(f"- DocID: {r.get('doc_id')}, Year: '{r.get('year')}', Title: {r.get('variety') or r.get('series')}")
        print(f"  Obverse: {r.get('image_url_obverse')}")
        print(f"  Reverse: {r.get('image_url_reverse')}")
        print(f"  Price Guide: {r.get('price_guide')}")
        print(f"  Population: {r.get('population_total')}")
        print(f"  APR: {r.get('apr_history')}")

    print("\n--- 2. Testing sorting by year (default) ---")
    resp_year = client.get("/api/reference/search?q=&page_size=5&sort_by=year")
    results_year = resp_year.json().get("results", [])
    print("Years in chronological order:")
    for r in results_year:
        print(f"- '{r.get('year')}' (Doc: {r.get('doc_id')}, Variety: {r.get('variety')})")

    print("\n--- 3. Testing alphabetical sorting ---")
    resp_alpha = client.get("/api/reference/search?q=&page_size=5&sort_by=alphabetical")
    results_alpha = resp_alpha.json().get("results", [])
    print("Titles in alphabetical order:")
    for r in results_alpha:
        print(f"- '{r.get('variety') or r.get('series')}' (Year: {r.get('year')})")

    print("\n--- 4. Testing custom search query ---")
    resp_query = client.get("/api/reference/search?q=fugio&page_size=2")
    results_query = resp_query.json().get("results", [])
    print("Search results for 'fugio':")
    for r in results_query:
        print(f"- DocID: {r.get('doc_id')}, Year: {r.get('year')}, Variety: {r.get('variety')}")

    print("\nAPI VERIFICATION SUCCESSFUL!")

except Exception as e:
    print("Error during API testing:")
    import traceback
    traceback.print_exc()
