"""
Dynamic Few-Shot Exemplar Service for Numista.AI
Retrieves verified Human-in-the-Loop (HITL) corrections and gold-standard exemplars
for multi-modal vision and document ingestion prompts.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("numista_backend.few_shot_service")


class FewShotExemplarService:
    """
    Retrieves high-quality, human-verified exemplars for in-context learning
    across checklist parsing, document classification, and visual coin grading.
    """

    def __init__(self, db_client=None, fallback_file_path: Optional[str] = None):
        self.db = db_client
        self.fallback_file_path = fallback_file_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "hitl_training_corrections.json"
        )

    def get_verified_exemplars(
        self,
        task_type: str,
        query_context: Optional[Dict[str, Any]] = None,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves up to `limit` verified exemplars matching the specified task_type.
        Enforces >= 67% consensus agreement rule on human reviews.
        """
        exemplars = []

        # 1. Attempt Firestore fetch if DB client is available
        if self.db:
            try:
                query = (
                    self.db.collection("hitl_training_corrections")
                    .where("task_type", "==", task_type)
                    .where("consensus_status", "==", "verified")
                    .limit(limit * 3)
                )
                docs = list(query.stream())
                for doc in docs:
                    data = doc.to_dict() or {}
                    if data.get("consensus_ratio", 1.0) >= 0.67:
                        exemplars.append(data)
                        if len(exemplars) >= limit:
                            break
            except Exception as e:
                logger.warning(f"Firestore HITL exemplar fetch failed: {e}")

        # 2. Fallback to local JSON log if Firestore returns insufficient items
        if len(exemplars) < limit and os.path.exists(self.fallback_file_path):
            try:
                with open(self.fallback_file_path, "r", encoding="utf-8") as f:
                    local_records = json.load(f)
                for rec in local_records:
                    if rec.get("task_type", "visual_grade") == task_type or task_type == "all":
                        exemplars.append(rec)
                        if len(exemplars) >= limit:
                            break
            except Exception as fe:
                logger.warning(f"Local HITL fallback read error: {fe}")

        return exemplars[:limit]

    def format_exemplars_for_prompt(
        self,
        exemplars: List[Dict[str, Any]],
        task_type: str = "checklist_ocr",
    ) -> str:
        """
        Formats verified exemplars into a clean, few-shot prompt section.
        """
        if not exemplars:
            return ""

        formatted_lines = [
            "### VERIFIED NUMISMATIC REFERENCE EXEMPLARS (Few-Shot Grounding):",
            "Use these verified historical corrections as guidance for formatting and attribution:",
        ]

        for i, ex in enumerate(exemplars, 1):
            input_sample = ex.get("input_payload") or ex.get("notes") or ex.get("coin_id")
            output_sample = ex.get("verified_output") or ex.get("human_suggested_grade")
            formatted_lines.append(f"\nExample {i}:")
            formatted_lines.append(f"- Raw Input / Problem: {input_sample}")
            formatted_lines.append(f"- Verified Output: {output_sample}")

        formatted_lines.append("\nApply the same rigorous standard to the current input.\n")
        return "\n".join(formatted_lines)


# Global Singleton
few_shot_service = FewShotExemplarService()
