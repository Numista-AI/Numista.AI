import os
import sqlite3
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger("proactive_scraper")
logging.basicConfig(level=logging.INFO)

DB_PATH = os.getenv("NUMISTA_DB_PATH", "numista_coins.db")

def init_staging_table(conn: sqlite3.Connection):
    """Ensure scraped_price_staging table exists for failure isolation."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraped_price_staging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_title TEXT NOT NULL,
            year TEXT,
            mint_mark TEXT,
            scraped_price REAL NOT NULL,
            source_url TEXT,
            confidence_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
            outlier_flag INTEGER DEFAULT 0,
            scraped_at TEXT NOT NULL
        )
    """)
    conn.commit()

def stage_scraped_price(
    conn: sqlite3.Connection,
    title: str,
    year: str,
    mint_mark: str,
    price: float,
    source_url: str = "",
    master_estimate: float = 0.0
) -> Dict[str, Any]:
    """
    Validates scraped auction result and writes to scraped_price_staging.
    Flags price outliers (e.g. price > 3x or < 0.25x master estimate).
    """
    cursor = conn.cursor()
    scraped_at = datetime.utcnow().isoformat()
    outlier_flag = 0

    if master_estimate > 0:
        ratio = price / master_estimate
        if ratio > 3.0 or ratio < 0.25:
            outlier_flag = 1
            logger.warning(f"Outlier price detected for {year}-{mint_mark} {title}: Scraped ${price:.2f} vs Master ${master_estimate:.2f}")

    confidence = 0.95 if outlier_flag == 0 else 0.40

    cursor.execute("""
        INSERT INTO scraped_price_staging
        (coin_title, year, mint_mark, scraped_price, source_url, confidence_score, status, outlier_flag, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, year, mint_mark, price, source_url, confidence, "PENDING", outlier_flag, scraped_at))

    conn.commit()
    staging_id = cursor.lastrowid

    return {
        "staging_id": staging_id,
        "title": title,
        "scraped_price": price,
        "outlier_flag": bool(outlier_flag),
        "status": "PENDING"
    }

def run_dry_run_scraper_demo():
    """Runs a dry-run test of the proactive scraper pipeline."""
    conn = sqlite3.connect(DB_PATH)
    init_staging_table(conn)

    sample_items = [
        {"title": "Morgan Silver Dollar", "year": "1893", "mint": "S", "price": 4500.00, "master": 4200.00},
        {"title": "Lincoln Cent", "year": "1909", "mint": "S VDB", "price": 1250.00, "master": 1100.00},
        {"title": "Washington Quarter", "year": "1932", "mint": "D", "price": 9500.00, "master": 450.00}, # Outlier test
    ]

    results = []
    for item in sample_items:
        res = stage_scraped_price(
            conn, item["title"], item["year"], item["mint"], item["price"],
            source_url="https://auction-example.numista.ai/item/123",
            master_estimate=item["master"]
        )
        results.append(res)

    conn.close()
    logger.info(f"Staged {len(results)} scraped prices into scraped_price_staging successfully.")
    return results

if __name__ == "__main__":
    run_dry_run_scraper_demo()
