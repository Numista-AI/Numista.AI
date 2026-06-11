# Missing Coin Images — Full Sourcing Report
**Source collection:** jseaman1204@gmail.com (3,910 coins — largest beta tester)  
**Generated:** 2026-06-05 | **Image index:** 667 unique Firestore entries

---

## Coverage Summary

| Metric | Value |
|--------|-------|
| Total coins | 3,910 |
| **With reference image** | **1,207 (30%)** |
| Missing image | 2,643 (68%) |
| Skipped (no year / coin sets) | 60 (2%) |
| **Unique gaps to fill** | **1,695** |

📥 **Full gap list:** [missing_coin_images.csv](file:///C:/Users/ericd/.gemini/antigravity/brain/15c081f5-8cd3-44dd-8c0a-17baa2030502/missing_coin_images.csv)  
*(Columns: Count, Year, Mint, Denomination, Program/Series, Theme/Subject, Resolved_Program, Resolved_Subject, Best_Key_Tried)*

---

## Gaps by Program (sorted by coins affected)

| Coins affected | Program | Top 3 missing keys |
|---------------:|---------|-------------------|
| **598** | lincoln-cent | 1921, 1925, 1911, 1912, 1916, 1917, 1919, 1920, 1924, 1925, 1928, 1930, 1931, 1938... |
| **367** | quarter | 2022_S, 1945_S, 1934, various pre-1999 |
| **342** | kennedy-half-dollar | 1952 and before (Franklin era mismatch) |
| **332** | dime | 1963_D, pre-1900 Barber/Seated Liberty |
| **200** | barber | 1911_D, 1895_S, 1905_O (halves/quarters) |
| **115** | dollar | 1974_S, 1973_S, 1971_S (Eisenhower) |
| **112** | morgan-dollar | 2023, 1880_CC, 1891 |
| **111** | american-eagle-silver | 1992, 2018, 2021 |
| **87** | mercury-dime | 1917_S, 1918_S, 1918_D |
| **82** | nickel | 1829–1832 (Shield/Liberty nickels) |
| **68** | presidential-dollars | 2015_P/D/S |
| **66** | UNKNOWN | "5-Coin Set" — no program match |
| **48** | cent | 1897, 1846, 1899 (Indian Head) |
| **39** | jefferson-nickel | 1945_S, 2021_S, 1943_S |
| **24** | peace-dollar | 1923_S, 2023, 1922 |
| **22** | native-american-dollar | 2001_P/D/S |
| **19** | buffalo-nickel | 1929_S, 1914_S, 1916_S |
| **6** | american-eagle-gold | 1995, 2006 |
| **3** | walking-liberty | 1941, 1943, 1944_D |
| **2** | commemorative | 1926, 1942 |

---

## Sourcing Guide by Category

> [!IMPORTANT]
> All images must be **obverse + reverse** pairs. Name files to include the year and side:
> e.g. `1921_lincoln_cent_obverse.jpg` / `1921_lincoln_cent_reverse.jpg`
> Upload to the correct GCS folder (see below) — the indexer picks them up automatically.

### 📁 GCS Upload Target
```
gs://numista-reference-library/reference_library/wikimedia_uscoin/{subfolder}/
```

---

### 🥇 Priority 1 — Lincoln Cents (598 coins affected)
**GCS subfolder:** `Lincoln_cents`  
**Years needed:** 1909–1958 (nearly all, especially 1911–1936, 1938–1958)  
**Already indexed:** 1909, 1943 (from existing Smithsonian/NNC images)

| Source | Quality | Search term | Notes |
|--------|---------|-------------|-------|
| **PCGS CoinFacts** | ⭐⭐⭐⭐⭐ | `pcgs.com/coinfacts/coin/lincoln-wheat-cent-1c/2936` | Year-by-year pages, right-click → Save image |
| **NGC Coin Explorer** | ⭐⭐⭐⭐⭐ | `ngccoin.com/coin-explorer/lincoln-cents-msb-item-3726` | Excellent high-res scans |
| **Kaggle** | ⭐⭐⭐⭐ | Search: "US coin dataset" or "Lincoln cent dataset" | Bulk CSVs with image URLs |
| **Heritage Auctions** | ⭐⭐⭐⭐⭐ | `ha.com` → Coins → Lincoln Cents | Superb auction photos |
| Wikimedia (NNC prefix) | ⭐⭐⭐⭐ | `NNC-US-{YEAR}-1C-Lincoln_Cent_(wheat)_LEFT.jpg` | Only 1909 + 1943 exist |

**Naming for indexer:**
```
1921_lincoln_cent_obverse.jpg → key: 1921_lincoln-cent_obverse ✓
1921_lincoln_cent_reverse.jpg → key: 1921_lincoln-cent_reverse ✓
```

---

### 🥈 Priority 2 — Quarter (367 coins, pre-1999 / S-mint proofs)
**GCS subfolder:** `United_States_quarters/Washington_quarter/Obverses_of_Washington_quarters/`  
*(Already exists — just add missing year images to this folder)*

| Years missing | Source |
|---------------|--------|
| S-mint proofs (2000S–2022S) | **US Mint** → usmint.gov/coins/coin-medal-programs → State Quarters |
| Pre-1999 Washington quarters | PCGS CoinFacts: `pcgs.com/coinfacts/coin/washington-quarter-25c/5796` |
| 1932–1964 proof quarters | NGC Coin Explorer |

---

### 🥉 Priority 3 — Eisenhower Dollar (115 coins, 1971–1978)
**GCS subfolder:** `Eisenhower_dollars`

| Source | URL |
|--------|-----|
| **US Mint archive** | usmint.gov/coins/coin-medal-programs/eisenhower-dollar |
| **PCGS CoinFacts** | `pcgs.com/coinfacts/coin/eisenhower-dollar-1/7354` |
| **Wikimedia** | `Eisenhower_dollar_obverse1.jpg` / `Eisenhower_dollar_reverse1.jpg` exist (full-size OK) |

**Naming:** `1974_S_eisenhower_dollar_obverse.jpg` → key: `1974_S_dollar_obverse`

---

### Priority 4 — Morgan Dollar (112 coins, inc. 2021–2023 modern)
**GCS subfolder:** `Morgan_dollars`

| Source | Notes |
|--------|-------|
| **US Mint** | 2021–2023 modern Morgans: usmint.gov/coins/coin-medal-programs/morgan-dollar |
| **PCGS CoinFacts** | Classic 1878–1921: `pcgs.com/coinfacts/coin/morgan-dollar-1/7090` |
| **Heritage Auctions** | Best for CC, O, S mint marks — auction photos |

---

### Priority 5 — American Eagle Silver (111 coins, 1986–present)
**GCS subfolder:** `American_eagle` *(or add to existing `american-eagle-silver` folder)*

| Source | Notes |
|--------|-------|
| **US Mint** | Official images: usmint.gov/coins/coin-medal-programs/american-silver-eagle |
| **PCGS CoinFacts** | `pcgs.com/coinfacts/coin/american-silver-eagle-1/11224` |

---

### Priority 6 — Barber Coinage (200 coins — half/quarter/dime 1892–1916)
**GCS subfolder:** `Barber_coinage`

| Source | Notes |
|--------|-------|
| **PCGS CoinFacts** | Halves: `/7086`, Quarters: `/5796`, Dimes: `/4584` |
| **NGC Coin Explorer** | Year-by-year variety photos |
| **Wikimedia** | `1892_Barber_dime_obverse.jpg`, etc. — some exist as full-size |

---

### Priority 7 — Mercury Dime (87 coins, 1916–1945)
**GCS subfolder:** `Mercury_dimes`

| Source | Notes |
|--------|-------|
| **PCGS CoinFacts** | `pcgs.com/coinfacts/coin/winged-liberty-head-dime-10c/4674` |
| **Wikimedia (full-size)** | `Mercury_dime_obverse.jpg` exists — great for generic; year-specific vary |

---

### Priority 8 — Peace Dollar (24 coins, 1921–2023)
**GCS subfolder:** `Peace_dollars`

| Source | Notes |
|--------|-------|
| **US Mint** | 2021–2023 modern Peace Dollars at usmint.gov |
| **PCGS CoinFacts** | Classic 1921–1935: `pcgs.com/coinfacts/coin/peace-dollar-1/7358` |
| **Wikimedia** | `1928_Peace_Dollar_LEFT.jpg` already in our bucket |

---

### Priority 9 — Buffalo Nickel (19 coins, 1913–1938)
**GCS subfolder:** `Buffalo_nickels`

| Source | Notes |
|--------|-------|
| **PCGS CoinFacts** | `pcgs.com/coinfacts/coin/buffalo-nickel-5c/3938` |
| **Wikimedia** | 1913 Type I/II exist as full-size; 1916-1938 need sourcing |

---

## How to Upload Images

Once you have the images saved locally:

```powershell
# Upload a single image
gsutil cp 1921_lincoln_cent_obverse.jpg gs://numista-reference-library/reference_library/wikimedia_uscoin/Lincoln_cents/

# Upload a whole folder
gsutil -m cp C:\CoinImages\Lincoln_cents\*.jpg gs://numista-reference-library/reference_library/wikimedia_uscoin/Lincoln_cents/
```

Then run the indexer to pick them up:
```powershell
cd C:\Users\ericd\Documents\MyVertexProject\numista_backend
$env:PYTHONUTF8=1; .venv\Scripts\python build_image_index.py
```

Then regenerate the gap CSV:
```powershell
$env:PYTHONUTF8=1; $env:GOOGLE_APPLICATION_CREDENTIALS=".\serviceAccountKey.json.json"; .venv\Scripts\python gen_missing_images.py
```

---

## Naming Convention Reference

The indexer detects year, side, and program from the filename. Use these patterns:

| Pattern | Key produced |
|---------|-------------|
| `1921_lincoln_cent_obverse.jpg` | `1921_lincoln-cent_obverse` |
| `1974_S_eisenhower_dollar_obverse.jpg` | `1974_S_dollar_obverse` |
| `1917_mercury_dime_reverse.jpg` | `1917_mercury-dime_reverse` |
| `1923_peace_dollar_obverse.jpg` | `1923_peace-dollar_obverse` |
| `1929_buffalo_nickel_reverse.jpg` | `1929_buffalo-nickel_reverse` |
| `1948_franklin_half_dollar_obverse.jpg` | `1948_kennedy-half-dollar_obverse` |

> [!TIP]
> Files need `obverse`/`reverse` (or `obv`/`rev`, `front`/`back`, `left`/`right`) in the filename.
> The year must be a 4-digit number. Mint mark in the filename (e.g. `1974_S_`) is optional but helps.
