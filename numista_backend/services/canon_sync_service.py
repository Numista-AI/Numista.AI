import os
import json
import logging
from datetime import datetime
from pathlib import Path
from google.cloud import storage, firestore
import google.auth

# --- CONFIGURATION ---
PROJECT_ID = "studio-9101802118-8c9a8"
BUCKET_NAME = "studio-9101802118-8c9a8-uploads"
CANON_PREFIX = "canon_library"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CanonSyncService")


def get_gcp_clients():
    """Initializes Google Cloud clients with default credentials."""
    credentials, _ = google.auth.default()
    db = firestore.Client(credentials=credentials, project=PROJECT_ID)
    storage_client = storage.Client(credentials=credentials, project=PROJECT_ID)
    return db, storage_client


def format_doc_to_markdown(doc_id: str, doc_data: dict, suggestions: list) -> str:
    """
    Formats an absorbed Brain document and its high-confidence/approved suggestions
    into a clean Markdown payload with YAML frontmatter for Vertex AI indexing.
    """
    filename = doc_data.get("filename", "Unknown Document")
    doc_type = doc_data.get("type", "General Reference")
    summary = doc_data.get("summary", "No summary available.")
    intent = doc_data.get("intent") or "General Knowledge Ingestion"
    absorbed_at = str(doc_data.get("absorbed_at", datetime.now().isoformat()))

    lines = [
        "---",
        f"id: {json.dumps(doc_id)}",
        f"title: {json.dumps(filename)}",
        f"type: {json.dumps(doc_type)}",
        f"absorbed_at: {json.dumps(absorbed_at)}",
        f"source_path: {json.dumps(doc_data.get('file_path', ''))}",
        "tier: \"Official Numista.AI Canon\"",
        "---",
        "",
        f"# {filename}",
        "",
        "## Classification",
        f"**Document Type**: {doc_type}",
        "",
        "## Summary",
        summary,
        "",
        "## Mission Briefing / User Intent",
        intent,
        "",
    ]

    if suggestions:
        lines.append("## Verified Facts & Self-Healing Suggestions")
        for idx, sug in enumerate(suggestions, 1):
            sug_text = sug.get("suggestion") or sug.get("action") or "Approved catalog update"
            target_coll = sug.get("target_collection") or "General"
            conf = sug.get("confidence")
            conf_str = f" ({int(conf * 100)}% confidence)" if conf is not None else ""
            status = sug.get("status", "pending")

            lines.append(f"{idx}. **[{target_coll.upper()}]** {sug_text}{conf_str} — *Status: {status}*")
            
            proposed_data = sug.get("proposed_data")
            if isinstance(proposed_data, dict) and proposed_data:
                lines.append("   ```json")
                lines.append(f"   {json.dumps(proposed_data, indent=2)}")
                lines.append("   ```")
        lines.append("")

    return "\n".join(lines)


def sync_canon_to_gcs() -> dict:
    """
    Core sync routine:
    1. Queries Firestore `brain_knowledge_base` for processed docs.
    2. Queries `brain_suggestions` for items marked 'approved' or confidence >= 0.93.
    3. Formats Markdown payloads.
    4. Uploads to gs://studio-9101802118-8c9a8-uploads/canon_library/.
    """
    logger.info("🚀 Starting Numista Brain Canon GCS Sync...")
    
    try:
        db, storage_client = get_gcp_clients()
        bucket = storage_client.bucket(BUCKET_NAME)
    except Exception as e:
        logger.error(f"Failed to connect to GCP: {e}")
        return {"status": "error", "message": f"GCP Connection failure: {e}"}

    # 1. Fetch Processed Knowledge Base Documents
    try:
        knowledge_docs = list(db.collection('brain_knowledge_base').stream())
        logger.info(f"Retrieved {len(knowledge_docs)} knowledge base docs from Firestore.")
    except Exception as e:
        logger.error(f"Failed to fetch brain_knowledge_base: {e}")
        return {"status": "error", "message": f"Firestore read failure: {e}"}

    # 2. Fetch High-Confidence or Approved Suggestions
    approved_suggestions = []
    try:
        all_sugs = list(db.collection('brain_suggestions').stream())
        for s in all_sugs:
            sdata = s.to_dict()
            sdata["id"] = s.id
            status = sdata.get("status")
            conf = sdata.get("confidence")
            
            # Criteria: Explicitly approved OR high confidence >= 0.93
            if status == "approved" or (conf is not None and conf >= 0.93 and status != "rejected"):
                approved_suggestions.append(sdata)
        logger.info(f"Qualified {len(approved_suggestions)} high-confidence / approved suggestions for Canon.")
    except Exception as e:
        logger.warning(f"Error fetching suggestions: {e}")

    # Map suggestions by source_doc_id
    sug_map = {}
    for sug in approved_suggestions:
        doc_id = sug.get("source_doc_id")
        if doc_id:
            sug_map.setdefault(doc_id, []).append(sug)

    uploaded_files = []
    total_suggestions_included = 0

    # 3. Format and Upload Individual Document Payloads
    for doc in knowledge_docs:
        doc_id = doc.id
        doc_data = doc.to_dict()
        doc_sugs = sug_map.get(doc_id, [])
        total_suggestions_included += len(doc_sugs)

        md_content = format_doc_to_markdown(doc_id, doc_data, doc_sugs)
        blob_path = f"{CANON_PREFIX}/{doc_id}.md"

        try:
            blob = bucket.blob(blob_path)
            blob.upload_from_string(md_content, content_type="text/markdown; charset=utf-8")
            uploaded_files.append(blob_path)
            logger.info(f"  Uploaded: gs://{BUCKET_NAME}/{blob_path}")
        except Exception as e:
            logger.error(f"  Failed to upload {blob_path}: {e}")

    # 4. Create Master Canon Index Document
    try:
        master_index_lines = [
            "---",
            "title: \"Numista.AI Master Canon Knowledge Index\"",
            f"updated_at: \"{datetime.now().isoformat()}\"",
            f"total_documents: {len(uploaded_files)}",
            f"total_facts: {total_suggestions_included}",
            "---",
            "",
            "# Numista.AI Master Canon Index",
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Cataloged Canon Reference Documents",
        ]
        for doc in knowledge_docs:
            ddata = doc.to_dict()
            master_index_lines.append(f"- **{ddata.get('filename')}** ({ddata.get('type')}) — {ddata.get('summary')}")
        
        master_blob = bucket.blob(f"{CANON_PREFIX}/_canon_master_index.md")
        master_blob.upload_from_string("\n".join(master_index_lines), content_type="text/markdown; charset=utf-8")
        uploaded_files.append(f"{CANON_PREFIX}/_canon_master_index.md")
        logger.info(f"  Uploaded master index: gs://{BUCKET_NAME}/{CANON_PREFIX}/_canon_master_index.md")
    except Exception as master_err:
        logger.warning(f"Could not create master index: {master_err}")

    summary_result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "bucket": BUCKET_NAME,
        "prefix": CANON_PREFIX,
        "gcs_uri_pattern": f"gs://{BUCKET_NAME}/{CANON_PREFIX}/*.md",
        "documents_synced": len(knowledge_docs),
        "suggestions_included": total_suggestions_included,
        "total_files_uploaded": len(uploaded_files)
    }

    logger.info(f"✅ Canon GCS Sync Complete: {len(uploaded_files)} files uploaded to gs://{BUCKET_NAME}/{CANON_PREFIX}/")
    return summary_result


if __name__ == "__main__":
    result = sync_canon_to_gcs()
    print(json.dumps(result, indent=2))
