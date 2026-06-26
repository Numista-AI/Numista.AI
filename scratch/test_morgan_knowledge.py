import json
import os
import sys

# Add numista_backend to path
sys.path.insert(0, r"c:\Users\ericd\Documents\MyVertexProject\numista_backend")

import morgan_knowledge

# Mock firestore client that returns a dummy document stream when called
class DummyDoc:
    def __init__(self, data):
        self._data = data
    def to_dict(self):
        return self._data

class DummyCollection:
    def stream(self):
        print("-> [Mock Firestore] streaming documents from collection...")
        return [
            DummyDoc({
                "series": "Lincoln Cent",
                "year": "1909",
                "denomination": "Cent",
                "composition": "95% copper",
                "design_obverse": "Lincoln portrait",
                "design_reverse": "Wheat ears",
                "design_description": "First year of Lincoln Cent design",
                "mint_marks": ["S", "VDB"],
                "mintage_notes": "Very rare variety",
                "fun_facts": ["Designed by Victor David Brenner"]
            })
        ]

class MockDB:
    def collection(self, name):
        return DummyCollection()

def safe_print(text):
    if not text:
        print(text)
        return
    try:
        print(text)
    except UnicodeEncodeError:
        # Fall back to replacing unsupported characters
        print(text.encode('ascii', errors='replace').decode('ascii'))

def run_tests():
    db = MockDB()
    
    # Inspect raw search response fields
    from google.cloud import discoveryengine_v1 as de
    ids_path = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\vertex_search\ids.json"
    with open(ids_path) as f:
        config = json.load(f)
    
    client = de.SearchServiceClient()
    request = de.SearchRequest(
        serving_config=config["serving_config"],
        query="Morgan Dollar",
        page_size=1
    )
    response = client.search(request=request)
    if response.results:
        doc = response.results[0].document
        print("--- Debug: Raw document attributes ---")
        print(f"Document ID: {doc.id}")
        print(f"struct_data type: {type(doc.struct_data)}")
        print(f"struct_data keys: {list(doc.struct_data.keys()) if doc.struct_data else 'None'}")
        if doc.struct_data:
            print("struct_data values (first 3):")
            for k in list(doc.struct_data.keys())[:3]:
                safe_print(f"  {k}: {doc.struct_data[k]}")
    
    print("\n--- Test 1: Querying Vertex AI Search (Active) ---")
    context = morgan_knowledge.get_coin_context(db, "Morgan Dollar")
    print("Result of Test 1:")
    safe_print(context)
    if context and "Vertex AI Search" in context:
        print("[OK] Test 1 Passed: Retrieved data from Vertex AI Search!")
    else:
        print("[FAIL] Test 1 Failed!")
        
    print("\n--- Test 2: Fallback behavior (Simulated search failure) ---")
    temp_ids_path = ids_path + ".bak"
    
    try:
        os.rename(ids_path, temp_ids_path)
        print("ids.json temporarily renamed to simulate offline status.")
        
        context = morgan_knowledge.get_coin_context(db, "Lincoln Cent 1909")
        print("Result of Test 2:")
        safe_print(context)
        if context and ("coins_reference" in context or "from Numista.AI knowledge base" in context):
            print("[OK] Test 2 Passed: Successfully fell back to Firestore keyword search!")
        else:
            print("[FAIL] Test 2 Failed!")
            
    finally:
        if os.path.exists(temp_ids_path):
            os.rename(temp_ids_path, ids_path)
            print("ids.json restored successfully.")

if __name__ == "__main__":
    run_tests()
