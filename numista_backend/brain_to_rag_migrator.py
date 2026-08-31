#!/usr/bin/env python3
"""
brain_to_rag_migrator.py
Populates numismatic_reference_chunks from brain_knowledge_base
for Morgan's RAG pipeline.

Usage:
    # Phase 1 - Dry run (no writes, no embedding calls):
    python brain_to_rag_migrator.py --dry-run

    # Phase 2 - Pilot 10 documents:
    python brain_to_rag_migrator.py --pilot-10 --write-production

    # Phase 3 - Full run from allowlist:
    python brain_to_rag_migrator.py --allowlist-file allowlist.txt --write-production

Rules:
    - --write-production is required for any live Firestore write.
    - Omitting --write-production forces dry-run regardless of other flags.
    - --dry-run, --pilot-10, and --allowlist-file are mutually exclusive.
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import google.auth
from google.api_core.exceptions import ResourceExhausted
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google import genai
from google.genai import types as genai_types

# Configuration
PROJECT_ID = "studio-9101802118-8c9a8"
LOCATION = "global"
EMBEDDING_MODEL = "gemini-embedding-2"
CHUNKS_COLLECTION = "numismatic_reference_chunks"
KB_COLLECTION = "brain_knowledge_base"
MIN_CONTENT_LENGTH = 200
BATCH_SIZE = 10
BASE_RATE_DELAY = 1.0
MAX_RETRIES = 3
EXPECTED_VECTOR_DIM = 1536   # Phase 4: 1536-dim MRL cut (Firestore cap is 2048; 3072 is illegal for indexing)
OUTPUT_DIMENSIONALITY = 1536  # Passed to gemini-embedding-2 via EmbedContentConfig
MAX_ALLOWLIST_ENTRIES = 50

# 10 named pilot documents - resolved to current filename winners at runtime.
# Do not bake source_doc_ids here; --pilot-10 resolves filename at runtime.
PILOT_10_FILENAMES = [
    "100_Famous_US_Coin_Errors.xlsx",
    "Grading-Standards.pdf",
    "List of Official US Mint Terms.docx",
    "Numismatic Abbreviations.xlsx",
    "Coin Counterfeit Diagnostics Guide.xlsx",
    "US_Mint_Official_2026_Specifications_Truth_Table.md",
    "usmint_2026_harvest_report.md",
    "Diagnostic & Authentication Prompt Guide.docx",
    "official us coin nomenclatures.docx",
    "guide-to-us-type-coins.pdf",
]

VALID_CATEGORIES = {
    "Variety Guide", "Grading", "Formal Nomenclature", "Mintage Report",
    "Historical Reference", "Checklist", "Article", "Price Guide",
}

# Filename keyword hard deny - case-insensitive substring match on filename only.
HARD_DENY_FILENAME_KEYWORDS = {
    "invoice", "receipt", "payment", "estate_worksheet", "partition", "token",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("brain_to_rag_migrator")


def normalize_category(raw_type: str) -> str:
    """Map brain_knowledge_base type field to validated category enum."""
    if raw_type in VALID_CATEGORIES:
        return raw_type
    return "Historical Reference"


def is_hard_deny(filename: str) -> bool:
    """Hard deny based on filename keywords only. No fragile summary heuristics."""
    fname_lower = filename.lower()
    return any(kw in fname_lower for kw in HARD_DENY_FILENAME_KEYWORDS)


def probe_embedding(client) -> None:
    """
    Runs a single probe call before any writes.
    Asserts output is the correct dimension and type.
    Halts execution on failure.
    """
    resp = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents="probe",
        config=genai_types.EmbedContentConfig(output_dimensionality=OUTPUT_DIMENSIONALITY),
    )
    if hasattr(resp, "embeddings") and len(resp.embeddings) > 0:
        probe_vec = resp.embeddings[0].values
    elif hasattr(resp, "embedding"):
        probe_vec = resp.embedding.values
    else:
        raise AssertionError("Probe: unrecognised response shape")

    assert isinstance(probe_vec, (list, Vector)) and len(probe_vec) == 1536, \
        f"Probe failed: type={type(probe_vec).__name__}, len={len(probe_vec)}"
    logger.info(f"PROBE_OK: dimension={len(probe_vec)}, type={type(probe_vec).__name__}")


def generate_embedding(client, text: str) -> Optional[list]:
    """
    Generate 1536-dim embedding via gemini-embedding-2 with MRL output_dimensionality.
    Exponential backoff on ResourceExhausted. Returns None on failure.
    Never returns a partial or zero-length vector.
    """
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text.strip(),
                config=genai_types.EmbedContentConfig(output_dimensionality=OUTPUT_DIMENSIONALITY),
            )
            if hasattr(resp, "embedding") and hasattr(resp.embedding, "values"):
                vec = list(resp.embedding.values)
            elif hasattr(resp, "embeddings") and len(resp.embeddings) > 0:
                vec = list(resp.embeddings[0].values)
            elif isinstance(resp, dict) and "embedding" in resp:
                vec = resp["embedding"].get("values", [])
            else:
                vec = []

            if len(vec) != EXPECTED_VECTOR_DIM:
                logger.error(f"  EMBED_BAD_DIM: got {len(vec)}, expected {EXPECTED_VECTOR_DIM}")
                return None
            return vec

        except ResourceExhausted:
            wait = (2 ** attempt) * BASE_RATE_DELAY
            logger.warning(f"  ResourceExhausted (attempt {attempt+1}/{MAX_RETRIES}). Retrying in {wait:.1f}s...")
            time.sleep(wait)
        except Exception as e:
            logger.error(f"  EMBED_ERROR: {e}")
            return None

    logger.error(f"  EMBED_FAILED after {MAX_RETRIES} retries")
    return None



def probe_embedding_dim(client) -> bool:
    """Probe embedding dimension before any real calls."""
    logger.info("Probing embedding dimension...")
    vec = generate_embedding(client, "numismatic test")
    if vec is None:
        logger.error("PROBE_FAILED: Cannot generate embedding. Check ADC and Vertex AI quota.")
        return False
    logger.info(f"PROBE_OK: dimension = {len(vec)}")
    return True


def load_eligible_docs(db) -> list:
    """
    Load brain_knowledge_base, deduplicate by filename (keep most recent absorbed_at),
    and apply corpus inclusion policy.
    """
    logger.info(f"Loading {KB_COLLECTION}...")
    all_docs = list(db.collection(KB_COLLECTION).stream())
    logger.info(f"  Total KB documents: {len(all_docs)}")

    # Group by filename, keep most recent absorbed_at
    by_filename: dict = {}
    for doc in all_docs:
        d = doc.to_dict() or {}
        filename = (d.get("filename") or "").strip()
        absorbed_at = d.get("absorbed_at")
        if not filename:
            continue
        if filename not in by_filename:
            by_filename[filename] = (doc.id, d, absorbed_at)
        else:
            existing_at = by_filename[filename][2]
            if absorbed_at and (existing_at is None or absorbed_at > existing_at):
                by_filename[filename] = (doc.id, d, absorbed_at)

    total_dup = len(all_docs) - len(by_filename)
    logger.info(f"  After filename dedup: {len(by_filename)} unique sources ({total_dup} SKIP_DUPLICATE)")

    eligible = []
    for filename, (doc_id, d, absorbed_at) in sorted(by_filename.items()):
        summary = (d.get("summary") or "").strip()
        raw_type = (d.get("type") or "").strip()

        if is_hard_deny(filename):
            logger.info(f"  SKIP_DENY    {doc_id} | {filename}")
            continue

        if len(summary) < MIN_CONTENT_LENGTH:
            logger.info(f"  SKIP_SHORT   {doc_id} | {filename} ({len(summary)} chars)")
            continue

        eligible.append({
            "source_doc_id": doc_id,
            "filename": filename,
            "summary": summary,
            "category": normalize_category(raw_type),
            "absorbed_at": absorbed_at,
        })

    logger.info(f"  Eligible after policy: {len(eligible)}")
    return eligible


def load_pilot_10(eligible: list) -> list:
    """Filter eligible to the 10 named pilot filenames. Runtime filename resolution."""
    pilot_set = set(PILOT_10_FILENAMES)
    result = [e for e in eligible if e["filename"] in pilot_set]
    found = {e["filename"] for e in result}
    missing = pilot_set - found
    if missing:
        logger.warning(f"PILOT_10: {len(missing)} named file(s) not in eligible set:")
        for m in sorted(missing):
            logger.warning(f"  MISSING: {m}")
    logger.info(f"PILOT_10: {len(result)} of {len(PILOT_10_FILENAMES)} documents eligible")
    return result


def load_allowlist(allowlist_path: str, eligible: list) -> list:
    """Filter eligible to source_doc_ids in allowlist file. Validates <=50 and known IDs."""
    eligible_ids = {e["source_doc_id"] for e in eligible}
    path = Path(allowlist_path)
    if not path.exists():
        logger.error(f"Allowlist file not found: {allowlist_path}")
        sys.exit(1)

    lines = [
        ln.strip()
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.startswith("#")
    ]

    if len(lines) > MAX_ALLOWLIST_ENTRIES:
        logger.error(f"Allowlist has {len(lines)} entries - max is {MAX_ALLOWLIST_ENTRIES}. Trim it.")
        sys.exit(1)

    unknown = [ln for ln in lines if ln not in eligible_ids]
    if unknown:
        logger.error(f"Allowlist contains {len(unknown)} source_doc_id(s) not in eligible set:")
        for u in unknown:
            logger.error(f"  UNKNOWN: {u}")
        logger.error("Run --dry-run to get current eligible set, then rebuild allowlist.txt.")
        sys.exit(1)

    allowlist_set = set(lines)
    selected = [e for e in eligible if e["source_doc_id"] in allowlist_set]
    logger.info(f"Allowlist: {len(selected)} documents selected")
    return selected


def run(args):
    is_dry_run = args.dry_run or not getattr(args, "write_production", False)

    if is_dry_run:
        logger.info("=" * 64)
        logger.info("DRY-RUN MODE - zero Firestore writes, zero embedding calls")
        logger.info("=" * 64)
    else:
        logger.info("=" * 64)
        logger.info(f"LIVE WRITE MODE - production Firestore ({PROJECT_ID})")
        logger.info("=" * 64)

    try:
        credentials, _ = google.auth.default()
        db = firestore.Client(credentials=credentials, project=PROJECT_ID)
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        logger.info("Clients initialized via ADC")
    except Exception as e:
        logger.error(f"Client init failed: {e}")
        sys.exit(1)

    eligible = load_eligible_docs(db)

    if getattr(args, "pilot_10", False):
        selected = load_pilot_10(eligible)
    elif getattr(args, "allowlist_file", None):
        selected = load_allowlist(args.allowlist_file, eligible)
    else:
        selected = eligible

    selected_ids = {e["source_doc_id"] for e in selected}

    # Print manifest - ALL eligible shown, WOULD_WRITE or ELIGIBLE_NOT_SELECTED
    logger.info("-" * 64)
    logger.info(f"MANIFEST ({len(eligible)} eligible, {len(selected)} selected):")
    for e in eligible:
        tag = "WOULD_WRITE          " if e["source_doc_id"] in selected_ids else "ELIGIBLE_NOT_SELECTED"
        logger.info(f"  {tag}  {e['source_doc_id']} | {e['filename']} | {e['category']} | {len(e['summary'])} chars")
    logger.info("-" * 64)

    if is_dry_run:
        logger.info("DRY-RUN complete.")
        logger.info(f"  {len(eligible)} eligible documents listed above (may exceed 50 - that is correct).")
        logger.info(f"  {len(selected)} marked WOULD_WRITE for this run mode.")
        logger.info("Next steps:")
        logger.info("  Phase 2: python brain_to_rag_migrator.py --pilot-10 --write-production")
        logger.info("  Phase 3: build allowlist.txt (max 50 source_doc_ids), then:")
        logger.info("           python brain_to_rag_migrator.py --allowlist-file allowlist.txt --write-production")
        return

    probe_embedding(client)  # AssertionError halts execution if dimension != 1536

    batch = db.batch()
    batch_count = 0
    written = 0
    skipped_exists = 0
    overwritten = 0
    failed_embed = 0

    for entry in selected:
        source_doc_id = entry["source_doc_id"]
        chunk_id = f"{source_doc_id}_0000"
        content_text = entry["summary"]

        chunk_ref = db.collection(CHUNKS_COLLECTION).document(chunk_id)
        existing = chunk_ref.get()
        if existing.exists:
            existing_data = existing.to_dict() or {}
            existing_vec = existing_data.get("embedding_vector", [])
            vec_len = len(existing_vec) if isinstance(existing_vec, list) else 0
            if vec_len == EXPECTED_VECTOR_DIM:
                logger.info(f"  SKIP_EXISTS   {chunk_id} (vector_len={vec_len})")
                skipped_exists += 1
                continue
            else:
                logger.info(f"  OVERWRITE     {chunk_id} (existing vector_len={vec_len} - malformed)")
                overwritten += 1

        # Generate embedding - never write on failure
        vec = generate_embedding(client, content_text)
        if vec is None:
            logger.error(f"  EMBED_FAILED  {chunk_id} - skipping, no write")
            failed_embed += 1
            continue

        time.sleep(BASE_RATE_DELAY)

        chunk_data = {
            "chunk_id": chunk_id,
            "source_doc_id": source_doc_id,
            "title": Path(entry["filename"]).stem,
            "source_document": entry["filename"],
            "content_text": content_text,
            "embedding_vector": Vector(vec),   # Phase 4: Firestore Vector type (not raw list)
            "category": entry["category"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        batch.set(chunk_ref, chunk_data)  # set(), never merge=True
        batch_count += 1
        written += 1
        logger.info(f"  QUEUED        {chunk_id} | {entry['filename']}")

        if batch_count >= BATCH_SIZE:
            batch.commit()
            logger.info(f"  Batch committed ({batch_count} ops)")
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
        logger.info(f"  Final batch committed ({batch_count} ops)")

    logger.info("=" * 64)
    logger.info("DONE:")
    logger.info(f"  {written} written")
    logger.info(f"  {skipped_exists} skipped (SKIP_EXISTS, valid {EXPECTED_VECTOR_DIM}-dim vector)")
    logger.info(f"  {overwritten} overwritten (malformed vector replaced)")
    logger.info(f"  {failed_embed} failed embedding (no write)")
    logger.info("=" * 64)



def main():
    parser = argparse.ArgumentParser(
        description="Migrate brain_knowledge_base summaries to numismatic_reference_chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true",
                      help="Print manifest only. No writes, no embedding calls.")
    mode.add_argument("--pilot-10", action="store_true",
                      help="Select the 10 named pilot documents. Requires --write-production.")
    mode.add_argument("--allowlist-file", metavar="PATH",
                      help="Select source_doc_ids in this file (max 50). Requires --write-production.")

    parser.add_argument("--write-production", action="store_true",
                        help="Authorize live Firestore writes. Omit to force dry-run.")

    args = parser.parse_args()

    if not args.write_production and not args.dry_run:
        logger.warning("--write-production not set. Forcing dry-run.")
        args.dry_run = True

    run(args)


if __name__ == "__main__":
    main()
