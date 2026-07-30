"""
Greysheet Quota Service — Manages API call counting, 24-hour cache TTL,
atomic Firestore increments, request coalescing, 25k warning alerts, and 50k hard cap.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable
from google.cloud import firestore

logger = logging.getLogger("greysheet_quota_service")

# Tier Pricing & Budget Limits
WARNING_CALL_LIMIT = 25000  # Send alert at 25,000 calls ($143/mo tier benchmark)
HARD_CAP_CALL_LIMIT = 50000 # Hard cost cap at 50,000 calls ($287/mo variable limit)

class GreysheetQuotaService:
    def __init__(self, db: Optional[firestore.Client] = None):
        self._db = db
        self._single_flight_in_flight: Dict[str, Any] = {}

    def _get_current_month_key(self) -> str:
        """Returns UTC YYYY-MM key for tracking monthly usage."""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m")

    def get_monthly_usage(self) -> Dict[str, Any]:
        """Returns the current month's usage document from Firestore."""
        month_key = self._get_current_month_key()
        if not self._db:
            return {"total_calls": 0, "month_key": month_key, "is_hard_capped": False, "is_warning_sent": False}
        
        try:
            doc_ref = self._db.collection("greysheet_usage").document(month_key)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict() or {}
                calls = data.get("total_calls", 0)
                return {
                    "total_calls": calls,
                    "month_key": month_key,
                    "is_hard_capped": calls >= HARD_CAP_CALL_LIMIT,
                    "is_warning_sent": data.get("warning_sent", False),
                    "last_updated": data.get("last_updated")
                }
            else:
                # Initialize new month
                doc_ref.set({
                    "total_calls": 0,
                    "month_key": month_key,
                    "warning_sent": False,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "last_updated": firestore.SERVER_TIMESTAMP
                })
                return {"total_calls": 0, "month_key": month_key, "is_hard_capped": False, "is_warning_sent": False}
        except Exception as e:
            logger.error(f"[Greysheet Quota] Error reading monthly usage: {e}")
            return {"total_calls": 0, "month_key": month_key, "is_hard_capped": False, "is_warning_sent": False}

    def increment_call_count(self) -> int:
        """
        Atomically increments the monthly API call counter in Firestore using FieldValue.increment(1).
        Triggers 25k warning alert if threshold crossed for the first time in the month.
        Returns updated estimate of total calls.
        """
        month_key = self._get_current_month_key()
        if not self._db:
            return 1
            
        try:
            doc_ref = self._db.collection("greysheet_usage").document(month_key)
            doc_ref.set({
                "total_calls": firestore.Increment(1),
                "last_updated": firestore.SERVER_TIMESTAMP
            }, merge=True)
            
            # Fetch current total to check for warning alert threshold
            usage = self.get_monthly_usage()
            current_calls = usage.get("total_calls", 0)
            
            if current_calls >= WARNING_CALL_LIMIT and not usage.get("is_warning_sent"):
                self._send_warning_alert(current_calls, month_key)
                
            return current_calls
        except Exception as e:
            logger.error(f"[Greysheet Quota] Error incrementing call count: {e}")
            return 0

    def _send_warning_alert(self, current_calls: int, month_key: str):
        """Logs high-priority warning and creates system notification in Firestore."""
        logger.warning(
            f"[Greysheet Quota ALERT] API usage has reached {current_calls:,} calls for {month_key}! "
            f"Approaching 25,000 threshold ($143/mo projected cost)."
        )
        if self._db:
            try:
                # Mark warning sent
                self._db.collection("greysheet_usage").document(month_key).set({
                    "warning_sent": True,
                    "warning_sent_at": firestore.SERVER_TIMESTAMP
                }, merge=True)
                
                # Write to system_notifications
                self._db.collection("system_notifications").add({
                    "type": "greysheet_quota_warning",
                    "title": "Greysheet API Quota Warning (25K Calls)",
                    "message": f"Greysheet API call volume for {month_key} has reached {current_calls:,} calls (approaching 25k limit).",
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "status": "unread"
                })
            except Exception as e:
                logger.error(f"[Greysheet Quota] Error writing warning notification: {e}")

    def is_hard_cap_engaged(self) -> bool:
        """Returns True if current month's usage has reached or exceeded 50,000 calls."""
        usage = self.get_monthly_usage()
        if usage.get("is_hard_capped"):
            logger.warning(
                f"[Greysheet Quota HARD CAP] Monthly limit of {HARD_CAP_CALL_LIMIT:,} calls reached. "
                "Serving strictly from 24h cache or fallback."
            )
            return True
        return False

    def is_cache_valid(self, updated_at: Optional[datetime], ttl_hours: int = 24) -> bool:
        """Checks if a cached item's timestamp is within the 24-hour TTL window per CDN §7.2."""
        if not updated_at:
            return False
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - updated_at
        return delta < timedelta(hours=ttl_hours)
