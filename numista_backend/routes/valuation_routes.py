"""
Spot Price, Precious Metal Melt Value, and Valuation History Routes
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import yfinance as yf
from routes.deps import db, logger

router = APIRouter(prefix="/api", tags=["Live Metal Spot Prices & Portfolio Valuation"])

@router.get("/spot_prices")
def get_live_metal_prices():
    """
    Returns live metal spot prices with a 15-minute Firestore TTL cache.
    Prevents yfinance rate-limiting bottlenecks across container recycles.
    """
    now = time.time()
    cache_ttl = 900  # 15 minutes
    
    try:
        cache_ref = db.collection("config").document("spot_prices")
        cache_doc = cache_ref.get()
        if cache_doc.exists:
            cache_data = cache_doc.to_dict() or {}
            last_updated = cache_data.get("updated_at", 0)
            if (now - last_updated) < cache_ttl and "prices" in cache_data:
                return cache_data["prices"]
    except Exception as ce:
        logger.warning(f"Failed to read spot price cache from Firestore: {ce}")

    try:
        gold = yf.Ticker("GC=F").fast_info.last_price
        silver = yf.Ticker("SI=F").fast_info.last_price
        plat = yf.Ticker("PL=F").fast_info.last_price
        pall = yf.Ticker("PA=F").fast_info.last_price
        
        prices = {
            "Gold": float(gold) if gold else 3100.0,
            "Silver": float(silver) if silver else 35.0,
            "Platinum": float(plat) if plat else 1000.0,
            "Palladium": float(pall) if pall else 1000.0
        }
        
        try:
            db.collection("config").document("spot_prices").set({
                "prices": prices,
                "updated_at": now
            })
        except Exception as se:
            logger.warning(f"Failed to save spot price cache to Firestore: {se}")

        return prices
    except Exception as e:
        logger.exception("Error fetching fresh metal prices from yfinance")
        try:
            cache_doc = db.collection("config").document("spot_prices").get()
            if cache_doc.exists and "prices" in cache_doc.to_dict():
                return cache_doc.to_dict()["prices"]
        except Exception:
            pass
        return {"Gold": 3100.0, "Silver": 35.0, "Platinum": 1000.0, "Palladium": 1000.0}
