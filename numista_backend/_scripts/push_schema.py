# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
push_schema.py (v4)
===================
Schema v4 — clean, unambiguous design.

Each coin_entry represents exactly ONE checklist row:
  coin_subject = full printed identifier, e.g. "1948-D", "1950 Proof",
                 "1913-S Variety 1", "1864, No L", "1886 Variety II"
  is_owned     = True if the collector's circle is filled, False if empty

This replaces the ambiguous v1-v3 has_p/has_d/has_s/has_s_slv/has_proof
multi-field design, which allowed nonsensical combinations (e.g. has_p=True
on a 1948-D entry) and created unnecessary labeling complexity.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import documentai_v1beta3 as docai
from google.protobuf import field_mask_pb2
import google.auth

PROJECT_ID   = "568985927038"
PROCESSOR_ID = "261d6897c84ca28b"
LOCATION     = "us"
SCHEMA_NAME  = (f"projects/{PROJECT_ID}/locations/{LOCATION}"
                f"/processors/{PROCESSOR_ID}/dataset/datasetSchema")
DATASET_NAME = (f"projects/{PROJECT_ID}/locations/{LOCATION}"
                f"/processors/{PROCESSOR_ID}/dataset")

def get_client():
    creds, _ = google.auth.default()
    return docai.DocumentServiceClient(
        credentials=creds,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    )

def main():
    client = get_client()
    OT = docai.DocumentSchema.EntityType.Property.OccurrenceType

    # Root document type — references coin_entry
    root_type = docai.DocumentSchema.EntityType(
        name="custom_extraction_document_type",
        base_types=["document"],
        properties=[
            docai.DocumentSchema.EntityType.Property(
                name="coin_entry",
                occurrence_type=OT.REQUIRED_MULTIPLE,
                value_type="coin_entry",
            ),
        ],
    )

    # coin_entry — one instance per checklist row
    # coin_subject: full identifier as printed ("1948-D", "1950 Proof", "1913-S Variety 1")
    # is_owned:     True = circle filled (owns it), False = circle empty (doesn't own it)
    coin_entry_type = docai.DocumentSchema.EntityType(
        name="coin_entry",
        base_types=["object"],
        properties=[
            docai.DocumentSchema.EntityType.Property(
                name="coin_subject",
                occurrence_type=OT.REQUIRED_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="is_owned",
                occurrence_type=OT.REQUIRED_ONCE,
                value_type="boolean",
            ),
        ],
    )

    document_schema = docai.DocumentSchema(
        display_name="Coin Checklist Schema v4",
        description=(
            "Littleton Coin Company checklist extractor. "
            "One coin_entry per checklist row. "
            "coin_subject = full printed identifier (e.g. '1948-D', '1950 Proof', "
            "'1913-S Variety 1'). "
            "is_owned = true if the collector's circle is filled, false if empty."
        ),
        entity_types=[root_type, coin_entry_type],
    )

    # ── Push Schema ───────────────────────────────────────────────────────────
    print("Pushing schema v4...")
    try:
        result = client.update_dataset_schema(
            request=docai.UpdateDatasetSchemaRequest(
                dataset_schema=docai.DatasetSchema(
                    name=SCHEMA_NAME,
                    document_schema=document_schema,
                ),
                update_mask=field_mask_pb2.FieldMask(paths=["document_schema"]),
            )
        )
        print("  Schema push SUCCESS!")
        for et in result.document_schema.entity_types:
            print(f"    Entity type: {et.name}  (props: {[p.name for p in et.properties]})")
    except Exception as e:
        print(f"  Schema push FAILED: {type(e).__name__}: {e}")
        return

    # ── Initialize Dataset ────────────────────────────────────────────────────
    print("\nInitializing dataset...")
    try:
        op = client.update_dataset(
            request=docai.UpdateDatasetRequest(
                dataset=docai.Dataset(
                    name=DATASET_NAME,
                    state=docai.Dataset.State.INITIALIZED,
                ),
                update_mask=field_mask_pb2.FieldMask(paths=["state"]),
            )
        )
        res = op.result(timeout=120)
        print(f"  Dataset state: {res.state}")
    except Exception as e:
        print(f"  Dataset init: {type(e).__name__}: {e}")

    print("\nDone. In the Document AI UI:")
    print("  1. Click 'Clear suggestions' to remove old v3 labels")
    print("  2. Open each document — the new schema shows coin_subject + is_owned only")
    print("  3. Label 10 documents and trigger Fine Tune")

if __name__ == "__main__":
    main()
