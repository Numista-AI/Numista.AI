#!/usr/bin/env python3
"""
tools/catalog/image_license_allowlist.py
Fail-closed certified public-domain license allow-list for CR3 catalog image attach.

Holds ONLY the four public-domain license classes and exact license strings present
in attach_manifest_v4 (SHA8 58ac149a). PD-US-SI is its own US government /
Smithsonian employee public-domain class and is NEVER treated as CC0.
Adding any new class or string requires its own reviewed plan update.
"""

from typing import Optional

# Exact mapping of the 4 attach_manifest_v4 public-domain classes to their exact strings.
CERTIFIED_LICENSE_BY_CLASS = {
    "US_MINT_PD": "Public domain (US government work, 17 U.S.C. \u00a7 105)",
    "PD-US-SI": (
        "Public domain (PD-US-SI; U.S. government / Smithsonian employee work, "
        "not Smithsonian Open Access CC0)"
    ),
    "WIKIMEDIA_PD_CONFIRMED": "Public domain (Wikimedia Commons)",
    "WIKIMEDIA_PD_OWN_WORK": (
        "Public domain (Wikimedia Commons; photographer's own work). "
        "Credit the photographer."
    ),
}

CERTIFIED_LICENSE_TO_CLASS = {
    license_str: license_class
    for license_class, license_str in CERTIFIED_LICENSE_BY_CLASS.items()
}


def get_certified_license_class(license_str: Optional[str]) -> Optional[str]:
    """Returns the certified license class for an exact allow-listed license string, or None."""
    if not isinstance(license_str, str) or not license_str:
        return None
    return CERTIFIED_LICENSE_TO_CLASS.get(license_str)


def is_certified_license(
    license_str: Optional[str],
    license_class: Optional[str] = None,
) -> bool:
    """
    Fail-closed validator for catalog image licenses.
    Rejects None, empty strings, case/whitespace variants, lookalikes, CC0, CC BY-SA 4.0,
    and All rights reserved. When license_class is provided, requires exact pair match.
    """
    matched_class = get_certified_license_class(license_str)
    if matched_class is None:
        return False
    if license_class is not None:
        if not isinstance(license_class, str) or not license_class:
            return False
        if matched_class != license_class:
            return False
    return True
