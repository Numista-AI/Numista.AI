import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from google.cloud import firestore
import google.auth
from google.genai import types

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("greysheet_service")

# Production API Endpoint
BASE_URL = "https://cpgpublicapiv2.greysheet.com/api"

# Default fallback credentials for development/testing
DEFAULT_API_KEY = "1FCAE3B4-966A-4F25-AFA1-BE242C26856B"
DEFAULT_API_TOKEN = "D876F1BA-DDC4-4F80-B155-509AB3B6B970"

class GreysheetService:
    def __init__(self, db: Optional[firestore.Client] = None):
        self._db = db
        self._api_key = None
        self._api_token = None
        self._headers = None
        self._leaf_nodes_cache = None  # In-memory cache of leaf nodes
        self._collectibles_cache = {}  # Cache of node_id -> collectibles list
        self._pricing_cache = {}       # Cache of gsid -> pricing data list
        
    def _lazy_init(self):
        """Lazy load credentials and setup headers."""
        if self._headers:
            return
            
        # 1. Try to read from environment variables
        self._api_key = os.environ.get("GREYSHEET_API_KEY")
        self._api_token = os.environ.get("GREYSHEET_API_TOKEN")
        
        # 2. Try Firestore config if DB is available and env vars are missing
        if (not self._api_key or not self._api_token) and self._db:
            try:
                doc = self._db.collection("config").document("greysheet").get()
                if doc.exists:
                    data = doc.to_dict()
                    self._api_key = self._api_key or data.get("apiKey")
                    self._api_token = self._api_token or data.get("apiToken")
                    logger.info("[Greysheet] Loaded credentials from Firestore config/greysheet")
            except Exception as e:
                logger.warning(f"[Greysheet] Failed to load credentials from Firestore: {e}")
                
        # 3. Fallback to user-provided dev credentials
        self._api_key = self._api_key or DEFAULT_API_KEY
        self._api_token = self._api_token or DEFAULT_API_TOKEN
        
        self._headers = {
            "x-api-key": self._api_key,
            "x-api-token": self._api_token,
            "Content-Type": "application/json"
        }
        logger.info("[Greysheet] GreysheetService initialized.")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        self._lazy_init()
        url = f"{BASE_URL}/{endpoint}"
        try:
            # Bypass SSL certificate verification for expired host certs
            response = requests.get(url, headers=self._headers, params=params, verify=False, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"[Greysheet] API Error: {url} returned status {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"[Greysheet] HTTP Error calling {url}: {e}")
            return None

    def get_node_children(self, node_id: int) -> List[Dict[str, Any]]:
        """Fetch children of a parent node."""
        res = self._get("GetNodeChildrenRequest", {"NodeId": node_id})
        return res.get("Data", []) if res else []

    def get_collectible_by_node(self, node_id: int) -> List[Dict[str, Any]]:
        """Fetch all collectibles under a leaf node."""
        if node_id in self._collectibles_cache:
            return self._collectibles_cache[node_id]
        res = self._get("GetCollectibleByNodeRequest", {"NodeId": node_id})
        data = res.get("Data", []) if res else []
        self._collectibles_cache[node_id] = data
        return data

    def get_pricing(self, gsid: int) -> List[Dict[str, Any]]:
        """Fetch pricing table for a specific GSID."""
        if gsid in self._pricing_cache:
            return self._pricing_cache[gsid]
        res = self._get("GetPricingRequest", {"Gsid": gsid})
        data = res.get("Data", []) if res else []
        self._pricing_cache[gsid] = data
        return data

    def get_collectible(self, gsid: int) -> Optional[Dict[str, Any]]:
        """Fetch a single collectible's metadata by GSID."""
        res = self._get("GetCollectibleRequest", {"Gsid": gsid})
        if res and res.get("Data"):
            data = res.get("Data")
            return data[0] if isinstance(data, list) and len(data) > 0 else None
        return None

    def crawl_all_us_leaf_nodes(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Recursively crawl U.S. Coins (NodeId=1) to retrieve all leaf nodes.
        Leaf nodes are nodes with CollectibleChildrenCountLive > 0 or NodeChildrenCountLive == 0.
        """
        if self._leaf_nodes_cache and not force_refresh:
            return self._leaf_nodes_cache

        logger.info("[Greysheet] Crawling U.S. Coins catalog nodes...")
        leaf_nodes = []
        queue = [{"Id": 1, "Name": "U.S. Coins"}]  # Start with U.S. Coins
        visited = set()

        while queue:
            current = queue.pop(0)
            node_id = current["Id"]
            if node_id in visited:
                continue
            visited.add(node_id)

            children = self.get_node_children(node_id)
            if not children:
                # Leaf node
                leaf_nodes.append(current)
            else:
                for child in children:
                    child_id = child.get("Id")
                    child_name = child.get("Name", "")
                    live_collectibles = child.get("CollectibleChildrenCountLive", 0)
                    live_children = child.get("NodeChildrenCountLive", 0)
                    
                    child_info = {
                        "Id": child_id,
                        "Name": child_name,
                        "ParentNode_Id": node_id
                    }

                    if live_collectibles > 0 or live_children == 0:
                        leaf_nodes.append(child_info)
                    else:
                        queue.append(child_info)

        self._leaf_nodes_cache = leaf_nodes
        logger.info(f"[Greysheet] Found {len(leaf_nodes)} U.S. Coins leaf nodes.")
        return leaf_nodes

    # ── Denomination normaliser ───────────────────────────────────────────────
    # Maps how the app stores denominations → Greysheet catalog naming.
    # Greysheet uses "$5 Liberty Gold", "$10 Indian Gold", etc.
    # Our DB stores "Five Dollars (Half Eagle)", "Ten Dollars (Eagle)", etc.
    # Without this map the fuzzy matcher picks up the wrong keyword (e.g. "half")
    # from "Half Eagle" and matches Half Cents/Dimes/Dollars instead of gold coins.
    _DENOM_NORM_MAP: List[tuple] = [
        # Word-form gold denominations (must be checked BEFORE generic keyword fallback)
        ("double eagle",    "$20 gold"),
        ("twenty dollar",   "$20 gold"),
        ("twenty dollars",  "$20 gold"),
        ("ten dollar",      "$10 gold"),
        ("ten dollars",     "$10 gold"),
        ("eagle",           "$10 gold"),   # plain "eagle" = $10 gold eagle
        ("five dollar",     "$5 gold"),
        ("five dollars",    "$5 gold"),
        ("half eagle",      "$5 gold"),    # half eagle = $5 face value gold
        ("quarter eagle",   "$2.50 gold"),
        ("two and half",    "$2.50 gold"),
        ("three dollar",    "$3 gold"),
        ("three dollars",   "$3 gold"),
        ("four dollar",     "$4 gold"),
        ("stella",          "$4 gold"),
        ("one dollar gold", "$1 gold"),
    ]

    @staticmethod
    def _normalise_denomination(denomination: str) -> List[str]:
        """
        Returns a list of Greysheet-compatible search terms for a given stored
        denomination string.  Always returns the original denomination as well so
        exact or partial matches still work for standard coins.
        """
        terms = [denomination.lower()]
        denom_lower = denomination.lower()
        for pattern, replacement in GreysheetService._DENOM_NORM_MAP:
            if pattern in denom_lower:
                terms.insert(0, replacement)   # prefer the normalised term
                break
        return terms

    def resolve_gsid_hybrid(
        self,
        coin_data: Dict[str, Any],
        genai_client: Optional[Any] = None,
        primary_model: str = "gemini-3.5-flash"
    ) -> Optional[int]:
        """
        Map a coin in the inventory to its Greysheet GSID.
        Uses PCGS number matching first, otherwise calls Gemini to select from candidate collectibles.
        """
        # Ingestion Type Guardrails: Non-coin items bypass the coin lookup
        item_type = str(coin_data.get("item_type") or coin_data.get("Item Type") or coin_data.get("Item_Type") or "").lower()
        if item_type in ["paper_currency", "medal", "supply"] or "medal" in item_type or "paper" in item_type or "supply" in item_type:
            logger.info(f"[Greysheet] Ingestion guardrail triggered: item_type='{item_type}' is non-coin. Bypassing Greysheet resolution.")
            return None

        # Country Guardrail: Only resolve U.S. coins (or unknown/empty countries)
        country = str(coin_data.get("Country") or coin_data.get("country") or "").lower().strip()
        if country and country not in ["us", "usa", "united states", "unknown"]:
            logger.info(f"[Greysheet] Country guardrail triggered: country='{country}' is non-U.S. Bypassing Greysheet resolution.")
            return None

        # Extract coin attributes
        pcgs_number = coin_data.get("PCGSNo") or coin_data.get("pcgs_number") or coin_data.get("pcgsNo") or coin_data.get("PCGS Number")
        if not pcgs_number and coin_data.get("certificationNumber") and coin_data.get("gradingService") == "PCGS":
            # Cert exists, but no PCGS number resolved yet. Should fetch pcgs number first if possible.
            pass

        year = str(coin_data.get("Year") or coin_data.get("year") or "")
        mint_mark = str(coin_data.get("MintMark") or coin_data.get("mintMark") or coin_data.get("Mint Mark") or "").upper()
        denomination = str(coin_data.get("Denomination") or coin_data.get("denomination") or "")
        series = str(coin_data.get("ProgramSeries") or coin_data.get("programSeries") or coin_data.get("series") or coin_data.get("Program/Series") or "")
        variety = str(coin_data.get("Variety") or coin_data.get("variety") or "")

        logger.info(f"[Greysheet] Resolving GSID for: Year={year}, Mint={mint_mark}, Denomination={denomination}, Series={series}, PCGS={pcgs_number}")

        # Step 1: Find matching leaf nodes by series or denomination
        leaf_nodes = self.crawl_all_us_leaf_nodes()

        # Normalise the stored denomination into Greysheet-compatible search terms.
        # e.g. "Five Dollars (Half Eagle)" -> ["$5 gold", "five dollars (half eagle)"]
        # This prevents "half" in "Half Eagle" from matching Half Cents/Dimes/Dollars.
        denom_terms = self._normalise_denomination(denomination) if denomination else []

        # Fuzzy match leaf nodes by preferring primary denomination keywords to ensure we capture
        # all relevant series (e.g. Statehood, ATB, and American Women Quarters when denomination is "Quarter").
        matched_nodes = []
        denom_lower = denomination.lower()
        primary_kw = None
        
        if "double eagle" in denom_lower or "twenty" in denom_lower or "$20" in denom_lower:
            primary_kw = "$20"
        elif "half eagle" in denom_lower or "five dollar" in denom_lower or "five dollars" in denom_lower or "$5" in denom_lower:
            primary_kw = "$5"
        elif "quarter eagle" in denom_lower or "two and half" in denom_lower or "$2.5" in denom_lower or "$2.50" in denom_lower:
            primary_kw = "$2.50"
        elif "ten dollar" in denom_lower or "ten dollars" in denom_lower or "$10" in denom_lower:
            primary_kw = "$10"
        elif "three dollar" in denom_lower or "$3" in denom_lower:
            primary_kw = "$3"
        elif "quarter" in denom_lower:
            primary_kw = "quarter"
        elif "dime" in denom_lower:
            primary_kw = "dime"
        elif "nickel" in denom_lower or "five cents" in denom_lower or "5c" in denom_lower:
            primary_kw = "nickel"
        elif "cent" in denom_lower or "penny" in denom_lower or "1c" in denom_lower:
            primary_kw = "cent"
        elif "half dollar" in denom_lower or ("half" in denom_lower and "dollar" in denom_lower):
            primary_kw = "half dollar"
        elif "half cent" in denom_lower:
            primary_kw = "half cent"
        elif "half dime" in denom_lower:
            primary_kw = "half dime"
        elif "dollar" in denom_lower or "1$" in denom_lower:
            primary_kw = "dollar"

        if primary_kw:
            for node in leaf_nodes:
                node_name_lower = node["Name"].lower()
                if primary_kw in node_name_lower:
                    matched_nodes.append(node)

        # If no primary keyword match, do a fuzzy substring match on series/denomination as fallback
        if not matched_nodes:
            logger.info("[Greysheet] No direct primary keyword node match. Trying fallback fuzzy substring match.")
            search_terms = []
            if series:
                search_terms.append(series.lower())
            search_terms.extend(denom_terms)

            for node in leaf_nodes:
                node_name_lower = node["Name"].lower()
                for term in search_terms:
                    if term in node_name_lower or node_name_lower in term:
                        matched_nodes.append(node)
                        break

        # Step 2: Fetch candidates under matched leaf nodes
        candidates = []
        for node in matched_nodes:
            node_id = node["Id"]
            logger.info(f"[Greysheet] Fetching collectibles for node: {node['Name']} (NodeId={node_id})")
            node_collectibles = self.get_collectible_by_node(node_id)
            candidates.extend(node_collectibles)

        if not candidates:
            logger.warning("[Greysheet] No candidate collectibles found for matched nodes.")
            return None

        # Step 3: PCGS Number Match (If certified)
        if pcgs_number:
            pcgs_str = str(pcgs_number).strip()
            for cand in candidates:
                cand_pcgs = str(cand.get("PcgsNumber", "")).strip()
                if cand_pcgs == pcgs_str:
                    logger.info(f"[Greysheet] Match found via PCGS number: {cand['Name']} (GSID={cand['Gsid']})")
                    return cand["Gsid"]

        # Step 4: AI Resolution for raw coins
        if genai_client:
            logger.info(f"[Greysheet] Invoking Gemini to map raw coin to GSID from {len(candidates)} candidates.")
            # Format candidate list for Gemini
            candidate_list_str = ""
            for cand in candidates:
                candidate_list_str += f"- GSID: {cand['Gsid']} | Name: {cand['Name']} | PCGS No: {cand.get('PcgsNumber', 'N/A')}\n"

            prompt = f"""
You are a expert numismatic data mapper. Match the following inventory coin record to the correct Greysheet Collectible GSID from the candidates listed below.

INVENTORY COIN RECORD:
- Year: {year}
- Mint Mark: {mint_mark}
- Denomination: {denomination}
- Series/Program: {series}
- Variety/Description: {variety}

CANDIDATE GREYSHEET COLLECTIBLES:
{candidate_list_str}

Select the SINGLE best GSID that exactly matches the inventory coin.
- Return ONLY a JSON object containing:
  "gsid": (integer or null, the matched GSID)
  "confidence": (float between 0.0 and 1.0)
  "explanation": (brief string explanation of why this was chosen)

If none of the candidates match, set "gsid" to null.
Do not output markdown code blocks, just raw JSON.
"""
            try:
                response = genai_client.models.generate_content(
                    model=primary_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                res_json = json.loads(response.text)
                gsid = res_json.get("gsid")
                confidence = res_json.get("confidence", 0.0)
                logger.info(f"[Greysheet AI] Resolution response: {res_json}")
                if gsid and confidence >= 0.7:
                    logger.info(f"[Greysheet AI] Selected GSID: {gsid} with confidence {confidence}")
                    return int(gsid)
            except Exception as e:
                logger.error(f"[Greysheet AI] Failed to resolve GSID via Gemini: {e}")

        # Step 5: Fallback to text matching
        logger.info("[Greysheet] Fallback to simple text keyword matching.")
        best_cand = None
        best_score = 0
        year_str = str(year)

        # Collect descriptive terms from the coin data
        descriptive_terms = []
        name_val = coin_data.get("Name") or coin_data.get("name")
        if name_val:
            descriptive_terms.extend(str(name_val).lower().split())
        theme_val = coin_data.get("Theme/Subject") or coin_data.get("theme")
        if theme_val:
            descriptive_terms.extend(str(theme_val).lower().replace("&", " ").replace("-", " ").split())
        if variety:
            descriptive_terms.extend(str(variety).lower().split())
            
        # Filter out common stop words or irrelevant details
        stop_words = {"&", "and", "or", "the", "a", "an", "of", "in", "on", "at", "to", "with", "couple", "compact"}
        descriptive_terms = [term for term in descriptive_terms if term not in stop_words and len(term) > 2]

        import re
        for cand in candidates:
            cand_name = cand["Name"].lower()

            # Roll/Set Guardrail: Skip or penalise rolls/sets if the coin itself is not a roll/set
            cand_has_roll_or_set = any(x in cand_name for x in ["roll", "set", "bag", "box", "case", "folder", "tribute"])
            coin_desc = f"{name_val or ''} {variety or ''} {theme_val or ''} {series or ''} {denomination or ''}".lower()
            coin_is_roll_or_set = any(x in coin_desc for x in ["roll", "set", "bag", "box", "case", "folder", "tribute"])
            if cand_has_roll_or_set and not coin_is_roll_or_set:
                continue

            # Year Guardrail: Skip candidate if it has a specific year/range in the name that doesn't match the coin's year
            if year_str and year_str.isdigit():
                cand_years = [int(y) for y in re.findall(r'\b\d{4}\b', cand_name)]
                if cand_years:
                    range_match = re.search(r'(\d{4})\s*[-–to\s]+\s*(\d{4})', cand_name)
                    if range_match:
                        start_yr = int(range_match.group(1))
                        end_yr = int(range_match.group(2))
                        if not (start_yr <= int(year_str) <= end_yr):
                            continue
                    elif int(year_str) not in cand_years:
                        continue

            score = 0
            if year_str and year_str in cand_name:
                score += 10
            if mint_mark and f"-{mint_mark.lower()}" in cand_name:
                score += 5
            elif mint_mark and f" {mint_mark.lower()} " in cand_name:
                score += 3
            elif not mint_mark and ("no mint mark" in cand_name or "philadelphia" in cand_name):
                score += 2
                
            # Match descriptive keywords
            for term in descriptive_terms:
                if term in cand_name:
                    score += 15

            if score > best_score:
                best_score = score
                best_cand = cand

        if best_cand and best_score >= 10:
            logger.info(f"[Greysheet] Best text match: {best_cand['Name']} (GSID={best_cand['Gsid']}) with score {best_score}")
            return best_cand["Gsid"]

        logger.warning("[Greysheet] Could not resolve GSID.")
        return None
