#!/usr/bin/env python3
"""
run_agent.py
------------
CLI entrypoint to run the Numista.AI Web Scraper Agent.
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Setup module path
sys.path.append(str(Path(__file__).parent.parent))


try:
    from numista_scraper.agent import NumistaScraperAgent
except ImportError:
    from agent import NumistaScraperAgent

def main():
    parser = argparse.ArgumentParser(description="Numista.AI Web Scraper Agent CLI Runner")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Perform searches and parse pages without saving to databases or GCS."
    )
    parser.add_argument(
        "--mode", 
        choices=["request", "browser"], 
        default="request", 
        help="Execution mode: request (spoofed HTTP, lightweight) or browser (real headless Chrome)."
    )
    parser.add_argument(
        "--target", 
        choices=["all", "coins", "errors"], 
        default="all", 
        help="What database targets to scrape: all, coins (US Numismatic), or errors (US Mint Errors)."
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=None, 
        help="Limit the number of records processed to avoid hitting rate limits or bans."
    )
    
    args = parser.parse_args()
    
    agent = NumistaScraperAgent(mode=args.mode)
    agent.run(target=args.target, limit=args.limit, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
