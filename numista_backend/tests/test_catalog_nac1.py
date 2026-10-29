"""NAC1 grammar / checksum gate (Plan.v2.1 section 2.2 canonical vectors)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from catalog_nac1 import (  # noqa: E402
    KIND_TO_COLLECTION,
    NAC1_REGEX,
    build_nac1,
    compute_nac1_chk,
    nac1_cc,
    nac1_kind,
    parse_nac1,
    validate_nac1,
)

# All 14 canonical verified NAC1 vectors from Plan.v2.2 §2.2 + extra fixture anchors
VECTORS = [
    ("NAC1.CN.CO.1C.FUGIO.1787.XX.BASE", "K"),
    ("NAC1.CN.US.G5.LIBCAP.1838.DD.BASE", "3"),
    ("NAC1.CN.US.1D.MORGAN.1881.S.BASE", "E"),
    ("NAC1.CN.US.1D.MORGAN.1921.P.BASE", "4"),
    ("NAC1.CN.US.5C.BUFFALO.1937.D.3LEG", "3"),
    ("NAC1.CN.US.25C.AWQ.2022.P.MAYA", "Z"),
    ("NAC1.CN.US.1D.ASE.2024.W.PRF", "S"),
    ("NAC1.BN.US.FRN1.FED.2017A.BEP.BASE", "6"),
    ("NAC1.BN.US.TN1000.TREAS.1890.BEP.WM", "C"),
    ("NAC1.MD.US.PRES.PRES.1923.P.COOL", "W"),
    ("NAC1.CN.PF.1P.PHL1P.1903.S.BASE", "3"),
    ("NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE", "P"),
    ("NAC1.MD.US.PRV.CWT.1863.XX.BASE", "H"),
    ("NAC1.TK.US.PRV.CWT.1863.XX.BASE", "T"),
    # Extra fixture anchors
    ("NAC1.CN.CO.1C.CT.1787.XX.DRAPED", "V"),
    ("NAC1.BN.US.SC5.SILV.1899.BEP.BASE", "A"),
]


@pytest.mark.parametrize("payload,chk", VECTORS)
def test_canonical_vectors(payload, chk):
    assert compute_nac1_chk(payload) == chk
    assert validate_nac1(f"{payload}.{chk}")
    assert build_nac1(payload) == f"{payload}.{chk}"


def test_wrong_check_digit_rejected():
    assert not validate_nac1("NAC1.CN.US.1D.MORGAN.1881.S.BASE.F")


@pytest.mark.parametrize("bad", [
    None, 123, "", "NAC1", "nac1.cn.us.1d.morgan.1881.s.base.e",
    "NAC1.XX.US.1D.MORGAN.1881.S.BASE.E",        # bad kind
    "NAC1.CN.GB.1D.MORGAN.1881.S.BASE.E",        # non-Circulating foreign ISO code rejected
    "NAC1.CN.US.1D.MORGAN.1881.Z.BASE.E",        # bad facility
    "NAC1.CN.US.1D.MORGAN.1881.S.BASE.U",        # 'U' not in Crockford alphabet
    "NAC1.CN.US.1D.MORGAN.1881.S.BASE.E.EXTRA",
])
def test_malformed_rejected(bad):
    assert not validate_nac1(bad)


def test_kind_routing_never_sends_non_coins_to_coins():
    assert KIND_TO_COLLECTION["CN"] == "coins"
    assert KIND_TO_COLLECTION["BN"] == "currency"
    for k in ("MD", "TK", "ST"):
        assert KIND_TO_COLLECTION[k] == "world_items"
    assert [k for k, v in KIND_TO_COLLECTION.items() if v == "coins"] == ["CN"]


def test_nac1_kind_and_cc_and_parse():
    assert nac1_kind("NAC1.BN.US.SC5.SILV.1899.BEP.BASE.A") == "BN"
    assert nac1_cc("NAC1.CN.CO.1C.FUGIO.1787.XX.BASE.K") == "CO"
    assert nac1_cc("NAC1.CN.PF.1P.PHL1P.1903.S.BASE.3") == "PF"
    assert nac1_cc("NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P") == "FS"
    parsed = parse_nac1("NAC1.CN.US.G5.LIBCAP.1838.DD.BASE.3")
    assert parsed["facility_code"] == "DD"
    assert parsed["chk"] == "3"
    parsed_mo = parse_nac1("NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P")
    assert parsed_mo["facility_code"] == "MO"
    with pytest.raises(ValueError):
        nac1_kind("garbage")
    with pytest.raises(ValueError):
        nac1_cc("garbage")
    with pytest.raises(ValueError):
        parse_nac1("NAC1.CN.US.1D.MORGAN.1881.S.BASE.F")


@pytest.mark.parametrize("excluded_char", ["I", "L", "O", "U"])
def test_regex_rejects_excluded_crockford_chars_I_L_O_U(excluded_char):
    candidate = f"NAC1.CN.US.1D.MORGAN.1881.S.BASE.{excluded_char}"
    assert NAC1_REGEX.match(candidate) is None
    assert not validate_nac1(candidate)
