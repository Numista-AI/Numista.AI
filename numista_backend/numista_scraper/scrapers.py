import re
import urllib.parse
from bs4 import BeautifulSoup
from botasaurus.request import request, Request
from botasaurus.soupify import soupify
import requests

# Load config settings
try:
    from .config import USER_AGENTS, DEFAULT_DELAY, REQUEST_TIMEOUT
except ImportError:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    DEFAULT_DELAY = 1.5
    REQUEST_TIMEOUT = 30

NUMISTA_API_KEY = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe'
NUMISTA_API_BASE = 'https://api.numista.com/v3'

# ─── Numista API Scraper ──────────────────────────────────────────────────────

def scrape_numista_api(coin_id):
    """
    Directly query the Numista API for obverse and reverse images.
    No browser or complex anti-detection needed as it is an official API.
    """
    url = f"{NUMISTA_API_BASE}/types/{coin_id}"
    headers = {
        'Numista-API-Key': NUMISTA_API_KEY,
        'Accept': 'application/json',
        'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            obv_img = data.get("obverse", {}).get("picture") or data.get("obverse", {}).get("thumbnail")
            rev_img = data.get("reverse", {}).get("picture") or data.get("reverse", {}).get("thumbnail")
            return {
                "obverse_url": obv_img,
                "reverse_url": rev_img,
                "title": data.get("title"),
                "description": data.get("description", ""),
                "composition": data.get("composition", {}).get("text") if isinstance(data.get("composition"), dict) else data.get("composition"),
                "source": "numista",
                "source_url": f"https://en.numista.com/catalogue/pieces/{coin_id}.html"
            }
    except Exception as e:
        print(f"    ⚠ Numista API error for ID {coin_id}: {e}")
    return None

# ─── PCGS CoinFacts Scraper ───────────────────────────────────────────────────

def fetch_pcgs_market_data(pcgs_no):
    """
    Query the official PCGS API endpoint /coindetail/GetCoinFactsByGrade.
    Fetches the bearer token securely from Firestore path config/pcgs.
    Returns a dictionary with price_guide, population_total, and apr_history.
    """
    if not pcgs_no:
        return None

    # Lazy-import Firestore to avoid startup initialization order issues
    try:
        from firebase_admin import firestore
        db = firestore.client()
        doc = db.collection("config").document("pcgs").get()
        token = doc.to_dict().get("bearerToken") if doc.exists else None
    except Exception as e:
        print(f"    ⚠ Error fetching PCGS token from Firestore: {e}")
        token = None

    if not token:
        print("    ⚠ PCGS bearer token not configured in Firestore config/pcgs.")
        return None

    # Query standard grades to populate the price guide and census data
    # Standard representative grades: G4, VF20, MS63, MS65
    grade_mapping = {
        4: "G4",
        20: "VF20",
        63: "MS63",
        65: "MS65"
    }

    price_guide = {}
    apr_history = []
    population_total = 0
    seen_auctions = set()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "NumistaAI/1.0 (eric@numista.ai)"
    }
    url = "https://api.pcgs.com/publicapi/coindetail/GetCoinFactsByGrade"

    # Fetch data across standard grades to build consolidated pricing and pop index
    for grade_no, grade_code in grade_mapping.items():
        params = {
            "PCGSNo": str(pcgs_no),
            "GradeNo": int(grade_no),
            "PlusGrade": "false"
        }
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("IsValidRequest"):
                    # 1. Price Guide
                    price_val = data.get("PriceGuideValue")
                    if price_val is not None:
                        price_guide[grade_code] = float(price_val)

                    # 2. Population Census (consolidated total)
                    pop = data.get("Population") or 0
                    population_total += int(pop)

                    # 3. APR History
                    for item in data.get("AuctionList") or []:
                        price = item.get("Price")
                        house = item.get("Auctioneer")
                        date_str = item.get("Date")
                        if price and house and date_str:
                            # Deduplicate auction entries
                            unique_key = (price, house, date_str)
                            if unique_key not in seen_auctions:
                                seen_auctions.add(unique_key)
                                apr_history.append({
                                    "price": float(price),
                                    "auction_house": house,
                                    "date": date_str
                                })
            elif resp.status_code == 401:
                print("    ⚠ PCGS API: Unauthorized (invalid bearer token).")
                break
            elif resp.status_code == 429:
                print("    ⚠ PCGS API: Rate limit/daily call count exceeded.")
                break
        except Exception as e:
            print(f"    ⚠ Error querying PCGS API for grade {grade_code}: {e}")

    # If we scraped absolutely no data (e.g. PCGS number invalid)
    if not price_guide and not apr_history and population_total == 0:
        return None

    return {
        "price_guide": price_guide,
        "population_total": population_total,
        "apr_history": apr_history[:10]  # Limit to top 10 recent records
    }


# ─── Heritage Auctions Scraper ────────────────────────────────────────────────

@request
def scrape_heritage_auctions(request: Request, data):
    """
    Search Heritage Auctions and extract coin or currency images.
    Uses Botasaurus proxy and browser impersonation to spoof TLS.
    `data` contains a dict with keys: 'query' (e.g. '1934 $1 Green Seal Boston')
    """
    query = data.get("query")
    if not query:
        return None
        
    search_url = f"https://currency.ha.com/c/search-results.zx?Nty=1&Ntt={urllib.parse.quote_plus(query)}&N=790+231+4294967291"
    try:
        resp = request.get(search_url)
        soup = soupify(resp)
        img_pattern = re.compile(
            r'<img[^>]+src="(https://dyn1\.heritagestatic\.com/ha\?[^"]+)"[^>]*alt="([^"]*)"',
            re.IGNORECASE
        )
        
        found = []
        for m in img_pattern.finditer(str(soup)):
            thumb_url = m.group(1)
            alt_text  = m.group(2).strip()
            if not alt_text or "logo" in alt_text.lower() or "employee" in alt_text.lower():
                continue
            # Construct high-resolution image URL (Heritage parameters)
            hi_res = re.sub(r'w=\d+', 'w=1200', thumb_url)
            hi_res = re.sub(r'h=\d+', 'h=900', hi_res)
            found.append({"title": alt_text, "url": hi_res})
            
        if found:
            # First result is obverse, second is reverse (or composite)
            return {
                "source": "heritage",
                "source_url": search_url,
                "obverse_url": found[0]["url"] if len(found) >= 1 else None,
                "reverse_url": found[1]["url"] if len(found) >= 2 else (found[0]["url"] if len(found) >= 1 else None),
                "title": found[0]["title"] if len(found) >= 1 else query
            }
    except Exception as e:
        print(f"    ⚠ Heritage Auctions scrape error for query '{query}': {e}")
    return None

# ─── Error-Ref.com Scraper ────────────────────────────────────────────────────

@request
def scrape_error_ref(request: Request, data):
    """
    Scrape error-ref.com for information and visual examples.
    `data` contains a dict with keys: 'error_type' (e.g. 'clipped planchet')
    """
    error_type = data.get("error_type")
    if not error_type:
        return None
        
    # Search error-ref.com via search query
    search_url = f"https://www.error-ref.com/?s={urllib.parse.quote_plus(error_type)}"
    try:
        resp = request.get(search_url)
        soup = soupify(resp)
        # Look for search results articles
        articles = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "www.error-ref.com/" in href and href != "https://www.error-ref.com/" and "?" not in href:
                articles.append(href)
                
        articles = list(dict.fromkeys(articles)) # deduplicate
        
        if not articles:
            return None
            
        # Visit first article
        article_url = articles[0]
        art_resp = request.get(article_url)
        art_soup = soupify(art_resp)
        
        # Extract images and text
        paragraphs = [p.get_text() for p in art_soup.find_all("p") if p.get_text().strip()]
        desc = "\n\n".join(paragraphs[:3]) # First 3 paragraphs
        
        images = []
        for img in art_soup.find_all("img", src=True):
            src = img["src"]
            if "uploads/" in src and "logo" not in src.lower():
                images.append(src)
                
        images = list(dict.fromkeys(images))
        
        return {
            "source": "error-ref",
            "source_url": article_url,
            "obverse_url": images[0] if len(images) >= 1 else None,
            "reverse_url": images[1] if len(images) >= 2 else None,
            "description": desc
        }
    except Exception as e:
        print(f"    ⚠ Error-Ref scrape error for '{error_type}': {e}")
    return None

# ─── CoinWeek Scraper ─────────────────────────────────────────────────────────

@request
def scrape_coinweek(request: Request, data):
    """
    Scrape coinweek.com for coin errors, descriptions, and high-quality photographs.
    `data` contains a dict with keys: 'query' (e.g. '1934-D Peace Dollar doubled die')
    """
    query = data.get("query")
    if not query:
        return None
        
    search_url = f"https://coinweek.com/?s={urllib.parse.quote_plus(query)}"
    try:
        resp = request.get(search_url)
        soup = soupify(resp)
        
        # Find article links
        article_links = []
        # CoinWeek search results typically contain <h2 class="entry-title"><a href="...">
        for h2 in soup.find_all("h2", class_=re.compile(r"entry-title|post-title|title", re.I)):
            a = h2.find("a", href=True)
            if a:
                article_links.append(a["href"])
                
        # Fallback to search links in main body
        if not article_links:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "coinweek.com/" in href and any(x in href for x in ["/19", "/20", "error", "die", "dollar", "cent"]):
                    if not any(x in href for x in ["?s=", "category", "tag", "author", "wp-content"]):
                        article_links.append(href)
                        
        article_links = list(dict.fromkeys(article_links))
        
        if not article_links:
            print(f"    ⚠ No CoinWeek article found for query: {query}")
            return None
            
        article_url = article_links[0]
        print(f"    Scraping CoinWeek article: {article_url}")
        
        art_resp = request.get(article_url)
        art_soup = soupify(art_resp)
        
        # Extract main text
        paragraphs = []
        for p in art_soup.find_all("p"):
            txt = p.get_text().strip()
            if txt and len(txt) > 60 and not any(x in txt.lower() for x in ["copyright", "subscribe", "newsletter", "advertisement"]):
                paragraphs.append(txt)
        
        desc = "\n\n".join(paragraphs[:3]) # Top 3 paragraphs
        
        # Extract high-res images from post content
        images = []
        # Post content is typically in <div class="entry-content"> or <article>
        content_div = art_soup.find(class_=re.compile(r"entry-content|post-content|article-content", re.I)) or art_soup
        
        for img in content_div.find_all("img", src=True):
            src = img["src"]
            # Exclude avatars, ads, logo images
            if not any(x in src.lower() for x in ["logo", "avatar", "advertis", "banner", "icon", "widget"]):
                # CoinWeek often uses srcset or lazy sizes. Let's resolve high-res if possible
                for attr in ["data-orig-file", "data-large-file", "data-src", "src"]:
                    val = img.get(attr)
                    if val and val.startswith("http"):
                        src = val
                        break
                images.append(src)
                
        images = list(dict.fromkeys(images))
        
        if images:
            return {
                "source": "coinweek",
                "source_url": article_url,
                "obverse_url": images[0] if len(images) >= 1 else None,
                "reverse_url": images[1] if len(images) >= 2 else (images[0] if len(images) >= 1 else None),
                "description": desc
            }
    except Exception as e:
        print(f"    ⚠ CoinWeek scrape error for query '{query}': {e}")
    return None


# ─── USMint.gov Scraper ────────────────────────────────────────────────────────

@request
def scrape_usmint(request: Request, data):
    """
    Search usmint.gov for coin designs, descriptions, and official public domain images.
    `data` contains a dict with keys: 'query' (e.g. 'Patsy Takemoto Mink')
    """
    query = data.get("query")
    if not query:
        return None
        
    search_url = f"https://www.usmint.gov/?s={urllib.parse.quote_plus(query)}"
    try:
        resp = request.get(search_url)
        if "waiting room" in resp.text.lower() or resp.status_code in [403, 429]:
            print(f"    [USMint.gov] Request blocked or placed in waiting room (Status {resp.status_code}). Skipping...")
            return None
        soup = soupify(resp)
        
        # Find links pointing to learn or coin programs
        article_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "usmint.gov/learn/" in href or "usmint.gov/news/" in href or "usmint.gov/coins/" in href:
                if not any(x in href for x in ["?s=", "/category/", "/tag/", "wp-content"]):
                    article_links.append(href)
                    
        article_links = list(dict.fromkeys(article_links))
        
        if not article_links:
            # Fallback catalog search
            catalog_url = f"https://catalog.usmint.gov/search?q={urllib.parse.quote_plus(query)}"
            cat_resp = request.get(catalog_url)
            cat_soup = soupify(cat_resp)
            for a in cat_soup.find_all("a", href=True):
                href = a["href"]
                if "/search?" not in href and (".html" in href or "-product-" in href):
                    abs_href = href if href.startswith("http") else f"https://catalog.usmint.gov{href}"
                    article_links.append(abs_href)
            article_links = list(dict.fromkeys(article_links))
            
        if not article_links:
            return None
            
        # Visit first page
        target_url = article_links[0]
        art_resp = request.get(target_url)
        art_soup = soupify(art_resp)
        
        paragraphs = []
        for p in art_soup.find_all("p"):
            txt = p.get_text().strip()
            if txt and len(txt) > 60 and not any(x in txt.lower() for x in ["copyright", "subscribe", "newsletter"]):
                paragraphs.append(txt)
                
        desc = "\n\n".join(paragraphs[:3])
        
        # Extract images from content
        images = []
        for img in art_soup.find_all("img", src=True):
            src = img["src"]
            if "content/dam/usmint" in src or "uploads/" in src or "product/" in src:
                # Resolve relative paths
                if src.startswith("/"):
                    src = f"https://www.usmint.gov{src}"
                if not any(x in src.lower() for x in ["logo", "icon", "banner", "150x", "300x"]):
                    images.append(src)
                    
        images = list(dict.fromkeys(images))
        
        if images:
            return {
                "source": "usmint",
                "source_url": target_url,
                "obverse_url": images[0] if len(images) >= 1 else None,
                "reverse_url": images[1] if len(images) >= 2 else (images[0] if len(images) >= 1 else None),
                "description": desc,
                "title": query
            }
    except Exception as e:
        print(f"    ⚠ USMint.gov scrape error for query '{query}': {e}")
    return None

