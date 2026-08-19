import pytest
import sys, os

# Add numista_backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'numista_backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.passport_pdf_generator import generate_passport_pdf, format_financial_details

def test_format_financial_details_dual_valuation():
    item = {
        "title": "2026 Dollar American Silver Eagle",
        "Year": "2026",
        "Denomination": "Dollar",
        "Quantity": 2,
        "purchaseCost": "70.00",
        "greysheetBid": "85.00",
        "cpgRetail": "110.00",
    }
    fin_html = format_financial_details(item)
    assert "<b>Qty:</b> 2" in fin_html
    assert "<b>Cost:</b> $70.00" in fin_html
    assert "<b>Wholesale (Bid):</b> $85.00" in fin_html
    assert "<b>Retail (CPG):</b> $110.00" in fin_html

def test_format_financial_details_ukn_cost_and_missing_guide():
    item = {
        "title": "1980 50 Fils",
        "Year": "1980",
        "Denomination": "50 Fils",
        "purchaseCost": "", # missing cost -> UKN
        "greysheetBid": None, # missing bid -> em-dash
        "cpgRetail": None,
    }
    fin_html = format_financial_details(item)
    assert "<b>Cost:</b> UKN" in fin_html
    assert "<b>Wholesale (Bid):</b> —" in fin_html
    assert "<b>Retail (CPG):</b> —" in fin_html

def test_generate_passport_pdf_success():
    transfer_data = {
        "transfer_id": "TX-TEST-2026",
        "claim_pin": "123456",
        "sender_id": "eric.seaman@yahoo.com",
        "created_at": "2026-08-19T09:30:00Z",
        "expires_at": "2026-10-19T09:30:00Z",
        "items": [
            {
                "title": "2026 American Silver Eagle",
                "Year": "2026",
                "Denomination": "Dollar",
                "Quantity": 1,
                "purchaseCost": "75.00",
                "greysheetBid": "85.00",
                "cpgRetail": "110.00",
            },
            {
                "title": "1921 Morgan Dollar",
                "Year": "1921",
                "Denomination": "Dollar",
                "Quantity": 1,
                "purchaseCost": "30.00",
                "greysheetBid": "38.00",
                "cpgRetail": "50.00",
            }
        ]
    }
    pdf_bytes = generate_passport_pdf(transfer_data)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b'%PDF')
