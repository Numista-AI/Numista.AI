import os
import unittest

MOBILE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestStaticCatalogHtml(unittest.TestCase):
    def test_per_coin_html_exists_and_has_canonical(self):
        coin_path = os.path.join(
            MOBILE_ROOT, 'build', 'web', 'catalog', 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3', 'index.html'
        )
        self.assertTrue(os.path.exists(coin_path), "Per-coin static HTML must exist for 1921 Morgan")
        with open(coin_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(
            '<link rel="canonical" href="https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3"',
            content,
        )
        self.assertIn(
            '<meta property="og:title" content="Numista.AI Reference Catalog – 1921-P Morgan Silver Dollars"',
            content,
        )
        self.assertIn('<base href="/"', content)
        # v2.0: primary_image is null on 1921-P Morgan; og:image and twitter:image MUST be omitted
        self.assertNotIn('<meta property="og:image"', content)
        self.assertNotIn('<meta name="twitter:image"', content)

    def test_catalog_root_html_exists(self):
        root_path = os.path.join(MOBILE_ROOT, 'build', 'web', 'catalog', 'index.html')
        self.assertTrue(os.path.exists(root_path), "Catalog root static HTML must exist")
        with open(root_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<link rel="canonical" href="https://numista.ai/catalog"', content)

    def test_pricing_html_exists(self):
        pricing_path = os.path.join(MOBILE_ROOT, 'build', 'web', 'pricing', 'index.html')
        self.assertTrue(os.path.exists(pricing_path), "Pricing static HTML must exist")
        with open(pricing_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<link rel="canonical" href="https://numista.ai/pricing"', content)
        self.assertNotIn('$30 / 6 months', content)
        self.assertNotIn('2027', content)

    def test_catalog_unknown_html_exists_and_has_noindex(self):
        unknown_path = os.path.join(MOBILE_ROOT, 'build', 'web', 'catalog_unknown.html')
        self.assertTrue(os.path.exists(unknown_path), "catalog_unknown.html must exist for soft-404 rewrite")
        with open(unknown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<meta name="robots" content="noindex, follow">', content)
        self.assertIn('<link rel="canonical" href="https://numista.ai/catalog"', content)


if __name__ == '__main__':
    unittest.main()
