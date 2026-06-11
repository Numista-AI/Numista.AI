"""
numista_bq_loader.py
Cloud Run Job: Loads the latest Firestore per-collection export from GCS into BigQuery.
Triggered nightly by Cloud Scheduler at 3am ET, after the Firestore export completes.

Export structure (from REST API with collectionIds array):
  gs://numista-firestore-exports/nightly/
    nightly.overall_export_metadata
    all_namespaces/
      kind_coins/all_namespaces_kind_coins.export_metadata
      kind_wishlist/all_namespaces_kind_wishlist.export_metadata
      kind_checklist_entries/...
      kind_global_programs/...
      kind_coin_set_index/...

Deploy as a Cloud Run Job:
  gcloud run jobs deploy numista-bq-loader \
    --source numista_bq_loader_job/ \
    --region us-central1 \
    --project studio-9101802118-8c9a8
"""

import datetime
from google.cloud import bigquery, storage

PROJECT_ID = "studio-9101802118-8c9a8"
EXPORT_BUCKET = "numista-firestore-exports"
EXPORT_PREFIX = "nightly"
BQ_DATASET = "numista_analytics"

COLLECTION_IDS = [
    "coins",
    "wishlist",
    "checklist_entries",
    "global_programs",
    "coin_set_index",
]


def get_export_base_uri() -> str:
    """Return the base URI for the nightly export."""
    return f"gs://{EXPORT_BUCKET}/{EXPORT_PREFIX}"


def get_metadata_uri(base_uri: str, collection: str) -> str:
    """Build the per-kind metadata URI from the export base path.

    Firestore REST API exports with collectionIds produce:
      {base}/all_namespaces/kind_{name}/all_namespaces_kind_{name}.export_metadata
    """
    return (f"{base_uri}/all_namespaces/kind_{collection}/"
            f"all_namespaces_kind_{collection}.export_metadata")


def load_collection(bq_client: bigquery.Client, metadata_uri: str, collection: str) -> int:
    """Load one collection from its per-kind export metadata into a BigQuery table."""
    table_id = f"{PROJECT_ID}.{BQ_DATASET}.{collection}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.DATASTORE_BACKUP,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    load_job = bq_client.load_table_from_uri(metadata_uri, table_id, job_config=job_config)
    load_job.result()
    table = bq_client.get_table(table_id)
    return table.num_rows


def main():
    print(f"Numista BQ Loader — {datetime.datetime.utcnow().isoformat()}Z")
    print(f"Project: {PROJECT_ID} | Dataset: {BQ_DATASET}")

    base_uri = get_export_base_uri()
    print(f"Export base: {base_uri}")

    bq_client = bigquery.Client(project=PROJECT_ID)
    total_rows = 0
    errors = []

    for collection in COLLECTION_IDS:
        metadata_uri = get_metadata_uri(base_uri, collection)
        print(f"Loading {collection}...", flush=True)
        print(f"  Source: {metadata_uri}")
        try:
            rows = load_collection(bq_client, metadata_uri, collection)
            print(f"  ✅ {collection}: {rows:,} rows")
            total_rows += rows
        except Exception as e:
            print(f"  ❌ {collection}: {e}")
            errors.append(collection)

    status = "✅" if not errors else "⚠️"
    print(f"\n{status} Done — {total_rows:,} total rows across {len(COLLECTION_IDS)} tables.")
    if errors:
        print(f"  Failed: {', '.join(errors)}")
        raise SystemExit(1)

    print(f"  BigQuery: https://console.cloud.google.com/bigquery"
          f"?project={PROJECT_ID}&ws=!1m4!1m3!3m2!1s{PROJECT_ID}!2s{BQ_DATASET}")


if __name__ == "__main__":
    main()
