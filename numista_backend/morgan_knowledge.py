"""
morgan_knowledge.py
===================
RAG (Retrieval-Augmented Generation) lookup module for Morgan.

Given a user query, searches the Firestore `coins_reference` collection
for relevant coin entries and returns structured context that is injected
into Morgan's prompt before calling Gemini.

Usage (from main.py):
    from morgan_knowledge import get_coin_context
    context_block = get_coin_context(db, query)
    # inject context_block into the deep_dive prompt
"""

import re
from typing import Optional
from google.cloud import firestore

# ─── CONFIG ───────────────────────────────────────────────────────────────────
COLLECTION       = "coins_reference"
MAX_RESULTS      = 5     # max coin entries to inject per query
MIN_SCORE        = 2     # minimum keyword match score to include

# ─── KEYWORD EXTRACTION ───────────────────────────────────────────────────────

# Common words to ignore when matching
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "what", "which", "who",
    "how", "when", "where", "why", "my", "your", "his", "her", "their",
    "its", "our", "this", "that", "these", "those", "coin", "coins",
    "about", "tell", "me", "us", "know", "like", "just", "get", "got",
    "need", "want", "please", "thanks", "and", "or", "but", "not",
    "with", "for", "from", "on", "in", "at", "to", "of", "by", "up",
}

# Keyword → series/type hints for better retrieval
SERIES_HINTS = {
    # State quarters
    "state quarter":       "50 State Quarters",
    "state quarters":      "50 State Quarters",
    "50 state":            "50 State Quarters",
    "delaware":            "50 State Quarters",
    "pennsylvania":        "50 State Quarters",
    # Morgan dollar
    "morgan":              "Morgan Silver Dollar",
    "morgan dollar":       "Morgan Silver Dollar",
    # Peace dollar
    "peace dollar":        "Peace Dollar",
    # Lincoln cent
    "lincoln":             "Lincoln Cent",
    "wheat cent":          "Lincoln Wheat Cent",
    "wheat penny":         "Lincoln Wheat Cent",
    "penny":               "Lincoln Cent",
    "cent":                "Lincoln Cent",
    # Buffalo nickel
    "buffalo":             "Buffalo Nickel",
    "buffalo nickel":      "Buffalo Nickel",
    "indian head nickel":  "Buffalo Nickel",
    # Jefferson nickel
    "jefferson":           "Jefferson Nickel",
    # Mercury dime
    "mercury":             "Mercury Dime",
    "mercury dime":        "Mercury Dime",
    # Roosevelt dime
    "roosevelt":           "Roosevelt Dime",
    # Kennedy half
    "kennedy":             "Kennedy Half Dollar",
    "half dollar":         "Kennedy Half Dollar",
    # Walking Liberty
    "walking liberty":     "Walking Liberty Half Dollar",
    # Fugio
    "fugio":               "Early American & Colonial Coppers",
    # Bicentennial
    "bicentennial":        "Bicentennial",
    "1776":                "Bicentennial",
    # Eisenhower
    "ike":                 "Eisenhower Dollar",
    "eisenhower":          "Eisenhower Dollar",
    # American Eagle
    "american eagle":      "American Gold Eagle",
    "silver eagle":        "American Silver Eagle",
    # Commemorative
    "commemorative":       "Commemorative",
    # Error coins
    "error":               "error",
    "doubled die":         "Doubled Die",
    "double die":          "Doubled Die",
    "ddo":                 "Doubled Die Obverse",
    "off center":          "Off-Center",
    "broadstrike":         "Broadstrike",
    "clipped":             "Clipped Planchet",
}


def extract_keywords(query: str) -> list[str]:
    """Extract meaningful keywords from the user's query."""
    q = query.lower()

    # Check for compound hints first
    hints_found = []
    for phrase, series in SERIES_HINTS.items():
        if phrase in q:
            hints_found.append(series.lower())

    # Extract individual tokens
    tokens = re.findall(r'\b[a-z0-9]+\b', q)
    meaningful = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]

    # Extract 4-digit years
    years = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', query)

    return list(set(meaningful + hints_found + years))


def score_coin(coin: dict, keywords: list[str]) -> int:
    """Score how relevant a coin entry is to the extracted keywords."""
    # Build a single searchable text blob from the coin's fields
    text = " ".join([
        str(coin.get("series", "")),
        str(coin.get("year", "")),
        str(coin.get("denomination", "")),
        str(coin.get("design_obverse", "")),
        str(coin.get("design_reverse", "")),
        str(coin.get("design_description", "")),
        str(coin.get("coin_id", "")),
    ]).lower()

    score = 0
    for kw in keywords:
        if kw in text:
            # Year matches are high-value signals
            if re.match(r'^\d{4}$', kw):
                score += 5
            # Series/denomination matches
            elif kw in str(coin.get("series", "")).lower():
                score += 4
            else:
                score += 1

    return score


def format_coin_for_context(coin: dict) -> str:
    """Format a single coin entry as a readable context block."""
    lines = [
        f"COIN: {coin.get('series', 'Unknown Series')} — {coin.get('year', '')}",
        f"  Denomination:  {coin.get('denomination', '')}",
        f"  Composition:   {coin.get('composition', '')}",
        f"  Obverse:       {coin.get('design_obverse', '')}",
        f"  Reverse:       {coin.get('design_reverse', '')}",
    ]
    if coin.get("design_description"):
        desc = coin["design_description"]
        # Truncate long descriptions
        if len(desc) > 300:
            desc = desc[:297] + "..."
        lines.append(f"  Description:   {desc}")
    if coin.get("mint_marks"):
        lines.append(f"  Mint marks:    {', '.join(coin['mint_marks'])}")
    if coin.get("mintage_notes"):
        lines.append(f"  Mintage:       {coin['mintage_notes']}")
    if coin.get("fun_facts"):
        for fact in coin["fun_facts"][:2]:
            lines.append(f"  ★ {fact}")
    return "\n".join(lines)


# ─── PUBLIC API ───────────────────────────────────────────────────────────────

def get_coin_context(
    db: firestore.Client,
    query: str,
    max_results: int = MAX_RESULTS,
) -> Optional[str]:
    """
    Given a user query, search coins_reference for relevant entries
    and return a formatted context block to inject into Morgan's prompt.

    Returns None if no relevant coins found (avoids polluting the prompt).
    """
    if not query or not query.strip():
        return None

    keywords = extract_keywords(query)
    if not keywords:
        return None

    # ── Query Firestore ────────────────────────────────────────────────────────
    # Strategy: fetch a reasonable sample and score in Python.
    # For collections up to ~2,000 docs this is fast (< 200ms).
    # For larger collections, add Firestore indexes or use Vertex AI Search.
    try:
        docs = db.collection(COLLECTION).stream()
        scored = []
        for doc in docs:
            coin = doc.to_dict()
            score = score_coin(coin, keywords)
            if score >= MIN_SCORE:
                scored.append((score, coin))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        top_coins = [coin for _, coin in scored[:max_results]]

    except Exception as e:
        # Never let a knowledge base failure break Morgan's chat
        print(f"[morgan_knowledge] Warning: Firestore query failed: {e}")
        return None

    if not top_coins:
        return None

    # ── Format context block ───────────────────────────────────────────────────
    header = (
        "NUMISMATIC REFERENCE DATA (from Numista.AI knowledge base):\n"
        "Use the following verified coin information to answer the user's question accurately.\n"
        "If the user's question matches one of these coins, cite these facts.\n"
    )
    entries = "\n\n".join(format_coin_for_context(c) for c in top_coins)

    return f"{header}\n{entries}\n"


def get_coin_by_id(db: firestore.Client, coin_id: str) -> Optional[dict]:
    """Direct lookup of a specific coin by its coin_id."""
    try:
        doc = db.collection(COLLECTION).document(coin_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"[morgan_knowledge] Lookup error for {coin_id}: {e}")
        return None
