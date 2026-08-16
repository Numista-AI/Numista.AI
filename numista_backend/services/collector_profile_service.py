"""
Collector Profile & Preference Episodic Memory Service
Maintains user-level numismatic goals, series focus, and grading preferences
under users/{uid}/collector_profile/preferences with strict snake_case contracts.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from routes.deps import db

logger = logging.getLogger("numista_backend.collector_profile_service")

VALID_INVESTMENT_GOALS = {"estate_planning", "numismatic_study", "commercial_trade"}


class CollectorProfileService:
    """
    Manages collector profile retrieval, preference updating, and
    system prompt memory generation for MORGAN AI.
    """

    def __init__(self, db_client=None):
        self.db = db_client or db

    def get_collector_profile(self, uid: str) -> Dict[str, Any]:
        """
        Retrieves user's collector preferences from Firestore.
        Returns default baseline profile if not yet created.
        """
        default_profile = {
            "schema_version": "1.0",
            "preferred_series": [],
            "target_grade_min": "",
            "target_grade_max": "",
            "preferred_services": ["PCGS", "NGC"],
            "investment_goal": "numismatic_study",
            "budget_tier": "intermediate",
            "opt_in_chat_extraction": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if not self.db or not uid:
            return default_profile

        try:
            doc_ref = (
                self.db.collection("users")
                .document(uid)
                .collection("collector_profile")
                .document("preferences")
            )
            snap = doc_ref.get()
            if snap.exists:
                data = snap.to_dict() or {}
                # Merge with default structure to ensure all keys exist
                merged = {**default_profile, **data}
                return merged
        except Exception as e:
            logger.warning(f"Error fetching collector profile for {uid}: {e}")

        return default_profile

    def update_collector_profile(self, uid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and updates collector preferences under users/{uid}/collector_profile/preferences.
        Strictly enforces lowercase snake_case keys and valid enum values.
        """
        if not self.db or not uid:
            return {"status": "error", "message": "Database not initialized or missing UID"}

        cleaned: Dict[str, Any] = {
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        if "preferred_series" in updates and isinstance(updates["preferred_series"], list):
            cleaned["preferred_series"] = [str(s).strip() for s in updates["preferred_series"] if s]

        if "target_grade_min" in updates:
            cleaned["target_grade_min"] = str(updates["target_grade_min"]).strip().upper()

        if "target_grade_max" in updates:
            cleaned["target_grade_max"] = str(updates["target_grade_max"]).strip().upper()

        if "preferred_services" in updates and isinstance(updates["preferred_services"], list):
            cleaned["preferred_services"] = [str(s).strip().upper() for s in updates["preferred_services"] if s]

        if "investment_goal" in updates:
            goal = str(updates["investment_goal"]).strip().lower()
            if goal in VALID_INVESTMENT_GOALS:
                cleaned["investment_goal"] = goal

        if "budget_tier" in updates:
            cleaned["budget_tier"] = str(updates["budget_tier"]).strip().lower()

        if "opt_in_chat_extraction" in updates:
            cleaned["opt_in_chat_extraction"] = bool(updates["opt_in_chat_extraction"])

        try:
            doc_ref = (
                self.db.collection("users")
                .document(uid)
                .collection("collector_profile")
                .document("preferences")
            )
            doc_ref.set(cleaned, merge=True)
            return {"status": "success", "profile": self.get_collector_profile(uid)}
        except Exception as e:
            logger.error(f"Failed to write collector profile for {uid}: {e}")
            return {"status": "error", "message": str(e)}

    def build_profile_prompt_context(self, uid: str) -> str:
        """
        Generates episodic collector profile context string for injection into MORGAN's prompt.
        """
        profile = self.get_collector_profile(uid)
        if not profile:
            return ""

        series = ", ".join(profile.get("preferred_series", [])) or "All US Series"
        grade_min = profile.get("target_grade_min", "None")
        grade_max = profile.get("target_grade_max", "None")
        goal = profile.get("investment_goal", "numismatic_study").replace("_", " ").title()
        services = ", ".join(profile.get("preferred_services", ["PCGS", "NGC"]))

        return (
            f"### COLLECTOR PROFILE & EPISODIC MEMORY (User UID: {uid[:8]}...):\n"
            f"- Primary Collecting Focus: {series}\n"
            f"- Target Grade Range: {grade_min} to {grade_max}\n"
            f"- Primary Investment / Estate Goal: {goal}\n"
            f"- Preferred Certification Services: {services}\n"
            f"Tailor advice and recommendations to align with these collector goals.\n"
        )


# Global Singleton
collector_profile_service = CollectorProfileService()
