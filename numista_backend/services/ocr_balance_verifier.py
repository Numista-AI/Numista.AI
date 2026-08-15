"""
OCR Balance and Structural Verifier (Generate-and-Select Pattern)
Validates Document AI and Gemini OCR extractions of invoices, receipts, and checklists
using deterministic mathematical reconciliation and regex constraints.
"""

from typing import Dict, Any, List, Optional
import re


def parse_currency(val: Any) -> float:
    """Safely parses a currency string or number to float."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    # Strip $, commas, whitespace
    cleaned = re.sub(r'[^\d.-]', '', str(val).strip())
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def verify_invoice_extraction(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconciles line items, tax, shipping, and grand total from an OCR invoice extraction.
    
    Returns:
        {
            "is_balanced": bool,
            "calculated_total": float,
            "stated_total": float,
            "delta": float,
            "errors": list[str],
            "warnings": list[str],
            "feedback_prompt": Optional[str]
        }
    """
    errors: List[str] = []
    warnings: List[str] = []

    stated_total = parse_currency(extraction.get("total") or extraction.get("grand_total") or extraction.get("total_amount"))
    subtotal = parse_currency(extraction.get("subtotal"))
    tax = parse_currency(extraction.get("tax") or extraction.get("sales_tax"))
    shipping = parse_currency(extraction.get("shipping") or extraction.get("postage"))

    raw_items = extraction.get("items") or extraction.get("line_items") or []
    calculated_line_sum = 0.0

    if not isinstance(raw_items, list):
        errors.append("Expected 'items' or 'line_items' to be an array of objects.")
        raw_items = []

    for idx, item in enumerate(raw_items, 1):
        if not isinstance(item, dict):
            continue
        desc = item.get("description") or item.get("title") or item.get("coin_name") or ""
        price = parse_currency(item.get("price") or item.get("unit_price") or item.get("amount") or item.get("total"))
        qty = float(item.get("quantity") or item.get("qty") or 1)
        line_total = price * qty
        calculated_line_sum += line_total

        # Check year in description
        year_match = re.search(r'\b(1[789]\d{2}|20[0-2]\d)\b', desc)
        if year_match:
            year_val = int(year_match.group(1))
            if year_val < 1792 or year_val > 2026:
                warnings.append(f"Line {idx}: Unlikely coin year '{year_val}' in description '{desc}'.")

    # Reconcile totals
    # Case A: Grand total vs (Subtotal + Tax + Shipping)
    if subtotal > 0:
        expected_grand = subtotal + tax + shipping
        delta_sub = abs(expected_grand - stated_total)
        if delta_sub > 0.05 and stated_total > 0:
            errors.append(
                f"Subtotal reconciliation mismatch: Subtotal (${subtotal:.2f}) + Tax (${tax:.2f}) + Shipping (${shipping:.2f}) "
                f"= ${expected_grand:.2f}, but stated Grand Total is ${stated_total:.2f} (diff: ${delta_sub:.2f})."
            )

    # Case B: Line items sum vs Subtotal / Grand Total
    reference_target = subtotal if subtotal > 0 else (stated_total - tax - shipping if stated_total > 0 else 0)
    delta_lines = 0.0
    if reference_target > 0 and calculated_line_sum > 0:
        delta_lines = abs(calculated_line_sum - reference_target)
        if delta_lines > 0.05:
            errors.append(
                f"Line item sum mismatch: Sum of {len(raw_items)} line items is ${calculated_line_sum:.2f}, "
                f"but target total is ${reference_target:.2f} (diff: ${delta_lines:.2f})."
            )

    is_balanced = (len(errors) == 0) and (stated_total > 0 or calculated_line_sum > 0)

    feedback_prompt = None
    if not is_balanced and errors:
        feedback_prompt = (
            f"RECONCILIATION ERROR: The extracted OCR table does not mathematically balance.\n"
            f"- Extracted Line Sum: ${calculated_line_sum:.2f}\n"
            f"- Extracted Stated Total: ${stated_total:.2f}\n"
            f"- Discrepancy details: {'; '.join(errors)}\n"
            f"Please re-examine the document image. Look for missed line items, OCR misread decimal points, or shipping/discount rows."
        )

    return {
        "is_balanced": is_balanced,
        "calculated_total": round(calculated_line_sum, 2),
        "stated_total": round(stated_total, 2),
        "delta": round(delta_lines, 2),
        "errors": errors,
        "warnings": warnings,
        "feedback_prompt": feedback_prompt
    }
