import { WishlistItem } from '../types';

// ──────────────────────────────────────────────────────────────
// Numista.AI eBay Partner Network (EPN) Configuration
// Campaign: "Numista.AI - Main"
// ──────────────────────────────────────────────────────────────
const EPN_CAMPAIGN_ID = '5339148752';
const EPN_NETWORK_ID  = '711-53200-19255-0'; // eBay US
const COINS_CATEGORY  = '11116';             // eBay: Coins & Paper Money

/**
 * Builds a trackable eBay affiliate search URL from a WishlistItem.
 * When a user or their family member clicks this link and completes
 * a purchase on eBay, Numista.AI earns an EPN commission (~3–4%).
 *
 * Search term priority:
 *   year + design  (most specific — e.g. "2010 Yellowstone Quarter")
 *   year + series  (e.g. "2010 America The Beautiful Quarter")
 *   year + denomination (fallback — e.g. "2010 Quarter")
 */
export function buildEbayAffiliateUrl(item: WishlistItem): string {
  const parts: string[] = [];

  if (item.year)        parts.push(item.year);
  if (item.design)      parts.push(item.design);
  else if (item.series) parts.push(item.series);
  if (item.denomination) parts.push(item.denomination);

  const searchTerm = parts.filter(Boolean).join(' ');
  const query = encodeURIComponent(searchTerm);

  const params = new URLSearchParams({
    _nkw:    query,
    _sacat:  COINS_CATEGORY,
    mkcid:   '1',
    mkrid:   EPN_NETWORK_ID,
    siteid:  '0',
    campid:  EPN_CAMPAIGN_ID,
    toolid:  '10001',
    mkevt:   '1',
  });

  return `https://www.ebay.com/sch/i.html?${params.toString()}`;
}

/**
 * Checks whether a WishlistItem has enough data to generate a
 * meaningful eBay search (needs at least a denomination).
 */
export function canSearchEbay(item: WishlistItem): boolean {
  return Boolean(item.denomination);
}
