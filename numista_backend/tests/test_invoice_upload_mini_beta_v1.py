"""
Regression & acceptance tests for Invoice Upload Mini-Beta v1:
- Redacted 2-order US Mint 26RG fixture (zero PII)
- Non-pack-expanded unit_cost_cents idempotency (never divides $107.00 by qty=2 -> $54.75)
- Per-page PDF splitting & strict per-order isolation (shipping/fees/dates never bleed)
- Integer-cent largest-remainder per-unit fee allocation ([498, 497] for $9.95 / 2)
- Arithmetic sanity validator failing closed to Needs review (+/-1 cent)
"""

import io
import json
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from pypdf import PdfWriter

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main  # noqa: E402
from services.us_mint_catalog_service import enrich_us_mint_item  # noqa: E402
from tests.test_v8_18_15e_regression import (  # noqa: E402
    InMemoryFirestore,
    MockGCSBlob,
    MockGCSClient,
)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "redacted_usmint_two_order_26rg.json"


def _build_blank_two_page_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_redacted_fixture_has_zero_pii():
    raw_text = FIXTURE_PATH.read_text(encoding="utf-8")
    assert re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", raw_text) is None
    assert re.search(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", raw_text) is None
    assert re.search(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Ln|Blvd|Way|Ct)\b", raw_text) is None


def test_redacted_two_order_fixture_normalization_and_fee_isolation():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    rows = main.normalize_and_validate_receipt(payload, fname="redacted_two_orders.pdf")

    assert len(rows) == 2
    by_inv = {r["invoice_number"]: r for r in rows}
    assert set(by_inv.keys()) == {"USM25343756", "USM25258130"}

    r1 = by_inv["USM25343756"]
    assert r1["purchase_date"] == "2026-11-19"
    assert r1["Quantity"] == 2
    assert r1["Cost"] == 107.00
    assert r1["Purchase Cost"] == 107.00
    assert r1["unit_cost_cents"] == 10700
    assert r1["line_total"] == 214.00
    assert r1["line_total_cents"] == 21400
    assert r1["allocated_fees"] == 0.0
    assert r1["allocated_fee_cents"] == 0
    assert r1["allocated_fee_per_unit_cents"] == [0, 0]
    assert r1["math_check_passed"] is True
    assert r1["review_needed"] is False

    r2 = by_inv["USM25258130"]
    assert r2["purchase_date"] == "2026-11-18"
    assert r2["Quantity"] == 2
    assert r2["Cost"] == 107.00
    assert r2["Purchase Cost"] == 107.00
    assert r2["unit_cost_cents"] == 10700
    assert r2["line_total"] == 214.00
    assert r2["line_total_cents"] == 21400
    assert r2["allocated_fees"] == 9.95
    assert r2["shipping_fee"] == 9.95
    assert r2["allocated_fee_cents"] == 995
    assert r2["allocated_fee_per_unit_cents"] == [498, 497]
    assert sum(r2["allocated_fee_per_unit_cents"]) == 995
    assert r2["order_landed_total"] == 223.95
    assert r2["math_check_passed"] is True
    assert r2["review_needed"] is False


def test_enrich_26rg_preserves_unit_cost_and_is_idempotent():
    doc = {
        "Retailer Item No.": "26RG",
        "Quantity": 2,
        "Cost": 107.00,
        "unit_price": 107.00,
        "line_total": 214.00,
    }
    first = enrich_us_mint_item(doc)
    assert first["unit_cost_cents"] == 10700
    assert first["unit_cost"] == 107.00
    assert first["line_total_cents"] == 21400
    assert first["line_total"] == 214.00
    assert first["pricing_contract_version"] == "v2_unit_and_line"

    # Simulate commit-time re-enrichment (main.py:3663 / :3914) -> must NOT divide again!
    second = enrich_us_mint_item(first)
    assert second["unit_cost_cents"] == 10700
    assert second["unit_cost"] == 107.00
    assert second["line_total_cents"] == 21400
    assert second["line_total"] == 214.00


def test_multipage_pdf_worker_splits_pages_and_persists_isolated_orders():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    pdf_bytes = _build_blank_two_page_pdf()

    mock_db = InMemoryFirestore()
    user_email = "collector@example.com"
    session_id = "sess_two_order_26rg"
    fname = "redacted_26rg_2orders.pdf"
    blob_path = f"{user_email}/imports/{session_id}/raw/{fname}"

    mock_db.document(f"users/{user_email}/import_sessions/{session_id}").set({
        "session_id": session_id,
        "status": "processing",
        "per_file": [{"name": fname, "type": "pdf", "status": "queued"}],
    })

    resp_p1 = MagicMock()
    resp_p1.text = json.dumps(payload[0])
    resp_p2 = MagicMock()
    resp_p2.text = json.dumps(payload[1])
    mock_genai = MagicMock()
    mock_genai.models.generate_content.side_effect = [resp_p1, resp_p2]

    mock_gcs = MockGCSClient({blob_path: MockGCSBlob(content_bytes=pdf_bytes)})

    with patch.object(main, "db", mock_db), \
         patch.object(main, "gcs_client", mock_gcs), \
         patch.object(main, "genai_client", mock_genai), \
         patch.object(main, "classify_document_bytes", return_value={"document_type": "invoice"}):
        main._execute_import_process_worker(user_email, session_id, mask_pii=True)

    assert mock_genai.models.generate_content.call_count == 2

    receipt_paths = sorted(k for k in mock_db.store if k.startswith(f"users/{user_email}/receipts/"))
    assert receipt_paths == [
        f"users/{user_email}/receipts/rec_redacted_26rg_2orders_o1",
        f"users/{user_email}/receipts/rec_redacted_26rg_2orders_o2",
    ]
    rec1 = mock_db.store[receipt_paths[0]]
    rec2 = mock_db.store[receipt_paths[1]]
    assert rec1["invoice_number"] == "USM25343756"
    assert rec1["invoice_date"] == "2026-11-19"
    assert rec1["shipping_fee"] == 0.0
    assert rec1["total_amount"] == 214.00
    assert rec2["invoice_number"] == "USM25258130"
    assert rec2["invoice_date"] == "2026-11-18"
    assert rec2["shipping_fee"] == 9.95
    assert rec2["total_amount"] == 223.95

    queue_rows = [
        v for k, v in mock_db.store.items()
        if k.startswith(f"users/{user_email}/review_queue/")
    ]
    assert len(queue_rows) == 2
    q_by_inv = {q["invoice_number"]: q for q in queue_rows}
    assert q_by_inv["USM25343756"]["purchase_date"] == "2026-11-19"
    assert q_by_inv["USM25343756"]["allocated_fees"] == 0.0
    assert q_by_inv["USM25343756"]["unit_cost_cents"] == 10700
    assert q_by_inv["USM25258130"]["purchase_date"] == "2026-11-18"
    assert q_by_inv["USM25258130"]["allocated_fees"] == 9.95
    assert q_by_inv["USM25258130"]["unit_cost_cents"] == 10700

    sess = mock_db.store[f"users/{user_email}/import_sessions/{session_id}"]
    assert sess["status"] == "done"
    assert sess["summary"]["receipts_parsed"] == 2
    assert sess["summary"]["coins_identified"] == 4


def test_math_guard_flags_line_and_order_mismatches():
    # (a) Deliberate line mismatch: 2 x $54.75 != $214.00
    bad_line = {
        "retailer": "United States Mint",
        "invoice_number": "USM99990001",
        "invoice_date": "2026-11-18",
        "subtotal": 214.00,
        "shipping_fee": 0.00,
        "total_amount": 214.00,
        "line_items": [
            {
                "Program/Series": "Proof Sets",
                "Year": "2026",
                "unit_price": 54.75,
                "Cost": 54.75,
                "line_total": 214.00,
                "qty": 2,
                "item_number": "26RG",
            }
        ],
    }
    res_line = main.normalize_and_validate_receipt(bad_line)
    assert len(res_line) == 1
    assert res_line[0]["math_check_passed"] is False
    assert res_line[0]["review_needed"] is True
    assert res_line[0]["confidence_score"] <= 0.75
    assert "54.75" in res_line[0]["needs_review_reason"]

    # (b) Deliberate order total mismatch: $214.00 + $9.95 != $250.00
    bad_total = {
        "retailer": "United States Mint",
        "invoice_number": "USM99990002",
        "invoice_date": "2026-11-18",
        "subtotal": 214.00,
        "shipping_fee": 9.95,
        "total_amount": 250.00,
        "line_items": [
            {
                "Program/Series": "Proof Sets",
                "Year": "2026",
                "unit_price": 107.00,
                "Cost": 107.00,
                "line_total": 214.00,
                "qty": 2,
                "item_number": "26RG",
            }
        ],
    }
    res_total = main.normalize_and_validate_receipt(bad_total)
    assert len(res_total) == 1
    assert res_total[0]["math_check_passed"] is False
    assert res_total[0]["review_needed"] is True
    assert res_total[0]["confidence_score"] <= 0.75
    assert "250.00" in res_total[0]["needs_review_reason"]
