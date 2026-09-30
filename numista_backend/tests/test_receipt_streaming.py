"""
test_receipt_streaming.py
-------------------------
Regression and unit tests for REQ_019:
- View Scan for Paper Trail receipts must stream actual PDF and JPG/PNG documents
- Dynamic MIME detection from magic bytes, extension, and GCS metadata
- Proper Content-Type ('image/jpeg', 'application/pdf', 'image/png')
- Prevents PDF viewer blank white page on image receipts
- User isolation security enforcement
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import (
    app,
    _detect_receipt_mime,
    _get_receipt_metadata,
)

client = TestClient(app)


def test_detect_receipt_mime_magic_bytes():
    """Verify magic bytes accurately identify MIME types regardless of filename."""
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    jpg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01"
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    webp_bytes = b"RIFF\x1a\x00\x00\x00WEBPVP8 "
    gif_bytes = b"GIF89a\x01\x00\x01\x00"

    assert _detect_receipt_mime(pdf_bytes, "scan.unknown")[0] == "application/pdf"
    assert _detect_receipt_mime(jpg_bytes, "scan.unknown")[0] == "image/jpeg"
    assert _detect_receipt_mime(png_bytes, "scan.unknown")[0] == "image/png"
    assert _detect_receipt_mime(webp_bytes, "scan.unknown")[0] == "image/webp"
    assert _detect_receipt_mime(gif_bytes, "scan.unknown")[0] == "image/gif"


def test_detect_receipt_mime_fallback_extension():
    """Verify extension fallback when raw bytes do not start with standard magic bytes."""
    dummy_bytes = b"raw text bytes"
    assert _detect_receipt_mime(dummy_bytes, "invoice.jpg") == ("image/jpeg", "jpg")
    assert _detect_receipt_mime(dummy_bytes, "invoice.png") == ("image/png", "png")
    assert _detect_receipt_mime(dummy_bytes, "invoice.pdf") == ("application/pdf", "pdf")
    assert _detect_receipt_mime(dummy_bytes, "invoice.webp") == ("image/webp", "webp")


def test_receipt_view_url_jpg_and_pdf(monkeypatch):
    """Verify receipt_view_url accurately reflects filename and file_type for both JPG and PDF."""
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email: email)

    mock_db = MagicMock()
    user_ref = MagicMock()

    mock_rec_jpg = MagicMock()
    mock_rec_jpg.exists = True
    mock_rec_jpg.to_dict.return_value = {
        "original_filename": "store_receipt.jpg",
        "gcs_path": "receipts/tester@numista.ai/rec_jpg/original.jpg",
    }

    mock_rec_pdf = MagicMock()
    mock_rec_pdf.exists = True
    mock_rec_pdf.to_dict.return_value = {
        "original_filename": "invoice_doc.pdf",
        "gcs_path": "gs://test-bucket/tester@numista.ai/imports/rec_pdf.pdf",
    }

    def _doc_router(doc_id):
        m = MagicMock()
        if doc_id == "rec_jpg":
            m.get.return_value = mock_rec_jpg
        elif doc_id == "rec_pdf":
            m.get.return_value = mock_rec_pdf
        else:
            empty = MagicMock()
            empty.exists = False
            m.get.return_value = empty
        return m

    user_ref.collection.return_value.document.side_effect = _doc_router
    mock_db.collection.return_value.document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    # 1. Test JPG view_url
    resp_jpg = client.get("/api/receipts/tester@numista.ai/rec_jpg/view_url", headers={"Authorization": "Bearer test-token"})
    assert resp_jpg.status_code == 200
    data_jpg = resp_jpg.json()
    assert data_jpg["receipt_id"] == "rec_jpg"
    assert data_jpg["file_type"] == "jpg"
    assert data_jpg["filename"] == "store_receipt.jpg"
    assert "/api/receipts/tester@numista.ai/rec_jpg/stream" in data_jpg["signed_url"]

    # 2. Test PDF view_url
    resp_pdf = client.get("/api/receipts/tester@numista.ai/rec_pdf/view_url", headers={"Authorization": "Bearer test-token"})
    assert resp_pdf.status_code == 200
    data_pdf = resp_pdf.json()
    assert data_pdf["receipt_id"] == "rec_pdf"
    assert data_pdf["file_type"] == "pdf"
    assert data_pdf["filename"] == "invoice_doc.pdf"
    assert "/api/receipts/tester@numista.ai/rec_pdf/stream" in data_pdf["signed_url"]


def test_receipt_stream_jpeg_serves_image_jpeg(monkeypatch):
    """Verify streaming a JPG receipt serves image/jpeg MIME type, resolving blank white page."""
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email: email)

    mock_db = MagicMock()
    user_ref = MagicMock()
    rec_doc = MagicMock()
    rec_doc.exists = True
    rec_doc.to_dict.return_value = {
        "original_filename": "receipt_photo.jpg",
        "gcs_path": "receipts/tester@numista.ai/rec_jpg_123/original.jpg",
    }
    user_ref.collection.return_value.document.return_value.get.return_value = rec_doc
    mock_db.collection.return_value.document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    # Mock GCS Client
    mock_gcs = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    fake_jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x60\x00\x60\x00\x00"
    mock_blob.download_as_bytes.return_value = fake_jpeg_bytes
    mock_blob.content_type = "image/jpeg"
    mock_blob.name = "receipts/tester@numista.ai/rec_jpg_123/original.jpg"
    mock_bucket.blob.return_value = mock_blob
    mock_gcs.bucket.return_value = mock_bucket
    monkeypatch.setattr(main, "gcs_client", mock_gcs)
    monkeypatch.setattr(main, "IMPORT_BUCKET", "test-bucket")

    # Stream request with query token
    resp = client.get("/api/receipts/tester@numista.ai/rec_jpg_123/stream?token=test_token")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"
    assert 'inline; filename="receipt_photo.jpg"' in resp.headers["content-disposition"]
    assert resp.content == fake_jpeg_bytes


def test_receipt_stream_pdf_serves_application_pdf(monkeypatch):
    """Verify streaming a PDF receipt serves application/pdf MIME type."""
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email: email)

    mock_db = MagicMock()
    user_ref = MagicMock()
    rec_doc = MagicMock()
    rec_doc.exists = True
    rec_doc.to_dict.return_value = {
        "original_filename": "invoice.pdf",
        "gcs_path": "gs://test-bucket/tester@numista.ai/imports/invoice.pdf",
    }
    user_ref.collection.return_value.document.return_value.get.return_value = rec_doc
    mock_db.collection.return_value.document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    # Mock GCS Client
    mock_gcs = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    fake_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    mock_blob.download_as_bytes.return_value = fake_pdf_bytes
    mock_blob.content_type = "application/pdf"
    mock_blob.name = "tester@numista.ai/imports/invoice.pdf"
    mock_bucket.blob.return_value = mock_blob
    mock_gcs.bucket.return_value = mock_bucket
    monkeypatch.setattr(main, "gcs_client", mock_gcs)
    monkeypatch.setattr(main, "IMPORT_BUCKET", "test-bucket")

    resp = client.get("/api/receipts/tester@numista.ai/rec_pdf_456/stream", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert 'inline; filename="invoice.pdf"' in resp.headers["content-disposition"]
    assert resp.content == fake_pdf_bytes


def test_receipt_stream_user_isolation(monkeypatch):
    """Verify access denied (403) when attempting to stream a blob outside the user's folder."""
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email: email)

    mock_db = MagicMock()
    user_ref = MagicMock()
    rec_doc = MagicMock()
    rec_doc.exists = True
    rec_doc.to_dict.return_value = {
        "original_filename": "stolen_receipt.pdf",
        "gcs_path": "gs://test-bucket/victim@numista.ai/imports/stolen.pdf",
    }
    user_ref.collection.return_value.document.return_value.get.return_value = rec_doc
    mock_db.collection.return_value.document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    mock_gcs = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.download_as_bytes.return_value = b"%PDF-1.4..."
    mock_blob.name = "victim@numista.ai/imports/stolen.pdf"
    mock_bucket.blob.return_value = mock_blob
    mock_gcs.bucket.return_value = mock_bucket
    monkeypatch.setattr(main, "gcs_client", mock_gcs)

    resp = client.get("/api/receipts/tester@numista.ai/rec_stolen/stream", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 403
    assert "Access denied" in resp.json()["detail"]


def test_receipt_stream_not_found(monkeypatch):
    """Verify 404 returned when receipt or blob does not exist."""
    monkeypatch.setattr(main, "_authenticate_request", lambda auth, email: email)

    mock_db = MagicMock()
    user_ref = MagicMock()
    rec_doc = MagicMock()
    rec_doc.exists = False
    user_ref.collection.return_value.document.return_value.get.return_value = rec_doc
    user_ref.collection.return_value.where.return_value.limit.return_value.stream.return_value = []
    mock_db.collection.return_value.document.return_value = user_ref
    monkeypatch.setattr(main, "db", mock_db)

    mock_gcs = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.download_as_bytes.side_effect = Exception("Not found")
    mock_bucket.blob.return_value = mock_blob
    mock_gcs.bucket.return_value = mock_bucket
    monkeypatch.setattr(main, "gcs_client", mock_gcs)

    resp = client.get("/api/receipts/tester@numista.ai/rec_none/stream", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 404
