import os
import json
import logging
from google.cloud import discoveryengine_v1 as discoveryengine
import google.auth

# --- CONFIGURATION ---
PROJECT_NUMBER = "568985927038"
LOCATION = "global"
COLLECTION = "default_collection"
DATA_STORE_ID = "numista-coin-library"
BUCKET_NAME = "studio-9101802118-8c9a8-uploads"
CANON_GCS_URI = f"gs://{BUCKET_NAME}/canon_library/*.md"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RefreshVertexDataStore")


def refresh_vertex_data_store(gcs_uri: str = CANON_GCS_URI) -> dict:
    """
    Triggers an incremental document import job on the Vertex AI Search Data Store
    (`numista-coin-library`) to re-index all Canon documents sitting in Cloud Storage.
    """
    logger.info(f"🔄 Triggering Vertex AI Data Store re-index for: {gcs_uri}")

    parent = (
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}"
        f"/collections/{COLLECTION}/dataStores/{DATA_STORE_ID}"
        f"/branches/0"
    )

    try:
        doc_client = discoveryengine.DocumentServiceClient()
        gcs_source = discoveryengine.GcsSource(
            input_uris=[gcs_uri],
            data_schema="content"  # Suitable for unstructured markdown/content documents
        )

        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            gcs_source=gcs_source,
            auto_generate_ids=True,
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
        )

        operation = doc_client.import_documents(request=request)
        op_name = getattr(operation, "operation", None)
        op_str = getattr(op_name, "name", str(operation))

        logger.info(f"✅ Vertex AI Import LRO started: {op_str}")

        return {
            "status": "triggered",
            "operation_name": op_str,
            "data_store_id": DATA_STORE_ID,
            "gcs_uri": gcs_uri
        }

    except Exception as e:
        logger.error(f"❌ Failed to trigger Vertex AI Data Store import: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    result = refresh_vertex_data_store()
    print(json.dumps(result, indent=2))
