"""
Unit tests for Numista.AI Checklist Notes & Storage Parser
Verifies 100% of real-world annotations from test checklists.
"""

import pytest
from services.checklist_parser import parse_checklist_notes, slugify_theme

def test_empty_notes():
    res = parse_checklist_notes("")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["condition"] == "Unspecified / Raw"
    assert res["storage_location"] == ""
    assert res["confidence_score"] == 1.0

def test_atb_p_tube():
    res = parse_checklist_notes("ATB-P tube")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "ATB-P tube"
    assert res["condition"] == "Unspecified / Raw"
    assert res["confidence_score"] == 1.0

def test_atb_d_tube():
    res = parse_checklist_notes("ATB -D tube")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "ATB-D tube"
    assert res["condition"] == "Unspecified / Raw"
    assert res["confidence_score"] == 1.0

def test_atb_p_tube_proof_condition():
    res = parse_checklist_notes("ATB-P tube – 79 Proof Condition")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "ATB-P tube"
    assert res["condition"] == "Proof"
    assert "79 Proof Condition" in res["personal_notes"]

def test_already_have_zero():
    res = parse_checklist_notes("Already have 0")
    assert res["is_owned"] is False
    assert res["quantity"] == 0
    assert res["storage_location"] == ""
    assert res["flag"] == "unselected_zero_ownership"

def test_have_zero():
    res = parse_checklist_notes("Have 0")
    assert res["is_owned"] is False
    assert res["quantity"] == 0

def test_zero_only():
    res = parse_checklist_notes("0")
    assert res["is_owned"] is False
    assert res["quantity"] == 0

def test_safe_box_ms65():
    res = parse_checklist_notes("Safe Box 2, MS65 BU, QTY: 3")
    assert res["is_owned"] is True
    assert res["quantity"] == 3
    assert res["storage_location"] == "Safe Box 2"
    assert res["condition"] == "MS65"
    assert "BU" in res["personal_notes"]

def test_2x2_box():
    res = parse_checklist_notes("2x2 Box 3")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "Box 3"
    assert "2x2" in res["personal_notes"]

def test_dansco_album():
    res = parse_checklist_notes("Dansco Album p. 4")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "Dansco Album p. 4"

def test_unc_roll():
    res = parse_checklist_notes("UNC Roll")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "UNC Roll"
    assert res["condition"] == "Uncirculated"

def test_proof_set_box():
    res = parse_checklist_notes("Proof Set box")
    assert res["is_owned"] is True
    assert res["quantity"] == 1
    assert res["storage_location"] == "Proof Set Box"
    assert res["condition"] == "Proof"

def test_theme_slugification():
    assert slugify_theme("Hot Springs (AR)") == "hot_springs"
    assert slugify_theme("Hot Springs National Park (AR)") == "hot_springs"
    assert slugify_theme("Yellowstone National Park (WY)") == "yellowstone"
    assert slugify_theme("Yosemite National Park (CA)") == "yosemite"
    assert slugify_theme("Grand Canyon National Park (AZ)") == "grand_canyon"
    assert slugify_theme("District of Columbia (DC)") == "district_of_columbia"
    assert slugify_theme("Puerto Rico (PR)") == "puerto_rico"
