# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
push_receipt_schema.py
======================
Pushes a redesigned schema to the Coin Receipts Data Extractor processor.

Changes from the original schema:
- Adds customer_name, customer_number, retailer_phone at invoice level
- Creates a proper 'line_item' nested entity (one per coin row)
- Moves item_number, quantity, description, condition, amount INTO line_item
- Removes Year, Mint_Mark from top level (Gemini handles those from description)
- Adds club_selection, certification to line_item
- Keeps Invoice, Date, Retailer_Website, Total_Amount at top level

Gemini (in the backend) will parse the raw 'description' field to extract:
  year, coin_type, denomination, mint_mark, variety, certification_detail
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import documentai_v1beta3 as docai
from google.protobuf import field_mask_pb2
import google.auth

PROJECT_ID        = "568985927038"
RECEIPT_PROC_ID   = "c113e9bb62be1554"   # Coin Receipts Data Extractor — DO NOT CHANGE
LOCATION          = "us"
SCHEMA_NAME = (f"projects/{PROJECT_ID}/locations/{LOCATION}"
               f"/processors/{RECEIPT_PROC_ID}/dataset/datasetSchema")

def get_client():
    creds, _ = google.auth.default()
    return docai.DocumentServiceClient(
        credentials=creds,
        client_options={"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    )

def main():
    client = get_client()
    OT = docai.DocumentSchema.EntityType.Property.OccurrenceType

    # ── Root Document Type ────────────────────────────────────────────────────
    # All invoice-level (header) fields + one repeated line_item per coin row.
    root_type = docai.DocumentSchema.EntityType(
        name="custom_extraction_document_type",
        base_types=["document"],
        properties=[
            # ── Invoice Header Fields ──
            docai.DocumentSchema.EntityType.Property(
                name="invoice_number",
                occurrence_type=OT.REQUIRED_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="date",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="datetime",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="customer_name",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="customer_number",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="retailer_phone",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="retailer_website",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="total_amount",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="money",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="rewards_points_earned",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            # ── Per-coin rows ──
            docai.DocumentSchema.EntityType.Property(
                name="line_item",
                occurrence_type=OT.OPTIONAL_MULTIPLE,
                value_type="line_item",   # references the entity type below
            ),
        ],
    )

    # ── Line Item Entity Type ─────────────────────────────────────────────────
    # One instance per coin row in the invoice table.
    # NOTE: 'description' is the RAW multi-line text — Gemini parses it later
    #       to extract year, coin_type, denomination, mint_mark, variety, etc.
    line_item_type = docai.DocumentSchema.EntityType(
        name="line_item",
        base_types=["object"],
        properties=[
            docai.DocumentSchema.EntityType.Property(
                name="item_number",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="quantity",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="number",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="club_selection",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="description",
                occurrence_type=OT.REQUIRED_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="condition",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="certification",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="string",
            ),
            docai.DocumentSchema.EntityType.Property(
                name="amount",
                occurrence_type=OT.OPTIONAL_ONCE,
                value_type="money",
            ),
        ],
    )

    document_schema = docai.DocumentSchema(
        display_name="Coin Invoice Schema v2",
        description=(
            "Extracts structured data from coin purchase invoices. "
            "invoice_number is the primary key. line_item captures each coin row. "
            "Description text is passed to Gemini for semantic parsing (year, type, mint mark, etc.)"
        ),
        entity_types=[root_type, line_item_type],
    )

    # ── Push Schema ───────────────────────────────────────────────────────────
    print(f"Pushing new schema to: {SCHEMA_NAME}")
    print("(Coin Receipts Data Extractor — c113e9bb62be1554)")
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
        print("\nSchema push SUCCESS!")
        print("\nEntity types:")
        for et in result.document_schema.entity_types:
            print(f"  {et.name}")
            for p in et.properties:
                print(f"    -> {p.name} ({p.value_type})  occurrence={p.occurrence_type.name}")
        print("\nDone! The receipt processor schema has been updated.")
        print("NOTE: Existing labeled training data in the dataset is preserved.")
        print("      Re-label any documents that used the old Year/Mint_Mark fields.")
    except Exception as e:
        print(f"\nFailed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
