"""
Numista.AI — Structured Logging Configuration
═══════════════════════════════════════════════
Centralized logging module for the Numista.AI backend.

Features:
  • JSON-structured logs that Cloud Run forwards to Cloud Logging automatically
  • Severity levels mapped to GCP log levels (DEBUG → CRITICAL)
  • Per-request context (request_id) via contextvars
  • Zero external dependencies — uses Python's built-in logging module

Usage:
    from logging_config import get_logger, request_id_var
    logger = get_logger(__name__)
    logger.info("Processing coin", extra={"user_email": email, "coin_id": cid})
"""

import logging
import json
import os
import sys
import uuid
import time
from contextvars import ContextVar
from datetime import datetime, timezone

# ── Context variable for per-request tracking ─────────────────────────────────
# Set by the FastAPI middleware on each incoming request.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# ── GCP severity mapping ──────────────────────────────────────────────────────
# Cloud Logging expects a `severity` field with these exact strings.
_GCP_SEVERITY = {
    logging.DEBUG:    "DEBUG",
    logging.INFO:     "INFO",
    logging.WARNING:  "WARNING",
    logging.ERROR:    "ERROR",
    logging.CRITICAL: "CRITICAL",
}


class CloudJSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects.

    On Cloud Run, anything written to stdout as a JSON object with a
    `severity` field is automatically parsed by Cloud Logging and
    displayed with the correct log level in the GCP console.

    Locally (when CLOUD_RUN is not set), it falls back to a readable
    coloured format for developer convenience.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "severity": _GCP_SEVERITY.get(record.levelno, "DEFAULT"),
            "message": record.getMessage(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logger": record.name,
            "module": record.module,
            "request_id": request_id_var.get("-"),
        }

        # Merge any extra structured fields passed via `extra={...}`
        # Standard LogRecord attributes to skip
        _SKIP = {
            "name", "msg", "args", "created", "relativeCreated",
            "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "filename", "module", "pathname", "thread", "threadName",
            "processName", "process", "levelname", "levelno",
            "msecs", "message", "taskName",
        }
        for key, val in record.__dict__.items():
            if key not in _SKIP and key not in log_entry and not key.startswith("_"):
                try:
                    json.dumps(val)  # only include JSON-serializable values
                    log_entry[key] = val
                except (TypeError, ValueError):
                    log_entry[key] = str(val)

        # Attach exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class ReadableFormatter(logging.Formatter):
    """
    Human-readable formatter for local development (non-Cloud-Run).
    """
    _COLORS = {
        logging.DEBUG:    "\033[36m",   # cyan
        logging.INFO:     "\033[32m",   # green
        logging.WARNING:  "\033[33m",   # yellow
        logging.ERROR:    "\033[31m",   # red
        logging.CRITICAL: "\033[35m",   # magenta
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, "")
        rid = request_id_var.get("-")
        rid_short = rid[:8] if rid != "-" else "-"
        prefix = f"{color}{record.levelname:<7}{self._RESET}"
        return f"{prefix} [{record.name}] [{rid_short}] {record.getMessage()}"


# ── Rate-limit tracker (observation-only) ─────────────────────────────────────
class RateLimitTracker:
    """
    Tracks request counts per user per minute using a simple sliding window.
    Does NOT block requests — only logs warnings when thresholds are exceeded.
    """

    def __init__(self, rpm_limit: int = 60):
        self.rpm_limit = rpm_limit
        # {user_email: [(timestamp, ...), ...]}
        self._windows: dict[str, list[float]] = {}

    def track(self, user_email: str) -> bool:
        """
        Record a request. Returns True if the user exceeded the RPM limit.
        """
        if not user_email:
            return False

        now = time.time()
        window = self._windows.setdefault(user_email, [])

        # Prune entries older than 60 seconds
        cutoff = now - 60.0
        self._windows[user_email] = [t for t in window if t > cutoff]
        window = self._windows[user_email]

        window.append(now)
        return len(window) > self.rpm_limit


# ── Public API ────────────────────────────────────────────────────────────────

# Detect Cloud Run environment
_IS_CLOUD_RUN = bool(os.environ.get("K_SERVICE") or os.environ.get("CLOUD_RUN"))

# Configurable log level (default INFO)
_LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

# Module-level tracker instance
rate_tracker = RateLimitTracker(
    rpm_limit=int(os.environ.get("RATE_LIMIT_RPM", "60"))
)


def get_logger(name: str) -> logging.Logger:
    """
    Create or retrieve a named logger with the correct formatter.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(_LOG_LEVEL)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(_LOG_LEVEL)

    if _IS_CLOUD_RUN:
        handler.setFormatter(CloudJSONFormatter())
    else:
        handler.setFormatter(ReadableFormatter())

    logger.addHandler(handler)
    return logger


def generate_request_id() -> str:
    """Generate a unique request ID (UUID4 hex, 32 chars)."""
    return uuid.uuid4().hex
