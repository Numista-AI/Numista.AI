"""
setup_search.py
Creates the Vertex AI Search data store + search app, then kicks off
the JSONL import from GCS.

Run once after prepare_search_data.py has uploaded the JSONL:
  python vertex_search/setup_search.py

Outputs DATASTORE_ID and ENGINE_ID to vertex_search/ids.json
for use by the FastAPI backend.
"""

import json
import os
import time
import sys

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.exceptions import AlreadyExists

PROJECT_ID      = "studio-9101802118-8c9a8"
PROJECT_NUMBER  = "568985927038"
LOCATION        = "global"          # Vertex AI Search uses 'global'
COLLECTION      = "default_collection"
DATA_STORE_ID   = "numista-coin-library"
ENGINE_ID       = "numista-coin-search"
BUCKET_NAME     = "numista-uploads-studio-9101802118-8c9a8"
GCS_JSONL_URI   = f"gs://{BUCKET_NAME}/vertex-search/coin_programs.jsonl"
IDS_FILE        = os.path.join(os.path.dirname(__file__), "ids.json")


def get_clients():
    ds_client  = discoveryengine.DataStoreServiceClient()
    doc_client = discoveryengine.DocumentServiceClient()
    eng_client = discoveryengine.EngineServiceClient()
    return ds_client, doc_client, eng_client


def create_data_store(ds_client) -> str:
    """Create a Generic Content data store. Returns the data store name."""
    parent = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/{COLLECTION}"
    data_store = discoveryengine.DataStore(
        display_name="Numista Coin Reference Library",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
    )
    try:
        op = ds_client.create_data_store(
            parent=parent,
            data_store=data_store,
            data_store_id=DATA_STORE_ID,
        )
        print("Creating data store (waiting for LRO)...")
        result = op.result(timeout=120)
        name = result.name
        print(f"  [OK] Data store created: {name}")
        return name
    except AlreadyExists:
        name = f"{parent}/dataStores/{DATA_STORE_ID}"
        print(f"  [INFO] Data store already exists: {name}")
        return name


def import_documents(doc_client, data_store_name: str):
    """Import JSONL from GCS into the data store."""
    gcs_source = discoveryengine.GcsSource(
        input_uris=[GCS_JSONL_URI],
        data_schema="document",
    )
    request = discoveryengine.ImportDocumentsRequest(
        parent=f"{data_store_name}/branches/default_branch",
        gcs_source=gcs_source,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    print(f"Starting import from {GCS_JSONL_URI}...")
    op = doc_client.import_documents(request=request)
    print(f"  Import LRO: {op.operation.name}")
    print("  Waiting for import (this takes 1-3 min)...")
    result = op.result(timeout=300)
    print(f"  [OK] Import complete!")
    if hasattr(result, 'error_samples') and result.error_samples:
        print(f"  [WARN] {len(result.error_samples)} error samples (first few docs may have issues)")
    return result


def create_engine(eng_client, data_store_name: str) -> str:
    """Create a Search App (engine) linked to the data store."""
    parent = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/{COLLECTION}"
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
        op = eng_client.create_engine(
            parent=parent,
            engine=engine,
            engine_id=ENGINE_ID,
        )
        print("Creating search engine (waiting for LRO)...")
        result = op.result(timeout=180)
        name = result.name
        print(f"  [OK] Engine created: {name}")
        return name
    except AlreadyExists:
        name = f"{parent}/engines/{ENGINE_ID}"
        print(f"  [INFO] Engine already exists: {name}")
        return name


def save_ids(data_store_name: str, engine_name: str):
    ids = {
        "project_id":       PROJECT_ID,
        "project_number":   PROJECT_NUMBER,
        "location":         LOCATION,
        "data_store_id":    DATA_STORE_ID,
        "engine_id":        ENGINE_ID,
        "data_store_name":  data_store_name,
        "engine_name":      engine_name,
        "serving_config":   f"{engine_name}/servingConfigs/default_config",
    }
    with open(IDS_FILE, "w") as f:
        json.dump(ids, f, indent=2)
    print(f"\n[OK] IDs saved to {IDS_FILE}")
    print(json.dumps(ids, indent=2))


def main():
    print("=== Vertex AI Search Setup ===")
    print(f"Project: {PROJECT_ID} ({PROJECT_NUMBER})")
    print(f"Data Store: {DATA_STORE_ID}")
    print(f"Engine: {ENGINE_ID}")
    print()

    ds_client, doc_client, eng_client = get_clients()

    # Step 1: Create data store
    data_store_name = create_data_store(ds_client)

    # Step 2: Import documents
    import_documents(doc_client, data_store_name)

    # Step 3: Create search engine
    engine_name = create_engine(eng_client, data_store_name)

    # Step 4: Save IDs
    save_ids(data_store_name, engine_name)

    print("\n=== Setup Complete ===")
    print("You can now use the /api/coin_search endpoint.")


if __name__ == "__main__":
    main()
