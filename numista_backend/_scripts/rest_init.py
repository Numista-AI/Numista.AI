# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
rest_init.py
============
Last attempt: use raw REST API instead of gRPC client.
Sometimes the REST endpoint handles initialization differently
than the Python gRPC client.
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import requests
import google.auth
import google.auth.transport.requests

PROJECT_ID   = "568985927038"
PROCESSOR_ID = "7425afc720652ee4"
LOCATION     = "us"
BASE          = f"https://{LOCATION}-documentai.googleapis.com/v1beta3"
DATASET_URL   = f"{BASE}/projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}/dataset"
GCS_PREFIX    = "gs://numista-training-docs/Numista.AI Training Data/Synthetic Filled/"

def get_token():
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token

def main():
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Step 1: GET current dataset state
    print("GET dataset state...")
    r = requests.get(DATASET_URL, headers=headers)
    print(f"  Status: {r.status_code}")
    print(f"  Body:   {json.dumps(r.json(), indent=2)}")

    # Step 2: PATCH to set state = INITIALIZED
    print("\nPATCH dataset state -> INITIALIZED...")
    r = requests.patch(
        DATASET_URL,
        headers=headers,
        params={"updateMask": "state"},
        json={"state": "INITIALIZED"}
    )
    print(f"  Status: {r.status_code}")
    print(f"  Body:   {json.dumps(r.json(), indent=2)}")

    if r.status_code not in (200, 202):
        print("\nPATCH failed. Will try import anyway in case state is wrong...")

    # Step 3: POST importDocuments
    print("\nPOST importDocuments...")
    import_url = f"{DATASET_URL}:importDocuments"
    import_body = {
        "batchDocumentsImportConfigs": [
            {
                "batchInputConfig": {
                    "gcsPrefix": {"gcsUriPrefix": GCS_PREFIX}
                },
                "datasetSplit": "DATASET_SPLIT_TRAIN",
            }
        ]
    }
    r = requests.post(import_url, headers=headers, json=import_body)
    print(f"  Status: {r.status_code}")
    print(f"  Body:   {json.dumps(r.json(), indent=2)}")

if __name__ == "__main__":
    main()
