"""
import_dataset.py
=================
Imports 650 synthetic training PDFs from GCS into the
'Coin Checklist Extractor' Document AI processor dataset.

Run AFTER the schema has been configured in the UI.
Run BEFORE attempting Fine Tuning or Train a custom model.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import documentai_v1beta3 as docai
import google.auth

PROJECT_ID      = "568985927038"
PROCESSOR_ID    = "261d6897c84ca28b"   # Coin Checklist Extractor
LOCATION        = "us"
GCS_PREFIX      = "gs://numista-training-docs/Numista.AI Training Data/Synthetic Filled/"
DATASET_NAME    = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}/dataset"

def main():
    creds, _ = google.auth.default()
    client = docai.DocumentServiceClient(
        credentials=creds,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    )

    print(f"Importing documents from:")
    print(f"  {GCS_PREFIX}")
    print(f"Into dataset:")
    print(f"  {DATASET_NAME}")
    print()

    # Import all PDFs from our Synthetic Filled folder into the TRAIN split
    request = docai.ImportDocumentsRequest(
        dataset=DATASET_NAME,
        batch_documents_import_configs=[
            docai.ImportDocumentsRequest.BatchDocumentsImportConfig(
                batch_input_config=docai.BatchDocumentsInputConfig(
                    gcs_prefix=docai.GcsPrefix(
                        gcs_uri_prefix=GCS_PREFIX,
                    )
                ),
                dataset_split=docai.DatasetSplitType.DATASET_SPLIT_TRAIN,
            )
        ]
    )

    print("Starting import operation (runs in background)...")
    operation = client.import_documents(request=request)
    print(f"Operation name: {operation.operation.name}")
    print()
    print("Waiting for import to complete (this may take 5-15 minutes)...")
    result = operation.result(timeout=900)   # wait up to 15 min
    print(f"Import complete!")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
