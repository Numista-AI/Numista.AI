"""Regression tests for GET /api/reference/search against an isolated copy of numista_coins.db."""

from __future__ import annotations

import logging
import shutil
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main as backend_main


@pytest.fixture()
def isolated_reference_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Copy numista_coins.db to tmp_path and isolate DB_PATH, auth, and schema cache per test."""
    src_db = Path(backend_main.DB_PATH)
    assert src_db.exists(), f"Expected SQLite catalog at {src_db}"

    db_copy = tmp_path / "numista_coins.db"
    shutil.copy2(src_db, db_copy)

    monkeypatch.setattr(backend_main, "DB_PATH", str(db_copy))
    monkeypatch.setattr(backend_main, "_get_user_owned_doc_ids", lambda _email: set())
    backend_main._get_definitive_reference_select_clause.cache_clear()

    prev_override = backend_main.app.dependency_overrides.get(backend_main.get_current_user)
    backend_main.app.dependency_overrides[backend_main.get_current_user] = (
        lambda: {"email": "test@example.com"}
    )
    try:
        yield db_copy
    finally:
        if prev_override is None:
            backend_main.app.dependency_overrides.pop(backend_main.get_current_user, None)
        else:
            backend_main.app.dependency_overrides[backend_main.get_current_user] = prev_override
        backend_main._get_definitive_reference_select_clause.cache_clear()


def test_reference_search_empty_query_against_real_db_copy(isolated_reference_db: Path) -> None:
    """Empty query against the 12-column DB copy returns HTTP 200 with defaulted optional fields."""
    client = TestClient(backend_main.app)
    resp = client.get("/api/reference/search?q=&page_size=10&offset=0&sort_by=year")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["total"] > 0
    assert len(payload["results"]) == 10
    first = payload["results"][0]
    assert first["image_url_obverse"] == ""
    assert first["image_url_reverse"] == ""
    assert first["price_guide"] == ""
    assert first["population_total"] == 0
    assert first["apr_history"] == ""


def test_reference_search_keyword_and_alphabetical_sort_against_real_db_copy(
    isolated_reference_db: Path,
) -> None:
    """Keyword + alphabetical sort returns HTTP 200 and matching rows from the copied DB."""
    client = TestClient(backend_main.app)
    resp = client.get("/api/reference/search?q=morgan&page_size=5&offset=0&sort_by=alphabetical")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["total"] > 0
    assert 0 < len(payload["results"]) <= 5


def test_reference_search_with_migrated_optional_columns_on_copy(
    isolated_reference_db: Path,
) -> None:
    """When optional enrichment columns exist on the DB, real values are returned."""
    conn = sqlite3.connect(str(isolated_reference_db))
    try:
        cur = conn.cursor()
        cur.execute("ALTER TABLE definitive_reference ADD COLUMN image_url_obverse TEXT;")
        cur.execute("ALTER TABLE definitive_reference ADD COLUMN image_url_reverse TEXT;")
        cur.execute("ALTER TABLE definitive_reference ADD COLUMN price_guide TEXT;")
        cur.execute("ALTER TABLE definitive_reference ADD COLUMN population_total INTEGER;")
        cur.execute("ALTER TABLE definitive_reference ADD COLUMN apr_history TEXT;")

        cur.execute(
            "SELECT doc_id FROM definitive_reference "
            "WHERE LOWER(variety) LIKE '%morgan%' "
            "ORDER BY CASE WHEN year = '' THEN 0 ELSE 1 END, year ASC, variety ASC "
            "LIMIT 1"
        )
        row = cur.fetchone()
        assert row is not None
        target_doc_id = row[0]

        cur.execute(
            """
            UPDATE definitive_reference
            SET image_url_obverse = ?,
                image_url_reverse = ?,
                price_guide = ?,
                population_total = ?,
                apr_history = ?
            WHERE doc_id = ?
            """,
            (
                "https://example.com/obv.jpg",
                "https://example.com/rev.jpg",
                "$125",
                42,
                "2026-01: $130",
                target_doc_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    backend_main._get_definitive_reference_select_clause.cache_clear()
    client = TestClient(backend_main.app)
    resp = client.get("/api/reference/search?q=morgan&page_size=25&offset=0&sort_by=year")

    assert resp.status_code == 200
    matches = [r for r in resp.json()["results"] if r["doc_id"] == target_doc_id]
    assert len(matches) == 1
    item = matches[0]
    assert item["image_url_obverse"] == "https://example.com/obv.jpg"
    assert item["image_url_reverse"] == "https://example.com/rev.jpg"
    assert item["image_url"] == "https://example.com/obv.jpg"
    assert item["price_guide"] == "$125"
    assert item["population_total"] == 42
    assert item["apr_history"] == "2026-01: $130"


def test_reference_search_logs_traceback_and_returns_friendly_error(
    isolated_reference_db: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """SQLite errors log full traceback without PII and return a friendly HTTP 500 detail."""
    conn = sqlite3.connect(str(isolated_reference_db))
    try:
        conn.execute("DROP TABLE definitive_reference")
        conn.commit()
    finally:
        conn.close()

    backend_main._get_definitive_reference_select_clause.cache_clear()
    client = TestClient(backend_main.app)
    with caplog.at_level(logging.ERROR, logger=backend_main.logger.name):
        resp = client.get("/api/reference/search?q=morgan&page_size=5&offset=0")

    assert resp.status_code == 500
    detail = resp.json()["detail"]
    assert detail == "Search is temporarily unavailable. Please try again."
    assert "no such table" not in detail.lower()
    assert "GET /api/reference/search failed" in caplog.text
    assert "OperationalError" in caplog.text
    assert "test@example.com" not in caplog.text
