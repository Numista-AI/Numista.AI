"""
numista_bq_loader.py
Cloud Run Job: Loads the latest Firestore export from GCS into BigQuery.
Triggered nightly by Cloud Scheduler at 3am ET, after the Firestore export completes.

Deploy as a Cloud Run Job:
  gcloud run jobs deploy numista-bq-loader \
    --source . \
    --region us-central1 \
    --project studio-9101802118-8c9a8
"""

import os
import datetime
from google.cloud import bigquery, storage

PROJECT_ID = "studio-9101802118-8c9a8"
EXPORT_BUCKET = "numista-firestore-exports"
BQ_DATASET = "numista_analytics"
EXPORT_PREFIX = "nightly"

# Firestore collections to load into BigQuery
COLLECTIONS = [
    "global_programs",
    "coin_set_index",
]

# Note: user-scoped collections (users/{uid}/coins, etc.) require
# a flatten step since the export nests them under the user doc.
# These are handled separately below.
USER_SUBCOLLECTIONS = [
    "coins",
    "wishlist",
    "checklist_entries",
]


def get_latest_export_prefix(bucket_name: str, prefix: str) -> str | None:
    """Find the most recent export folder under the given prefix."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=f"{prefix}/", delimiter="/"))
    # Get all top-level subdirs
    prefixes = [p for p in bucket.list_blobs(prefix=f"{prefix}/", delimiter="/").prefixes]
    if not prefixes:
        print(f"No export found under gs://{bucket_name}/{prefix}/")
        return None
    latest = sorted(prefixes)[-1]
    print(f"Latest export: gs://{bucket_name}/{latest}")
    return f"gs://{bucket_name}/{latest}"


def load_collection(bq_client: bigquery.Client, export_uri: str, collection: str):
    """Load a Firestore-exported collection into a BigQuery table."""
    table_id = f"{PROJECT_ID}.{BQ_DATASET}.{collection}"
    source_uri = f"{export_uri}/all_namespaces/kind_{collection}/all_namespaces_kind_{collection}.export_metadata"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.DATASTORE_BACKUP,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Full refresh nightly
    )

    print(f"Loading {collection} → {table_id}")
    try:
        load_job = bq_client.load_table_from_uri(source_uri, table_id, job_config=job_config)
        load_job.result()  # Wait for completion
        table = bq_client.get_table(table_id)
        print(f"  ✅ {collection}: {table.num_rows:,} rows loaded")
    except Exception as e:
        print(f"  ❌ {collection}: {e}")


def main():
    print(f"Numista BQ Loader — {datetime.datetime.utcnow().isoformat()}Z")
    print(f"Project: {PROJECT_ID} | Dataset: {BQ_DATASET}")

    export_uri = get_latest_export_prefix(EXPORT_BUCKET, EXPORT_PREFIX)
    if not export_uri:
        print("No export found — skipping load. Check that the Firestore export ran.")
        return

    bq_client = bigquery.Client(project=PROJECT_ID)

    # Load top-level collections
    for collection in COLLECTIONS:
        load_collection(bq_client, export_uri, collection)

    # Load user sub-collections (coins, wishlist, checklist_entries)
    for sub in USER_SUBCOLLECTIONS:
        load_collection(bq_client, export_uri, sub)

    print("\nDone. View your data at:")
    print(f"  https://console.cloud.google.com/bigquery?project={PROJECT_ID}&ws=!1m4!1m3!3m2!1s{PROJECT_ID}!2s{BQ_DATASET}")


if __name__ == "__main__":
    main()
