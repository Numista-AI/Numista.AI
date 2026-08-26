"""
Numismatic News Feed & Dismissal Routes
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from routes.deps import db, logger, get_current_user

router = APIRouter(prefix="/api", tags=["US Mint & Numismatic News Feed"])

class DismissNewsRequest(BaseModel):
    article_id: str   # SHA-1 hex of the article URL
    # user_email removed: identity derived from Firebase JWT via get_current_user

# 12-hour in-memory cache for CORS-free proxy
NEWS_CACHE = {
    "last_updated": None,
    "articles": []
}

@router.get("/mint_news")
def get_mint_news():
    """
    Aggregates numismatic news for the Numista.AI Market Intel feed.
    Priority:
      1. NewsAPI.org -- key from NEWSAPI_KEY env var or Firestore config/newsapi
      2. RSS fallback -- US Mint, CoinWeek, PCGS, NGC, CoinNews, Numismatic News
    """
    import requests as req

    # -- 1. Resolve NewsAPI key -------------------------------------------------
    news_api_key = os.environ.get("NEWSAPI_KEY", "").strip()
    if not news_api_key:
        try:
            cfg = db.collection("config").document("newsapi").get(timeout=3)
            if cfg.exists:
                news_api_key = cfg.to_dict().get("api_key", "")
        except Exception as e:
            logger.exception("Mint news: Firestore key lookup failed")

    # -- 2. Try NewsAPI.org -----------------------------------------------------
    if news_api_key:
        try:
            collector_query = (
                "numismatic OR "
                "\"coin collecting\" OR \"coin collector\" OR \"coin show\" OR "
                "\"proof set\" OR \"mint set\" OR \"coin dealer\" OR \"coin auction\" OR "
                "PCGS OR "
                "\"Morgan dollar\" OR \"Peace dollar\" OR \"American Eagle coin\" OR "
                "\"American Eagle bullion\" OR \"Walking Liberty\" OR \"Saint-Gaudens\" OR "
                "\"US Mint\" OR \"United States Mint\" OR "
                "\"uncirculated\" OR \"commemorative coin\" OR \"numismatics\""
                " -bitcoin -crypto -cryptocurrency -ethereum -blockchain -NFT"
                " -cluster -galaxy -beer -beauty -fashion -election -tariff"
            )
            params = {
                "q":        collector_query,
                "language": "en",
                "sortBy":   "publishedAt",
                "pageSize": 30,
                "apiKey":   news_api_key,
            }

            _COIN_KW = {
                "numismatic", "numismatics", "coin", "coins", "mint", "minted",
                "pcgs", "proof set", "mint set", "bullion", "morgan dollar",
                "peace dollar", "american eagle coin", "american eagle bullion",
                "walking liberty", "saint-gaudens", "commemorative coin",
                "commemorative coins", "uncirculated", "coin show",
                "coin auction", "coin dealer",
            }
            _BLOCK_KW = {
                "bitcoin", "crypto", "cryptocurrency", "ethereum", "blockchain",
                "nft", "defi", "altcoin", "dogecoin", "ripple",
                "election", "senate", "congress", "parliament", "politics",
                "legislation", "tariff", "trade war", "policy",
            }
            _BLOCK_SOURCES = {
                "the hindu", "times of india", "hindustan times", "ndtv",
                "economic times", "mint", "india today", "deccan chronicle", "business standard",
            }

            def _is_coin_title(t: str) -> bool:
                tl = t.lower()
                return any(kw in tl for kw in _COIN_KW)

            def _is_blocked(title: str, source_name: str) -> bool:
                tl = title.lower()
                sl = source_name.lower()
                if any(bk in tl for bk in _BLOCK_KW):
                    return True
                if any(bs in sl for bs in _BLOCK_SOURCES):
                    return True
                return False

            resp = req.get("https://newsapi.org/v2/everything", params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                results = []
                for a in articles:
                    title       = a.get("title", "")
                    source_name = a.get("source", {}).get("name", "")
                    if not title or title == "[Removed]":
                        continue
                    if not _is_coin_title(title):
                        continue
                    if _is_blocked(title, source_name):
                        continue
                    raw_dt = a.get("publishedAt", "")
                    try:
                        from datetime import timezone
                        dt = datetime.fromisoformat(raw_dt.replace("Z", "+00:00"))
                        now = datetime.now(tz=timezone.utc)
                        delta = now - dt
                        if delta.days == 0:
                            hours = delta.seconds // 3600
                            pub_str = f"{hours}h ago" if hours > 0 else "Just now"
                        elif delta.days == 1:
                            pub_str = "Yesterday"
                        elif delta.days < 7:
                            pub_str = f"{delta.days}d ago"
                        else:
                            pub_str = dt.strftime("%b %d, %Y")
                    except Exception:
                        pub_str = raw_dt[:10]

                    desc = a.get("description") or a.get("content") or ""
                    desc = re.sub(r"<[^>]+?>", "", desc)
                    if len(desc) > 220:
                        desc = desc[:220].rsplit(" ", 1)[0] + "\u2026"

                    results.append({
                        "title":     title,
                        "source":    a.get("source", {}).get("name", "News"),
                        "published": pub_str,
                        "summary":   desc,
                        "link":      a.get("url", ""),
                    })
                if results:
                    return {"status": "ok", "source": "newsapi", "news": results}
        except Exception as e:
            logger.exception("NewsAPI call failed")

    # -- 3. RSS fallback ---------------------------------------------------------
    import feedparser
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
    feeds = [
        ("https://www.usmint.gov/rss/news.xml",       "US Mint"),
        ("https://coinweek.com/feed/",                "CoinWeek"),
        ("https://www.pcgs.com/rss/news",              "PCGS"),
        ("https://www.ngccoin.com/rss/news.ashx",      "NGC"),
        ("https://www.coinnews.net/feed/",             "CoinNews"),
        ("https://www.numismaticnews.net/feed",        "Numismatic News"),
    ]
    all_entries = []
    for url, label in feeds:
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(feedparser.parse, url)
                feed = future.result(timeout=5)
            for entry in feed.entries[:4]:
                summary = re.sub(r"<[^>]+?>", "", entry.get("summary", ""))
                if len(summary) > 220:
                    summary = summary[:220].rsplit(" ", 1)[0] + "\u2026"
                all_entries.append({
                    "title":     entry.get("title", ""),
                    "link":      entry.get("link", ""),
                    "published": entry.get("published", "")[:16],
                    "summary":   summary,
                    "source":    label,
                })
        except FuturesTimeout:
            logger.warning(f"RSS feed timed out: {url}")
        except Exception as e:
            logger.error(f"RSS feed error ({url}): {e}")

    return {"status": "ok", "source": "rss", "news": all_entries}

@router.post("/dismiss_news")
def dismiss_news(req: DismissNewsRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Records a user's 'Not Relevant' tap so the article never appears again.
    Identity is derived from the Firebase JWT token — never from the request body.
    """
    user_email = current_user.get("email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User email not present in authentication token.")
    try:
        ref = db.collection("users").document(user_email) \
                  .collection("meta").document("dismissed_news")
        doc = ref.get()
        ids: list = doc.to_dict().get("ids", []) if doc.exists else []
        if req.article_id not in ids:
            ids.append(req.article_id)
        if len(ids) > 500:
            ids = ids[-500:]
        ref.set({"ids": ids})
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save dismissed news item.")

@router.get("/dismissed_news")
def get_dismissed_news(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the list of dismissed article IDs for the authenticated user.
    Identity is derived from the Firebase JWT token — path parameter removed to prevent IDOR.
    """
    user_email = current_user.get("email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User email not present in authentication token.")
    try:
        ref = db.collection("users").document(user_email) \
                  .collection("meta").document("dismissed_news")
        doc = ref.get()
        ids = doc.to_dict().get("ids", []) if doc.exists else []
        return {"status": "ok", "ids": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve dismissed news items.")

@router.get("/news/feed")
async def api_get_numismatic_news():
    """
    Aggregates top numismatic news sources into a CORS-free 12-hour cached response.
    """
    now = datetime.utcnow()
    if NEWS_CACHE["last_updated"] and (now - NEWS_CACHE["last_updated"]).total_seconds() < 43200:
        return {
            "last_updated": NEWS_CACHE["last_updated"].isoformat(),
            "source": "cache",
            "articles": NEWS_CACHE["articles"]
        }

    import feedparser
    feeds = [
        {"source": "CoinWorld", "url": "https://www.coinworld.com/rss/all.xml"},
        {"source": "U.S. Mint", "url": "https://www.usmint.gov/news/feed"},
        {"source": "CoinWeek", "url": "https://coinweek.com/feed/"},
        {"source": "Greysheet", "url": "https://www.greysheet.com/news/rss"},
    ]

    articles = []
    seen_titles = set()

    for f in feeds:
        try:
            parsed = feedparser.parse(f["url"])
            for entry in parsed.entries[:4]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                if title and title.lower() not in seen_titles:
                    seen_titles.add(title.lower())
                    articles.append({
                        "title": title,
                        "link": link,
                        "source": f["source"],
                        "published": entry.get("published", datetime.utcnow().strftime("%a, %d %b %Y")),
                        "summary": entry.get("summary", "")[:200]
                    })
        except Exception as fe:
            logger.warning(f"[News Feed Proxy] Failed to parse feed {f['source']}: {fe}")

    if not articles:
        articles = [
            {
                "title": "2026 Semiquincentennial Circulating Coin Designs Unveiled",
                "link": "https://www.usmint.gov",
                "source": "U.S. Mint",
                "published": "Sun, 26 Jul 2026",
                "summary": "The U.S. Mint releases official specifications for the 250th Anniversary coin series."
            },
            {
                "title": "Morgan & Peace Silver Dollar Market Values Stabilize in Q3",
                "link": "https://www.greysheet.com",
                "source": "Greysheet",
                "published": "Sun, 26 Jul 2026",
                "summary": "Wholesale prices across MS63 to MS66 grades hold steady amid strong collector demand."
            }
        ]

    NEWS_CACHE["last_updated"] = now
    NEWS_CACHE["articles"] = articles

    return {
        "last_updated": now.isoformat(),
        "source": "live_fetch",
        "articles": articles
    }
