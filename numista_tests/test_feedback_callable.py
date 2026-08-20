import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
import asyncio as _asyncio

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'numista_backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from routes.feedback_callable_route import _to_dt, _compute_doc_id, _format_transcript

# =============================================================================
# Section 1 — Helper function unit tests
# =============================================================================

class TestToDt:
    def test_passthrough_aware_datetime(self):
        dt = datetime(2026, 8, 20, 12, 0, 0, tzinfo=timezone.utc)
        assert _to_dt(dt) == dt

    def test_naive_datetime_gets_utc(self):
        dt = datetime(2026, 8, 20, 12, 0, 0)
        assert _to_dt(dt).tzinfo == timezone.utc

    def test_firestore_timestamp_object(self):
        mock_ts = MagicMock()
        mock_ts.timestamp.return_value = 1755734400.0
        result = _to_dt(mock_ts)
        assert isinstance(result, datetime) and result.tzinfo == timezone.utc

    def test_fallback_for_unknown_type(self):
        result = _to_dt("not-a-timestamp")
        assert isinstance(result, datetime) and result.tzinfo == timezone.utc


class TestComputeDocId:
    def test_counter_affects_doc_id(self):
        uid = "testUser123"
        assert _compute_doc_id(uid, "manualFAB", 1) != _compute_doc_id(uid, "manualFAB", 2)

    def test_reason_affects_doc_id(self):
        uid = "testUser123"
        assert _compute_doc_id(uid, "manualFAB", 1) != _compute_doc_id(uid, "navigation", 1)

    def test_returns_nonempty_string(self):
        doc_id = _compute_doc_id("uid", "manualFAB", 1)
        assert isinstance(doc_id, str) and len(doc_id) > 0


class TestFormatTranscript:
    def test_empty(self):
        assert _format_transcript([]) == ""

    def test_user_message(self):
        result = _format_transcript([{"role": "user", "message": "Morgan Dollar"}])
        assert "USER:" in result and "Morgan Dollar" in result

    def test_uses_message_redacted_fallback(self):
        result = _format_transcript([{"role": "user", "message": None, "message_redacted": "REDACTED"}])
        assert "REDACTED" in result

    def test_multi_turn_order(self):
        msgs = [
            {"role": "assistant", "message": "Hello"},
            {"role": "user", "message": "Hi"},
        ]
        lines = _format_transcript(msgs).strip().split("\n")
        assert lines[0].startswith("ASSISTANT:") and lines[1].startswith("USER:")


# =============================================================================
# Section 2 — CHECK handler business logic (mocked Firestore)
# =============================================================================

def _make_db_mock(user_data: dict):
    doc_snap = MagicMock()
    doc_snap.exists = bool(user_data)
    doc_snap.to_dict.return_value = user_data
    doc_ref = MagicMock()
    doc_ref.get.return_value = doc_snap
    doc_ref.set = MagicMock()
    coll = MagicMock()
    coll.document.return_value = doc_ref
    db_mock = MagicMock()
    db_mock.collection.return_value = coll
    return db_mock, doc_ref


def test_check_clean_user_allowed():
    from routes.feedback_callable_route import _handle_check, CallableRequest
    db_mock, doc_ref = _make_db_mock({})
    req = CallableRequest(mode="CHECK", trigger_reason="manualFAB")
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_check("uid1", req))
    assert result["allowed"] is True
    assert result["interview_mode"] is True
    assert "lock_id" in result and "draft_doc_id" in result
    doc_ref.set.assert_called_once()


def test_check_active_lock_returns_credentials():
    """CRITICAL: already_locked must return lock_id + draft_doc_id for fallback form submit."""
    from routes.feedback_callable_route import _handle_check, CallableRequest
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    user_data = {
        "feedback_trigger_lock": {
            "locked_until": future,
            "lock_id": "existing-lock-abc",
            "draft_doc_id": "fb_draft_existing",
            "reason": "manualFAB",
        }
    }
    db_mock, doc_ref = _make_db_mock(user_data)
    req = CallableRequest(mode="CHECK", trigger_reason="manualFAB")
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_check("uid1", req))
    assert result["allowed"] is False
    assert result["reason"] == "already_locked"
    assert result["lock_id"] == "existing-lock-abc"       # must be present for fallback submit
    assert result["draft_doc_id"] == "fb_draft_existing"  # must be present for fallback submit
    doc_ref.set.assert_not_called()


def test_check_expired_lock_cleared():
    from routes.feedback_callable_route import _handle_check, CallableRequest
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    user_data = {
        "feedback_trigger_lock": {
            "locked_until": past,
            "lock_id": "old-lock",
            "draft_doc_id": "fb_old",
        }
    }
    db_mock, _ = _make_db_mock(user_data)
    req = CallableRequest(mode="CHECK", trigger_reason="manualFAB")
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_check("uid1", req))
    assert result["allowed"] is True


def test_check_behavioral_throttle_blocks_non_fab():
    from routes.feedback_callable_route import _handle_check, CallableRequest, BEHAVIORAL_THROTTLE_SECONDS
    recent = datetime.now(timezone.utc) - timedelta(seconds=BEHAVIORAL_THROTTLE_SECONDS - 100)
    db_mock, _ = _make_db_mock({"last_feedback_trigger_ts": recent})
    req = CallableRequest(mode="CHECK", trigger_reason="navigation")
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_check("uid1", req))
    assert result["allowed"] is False and result["reason"] == "throttled"


def test_check_fab_bypasses_behavioral_throttle():
    """manualFAB must NOT be blocked by the 24h behavioral throttle."""
    from routes.feedback_callable_route import _handle_check, CallableRequest, BEHAVIORAL_THROTTLE_SECONDS
    recent = datetime.now(timezone.utc) - timedelta(seconds=BEHAVIORAL_THROTTLE_SECONDS - 100)
    db_mock, _ = _make_db_mock({"last_feedback_trigger_ts": recent})
    req = CallableRequest(mode="CHECK", trigger_reason="manualFAB")
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_check("uid1", req))
    assert result["allowed"] is True


def test_check_rate_limit_fallback_mode():
    from routes.feedback_callable_route import _handle_check, CallableRequest, MAX_INTERVIEWS_PER_WINDOW, RATE_LIMIT_WINDOW_SECONDS
    recent_reset = datetime.now(timezone.utc) - timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS - 60)
    db_mock, _ = _make_db_mock({
        "interviews_this_hour": MAX_INTERVIEWS_PER_WINDOW,
        "interviews_this_hour_reset_at": recent_reset,
    })
    req = CallableRequest(mode="CHECK", trigger_reason="manualFAB")
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_check("uid1", req))
    assert result["allowed"] is True
    assert result["interview_mode"] is False
    assert result["reason"] == "rate_limited"


# =============================================================================
# Section 3 — DISMISS handler
# =============================================================================

def test_dismiss_clears_lock():
    import uuid
    from routes.feedback_callable_route import _handle_dismiss, CallableRequest
    lock_id = str(uuid.uuid4())
    user_data = {
        "feedback_trigger_lock": {
            "lock_id": lock_id,
            "draft_doc_id": "fb_draft",
            "reason": "manualFAB",
            "locked_until": datetime.now(timezone.utc) + timedelta(hours=1),
        }
    }
    db_mock, doc_ref = _make_db_mock(user_data)
    req = CallableRequest(mode="DISMISS", lock_id=lock_id)
    with patch('routes.feedback_callable_route.db', db_mock):
        result = _asyncio.run(_handle_dismiss("uid1", req))
    assert result.get("status") == "dismissed"
    doc_ref.set.assert_called_once()


# =============================================================================
# Section 4 — Constants sanity
# =============================================================================

def test_behavioral_throttle_is_24h():
    from routes.feedback_callable_route import BEHAVIORAL_THROTTLE_SECONDS
    assert BEHAVIORAL_THROTTLE_SECONDS == 86400

def test_rate_limit_window_is_1h():
    from routes.feedback_callable_route import RATE_LIMIT_WINDOW_SECONDS
    assert RATE_LIMIT_WINDOW_SECONDS == 3600

def test_max_interviews_per_window_is_reasonable():
    from routes.feedback_callable_route import MAX_INTERVIEWS_PER_WINDOW
    assert 1 <= MAX_INTERVIEWS_PER_WINDOW <= 10

def test_interview_max_duration_is_reasonable():
    from routes.feedback_callable_route import INTERVIEW_MAX_DURATION_SECONDS
    assert 300 <= INTERVIEW_MAX_DURATION_SECONDS <= 7200
