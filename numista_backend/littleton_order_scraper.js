/**
 * littleton_order_scraper.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Littleton Coin Company — Order History DOM Scraper
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * PURPOSE:
 *   Scrapes the Littleton Coin Company order history / order detail HTML page
 *   and extracts line-item records into a JSON array that matches the shape
 *   expected by POST /api/import/littleton_sync.
 *
 * USAGE — Browser DevTools:
 *   1.  Navigate to the Littleton order history or order detail page.
 *   2.  Open the browser DevTools console (F12).
 *   3.  Paste this entire script and press Enter.
 *   4.  The script logs the extracted payload to the console and optionally
 *       POSTs it directly to the Numista.AI backend.
 *
 * USAGE — WebView / Frame Injection:
 *   Inject this IIFE string via webview.evaluateJavascript() (Android/Flutter)
 *   or WKWebView.evaluateJavaScript() (iOS/Flutter). The IIFE returns a JSON
 *   string suitable for bridging back to the native layer.
 *
 * OUTPUT SHAPE (matches LittletonOrderRecord Pydantic model):
 *   [
 *     {
 *       "purchase_date":  "06/03/2026",
 *       "littleton_sku":  "ME-6100",
 *       "description":    "1921 Morgan Silver Dollar BU",
 *       "cost":           "$14.95",
 *       "qty":            1
 *     },
 *     ...
 *   ]
 *
 * RESILIENCE:
 *   - Header detection by text content, not fixed column index — survives
 *     minor table restructures on the Littleton website.
 *   - All DOM queries wrapped in try/catch.
 *   - Returns empty array (never throws) if no matching table is found.
 * ─────────────────────────────────────────────────────────────────────────────
 */

(function LittletonOrderScraper() {
  'use strict';

  // ── Configuration ────────────────────────────────────────────────────────
  const NUMISTA_API_BASE = 'https://numista-backend-xxxxxxxx-uc.a.run.app'; // ← update with real URL
  const DEBUG            = true;   // Set false in production injection

  // Column header keywords used to detect the correct <th> index.
  // All comparisons are case-insensitive and trim-stripped.
  const HEADER_KEYWORDS = {
    date:        ['date', 'order date', 'purchase date', 'ordered'],
    sku:         ['sku', 'item #', 'item no', 'item number', 'product #', 'catalog #', 'cat #'],
    description: ['description', 'item', 'product', 'title', 'name'],
    price:       ['price', 'unit price', 'cost', 'amount', 'each'],
    qty:         ['qty', 'quantity', 'count', 'ordered', 'amount'],
  };

  // ── Logging utility ──────────────────────────────────────────────────────
  function log(...args) {
    if (DEBUG) console.log('[LCC Scraper]', ...args);
  }

  // ── Find column index by header text ─────────────────────────────────────
  /**
   * Given an array of <th> elements, returns the 0-based column index
   * whose text content matches any keyword in the provided list.
   * Returns -1 if not found.
   *
   * @param {NodeListOf<HTMLElement>|Array} headerCells
   * @param {string[]} keywords
   * @returns {number}
   */
  function findColIndex(headerCells, keywords) {
    const cells = Array.from(headerCells);
    for (let i = 0; i < cells.length; i++) {
      const text = (cells[i].textContent || '').trim().toLowerCase();
      if (keywords.some(kw => text.includes(kw.toLowerCase()))) {
        return i;
      }
    }
    return -1;
  }

  // ── Safe text extractor ───────────────────────────────────────────────────
  /**
   * Safely extracts trimmed text from a table cell at a given index.
   * Returns empty string if the cell is missing or the index is -1.
   *
   * @param {HTMLCollectionOf<HTMLTableCellElement>} cells
   * @param {number} index
   * @returns {string}
   */
  function cellText(cells, index) {
    if (index < 0 || index >= cells.length) return '';
    return (cells[index].textContent || '').trim();
  }

  // ── Parse quantity from a cell ────────────────────────────────────────────
  /**
   * Extracts an integer quantity from a cell value.
   * Falls back to 1 if parsing fails.
   *
   * @param {string} raw
   * @returns {number}
   */
  function parseQty(raw) {
    if (!raw) return 1;
    const parsed = parseInt(raw.replace(/[^0-9]/g, ''), 10);
    return isNaN(parsed) || parsed < 1 ? 1 : parsed;
  }

  // ── Infer order date from page ────────────────────────────────────────────
  /**
   * Attempts to find a global order date on the page — many Littleton
   * "Order Detail" pages show the date as a heading or meta field rather
   * than per-row. Falls back to today's ISO date if nothing is found.
   *
   * @returns {string}
   */
  function inferPageOrderDate() {
    // Try common Littleton date label patterns
    const selectors = [
      '[class*="order-date"]',
      '[class*="orderDate"]',
      '[data-order-date]',
      'span.date',
      'td.orderDate',
      '.order-header .date',
    ];

    for (const sel of selectors) {
      try {
        const el = document.querySelector(sel);
        if (el) {
          const text = (el.textContent || el.getAttribute('data-order-date') || '').trim();
          if (text.match(/\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}/)) {
            return text;
          }
        }
      } catch (_) { /* ignore */ }
    }

    // Fallback: scan <td> / <span> text for date patterns near "Date:" labels
    try {
      const allText = Array.from(document.querySelectorAll('td, span, p, div'));
      for (const el of allText) {
        const text = (el.textContent || '').trim();
        if (/^(order\s*date|date\s*ordered|purchase\s*date)\s*:/i.test(text)) {
          const match = text.match(/(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})/);
          if (match) return match[1];
        }
      }
    } catch (_) { /* ignore */ }

    // Last resort: today
    const today = new Date();
    return `${String(today.getMonth() + 1).padStart(2, '0')}/${String(today.getDate()).padStart(2, '0')}/${today.getFullYear()}`;
  }

  // ── Core scraper ─────────────────────────────────────────────────────────
  /**
   * Scrapes all product tables on the current page and returns an array of
   * LittletonOrderRecord objects.
   *
   * Supports two common Littleton table layouts:
   *   A) Single detail table on an Order Detail page (1 order date in header)
   *   B) Multi-order history table (each row may contain its own date column)
   *
   * @returns {Array<{purchase_date: string, littleton_sku: string, description: string, cost: string, qty: number}>}
   */
  function scrapeOrders() {
    const results = [];
    const pageLevelDate = inferPageOrderDate();

    // Grab every table on the page; we'll filter to ones that look like order tables
    const tables = Array.from(document.querySelectorAll('table'));
    if (tables.length === 0) {
      log('No <table> elements found on this page.');
      return results;
    }

    for (const table of tables) {
      try {
        // Find the header row — prefer <thead> > <tr>, fall back to first <tr>
        const thead = table.querySelector('thead');
        let headerRow = thead
          ? thead.querySelector('tr')
          : table.querySelector('tr');

        if (!headerRow) continue;

        const headerCells = headerRow.querySelectorAll('th, td');
        if (headerCells.length === 0) continue;

        // Detect column positions using keyword matching
        const colDate  = findColIndex(headerCells, HEADER_KEYWORDS.date);
        const colSku   = findColIndex(headerCells, HEADER_KEYWORDS.sku);
        const colDesc  = findColIndex(headerCells, HEADER_KEYWORDS.description);
        const colPrice = findColIndex(headerCells, HEADER_KEYWORDS.price);
        const colQty   = findColIndex(headerCells, HEADER_KEYWORDS.qty);

        // A table is considered an "order table" if it has at least
        // a description column AND (sku OR price)
        const isOrderTable = colDesc >= 0 && (colSku >= 0 || colPrice >= 0);
        if (!isOrderTable) {
          log(`Skipping table — missing required columns (desc=${colDesc}, sku=${colSku}, price=${colPrice})`);
          continue;
        }

        log(`Found order table. Columns → date:${colDate} sku:${colSku} desc:${colDesc} price:${colPrice} qty:${colQty}`);

        // Collect data rows — skip the header row itself
        const tbody = table.querySelector('tbody');
        const dataRows = tbody
          ? Array.from(tbody.querySelectorAll('tr'))
          : Array.from(table.querySelectorAll('tr')).slice(1); // skip header row

        for (const row of dataRows) {
          try {
            const cells = row.querySelectorAll('td');
            if (cells.length === 0) continue;  // skip sub-headers / spacer rows

            const description = cellText(cells, colDesc);
            if (!description) continue;  // skip visually blank rows

            // SKU: prefer the dedicated SKU column; fall back to extracting
            // from the description string using known Littleton SKU pattern
            let sku = colSku >= 0 ? cellText(cells, colSku) : '';
            if (!sku) {
              // Attempt to pull from a link href (Littleton often puts SKU in the product URL)
              const link = cells[colDesc >= 0 ? colDesc : 0].querySelector('a[href]');
              if (link) {
                const href = link.getAttribute('href') || '';
                const skuMatch = href.match(/[?&](?:sku|item|product)=([A-Z0-9\-]+)/i);
                if (skuMatch) sku = skuMatch[1];
              }
            }

            // If still no SKU, derive a placeholder from the description
            if (!sku) {
              sku = description
                .replace(/[^a-zA-Z0-9 ]/g, '')
                .trim()
                .split(/\s+/)
                .slice(0, 3)
                .join('-')
                .toUpperCase();
            }

            const rawCost     = cellText(cells, colPrice);
            const rawQty      = cellText(cells, colQty);
            const rowDate     = colDate >= 0 ? cellText(cells, colDate) : '';
            const purchaseDate = rowDate || pageLevelDate;

            // Validate price — skip header-like rows that contain non-numeric prices
            if (rawCost && !/[\d\.]/.test(rawCost)) continue;

            results.push({
              purchase_date: purchaseDate,
              littleton_sku: sku.trim(),
              description:   description,
              cost:          rawCost || '0.00',
              qty:           parseQty(rawQty),
            });

          } catch (rowErr) {
            log('Row parse error:', rowErr);
          }
        }

      } catch (tableErr) {
        log('Table parse error:', tableErr);
      }
    }

    return results;
  }

  // ── POST to Numista.AI backend ────────────────────────────────────────────
  /**
   * Posts the scraped order records to the Numista.AI backend endpoint.
   *
   * @param {string} userEmail    - Authenticated user email
   * @param {string} apiBase      - Backend base URL (override NUMISTA_API_BASE)
   * @param {string} [sessionId]  - Optional import session ID for bulk tracking
   * @returns {Promise<object>}   - API response JSON
   */
  async function postToNumista(userEmail, apiBase, sessionId) {
    const base    = (apiBase || NUMISTA_API_BASE).replace(/\/$/, '');
    const records = scrapeOrders();

    if (records.length === 0) {
      log('No order records found — nothing to post.');
      return { status: 'no_records', total: 0 };
    }

    log(`Posting ${records.length} order records to ${base}/api/import/littleton_sync`);

    const payload = {
      user_email:        userEmail,
      orders:            records,
      import_session_id: sessionId || null,
    };

    try {
      const response = await fetch(`${base}/api/import/littleton_sync`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });

      if (!response.ok) {
        const errText = await response.text();
        log(`API error ${response.status}:`, errText);
        return { status: 'error', http_status: response.status, detail: errText };
      }

      const result = await response.json();
      log('API response:', result);
      return result;

    } catch (fetchErr) {
      log('fetch() failed:', fetchErr);
      return { status: 'fetch_error', detail: String(fetchErr) };
    }
  }

  // ── Dry-run: log results immediately ─────────────────────────────────────
  const scrapedRecords = scrapeOrders();

  if (scrapedRecords.length === 0) {
    console.warn('[LCC Scraper] No order line items found on this page. Check that you are on a Littleton order history or order detail page.');
  } else {
    console.log(
      `[LCC Scraper] Extracted ${scrapedRecords.length} order record(s). ` +
      'Call window.LittletonScraper.postToNumista(email, apiBase) to sync to Numista.AI.'
    );
    console.table(scrapedRecords);
  }

  // ── Expose public API on window for interactive console use ──────────────
  window.LittletonScraper = {
    /**
     * Returns the array of scraped order records without posting.
     * Useful for previewing data before committing.
     *
     * @returns {Array} Scraped records
     *
     * Example:
     *   window.LittletonScraper.preview()
     */
    preview: scrapeOrders,

    /**
     * Posts scraped records to the Numista.AI backend.
     *
     * @param {string} userEmail  - Your Numista.AI account email
     * @param {string} [apiBase]  - API base URL (defaults to production)
     * @param {string} [sessionId] - Optional bulk session tracking ID
     * @returns {Promise<object>}
     *
     * Example:
     *   await window.LittletonScraper.postToNumista('user@example.com')
     */
    postToNumista,

    /**
     * Returns the current page-level order date inference.
     * @returns {string}
     */
    inferDate: inferPageOrderDate,
  };

  // Return JSON string for WebView bridge injection
  return JSON.stringify(scrapedRecords);

})();
