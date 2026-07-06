# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
try_import.py
=============
Now that schema is valid, retry import directly.
Sometimes the 500 on update_dataset is a transient issue;
the import itself may succeed even if state update failed.
Also tries a single-doc import first to force initialization.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import documentai_v1beta3 as docai
import google.auth, time

PROJECT_ID   = "568985927038"
PROCESSOR_ID = "7425afc720652ee4"
LOCATION     = "us"
DATASET_NAME = (f"projects/{PROJECT_ID}/locations/{LOCATION}"
                f"/processors/{PROCESSOR_ID}/dataset")
GCS_PREFIX   = "gs://numista-training-docs/Numista.AI Training Data/Synthetic Filled/"
# Single doc to warm-start the dataset
SINGLE_DOC   = ("gs://numista-training-docs/Numista.AI Training Data/Synthetic Filled/"
                "LC-KGW-50-State-Commemorative-Quarter-Checklist/variant_00_empty.pdf")

def get_client():
    creds, _ = google.auth.default()
    return docai.DocumentServiceClient(
        credentials=creds,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    )

def try_import(client, gcs_uri_prefix, label="bulk import"):
    print(f"\nAttempting {label}...")
    print(f"  Source: {gcs_uri_prefix}")
    try:
        op = client.import_documents(
            request=docai.ImportDocumentsRequest(
                dataset=DATASET_NAME,
                batch_documents_import_configs=[
                    docai.ImportDocumentsRequest.BatchDocumentsImportConfig(
                        batch_input_config=docai.BatchDocumentsInputConfig(
                            gcs_prefix=docai.GcsPrefix(gcs_uri_prefix=gcs_uri_prefix)
                        ),
                        dataset_split=docai.DatasetSplitType.DATASET_SPLIT_TRAIN,
                    )
                ]
            )
        )
        print(f"  Operation started: {op.operation.name}")
        if "bulk" in label:
            print("  This runs in background. Check the UI in 5-15 minutes.")
            # Don't wait — let it run async
            print(f"  Operation name saved for tracking: {op.operation.name}")
        else:
            print("  Waiting for single-doc import...")
            res = op.result(timeout=120)
            print(f"  Single doc import complete: {res}")
        return True, op.operation.name
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
        return False, str(e)

def main():
    client = get_client()

    # Warm-start with single doc first
    ok, op_name = try_import(client, SINGLE_DOC.rsplit("/", 1)[0] + "/",
                             label="single-doc warm-start")
    if not ok:
        print("\nSingle doc import failed. Waiting 5s and trying bulk...")
        time.sleep(5)

    # Full bulk import
    ok2, op_name2 = try_import(client, GCS_PREFIX, label="bulk import (650 docs)")
    if ok2:
        print(f"\nBulk import operation is running: {op_name2}")
        print("Go to the UI Label & Build page — you should see docs appearing")
        print("in the dataset within 5-15 minutes.")
    else:
        print("\nBoth imports failed. The issue is persistent 'Dataset not initialized'.")
        print("Recommended fix: In the UI, go to Label & Build and upload ONE doc")
        print("manually using the 'Upload single document' link (if visible).")
        print("Or contact Google Support — this may be a Document AI v2 provisioning bug.")

if __name__ == "__main__":
    main()
