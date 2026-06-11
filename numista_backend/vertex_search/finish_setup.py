"""
finish_setup.py
Polls the already-started import LRO, then creates the search engine.
Run this INSTEAD of re-running setup_search.py (data store already exists).

  python vertex_search/finish_setup.py
"""
import json
import os
import sys
import time

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.exceptions import AlreadyExists
from google.api_core import operations_v1
import google.auth
import google.auth.transport.requests

PROJECT_NUMBER  = "568985927038"
LOCATION        = "global"
COLLECTION      = "default_collection"
DATA_STORE_ID   = "numista-coin-library"
ENGINE_ID       = "numista-coin-search"
PROJECT_ID      = "studio-9101802118-8c9a8"

# The LRO name printed by setup_search.py
IMPORT_OP_NAME  = (
    "projects/568985927038/locations/global"
    "/collections/default_collection"
    "/dataStores/numista-coin-library"
    "/branches/0/operations/import-documents-16450687471318810394"
)

DATA_STORE_NAME = (
    f"projects/{PROJECT_NUMBER}/locations/{LOCATION}"
    f"/collections/{COLLECTION}/dataStores/{DATA_STORE_ID}"
)

IDS_FILE = os.path.join(os.path.dirname(__file__), "ids.json")


def poll_import_lro():
    """Poll the import LRO until done. Returns True if successful."""
    print(f"Polling import LRO: {IMPORT_OP_NAME}")
    doc_client = discoveryengine.DocumentServiceClient()

    # Use the low-level operations client to poll by name
    transport = doc_client._transport
    ops_client = transport.operations_client

    attempt = 0
    while True:
        attempt += 1
        try:
            op = ops_client.get_operation(name=IMPORT_OP_NAME)
            if op.done:
                if op.HasField("error"):
                    print(f"  ❌ Import failed: {op.error}")
                    return False
                print(f"  ✅ Import complete! (polled {attempt} times)")
                return True
            else:
                pct = ""
                if op.metadata:
                    try:
                        meta = discoveryengine.ImportDocumentsMetadata()
                        op.metadata.Unpack(meta)
                        total = meta.total_count or "?"
                        success = meta.success_count or 0
                        pct = f" — {success}/{total} docs"
                    except Exception:
                        pass
                print(f"  ⏳ [{attempt}] Still importing{pct}… waiting 20s")
                time.sleep(20)
        except Exception as e:
            print(f"  ⚠️  Poll error: {e}")
            if attempt > 30:   # ~10 minutes max
                print("  ❌ Giving up after 30 attempts")
                return False
            time.sleep(20)


def create_engine():
    """Create the search engine (Enterprise + LLM add-on)."""
    eng_client = discoveryengine.EngineServiceClient()
    parent = (
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}"
        f"/collections/{COLLECTION}"
    )
    engine = discoveryengine.Engine(
        display_name="Numista Coin Search",
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        data_store_ids=[DATA_STORE_ID],
        search_engine_config=discoveryengine.Engine.SearchEngineConfig(
            search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
            search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
        ),
    )
    try:
        print("Creating search engine…")
        op = eng_client.create_engine(
            parent=parent,
            engine=engine,
            engine_id=ENGINE_ID,
        )
        result = op.result(timeout=300)
        name = result.name
        print(f"  ✅ Engine created: {name}")
        return name
    except AlreadyExists:
        name = f"{parent}/engines/{ENGINE_ID}"
        print(f"  ℹ️  Engine already exists: {name}")
        return name


def save_ids(engine_name: str):
    engine_name_full = (
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}"
        f"/collections/{COLLECTION}/engines/{ENGINE_ID}"
    )
    ids = {
        "project_id":     PROJECT_ID,
        "project_number": PROJECT_NUMBER,
        "location":       LOCATION,
        "data_store_id":  DATA_STORE_ID,
        "engine_id":      ENGINE_ID,
        "data_store_name": DATA_STORE_NAME,
        "engine_name":    engine_name_full,
        "serving_config": f"{engine_name_full}/servingConfigs/default_config",
    }
    with open(IDS_FILE, "w") as f:
        json.dump(ids, f, indent=2)
    print(f"\n✅ IDs saved to {IDS_FILE}")
    print(json.dumps(ids, indent=2))


def main():
    print("=== Vertex AI Search — Finish Setup ===")
    print(f"Data store already created: {DATA_STORE_ID}")
    print(f"Resuming from import LRO...\n")

    # Step 1: Wait for import to finish
    ok = poll_import_lro()
    if not ok:
        print("\n⚠️  Import may have partially failed. Proceeding to engine creation anyway.")

    # Step 2: Create engine
    engine_name = create_engine()

    # Step 3: Save IDs
    save_ids(engine_name)

    print("\n=== Setup Complete ===")
    print("The /api/coin_search endpoint is now live.")
    print(f"\nServing config:")
    print(f"  projects/{PROJECT_NUMBER}/locations/global/collections/default_collection")
    print(f"  /engines/{ENGINE_ID}/servingConfigs/default_config")


if __name__ == "__main__":
    main()
