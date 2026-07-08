import re
import urllib.parse
import json
import time
from bs4 import BeautifulSoup
from botasaurus.request import request, Request
from botasaurus.soupify import soupify
import requests

# Load config settings
try:
    from .config import USER_AGENTS, DEFAULT_DELAY, REQUEST_TIMEOUT, PROXIES, get_scrape_proxy
except ImportError:
    def get_scrape_proxy(): return {"http": None, "https": None}
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    DEFAULT_DELAY = 1.5
    REQUEST_TIMEOUT = 30
    PROXIES = {"http": None, "https": None}

UA = "NumistaAI/1.0 (educational numismatic archive; contact eric.seaman@yahoo.com)"
WIKI_API = "https://commons.wikimedia.org/w/api.php"

NUMISTA_API_KEY = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe'
NUMISTA_API_BASE = 'https://api.numista.com/v3'

# ─── Numista API Scraper ──────────────────────────────────────────────────────

def search_numista_api(query):
    """
    Search the Numista API for types matching a keyword query.
    """
    url = f"{NUMISTA_API_BASE}/types"
    params = {'q': query}
    headers = {
        'Numista-API-Key': NUMISTA_API_KEY,
        'Accept': 'application/json',
        'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)'
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return resp.json().get('types', [])
    except Exception as e:
        print(f"    ⚠ Numista API search error for '{query}': {e}")
    return []

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

def is_article_related(title, error, query=None):
    if not title or not error:
        return True
    title_lower = title.lower()
    name_lower = error.get("name", "").lower()
    short_lower = error.get("shortName", "").lower()
    error_id = error.get("id", "").lower()
    
    # If query is general term, allow general titles matching query
    if query:
        q_clean = query.lower().strip()
        general_terms = [
            "die gouge", "die errors", "striking errors", "currency", "striking", "die chips",
            "struck through", "struck-through", "grease", "planchet", "planchet errors",
            "struck through grease", "struck-through grease"
        ]
        if q_clean in general_terms:
            return q_clean in title_lower or any(word in title_lower for word in q_clean.split())
            
    # Check if the title has general modern coins or list indicators (to allow list articles like "5 Modern Quarters...")
    list_indicators = ["modern", "quarter", "cent", "dollar", "nickel", "dime", "worth", "money", "find", "change", "error", "die", "misprint", "collect"]
    has_list_indicator = any(word in title_lower for word in list_indicators)
    
    # Specific date/variety checks
    if "1955" in name_lower:
        return "1955" in title_lower or "double" in title_lower or "ddo" in title_lower or has_list_indicator
        
    if "wisconsin" in name_lower:
        return "wisconsin" in title_lower or "leaf" in title_lower or has_list_indicator
        
    if "bat" in name_lower or "samoa" in name_lower:
        return "samoa" in title_lower or "bat" in title_lower or has_list_indicator
        
    if "new jersey" in name_lower or "nj-quarter" in error_id:
        return "new jersey" in title_lower or "nj" in title_lower or "crossroads" in title_lower or has_list_indicator
        
    if "inverted back" in name_lower or "inverted-back" in error_id:
        currency_indicators = ["note", "bill", "currency", "banknote", "conway", "paper", "worth", "money", "find", "error", "misprint", "collect"]
        has_currency_indicator = any(word in title_lower for word in currency_indicators)
        return "inverted" in title_lower or "back" in title_lower or has_currency_indicator
        
    if "clipped" in name_lower or "clip" in name_lower:
        return "clip" in title_lower or "planchet" in title_lower or has_list_indicator
        
    # General fallback: check if any of the keywords are in the title
    words = re.findall(r'[a-z0-9]{3,}', short_lower or name_lower)
    stops = {"coin", "error", "quarter", "cent", "dollar", "nickel", "dime", "mint", "state", "the", "and"}
    keywords = [w for w in words if w not in stops]
    if not keywords:
        return True
    return any(kw in title_lower for kw in keywords) or has_list_indicator


def validate_article_content(text, error, query=None):
    if not text or not error:
        return True
    text_lower = text.lower()
    error_id = error.get("id", "").lower()
    name_lower = error.get("name", "").lower()
    
    general_terms = [
        "die gouge", "die errors", "striking errors", "currency", "striking", "die chips",
        "struck through", "struck-through", "grease", "die gouges", "die chip", "die chips",
        "doubled die", "clipped planchet", "curved clip", "planchet", "planchet errors",
        "struck through grease", "struck-through grease"
    ]
    is_general_query = query and query.lower().strip() in general_terms
    
    if "1955-ddo" in error_id or "1955" in name_lower:
        return "1955" in text_lower and ("double" in text_lower or "ddo" in text_lower)
        
    if "wisconsin" in name_lower:
        return "wisconsin" in text_lower and "leaf" in text_lower
        
    if "bat" in name_lower or "samoa" in name_lower:
        return "samoa" in text_lower and ("bat" in text_lower or "fruit bat" in text_lower)
        
    if "new jersey" in name_lower or "nj-quarter" in error_id:
        if is_general_query:
            if "die-gouge" in error_id or "gouge" in name_lower:
                return "gouge" in text_lower or "extra tree" in text_lower
            if "struck-through" in error_id or "struck-through" in name_lower:
                return "grease" in text_lower or "die fill" in text_lower or "struck through grease" in text_lower or "struck-through grease" in text_lower
            return True
            
        has_nj = "new jersey" in text_lower or bool(re.search(r'\bnj\b', text_lower))
        if not has_nj:
            return False
            
        if "die-gouge" in error_id or "gouge" in name_lower:
            return "gouge" in text_lower or "extra tree" in text_lower
            
        if "struck-through" in error_id or "struck-through" in name_lower:
            return "grease" in text_lower or "die fill" in text_lower or "struck through grease" in text_lower or "struck-through grease" in text_lower
            
        return True
        
    if "inverted-back" in error_id or "inverted back" in name_lower:
        has_inverted = "inverted" in text_lower or "upside" in text_lower
        has_paper = any(w in text_lower for w in ["banknote", "paper money", "conway", "dollar bill", "currency error", "inverted back", "inverted reverse", "inverted printing"])
        is_coin_page = "die installation" in text_lower or "die gouge" in text_lower or "clipped planchet" in text_lower
        return has_inverted and has_paper and not is_coin_page
        
    if "clipped" in name_lower or "clip" in name_lower:
        return bool(re.search(r'\bclips?\b|\bclipped\b|\bplanchets?\b', text_lower))
        
    return True


def get_scored_images(soup, error, content_div, is_general_query=False):
    if not error:
        images = []
        for img in content_div.find_all("img", src=True):
            src = img["src"]
            if not any(x in src.lower() for x in ["logo", "avatar", "advertis", "banner", "icon", "widget", "bio", "author", "staff", "headshot", "person", "profile", "gravatar"]):
                for attr in ["bv-data-src", "data-orig-file", "data-large-file", "data-src", "src"]:
                    val = img.get(attr)
                    if val and val.startswith("http"):
                        src = val
                        break
                images.append(src)
        return list(dict.fromkeys(images))

    name = error.get("name", "")
    short_name = error.get("shortName", "")
    category = error.get("category", "")
    subcategory = error.get("subcategory", "")
    error_id = error.get("id", "")
    
    words = re.findall(r'[a-z0-9]{3,}', (name + " " + short_name + " " + category + " " + subcategory + " " + error_id).lower())
    stops = {"coin", "error", "quarter", "cent", "dollar", "nickel", "dime", "mint", "state", "the", "and"}
    keywords = list(set([w for w in words if w not in stops]))
    
    if "1955-ddo" in error_id.lower() or "1955" in name.lower():
        keywords.extend(["1955", "ddo", "doubled"])
    if "wisconsin" in name.lower():
        keywords.extend(["wisconsin", "leaf", "corn"])
    if "bat" in name.lower() or "samoa" in name.lower():
        keywords.extend(["bat", "samoa"])
    if "jersey" in name.lower():
        keywords.extend(["jersey", "gouge", "tree", "crossroads"])
    if "inverted" in name.lower():
        keywords.extend(["inverted", "back", "upside", "reverse", "obverse"])
    if "clip" in name.lower():
        keywords.extend(["clip", "clipped", "planchet", "curved"])
        
    keywords = list(set(keywords))
    
    scored_images = []
    for img in content_div.find_all("img", src=True):
        src = img["src"]
        if any(x in src.lower() for x in ["logo", "avatar", "advertis", "banner", "icon", "widget", "bio", "author", "staff", "headshot", "person", "profile", "gravatar"]):
            continue
            
        for attr in ["bv-data-src", "data-orig-file", "data-large-file", "data-src", "src"]:
            val = img.get(attr)
            if val and val.startswith("http"):
                src = val
                break
                
        alt = img.get("alt", "").lower()
        src_lower = src.lower()
        
        parent_text = ""
        parent = img.parent
        for _ in range(2):
            if parent:
                parent_text += " " + parent.get_text()
                parent = parent.parent
        parent_text = parent_text.lower()
        
        score = 0
        for kw in keywords:
            if kw in alt:
                score += 15
            if kw in src_lower:
                score += 15
            if kw in parent_text:
                score += 5
                
        # Year penalty: check for mismatching 4-digit years if the error has target years and is not general
        years = error.get("years")
        if years and not is_general_query:
            filename = src_lower.split("/")[-1]
            found_years = set(re.findall(r'\b(1[89]\d{2}|20\d{2})\b', alt + " " + filename))
            target_years_str = [str(y) for y in years]
            mismatch = False
            for fy in found_years:
                if fy not in target_years_str:
                    mismatch = True
                    break
            if mismatch:
                score = -9999  # Discard mismatching years completely
                
        if score >= 0:
            scored_images.append((score, src))
        
    scored_images.sort(key=lambda x: x[0], reverse=True)
    
    seen = set()
    res = []
    for score, src in scored_images:
        if src not in seen:
            res.append((score, src))
            seen.add(src)
            
    return res


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
    query_clean = error_type.replace("-", " ")
    search_url = f"https://www.error-ref.com/?s={urllib.parse.quote_plus(query_clean)}"
    try:
        resp = request.get(search_url)
        soup = soupify(resp)
        # Look for search results articles
        articles = []
        for h2 in soup.find_all("h2", class_="entry-title"):
            a = h2.find("a", href=True)
            if a:
                href = a["href"]
                title = h2.get_text().strip()
                if "www.error-ref.com/" in href and href != "https://www.error-ref.com/" and "?" not in href:
                    # Filter out direct binary, PDF, or image files to prevent utf-8 decoding crashes
                    if any(href.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".zip"]) or "wp-content/uploads" in href.lower():
                        continue
                    articles.append((title, href))
                
        # Filter candidates
        error_record = data.get("error_record")
        article_url = None
        for title, url in articles:
            if is_article_related(title, error_record, query=error_type):
                article_url = url
                break
                
        if not article_url:
            return None
            
        # Visit selected article
        art_resp = request.get(article_url)
        art_soup = soupify(art_resp)
        
        # Extract text and validate content (exclude header/footer menus by targeting the content div)
        paragraphs = [p.get_text() for p in art_soup.find_all("p") if p.get_text().strip()]
        desc = "\n\n".join(paragraphs[:3]) # First 3 paragraphs
        
        content_div = art_soup.find(class_=re.compile(r"entry-content|post-content|article-content", re.I)) or art_soup.find(id="content") or art_soup
        full_text = content_div.get_text() + " " + " ".join([img.get("alt", "") for img in content_div.find_all("img")])
        if not validate_article_content(full_text, error_record, query=error_type):
            print(f"    ⚠ Article {article_url} failed content validation for {error_type}. Skipping...")
            return None
            
        # Score and extract images
        general_terms = [
            "die gouge", "die errors", "striking errors", "currency", "striking", "die chips",
            "struck through", "struck-through", "grease", "die gouges", "die chip", "die chips",
            "doubled die", "clipped planchet", "curved clip", "planchet", "planchet errors",
            "struck through grease", "struck-through grease"
        ]
        is_general_query = error_type.lower().strip() in general_terms
        
        scored = get_scored_images(art_soup, error_record, art_soup, is_general_query=is_general_query)
        min_score = 0 if is_general_query else 1
        valid_images = [url for score, url in scored if score >= min_score]
        if not valid_images:
            print(f"    ⚠ Article {article_url} has no images matching error keywords/year. Skipping...")
            return None
            
        return {
            "source": "error-ref",
            "source_url": article_url,
            "obverse_url": valid_images[0] if len(valid_images) >= 1 else None,
            "reverse_url": valid_images[1] if len(valid_images) >= 2 else None,
            "description": desc
        }
    except Exception as e:
        print(f"    ⚠ Error-Ref scrape error for '{error_type}': {e}")
    return None


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
        article_candidates = []
        for heading in soup.find_all(["h2", "h3"], class_=re.compile(r"entry-title|post-title|title|td-module-title", re.I)):
            a = heading.find("a", href=True)
            if a:
                title = heading.get_text().strip()
                article_candidates.append((title, a["href"]))
                
        # Fallback to search links in main body
        if not article_candidates:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text().strip() or href
                if "coinweek.com/" in href and any(x in href for x in ["/19", "/20", "error", "die", "dollar", "cent"]):
                    if not any(x in href for x in ["?s=", "category", "tag", "author", "wp-content"]):
                        article_candidates.append((title, href))
                        
        # Filter and validate candidates
        error_record = data.get("error_record")
        article_url = None
        for title, url in article_candidates:
            if is_article_related(title, error_record, query=query):
                print(f"    Scraping CoinWeek candidate article: {url}")
                art_resp = request.get(url)
                art_soup = soupify(art_resp)
                
                # Extract text
                paragraphs = []
                for p in art_soup.find_all("p"):
                    txt = p.get_text().strip()
                    if txt and len(txt) > 60 and not any(x in txt.lower() for x in ["copyright", "subscribe", "newsletter", "advertisement"]):
                        paragraphs.append(txt)
                desc = "\n\n".join(paragraphs[:3])
                
                # Validate text content (exclude header/footer menus by targeting the content div)
                content_div = art_soup.find(class_=re.compile(r"entry-content|post-content|article-content", re.I)) or art_soup
                full_text = content_div.get_text() + " " + " ".join([img.get("alt", "") for img in content_div.find_all("img")])
                if validate_article_content(full_text, error_record, query=query):
                    article_url = url
                    break
                else:
                    print(f"    ⚠ Article {url} failed content validation. Trying next candidate...")
                    
        if not article_url:
            print(f"    ⚠ No valid CoinWeek article found for query: {query}")
            return None
            
        # Extract high-res images from post content
        content_div = art_soup.find(class_=re.compile(r"entry-content|post-content|article-content", re.I)) or art_soup
        
        general_terms = [
            "die gouge", "die errors", "striking errors", "currency", "striking", "die chips",
            "struck through", "struck-through", "grease", "die gouges", "die chip", "die chips",
            "doubled die", "clipped planchet", "curved clip", "planchet", "planchet errors"
        ]
        q_clean = re.sub(r'\berror\b', '', query, flags=re.I).strip().lower()
        is_general_query = q_clean in general_terms
        
        scored = get_scored_images(art_soup, error_record, content_div, is_general_query=is_general_query)
        
        # Pick top images
        min_score = 0 if is_general_query else 1
        valid_images = [url for score, url in scored if score >= min_score]
        if not valid_images:
            print(f"    ⚠ Article {article_url} has no images matching error keywords/year. Skipping...")
            return None
            
        if valid_images:
            return {
                "source": "coinweek",
                "source_url": article_url,
                "obverse_url": valid_images[0] if len(valid_images) >= 1 else None,
                "reverse_url": valid_images[1] if len(valid_images) >= 2 else (valid_images[0] if len(valid_images) >= 1 else None),
                "description": desc
            }
    except Exception as e:
        print(f"    ⚠ CoinWeek scrape error for query '{query}': {e}")
    return None


def fetch_usmint_cookies():
    """
    Fetches the USMint.gov cookie string from Firestore config/usmint.
    Used to bypass 403 blocks by sharing active session cookies.
    """
    try:
        from firebase_admin import firestore
        db = firestore.client()
        doc = db.collection("config").document("usmint").get()
        if doc.exists:
            return doc.to_dict().get("cookieString")
    except Exception as e:
        print(f"    ⚠ Error fetching USMint cookies from Firestore: {e}")
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
        
    cookies = fetch_usmint_cookies()
    headers = {
        "User-Agent": USER_AGENTS[0],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1"
    }
    if cookies:
        headers["Cookie"] = cookies
        print("    [USMint.gov] Using provided session cookies for request...")

    search_url = f"https://www.usmint.gov/?s={urllib.parse.quote_plus(query)}"
    try:
        _proxy = get_scrape_proxy()
        resp = request.get(search_url, headers=headers, proxy=_proxy.get("http"))
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
            cat_resp = request.get(catalog_url, proxy=get_scrape_proxy().get("http"))
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
        art_resp = request.get(target_url, headers=headers, proxy=get_scrape_proxy().get("http"))
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

# ─── Wikimedia Commons Scraper ────────────────────────────────────────────────

def scrape_wikimedia(data):
    """
    Search Wikimedia Commons for public domain coin images.
    `data` contains a dict with keys: 'query' (e.g. '1943 Lincoln Cent')

    Validation rules enforced before accepting any candidate:
    - If a 4-digit year appears in the query, that exact year MUST appear in
      the candidate image filename/title.  A 1972 image will never be accepted
      for a 2025 query.
    - If the query contains a named series keyword (e.g. "American Innovation",
      "State Quarter", "Sacagawea"), that keyword MUST appear in the title.
    - Minimum relevance score of 2 required (at least 2 query words in title).
    """
    query = data.get("query")
    if not query:
        return None

    # ── Extract validation constraints from query ──────────────────────────────
    year_match = re.search(r'\b(1[89]\d{2}|20\d{2})\b', query)
    required_year = year_match.group(1) if year_match else None

    # Named series keywords — if any appear in the query, the result title
    # must also contain at least one of the series terms.
    SERIES_KEYWORDS = [
        "american innovation", "state quarter", "50 state", "america the beautiful",
        "sacagawea", "native american", "presidential dollar", "westward journey",
        "lincoln cent", "lincoln memorial", "lincoln wheat", "jefferson nickel",
        "buffalo nickel", "walking liberty", "morgan", "peace dollar",
        "kennedy half", "eisenhower dollar", "susan b anthony",
        "american silver eagle", "american gold eagle", "american buffalo",
        "women quarters", "american women",
    ]
    query_lower = query.lower()
    required_series = [kw for kw in SERIES_KEYWORDS if kw in query_lower]

    def is_valid_candidate(title: str) -> bool:
        """Returns True only if this image title satisfies our validation rules."""
        t = title.lower()
        # Rule 1: Year must match exactly
        if required_year and required_year not in t:
            return False
        # Rule 2: At least one series keyword must appear (if query had one)
        if required_series and not any(kw in t for kw in required_series):
            return False
        return True

    def score_candidate(title: str, side: str, query: str) -> int:
        """Score how well an image title matches our query."""
        t = title.lower()
        q_words = query.lower().split()
        score = sum(1 for w in q_words if len(w) > 2 and w in t)
        if side in t:
            score += 2
        if required_year and required_year in t:
            score += 3  # Strong bonus for exact year match
        if required_series and any(kw in t for kw in required_series):
            score += 3  # Strong bonus for series name match
        return score

    # ── Search Wikimedia for obverse and reverse ───────────────────────────────
    results = {}
    for side in ["obverse", "reverse"]:
        search_term = f"{query} coin {side}"
        api_url = (
            f"{WIKI_API}?action=query&list=search&srnamespace=6"
            f"&srsearch={urllib.parse.quote(search_term)}&srlimit=10&format=json"
        )

        try:
            resp = requests.get(api_url, headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                continue

            search_data = resp.json()
            search_results = search_data.get("query", {}).get("search", [])

            candidates = []
            for r in search_results:
                title = r.get("title", "")
                if not any(title.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    continue

                # ── VALIDATION GATE ──────────────────────────────────────────
                if not is_valid_candidate(title):
                    print(f"      [Wikimedia] Rejected '{title}' (year/series mismatch)")
                    continue

                # Resolve to direct image URL
                info_url = (
                    f"{WIKI_API}?action=query&titles={urllib.parse.quote(title)}"
                    f"&prop=imageinfo&iiprop=url&format=json"
                )
                info_resp = requests.get(info_url, headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT)
                if info_resp.status_code == 200:
                    info_data = info_resp.json()
                    pages = info_data.get("query", {}).get("pages", {})
                    for pid, page in pages.items():
                        ii = page.get("imageinfo", [])
                        if ii:
                            img_url = ii[0].get("url")
                            if img_url:
                                score = score_candidate(title, side, query)
                                candidates.append((score, img_url, title))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                best_score, best_url, best_title = candidates[0]
                # Minimum score threshold — must be a genuinely relevant match
                if best_score >= 2:
                    print(f"      [Wikimedia] Accepted '{best_title}' (score={best_score})")
                    results[side] = best_url
                else:
                    print(f"      [Wikimedia] Best candidate '{best_title}' score too low ({best_score}), rejecting.")

            time.sleep(0.5)  # Be polite
        except Exception as e:
            print(f"    ⚠ Wikimedia API error for '{search_term}': {e}")

    if results.get("obverse"):
        return {
            "source": "wikimedia",
            "source_url": "https://commons.wikimedia.org/",
            "obverse_url": results.get("obverse"),
            "reverse_url": results.get("reverse") or results.get("obverse"),
            "description": f"Public domain image for {query} sourced from Wikimedia Commons."
        }
    return None


# ─── PCGS PhotoGrade Online ───────────────────────────────────────────────────

def scrape_pcgs_photograde(data):
    """
    Search PCGS CoinFacts for high-quality reference coin images.
    PCGS CoinFacts is publicly accessible and contains professional obverse/reverse photos.
    """
    query = data.get("query", "")
    year = data.get("year", "")
    denomination = data.get("denomination", "")
    if not query:
        return None
    try:
        search_url = f"https://www.pcgs.com/coinfacts/search?q={urllib.parse.quote_plus(query)}"
        resp = requests.get(search_url, headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT, proxies=get_scrape_proxy())
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Find first coin detail link
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/coinfacts/coin/" in href or "/coinfacts/detail/" in href:
                links.append(href if href.startswith("http") else f"https://www.pcgs.com{href}")
        if not links:
            return None
        # Visit first result
        detail = requests.get(links[0], headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT, proxies=get_scrape_proxy())
        if detail.status_code != 200:
            return None
        dsoup = BeautifulSoup(detail.text, "html.parser")
        # PCGS uses img tags with class containing 'obverse' / 'reverse' or data-side
        obverse_url = None
        reverse_url = None
        for img in dsoup.find_all("img"):
            src = img.get("src", "") or img.get("data-src", "")
            alt = img.get("alt", "").lower()
            cls = " ".join(img.get("class", [])).lower()
            if not src or "placeholder" in src.lower():
                continue
            if "obverse" in alt or "obverse" in cls or "front" in alt:
                obverse_url = src if src.startswith("http") else f"https://www.pcgs.com{src}"
            elif "reverse" in alt or "reverse" in cls or "back" in alt:
                reverse_url = src if src.startswith("http") else f"https://www.pcgs.com{src}"
        if not obverse_url:
            return None
        return {
            "source": "pcgs",
            "source_url": links[0],
            "obverse_url": obverse_url,
            "reverse_url": reverse_url,
            "description": f"PCGS CoinFacts reference image for {query}."
        }
    except Exception as e:
        print(f"    ⚠ PCGS PhotoGrade scrape error: {e}")
    return None


# ─── NGC Coin Explorer ────────────────────────────────────────────────────────

def scrape_ngc(data):
    """
    Search NGC Coin Explorer for reference images.
    NGC's coin catalog is publicly browsable with quality obverse/reverse images.
    """
    query = data.get("query", "")
    year = data.get("year", "")
    denomination = data.get("denomination", "")
    if not query:
        return None
    try:
        # NGC coin explorer search
        search_url = f"https://www.ngccoin.com/coin-explorer/search/?q={urllib.parse.quote_plus(query)}"
        resp = requests.get(search_url, headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT, proxies=get_scrape_proxy())
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Find coin detail links
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/coin-explorer/" in href and ("/detail/" in href or "/coins/" in href):
                links.append(href if href.startswith("http") else f"https://www.ngccoin.com{href}")
        if not links:
            return None
        detail = requests.get(links[0], headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT, proxies=get_scrape_proxy())
        if detail.status_code != 200:
            return None
        dsoup = BeautifulSoup(detail.text, "html.parser")
        obverse_url = None
        reverse_url = None
        for img in dsoup.find_all("img"):
            src = img.get("src", "") or img.get("data-src", "")
            alt = img.get("alt", "").lower()
            if not src or "logo" in src.lower() or "icon" in src.lower():
                continue
            if "obverse" in alt or "front" in alt:
                obverse_url = src if src.startswith("http") else f"https://www.ngccoin.com{src}"
            elif "reverse" in alt or "back" in alt:
                reverse_url = src if src.startswith("http") else f"https://www.ngccoin.com{src}"
        # Fallback: grab first large coin image
        if not obverse_url:
            for img in dsoup.find_all("img"):
                src = img.get("src", "")
                if src and ("coin" in src.lower() or "numis" in src.lower()):
                    obverse_url = src if src.startswith("http") else f"https://www.ngccoin.com{src}"
                    break
        if not obverse_url:
            return None
        return {
            "source": "ngc",
            "source_url": links[0],
            "obverse_url": obverse_url,
            "reverse_url": reverse_url,
            "description": f"NGC Coin Explorer reference image for {query}."
        }
    except Exception as e:
        print(f"    ⚠ NGC scrape error: {e}")
    return None


# ─── Smithsonian National Museum of American History ─────────────────────────

def scrape_smithsonian(data):
    """
    Search the Smithsonian NMAH online collection for numismatic objects.
    Uses the Smithsonian Open Access API (no key required for basic searches).
    Images are public domain / CC0.
    """
    query = data.get("query", "")
    if not query:
        return None
    try:
        api_url = "https://api.si.edu/openaccess/api/v1.0/search"
        params = {
            "q": f"{query} coin",
            "unit_code": "NMAH",
            "type": "edanmdm",
            "rows": 5,
            "api_key": "DEMO_KEY"  # Public demo key — sufficient for low-volume use
        }
        resp = requests.get(api_url, params=params, headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return None
        data_json = resp.json()
        rows = data_json.get("response", {}).get("rows", [])
        for row in rows:
            descriptor = row.get("content", {}).get("descriptiveNonRepeating", {})
            online_media = descriptor.get("online_media", {}).get("media", [])
            for media in online_media:
                if media.get("type") == "Images":
                    resources = media.get("resources", [])
                    for res in resources:
                        url = res.get("url", "")
                        if url and (url.endswith(".jpg") or url.endswith(".png") or "iiif" in url):
                            return {
                                "source": "smithsonian",
                                "source_url": row.get("id", "https://americanhistory.si.edu/"),
                                "obverse_url": url,
                                "reverse_url": None,
                                "description": row.get("title", f"Smithsonian NMAH reference for {query}.")
                            }
    except Exception as e:
        print(f"    ⚠ Smithsonian NMAH scrape error: {e}")
    return None


# ─── USA CoinBook ─────────────────────────────────────────────────────────────

def scrape_usacoinbook(data):
    """
    Search USA CoinBook (usacoinbook.com) for coin images.
    A well-structured collector reference site with clean obverse/reverse photos.
    """
    query = data.get("query", "")
    year = data.get("year", "")
    denomination = data.get("denomination", "").lower()
    if not query:
        return None
    try:
        # Map denomination to URL slug used by USA CoinBook
        denom_map = {
            "cent": "lincoln-cents",
            "cents": "lincoln-cents",
            "penny": "lincoln-cents",
            "nickel": "jefferson-nickels",
            "nickels": "jefferson-nickels",
            "dime": "roosevelt-dimes",
            "dimes": "roosevelt-dimes",
            "quarter": "washington-quarters",
            "quarters": "washington-quarters",
            "half dollar": "kennedy-half-dollars",
            "dollar": "eisenhower-dollars",
        }
        slug = None
        for key, val in denom_map.items():
            if key in denomination:
                slug = val
                break

        search_url = f"https://www.usacoinbook.com/coins/search/?q={urllib.parse.quote_plus(query)}"
        resp = requests.get(search_url, headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT, proxies=get_scrape_proxy())
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Find coin detail links
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/coins/" in href and href.count("/") >= 3:
                links.append(href if href.startswith("http") else f"https://www.usacoinbook.com{href}")
        if not links:
            return None
        detail = requests.get(links[0], headers={"User-Agent": UA}, timeout=REQUEST_TIMEOUT, proxies=get_scrape_proxy())
        if detail.status_code != 200:
            return None
        dsoup = BeautifulSoup(detail.text, "html.parser")
        obverse_url = None
        reverse_url = None
        for img in dsoup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "").lower()
            if not src or "logo" in src.lower() or "ad" in src.lower():
                continue
            if "obverse" in alt or "front" in alt or "heads" in alt:
                obverse_url = src if src.startswith("http") else f"https://www.usacoinbook.com{src}"
            elif "reverse" in alt or "back" in alt or "tails" in alt:
                reverse_url = src if src.startswith("http") else f"https://www.usacoinbook.com{src}"
        # Fallback: first coin image on the page
        if not obverse_url:
            for img in dsoup.find_all("img"):
                src = img.get("src", "")
                if src and (".jpg" in src or ".png" in src) and "coin" in src.lower():
                    obverse_url = src if src.startswith("http") else f"https://www.usacoinbook.com{src}"
                    break
        if not obverse_url:
            return None
        return {
            "source": "usacoinbook",
            "source_url": links[0],
            "obverse_url": obverse_url,
            "reverse_url": reverse_url,
            "description": f"USA CoinBook reference image for {query}."
        }
    except Exception as e:
        print(f"    ⚠ USA CoinBook scrape error: {e}")
    return None
