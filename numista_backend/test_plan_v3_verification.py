import sys
sys.path.insert(0, 'numista_backend')
from services.us_mint_catalog_service import US_MINT_PRODUCT_CATALOG, enrich_us_mint_item

# 1. Catalog presence & values
assert '26RJ' in US_MINT_PRODUCT_CATALOG, '26RJ missing'
rj = US_MINT_PRODUCT_CATALOG['26RJ']
assert rj['issue_price'] == 124.50, f"26RJ price mismatch: {rj['issue_price']}"
assert rj['is_set'] is True, '26RJ is_set mismatch'
assert rj['set_id'] == 'uncirculated-coin-set-2026', f"set_id: {rj['set_id']}"

assert '23RH' in US_MINT_PRODUCT_CATALOG, '23RH missing'
assert US_MINT_PRODUCT_CATALOG['23RH']['issue_price'] == 130.00

# 2. Fill-missing-only logic: must NOT overwrite existing collector fields
doc = {
    'item_number': '26RJ',
    'Program/Series': 'Custom Collector Series',
    'Condition': 'MS-70',
    'Strike Type': 'Proof',
    'Metal Content': 'Silver',
    'retailer': 'US Mint'
}
enrich_us_mint_item(doc)
assert doc['Program/Series'] == 'Custom Collector Series', 'Overwrote Program/Series!'
assert doc['Condition'] == 'MS-70', 'Overwrote Condition!'
assert doc['Strike Type'] == 'Proof', 'Overwrote Strike Type!'
assert doc['Metal Content'] == 'Silver', 'Overwrote Metal Content!'
assert doc['is_set'] is True
assert doc['issue_price'] == 124.50

# 3. Fill-missing-only logic: fills empty fields
doc2 = {
    'item_number': '26RJ',
    'retailer': 'US Mint'
}
enrich_us_mint_item(doc2)
assert doc2['Program/Series'] == 'Uncirculated Sets', f"Expected Uncirculated Sets, got {doc2.get('Program/Series')}"
assert doc2['Strike Type'] == 'Uncirculated'
assert doc2['Condition'] == 'Uncirculated'

# 4. Duplicate score tests from main
from main import _score_duplicate
new_item = {
    'Year': '2026',
    'Mint Mark': 'P',
    'Program/Series': 'Semiquincentennial Quarter',
    'retailer_item_num': '26RJ',
    'retailer_invoice_num': 'INV-999',
    'Denomination': 'Quarter',
}
exist_same_sku = {
    'Year': '2026',
    'retailer_item_num': '26RJ',
    'retailer_invoice_num': 'INV-OTHER',
}
score_sku_only = _score_duplicate(new_item, exist_same_sku)
assert score_sku_only >= 0.60, f"SKU only score too low: {score_sku_only}"

exist_same_sku_inv = {
    'Year': '2026',
    'retailer_item_num': '26RJ',
    'retailer_invoice_num': 'INV-999',
}
score_sku_inv = _score_duplicate(new_item, exist_same_sku_inv)
assert score_sku_inv >= 0.90, f"SKU + invoice score too low: {score_sku_inv}"

print("ALL BACKEND ENRICHMENT AND DUPLICATE SCORING TESTS PASSED 100%!")
