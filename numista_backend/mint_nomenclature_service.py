#!/usr/bin/env python3
"""
mint_nomenclature_service.py

Ingestion-time normalization and enrichment service for the Golden Coin Schema.
Parses numeric face values, precious metal weights, millesimal fineness, and purity.
"""

import re
from typing import Dict, Any, Optional

def parse_denomination_numeric(raw_denom: str) -> float:
    """
    Parses a raw denomination string into an exact float value in USD.
    Normalizes input by lowercasing, collapsing whitespace, and stripping
    trailing parenthetical text / ellipses (e.g. "Five Dollars (Hal..." -> 5.00).
    Evaluates multi-word written numbers and dollar symbols in strict descending order.
    """
    if not raw_denom:
        return 0.0

    s = raw_denom.lower().strip()
    # Strip parenthetical notes and trailing dots/ellipses
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'\.{2,}', '', s).strip()

    # 1. High Gold & Commemoratives
    if '$500' in s or 'five hundred dollar' in s: return 500.00
    if '$100' in s or 'one hundred dollar' in s or 'hundred dollar' in s: return 100.00
    if '$50' in s or 'fifty dollar' in s: return 50.00
    if '$25' in s or 'twenty five dollar' in s or 'twenty-five dollar' in s: return 25.00
    if '$20' in s or 'twenty dollar' in s or 'double eagle' in s: return 20.00
    if '$10' in s or 'ten dollar' in s or ('eagle' in s and 'half' not in s and 'quarter' not in s and 'silver' not in s): return 10.00
    if '$5' in s or 'five dollar' in s or 'half eagle' in s: return 5.00
    if '$3' in s or 'three dollar' in s: return 3.00
    if '$2.50' in s or '$2.5' in s or 'quarter eagle' in s or 'two and a half' in s: return 2.50
    if '$2' in s or 'two dollar' in s: return 2.00

    # 2. Standard Dollars & Sub-Dollar Denominations
    if 'half dollar' in s or '50c' in s or '50 cent' in s or '$0.50' in s or '$0.5' in s: return 0.50
    if 'quarter dollar' in s or 'quarter' in s or '25c' in s or '25 cent' in s or '$0.25' in s: return 0.25
    if 'twenty cent' in s or '20c' in s: return 0.20
    if 'dime' in s or '10c' in s or '10 cent' in s or '$0.10' in s or '$0.1' in s: return 0.10
    if 'half dime' in s: return 0.05
    if 'nickel' in s or '5c' in s or '5 cent' in s or '$0.05' in s: return 0.05
    if 'three cent' in s or '3c' in s: return 0.03
    if 'two cent' in s or '2c' in s: return 0.02
    if 'half cent' in s: return 0.005
    if 'penny' in s or 'cent' in s or '1c' in s or '1 cent' in s or '$0.01' in s: return 0.01

    if 'dollar' in s or '$1' in s: return 1.00

    # Fallback: plain numeric parse (e.g. "0.25" -> 0.25)
    match = re.search(r'\d+(?:\.\d+)?', s)
    if match:
        val = float(match.group(0))
        return val if val <= 1000.0 else 0.0

    return 0.0

def calculate_metal_weight(
    metal_str: str = "",
    denom_str: str = "",
    series_str: str = "",
    theme_str: str = ""
) -> Dict[str, Any]:
    """
    Calculates metal_type, purity, weight_grams, troy_oz_pure_metal, is_gold, is_silver.
    Combines metalContent field with series, theme, and denomination inference.
    """
    mc = (metal_str or "").lower()
    denom = (denom_str or "").lower()
    series = (series_str or "").lower()
    theme = (theme_str or "").lower()
    combined = f"{mc} {denom} {series} {theme}"

    is_gold = False
    is_silver = False
    metal_type = "Clad/Base"
    purity = 0.0
    weight_grams = 0.0
    troy_oz_pure_metal = 0.0

    # 1. Gold Detection & Weight
    if 'gold' in combined or 'au' in mc or 'half eagle' in combined or 'eagle' in combined or 'double eagle' in combined:
        if '99.99' in combined or 'buffalo' in combined:
            is_gold = True
            metal_type = "Gold"
            purity = 0.9999
            troy_oz_pure_metal = 1.000
            weight_grams = 31.1035
        elif 'gold eagle' in combined or '91.67' in combined:
            is_gold = True
            metal_type = "Gold"
            purity = 0.9167
            # Denomination face value determines Gold Eagle size
            fv = parse_denomination_numeric(denom_str)
            if fv == 50.0: troy_oz_pure_metal = 1.00; weight_grams = 33.93
            elif fv == 25.0: troy_oz_pure_metal = 0.50; weight_grams = 16.96
            elif fv == 10.0: troy_oz_pure_metal = 0.25; weight_grams = 8.48
            elif fv == 5.0: troy_oz_pure_metal = 0.10; weight_grams = 3.39
            else: troy_oz_pure_metal = 1.00; weight_grams = 33.93
        elif '90%' in combined or 'half eagle' in combined or 'indian head gold' in combined or 'pre-1933' in combined or 'saint-gaudens' in combined or 'liberty head' in combined:
            is_gold = True
            metal_type = "Gold"
            purity = 0.9000
            fv = parse_denomination_numeric(denom_str)
            if fv == 20.0: troy_oz_pure_metal = 0.96750; weight_grams = 33.436
            elif fv == 10.0: troy_oz_pure_metal = 0.48375; weight_grams = 16.718
            elif fv == 5.0: troy_oz_pure_metal = 0.24187; weight_grams = 8.359
            elif fv == 2.5: troy_oz_pure_metal = 0.12094; weight_grams = 4.180
            else: troy_oz_pure_metal = 0.24187; weight_grams = 8.359
        elif 'gold' in combined:
            is_gold = True
            metal_type = "Gold"
            purity = 0.9000
            troy_oz_pure_metal = 0.24187
            weight_grams = 8.359

    # 2. Silver Detection & Weight
    if not is_gold and ('silver' in combined or 'ag' in mc or 'silver eagle' in combined or 'peace dollar' in combined or 'morgan' in combined):
        if 'silver eagle' in combined or '99.9' in combined or '.999' in combined or 'fine silver' in combined:
            is_silver = True
            metal_type = "Silver"
            purity = 0.999
            troy_oz_pure_metal = 1.000
            weight_grams = 31.1035
        elif '90%' in combined or 'morgan' in combined or 'peace' in combined or 'barber' in combined or 'walking liberty' in combined or 'standing liberty' in combined or 'mercury' in combined:
            is_silver = True
            metal_type = "Silver"
            purity = 0.9000
            fv = parse_denomination_numeric(denom_str)
            if fv == 1.00: troy_oz_pure_metal = 0.77344; weight_grams = 26.73
            elif fv == 0.50: troy_oz_pure_metal = 0.36169; weight_grams = 12.50
            elif fv == 0.25: troy_oz_pure_metal = 0.18084; weight_grams = 6.25
            elif fv == 0.10: troy_oz_pure_metal = 0.07234; weight_grams = 2.50
            else: troy_oz_pure_metal = 0.77344; weight_grams = 26.73
        elif '40%' in combined:
            is_silver = True
            metal_type = "Silver"
            purity = 0.4000
            troy_oz_pure_metal = 0.14792
            weight_grams = 11.50
        elif '35%' in combined or 'war nickel' in combined:
            is_silver = True
            metal_type = "Silver"
            purity = 0.3500
            troy_oz_pure_metal = 0.05626
            weight_grams = 5.00
        elif 'silver' in combined:
            is_silver = True
            metal_type = "Silver"
            purity = 0.9000
            troy_oz_pure_metal = 0.77344
            weight_grams = 26.73

    return {
        'metal_type': metal_type,
        'purity': purity,
        'weight_grams': weight_grams,
        'troy_oz_pure_metal': troy_oz_pure_metal,
        'is_gold': is_gold,
        'is_silver': is_silver,
    }

def enrich_coin_schema(coin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches a coin dictionary with canonical numeric schema fields.
    """
    denom_str = str(coin_data.get('Denomination') or coin_data.get('denomination') or '')
    metal_str = str(coin_data.get('Metal Content') or coin_data.get('metalContent') or coin_data.get('metal_content') or '')
    series_str = str(coin_data.get('Program/Series') or coin_data.get('programSeries') or coin_data.get('series') or '')
    theme_str = str(coin_data.get('Theme/Subject') or coin_data.get('themeSubject') or coin_data.get('theme') or '')

    denom_num = parse_denomination_numeric(denom_str)
    metal_info = calculate_metal_weight(metal_str, denom_str, series_str, theme_str)

    enriched = dict(coin_data)
    enriched['denomination_numeric'] = denom_num
    enriched['metal_type'] = metal_info['metal_type']
    enriched['purity'] = metal_info['purity']
    enriched['weight_grams'] = metal_info['weight_grams']
    enriched['troy_oz_pure_metal'] = metal_info['troy_oz_pure_metal']
    enriched['is_gold'] = metal_info['is_gold']
    enriched['is_silver'] = metal_info['is_silver']

    return enriched
