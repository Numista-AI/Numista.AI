"""
agent_config.py — Numista.AI Desktop Agent Configuration
=========================================================
Reads and writes %APPDATA%\\NumistaAI\\config.json so the agent is
not tied to any single user's email address.

Usage
-----
    from agent_config import AgentConfig

    cfg = AgentConfig()
    if not cfg.is_configured():
        # Launch setup wizard before starting agent
        ...
    email = cfg.get_user_email()
"""

import json
import os
import logging
from pathlib import Path

_CONFIG_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "NumistaAI"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

_DEFAULT = {
    "user_email": "",
    "device_name": "",
    "configured": False,
}


class AgentConfig:
    """Singleton-safe config manager backed by a JSON file."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = None
        return cls._instance

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if self._data is not None:
            return self._data
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._data = {**_DEFAULT, **json.load(f)}
                logging.info(f"[CONFIG] Loaded from {_CONFIG_FILE}")
                return self._data
            except Exception as e:
                logging.warning(f"[CONFIG] Failed to read config ({e}) — using defaults")
        self._data = dict(_DEFAULT)
        return self._data

    def save(self) -> None:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        logging.info(f"[CONFIG] Saved to {_CONFIG_FILE}")

    def reload(self) -> None:
        """Force a re-read from disk (e.g. after wizard writes config)."""
        self._data = None
        self._load()

    # ─── Accessors ────────────────────────────────────────────────────────────

    def is_configured(self) -> bool:
        data = self._load()
        return bool(data.get("configured")) and bool(data.get("user_email"))

    def get_user_email(self) -> str:
        return self._load().get("user_email", "")

    def get_device_name(self) -> str:
        return self._load().get("device_name", "My Computer")

    # ─── Mutators ─────────────────────────────────────────────────────────────

    def set_user(self, email: str, device_name: str = "") -> None:
        data = self._load()
        data["user_email"]  = email.strip()
        data["device_name"] = device_name.strip() or "My Computer"
        data["configured"]  = True
        self._data = data
        self.save()

    # ─── Paths ────────────────────────────────────────────────────────────────

    @staticmethod
    def get_log_path() -> Path:
        log_dir = _CONFIG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / "numista_agent.log"

    @staticmethod
    def get_config_dir() -> Path:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        return _CONFIG_DIR
