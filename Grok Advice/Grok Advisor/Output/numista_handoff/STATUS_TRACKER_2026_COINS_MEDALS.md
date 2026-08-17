# Numista.AI — 2026 Coins, Currency & Medals Image Tracker

**Created:** 2026-08-17  
**Last Updated:** 2026-08-17 15:25 EDT  
**Purpose:** Lightweight companion tracker for all 2026 U.S. Mint circulating coins, new currency, and medals released (or scheduled) in 2026.  
**Companion to:** `STATUS_TRACKER.md` (the 224 banknote/obsolete list). Keep the two files separate.

**Working order (locked):** Finish every 2026 US Mint numismatic item (COMPLETE or explicitly CAN’T FIND / PENDING_RELEASE) → then 2025 → then 2024. “Easy fruit” first.

**Rules (same discipline as banknote tracker):**
- Real photographs only. No AI generation.
- Preferred sources: Official U.S. Mint images, NNC/Smithsonian, BEP, public-domain government photography.
- Always record source URL + credit before download.
- Naming: `{year}_{description}_{side}.png` (or .jpg). Include mint mark when relevant.
- Specs: Prefer ≥1200 px on long edge, clean background, properly cropped.

**Status vocabulary:**  
`NOT_STARTED` | `SEARCHING` | `URL_FOUND` | `DOWNLOADED` | `COMPLETE` | `PENDING_RELEASE`

---

## Coverage Summary — 2026-08-17 (updated after canonical copy)

| Category                        | Total Items | Complete | Remaining |
|---------------------------------|-------------|----------|-----------|
| Semiquincentennial Circulating  | 8           | **8**     | 0         |
| American Innovation $1          | 4 + shared  | **5**     | 0         |
| Other Circulating / Program     | 3           | **2**     | 1         |
| 2026 Currency (new designs)     | 1           | 0        | 1         |
| Medals (Comic Art + Best of Mint + Presidential + other) | ~20+ | Partial | Most      |
| **Total major circulating**     | **~16**     | **15**   | **1**     |

**Note:** All major 2026 circulating designs are now present in the canonical folder  
`gs://numista-reference-library/reference_library/2026_series/` (25 official stills).

---

## 1. Semiquincentennial Circulating Coins (1776~2026 dual date)

| ID | Description | Need Obv | Need Rev | Status | Notes / Credit |
|----|-------------|----------|----------|--------|----------------|
| 2026-Q1 | Mayflower Compact Quarter | YES | YES | **COMPLETE** | In `2026_series/` |
| 2026-Q2 | Revolutionary War Quarter | YES | YES | **COMPLETE** | In `2026_series/` |
| 2026-Q3 | Declaration of Independence Quarter | YES | YES | **COMPLETE** | Added 2026-08-17 from official Mint stills |
| 2026-Q4 | U.S. Constitution Quarter | YES | YES | **COMPLETE** | Added 2026-08-17 from official Mint stills |
| 2026-Q5 | Gettysburg Address Quarter | YES | YES | **COMPLETE** | Added 2026-08-17 from official Mint stills |
| 2026-DIME | Emerging Liberty Dime | YES | YES | **COMPLETE** | In `2026_series/` |
| 2026-HALF | Enduring Liberty Half Dollar | YES | YES | **COMPLETE** | Added 2026-08-17 from official Mint stills |
| 2026-CENT | 2026 Lincoln Cent (numismatic) | YES | YES | **COMPLETE** | In `2026_series/` |

## 2. American Innovation $1 Coins — 2026

| ID | State | Need Obv | Need Rev | Status | Notes |
|----|-------|----------|----------|--------|-------|
| 2026-AI-OBV | Shared 2026 Innovation Obverse | YES | — | **COMPLETE** | Liberty Bell “250” privy; in `2026_series/` |
| 2026-AI-IA | Iowa | — | YES | **COMPLETE** | Reverse only (shared obverse); in `2026_series/` |
| 2026-AI-WI | Wisconsin | — | YES | **COMPLETE** | Reverse only; in `2026_series/` |
| 2026-AI-CA | California | — | YES | **COMPLETE** | Reverse only; in `2026_series/` |
| 2026-AI-MN | Minnesota | — | YES | **COMPLETE** | Reverse only; in `2026_series/` |

## 3. Other 2026 Program / Circulating

| ID | Description | Need Obv | Need Rev | Status | Notes |
|----|-------------|----------|----------|--------|-------|
| 2026-NA | Native American $1 Coin 2026 (Polly Cooper) | YES | YES | **COMPLETE** | Added 2026-08-17; official Mint stills |
| 2026-NICKEL | 2026 Jefferson Nickel | YES | YES | **COMPLETE** | Dual-date; in `2026_series/` |
| 2026-PENNY-CIRC | 2026 circulating Lincoln Cent (if any) | YES | YES | NOT_STARTED | Regular circulating cents may be limited / different from collector version |

## 4. 2026 Currency (Paper Money)

| ID | Description | Need Obv | Need Rev | Status | Notes |
|----|-------------|----------|----------|--------|-------|
| 2026-C10 | Redesigned $10 Federal Reserve Note (Catalyst / next family) | YES | YES | PENDING_RELEASE | Official schedule targets 2026. Not yet confirmed in circulation as of mid-August 2026. |

## 5. 2026 U.S. Mint Medals (selected major series)

### Comic Art Medal Series
| ID | Subject | Status | Notes |
|----|---------|--------|-------|
| 2026-MED-COMIC-SUP | Superman | SEARCHING | Gold coin pairs exist; silver medal reverses incomplete |
| 2026-MED-COMIC-BAT | Batman | SEARCHING | Gold coin pairs exist |
| 2026-MED-COMIC-WW | Wonder Woman | SEARCHING | Gold coin pairs exist; silver medal reverses incomplete |
| 2026-MED-COMIC-SG | Supergirl | NOT_STARTED | |
| 2026-MED-COMIC-ROB | Robin | **DOWNLOADED** | Official composite (gold coin + 2.5 oz silver medal) staged as `2026_comic_art_robin_gold_and_silver_medal_composite.png`. Source: U.S. Mint via CoinNews (11 Aug 2026). |
| 2026-MED-COMIC-GL | Green Lantern | SEARCHING | Final product images not yet confirmed public as of mid-Aug 2026. |

### Best of the Mint Companion Silver Medals
| ID | Companion to | Status | Notes |
|----|--------------|--------|-------|
| 2026-MED-BOTM-MERC | 1916 Mercury Dime gold | **COMPLETE** | Official pairs present in bulk_programs / us_mint_coin_images |
| 2026-MED-BOTM-SLQ | 1916 Standing Liberty Quarter gold | **COMPLETE** | Official pairs present |
| 2026-MED-BOTM-WLH | 1916 Walking Liberty Half gold | **COMPLETE** | Official pairs present |
| 2026-MED-BOTM-1804 | 1804 Draped Bust Dollar gold | **COMPLETE** | Official pairs present |
| 2026-MED-BOTM-STG | 1907 Saint-Gaudens High Relief $20 gold | **COMPLETE** | Official pairs present |

### Presidential Silver Medals (2026 releases)
| ID | President | Status | Notes |
|----|-----------|--------|-------|
| 2026-MED-PRES-HARDING | Warren G. Harding | **DOWNLOADED** | Obverse + reverse staged (`2026_presidential_silver_medal_harding_obverse.png` / `_reverse.png` + composite). Source: U.S. Mint via CoinNews (May 2026). |
| 2026-MED-PRES-COOLIDGE | Calvin Coolidge | PENDING_RELEASE / SEARCHING | Scheduled later 2026. |
| 2026-MED-PRES-HOOVER | Herbert Hoover | PENDING_RELEASE / SEARCHING | Scheduled Fall 2026. |

### FIFA World Cup 2026 Commemoratives
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| 2026-FIFA-GOLD | $5 Gold (Proof/Unc) | **DOWNLOADED** | Obverse + reverse staged. Source: U.S. Mint via CoinNews (June 2026). |
| 2026-FIFA-SILVER | Silver Dollar (Proof/Unc) | **DOWNLOADED** | Obverse + reverse staged. |
| 2026-FIFA-HALF | Half Dollar (Proof/Unc) | **DOWNLOADED** | Obverse + reverse staged. |
| 2026-FIFA-SET | Three-coin set composite | **DOWNLOADED** | Full set composite also staged. |

### Other / Semiquincentennial Medals
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| 2026-MED-SEMIQ-MISC | Other official Semiquincentennial medals | SEARCHING | Expand as specific medals are identified |

---

## Canonical Folder Status

**Path:** `gs://numista-reference-library/reference_library/2026_series/`  
**Objects:** 25 official stills (as of 2026-08-17) + new FIFA / Robin / Harding stills staged locally  
**Action completed:** High-quality official Mint stills for all major 2026 circulating designs were copied into this folder with consistent naming.

**Change notice for Antigravity:** Sent 2026-08-17 — full 2026 circulating set now available in the canonical folder.

---

**Last Updated:** 2026-08-17 15:30 EDT

**Working order (per direction):** Finish every 2026 US Mint numismatic coin / note / medal (complete or explicitly “CAN’T FIND / PENDING_RELEASE”) → then 2025 → then 2024.
