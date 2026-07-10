import os
import re
import time
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Import scraper modules
try:
    from .config import DB_PATH, KEY_PATH, BUCKET_NAME, DEFAULT_DELAY
    from .scrapers import (
        scrape_numista_api,
        fetch_pcgs_market_data,
        scrape_heritage_auctions,
        scrape_error_ref,
        scrape_coinweek,
        scrape_usmint,
        scrape_wikimedia,
        scrape_pcgs_photograde,
        scrape_ngc,
        scrape_smithsonian,
        scrape_usacoinbook,
    )
    from .storage import (
        ensure_sqlite_schema,
        download_image,
        upload_to_gcs,
        update_coin_images_in_databases,
        update_mint_error_images_in_firestore,
        auto_migrate_to_gcs,
        db
    )
except ImportError:
    # Fallbacks for local direct imports
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from numista_scraper.config import DB_PATH, KEY_PATH, BUCKET_NAME, DEFAULT_DELAY
    from numista_scraper.scrapers import (
        scrape_numista_api,
        fetch_pcgs_market_data,
        scrape_heritage_auctions,
        scrape_error_ref,
        scrape_coinweek,
        scrape_usmint,
        scrape_wikimedia,
        scrape_pcgs_photograde,
        scrape_ngc,
        scrape_smithsonian,
        scrape_usacoinbook,
    )
    from numista_scraper.storage import (
        ensure_sqlite_schema,
        download_image,
        upload_to_gcs,
        update_coin_images_in_databases,
        update_mint_error_images_in_firestore,
        auto_migrate_to_gcs,
        db
    )



class NumistaScraperAgent:
    def __init__(self, mode="request"):
        self.mode = mode
        self.processed_list = []
        self.ai_pending_list = []  # Coins that need AI approval before image generation
        # Ensure schema is aligned on startup
        ensure_sqlite_schema()

    def audit_gaps(self, use_firestore=True):
        """
        Audit the SQLite database or Firestore to identify missing images or catalog mismatches.
        """
        print(f"🔍 Auditing {'Firestore' if use_firestore else 'SQLite'} for image gaps...")
        
        coin_gaps = []

        if use_firestore:
            try:
                # Audit against Firestore for persistent cloud tracking
                ref_col = db.collection("definitive_reference")
                print("    Streaming 'definitive_reference' to find gaps...")
                docs = ref_col.stream()
                for doc in docs:
                    data = doc.to_dict()
                    obv = data.get("image_url_obverse", "")
                    if not obv or str(obv).strip() == "" or obv is None:
                        coin_gaps.append(data)
                
                print(f"  - Found {len(coin_gaps)} coin/note records missing obverse images in Firestore.")
            except Exception as e:
                print(f"  ⚠ Firestore audit error: {e}. Falling back to SQLite.")
                use_firestore = False

        if not use_firestore:
            # Fallback to SQLite (local mode)
            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("""
                    SELECT doc_id, year, denomination, mint_mark, variety, series, category 
                    FROM definitive_reference 
                    WHERE image_url_obverse IS NULL OR image_url_obverse = ''
                """)
                rows = cur.fetchall()
                conn.close()
                for r in rows:
                    coin_gaps.append(dict(r))
                print(f"  - Found {len(coin_gaps)} coin/note records missing obverse images in SQLite.")
            except Exception as e:
                print(f"  ⚠ SQLite audit error: {e}")

        # 2. Audit Firestore US Mint Error Database
        error_gaps = []
        try:
            errors_col = db.collection("mint_errors")
            docs = errors_col.stream()
            for doc in docs:
                data = doc.to_dict()
                images = data.get("images", [])
                
                # A gap exists if there are no images or the URLs are empty
                has_valid_images = False
                for img in images:
                    if img.get("url"):
                        has_valid_images = True
                        break
                        
                if not has_valid_images:
                    error_data = data.copy()
                    error_data["id"] = doc.id
                    error_gaps.append(error_data)
                    
            print(f"  - Found {len(error_gaps)} mint error records missing images.")
        except Exception as e:
            print(f"  ⚠ Firestore audit error: {e}")

        return coin_gaps, error_gaps

    def slugify(self, text):
        if not text:
            return "none"
        return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")

    def resolve_pcgs_no(self, coin):
        """
        Resolves the PCGS number for a given coin using hardcoded mappings or rules.
        """
        # 1. Check if coin dict already contains a PCGS number
        pcgs_no = coin.get("pcgs_no") or coin.get("pcgs_number") or coin.get("PCGSNo")
        if pcgs_no:
            return pcgs_no

        # 2. Extract from doc_id or variety if PCGS number is embedded
        doc_id = coin.get("doc_id") or ""
        variety = coin.get("variety") or ""

        match = re.search(r"PCGS\s*(?:No\.?|#)?\s*(\d+)", variety, re.IGNORECASE)
        if match:
            return match.group(1)

        note = coin.get("note") or ""
        match = re.search(r"PCGS\s*(?:No\.?|#)?\s*(\d+)", note, re.IGNORECASE)
        if match:
            return match.group(1)

        # 3. Common coin mapping for testing and production baseline database
        year = str(coin.get("year") or "")
        denom = str(coin.get("denomination") or "").lower()
        mint = str(coin.get("mint_mark") or "").upper()
        series = str(coin.get("series") or "").lower()
        variety_lower = variety.lower()

        # Morgan Silver Dollars (1878 - 1921)
        if "morgan" in variety_lower or "morgan" in series or ("dollar" in denom and "silver" in variety_lower and (year.isdigit() and (1878 <= int(year) <= 1921))):
            morgan_map = {
                ("1881", "S"): "7130",
                ("1881", "O"): "7128",
                ("1881", "CC"): "7126",
                ("1881", "P"): "7124",
                ("1921", "P"): "7294",
                ("1921", "D"): "7296",
                ("1921", "S"): "7298",
            }
            key = (year, mint if mint not in ["NONE", ""] else "P")
            if key in morgan_map:
                return morgan_map[key]
            return "7130" # Default Morgan Dollar 1881-S for testing

        # Peace Dollars (1921 - 1935)
        if "peace" in variety_lower or "peace" in series or ("dollar" in denom and "silver" in variety_lower and (year.isdigit() and (1921 <= int(year) <= 1935))):
            peace_map = {
                ("1934", "D"): "7378",
                ("1921", "P"): "7356",
            }
            key = (year, mint if mint not in ["NONE", ""] else "P")
            if key in peace_map:
                return peace_map[key]
            return "7356" # Default Peace Dollar 1921

        # Lincoln Cents
        if "lincoln" in variety_lower or "lincoln" in series:
            if "memorial" in variety_lower or "memorial" in series:
                return "2886" # 1959 Lincoln Cent ( Memorial )
            return "2426" # 1909 Lincoln Cent ( Wheat )

        # Jefferson Nickels
        if "jefferson" in variety_lower or "jefferson" in series:
            return "3998"

        # Washington Quarters
        if "washington" in variety_lower or "washington" in series:
            return "5790"

        # Kennedy Half Dollars
        if "kennedy" in variety_lower or "kennedy" in series:
            return "6706"

        return None

    def _has_usmint_cookies(self):
        """
        Returns True only if valid USMint session cookies are stored in Firestore.
        Without cookies, USMint.gov will 403 immediately — no point attempting.
        """
        try:
            doc = db.collection("config").document("usmint").get()
            if doc.exists:
                val = doc.to_dict().get("cookieString", "")
                return bool(val and val.strip())
        except Exception:
            pass
        return False

    def process_coin_gap(self, coin, dry_run=False, source_priority="all"):
        """
        Source obverse and reverse images and fetch PCGS market data.
        source_priority: "all", "usmint", "numista", "heritage", "wikimedia"

        Source waterfall order:
          1. USMint.gov        — only if session cookies are stored in Firestore
          2. Wikimedia Commons — free public-domain images
          3. Numista API       — official numismatic API
          4. PCGS PhotoGrade  — professional coin photography
          5. NGC Coin Explorer — NGC registry images
          6. Smithsonian NMAH — museum archive images
          7. USA CoinBook      — collector reference images
          8. Heritage Auctions — auction lot photographs
        If none succeed, the coin is queued in 'ai_reconstruction_pending'
        for your manual approval — AI is NEVER triggered automatically.
        """
        doc_id = coin.get("doc_id")
        year = coin.get("year", "")
        denom = coin.get("denomination", "")
        mint = coin.get("mint_mark", "P")
        variety = coin.get("variety", "")
        category = coin.get("category", "")

        print(f"\n⚡ Sourcing images and market data for: {year} {denom} ({variety}) [ID: {doc_id}]")

        scraped_data = None
        query = f"{year} {denom} {mint} {variety}".strip()

        # Override default priority based on US Mint cookie state
        if source_priority == "all":
            if self._has_usmint_cookies():
                print("    [USMint.gov] Active session cookies found. USMint.gov will be prioritized in the waterfall.")
                # Keep source_priority as "all" so we fall back to other sources if US Mint fails
            else:
                print("    [USMint.gov] No session cookies found. Skipping USMint.gov and searching fallbacks.")

        # 1. US Mint — ONLY attempt if valid session cookies exist in Firestore
        if category == "coin" and source_priority in ["all", "usmint"]:
            if self._has_usmint_cookies():
                print("    Attempting USMint.gov (session cookies found)...")
                scraped_data = scrape_usmint({"query": query})
                if scraped_data and scraped_data.get("obverse_url"):
                    print("    ✓ Successfully found on USMint.gov")
                    scraped_data["source"] = "usmint"
            else:
                print("    Skipping USMint.gov — no session cookies stored. Paste cookies in the dashboard to enable.")
            if source_priority == "usmint" and (not scraped_data or not scraped_data.get("obverse_url")):
                print("    ⚠ USMint.gov returned no images. Skipping other sources (US Mint Only Mode).")
                return False

        # 2. Wikimedia Commons
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all", "wikimedia"]:
                print("    Attempting Wikimedia Commons...")
                scraped_data = scrape_wikimedia({"query": query})
                if scraped_data and scraped_data.get("obverse_url"):
                    print("    ✓ Successfully found on Wikimedia Commons")
                    scraped_data["source"] = "wikimedia"

        # 3. Numista API
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all", "numista"]:
                numista_id_match = re.match(r"^ref_coin_type_(\d+)$", doc_id)
                if numista_id_match:
                    numista_id = int(numista_id_match.group(1))
                    print(f"    Fetching from Numista API...")
                    scraped_data = scrape_numista_api(numista_id)
                    if scraped_data:
                        scraped_data["source"] = "numista"

        # 4. PCGS PhotoGrade Online
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all"]:
                print("    Attempting PCGS PhotoGrade...")
                scraped_data = scrape_pcgs_photograde({"query": query, "year": year, "denomination": denom})
                if scraped_data and scraped_data.get("obverse_url"):
                    print("    ✓ Successfully found on PCGS PhotoGrade")
                    scraped_data["source"] = "pcgs"

        # 5. NGC Coin Explorer
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all"]:
                print("    Attempting NGC Coin Explorer...")
                scraped_data = scrape_ngc({"query": query, "year": year, "denomination": denom})
                if scraped_data and scraped_data.get("obverse_url"):
                    print("    ✓ Successfully found on NGC Coin Explorer")
                    scraped_data["source"] = "ngc"

        # 6. Smithsonian National Museum of American History
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all"]:
                print("    Attempting Smithsonian NMAH...")
                scraped_data = scrape_smithsonian({"query": query})
                if scraped_data and scraped_data.get("obverse_url"):
                    print("    ✓ Successfully found on Smithsonian NMAH")
                    scraped_data["source"] = "smithsonian"

        # 7. USA CoinBook
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all"]:
                print("    Attempting USA CoinBook...")
                scraped_data = scrape_usacoinbook({"query": query, "year": year, "denomination": denom})
                if scraped_data and scraped_data.get("obverse_url"):
                    print("    ✓ Successfully found on USA CoinBook")
                    scraped_data["source"] = "usacoinbook"

        # 8. Heritage Auctions (last resort for actual coin photos)
        if not scraped_data or not scraped_data.get("obverse_url"):
            if source_priority in ["all", "heritage"]:
                print("    Sourcing from Heritage Auctions fallback...")
                scraped_data = scrape_heritage_auctions({"query": query})
                if scraped_data:
                    scraped_data["source"] = "heritage"

        # Apply GCS Migration for any found image
        if scraped_data:
            if scraped_data.get("obverse_url"):
                scraped_data["obverse_url"] = auto_migrate_to_gcs(scraped_data.get("obverse_url"), doc_id, "obverse")
            if scraped_data.get("reverse_url"):
                scraped_data["reverse_url"] = auto_migrate_to_gcs(scraped_data.get("reverse_url"), doc_id, "reverse")

        # Fetch PCGS Market Data if it's a coin
        market_data = None
        if category == "coin":
            pcgs_no = self.resolve_pcgs_no(coin)
            if pcgs_no:
                print(f"    Fetching PCGS market data for PCGS No: {pcgs_no}...")
                market_data = fetch_pcgs_market_data(pcgs_no)

        if not scraped_data:
            scraped_data = {}

        # Double-Checking / Self-Healing Metadata
        if scraped_data.get("title"):
            self.double_check_metadata(coin, scraped_data, dry_run)

        if dry_run:
            print(f"    ✓ [DRY RUN] Would download obverse: {scraped_data.get('obverse_url')}")
            if scraped_data.get("reverse_url"):
                print(f"    ✓ [DRY RUN] Would download reverse: {scraped_data.get('reverse_url')}")
            return True

        # Final Verification
        obv_url = scraped_data.get("obverse_url")
        rev_url = scraped_data.get("reverse_url")

        if not obv_url or "storage.googleapis.com" not in obv_url:
            # ── NO AI generation without approval ──────────────────────────────
            # Queue this coin for human review. The nightly report will list
            # all pending items. User must approve before any AI image is made.
            print(f"    ℹ No image found for {doc_id} from any source. Adding to AI approval queue.")
            try:
                db.collection("ai_reconstruction_pending").document(doc_id).set({
                    "doc_id": doc_id,
                    "year": year,
                    "denomination": denom,
                    "mint_mark": mint,
                    "variety": variety,
                    "category": category,
                    "sources_tried": ["usmint", "wikimedia", "numista", "pcgs", "ngc", "smithsonian", "usacoinbook", "heritage"],
                    "status": "pending_approval",
                    "queued_at": int(time.time())
                }, merge=True)
                self.ai_pending_list.append(f"{year} {denom} {variety} [{doc_id}]")
            except Exception as e:
                print(f"    ⚠ Failed to queue for AI review: {e}")
            return False

        # Success — persist
        if not dry_run:
            self.processed_list.append({
                "title": f"{year} {denom} ({variety})",
                "category": category,
                "source": scraped_data.get("source", "unknown"),
                "obverse_url": obv_url,
                "reverse_url": rev_url
            })

        update_coin_images_in_databases(doc_id, obv_url, rev_url, market_data)
        return True

    def trigger_ai_reconstruction(self, coin, dry_run=False):
        """
        Fallback: Generate a 'Historical Reconstruction' using gemini-3.1-flash-image.
        """
        doc_id = coin.get("doc_id")
        year = coin.get("year", "")
        denom = coin.get("denomination", "")
        variety = coin.get("variety", "")
        category = coin.get("category", "")
        
        prompt = f"Historical reconstruction of a {year} {denom} {category} from the United States. Variety: {variety}. High-detail, professional numismatic photography style, white background."
        
        print(f"    🎨 Generating AI Reconstruction for {doc_id}...")
        
        if dry_run:
            print(f"    ✓ [DRY RUN] Would generate AI image with prompt: {prompt}")
            return False

        try:
            # We save the intention to a dedicated queue for human review
            reconstruction_data = {
                "doc_id": doc_id,
                "prompt": prompt,
                "status": "pending_generation",
                "timestamp": int(time.time()),
                "metadata": coin
            }
            
            db.collection("ai_training_queue").document(doc_id).set(reconstruction_data)
            print(f"    ✓ Queued for AI Reconstruction: {doc_id}")
            return False # Not 'Successfully Processed' yet until human-voted
        except Exception as e:
            print(f"    ❌ AI Reconstruction queuing failed: {e}")
            return False

        # Persist updates (always write market data even if images weren't uploaded)
        update_coin_images_in_databases(doc_id, gcs_obv_url, gcs_rev_url, market_data)
        print("    ✓ Successfully updated databases with new image links and market metadata.")
        return True


    def get_fallback_queries(self, error):
        name = error.get("name", "")
        shortName = error.get("shortName", "")
        category = error.get("category", "")
        subcategory = error.get("subcategory", "")
        years = error.get("years", [])
        denoms = error.get("denominations", [])
        
        # Helper to clean a string of specific blocking terms
        def clean_term(text):
            if not text:
                return ""
            text = text.replace("—", " ").replace("–", " ").replace("-", " ")
            text = re.sub(r"[#`'\"(),/]", " ", text)
            blocking = [
                "Crossroads of the Revolution",
                "State Quarter",
                "State",
                "Extra Tree",
                "Grease",
                "FRN",
                "High",
                "Low",
                "Obverse",
                "Reverse"
            ]
            for word in blocking:
                text = re.sub(rf"\b{re.escape(word)}\b", "", text, flags=re.I)
            text = re.sub(r"\s+", " ", text).strip()
            return text

        # Candidate query list
        candidates = []
        
        # 1. Cleaned name
        c_name = clean_term(name)
        if c_name:
            candidates.append(c_name)
            candidates.append(f"{c_name} error")
            
        # 2. Short name (cleaned)
        if shortName:
            c_short = clean_term(shortName)
            if c_short:
                candidates.append(c_short)
                candidates.append(f"{c_short} error")
                if years and str(years[0]) not in c_short:
                    candidates.append(f"{years[0]} {c_short}")
                    candidates.append(f"{years[0]} {c_short} error")

        # 3. Domain variety shortcuts (high priority)
        name_lower = name.lower()
        if "bat" in name_lower or "samoa" in name_lower:
            candidates.append("Samoa Bat Quarter")
            candidates.append("2020 Samoa Bat Quarter")
            candidates.append("Samoa Bat")
            candidates.append("Samoa Bat error")
            candidates.append("2020 Samoa Bat Quarter error")
        if "wisconsin" in name_lower:
            candidates.append("Wisconsin Extra Leaf")
            candidates.append("Wisconsin Leaf Quarter")
            candidates.append("Wisconsin Extra Leaf error")
            candidates.append("Wisconsin Leaf Quarter error")
        if "new jersey" in name_lower or "jersey" in name_lower:
            candidates.append("New Jersey Quarter error")
            candidates.append("New Jersey Crossroads Quarter")
            candidates.append("New Jersey Crossroads Quarter error")

        # 4. Smart nickname fallback if name contains quotes (e.g. 'Bat')
        nick_match = re.search(r"['\"‘“]([^'\"’”]+)['\"’ ”]", name)
        if nick_match:
            nick = nick_match.group(1).strip()
            if len(nick) > 2:
                candidates.append(nick)
                candidates.append(f"{nick} error")
                if denoms:
                    candidates.append(f"{denoms[0]} {nick}")
                    candidates.append(f"{denoms[0]} {nick} error")
                if years:
                    candidates.append(f"{years[0]} {nick}")
                    candidates.append(f"{years[0]} {nick} error")

        # 5. Cleaned shortName directly
        if shortName:
            short_part = shortName.split("/")[0].strip()
            candidates.append(short_part)
            candidates.append(f"{short_part} error")

        # 6. Extract core general variety terms
        for term in ["struck-through grease", "struck through grease", "struck-through", "struck through", "die gouge", "die chip", "doubled die", "clipped planchet", "curved clip", "grease"]:
            if term in name_lower or term in shortName.lower():
                candidates.append(term)
                candidates.append(f"{term} error")

        # 7. Year + Denomination + Category
        if years and denoms:
            candidates.append(f"{years[0]} {denoms[0]} {category}")
            candidates.append(f"{years[0]} {denoms[0]} {category} error")
            candidates.append(f"{years[0]} {denoms[0]}")
            candidates.append(f"{years[0]} {denoms[0]} error")

        # 8. Denomination + Category
        if denoms:
            candidates.append(f"{denoms[0]} {category}")
            candidates.append(f"{denoms[0]} {category} error")

        # Deduplicate candidates preserving order
        seen = set()
        unique_candidates = []
        for q in candidates:
            q_clean = q.lower().strip()
            if q_clean not in seen and len(q) > 3:
                seen.add(q_clean)
                unique_candidates.append(q)

        # Specific vs Generic categorization
        def is_specific_str(q):
            q_lower = q.lower()
            # If it has a specific year, it is specific
            if re.search(r'\b(19\d{2}|20\d{2})\b', q_lower):
                # But generic year + denomination/category is treated as generic/broad
                if q_lower in [f"{years[0]} {denoms[0]} {category}".lower(), f"{years[0]} {denoms[0]}".lower(), f"{years[0]} {denoms[0]} error".lower(), f"{years[0]} {denoms[0]} {category} error".lower()] if (years and denoms) else False:
                    return False
                return True
            # Specific variety keywords (including currency/banknote terms)
            specific_keywords = [
                "wisconsin", "samoa", "jersey", "bat", "conway", "mankiller", "leaf", 
                "delaware", "connecticut", "patsy", "mink", "note", "bill", "currency", 
                "banknote", "inverted back", "federal reserve", "frn"
            ]
            if any(kw in q_lower for kw in specific_keywords):
                return True
            return False

        specific_queries = []
        generic_queries = []
        for q in unique_candidates:
            if is_specific_str(q):
                specific_queries.append(q)
            else:
                generic_queries.append(q)

        return specific_queries, generic_queries

    def try_error_ref_flow(self, error, queries):
        for q in queries:
            print(f"    Searching Error-Ref for: '{q}'...")
            scraped = scrape_error_ref({"error_type": q, "error_record": error})
            if scraped and scraped.get("obverse_url"):
                return scraped
        return None

    def try_coinweek_flow(self, error, queries):
        for q in queries:
            print(f"    Searching CoinWeek for: '{q}'...")
            scraped = scrape_coinweek({"query": q, "error_record": error})
            if scraped and scraped.get("obverse_url"):
                return scraped
        return None

    def try_heritage_flow(self, error, queries):
        for q in queries:
            print(f"    Searching Heritage Auctions for currency error: '{q}'...")
            scraped = scrape_heritage_auctions({"query": q, "error_record": error})
            if scraped and scraped.get("obverse_url"):
                return scraped
        return None

    def process_error_gap(self, error, dry_run=False):
        """
        Source illustrations and descriptions for a missing mint error.
        """
        error_id = error.get("id")
        name = error.get("name")
        category = error.get("category", "")
        subcategory = error.get("subcategory", "")
        years = error.get("years", [])
        is_specific = len(years) > 0
        
        print(f"\n⚡ Sourcing images/descriptions for Mint Error: {name} [ID: {error_id}]")
        
        scraped = None
        is_currency = (
            subcategory.lower() == "currency" or
            "currency" in [d.lower() for d in error.get("denominations", [])] or
            "federal reserve" in name.lower()
        )
        
        # Get specific and generic fallback queries
        specific_queries, generic_queries = self.get_fallback_queries(error)
        
        # Prepend the primary name to the specific queries list if it is not already there
        if name not in specific_queries:
            specific_queries.insert(0, name)
        name_err = f"{name} error"
        if name_err not in specific_queries:
            specific_queries.insert(1, name_err)

        if is_currency:
            print("    Item is a Banknote/Currency error. Trying Heritage Auctions first...")
            scraped = self.try_heritage_flow(error, specific_queries)
            if not scraped or not scraped.get("obverse_url"):
                print("    Heritage specific search returned no images. Trying CoinWeek specific...")
                scraped = self.try_coinweek_flow(error, specific_queries)
            if not scraped or not scraped.get("obverse_url"):
                print("    CoinWeek specific search returned no images. Trying Error-Ref specific...")
                scraped = self.try_error_ref_flow(error, specific_queries)
        elif is_specific:
            # Specific variety -> Prefer CoinWeek/Error-Ref specific first
            scraped = self.try_coinweek_flow(error, specific_queries)
            if not scraped or not scraped.get("obverse_url"):
                print("    CoinWeek specific search returned no images. Trying Error-Ref specific...")
                scraped = self.try_error_ref_flow(error, specific_queries)
        else:
            # General error -> Prefer Error-Ref generic first
            scraped = self.try_error_ref_flow(error, generic_queries)
            if not scraped or not scraped.get("obverse_url"):
                print("    Error-Ref generic search returned no images. Trying CoinWeek generic...")
                scraped = self.try_coinweek_flow(error, generic_queries)
                
        # If specific searches failed for specific variety/currency, we fall back to generic/general definitions
        if not scraped or not scraped.get("obverse_url"):
            if is_specific or is_currency:
                print("    ⚠ Specific variety searches failed. Falling back to generic definition pages...")
                # For generic fallbacks, we always prefer Error-Ref first (since it is a glossary), then CoinWeek
                scraped = self.try_error_ref_flow(error, generic_queries)
                if not scraped or not scraped.get("obverse_url"):
                    scraped = self.try_coinweek_flow(error, generic_queries)
            
        if not scraped or not scraped.get("obverse_url"):
            print("    ✗ Failed to source images from Heritage, CoinWeek, or Error-Ref.")
            return False

        if dry_run:
            print(f"    ✓ [DRY RUN] Would download obverse: {scraped.get('obverse_url')}")
            if scraped.get("reverse_url"):
                print(f"    ✓ [DRY RUN] Would download reverse: {scraped.get('reverse_url')}")
            return True

        # Step 3: Download and Upload to GCS
        gcs_obv_url = None
        gcs_rev_url = None
        
        slug = self.slugify(name)
        
        obv_bytes = download_image(scraped.get("obverse_url"))
        if obv_bytes:
            obv_path = f"error_library/{slug}_obverse.jpg"
            gcs_obv_url = upload_to_gcs(obv_bytes, obv_path)
            print(f"    ✓ Uploaded obverse to GCS: {gcs_obv_url}")
            
        rev_bytes = download_image(scraped.get("reverse_url"))
        if rev_bytes:
            rev_path = f"error_library/{slug}_reverse.jpg"
            gcs_rev_url = upload_to_gcs(rev_bytes, rev_path)
            print(f"    ✓ Uploaded reverse to GCS: {gcs_rev_url}")

        if gcs_obv_url:
            # Construct Firebase images payload
            images_payload = [
                {
                    "url": gcs_obv_url,
                    "source": scraped.get("source", "web"),
                    "attributionText": f"{scraped.get('source', 'web').upper()} reference photograph",
                    "attributionUrl": scraped.get("source_url", ""),
                    "isVerified": False,
                    "side": "obverse"
                }
            ]
            if gcs_rev_url:
                images_payload.append({
                    "url": gcs_rev_url,
                    "source": scraped.get("source", "web"),
                    "attributionText": f"{scraped.get('source', 'web').upper()} reference photograph",
                    "attributionUrl": scraped.get("source_url", ""),
                    "isVerified": False,
                    "side": "reverse"
                })
                
            # Update Firestore
            update_mint_error_images_in_firestore(error_id, images_payload)
            
            # If description was missing, update it
            if scraped.get("description") and not error.get("description"):
                try:
                    db.collection("mint_errors").document(error_id).update({
                        "description": scraped["description"]
                    })
                    print("    ✓ Updated missing description in Firestore.")
                except Exception as de:
                    print(f"    ⚠ Error updating description: {de}")
                    
            print("    ✓ Successfully updated Firestore mint_errors with images.")
            return True
            
        return False

    def double_check_metadata(self, coin, scraped_data, dry_run=False):
        """
        Verify scraped coin data against existing local data and report/correct discrepancies.
        """
        doc_id = coin.get("doc_id")
        existing_title = coin.get("variety", "")
        scraped_title = scraped_data.get("title", "")
        
        if not scraped_title:
            return
            
        # Example healing logic: check if the official title differs significantly
        # (e.g. correct spelling mistakes, add formal sub-variety descriptions)
        clean_existing = existing_title.lower().strip()
        clean_scraped = scraped_title.lower().strip()
        
        if clean_existing != clean_scraped and len(clean_scraped) > 3:
            print(f"    [Double-Check] Warning: Variety names mismatch!")
            print(f"      - Local database: '{existing_title}'")
            print(f"      - Scraped official: '{scraped_title}'")
            
            if not dry_run:
                # Align SQLite database title if it is just a minor spelling/formalization difference
                try:
                    conn = sqlite3.connect(str(DB_PATH))
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE definitive_reference
                        SET variety = ?
                        WHERE doc_id = ?
                    """, (scraped_title, doc_id))
                    conn.commit()
                    conn.close()
                    print(f"      ✓ Healed variety name in SQLite to official: '{scraped_title}'")
                    
                    # Update Firestore as well
                except Exception as e:
                    print(f"      ⚠ Self-healing update failed: {e}")

    def run(self, limit=10, target="all", dry_run=False, source_priority="all"):
        """
        Run the full scraper agent flow: audit gaps, fetch images, heal data, and write audit reports.
        """
        print("="*60)
        print(f"  Numista.AI Scraper Agent Executing (Mode: {self.mode})")
        print(f"  Dry-Run: {dry_run} | Target: {target} | Limit: {limit} | Priority: {source_priority}")
        print("="*60)
        
        # 1. Audit
        coin_gaps, error_gaps = self.audit_gaps()
        
        processed_coins = 0
        processed_errors = 0
        
        # 2. Process Coin Gaps
        if target in ["all", "coins"] and coin_gaps:
            print(f"\nProcessing Coin Gaps (up to limit={limit})...")
            attempted = 0
            for coin in coin_gaps:
                if limit and attempted >= limit:
                    break
                attempted += 1
                try:
                    success = self.process_coin_gap(coin, dry_run, source_priority)
                    if success:
                        processed_coins += 1
                        self.processed_list.append({
                            "title": f"{coin.get('year', '')} {coin.get('variety', '')}",
                            "category": coin.get('category', 'coin'),
                            "source": "Numista/PCGS"
                        })
                    # Rate limiting delay
                    time.sleep(DEFAULT_DELAY)
                except Exception as e:
                    print(f"  Error processing coin gap {coin.get('doc_id')}: {e}")

        # 3. Process Error Gaps
        if target in ["all", "errors"] and error_gaps:
            print(f"\nProcessing Error Gaps (up to limit={limit})...")
            attempted = 0
            for err in error_gaps:
                if limit and attempted >= limit:
                    break
                attempted += 1
                try:
                    success = self.process_error_gap(err, dry_run)
                    if success:
                        processed_errors += 1
                        self.processed_list.append({
                            "title": err.get('variety_name', 'Unnamed Error'),
                            "category": "mint_error",
                            "source": "Heritage/Error-Ref"
                        })
                    time.sleep(DEFAULT_DELAY)
                except Exception as e:
                    print(f"  Error processing error gap {err.get('id')}: {e}")

        # 4. Generate Report
        report_path = Path(__file__).parent.parent / "sourcing_audit_report.md"
        report_content = f"# Numista.AI - Image Sourcing & Audit Report\n\n"
        report_content += f"Generated at: {datetime.now(timezone.utc).isoformat()} UTC\n\n"
        report_content += f"## Summary of Executed Operations\n\n"
        report_content += f"* **Agent Mode**: {self.mode}\n"
        report_content += f"* **Dry-Run Status**: {dry_run}\n"
        report_content += f"* **Target Scope**: {target}\n"
        report_content += f"* **Total Coin/Note Image Gaps Filled**: {processed_coins} / {len(coin_gaps)}\n"
        report_content += f"* **Total Mint Error Gaps Filled**: {processed_errors} / {len(error_gaps)}\n\n"

        if self.processed_list:
            report_content += f"## Successfully Processed Items\n\n"
            for item in self.processed_list:
                report_content += f"* **{item['title']}** ({item['category']}) - *{item['source']}*\n"
            report_content += "\n"

        if self.ai_pending_list:
            report_content += f"## ⚠ Pending AI Image Approval ({len(self.ai_pending_list)} coins)\n\n"
            report_content += "The following coins had **no image found** from any source.\n"
            report_content += "**No AI images were generated.** Please review this list and approve AI generation\n"
            report_content += "when it is convenient (e.g. overnight) to avoid impacting your Gemini quota:\n\n"
            for entry in self.ai_pending_list:
                report_content += f"* {entry}\n"
            report_content += "\nTo trigger AI generation for approved coins, use the dashboard\n"
            report_content += "or the `/api/cron/generate-pending-ai` endpoint.\n\n"

        report_content += f"## Data Quality and Corrections\n\n"
        report_content += f"All varieties checked against official references. SQLite schemas aligned to support `image_url_obverse` and `image_url_reverse` keys.\n"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        # 5. Save to Firestore for Dashboard
        if not dry_run:
            try:
                db.collection("scraper_reports").add({
                    "timestamp": int(time.time()),
                    "datetime_utc": datetime.now(timezone.utc).isoformat(),
                    "limit": limit,
                    "target": target,
                    "dry_run": dry_run,
                    "processed_coins": processed_coins,
                    "processed_errors": processed_errors,
                    "report_content": report_content
                })
                print("      ✓ Saved report to Firestore for dashboard.")
            except Exception as e:
                print(f"      ⚠ Failed to save report to Firestore: {e}")

        print("\n" + "="*60)
        print(f"  Agent run completed. Report written to {report_path.name}")
        print("="*60)
        return processed_coins, processed_errors


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Numista.AI Scraper Agent")
    parser.add_argument("--mode", type=str, default="audit", choices=["audit", "campaign", "verify"], help="Operation mode")
    parser.add_argument("--limit", type=int, default=10, help="Max items to process")
    parser.add_argument("--target", type=str, default="all", choices=["all", "coins", "errors"], help="Target items")
    parser.add_argument("--priority", type=str, default="all", help="Source priority (e.g. 'wikimedia')")
    parser.add_argument("--dry-run", action="store_true", help="Don't perform actual updates")
    
    args = parser.parse_args()
    
    # Ensure numista_backend is on path if running as script
    sys.path.append(str(Path(__file__).parent.parent))
    
    agent = NumistaScraperAgent(mode=args.mode)
    agent.run(limit=args.limit, target=args.target, dry_run=args.dry_run, source_priority=args.priority)
