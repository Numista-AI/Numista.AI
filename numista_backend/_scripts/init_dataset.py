# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
init_dataset.py
===============
Initializes the Document AI dataset for the Coin Checklist Extractor
processor and then imports 650 training PDFs from GCS.

Needed because the processor was created via API (not via UI wizard),
so the dataset resource was never provisioned.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import documentai_v1beta3 as docai
from google.protobuf import field_mask_pb2
import google.auth
import time

PROJECT_ID      = "568985927038"
PROCESSOR_ID    = "7425afc720652ee4"
LOCATION        = "us"
GCS_PREFIX      = "gs://numista-training-docs/Numista.AI Training Data/Synthetic Filled/"
DATASET_NAME    = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}/dataset"

def get_client():
    creds, _ = google.auth.default()
    return docai.DocumentServiceClient(
        credentials=creds,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    )

def step1_check_dataset(client):
    print("Step 1: Checking current dataset state...")
    try:
        ds = client.get_dataset(request=docai.GetDatasetRequest(name=DATASET_NAME))
        print(f"  Dataset state: {ds.state}")
        print(f"  Dataset name:  {ds.name}")
        return ds.state
    except Exception as e:
        print(f"  Could not get dataset: {e}")
        return None

def step2_initialize_dataset(client):
    print("\nStep 2: Initializing dataset...")
    try:
        operation = client.update_dataset(
            request=docai.UpdateDatasetRequest(
                dataset=docai.Dataset(
                    name=DATASET_NAME,
                    state=docai.Dataset.State.INITIALIZED,
                ),
                update_mask=field_mask_pb2.FieldMask(paths=["state"]),
            )
        )
        print(f"  Waiting for initialization... (operation: {operation.operation.name})")
        result = operation.result(timeout=120)
        print(f"  Initialized! State: {result.state}")
        return True
    except Exception as e:
        print(f"  Initialization via state failed: {e}")
        return False

def step3_import_documents(client):
    print("\nStep 3: Importing 650 documents from GCS...")
    print(f"  Source: {GCS_PREFIX}")
    try:
        request = docai.ImportDocumentsRequest(
            dataset=DATASET_NAME,
            batch_documents_import_configs=[
                docai.ImportDocumentsRequest.BatchDocumentsImportConfig(
                    batch_input_config=docai.BatchDocumentsInputConfig(
                        gcs_prefix=docai.GcsPrefix(gcs_uri_prefix=GCS_PREFIX)
                    ),
                    dataset_split=docai.DatasetSplitType.DATASET_SPLIT_TRAIN,
                )
            ]
        )
        operation = client.import_documents(request=request)
        print(f"  Import operation started: {operation.operation.name}")
        print(f"  Waiting for completion (5-15 min)...")
        result = operation.result(timeout=900)
        print(f"  Import complete: {result}")
        return True
    except Exception as e:
        print(f"  Import failed: {e}")
        return False

def main():
    client = get_client()

    state = step1_check_dataset(client)

    if str(state) not in ("State.INITIALIZED", "2"):
        ok = step2_initialize_dataset(client)
        if not ok:
            print("\nDataset initialization failed.")
            print("Try: go to the Label & Build page in the UI, scroll past")
            print("the 3 cards, and look for a dataset section / import button.")
            print("Or try 'Call foundation model' first to init, then switch.")
            return
        time.sleep(5)  # Brief pause after init

    step3_import_documents(client)

if __name__ == "__main__":
    main()
