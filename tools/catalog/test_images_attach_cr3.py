#!/usr/bin/env python3
"""
tools/catalog/test_images_attach_cr3.py
Regression and fail-closed negative tests for CR3 catalog image attach (v1.1).
Covers P5 URL negatives, D3/N1 license allow-list, N2 pii_gate masking on both
dry-run and live main() paths, m1 7-key mapping, CM-1 planted captions, P10,
live 3,202-row audit, and S1 1799 $5 recode hold check.
"""

import csv
import hashlib
import json
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TOOLS_CATALOG_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_CATALOG_DIR not in sys.path:
    sys.path.insert(0, TOOLS_CATALOG_DIR)

import apply_image_attach  # noqa: E402
import build_public_catalog  # noqa: E402
import image_license_allowlist  # noqa: E402
import pii_gate_validator  # noqa: E402

LIVE_CATALOG_PATH = os.path.join(
    REPO_ROOT, "numista_mobile", "assets", "catalog", "catalog_public_v1.json"
)
MANIFEST_V4_ENV = "CR3_MANIFEST_V4_PATH"


def _make_manifest_row(**overrides):
    row = {
        "nac1": "NAC1.CN.US.25C.QUARTER.2026.P.MAYFLOWERC.K",
        "title": "2026-P Test Quarter",
        "series": "Semiquincentennial Quarters",
        "year": "2026",
        "denomination": "Quarter",
        "row_mint": "P",
        "presentation": "unique",
        "both_unique": "Y",
        "confidence": "high",
        "obverse_object_path": "gs://numista-reference-library/test/obv.jpg",
        "obverse_public_url": "https://storage.googleapis.com/numista-reference-library/reference_library/test/obv.jpg",
        "obverse_http_status": "200",
        "obverse_content_type": "image/jpeg",
        "obverse_bytes": "12345",
        "obverse_source": "Image: United States Mint",
        "obverse_provenance_note": "INTERNAL copied from /workspace/coin_image_index in this pass",
        "obverse_license_class": "US_MINT_PD",
        "obverse_license": image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS["US_MINT_PD"],
        "obverse_credit": "Image: United States Mint",
        "obverse_source_url": "https://www.usmint.gov/news/image-library/test",
        "obverse_file_page_url": "https://commons.wikimedia.org/wiki/File:ShouldNeverWriteObv.jpg",
        "obverse_license_basis": "Internal license basis notes",
        "obverse_unique_side": "Y",
        "obverse_target_field": "primary_image",
        "obverse_mint_match": "Y",
        "obverse_needs_thumbnail": "N",
        "obverse_app_hostable": "Y",
        "reverse_object_path": "gs://us_mint_coin_images/test/rev.jpg",
        "reverse_public_url": "https://storage.googleapis.com/us_mint_coin_images/test/rev.jpg",
        "reverse_http_status": "200",
        "reverse_content_type": "image/jpeg",
        "reverse_bytes": "12346",
        "reverse_source": "National Numismatic Collection, National Museum of American History (photograph by Jaclyn Nash)",
        "reverse_provenance_note": "INTERNAL reverse provenance note",
        "reverse_license_class": "PD-US-SI",
        "reverse_license": image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS["PD-US-SI"],
        "reverse_credit": "National Numismatic Collection, National Museum of American History (photograph by Jaclyn Nash)",
        "reverse_source_url": "https://commons.wikimedia.org/wiki/File:TestRev.jpg",
        "reverse_file_page_url": "https://commons.wikimedia.org/wiki/File:ShouldNeverWriteRev.jpg",
        "reverse_license_basis": "Internal reverse basis",
        "reverse_unique_side": "N",
        "reverse_target_field": "extra_images[]",
        "reverse_mint_match": "Y",
        "reverse_needs_thumbnail": "N",
        "reverse_app_hostable": "Y",
        "catalog_side_class": "catalog_none",
        "replace_vs_keep": "replace",
        "needs_hosting": "N",
        "m2_resolution": "resolved",
        "m3_resolution": "resolved",
        "m4_resolution": "resolved",
        "sacagawea_duplicate_note": "internal dup note",
        "notes": "internal notes /workspace",
        "unknown_reason": "internal reason",
        "target_field": "primary_image",
        "field_being_replaced": "current_value",
        "current_value": "collection-seed/obv.jpg",
        "action": "add",
        "primary_image_action": "add",
        "primary_image_current_value": "collection-seed/cur.jpg",
        "primary_image_write": "yes",
        "type_image_action": "none",
        "type_image_current_value": "collection-seed/type.jpg",
        "extra_images_action": "add",
        "extra_images_current_value": "",
        "d2_cohort": "cohort1",
        "d2_resolution": "resolved",
        "dm1_resolution": "resolved",
        "obverse_uniqueness_reason": "exact mint",
        "reverse_uniqueness_reason": "representative",
        "thumbnail_spec": "400x400",
        "source_write_rule": "source=credit",
        "local_path": "/workspace/local/should_never_write.jpg",
    }
    row.update(overrides)
    return row


def _write_csv(path, rows):
    fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return apply_image_attach.file_sha256(str(path))


def test_p5_url_allowlist_positives_and_all_negatives():
    approved = [
        "https://storage.googleapis.com/us_mint_coin_images/2026_quarter_obv.jpg",
        " https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/2024_atb_rev.jpg ",
        "https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/1999_nj_rev.jpg",
        "assets/catalog/images/morgan_1921.jpg",
    ]
    for url in approved:
        assert build_public_catalog.is_approved_image_url(url), f"Expected approved: {url}"

    rejected = [
        # Lookalike buckets
        "https://storage.googleapis.com/numista-reference-library-evil/coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images-x/coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images_evil/coin.jpg",
        "https://storage.googleapis.com/numista-reference-libraryx/coin.jpg",
        # Userinfo @ in both forms + bare @
        "https://user@storage.googleapis.com/us_mint_coin_images/coin.jpg",
        "https://user:secret@storage.googleapis.com/us_mint_coin_images/coin.jpg",
        "https://@storage.googleapis.com/us_mint_coin_images/coin.jpg",
        # Host prefix/suffix & firebasestorage
        "https://evil.storage.googleapis.com/us_mint_coin_images/coin.jpg",
        "https://storage.googleapis.com.evil.com/us_mint_coin_images/coin.jpg",
        "https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fu1%2Fphoto.jpg?alt=media",
        "https://firebasestorage.googleapis.com/v0/b/studio/o/coin.jpg",
        # Ports including :443
        "https://storage.googleapis.com:443/us_mint_coin_images/coin.jpg",
        "https://storage.googleapis.com:8443/us_mint_coin_images/coin.jpg",
        "https://storage.googleapis.com:/us_mint_coin_images/coin.jpg",
        # http://
        "http://storage.googleapis.com/us_mint_coin_images/coin.jpg",
        "http://storage.googleapis.com/numista-reference-library/coin.jpg",
        # Raw or encoded traversal & backslashes
        "https://storage.googleapis.com/us_mint_coin_images/../secret/coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/a/../coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/./coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/%2e%2e/secret/coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/%2E/coin.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/a%2fb.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/a%2Fb.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/a%5cb.jpg",
        "https://storage.googleapis.com/us_mint_coin_images/a%5Cb.jpg",
        "https://storage.googleapis.com/us_mint_coin_images\\coin.jpg",
        "assets/catalog/images/../../secret.png",
        "assets/catalog/images/",
        # numista-public & uploads-studio (ALL paths off in Python)
        "https://storage.googleapis.com/numista-public/coin.jpg",
        "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/u1/orig.jpg",
        "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/fixture_program/fixture.jpg",
        "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference",
        # Wikimedia, Met, ANS, and other external hosts
        "https://upload.wikimedia.org/wikipedia/commons/6/69/Coin.jpg",
        "https://commons.wikimedia.org/wiki/File:Coin.jpg",
        "https://images.metmuseum.org/CRDImages/an/web-large/coin.jpg",
        "https://numismatics.org/collectionimages/1950/coin.jpg",
        "https://example.com/coin.jpg",
        # Greysheet hosts and gsid
        "https://www.greysheet.com/images/gsid/12345.jpg",
        "https://cdn.greysheet.com/gsid/12345.jpg",
        "https://storage.googleapis.com/gsid-cache/12345.jpg",
        # Signed / query / fragment / encoded ? and # on approved buckets (D2, N2)
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg?X-Goog-Signature=deadbeef",
        "https://storage.googleapis.com/numista-reference-library/coin.jpg?GoogleAccessId=a@b&Expires=999999&Signature=xyz",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg?alt=media",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg?",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg#fragment",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg#",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg%3Falt=media",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg%3falt=media",
        "https://storage.googleapis.com/us_mint_coin_images/coin.jpg%23fragment",
        # Non-strings / empty / bare bucket
        "",
        None,
        "https://storage.googleapis.com/us_mint_coin_images/",
        "https://storage.googleapis.com/us_mint_coin_images",
    ]
    for url in rejected:
        assert not build_public_catalog.is_approved_image_url(url), f"Expected rejected: {url!r}"


def test_d3_n1_license_allowlist_and_fail_closed_fixtures(tmp_path):
    # Exact 4 v4 classes only (N1: no CC0 category; PD-US-SI is not CC0)
    assert set(image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS.keys()) == {
        "US_MINT_PD",
        "PD-US-SI",
        "WIKIMEDIA_PD_CONFIRMED",
        "WIKIMEDIA_PD_OWN_WORK",
    }
    assert "CC0" not in image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS

    # All 4 certified classes pass
    for cls, lic in image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS.items():
        assert image_license_allowlist.is_certified_license(lic)
        assert image_license_allowlist.is_certified_license(lic, cls)
        cleaned = build_public_catalog.sanitize_image_dict(
            {
                "url": "https://storage.googleapis.com/numista-reference-library/test/coin.jpg",
                "license": lic,
                "credit": "Test Credit",
            },
            build_public_catalog.PRIMARY_IMAGE_KEYS,
        )
        assert cleaned is not None and cleaned["license"] == lic

    # Specifically confirm PD-US-SI is NOT treated as CC0
    pd_us_si = image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS["PD-US-SI"]
    assert image_license_allowlist.is_certified_license(pd_us_si, "PD-US-SI")
    assert not image_license_allowlist.is_certified_license(pd_us_si, "CC0")

    bad_licenses = [
        ("missing", None),
        ("empty", ""),
        ("whitespace", "   "),
        ("cc_by_sa", "CC BY-SA 4.0"),
        ("all_rights_reserved", "All rights reserved"),
        ("cc0", "CC0 1.0 Universal"),
        ("cc0_plain", "CC0"),
        ("lookalike_no_section_symbol", "Public domain (US government work, 17 U.S.C. 105)"),
        ("lookalike_trailing_space", image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS["US_MINT_PD"] + " "),
        ("lookalike_case", image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS["WIKIMEDIA_PD_CONFIRMED"].upper()),
        ("lookalike_pd_us_si_cc0", "Public domain (PD-US-SI; Smithsonian Open Access CC0)"),
    ]

    target_path = tmp_path / "target.json"
    target_path.write_text(
        json.dumps([{"nac_code": "NAC1.CN.US.25C.QUARTER.2026.P.MAYFLOWERC.K", "name": "Test"}]),
        encoding="utf-8",
    )

    for tag, bad_lic in bad_licenses:
        # 1) Builder sanitize drops GCS image object fail-closed
        dropped = []
        img = {
            "url": "https://storage.googleapis.com/us_mint_coin_images/test.jpg",
            "credit": "Image: United States Mint",
        }
        if bad_lic is not None:
            img["license"] = bad_lic
        res = build_public_catalog.sanitize_image_dict(
            img,
            build_public_catalog.PRIMARY_IMAGE_KEYS,
            nac_code="NAC1.TEST",
            field_name="primary_image",
            dropped_report=dropped,
        )
        assert res is None, f"sanitize_image_dict did not drop {tag}: {bad_lic!r}"
        assert len(dropped) == 1 and dropped[0]["reason"] == "uncertified_or_missing_license"

        # 2) Write script stops BEFORE writing anything
        row = _make_manifest_row(obverse_license="" if bad_lic is None else bad_lic)
        manifest_path = tmp_path / f"manifest_{tag}.csv"
        sha = _write_csv(manifest_path, [row])
        out_path = tmp_path / f"out_{tag}.json"
        with pytest.raises(ValueError):
            apply_image_attach.apply_image_attach(
                manifest_path=str(manifest_path),
                target_path=str(target_path),
                output_path=str(out_path),
                expected_sha256=sha,
            )
        assert not out_path.exists(), f"Write script must not write on {tag}"

    # Verify sanitize also drops GCS dict with rejected query/signed URL even if license is certified
    dropped_url = []
    assert build_public_catalog.sanitize_image_dict(
        {
            "url": "https://storage.googleapis.com/us_mint_coin_images/test.jpg?X-Goog-Signature=bad",
            "license": image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS["US_MINT_PD"],
        },
        build_public_catalog.PRIMARY_IMAGE_KEYS,
        nac_code="NAC1.TEST",
        field_name="primary_image",
        dropped_report=dropped_url,
    ) is None
    assert dropped_url and dropped_url[0]["reason"] == "unapproved_gcs_url"


def test_part2_key_lists_and_live_3202_catalog_zero_drops():
    assert "thumb_url" in build_public_catalog.PRIMARY_IMAGE_KEYS
    for k in ("license", "credit", "source", "source_url", "unique_side", "full_url", "thumb_url"):
        assert k in build_public_catalog.TYPE_IMAGE_KEYS
    for k in ("source", "thumb_url"):
        assert k in build_public_catalog.EXTRA_IMAGE_KEYS

    with open(LIVE_CATALOG_PATH, "r", encoding="utf-8") as f:
        live_records = json.load(f)
    assert len(live_records) == 3202
    dropped = build_public_catalog.audit_catalog_images(live_records)
    assert dropped == [], f"Live catalog lost images: {dropped}"


def test_n2_pii_gate_masking_dry_run_and_live_main(tmp_path):
    # Whitelist and forbidden tokens must remain unchanged (no blanket googleapis whitelist)
    assert all("googleapis" not in wl.lower() for wl in pii_gate_validator.EXACT_WHITELIST)
    assert r"googleapis" in pii_gate_validator.FORBIDDEN_TOKENS
    assert r"gs://" in pii_gate_validator.FORBIDDEN_TOKENS

    approved_url = "https://storage.googleapis.com/numista-reference-library/reference_library/test/coin.jpg"
    clean_doc = [
        {
            "nac_code": "NAC1.TEST.1",
            "name": "Test Coin",
            "primary_image": {
                "url": approved_url,
                "full_url": approved_url,
                "thumb_url": approved_url,
                "credit": "Image: United States Mint",
                "source": "Image: United States Mint",
            },
            "type_image": {"url": approved_url},
            "extra_images": [{"url": approved_url, "side": "reverse"}],
            "history": "Clean historical background.",
            "sources": [{"label": "US Mint Media Kit", "url": "https://www.usmint.gov/news/image-library"}],
        }
    ]
    clean_file = tmp_path / "clean.json"
    clean_file.write_text(json.dumps(clean_doc), encoding="utf-8")

    # Both dry-run and live main() PASS when approved URL is only in url/full_url/thumb_url
    assert pii_gate_validator.run_dry_run(str(clean_file)) == 0
    proc_clean = subprocess.run(
        [sys.executable, os.path.join(TOOLS_CATALOG_DIR, "pii_gate_validator.py"), "--input", str(clean_file)],
        capture_output=True,
        text=True,
    )
    assert proc_clean.returncode == 0, proc_clean.stderr
    assert "GATE PASSED" in proc_clean.stdout

    # Same URL text inside history MUST FAIL both dry-run and live main()
    history_leak_doc = json.loads(json.dumps(clean_doc))
    history_leak_doc[0]["history"] = f"Copied from {approved_url}"
    history_file = tmp_path / "history_leak.json"
    history_file.write_text(json.dumps(history_leak_doc), encoding="utf-8")
    assert pii_gate_validator.run_dry_run(str(history_file)) == 1
    proc_hist = subprocess.run(
        [sys.executable, os.path.join(TOOLS_CATALOG_DIR, "pii_gate_validator.py"), "--input", str(history_file)],
        capture_output=True,
        text=True,
    )
    assert proc_hist.returncode == 1
    assert "GATE FAILED" in proc_hist.stderr

    # Same URL text inside sources[].label MUST FAIL both dry-run and live main()
    label_leak_doc = json.loads(json.dumps(clean_doc))
    label_leak_doc[0]["sources"][0]["label"] = f"Mirror at {approved_url}"
    label_file = tmp_path / "label_leak.json"
    label_file.write_text(json.dumps(label_leak_doc), encoding="utf-8")
    assert pii_gate_validator.run_dry_run(str(label_file)) == 1
    proc_lbl = subprocess.run(
        [sys.executable, os.path.join(TOOLS_CATALOG_DIR, "pii_gate_validator.py"), "--input", str(label_file)],
        capture_output=True,
        text=True,
    )
    assert proc_lbl.returncode == 1

    # Same URL text inside sources[].url MUST FAIL both (sources is excluded from masking)
    src_url_leak = json.loads(json.dumps(clean_doc))
    src_url_leak[0]["sources"][0]["url"] = approved_url
    src_url_file = tmp_path / "src_url_leak.json"
    src_url_file.write_text(json.dumps(src_url_leak), encoding="utf-8")
    assert pii_gate_validator.run_dry_run(str(src_url_file)) == 1

    # Unapproved GCS / signed / uploads-studio URL in primary_image.url MUST FAIL both
    unapproved_doc = json.loads(json.dumps(clean_doc))
    unapproved_doc[0]["primary_image"]["url"] = (
        "https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/u1/x.jpg"
    )
    unapproved_file = tmp_path / "unapproved.json"
    unapproved_file.write_text(json.dumps(unapproved_doc), encoding="utf-8")
    assert pii_gate_validator.run_dry_run(str(unapproved_file)) == 1


def test_m1_explicit_7_key_mapping_never_writes_internal_columns():
    row = _make_manifest_row(
        obverse_credit="Image: United States Mint",
        obverse_source="DIFFERENT INTERNAL SOURCE SHOULD BE IGNORED OR CAUGHT",
    )
    # Using clean matching source for build_side_image_object check:
    row["obverse_source"] = "Image: United States Mint"
    obv_obj = apply_image_attach.build_side_image_object(row, "obverse")
    rev_obj = apply_image_attach.build_side_image_object(row, "reverse")

    expected_keys = ("url", "side", "unique_side", "license", "credit", "source", "source_url")
    assert tuple(obv_obj.keys()) == expected_keys
    assert tuple(rev_obj.keys()) == expected_keys
    assert obv_obj["source"] == obv_obj["credit"] == "Image: United States Mint"
    assert rev_obj["source"] == rev_obj["credit"]
    assert obv_obj["unique_side"] is True
    assert rev_obj["unique_side"] is False

    # None of the internal / *_file_page_url values may leak into serialized objects
    dumped = json.dumps([obv_obj, rev_obj])
    for forbidden_substr in (
        "ShouldNeverWrite",
        "should_never_write",
        "provenance_note",
        "gs://",
        "/workspace",
        "collection-seed",
        "coin_image_index",
        "this pass",
        "sacagawea_duplicate_note",
    ):
        assert forbidden_substr not in dumped


def test_cm1_planted_internal_caption_fails_p10_and_write(tmp_path):
    planted_records = [
        {
            "nac_code": "NAC1.CN.US.25C.QUARTER.2026.P.MAYFLOWERC.K",
            "primary_image": {
                "url": "https://storage.googleapis.com/us_mint_coin_images/ok.jpg",
                "source": "re-pointed in this pass from /workspace/coin_image_index",
                "unique_side": True,
            },
        }
    ]
    hits = apply_image_attach.scan_rendered_captions_p10(planted_records)
    assert hits, "Planted internal caption in source must fail P10"

    target_path = tmp_path / "target.json"
    target_path.write_text(
        json.dumps([{"nac_code": "NAC1.CN.US.25C.QUARTER.2026.P.MAYFLOWERC.K"}]),
        encoding="utf-8",
    )
    row = _make_manifest_row(obverse_source="No copy /workspace re-pointed")
    manifest_path = tmp_path / "manifest_cm1.csv"
    sha = _write_csv(manifest_path, [row])
    out_path = tmp_path / "out_cm1.json"
    with pytest.raises(ValueError, match="P10"):
        apply_image_attach.apply_image_attach(
            manifest_path=str(manifest_path),
            target_path=str(target_path),
            output_path=str(out_path),
            expected_sha256=sha,
        )
    assert not out_path.exists()


def test_apply_image_attach_no_network_imports_and_sha_check(tmp_path):
    src = open(os.path.join(TOOLS_CATALOG_DIR, "apply_image_attach.py"), "r", encoding="utf-8").read()
    for net_mod in ("urllib.request", "import requests", "http.client", "google.cloud"):
        assert net_mod not in src, f"Offline attach script must not import {net_mod}"

    row = _make_manifest_row()
    manifest_path = tmp_path / "manifest.csv"
    _write_csv(manifest_path, [row])
    target_path = tmp_path / "target.json"
    target_path.write_text(json.dumps([{"nac_code": row["nac1"]}]), encoding="utf-8")
    out_path = tmp_path / "out.json"

    with pytest.raises(ValueError, match="mismatch"):
        apply_image_attach.apply_image_attach(
            manifest_path=str(manifest_path),
            target_path=str(target_path),
            output_path=str(out_path),
            expected_sha8="00000000",
        )
    assert not out_path.exists()


def test_pii_gate_dry_run_on_manifest_v4_public_columns_and_e2e_attach(tmp_path):
    manifest_path = os.environ.get(MANIFEST_V4_ENV)
    if not manifest_path:
        # CI fallback: verify public columns extraction + pii_gate pass on 4-class synthetic rows
        rows = [
            _make_manifest_row(
                nac1="NAC1.CN.US.25C.QUARTER.2026.P.MAYFLOWERC.K",
                obverse_license_class=cls,
                obverse_license=lic,
                reverse_license_class=cls,
                reverse_license=lic,
            )
            for cls, lic in image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS.items()
        ]
        public_doc = [
            {
                "nac_code": r["nac1"],
                "primary_image": apply_image_attach.build_side_image_object(r, "obverse"),
                "extra_images": [apply_image_attach.build_side_image_object(r, "reverse")],
            }
            for r in rows
        ]
        assert pii_gate_validator.scan_document_for_leaks(public_doc) == []
        return

    assert os.path.exists(manifest_path), f"Missing {manifest_path}"
    assert apply_image_attach.file_sha256(manifest_path)[:8] == "58ac149a"

    with open(manifest_path, "r", encoding="utf-8", newline="") as f:
        v4_rows = list(csv.DictReader(f))
    assert len(v4_rows) == 487

    # S1: assert zero 1799 $5 rows in manifest and live catalog
    for r in v4_rows:
        assert not ("1799" in r["nac1"] and "GD5" in r["nac1"])

    # Match attach_manifest_v4_pii_gate_scan_20261123.json public-column scan (0 leaks)
    public_cols = [
        "obverse_source",
        "reverse_source",
        "obverse_credit",
        "reverse_credit",
        "obverse_license",
        "reverse_license",
        "obverse_source_url",
        "reverse_source_url",
        "obverse_file_page_url",
        "reverse_file_page_url",
    ]
    public_scan_doc = []
    seen_pairs = set()
    for r in v4_rows:
        seen_pairs.add((r["obverse_license_class"], r["obverse_license"]))
        seen_pairs.add((r["reverse_license_class"], r["reverse_license"]))
        entry = {
            "primary_image": {
                "url": r["obverse_public_url"],
                "source": r["obverse_source"],
                "credit": r["obverse_credit"],
                "license": r["obverse_license"],
                "source_url": r["obverse_source_url"],
            },
            "extra_images": [
                {
                    "url": r["reverse_public_url"],
                    "source": r["reverse_source"],
                    "credit": r["reverse_credit"],
                    "license": r["reverse_license"],
                    "source_url": r["reverse_source_url"],
                }
            ],
            "public_file_pages": {
                "obv": r["obverse_file_page_url"],
                "rev": r["reverse_file_page_url"],
            },
        }
        for col in public_cols:
            assert col in r
        public_scan_doc.append(entry)

    assert seen_pairs == set(image_license_allowlist.CERTIFIED_LICENSE_BY_CLASS.items())

    public_json = tmp_path / "v4_public_columns.json"
    public_json.write_text(json.dumps(public_scan_doc, ensure_ascii=False), encoding="utf-8")
    assert pii_gate_validator.run_dry_run(str(public_json)) == 0
    proc = subprocess.run(
        [sys.executable, os.path.join(TOOLS_CATALOG_DIR, "pii_gate_validator.py"), "--input", str(public_json)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "GATE PASSED" in proc.stdout

    # Run full 6-step offline apply_image_attach on a temp copy of catalog_public_v1.json
    target_copy = tmp_path / "catalog_public_copy.json"
    target_copy.write_bytes(open(LIVE_CATALOG_PATH, "rb").read())
    output_copy = tmp_path / "catalog_public_attached.json"
    backup_copy = tmp_path / "catalog_public_copy.bak.json"

    report = apply_image_attach.apply_image_attach(
        manifest_path=manifest_path,
        target_path=str(target_copy),
        output_path=str(output_copy),
        expected_sha8="58ac149a",
        backup_path=str(backup_copy),
    )
    assert report["rows_applied"] == 487
    assert report["primary_image_writes"] == 296
    assert report["type_image_writes"] == 191
    assert report["extra_images_replaces"] == 2
    assert report["backup_md5"] == report["target_pre_md5"]
    assert report["output_md5"] == apply_image_attach.file_md5(str(output_copy))
    assert report["sanitize_dropped"] == 0
    assert report["pii_gate_leaks"] == 0
    assert report["p10_hits"] == 0

    # Ensure 191 type_image rows have primary_image == None so type_image is never masked
    attached = json.loads(output_copy.read_text(encoding="utf-8"))
    assert len(attached) == 3202
    by_nac = {c["nac_code"]: c for c in attached}
    for r in v4_rows:
        c = by_nac[r["nac1"]]
        if r["obverse_target_field"] == "type_image":
            assert c["primary_image"] is None
            assert tuple(c["type_image"].keys()) == apply_image_attach.ALLOWED_IMAGE_KEYS
        else:
            assert tuple(c["primary_image"].keys()) == apply_image_attach.ALLOWED_IMAGE_KEYS
        assert any(
            ex.get("side") == "reverse" and tuple(ex.keys()) == apply_image_attach.ALLOWED_IMAGE_KEYS
            for ex in (c.get("extra_images") or [])
        )
        # Confirm stale NNC Wikimedia obverse extra_image was replaced
        if (r.get("extra_images_action") or "").startswith("replace"):
            assert len(c["extra_images"]) == 1
            assert c["extra_images"][0]["side"] == "reverse"


def test_s1_1799_5_recode_hold_intact():
    with open(LIVE_CATALOG_PATH, "r", encoding="utf-8") as f:
        live = json.load(f)
    hits_live = [
        c.get("nac_code")
        for c in live
        if "1799" in (c.get("nac_code") or "") and "GD5" in (c.get("nac_code") or "")
    ]
    assert hits_live == []
