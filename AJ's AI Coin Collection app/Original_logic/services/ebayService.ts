
import { Coin } from '../types';

const EBAY_AUTH_URL = 'https://api.ebay.com/identity/v1/oauth2/token';
const EBAY_BROWSE_URL = 'https://api.ebay.com/buy/browse/v1/item_summary/search';

export interface EbaySoldItem {
  title: string;
  price: string;
  currency: string;
  itemWebUrl: string;
  thumbnailUrl: string;
  soldDate: string;
}

/**
 * Proxy helper for eBay requests (CORS handling)
 */
async function ebayFetch(url: string, options: any): Promise<Response> {
  const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(url)}`;
  return fetch(proxyUrl, options);
}

/**
 * Exchanges Client ID and Secret for an OAuth Access Token.
 */
export const getEbayToken = async (clientId: string, clientSecret: string): Promise<string> => {
  if (!clientId || !clientSecret) {
      throw new Error("eBay keys are missing. Please add them in Settings.");
  }

  // Basic Auth header requires base64 encoding of "ID:Secret"
  const credentials = btoa(`${clientId.trim()}:${clientSecret.trim()}`);
  const body = new URLSearchParams();
  body.append('grant_type', 'client_credentials');
  body.append('scope', 'https://api.ebay.com/oauth/api_scope');

  try {
      const response = await ebayFetch(EBAY_AUTH_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': `Basic ${credentials}`
        },
        body: body.toString()
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        console.error("eBay Auth Fail:", error);
        throw new Error(error.error_description || `eBay Auth failed (${response.status}). Check your keys.`);
      }

      const data = await response.json();
      return data.access_token;
  } catch (err: any) {
      if (err.message.includes('Failed to fetch')) {
          throw new Error("Network error connecting to eBay via proxy. Please try again.");
      }
      throw err;
  }
};

/**
 * Searches eBay for sold listings matching the coin details.
 */
export const fetchEbaySoldItems = async (coin: Coin, token: string): Promise<EbaySoldItem[]> => {
  // Construct search query - prioritized by specificity
  const query = `${coin.year} ${coin.mintMark || ''} ${coin.denomination} ${coin.series || ''} sold`.replace(/\s+/g, ' ').trim();
  
  // Browsing API search for sold items
  // We use filter to find items that have a 'lastSoldDate'
  // Note: Production API is required for this to return real data.
  const url = `${EBAY_BROWSE_URL}?q=${encodeURIComponent(query)}&filter=buyingOptions:{FIXED_PRICE|AUCTION},lastSoldDate:[2023-01-01T00:00:00Z..]&limit=5`;

  const response = await ebayFetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
      'Accept': 'application/json'
    }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.message || `eBay Search Error (${response.status})`);
  }

  const data = await response.json();
  
  if (!data.itemSummaries || data.itemSummaries.length === 0) return [];

  return data.itemSummaries.map((item: any) => ({
    title: item.title,
    price: item.price.value,
    currency: item.price.currency,
    itemWebUrl: item.itemWebUrl,
    thumbnailUrl: item.thumbnailImages?.[0]?.imageUrl || item.image?.imageUrl || '',
    soldDate: item.lastSoldDate || ''
  }));
};
