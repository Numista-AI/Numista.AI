import json
import os
import sys

# Add numista_backend to path
sys.path.insert(0, r"c:\Users\ericd\Documents\MyVertexProject\numista_backend")

try:
    from google.cloud import discoveryengine_v1 as de
    import google.auth
    
    # Load configuration
    ids_path = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\vertex_search\ids.json"
    with open(ids_path) as f:
        config = json.load(f)
    
    print("Attempting to connect using credentials...")
    credentials, project = google.auth.default()
    print(f"Authenticated with project: {project}")
    
    client = de.SearchServiceClient(credentials=credentials)
    serving_config = config["serving_config"]
    print(f"Querying serving config: {serving_config}")
    
    request = de.SearchRequest(
        serving_config=serving_config,
        query="Morgan dollar",
        page_size=3
    )
    
    response = client.search(request=request)
    print("=== Connection Success! ===")
    print(f"Found {len(response.results)} results.")
    for hit in response.results:
        doc = hit.document
        print(f" - Document ID: {doc.id}")
except Exception as e:
    print("=== Connection Failed / Error ===")
    print(e)
