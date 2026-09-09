#!/usr/bin/env python3
"""
repair_26rj_ghosts.py
======================
Audits and repairs ghost USMC children in 2026 Uncirculated Coin Set (26RJ)
parent documents in Firestore.

Requirements & Operational Contract:
1. Uses google-cloud-firestore Python SDK.
2. Target Firestore Project: studio-9101802118-8c9a8.
3. Supports --dry-run (default), --execute, and --user <email> flags.
4. User collections live at: users/{email}/coins.

Safety Gates:
- --execute strictly refuses execution without explicit --user <email>.
- Never deletes any parent set document.
- Never deletes or prunes any entry where Denomination contains 'cent' (case-insensitive).
- All mutations are transaction-wrapped per parent document.
- Full before/after verification report suitable for audit log pasting.

Usage:
    python repair_26rj_ghosts.py                          # Default dry-run audit on eric.seaman@yahoo.com
    python repair_26rj_ghosts.py --dry-run --user eric.seaman@yahoo.com
    python repair_26rj_ghosts.py --execute --user eric.seaman@yahoo.com
"""

import argparse
from datetime import datetime, timezone
import io
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import google.auth
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from google.oauth2 import service_account

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS & CANONICAL DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ID = "studio-9101802118-8c9a8"
DEFAULT_USER = "eric.seaman@yahoo.com"
BACKUP_FIELD_NAME = "set_contents_backup_20260909"
RETAILER_ITEM_STAMP = "26RJ"

CANONICAL_COINS: List[Tuple[str, str]] = [
    ("1 Cent", "Lincoln Cent"),
    ("5 Cents", "Jefferson Nickel"),
    ("10 Cents", "Emerging Liberty Dime"),
    ("50 Cents", "Enduring Liberty Half Dollar"),
    ("25 Cents", "Semiquincentennial Quarter"),  # 5 designs
    ("1 Dollar", "Native American Dollar"),
]
CANONICAL_MINTS: List[str] = ["P", "D"]

USMC_PATTERNS: List[str] = [
    "marine",
    "usmc",
    "1775-2025",
    "1775~2025",
    "250 years",
    "honor, courage",
    "honor courage",
]

# ─────────────────────────────────────────────────────────────────────────────
# FIRESTORE CLIENT INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def get_firestore_client(project_id: str = PROJECT_ID) -> firestore.Client:
    """
    Initializes and returns a google-cloud-firestore Client, searching standard
    service account credential locations before falling back to default auth.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    workspace_dir = os.path.abspath(os.path.join(backend_dir, ".."))

    candidate_paths = [
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        os.path.join(backend_dir, "serviceAccountKey.json"),
        os.path.join(backend_dir, "serviceAccountKey.json.json"),
        os.path.join(script_dir, "serviceAccountKey.json"),
        os.path.join(script_dir, "serviceAccountKey.json.json"),
        os.path.join(workspace_dir, "serviceAccountKey.json"),
        os.path.join(workspace_dir, "serviceAccountKey.json.json"),
    ]

    for path in candidate_paths:
        if path and os.path.isfile(path):
            try:
                creds = service_account.Credentials.from_service_account_file(path)
                return firestore.Client(project=project_id, credentials=creds)
            except Exception as ex:
                print(f"[WARN] Failed loading credentials from {path}: {ex}")

    # Fallback to Application Default Credentials
    try:
        creds, _ = google.auth.default()
        return firestore.Client(project=project_id, credentials=creds)
    except Exception:
        # Final fallback: bare project initialization
        return firestore.Client(project=project_id)


# ─────────────────────────────────────────────────────────────────────────────
# NUMISMATIC & GHOST CLASSIFICATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def is_cent_entry(denomination: Any) -> bool:
    """
    Safety Rule: Checks if denomination contains 'cent' (case-insensitive)
    representing 1-cent coins (e.g. '1 Cent', 'Cent', 'One Cent', 'Lincoln Cent', 'Penny').
    Strictly protects all 1-cent entries from deletion or pruning.
    Multi-cent denominations (5 Cents, 10 Cents, 25 Cents, 50 Cents) represent
    nickels, dimes, quarters, and half dollars.
    """
    denom_lower = str(denomination or "").strip().lower()
    if not denom_lower:
        return False
    # Multi-cent denominations are nickels, dimes, quarters, and half dollars
    if any(prefix in denom_lower for prefix in ["5 ", "5c", "10 ", "10c", "25 ", "25c", "50 ", "50c", "half", "quarter", "nickel", "dime"]):
        return False
    return "cent" in denom_lower or "penny" in denom_lower or denom_lower in ["1c", "0.01", "one cent"]


def extract_mint_mark(mint_val: Any, text_context: str = "") -> Optional[str]:
    """
    Extracts canonical mint mark ('P' or 'D') from mint mark field or text context.
    """
    m = str(mint_val or "").strip().upper()
    if m in ["P", "D"]:
        return m
    ctx = text_context.lower()
    if "(p)" in ctx or "-p" in ctx or "philadelphia" in ctx or " 2026 p" in ctx or " 2026-p" in ctx:
        return "P"
    if "(d)" in ctx or "-d" in ctx or "denver" in ctx or " 2026 d" in ctx or " 2026-d" in ctx:
        return "D"
    return None


def get_canonical_denomination_category(denomination: str, theme: str = "") -> Optional[str]:
    """
    Maps denomination and theme to one of the 6 canonical 26RJ coin types:
    '1 Cent', '5 Cents', '10 Cents', '25 Cents', '50 Cents', '1 Dollar'.
    Returns None if not matching canonical 26RJ series.
    """
    d = denomination.strip().lower()
    t = theme.strip().lower()

    if is_cent_entry(d) or "lincoln" in t:
        return "1 Cent"
    if "5 cent" in d or "five cent" in d or "nickel" in d or "5c" in d or "0.05" in d:
        return "5 Cents"
    if "10 cent" in d or "one dime" in d or "dime" in d or "10c" in d or "0.10" in d:
        return "10 Cents"
    if "25 cent" in d or "quarter" in d or "25c" in d or "0.25" in d:
        return "25 Cents"
    if "50 cent" in d or "half dollar" in d or "half" in d or "50c" in d or "0.50" in d:
        return "50 Cents"
    if ("dollar" in d or "$1" in d or "one dollar" in d) and "half" not in d and "quarter" not in d:
        return "1 Dollar"

    return None


def evaluate_ghost(
    denomination: Any,
    theme: Any,
    name: Any = "",
    program: Any = "",
    doc_id: Optional[str] = None,
    parent_doc_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Evaluates an entry or child document against safety rules, USMC ghost patterns,
    and canonical 20-coin set specifications.

    Returns:
        (is_ghost: bool, reason: str)
    """
    denom_str = str(denomination or "").strip()
    theme_str = str(theme or "").strip()
    name_str = str(name or "").strip()
    prog_str = str(program or "").strip()
    combined_text = f"{denom_str} {theme_str} {name_str} {prog_str}".lower()

    # Safety Rule 1: Never delete or prune parent set document
    if doc_id and parent_doc_id and doc_id == parent_doc_id:
        return False, "SAFETY PROTECTED: Document is parent set document"

    # Safety Rule 2: Never delete or prune any entry containing 'cent'
    if is_cent_entry(denom_str):
        return False, "SAFETY PROTECTED: Denomination contains 'cent'"

    # USMC Pattern Detection
    for pattern in USMC_PATTERNS:
        if pattern in combined_text:
            return True, f"Matches USMC ghost pattern '{pattern}'"

    # Canonical 20-coin check:
    canonical_cat = get_canonical_denomination_category(denom_str, theme_str)
    if canonical_cat is None:
        return True, f"Non-canonical denomination/theme ('{denom_str}' / '{theme_str}')"

    return False, f"Canonical ({canonical_cat})"


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: QUERY 26RJ PARENT SET DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────

def matches_26rj_in_code_filter(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    In-code tightened filter:
    Theme/Subject contains 'Uncirculated Coin Set' OR
    set_type == 'uncirculated' OR
    name contains '26RJ' OR
    Program/Series contains 'Uncirculated' OR
    'Retailer Item No.' == '26RJ'
    """
    theme = str(data.get("Theme/Subject") or data.get("theme_subject") or data.get("theme") or "").strip()
    set_type = str(data.get("set_type") or "").strip()
    name = str(data.get("name") or data.get("Name") or "").strip()
    prog = str(data.get("Program/Series") or data.get("program_series") or "").strip()
    retailer = str(data.get("Retailer Item No.") or data.get("retailer_item_no") or "").strip()

    reasons = []
    if "uncirculated coin set" in theme.lower():
        reasons.append(f"Theme/Subject contains 'Uncirculated Coin Set' ('{theme}')")
    if set_type.lower() == "uncirculated":
        reasons.append("set_type == 'uncirculated'")
    if "26rj" in name.lower():
        reasons.append(f"name contains '26RJ' ('{name}')")
    if "uncirculated" in prog.lower():
        reasons.append(f"Program/Series contains 'Uncirculated' ('{prog}')")
    if retailer.upper() == "26RJ":
        reasons.append("Retailer Item No. == '26RJ'")

    return len(reasons) > 0, reasons


def find_26rj_parents(coins_ref: firestore.CollectionReference) -> List[firestore.DocumentSnapshot]:
    """
    Finds 26RJ parent set documents using tightened Firestore query + in-code filter:
    (is_set == True OR item_type == 'set') AND Year == '2026'
    """
    matched_snapshots: Dict[str, firestore.DocumentSnapshot] = {}

    # Query variations for Year == '2026' and Year == 2026
    year_queries = [
        coins_ref.where(filter=FieldFilter("Year", "==", "2026")),
        coins_ref.where(filter=FieldFilter("Year", "==", 2026)),
    ]

    for yq in year_queries:
        try:
            # Query combining OR condition for is_set / item_type
            q = yq.where(filter=Or([
                FieldFilter("is_set", "==", True),
                FieldFilter("item_type", "==", "set")
            ]))
            for snap in q.stream():
                matched_snapshots[snap.id] = snap
        except Exception:
            # Fallback if composite OR query requires index or fails:
            for snap in yq.stream():
                data = snap.to_dict() or {}
                if data.get("is_set") is True or str(data.get("item_type") or "").lower() == "set":
                    matched_snapshots[snap.id] = snap

    # Filter in-code for 26RJ criteria
    final_parents = []
    for doc_id, snap in matched_snapshots.items():
        data = snap.to_dict() or {}
        matches, _ = matches_26rj_in_code_filter(data)
        if matches:
            final_parents.append(snap)

    return final_parents


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: AUDIT PATH A (set_contents) AND PATH B (real child documents)
# ─────────────────────────────────────────────────────────────────────────────

def audit_parent_set(
    parent_snap: firestore.DocumentSnapshot,
    coins_ref: firestore.CollectionReference
) -> Dict[str, Any]:
    """
    Audits a single parent set document across Path A (set_contents) and Path B (real child docs).
    """
    parent_id = parent_snap.id
    parent_data = parent_snap.to_dict() or {}

    audit_result: Dict[str, Any] = {
        "parent_id": parent_id,
        "parent_data": parent_data,
        "path_a": {
            "type_desc": "None",
            "raw_contents": parent_data.get("set_contents"),
            "count": 0,
            "entries": [],
            "ghost_indices": [],
            "ghost_entries": [],
        },
        "path_b": {
            "count": 0,
            "children": [],
            "usmc_children": [],
        },
        "canonical_summary": {
            "p_cent_present": False,
            "d_cent_present": False,
            "canonical_counts": {
                "1 Cent (P)": 0,
                "1 Cent (D)": 0,
                "5 Cents (P)": 0,
                "5 Cents (D)": 0,
                "10 Cents (P)": 0,
                "10 Cents (D)": 0,
                "50 Cents (P)": 0,
                "50 Cents (D)": 0,
                "25 Cents (P)": 0,
                "25 Cents (D)": 0,
                "1 Dollar (P)": 0,
                "1 Dollar (D)": 0,
            },
            "missing_coins": [],
        }
    }

    # ─────────────────────────────────────────────────────────────────────────
    # Path A — set_contents array inspection
    # ─────────────────────────────────────────────────────────────────────────
    raw_sc = parent_data.get("set_contents")
    if raw_sc is None:
        audit_result["path_a"]["type_desc"] = "None (no set_contents field or null)"
        audit_result["path_a"]["count"] = 0
    elif not isinstance(raw_sc, list):
        audit_result["path_a"]["type_desc"] = f"Invalid ({type(raw_sc).__name__})"
        audit_result["path_a"]["count"] = 0
    else:
        audit_result["path_a"]["count"] = len(raw_sc)
        has_str = any(isinstance(x, str) for x in raw_sc)
        has_dict = any(isinstance(x, dict) for x in raw_sc)
        if has_str and has_dict:
            type_desc = "mixed (list of doc IDs and inline dicts)"
        elif has_str:
            type_desc = "list of strings (doc IDs)"
        elif has_dict:
            type_desc = "list of dicts (inline objects)"
        else:
            type_desc = "empty list"
        audit_result["path_a"]["type_desc"] = type_desc

        for idx, entry in enumerate(raw_sc):
            entry_info: Dict[str, Any] = {
                "index": idx,
                "raw": entry,
                "entry_type": type(entry).__name__,
                "doc_id": None,
                "denomination": "",
                "theme": "",
                "mint_mark": "",
                "is_ghost": False,
                "ghost_reason": "",
                "resolved": False,
            }

            if isinstance(entry, str):
                # String doc ID: resolve actual document
                child_id = entry.strip()
                entry_info["doc_id"] = child_id
                child_snap = coins_ref.document(child_id).get()
                if child_snap.exists:
                    cdata = child_snap.to_dict() or {}
                    entry_info["resolved"] = True
                    entry_info["denomination"] = cdata.get("Denomination") or cdata.get("denomination") or ""
                    entry_info["theme"] = cdata.get("Theme/Subject") or cdata.get("theme_subject") or cdata.get("theme") or ""
                    entry_info["mint_mark"] = cdata.get("Mint Mark") or cdata.get("mint_mark") or ""
                    entry_info["name"] = cdata.get("name") or cdata.get("Name") or ""
                    entry_info["program"] = cdata.get("Program/Series") or cdata.get("program_series") or ""
                else:
                    entry_info["resolved"] = False
                    entry_info["theme"] = "(Missing / Unresolvable Document)"
            elif isinstance(entry, dict):
                # Inline dictionary object
                entry_info["resolved"] = True
                entry_info["denomination"] = entry.get("Denomination") or entry.get("denomination") or ""
                entry_info["theme"] = entry.get("Theme/Subject") or entry.get("theme_subject") or entry.get("theme") or ""
                entry_info["mint_mark"] = entry.get("Mint Mark") or entry.get("mint_mark") or ""
                entry_info["name"] = entry.get("name") or entry.get("Name") or ""
                entry_info["program"] = entry.get("Program/Series") or entry.get("program_series") or ""
            else:
                entry_info["theme"] = f"(Unsupported entry type: {type(entry).__name__})"

            is_ghost, ghost_reason = evaluate_ghost(
                denomination=entry_info["denomination"],
                theme=entry_info["theme"],
                name=entry_info.get("name", ""),
                program=entry_info.get("program", ""),
                doc_id=entry_info["doc_id"],
                parent_doc_id=parent_id
            )
            entry_info["is_ghost"] = is_ghost
            entry_info["ghost_reason"] = ghost_reason

            if is_ghost:
                audit_result["path_a"]["ghost_indices"].append(idx)
                audit_result["path_a"]["ghost_entries"].append(entry_info)

            # Record canonical presence
            if not is_ghost and entry_info["resolved"]:
                canon_cat = get_canonical_denomination_category(entry_info["denomination"], entry_info["theme"])
                mint = extract_mint_mark(
                    entry_info["mint_mark"],
                    f"{entry_info['denomination']} {entry_info['theme']} {entry_info.get('name', '')}"
                )
                if canon_cat and mint:
                    key = f"{canon_cat} ({mint})"
                    if key in audit_result["canonical_summary"]["canonical_counts"]:
                        audit_result["canonical_summary"]["canonical_counts"][key] += 1

            audit_result["path_a"]["entries"].append(entry_info)

    # ─────────────────────────────────────────────────────────────────────────
    # Path B — real child documents query
    # ─────────────────────────────────────────────────────────────────────────
    real_children_map: Dict[str, firestore.DocumentSnapshot] = {}

    # Query 1: parent_set_id == parent_doc_id
    try:
        q1 = coins_ref.where(filter=FieldFilter("parent_set_id", "==", parent_id)).stream()
        for csnap in q1:
            if csnap.id != parent_id:
                real_children_map[csnap.id] = csnap
    except Exception as ex:
        print(f"[WARN] Error querying parent_set_id: {ex}")

    # Query 2: set_id == parent_doc_id
    try:
        q2 = coins_ref.where(filter=FieldFilter("set_id", "==", parent_id)).stream()
        for csnap in q2:
            if csnap.id != parent_id:
                real_children_map[csnap.id] = csnap
    except Exception as ex:
        print(f"[WARN] Error querying set_id: {ex}")

    audit_result["path_b"]["count"] = len(real_children_map)

    for cid, csnap in real_children_map.items():
        cdata = csnap.to_dict() or {}
        denom = cdata.get("Denomination") or cdata.get("denomination") or ""
        theme = cdata.get("Theme/Subject") or cdata.get("theme_subject") or cdata.get("theme") or ""
        mint = cdata.get("Mint Mark") or cdata.get("mint_mark") or ""
        name = cdata.get("name") or cdata.get("Name") or ""
        prog = cdata.get("Program/Series") or cdata.get("program_series") or ""

        is_ghost, ghost_reason = evaluate_ghost(
            denomination=denom,
            theme=theme,
            name=name,
            program=prog,
            doc_id=cid,
            parent_doc_id=parent_id
        )

        child_info = {
            "doc_id": cid,
            "denomination": denom,
            "theme": theme,
            "mint_mark": mint,
            "name": name,
            "program": prog,
            "is_ghost": is_ghost,
            "ghost_reason": ghost_reason,
            "snapshot": csnap,
        }
        audit_result["path_b"]["children"].append(child_info)

        if is_ghost:
            audit_result["path_b"]["usmc_children"].append(child_info)
        else:
            canon_cat = get_canonical_denomination_category(denom, theme)
            extracted_mint = extract_mint_mark(mint, f"{denom} {theme} {name}")
            if canon_cat and extracted_mint:
                key = f"{canon_cat} ({extracted_mint})"
                if key in audit_result["canonical_summary"]["canonical_counts"]:
                    audit_result["canonical_summary"]["canonical_counts"][key] += 1

    # ─────────────────────────────────────────────────────────────────────────
    # Canonical Evaluation & Missing Coin Analysis
    # ─────────────────────────────────────────────────────────────────────────
    counts = audit_result["canonical_summary"]["canonical_counts"]
    audit_result["canonical_summary"]["p_cent_present"] = counts.get("1 Cent (P)", 0) > 0
    audit_result["canonical_summary"]["d_cent_present"] = counts.get("1 Cent (D)", 0) > 0

    missing: List[str] = []
    # 1 Cent
    if counts.get("1 Cent (P)", 0) == 0:
        missing.append("1 Cent (P) - Lincoln Cent [CRITICAL]")
    if counts.get("1 Cent (D)", 0) == 0:
        missing.append("1 Cent (D) - Lincoln Cent [CRITICAL]")
    # 5 Cents
    if counts.get("5 Cents (P)", 0) == 0:
        missing.append("5 Cents (P) - Jefferson Nickel")
    if counts.get("5 Cents (D)", 0) == 0:
        missing.append("5 Cents (D) - Jefferson Nickel")
    # 10 Cents
    if counts.get("10 Cents (P)", 0) == 0:
        missing.append("10 Cents (P) - Emerging Liberty Dime")
    if counts.get("10 Cents (D)", 0) == 0:
        missing.append("10 Cents (D) - Emerging Liberty Dime")
    # 50 Cents
    if counts.get("50 Cents (P)", 0) == 0:
        missing.append("50 Cents (P) - Enduring Liberty Half Dollar")
    if counts.get("50 Cents (D)", 0) == 0:
        missing.append("50 Cents (D) - Enduring Liberty Half Dollar")
    # 25 Cents (5 expected per mint)
    qp_found = counts.get("25 Cents (P)", 0)
    if qp_found < 5:
        missing.append(f"25 Cents (P) - Semiquincentennial Quarters ({qp_found}/5 present)")
    qd_found = counts.get("25 Cents (D)", 0)
    if qd_found < 5:
        missing.append(f"25 Cents (D) - Semiquincentennial Quarters ({qd_found}/5 present)")
    # 1 Dollar
    if counts.get("1 Dollar (P)", 0) == 0:
        missing.append("1 Dollar (P) - Native American Dollar")
    if counts.get("1 Dollar (D)", 0) == 0:
        missing.append("1 Dollar (D) - Native American Dollar")

    audit_result["canonical_summary"]["missing_coins"] = missing

    return audit_result


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: TRANSACTIONAL REPAIR (--execute)
# ─────────────────────────────────────────────────────────────────────────────

def repair_parent_set(
    db: firestore.Client,
    coins_ref: firestore.CollectionReference,
    audit_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes an atomic Firestore transaction per parent document:
    1. Backup: writes original set_contents to 'set_contents_backup_20260909'
    2. Prune set_contents: removes ghost entries by index
    3. Delete orphaned USMC real child docs (confirming safety rules)
    4. Stamps 'Retailer Item No.': '26RJ' on parent
    5. Verifies and returns before/after state
    """
    parent_id = audit_data["parent_id"]
    parent_ref = coins_ref.document(parent_id)

    # 1. Prepare pruned set_contents
    raw_contents = audit_data["path_a"]["raw_contents"]
    ghost_indices: Set[int] = set(audit_data["path_a"]["ghost_indices"])

    if isinstance(raw_contents, list):
        pruned_contents = [entry for i, entry in enumerate(raw_contents) if i not in ghost_indices]
    else:
        pruned_contents = raw_contents  # None or unchanged

    # 2. Identify child docs to delete with safety gates
    child_refs_to_delete: List[firestore.DocumentReference] = []
    skipped_children: List[Tuple[str, str]] = []

    for child in audit_data["path_b"]["usmc_children"]:
        cid = child["doc_id"]
        denom = child["denomination"]

        # Safety Gate: Never delete parent set doc
        if cid == parent_id:
            skipped_children.append((cid, "Refusing deletion: Document is parent set document"))
            continue

        # Safety Gate: Never delete any entry where denomination contains 'cent'
        if is_cent_entry(denom):
            skipped_children.append((cid, "Refusing deletion: Denomination contains 'cent'"))
            continue

        child_refs_to_delete.append(coins_ref.document(cid))

    # Also check if any ghost entries in set_contents were doc IDs of real docs needing deletion
    for entry in audit_data["path_a"]["ghost_entries"]:
        cid = entry.get("doc_id")
        denom = entry.get("denomination", "")
        if cid and cid != parent_id and not is_cent_entry(denom):
            cref = coins_ref.document(cid)
            if cref not in child_refs_to_delete:
                if entry.get("resolved"):
                    child_refs_to_delete.append(cref)

    # 3. Transaction Execution
    transaction = db.transaction()

    @firestore.transactional
    def apply_repair_transaction(txn: firestore.Transaction) -> None:
        # Transactional Reads (MUST precede writes)
        _ = parent_ref.get(transaction=txn)
        for cref in child_refs_to_delete:
            _ = cref.get(transaction=txn)

        # Transactional Writes
        parent_update: Dict[str, Any] = {
            "Retailer Item No.": RETAILER_ITEM_STAMP,
            BACKUP_FIELD_NAME: raw_contents,
        }
        if isinstance(raw_contents, list):
            parent_update["set_contents"] = pruned_contents

        txn.update(parent_ref, parent_update)

        for cref in child_refs_to_delete:
            txn.delete(cref)

    # Commit the transaction
    apply_repair_transaction(transaction)

    # 4. Post-Repair Verification
    updated_parent_snap = parent_ref.get()
    updated_parent_data = updated_parent_snap.to_dict() or {}
    new_set_contents = updated_parent_data.get("set_contents")
    new_sc_len = len(new_set_contents) if isinstance(new_set_contents, list) else 0

    return {
        "parent_id": parent_id,
        "backup_written": BACKUP_FIELD_NAME in updated_parent_data,
        "retailer_stamped": updated_parent_data.get("Retailer Item No.") == RETAILER_ITEM_STAMP,
        "original_set_contents_len": audit_data["path_a"]["count"],
        "pruned_set_contents_len": new_sc_len,
        "deleted_child_count": len(child_refs_to_delete),
        "deleted_child_ids": [r.id for r in child_refs_to_delete],
        "skipped_children": skipped_children,
        "p_cent_present": audit_data["canonical_summary"]["p_cent_present"],
        "d_cent_present": audit_data["canonical_summary"]["d_cent_present"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def print_audit_report(
    user_email: str,
    dry_run: bool,
    parent_audits: List[Dict[str, Any]],
    repair_results: Optional[List[Dict[str, Any]]] = None
) -> None:
    """
    Formats and prints a clean, comprehensive markdown report suitable for
    pasting directly into an audit review log.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mode_str = "AUDIT (DRY-RUN - NO CHANGES APPLIED)" if dry_run else "REPAIR (LIVE EXECUTION - COMMITTED)"

    print("=" * 80)
    print(" 2026 UNCIRCUATED COIN SET (26RJ) GHOST CHILD AUDIT & REPAIR REPORT")
    print("=" * 80)
    print(f"Timestamp    : {timestamp}")
    print(f"GCP Project  : {PROJECT_ID}")
    print(f"Target User  : {user_email}")
    print(f"Mode         : {mode_str}")
    print(f"Parent Sets  : {len(parent_audits)} matching document(s)")
    print("-" * 80)

    if not parent_audits:
        print("\n[RESULT] No 2026 Uncirculated Coin Set (26RJ) parent documents found matching criteria.")
        print("Criteria: (is_set == True OR item_type == 'set') AND Year == '2026' + 26RJ filter.")
        print("=" * 80)
        return

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1: PARENT DOCUMENT DISCOVERY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n### SECTION 1: DISCOVERED 26RJ PARENT SET DOCUMENTS\n")
    for idx, audit in enumerate(parent_audits, start=1):
        pdata = audit["parent_data"]
        pid = audit["parent_id"]
        _, match_reasons = matches_26rj_in_code_filter(pdata)
        print(f"[{idx}] Parent ID : {pid}")
        print(f"    Name      : {pdata.get('name') or pdata.get('Name') or 'N/A'}")
        print(f"    Theme     : {pdata.get('Theme/Subject') or 'N/A'}")
        print(f"    Series    : {pdata.get('Program/Series') or 'N/A'}")
        print(f"    Retailer  : {pdata.get('Retailer Item No.') or 'N/A'}")
        print(f"    Matched On: {', '.join(match_reasons)}")
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2: AUDIT DETAILS PER PARENT (PATH A & PATH B)
    # ─────────────────────────────────────────────────────────────────────────
    print("-" * 80)
    print("### SECTION 2: PATH A & PATH B AUDIT DETAILS\n")

    for idx, audit in enumerate(parent_audits, start=1):
        pid = audit["parent_id"]
        pa = audit["path_a"]
        pb = audit["path_b"]

        print(f"--- Parent Document [{idx}/{len(parent_audits)}]: {pid} ---")

        # Path A
        print("\n[Path A: set_contents array]")
        print(f"  Status / Type : {pa['type_desc']}")
        print(f"  Total Entries : {pa['count']}")
        if pa["count"] > 0:
            print("  Entries Listing:")
            for entry in pa["entries"]:
                e_idx = entry["index"]
                e_type = entry["entry_type"]
                denom = entry["denomination"] or "N/A"
                theme = entry["theme"] or "N/A"
                mint = entry["mint_mark"] or "-"
                ghost_tag = f" [** GHOST **: {entry['ghost_reason']}]" if entry["is_ghost"] else ""
                ref_id = f" (doc_id: {entry['doc_id']})" if entry["doc_id"] else ""
                print(f"    [{e_idx:02d}] {denom} | Theme: {theme} | Mint: {mint}{ref_id}{ghost_tag}")

        if pa["ghost_indices"]:
            print(f"  Ghost Entries Identified in set_contents: {len(pa['ghost_indices'])}")
            for g in pa["ghost_entries"]:
                print(f"    - Index {g['index']:02d}: {g['denomination']} - {g['theme']} (Reason: {g['ghost_reason']})")
        else:
            print("  Ghost Entries in set_contents: None detected")

        # Path B
        print(f"\n[Path B: Real Child Documents in users/{user_email}/coins]")
        print(f"  Query Criteria : parent_set_id == '{pid}' OR set_id == '{pid}'")
        print(f"  Real Children  : {pb['count']}")
        if pb["count"] > 0:
            print("  Children Listing:")
            for child in pb["children"]:
                cid = child["doc_id"]
                denom = child["denomination"] or "N/A"
                theme = child["theme"] or "N/A"
                mint = child["mint_mark"] or "-"
                ghost_tag = f" [** USMC GHOST **: {child['ghost_reason']}]" if child["is_ghost"] else ""
                print(f"    - ID: {cid} | {denom} | Theme: {theme} | Mint: {mint}{ghost_tag}")

        if pb["usmc_children"]:
            print(f"  Confirmed USMC / Non-Canonical Real Children: {len(pb['usmc_children'])}")
            for ug in pb["usmc_children"]:
                print(f"    - ID: {ug['doc_id']} | {ug['denomination']} - {ug['theme']} ({ug['ghost_reason']})")
        else:
            print("  Confirmed USMC / Non-Canonical Real Children: None detected")

        print()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3: SUMMARY PER PARENT & CANONICAL COMPLETENESS
    # ─────────────────────────────────────────────────────────────────────────
    print("-" * 80)
    print("### SECTION 3: SUMMARY PER PARENT & CANONICAL CHECKLIST\n")

    for idx, audit in enumerate(parent_audits, start=1):
        pid = audit["parent_id"]
        pa = audit["path_a"]
        pb = audit["path_b"]
        cs = audit["canonical_summary"]

        virtual_ghosts = len(pa["ghost_indices"])
        real_ghosts = len(pb["usmc_children"])
        total_ghosts = virtual_ghosts + real_ghosts

        print(f"Summary for Parent: {pid}")
        print(f"  * set_contents Count  : {pa['count']} ({pa['type_desc']})")
        print(f"  * Real Child Docs     : {pb['count']}")
        print(f"  * Ghost Count Total   : {total_ghosts} (Virtual: {virtual_ghosts}, Real Docs: {real_ghosts})")
        print(f"  * P Cent Present      : {'YES [OK]' if cs['p_cent_present'] else 'NO [MISSING]'}")
        print(f"  * D Cent Present      : {'YES [OK]' if cs['d_cent_present'] else 'NO [MISSING]'}")

        print("\n  Canonical 20-Coin Inventory Status:")
        for key, count in cs["canonical_counts"].items():
            expected = 5 if "25 Cents" in key else 1
            status = f"{count}/{expected} present"
            flag = "[OK]" if count >= expected else "[INCOMPLETE]"
            print(f"    - {key:<16}: {status:<15} {flag}")

        if cs["missing_coins"]:
            print("\n  Missing Canonical Items:")
            for m in cs["missing_coins"]:
                print(f"    - {m}")
        else:
            print("\n  Canonical Completeness: 100% (All 20 canonical coins accounted for)")

        print()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4: REPAIR ACTIONS / BEFORE & AFTER (IF --EXECUTE)
    # ─────────────────────────────────────────────────────────────────────────
    print("-" * 80)
    print("### SECTION 4: REPAIR EXECUTION & AUDIT TRAIL\n")

    if dry_run:
        print("[DRY-RUN MODE]")
        print("No mutations were written to Firestore.")
        print("To commit these repairs atomically, run with:")
        print(f"    python repair_26rj_ghosts.py --execute --user {user_email}")
    else:
        print("[EXECUTE MODE - COMMITTED REPAIRS]")
        if repair_results:
            for res in repair_results:
                pid = res["parent_id"]
                print(f"Parent Document: {pid}")
                print(f"  * Backup Field Written        : {res['backup_written']} (`{BACKUP_FIELD_NAME}`)")
                print(f"  * Retailer Item No. Stamped   : {res['retailer_stamped']} (`{RETAILER_ITEM_STAMP}`)")
                print(f"  * set_contents Array Length   : Before: {res['original_set_contents_len']} -> After: {res['pruned_set_contents_len']}")
                print(f"  * Real Child Documents Purged : {res['deleted_child_count']}")
                if res["deleted_child_ids"]:
                    for del_id in res["deleted_child_ids"]:
                        print(f"      - Purged Doc ID: {del_id}")
                if res["skipped_children"]:
                    for sk_id, reason in res["skipped_children"]:
                        print(f"      - Skipped ID: {sk_id} ({reason})")
                print(f"  * P Cent Present Post-Repair  : {'YES' if res['p_cent_present'] else 'NO'}")
                print(f"  * D Cent Present Post-Repair  : {'YES' if res['d_cent_present'] else 'NO'}")
                print()
        else:
            print("No repair operations were necessary.")

    print("=" * 80)
    print("END OF REPORT")
    print("=" * 80)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTINE & CLI PARSER
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit and repair ghost USMC children in 2026 Uncirculated Coin Set (26RJ) parent documents in Firestore."
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Audit mode: scan and report without modifying Firestore (default)."
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        help="Repair mode: apply live database mutations. REQUIRES explicit --user."
    )
    parser.add_argument(
        "--user",
        type=str,
        default=None,
        help=f"Target user email (e.g. {DEFAULT_USER}). In dry-run defaults to {DEFAULT_USER} if omitted. In --execute, this argument MUST be explicitly passed."
    )
    parser.add_argument(
        "--project",
        type=str,
        default=PROJECT_ID,
        help=f"Firestore GCP Project ID (default: {PROJECT_ID})."
    )

    args = parser.parse_args()

    # Safety Gate: --execute refuses without explicit --user
    if args.execute and not args.user:
        print("\n" + "!" * 80)
        print("[SAFETY ERROR] Execution Refused!")
        print("The --execute flag requires an explicit --user <email> argument.")
        print(f"Example: python repair_26rj_ghosts.py --execute --user {DEFAULT_USER}")
        print("!" * 80 + "\n")
        sys.exit(1)

    is_dry_run = not args.execute
    target_user = args.user if args.user else DEFAULT_USER

    print(f"Connecting to Firestore project '{args.project}'...")
    db = get_firestore_client(project_id=args.project)
    coins_ref = db.collection("users").document(target_user).collection("coins")

    # Step 1: Query 26RJ Parent Documents
    print(f"Auditing 26RJ parent sets for user: {target_user} (dry_run={is_dry_run})...")
    parent_snaps = find_26rj_parents(coins_ref)

    # Step 2: Audit each parent document (Path A and Path B)
    parent_audits = []
    for snap in parent_snaps:
        audit_info = audit_parent_set(snap, coins_ref)
        parent_audits.append(audit_info)

    # Phase 2: Execute repairs if requested
    repair_results = None
    if not is_dry_run and parent_audits:
        repair_results = []
        for audit_info in parent_audits:
            res = repair_parent_set(db, coins_ref, audit_info)
            repair_results.append(res)

    # Output Clean Report
    print_audit_report(
        user_email=target_user,
        dry_run=is_dry_run,
        parent_audits=parent_audits,
        repair_results=repair_results
    )


if __name__ == "__main__":
    main()
