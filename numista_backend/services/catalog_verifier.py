"""
Catalog Sanity-Check Verifier (Generate-and-Select Pattern)
Validates AI-generated coin identification and grading candidates against
physical numismatic mintage rules and ground-truth catalog bounds.
"""

from typing import Dict, Any, List, Optional
import re

# Known valid mint marks by series and year ranges
US_MINT_RULES = {
    "morgan dollar": {
        "start": 1878,
        "end": 1921,
        "valid_mints": {
            (1878, 1904): ["P", "CC", "S", "O", ""],
            (1921, 1921): ["P", "D", "S", ""],  # Note: No CC or O in 1921
        }
    },
    "peace dollar": {
        "start": 1921,
        "end": 1935,
        "valid_mints": {
            (1921, 1935): ["P", "D", "S", ""]
        }
    },
    "lincoln cent": {
        "start": 1909,
        "end": 2026,
        "valid_mints": {
            (1909, 1958): ["P", "D", "S", ""],
            (1959, 2026): ["P", "D", "S", "W", ""]
        }
    },
    "washington quarter": {
        "start": 1932,
        "end": 2026,
        "valid_mints": {
            (1932, 1964): ["P", "D", "S", ""],
            (1965, 1967): [""],  # No mint marks on 1965-1967 circulating coinage
            (1968, 2026): ["P", "D", "S", "W", ""]
        }
    },
    "walking liberty half dollar": {
        "start": 1916,
        "end": 1947,
        "valid_mints": {
            (1916, 1947): ["P", "D", "S", ""]
        }
    },
    "franklin half dollar": {
        "start": 1948,
        "end": 1963,
        "valid_mints": {
            (1948, 1963): ["P", "D", "S", ""]
        }
    },
    "kennedy half dollar": {
        "start": 1964,
        "end": 2026,
        "valid_mints": {
            (1964, 1964): ["P", "D", ""],
            (1965, 1967): [""],
            (1968, 2026): ["P", "D", "S", ""]
        }
    },
    "mercury dime": {
        "start": 1916,
        "end": 1945,
        "valid_mints": {
            (1916, 1945): ["P", "D", "S", ""]
        }
    },
    "roosevelt dime": {
        "start": 1946,
        "end": 2026,
        "valid_mints": {
            (1946, 1964): ["P", "D", "S", ""],
            (1965, 1967): [""],
            (1968, 2026): ["P", "D", "S", "W", ""]
        }
    },
    "buffalo nickel": {
        "start": 1913,
        "end": 1938,
        "valid_mints": {
            (1913, 1938): ["P", "D", "S", ""]
        }
    },
    "jefferson nickel": {
        "start": 1938,
        "end": 2026,
        "valid_mints": {
            (1938, 1941): ["P", "D", "S", ""],
            (1942, 1945): ["P", "D", "S"],  # War nickels had large P, D, or S
            (1946, 1964): ["P", "D", "S", ""],
            (1965, 1967): [""],
            (1968, 2026): ["P", "D", "S", ""]
        }
    },
    "saint-gaudens double eagle": {
        "start": 1907,
        "end": 1933,
        "valid_mints": {
            (1907, 1933): ["P", "D", "S", ""]
        }
    }
}

VALID_SHELDON_NUMBERS = {
    1, 2, 3, 4, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 53, 55, 58,
    60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70
}

VALID_GRADE_PREFIXES = {
    "P", "PO", "FR", "AG", "G", "VG", "F", "VF", "XF", "EF", "AU", "MS", "UNC",
    "PR", "PF", "SP"
}


def parse_sheldon_grade(grade_str: str) -> Optional[int]:
    """Extract integer numerical grade from Sheldon string (e.g. 'MS-65' -> 65, 'AU58' -> 58)."""
    if not grade_str:
        return None
    match = re.search(r'(\d{1,2})', str(grade_str))
    if match:
        val = int(match.group(1))
        if 1 <= val <= 70:
            return val
    return None


def verify_coin_identification(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a candidate coin identification against physical and historical catalog constraints.
    
    Returns:
        {
            "is_valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "sanitized": dict
        }
    """
    errors: List[str] = []
    warnings: List[str] = []
    sanitized: Dict[str, Any] = dict(candidate)

    # 1. Year Validation
    raw_year = candidate.get("year")
    year_val: Optional[int] = None
    if raw_year is not None:
        try:
            year_val = int(str(raw_year).strip())
            if year_val < 1792 or year_val > 2030:
                errors.append(f"Invalid US coin year {year_val}: US coinage mintage spans 1792-2026.")
        except ValueError:
            errors.append(f"Non-numeric year provided: '{raw_year}'")
    else:
        warnings.append("No year provided in candidate identification.")

    # 2. Grade Validation
    raw_grade = candidate.get("grade")
    if raw_grade:
        num_grade = parse_sheldon_grade(raw_grade)
        if num_grade is not None:
            if num_grade not in VALID_SHELDON_NUMBERS:
                errors.append(f"Invalid Sheldon grade number '{num_grade}'. Standard Sheldon scale uses discrete steps (e.g., 50, 53, 55, 58, 60-70).")
        else:
            # Check for qualitative grades (e.g., 'Ungraded', 'Details', 'Cleaned')
            upper_grade = str(raw_grade).upper()
            if not any(k in upper_grade for k in ["DETAILS", "GENUINE", "UNGRADED", "RAW", "UNC"]):
                warnings.append(f"Unrecognized grade format '{raw_grade}'.")

    # 3. Series & Mint Mark Mintage Rules
    series_name = str(candidate.get("program_series") or candidate.get("series") or "").strip().lower()
    mint_mark = str(candidate.get("mint_mark") or "").strip().upper()
    if mint_mark in ["NONE", "NO MINT MARK", "PHILADELPHIA"]:
        mint_mark = ""

    # Normalize series lookup
    matched_rule_key = None
    for rule_key in US_MINT_RULES:
        if rule_key in series_name:
            matched_rule_key = rule_key
            break

    if matched_rule_key and year_val:
        rule = US_MINT_RULES[matched_rule_key]
        if year_val < rule["start"] or year_val > rule["end"]:
            errors.append(f"Historical date mismatch: '{matched_rule_key.title()}' was only minted from {rule['start']} to {rule['end']}, but received year {year_val}.")
        else:
            # Check valid mint marks for this specific year
            mint_allowed = False
            valid_mints_for_year: List[str] = []
            for (y_start, y_end), mints in rule["valid_mints"].items():
                if y_start <= year_val <= y_end:
                    valid_mints_for_year.extend(mints)
                    if mint_mark in mints:
                        mint_allowed = True
                        break
            if not mint_allowed and valid_mints_for_year:
                display_mints = [m if m else '(Philadelphia / No Mint Mark)' for m in set(valid_mints_for_year)]
                errors.append(
                    f"Invalid mint mark '{mint_mark or 'No Mint'}' for {year_val} {matched_rule_key.title()}. "
                    f"Valid mints for {year_val} are: {', '.join(display_mints)}."
                )

    # 4. Metal Composition Sanity Checks
    metal = str(candidate.get("metal_content") or candidate.get("metal") or "").lower()
    if year_val and matched_rule_key:
        if "washington quarter" in series_name or "quarter" in series_name:
            if year_val <= 1964 and "copper-nickel" in metal:
                errors.append(f"Composition error: {year_val} quarters are 90% Silver, not Copper-Nickel clad.")
            elif 1965 <= year_val <= 2026 and "90% silver" in metal and "silver proof" not in str(candidate.get("strike", "")).lower():
                warnings.append(f"Standard {year_val} Washington Quarters are Copper-Nickel Clad (unless special Silver Proof issue).")

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "sanitized": sanitized
    }
