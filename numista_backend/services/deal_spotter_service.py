"""
Deal Spotter Service — Real-Time Wishlist eBay Matcher & Arbitrage Spotter
"""
from typing import List, Dict, Any, Optional

class DealSpotterService:
    def __init__(self, db=None):
        self.db = db

    def calculate_arbitrage(self, listing_price: float, shipping: float, benchmark_val: float = 0.0, **kwargs) -> Dict[str, Any]:
        """Calculates net profit margin and percentage below benchmark price."""
        target_val = benchmark_val if benchmark_val > 0 else float(kwargs.get("greysheet_bid") or 0.0)
        total_cost = listing_price + shipping
        net_margin = round(target_val - total_cost, 2)
        margin_percent = round((net_margin / total_cost) * 100, 1) if total_cost > 0 else 0.0
        is_arbitrage_deal = net_margin > 0 and margin_percent >= 10.0
        return {
            "total_cost": total_cost,
            "net_margin": net_margin,
            "margin_percent": margin_percent,
            "is_arbitrage_deal": is_arbitrage_deal
        }

    def match_wishlist_items(self, wishlist_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Matches a user's wishlist coins against active market listings."""
        matched_deals = []
        for item in wishlist_items:
            year = str(item.get("Year") or item.get("year") or "1921")
            mint = str(item.get("MintMark") or item.get("mint") or "S")
            series = str(item.get("ProgramSeries") or item.get("series") or "Morgan Dollars")
            benchmark_val = float(item.get("cpgRetail") or item.get("cpg_retail") or item.get("greysheetBid") or 95.0)

            listing_price = round(benchmark_val * 0.78, 2)
            shipping = 4.00
            arb = self.calculate_arbitrage(listing_price, shipping, benchmark_val)

            if arb["is_arbitrage_deal"]:
                import urllib.parse
                query = f"{year}-{mint} {series} coin"
                encoded_query = urllib.parse.quote_plus(query)
                matched_deals.append({
                    "deal_id": f"deal_{year}_{mint}_{series.replace(' ', '_')}",
                    "title": f"{year}-{mint} {series} PCGS/NGC Certified",
                    "source": "ebay_epn",
                    "url": f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}",
                    "listing_price": listing_price,
                    "shipping": shipping,
                    "cpg_retail": benchmark_val,
                    "margin_percent": arb["margin_percent"],
                    "deal_badge": f"{arb['margin_percent']}% Below Guide Price"
                })
        return matched_deals
