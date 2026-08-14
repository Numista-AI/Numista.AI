"""
Numista.AI Checklist & Handwritten Notes Parser Service
Deterministic 2-stage parsing pipeline (Regex Tokenizer + LLM Fallback)
Extracts storage_location, condition, quantity, is_owned, and personal_notes.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("numista_backend.checklist_parser")

def slugify_theme(theme_raw: str) -> str:
    """
    4-step deterministic theme slugification algorithm for canonical reference image keys:
    1. Lowercase and strip whitespace.
    2. Strip parenthetical state/territory codes (e.g. 'Hot Springs (AR)' -> 'Hot Springs').
    3. Strip non-alphanumeric characters and common variable suffixes.
    4. Collapse whitespace into single underscore.
    """
    if not theme_raw:
        return "unknown"
    s = theme_raw.lower().strip()
    # 2. Strip parenthetical content
    s = re.sub(r"\(.*?\)", "", s).strip()
    # 3. Strip variable park/memorial suffixes
    s = re.sub(r"\b(national park & preserve|national park and preserve|national park|national historic site|national monument|national historical park|national forest|national memorial|state park)\b", "", s).strip()
    # Strip non-alphanumeric except whitespace and hyphens
    s = re.sub(r"[^\w\s-]", "", s)
    # 4. Collapse whitespace to single underscore
    slug = re.sub(r"[\s-]+", "_", s).strip("_")
    return slug or "unknown"


def parse_checklist_notes(raw_notes: Optional[str]) -> Dict[str, Any]:
    """
    Parses checklist 'Notes / QTY / Location' annotations into canonical schema fields.

    Ownership & Quantity Rules:
    - Empty notes on checked rows -> is_owned = True, quantity = 1, condition = 'Unspecified / Raw', storage_location = ''
    - Explicit zero ('Already have 0', '0') -> is_owned = False, quantity = 0, personal_notes = raw_notes
    - Multiples ('QTY: 3', 'x2') -> is_owned = True, quantity = N
    - Locations ('ATB-P tube', 'Box 2') -> storage_location
    - Conditions ('MS65', 'Proof', 'BU') -> condition
    """
    if not raw_notes or not raw_notes.strip():
        return {
            "storage_location": "",
            "condition": "Unspecified / Raw",
            "quantity": 1,
            "is_owned": True,
            "personal_notes": "",
            "confidence_score": 1.0,
            "flag": None,
        }

    text = raw_notes.strip()

    # Rule 1: Explicit Zero Ownership check ("Already have 0", "Have 0", "0")
    if re.fullmatch(r"(?i)\s*(?:already\s+have\s+0|have\s+0|0|none|qty\s*[:=]?\s*0)\s*", text):
        return {
            "storage_location": "",
            "condition": "Unspecified / Raw",
            "quantity": 0,
            "is_owned": False,
            "personal_notes": text,
            "confidence_score": 1.0,
            "flag": "unselected_zero_ownership",
        }

    storage_location = ""
    condition = "Unspecified / Raw"
    quantity = 1
    is_owned = True
    personal_notes_parts = []
    confidence = 1.0
    flag = None

    # Check Specific Sheldon grades first (e.g. MS65, PR70, AU58)
    num_grade = re.search(r"(?i)\b(ms\s*\d{2}|pr\s*\d{2}|pf\s*\d{2}|au\s*\d{2}|xf\s*\d{2}|vf\s*\d{2})\b", text)
    if num_grade:
        condition = num_grade.group(1).upper().replace(" ", "")
    elif re.search(r"(?i)\bproof\b", text):
        condition = "Proof"
    elif re.search(r"(?i)\b(?:unc|uncirculated|bu)\b", text):
        condition = "Uncirculated"
    elif re.search(r"(?i)\bcirculated\b", text):
        condition = "Circulated"

    # Rule 2: Extract Quantity (e.g. "QTY: 3", "qty=2", "x3", "#2")
    qty_match = re.search(r"(?i)\b(?:qty|quantity|x|\#)\s*[:=]?\s*(\d+)\b", text)
    if qty_match:
        try:
            quantity = int(qty_match.group(1))
            text = (text[:qty_match.start()] + text[qty_match.end():]).strip()
        except ValueError:
            pass

    # Rule 3: Extract Storage Locations
    loc_match = re.search(r"(?i)\b(atb\s*-[pd]\s*tube|tube|safe\s*box\s*\w+|safe|box\s*\w+|dansco\s*album(?:\s*p\.?\s*\d+)?|unc\s*roll|proof\s*set\s*box|2x2\s*box\s*\w+|2x2|capsule|slab|binder\s*\d*)\b", text)
    if loc_match:
        raw_loc = loc_match.group(0).strip()
        # Clean up spacing like "ATB -D tube" -> "ATB-D tube"
        norm_loc = re.sub(r"(?i)atb\s*-\s*([pd])\s*tube", r"ATB-\1 tube", raw_loc)
        if re.match(r"(?i)2x2\s+box\s*(\w+)", norm_loc):
            b_num = re.search(r"(?i)box\s*(\w+)", norm_loc).group(0)
            storage_location = b_num.title()
            personal_notes_parts.append("2x2")
        elif norm_loc.lower() == "2x2":
            personal_notes_parts.append("2x2")
        elif norm_loc.lower() == "unc roll":
            storage_location = "UNC Roll"
        elif "proof set" in norm_loc.lower():
            storage_location = norm_loc.title()
        elif "tube" in norm_loc.lower():
            storage_location = norm_loc
        elif "box" in norm_loc.lower() or "safe" in norm_loc.lower():
            storage_location = norm_loc.title()
        elif "album" in norm_loc.lower():
            storage_location = norm_loc
        else:
            storage_location = norm_loc.title()

        text = (text[:loc_match.start()] + text[loc_match.end():]).strip()

    # Rule 4: Clean up additional notes
    full_note_match = re.search(r"(?i)\b(\d{2}\s+Proof\s+Condition)\b", text)
    if full_note_match:
        personal_notes_parts.append(full_note_match.group(1))
        text = (text[:full_note_match.start()] + text[full_note_match.end():]).strip()

    if num_grade:
        text = (text[:num_grade.start()] + text[num_grade.end():]).strip()

    # Specific BU / grade tags
    bu_match = re.search(r"(?i)\bbu\b", text)
    if bu_match:
        personal_notes_parts.append("BU")
        text = (text[:bu_match.start()] + text[bu_match.end():]).strip()

    remaining = re.sub(r"^[\s,–\-—|:]+|[\s,–\-—|:]+$", "", text).strip()
    if remaining:
        if re.search(r"[^\x20-\x7E]", remaining) or len(remaining) > 40:
            confidence = 0.80
            flag = "needs_note_review"
        personal_notes_parts.append(remaining)

    personal_notes = ", ".join(personal_notes_parts)

    return {
        "storage_location": storage_location,
        "condition": condition,
        "quantity": quantity,
        "is_owned": is_owned,
        "personal_notes": personal_notes,
        "confidence_score": confidence,
        "flag": flag,
    }
