"""
services/analytics_tools.py
---------------------------
Deterministic Analytics & Morgan Analytics Co-Pilot tools.
Zero LLM arithmetic: all aggregations, spot-price simulations, net liquidation,
and duplicate grouping are executed deterministically against a normalized
in-request `vault_snapshot`.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_LIQUIDATION_FEE_PCT = 0.13
PLATED_OR_BASE_REGEX = re.compile(
    r"(plated|clad|nickel\s*silver|copper[-\s]?nickel|cupro[-\s]?nickel|brass|bronze|zinc|steel|aluminum)",
    re.IGNORECASE,
)

# Canonical US denomination normalization (mirrors DenominationCanon.normalize)
_DENOM_CANON_MAP = {
    "1c": "cent",
    "1¢": "cent",
    "penny": "cent",
    "pennies": "cent",
    "one cent": "cent",
    "1 cent": "cent",
    "lincoln cent": "cent",
    "5c": "five cents",
    "5¢": "five cents",
    "nickel": "five cents",
    "nickels": "five cents",
    "10c": "dime",
    "10¢": "dime",
    "one dime": "dime",
    "25c": "quarter dollar",
    "25¢": "quarter dollar",
    "quarter": "quarter dollar",
    "quarters": "quarter dollar",
    "50c": "half dollar",
    "50¢": "half dollar",
    "half": "half dollar",
    "half dollar": "half dollar",
    "$1": "dollar",
    "1$": "dollar",
    "one dollar": "dollar",
    "silver dollar": "dollar",
}

_AG90_OZ = {
    "half dime": 0.03617,
    "dime": 0.07234,
    "quarter dollar": 0.18084,
    "half dollar": 0.36169,
    "dollar": 0.77344,
}


def _safe_float(val: Any) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val) if math.isfinite(float(val)) else 0.0
    s = str(val).replace(",", "").strip()
    if not s or s.lower() in {"pending", "n/a", "null", "none"}:
        return 0.0
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return 0.0
    v = float(m.group(0))
    return v if math.isfinite(v) else 0.0


def parse_ai_value(raw: Any) -> float:
    """
    Parses aiEstimatedValue, rejecting <= 0.0 zero sentinels ('$0.00', '0', 'Pending')
    so unvalued items are never counted as $0 priced coins.
    """
    if raw is None:
        return 0.0
    s = str(raw).replace(",", "").replace("\u2013", "-").replace("\u2014", "-").strip()
    if not s or s.lower() in {"pending", "n/a", "null", "none"}:
        return 0.0
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*[^0-9]*(\d+(?:\.\d+)?)", s)
    if range_match:
        v = float(range_match.group(1))
    else:
        cleaned = re.sub(r"[^\d.]", "", s)
        if not cleaned:
            return 0.0
        try:
            v = float(cleaned)
        except ValueError:
            return 0.0
    if v <= 0.0 or v > 100000.0:
        return 0.0
    return v


def normalize_denomination(raw: Any) -> str:
    s = str(raw or "").strip().lower()
    return _DENOM_CANON_MAP.get(s, s)


def _infer_fine_oz(doc: Dict[str, Any]) -> Dict[str, float]:
    """
    Returns per-unit fine troy ounces {au, ag, pt, pd}, enforcing the plated/base-metal guard.
    """
    metal_str = str(doc.get("metalContent") or doc.get("metal_content") or "").strip()
    if PLATED_OR_BASE_REGEX.search(metal_str):
        return {"au": 0.0, "ag": 0.0, "pt": 0.0, "pd": 0.0}

    # Explicit numeric field takes precedence when present
    explicit_oz = _safe_float(doc.get("troy_oz_pure_metal"))
    ml = metal_str.lower()
    if explicit_oz > 0.0:
        if "gold" in ml or "au" in ml:
            return {"au": explicit_oz, "ag": 0.0, "pt": 0.0, "pd": 0.0}
        if "platinum" in ml or "pt" in ml:
            return {"au": 0.0, "ag": 0.0, "pt": explicit_oz, "pd": 0.0}
        if "palladium" in ml or "pd" in ml:
            return {"au": 0.0, "ag": 0.0, "pt": 0.0, "pd": explicit_oz}
        return {"au": 0.0, "ag": explicit_oz, "pt": 0.0, "pd": 0.0}

    denom = normalize_denomination(doc.get("denomination") or doc.get("Denomination"))
    series = str(doc.get("programSeries") or doc.get("program_series") or "").lower()

    if "999" in ml or "fine silver" in ml or "silver eagle" in series:
        if "silver" in ml or "silver eagle" in series:
            return {"au": 0.0, "ag": 1.0, "pt": 0.0, "pd": 0.0}
    if "90%" in ml or ("silver" in ml and denom in _AG90_OZ):
        return {"au": 0.0, "ag": _AG90_OZ.get(denom, 0.0), "pt": 0.0, "pd": 0.0}
    if "gold" in ml or "gold eagle" in series or "buffalo" in series:
        if "1 oz" in ml or "50" in denom:
            return {"au": 1.0, "ag": 0.0, "pt": 0.0, "pd": 0.0}
        if "1/2" in ml or "25" in denom:
            return {"au": 0.5, "ag": 0.0, "pt": 0.0, "pd": 0.0}
        if "1/4" in ml or "10" in denom:
            return {"au": 0.25, "ag": 0.0, "pt": 0.0, "pd": 0.0}
        if "1/10" in ml or "5" in denom:
            return {"au": 0.1, "ag": 0.0, "pt": 0.0, "pd": 0.0}

    return {"au": 0.0, "ag": 0.0, "pt": 0.0, "pd": 0.0}


def build_vault_snapshot(
    raw_docs: List[Tuple[str, Dict[str, Any]]],
    advanced_mode: bool = False,
    fee_pct: float = DEFAULT_LIQUIDATION_FEE_PCT,
) -> List[Dict[str, Any]]:
    """
    Normalizes raw Firestore coin documents into an analytics-ready snapshot:
    - Excludes supplies (`item_type == 'supply'` or `is_supply == True`)
    - Guards against set + child double counting (`isSet == True` vs `parentSetId`)
    - Applies quantity multiplier (lot-level for sets)
    - Rejects <= 0.0 zero sentinels in aiEstimatedValue
    """
    # Identify parent sets that already have expanded child docs in the vault
    parent_ids_with_children = {
        str(d.get("parentSetId") or "").strip()
        for _, d in raw_docs
        if d.get("parentSetId")
    }

    snapshot: List[Dict[str, Any]] = []
    for doc_id, d in raw_docs:
        item_type = str(d.get("item_type") or "").strip().lower()
        if d.get("is_supply") is True or item_type == "supply":
            continue

        is_set = bool(d.get("isSet") is True or d.get("is_set") is True)
        if is_set and doc_id in parent_ids_with_children:
            # Skip parent set record when child coins are present to prevent double-counting
            continue

        qty = 1 if is_set else max(1, int(_safe_float(d.get("quantity") or 1)))

        cpg = _safe_float(d.get("cpgRetail") or d.get("cpg_retail"))
        pcgs = _safe_float(d.get("pcgsValue") or d.get("pcgs_value"))
        ngc = _safe_float(d.get("ngcValue") or d.get("ngc_value"))
        gs_bid = _safe_float(d.get("greysheetBid") or d.get("greysheet_bid"))
        blue_book = _safe_float(d.get("blueBookValue") or d.get("blue_book_value"))
        ai_val = parse_ai_value(d.get("aiEstimatedValue") or d.get("ai_estimated_value"))

        if advanced_mode:
            unit_primary = cpg or pcgs or ngc or ai_val
        else:
            unit_primary = gs_bid or blue_book or ai_val or cpg

        unit_melt = _safe_float(d.get("meltValue") or d.get("melt_value"))
        fine_oz = _infer_fine_oz(d)
        has_fine_oz = sum(fine_oz.values()) > 0.0

        if gs_bid > 0.0:
            unit_net_liq = gs_bid
        elif unit_primary > 0.0:
            unit_net_liq = unit_primary * (1.0 - fee_pct)
        else:
            unit_net_liq = 0.0

        if has_fine_oz and unit_melt > 0.0:
            unit_net_liq = max(unit_net_liq, 0.95 * unit_melt)

        unit_cost = _safe_float(d.get("purchaseCost") or d.get("purchase_cost") or d.get("Cost"))
        grading = str(d.get("gradingService") or d.get("grading_service") or "").strip()

        snapshot.append(
            {
                "id": doc_id,
                "country": str(d.get("country") or "USA").strip() or "USA",
                "year": str(d.get("year") or "").strip(),
                "mint_mark": str(d.get("mintMark") or d.get("mint_mark") or "").strip(),
                "denomination": normalize_denomination(d.get("denomination") or d.get("Denomination")),
                "program_series": str(d.get("programSeries") or d.get("program_series") or "").strip(),
                "variety": str(d.get("variety") or "").strip(),
                "condition": str(d.get("condition") or "Ungraded").strip(),
                "grading_service": grading,
                "is_raw": grading == "" or grading.lower() in {"none", "ungraded", "raw"},
                "metal_content": str(d.get("metalContent") or d.get("metal_content") or "").strip(),
                "retailer": str(d.get("retailer") or "").strip(),
                "storage_location": str(d.get("storageLocation") or d.get("storage_location") or "").strip(),
                "is_set": is_set,
                "parent_set_id": d.get("parentSetId"),
                "qty": qty,
                "unit_primary": unit_primary,
                "total_value": unit_primary * qty,
                "unit_net_liq": unit_net_liq,
                "total_net_liq": unit_net_liq * qty,
                "unit_melt": unit_melt if has_fine_oz or unit_melt > 0 else 0.0,
                "total_melt": (unit_melt if has_fine_oz or unit_melt > 0 else 0.0) * qty,
                "unit_cost": unit_cost,
                "total_cost": unit_cost * qty,
                "has_price": unit_primary > 0.0,
                "has_cost": unit_cost > 0.0,
                "fine_au_oz": fine_oz["au"] * qty,
                "fine_ag_oz": fine_oz["ag"] * qty,
                "fine_pt_oz": fine_oz["pt"] * qty,
                "fine_pd_oz": fine_oz["pd"] * qty,
            }
        )
    return snapshot


def _matches_filters(item: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
    if not filters:
        return True
    for k, v in filters.items():
        if v is None or v == "":
            continue
        if k == "is_raw":
            if bool(item.get("is_raw")) != bool(v):
                return False
        elif k == "metal":
            if str(v).lower() not in item.get("metal_content", "").lower():
                return False
        else:
            if str(item.get(k, "")).strip().lower() != str(v).strip().lower():
                return False
    return True


def query_vault_aggregate(
    vault_snapshot: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]] = None,
    group_by: str = "none",
    metrics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Tool 1: Deterministic vault aggregation & filtering."""
    filtered = [c for c in vault_snapshot if _matches_filters(c, filters)]
    groups: Dict[str, Dict[str, Any]] = {}

    for c in filtered:
        if group_by == "none" or not group_by:
            key = "all"
        elif group_by == "metal":
            key = c.get("metal_content") or "Unknown"
        else:
            key = str(c.get(group_by) or "Unknown") or "Unknown"

        g = groups.setdefault(
            key,
            {
                "key": key,
                "count": 0,
                "total_value": 0.0,
                "net_liq": 0.0,
                "melt_value": 0.0,
                "cost_basis": 0.0,
            },
        )
        g["count"] += c["qty"]
        g["total_value"] += c["total_value"]
        g["net_liq"] += c["total_net_liq"]
        g["melt_value"] += c["total_melt"]
        if c["has_cost"]:
            g["cost_basis"] += c["total_cost"]

    rounded_groups = [
        {
            **g,
            "total_value": round(g["total_value"], 2),
            "net_liq": round(g["net_liq"], 2),
            "melt_value": round(g["melt_value"], 2),
            "cost_basis": round(g["cost_basis"], 2),
        }
        for g in sorted(groups.values(), key=lambda x: x["total_value"], reverse=True)
    ]

    return {
        "groups": rounded_groups,
        "coverage": {
            "priced": sum(c["qty"] for c in filtered if c["has_price"]),
            "with_cost": sum(c["qty"] for c in filtered if c["has_cost"]),
            "total": sum(c["qty"] for c in filtered),
        },
        "matching_coin_ids": [c["id"] for c in filtered],
    }


def simulate_spot_prices(
    vault_snapshot: List[Dict[str, Any]],
    gold: float,
    silver: float,
    platinum: float = 0.0,
    palladium: float = 0.0,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Tool 2: Deterministic O(N) spot-price simulator with melt-floor bump."""
    filtered = [c for c in vault_snapshot if _matches_filters(c, filters)]

    baseline_total = 0.0
    simulated_total = 0.0
    bullion_portion = 0.0
    numismatic_portion = 0.0
    fine_au = fine_ag = fine_pt = fine_pd = 0.0

    for c in filtered:
        base_val = c["total_value"]
        baseline_total += base_val
        fine_au += c["fine_au_oz"]
        fine_ag += c["fine_ag_oz"]
        fine_pt += c["fine_pt_oz"]
        fine_pd += c["fine_pd_oz"]

        sim_melt = (
            c["fine_au_oz"] * gold
            + c["fine_ag_oz"] * silver
            + c["fine_pt_oz"] * platinum
            + c["fine_pd_oz"] * palladium
        )
        sim_val = max(base_val, sim_melt)
        simulated_total += sim_val
        bullion_portion += min(sim_melt, sim_val)
        numismatic_portion += max(0.0, sim_val - sim_melt)

    delta = simulated_total - baseline_total
    delta_pct = (delta / baseline_total * 100.0) if baseline_total > 0 else 0.0
    bullion_share = (bullion_portion / simulated_total * 100.0) if simulated_total > 0 else 0.0
    numismatic_share = (numismatic_portion / simulated_total * 100.0) if simulated_total > 0 else 0.0

    return {
        "baseline_total": round(baseline_total, 2),
        "simulated_total": round(simulated_total, 2),
        "delta_dollars": round(delta, 2),
        "delta_pct": round(delta_pct, 2),
        "bullion_share_pct": round(bullion_share, 2),
        "numismatic_share_pct": round(numismatic_share, 2),
        "fine_oz": {
            "au": round(fine_au, 4),
            "ag": round(fine_ag, 4),
            "pt": round(fine_pt, 4),
            "pd": round(fine_pd, 4),
        },
    }


def find_duplicates(
    vault_snapshot: List[Dict[str, Any]],
    include_sets: bool = False,
    min_unit_value: float = 0.0,
) -> Dict[str, Any]:
    """Tool 3: Canonical duplicate grouping separating loose vs set/bullion multiples."""
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for c in vault_snapshot:
        if not include_sets and (c["is_set"] or c["parent_set_id"]):
            continue
        if c["unit_primary"] < min_unit_value:
            continue
        key = "|".join(
            [
                c["country"].upper(),
                c["year"],
                c["mint_mark"].upper(),
                c["denomination"].lower(),
                c["variety"].lower(),
            ]
        )
        buckets.setdefault(key, []).append(c)

    dup_groups: List[Dict[str, Any]] = []
    total_recoverable = 0.0

    for key, items in buckets.items():
        total_units = sum(i["qty"] for i in items)
        if total_units <= 1:
            continue
        loose_count = sum(i["qty"] for i in items if not i["is_set"] and not i["parent_set_id"])
        set_count = total_units - loose_count
        avg_val = sum(i["total_value"] for i in items) / total_units
        recoverable = max(0, total_units - 1) * avg_val
        total_recoverable += recoverable

        sample = items[0]
        label = " ".join(
            p
            for p in [
                sample["year"],
                sample["mint_mark"],
                sample["denomination"].title(),
                sample["variety"],
            ]
            if p
        ).strip()

        dup_groups.append(
            {
                "key": key,
                "label": label or key,
                "loose_count": loose_count,
                "set_count": set_count,
                "recoverable_value": round(recoverable, 2),
                "coin_ids": [i["id"] for i in items],
            }
        )

    dup_groups.sort(key=lambda x: x["recoverable_value"], reverse=True)
    return {
        "duplicate_groups": dup_groups,
        "total_recoverable_value": round(total_recoverable, 2),
    }
