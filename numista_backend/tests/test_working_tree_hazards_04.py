"""Regression suite for Track #4: Working-Tree Hazards & Test Runner Unblocking (W4-01..W4-05)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _TESTS_DIR.parent
_REPO_ROOT = _BACKEND_DIR.parent

import stripe_config
from scripts import enrich_catalog


# Note: stripe_config._safe_load_dotenv() already ran at import time against the real .env.
# Passing an explicit dotenv_path= overrides that and isolates the test to the tmp file.
def test_safe_load_dotenv_cp1252_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """W4-01: _safe_load_dotenv decodes a cp1252 .env (byte 0x97) without UnicodeDecodeError."""
    env_file = tmp_path / ".env"
    env_file.write_bytes(
        b"# Windows-1252 comment with em-dash \x97 in header\r\n"
        b"W4_TEST_CP1252_KEY=cp1252_ok_value\r\n"
    )
    monkeypatch.delenv("W4_TEST_CP1252_KEY", raising=False)

    loaded = stripe_config._safe_load_dotenv(dotenv_path=env_file)
    assert loaded is True
    assert os.environ.get("W4_TEST_CP1252_KEY") == "cp1252_ok_value"


def test_safe_load_dotenv_utf8_bom(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """W4-01: _safe_load_dotenv strips UTF-8 BOM (utf-8-sig) from the first key."""
    env_file = tmp_path / ".env"
    env_file.write_bytes(b"\xef\xbb\xbfW4_TEST_BOM_KEY=bom_ok_value\n")
    monkeypatch.delenv("W4_TEST_BOM_KEY", raising=False)

    loaded = stripe_config._safe_load_dotenv(dotenv_path=env_file)
    assert loaded is True
    assert os.environ.get("W4_TEST_BOM_KEY") == "bom_ok_value"
    assert "\ufeffW4_TEST_BOM_KEY" not in os.environ


def test_conftest_sys_path_and_no_root_main() -> None:
    """W4-02: numista_backend precedes repo root on sys.path, root main.py is absent, and 'import main' resolves to numista_backend/main.py."""
    assert not (_REPO_ROOT / "main.py").exists(), "Untracked root main.py must not exist"

    norm_paths = [os.path.normcase(os.path.abspath(p)) for p in sys.path if p]
    backend_norm = os.path.normcase(str(_BACKEND_DIR))
    root_norm = os.path.normcase(str(_REPO_ROOT))

    assert backend_norm in norm_paths, "numista_backend must be in sys.path"
    if root_norm in norm_paths:
        assert norm_paths.index(backend_norm) < norm_paths.index(root_norm), (
            "numista_backend must precede repo root in sys.path"
        )

    import main as resolved_main

    assert Path(resolved_main.__file__).resolve() == (_BACKEND_DIR / "main.py").resolve()


def test_enrich_catalog_mint_and_token_guards() -> None:
    """W4-05: enrich_catalog rejects initials/tokens and supports hyphenated/parenthesized US + Philippines M marks."""
    # False-positive id=6460 case: '1839 W. Scott' must NOT parse 'W' as West Point mint mark
    year, mm = enrich_catalog.parse_year_and_mint(
        "Hard Times Token - 1839 W. Scott (Pittsburgh, PA; Counterstamped on a Mexico 1800 2 Reales)",
        issuer="United States",
    )
    assert (year, mm) == ("1839", "")
    assert enrich_catalog.is_excluded_non_coin(
        "Hard Times Token - 1839 W. Scott (Pittsburgh, PA)", category="quarter"
    ) is True

    # False-positive id=6461 case: Civil War token overstruck on 1838-O Dime
    assert enrich_catalog.is_excluded_non_coin(
        "10 Cents - Civil War Patriotic Token - Overstruck on 1838-O Dime", category="dollar"
    ) is True

    # Charlotte 'C' mint mark supported
    assert enrich_catalog.parse_year_and_mint("1849-C Gold Dollar", issuer="United States") == ("1849", "C")

    # Parenthesized mint mark supported
    assert enrich_catalog.parse_year_and_mint("1921 (P) Morgan Silver Dollar", issuer="United States") == ("1921", "P")

    # Manila 'M' allowed for Philippines, rejected for mainland United States
    assert enrich_catalog.parse_year_and_mint("1944-M 50 Centavos", issuer="Philippines") == ("1944", "M")
    assert enrich_catalog.parse_year_and_mint("1944-M 50 Centavos", issuer="United States") == ("1944", "")
