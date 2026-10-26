"""
Shared Duplicate Detection Helper (NET-440B / Priority 1 Item 4)

Runs the standard Year + Mint + normalized Denomination check across all coin
ingestion pathways (review queue commit, spreadsheet batch commit, photo ID save,
cert save, manual add).
Never drops or deletes coins; flags them with possible_duplicate: True.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("numista_backend.duplicate_check")


def check_and_flag_duplicate(
    coins_ref: Any,
    coin_dict: Dict[str, Any],
    exclude_ids: Optional[List[str]] = None,
) -> bool:
    """
    Check if a coin matching Year, Mint Mark, and normalized Denomination
    already exists in the user's coins collection.

    If match found:
        coin_dict['possible_duplicate'] = True
        coin_dict['duplicate_flag'] = 'Attribute match (Year, Mint, Denomination)'
        return True
    
    Never drops or deletes the coin!
    """
    if not isinstance(coin_dict, dict) or not coins_ref:
        return False

    raw_d = str(coin_dict.get("Denomination") or coin_dict.get("denomination") or "").strip()
    norm_d = raw_d.lstrip("$").strip()
    denom_variants = [v for v in [raw_d, norm_d, f"${norm_d}"] if v]
    # Remove duplicates preserving order
    seen = set()
    denom_variants = [x for x in denom_variants if not (x in seen or seen.add(x))]

    year_val = str(coin_dict.get("Year") or coin_dict.get("year") or "").strip()
    mint_val = str(coin_dict.get("Mint Mark") or coin_dict.get("mint_mark") or "").strip()

    if not year_val or not denom_variants:
        return False

    exclude = set(exclude_ids or [])
    try:
        # Check against coins collection (PascalCase schema)
        q = (
            coins_ref
            .where("Year", "==", year_val)
            .where("Mint Mark", "==", mint_val)
            .where("Denomination", "in", denom_variants[:10])
            .limit(5)
            .get()
        )
        matches = [d for d in q if d.id not in exclude]
        if matches:
            coin_dict["possible_duplicate"] = True
            coin_dict["duplicate_flag"] = "Attribute match (Year, Mint, Denomination)"
            return True
    except Exception as e:
        logger.warning(f"Attribute duplicate check error: {e}")
        # Fallback: check lowercase fields if query failed due to casing or schema variation
        try:
            q_lc = (
                coins_ref
                .where("year", "==", year_val)
                .where("mint_mark", "==", mint_val)
                .limit(5)
                .get()
            )
            matches_lc = [d for d in q_lc if d.id not in exclude]
            if matches_lc:
                for d in matches_lc:
                    d_data = d.to_dict() or {}
                    ex_d = str(d_data.get("denomination") or d_data.get("Denomination") or "").strip()
                    if ex_d in denom_variants or (norm_d and ex_d.lstrip("$").strip() == norm_d):
                        coin_dict["possible_duplicate"] = True
                        coin_dict["duplicate_flag"] = "Attribute match (Year, Mint, Denomination)"
                        return True
        except Exception:
            pass

    return False
