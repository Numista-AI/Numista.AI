"""
catalog_nac1.py
---------------
NAC1 (Numista.AI Catalog v1) identifier grammar, Crockford-32 checksum and validator.

Pure module: NO Firebase / network imports, so it is safe to import from the API
boundary, ETL pipelines and unit tests alike.

Spec: Numismatics Catalog/Argon Implementation Plan/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.1.md (section 2.1-2.2)
"""

import re
from typing import Dict

CROCKFORD_32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# Plan.v2.2: CC = US|CO|PF|CS|FS; FAC includes MO (Mexico City) distinct from M (Manila);
# CHK regex strictly excludes Crockford-ambiguous I, L, O, U ([0-9A-HJ-KM-NP-TV-Z]).
NAC1_REGEX = re.compile(
    r"^(?P<payload>NAC1\.(?P<kind>CN|BN|MD|TK|ST)\.(?P<cc>US|CO|PF|CS|FS)\."
    r"(?P<denom>[A-Z0-9]{2,8})\.(?P<series>[A-Z0-9_]{2,12})\."
    r"(?P<year>[0-9]{4}[A-Z]?|ND|XXXX)\.(?P<fac>P|D|S|W|CC|O|C|DD|M|MO|L|PTS|PH|BEP|NARA|XX)\."
    r"(?P<var>[A-Z0-9_]{2,12}))\.(?P<chk>[0-9A-HJ-KM-NP-TV-Z])$"
)

# Catalog `kind` -> user sub-collection (Plan section 3.1). BN/MD/TK/ST must NEVER land in "coins".
KIND_TO_COLLECTION = {
    "CN": "coins",
    "BN": "currency",
    "MD": "world_items",
    "TK": "world_items",
    "ST": "world_items",
}


def compute_nac1_chk(payload: str) -> str:
    """Crockford-32 check character over the ASCII payload preceding the final '.CHK'."""
    h = 0
    for b in payload.encode("utf-8"):
        h = (h * 33 + b) % 37
    return CROCKFORD_32[h % 32]


def validate_nac1(nac_code) -> bool:
    """True only for a well-formed NAC1 string whose check character is correct."""
    if not isinstance(nac_code, str):
        return False
    match = NAC1_REGEX.match(nac_code)
    if not match:
        return False
    payload, chk = match.group("payload"), match.group("chk")
    return compute_nac1_chk(payload) == chk


def build_nac1(payload: str) -> str:
    """Append the computed check character to a payload (ETL / seed helper)."""
    return f"{payload}.{compute_nac1_chk(payload)}"


def nac1_kind(nac_code: str) -> str:
    """Return the KIND segment (CN/BN/MD/TK/ST) of a syntactically valid NAC1 code."""
    m = NAC1_REGEX.match(nac_code or "")
    if not m:
        raise ValueError("INVALID_NAC1_FORMAT")
    return m.group("kind")


def nac1_cc(nac_code: str) -> str:
    """Return the CC segment (US/CO/PF/CS/FS) of a syntactically valid NAC1 code."""
    m = NAC1_REGEX.match(nac_code or "")
    if not m:
        raise ValueError("INVALID_NAC1_FORMAT")
    return m.group("cc")


def parse_nac1(nac_code: str) -> Dict[str, str]:
    """Parse a validated NAC1 code into its constituent segments."""
    if not validate_nac1(nac_code):
        raise ValueError("INVALID_NAC1_CHECKSUM")
    m = NAC1_REGEX.match(nac_code)
    assert m is not None
    return {
        "payload": m.group("payload"),
        "kind": m.group("kind"),
        "cc": m.group("cc"),
        "denomination_class": m.group("denom"),
        "series": m.group("series"),
        "year": m.group("year"),
        "facility_code": m.group("fac"),
        "variety": m.group("var"),
        "chk": m.group("chk"),
    }
