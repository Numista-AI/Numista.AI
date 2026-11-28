"""
numista_tests/test_wave2_catalog_and_morgan.py
Comprehensive Wave 2 (Plan cc9d2916) automated verification suite:
- Component C: Catalog-First Morgan AI mouthpiece, disambiguation, privacy isolation, retired auto-scraper
- Component D: Builder v2.1 (d2-3 _ensure_scalar, MF-1 held rows/1875-S/S varieties, MF-5 Collector reference,
               search_aliases 17-row Capped Bust Right, nac_aliases, firebase.json 301s, catalog_nac1.py BN-only NY)
- Component E: Sets / OGP packaging / privy_detail in builder & apply_image_attach
- Component F: 31 CFR § 411.1 AI banknote rules (one-sided obverse, 403 download disabled, allow_marketing_use=false)
- Component G: Minified JSON + split search index
"""

import json
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "numista_backend")
for p in (REPO_ROOT, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from catalog_nac1 import build_nac1, validate_nac1
from catalog_service import (
    CatalogError,
    FREE_TRIAL_ITEM_LIMIT,
    filter_catalog,
    verify_banknote_ai_download_allowed,
)
import morgan_knowledge as mk
from tools.catalog.apply_image_attach import (
    attach_packaging_or_privy_image,
    build_side_image_object,
)
from tools.catalog.build_public_catalog import (
    _ensure_scalar,
    build_public_catalog,
)
from tools.catalog.pii_gate_validator import scan_document_for_leaks, scan_text_for_leaks


class TestWave2Nac1NyConstraint(unittest.TestCase):
    """Component D.6 (Muse 97 / Gemini 99 ruling): NY permitted for BN only."""

    def test_ny_allowed_for_banknote_sheets(self):
        self.assertTrue(validate_nac1("NAC1.BN.US.100.NOTESHEET.2025.NY.B7800.R"))
        self.assertTrue(validate_nac1("NAC1.BN.US.100.NOTESHEET.2025.NY.B7801.S"))

    def test_ny_rejected_for_coins_and_medals_even_with_valid_chk(self):
        bad_coin = build_nac1("NAC1.CN.US.25C.WASHQTR.2025.NY.BASE")
        bad_medal = build_nac1("NAC1.MD.US.PRES.PRESMEDAL.2026.NY.S828")
        self.assertFalse(validate_nac1(bad_coin))
        self.assertFalse(validate_nac1(bad_medal))


class TestWave2BuilderV21Hardening(unittest.TestCase):
    """Components D, E, F, G: d2-3, MF-1..MF-5, OGP/Privy, 31 CFR § 411.1, minification."""

    def test_ensure_scalar_rejects_nested_collections(self):
        self.assertEqual(_ensure_scalar("ok", "f"), "ok")
        self.assertEqual(_ensure_scalar(123, "f"), 123)
        self.assertIsNone(_ensure_scalar(None, "f"))
        with self.assertRaises(ValueError):
            _ensure_scalar({"nested": 1}, "mintage.value")
        with self.assertRaises(ValueError):
            _ensure_scalar(["bad"], "name")

    def test_builder_drops_held_rows_held_varieties_and_rewrites_mf5_and_cfr411(self):
        sample_rows = [
            # 1. Held row must NEVER emit publicly (MF-1)
            {
                "nac_code": "NAC1.CN.US.20C.TWENTYCENT.1877.P.BASE.6",
                "name": "1877 Twenty-Cent Piece (Held)",
                "type": "coin",
                "year": 1877,
                "held_from_live": True,
            },
            # 2. 1875-S Twenty-Cent with held 1875-S/S variety + MF-5 Collector reference + nac_aliases
            {
                "nac_code": "NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0",
                "nac_aliases": ["NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1"],
                "name": "1875-S twenty-cent piece",
                "type": "coin",
                "year": 1875,
                "denomination": "20 cents",
                "series": "Twenty-Cent Piece",
                "diameter_mm": None,
                "mintage": {"value": 1155000, "label": "1,155,000 pieces (calendar year 1875)", "source_url": "https://fraser.stlouisfed.org/"},
                "figures": {
                    "diameter_mm": {
                        "value": 22,
                        "unit": "mm",
                        "label": "Collector reference: 22 mm standard diameter",
                        "source_url": None,
                    }
                },
                "varieties": [
                    {"name": "1875-S/S repunched mint mark", "visibility": "internal", "held_from_live": True},
                    {"name": "Normal 1875-S", "attribution": "Mint", "reference_work": "Standard"},
                ],
                "sources": [{"label": "Collector reference diameter note", "url": "https://www.usmint.gov/"}],
            },
            # 3. Capped Bust Right row with search_aliases + OGP/privy/permission scrub
            {
                "nac_code": "NAC1.CN.US.GD5.TURBANHEAD.1797.P.HERALDICEA.J",
                "name": "1797 Capped Bust Right $5 Half Eagle (Heraldic Eagle)",
                "type": "coin",
                "year": 1797,
                "denomination": "$5",
                "series": "Capped Bust Right",
                "search_aliases": ["Turban Head", "Draped Bust", "Capped Bust to Right", "Heraldic Eagle"],
                "primary_image": {
                    "url": "https://storage.googleapis.com/us_mint_coin_images/catalog/test_obv.jpg",
                    "side": "obverse",
                    "license": "Public domain (US government work, 17 U.S.C. \u00a7 105)",
                    "credit": "Used with permission of the U.S. Mint",
                    "source": "Courtesy U.S. Mint",
                    "source_url": "https://www.usmint.gov/",
                },
                "packaging_images": [
                    {
                        "url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp",
                        "side": "packaging",
                        "role": "packaging",
                        "license": "Public domain (US government work, 17 U.S.C. \u00a7 105)",
                        "credit": "Image: United States Mint",
                        "source": "Image: United States Mint",
                        "source_url": "https://www.usmint.gov/",
                    }
                ],
                "extra_images": [
                    {
                        "url": "https://storage.googleapis.com/us_mint_coin_images/catalog/test_privy.jpg",
                        "side": "privy_detail",
                        "role": "privy_detail",
                        "license": "Public domain (US government work, 17 U.S.C. \u00a7 105)",
                        "credit": "Image: United States Mint",
                        "source": "Image: United States Mint",
                        "source_url": "https://www.usmint.gov/",
                    }
                ],
                "sources": [],
            },
            # 4. AI Banknote: obverse allowed (allow_marketing_use forced False), AI reverse DROPPED (31 CFR § 411.1)
            {
                "nac_code": "NAC1.BN.US.SC1.SCLARGE.1896.BEP.BASE.D",
                "name": "Series 1896 $1 Silver Certificate",
                "type": "note",
                "year": 1896,
                "denomination": "$1",
                "series": "Silver Certificate",
                "primary_image": {
                    "url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/ai_obv.jpg",
                    "side": "obverse",
                    "ai_generated": True,
                    "allow_marketing_use": True,  # must be forced False!
                    "credit": "AI-generated illustration of the note — not a genuine specimen",
                    "source": "AI-generated illustration of the note — not a genuine specimen",
                },
                "secondary_image": {
                    "url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/ai_rev.jpg",
                    "side": "reverse",
                    "ai_generated": True,
                    "credit": "Should be dropped",
                },
                "sources": [],
            },
        ]

        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "master.jsonl")
            out = os.path.join(td, "catalog_public_v1.json")
            with open(inp, "w", encoding="utf-8") as f:
                for r in sample_rows:
                    f.write(json.dumps(r) + "\n")

            rc = build_public_catalog(inp, out, emit_split_index=True)
            self.assertEqual(rc, 0)
            raw_text = open(out, encoding="utf-8").read()
            # Minified JSON check (no pretty-print newlines/indents)
            self.assertNotIn("\n  ", raw_text)
            built = json.loads(raw_text)
            # Zero PII leaks via N2 document-aware scanner (MF-5 Collector reference rewritten!)
            self.assertEqual(scan_document_for_leaks(built), [])
            # Planted leak negative check
            self.assertGreaterEqual(len(scan_text_for_leaks(raw_text + ' "collector owner gs://x"')), 3)
            self.assertEqual(len(built), 3)  # held 1877 row dropped!
            by_nac = {r["nac_code"]: r for r in built}
            self.assertNotIn("NAC1.CN.US.20C.TWENTYCENT.1877.P.BASE.6", by_nac)

            # 1875-S checks
            r20 = by_nac["NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0"]
            self.assertEqual(r20["nac_aliases"], ["NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1"])
            self.assertEqual(len(r20["varieties"]), 1)
            self.assertEqual(r20["varieties"][0]["name"], "Normal 1875-S")
            self.assertIn("Numismatic reference", r20["figures"]["diameter_mm"]["label"])

            # Capped Bust Right + OGP/privy/credit scrub checks
            rcb = by_nac["NAC1.CN.US.GD5.TURBANHEAD.1797.P.HERALDICEA.J"]
            self.assertIn("Turban Head", rcb["search_aliases"])
            self.assertEqual(rcb["primary_image"]["credit"], "Image: United States Mint")
            self.assertEqual(rcb["primary_image"]["source"], "Image: United States Mint")
            self.assertEqual(rcb["packaging_images"][0]["role"], "packaging")
            self.assertEqual(rcb["extra_images"][0]["role"], "privy_detail")

            # 31 CFR § 411.1 banknote checks
            rbn = by_nac["NAC1.BN.US.SC1.SCLARGE.1896.BEP.BASE.D"]
            self.assertIsNotNone(rbn["primary_image"])
            self.assertFalse(rbn["primary_image"]["allow_marketing_use"])
            self.assertIsNone(rbn["secondary_image"])  # AI reverse dropped fail-closed!

            # Split index emitted cleanly
            self.assertTrue(os.path.exists(os.path.join(td, "catalog_search_index_v1.json")))

    def test_builder_fails_closed_on_greysheet_leak(self):
        bad_row = {
            "nac_code": "NAC1.CN.US.1C.LINCOLN.1909.S.VDB.4",
            "name": "1909-S VDB Lincoln Cent",
            "type": "coin",
            "year": 1909,
            "history": "Leaked https://www.greysheet.com/coin-prices/item/1234",
            "sources": [],
        }
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "bad.jsonl")
            out = os.path.join(td, "out.json")
            open(inp, "w", encoding="utf-8").write(json.dumps(bad_row) + "\n")
            with self.assertRaises(RuntimeError):
                build_public_catalog(inp, out)


class TestWave2AttachHelperAndCFR411Download(unittest.TestCase):
    """Components E & F: OGP/Privy attach helper + 403 AI banknote download guard."""

    def test_packaging_and_privy_attach_helper(self):
        pkg_row = {
            "packaging_public_url": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp",
            "packaging_license": "Public domain (US government work, 17 U.S.C. \u00a7 105)",
            "packaging_license_class": "US_MINT_PD",
            "packaging_unique_side": "Y",
            "packaging_credit": "Image: United States Mint",
            "packaging_source_url": "https://www.usmint.gov/uncirculated-coin-set-2026-26RJ.html",
            "packaging_role": "packaging",
        }
        privy_row = {
            "privy_detail_public_url": "https://storage.googleapis.com/us_mint_coin_images/catalog/26xe_privy.jpg",
            "privy_detail_license": "Public domain (US government work, 17 U.S.C. \u00a7 105)",
            "privy_detail_license_class": "US_MINT_PD",
            "privy_detail_unique_side": "Y",
            "privy_detail_credit": "Image: United States Mint",
            "privy_detail_source_url": "https://www.usmint.gov/",
            "privy_detail_role": "privy_detail",
        }
        pkg_obj = build_side_image_object(pkg_row, "packaging")
        privy_obj = build_side_image_object(privy_row, "privy_detail")
        entry = {"nac_code": "NAC1.CN.US.SET.UNCSET.2026.XX.26RJ.X", "extra_images": [{"url": "https://storage.googleapis.com/us_mint_coin_images/rev.jpg", "side": "reverse"}]}
        attach_packaging_or_privy_image(entry, pkg_obj)
        attach_packaging_or_privy_image(entry, privy_obj)
        self.assertEqual(entry["packaging_images"][0]["role"], "packaging")
        self.assertEqual(len(entry["extra_images"]), 2)
        self.assertEqual(entry["extra_images"][1]["role"], "privy_detail")

        # Forbidden credit wording fails closed
        bad = dict(pkg_row, packaging_credit="Used with permission of US Mint")
        with self.assertRaises(ValueError):
            build_side_image_object(bad, "packaging")

    def test_banknote_ai_download_blocked_403_even_for_authed_users(self):
        ai_note = {
            "nac_code": "NAC1.BN.US.SC1.SCLARGE.1896.BEP.BASE.D",
            "type": "note",
            "primary_image": {"ai_generated": True, "side": "obverse"},
        }
        with self.assertRaises(CatalogError) as ctx:
            verify_banknote_ai_download_allowed(ai_note)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.code, "AI_BANKNOTE_DOWNLOAD_DISABLED")

        # Real PD banknote allowed
        pd_note = {
            "nac_code": "NAC1.BN.US.SC1.SCLARGE.1896.BEP.BASE.D",
            "type": "note",
            "primary_image": {"ai_generated": False, "side": "obverse"},
        }
        verify_banknote_ai_download_allowed(pd_note)  # should not raise
        self.assertEqual(FREE_TRIAL_ITEM_LIMIT, 10)


class TestWave2FirebaseRedirectsAndFilterAliases(unittest.TestCase):
    """Component D: Firebase 301s precede /catalog/** rewrite; 1799 $5 hold intact; search_aliases."""

    def test_firebase_json_301_redirects_and_1799_hold(self):
        fb_path = os.path.join(REPO_ROOT, "numista_mobile", "firebase.json")
        fb = json.load(open(fb_path, encoding="utf-8"))
        redirects = fb["hosting"]["redirects"]
        rmap = {r["source"]: (r["destination"], r["type"]) for r in redirects}

        expected_pairs = [
            ("NAC1.CN.US.1C.20CENTPIEC.1875.XX.BASE.J", "NAC1.CN.US.20C.TWENTYCENT.1875.P.BASE.1"),
            ("NAC1.CN.US.1C.20CENTPIEC.1875.CC.BASE.2", "NAC1.CN.US.20C.TWENTYCENT.1875.CC.BASE.N"),
            ("NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1", "NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0"),
            ("NAC1.CN.US.D1.FLOWINGHAI.1795.P.BASE.S", "NAC1.CN.US.1D.FLOWINGHAI.1795.P.BASE.J"),
            ("NAC1.CN.US.D1.DRAPEDBUST.1798.P.HERALDICEA.N", "NAC1.CN.US.1D.DRAPEDBUST.1798.P.HERALDICEA.R"),
        ]
        for old_c, new_c in expected_pairs:
            self.assertEqual(rmap.get(f"/catalog/{old_c}"), (f"/catalog/{new_c}", 301))
            self.assertEqual(rmap.get(f"/catalog/{old_c}/"), (f"/catalog/{new_c}", 301))

        # Standing 1799 $5 recode hold MUST remain untouched
        self.assertNotIn("/catalog/NAC1.CN.US.GD5.DRAPEDBUST.1799.P.BASE.2", rmap)

    def test_catalog_service_filter_indexes_search_aliases(self):
        items = [
            {
                "nac_code": "NAC1.CN.US.GD5.TURBANHEAD.1797.P.HERALDICEA.J",
                "name": "1797 Capped Bust Right $5 Half Eagle",
                "series": "Capped Bust Right",
                "search_aliases": ["Turban Head", "Draped Bust", "Capped Bust to Right", "Heraldic Eagle"],
            },
            {
                "nac_code": "NAC1.CN.US.GD5.CAPPEDBUST.1807.P.BASE.A",
                "name": "1807 Capped Bust Left $5 Half Eagle",
                "series": "Capped Bust Left",
                "search_aliases": ["John Reich Bust Left"],
            },
        ]
        for q in ("Turban Head", "Draped Bust", "Capped Bust to Right", "Heraldic Eagle"):
            res = filter_catalog(items, q=q)
            self.assertEqual([x["nac_code"] for x in res], ["NAC1.CN.US.GD5.TURBANHEAD.1797.P.HERALDICEA.J"])
        res_left = filter_catalog(items, q="John Reich")
        self.assertEqual([x["nac_code"] for x in res_left], ["NAC1.CN.US.GD5.CAPPEDBUST.1807.P.BASE.A"])


class TestWave2MorganCatalogFirstAndNoScraper(unittest.TestCase):
    """Component C: Catalog-First Morgan lookup, disambiguation, privacy, retired auto-scraper."""

    def setUp(self):
        mk.reset_public_catalog_cache()
        self.sample_catalog = [
            {
                "nac_code": "NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0",
                "nac_aliases": ["NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1"],
                "name": "1875-S twenty-cent piece",
                "type": "coin",
                "year": 1875,
                "denomination": "20 cents",
                "series": "Twenty-Cent Piece",
                "mintage": {"value": 1155000, "label": "calendar year 1875", "source_url": "https://fraser.stlouisfed.org/"},
                "sources": [{"label": "Mint Director AR FY1876", "url": "https://fraser.stlouisfed.org/"}],
            },
            {
                "nac_code": "NAC1.CN.US.GD5.TURBANHEAD.1797.P.HERALDICEA.J",
                "name": "1797 Capped Bust Right $5 Half Eagle",
                "type": "coin",
                "year": 1797,
                "denomination": "$5",
                "series": "Capped Bust Right $5",
                "search_aliases": ["Turban Head", "Draped Bust", "Heraldic Eagle"],
                "mintage": {"value": None, "label": "not yet sourced", "source_url": None},
                "sources": [],
            },
            {
                "nac_code": "NAC1.CN.US.GD10.TURBANHEAD.1797.P.HERALDICEA.P",
                "name": "1797 Capped Bust Right $10 Eagle",
                "type": "coin",
                "year": 1797,
                "denomination": "$10",
                "series": "Capped Bust Right $10",
                "search_aliases": ["Turban Head", "Draped Bust", "Heraldic Eagle"],
                "mintage": {"value": None, "label": "not yet sourced", "source_url": None},
                "sources": [],
            },
        ]
        self.idx = mk.load_public_catalog_index(entries_override=self.sample_catalog)

    def tearDown(self):
        mk.reset_public_catalog_cache()

    def test_tier0_exact_and_alias_lookup_zero_firestore_reads(self):
        res = mk.get_catalog_context("tell me about this", nac_code="NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1", catalog_index=self.idx)
        self.assertEqual(res["matched_tier"], "tier0_nac")
        self.assertEqual(len(res["catalog_cards"]), 1)
        self.assertEqual(res["catalog_cards"][0]["nac_code"], "NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0")
        self.assertIn("1,155,000", res["context_block"])
        self.assertEqual(res["catalog_cards"][0]["actions"], ["view_in_catalog", "add_to_collection", "add_to_wishlist"])

    def test_ambiguous_nickname_triggers_disambiguation_and_honest_unsourced(self):
        res = mk.get_catalog_context("Tell me about Turban Head coins", catalog_index=self.idx)
        self.assertEqual(res["matched_tier"], "tier1_catalog")
        self.assertTrue(res["needs_disambiguation"])
        self.assertIn("DISAMBIGUATION REQUIRED", res["context_block"])
        self.assertIn("not yet sourced", res["context_block"])

    def test_missing_item_returns_honest_prompt_and_queues_without_autopublish(self):
        res = mk.get_catalog_context("Do we have the 1999 Atlantis Platinum Trillion?", catalog_index=self.idx)
        self.assertEqual(res["matched_tier"], "none")
        self.assertIsNotNone(res["missing_item_report_prompt"])
        self.assertIn("MORGAN §1 HONESTY RULE", res["context_block"])

        # Verify record_missing_catalog_request never auto-publishes
        rec = mk.record_missing_catalog_request(None, "1999 Atlantis Platinum Trillion", requester_uid="uid_test_1")
        self.assertFalse(rec["auto_published"])
        self.assertEqual(rec["status"], "pending_morgan_review")

    def test_main_py_retired_ungated_background_scraper(self):
        main_src = open(os.path.join(BACKEND_DIR, "main.py"), encoding="utf-8").read()
        self.assertNotIn("threading.Thread(target=scrape_url", main_src)
        self.assertIn("Un-gated Background Auto-Scraper RETIRED", main_src)

    def test_catalog_card_emits_both_canonical_and_alias_keys(self):
        item = dict(self.sample_catalog[0])
        item["primary_image"] = {
            "url": "https://storage.googleapis.com/us_mint_coin_images/catalog/test.jpg",
            "credit": "Public domain (US government work)",
        }
        card = mk._build_catalog_card(item)
        self.assertEqual(card["mintage_display"], "1,155,000 (calendar year 1875)")
        self.assertEqual(card["mintage_label"], card["mintage_display"])
        self.assertEqual(card["image_url"], "https://storage.googleapis.com/us_mint_coin_images/catalog/test.jpg")
        self.assertEqual(card["thumb_url"], card["image_url"])

    def test_catalog_missing_request_endpoint_auth_and_persistence(self):
        from fastapi.testclient import TestClient
        from unittest.mock import MagicMock, patch
        import main as app_main

        client = TestClient(app_main.app)

        # 1. Unauthenticated -> 401
        r_unauth = client.post("/api/v1/collection/catalog-missing-request", json={"query": "1999 Atlantis Coin"})
        self.assertEqual(r_unauth.status_code, 401)

        # Authenticated override
        app_main.app.dependency_overrides[app_main.get_current_user] = lambda: {"uid": "uid_w2_test"}
        try:
            # 2. Blank query -> 422
            r_blank = client.post("/api/v1/collection/catalog-missing-request", json={"query": "   "})
            self.assertIn(r_blank.status_code, (400, 422))

            # 3. Valid query -> 201 and auto_published: False written to missing_catalog_requests
            mock_doc = MagicMock()
            mock_doc.id = "req_test_123"
            mock_coll = MagicMock()
            mock_coll.document.return_value = mock_doc
            mock_db = MagicMock()
            mock_db.collection.return_value = mock_coll

            import routes.catalog_routes as cat_routes
            with patch.object(cat_routes, "db", mock_db):
                r_ok = client.post(
                    "/api/v1/collection/catalog-missing-request",
                    json={"query": "1999 Atlantis Coin", "note": "Asked in Morgan chat"},
                )
            self.assertEqual(r_ok.status_code, 201)
            body = r_ok.json()
            self.assertEqual(body["status"], "logged")
            self.assertEqual(body["request_id"], "req_test_123")
            self.assertFalse(body["auto_published"])
            mock_db.collection.assert_called_with("missing_catalog_requests")
            saved_payload = mock_doc.set.call_args[0][0]
            self.assertEqual(saved_payload["query"], "1999 Atlantis Coin")
            self.assertEqual(saved_payload["requested_by_uid"], "uid_w2_test")
            self.assertFalse(saved_payload["auto_published"])
            self.assertEqual(saved_payload["status"], "pending_review")
        finally:
            app_main.app.dependency_overrides.clear()


class TestChapter0ShardingAndChildTables(unittest.TestCase):
    """Chapter 0 (Plan 8f01c991): sharded manifest, enriched index, sub-chunking, child tables, PII manifest gate, & Morgan parity."""

    def _build_fixture_master(self, td: str) -> str:
        rows = [
            {
                "nac_code": "NAC1.CN.US.1D.MORGAN.1878.P.BASE.2",
                "nac_aliases": ["NAC1.CN.US.1D.MORGAN.1878.XX.BASE.1"],
                "search_aliases": ["8 Tail Feathers", "8TF"],
                "name": "1878 Morgan Silver Dollar",
                "type": "coin",
                "year": 1878,
                "denomination": "Dollar",
                "series": "Morgan Silver Dollar",
                "mint_facility": "Philadelphia",
                "mint_mark_on_coin": None,
                "era": "Seated & Gold Rush (1839–1891)",
                "history": "First year of the Morgan dollar design.",
                "mintage": {"value": 749500, "label": "8TF", "source_url": "https://fraser.stlouisfed.org/"},
                "primary_image": {
                    "url": "https://storage.googleapis.com/us_mint_coin_images/catalog/1878_morgan.jpg",
                    "side": "obverse",
                    "license": "Public domain (US government work, 17 U.S.C. § 105)",
                    "credit": "Image: United States Mint",
                    "source": "Image: United States Mint",
                },
                "varieties": [
                    {"name": "8 Tail Feathers", "attribution": "VAM-14", "reference_work": "Van Allen & Mallis"},
                    {"name": "Internal Held Variety", "held_from_live": True, "visibility": "internal"},
                ],
                "sources": [{"label": "U.S. Mint Report", "url": "https://fraser.stlouisfed.org/", "title": "Mint Report"}],
            },
            {
                "nac_code": "NAC1.BN.US.1TO10.NOTESHEET.2021.ATL.B4003.J",
                "name": "$1–$10 Note Sheet, Atlanta, Series 2021 (B4003)",
                "type": "note",
                "year": 2021,
                "denomination": "Dollar",
                "series": "Uncut Currency Sheet",
                "mint_facility": "BEP",
                "era": "21st century (2000–2026)",
                "history": "Uncut Federal Reserve note sheet for the Atlanta district.",
                "sources": [],
            },
            {
                "nac_code": "NAC1.CN.US.25C.AWQ.2024.P.BASE.9",
                "name": "2024-P American Women Quarter",
                "type": "coin",
                "year": 2024,
                "denomination": "Quarter Dollar",
                "series": "American Women Quarters",
                "mint_facility": "Philadelphia",
                "mint_mark_on_coin": "P",
                "era": "21st century (2000–2026)",
                "history": "2024 American Women Quarters release.",
                "sources": [],
            },
        ]
        inp = os.path.join(td, "master.jsonl")
        with open(inp, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        return inp

    def test_sharded_manifest_index_children_and_no_monolith(self):
        from tools.catalog.build_public_catalog import _partition_era_chunks, build_public_catalog
        from tools.catalog.pii_gate_validator import run_manifest_gate

        with tempfile.TemporaryDirectory() as td:
            inp = self._build_fixture_master(td)
            out = os.path.join(td, "catalog_public_v1.json")
            rc = build_public_catalog(inp, out, emit_split_index=True, no_monolith=True)
            self.assertEqual(rc, 0)
            self.assertFalse(os.path.exists(out))

            manifest_path = os.path.join(td, "catalog_manifest_v1.json")
            self.assertTrue(os.path.exists(manifest_path))
            manifest = json.load(open(manifest_path, encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "catalog_sharded_v1")
            self.assertEqual(manifest["public_row_count"], 3)
            self.assertFalse(manifest["monolith_present"])
            self.assertEqual(manifest["monolith_bytes"], 0)
            self.assertEqual(manifest["index"]["files"], ["catalog_search_index_v1.json"])
            self.assertEqual(manifest["child_tables"]["varieties"]["row_count"], 1)
            self.assertEqual(manifest["child_tables"]["nbn_charters"]["row_count"], 0)
            self.assertEqual(manifest["child_tables"]["obsolete_issuers"]["row_count"], 0)

            # Enriched index parity checks
            idx_rows = json.load(open(os.path.join(td, "catalog_search_index_v1.json"), encoding="utf-8"))
            self.assertEqual(len(idx_rows), 3)
            by_nac = {r["nac_code"]: r for r in idx_rows}
            m78 = by_nac["NAC1.CN.US.1D.MORGAN.1878.P.BASE.2"]
            self.assertIs(m78["is_placeholder"], False)
            self.assertTrue(m78["has_photo"])
            self.assertTrue(m78["has_varieties"])
            self.assertEqual(m78["variety_count"], 1)
            self.assertEqual(m78["mint_facility"], "Philadelphia")
            self.assertIn("primary_image", m78)
            self.assertNotIn("history", m78)

            # Normalized varieties child table excludes held varieties fail-closed
            var_rows = json.load(open(os.path.join(td, "children", "varieties_v1.json"), encoding="utf-8"))
            self.assertEqual(len(var_rows), 1)
            self.assertEqual(var_rows[0]["parent_nac1"], "NAC1.CN.US.1D.MORGAN.1878.P.BASE.2")
            self.assertEqual(var_rows[0]["name"], "8 Tail Feathers")

            # Fail-closed PII manifest gate + negative test passes on clean build
            self.assertEqual(run_manifest_gate(manifest_path, dry_run=True, negative_test=True), 0)

            # Sub-chunk partitioning splits deterministically when row cap exceeded
            parts = _partition_era_chunks([{"nac_code": f"A{i}"} for i in range(5)], max_chunk_rows=2, max_chunk_bytes=100000)
            self.assertEqual([len(p) for p in parts], [2, 2, 1])

            # Tampered chunk with PII token fails manifest gate closed
            chunk_rel = manifest["chunks"][0]["path"]
            chunk_abs = os.path.join(td, chunk_rel)
            chunk_data = json.load(open(chunk_abs, encoding="utf-8"))
            chunk_data[0]["history"] = "from a private collector album"
            with open(chunk_abs, "w", encoding="utf-8", newline="\n") as cf:
                json.dump(chunk_data, cf)
            self.assertEqual(run_manifest_gate(manifest_path), 1)

    def test_morgan_knowledge_sharded_manifest_parity(self):
        from tools.catalog.build_public_catalog import build_public_catalog

        with tempfile.TemporaryDirectory() as td:
            inp = self._build_fixture_master(td)
            out = os.path.join(td, "catalog_public_v1.json")
            build_public_catalog(inp, out, emit_split_index=True, no_monolith=True)
            manifest_path = os.path.join(td, "catalog_manifest_v1.json")

            mk.reset_public_catalog_cache()
            try:
                idx = mk.load_public_catalog_index(manifest_path=manifest_path)
                self.assertEqual(idx["source_mode"], "sharded")
                self.assertEqual(len(idx["entries"]), 3)
                self.assertIn("NAC1.CN.US.1D.MORGAN.1878.P.BASE.2", idx["varieties_by_parent"])
                self.assertEqual(len(idx["varieties_by_parent"]["NAC1.CN.US.1D.MORGAN.1878.P.BASE.2"]), 1)

                # Tier-0 canonical NAC1 + retired alias parity
                res_canonical = mk.get_catalog_context(
                    "tell me about it",
                    nac_code="NAC1.CN.US.1D.MORGAN.1878.P.BASE.2",
                    catalog_index=idx,
                )
                self.assertEqual(res_canonical["matched_tier"], "tier0_nac")
                res_alias = mk.get_catalog_context(
                    "tell me about it",
                    nac_code="NAC1.CN.US.1D.MORGAN.1878.XX.BASE.1",
                    catalog_index=idx,
                )
                self.assertEqual(res_alias["matched_tier"], "tier0_nac")
                self.assertEqual(
                    res_alias["catalog_cards"][0]["nac_code"],
                    "NAC1.CN.US.1D.MORGAN.1878.P.BASE.2",
                )
                # Atlanta BN vector resolves in Tier-0
                res_atl = mk.get_catalog_context(
                    "Atlanta note sheet",
                    nac_code="NAC1.BN.US.1TO10.NOTESHEET.2021.ATL.B4003.J",
                    catalog_index=idx,
                )
                self.assertEqual(res_atl["matched_tier"], "tier0_nac")
            finally:
                mk.reset_public_catalog_cache()

    def test_all_12_fed_districts_bn_only_in_wave2_suite(self):
        from catalog_nac1 import BN_ONLY_FACILITIES, build_nac1, validate_nac1

        expected = {"BOS", "NY", "PHI", "CLE", "RIC", "ATL", "CHI", "STL", "MIN", "KC", "DAL", "SF"}
        self.assertEqual(BN_ONLY_FACILITIES, frozenset(expected))
        self.assertTrue(validate_nac1("NAC1.BN.US.1TO10.NOTESHEET.2021.ATL.B4003.J"))
        for dist in sorted(expected):
            self.assertTrue(validate_nac1(build_nac1(f"NAC1.BN.US.100.NOTESHEET.2025.{dist}.B7800")))
            for kind in ("CN", "MD", "TK", "ST"):
                self.assertFalse(validate_nac1(build_nac1(f"NAC1.{kind}.US.1D.MORGAN.2025.{dist}.BASE")))


if __name__ == "__main__":
    unittest.main()
