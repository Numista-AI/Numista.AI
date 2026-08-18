# Numista.AI Image Sourcing Status Tracker

**Canonical file:** this document. Do not create `STATUS_TRACKER (1).md` or a second table. `STATUS_TRACKER (1).md` is a superseded 2026-08-07 snapshot (it incorrectly counted TYPE_003/004 Imagine pairs as delivered).

**Task start:** 2026-08-07
**Last updated:** 2026-08-16
**Universe:** 224 work IDs (TYPE_001–TYPE_224) from `grok_prompt_payload.txt`
**Owner:** unassigned

**HOLD:** No AI generation of coin/note images. Banknote SOP forbids AI renders in the reference library.
**Ingest only if:** real photograph + `MANIFEST.json` + SOP filename + catalog_key + license.
**Work ID vs storage name:** `TYPE_XXX` is a tracker key only. Storage names must follow `SOPs/banknote_image_sop.md` (or the coin SOP for coins).
**Target bucket:** `gs://numista-reference-library/reference_library/us_banknotes/`
(not `studio-...-uploads`; that bucket is personal/user photos)
**Allowed sources:** NNC/Wikimedia, BEP/Treasury/LOC/NARA, Newman Numismatic Portal public domain, attributed user contributions with waiver.
**Prohibited:** Heritage, Stack's, PMG/PCGS scrapers, AI renders.

**Credits:** Always record source URL, license, and credit before any download.
**Specs for real photos:** genuine physical-note photography; clean crop; prefer ≥1200 px on the long edge. Do not square-crop banknotes.

## Coverage strip — 2026-08-16

| Bucket | Complete real pairs | Remaining | Notes |
|--------|---------------------|-----------|-------|
| **P1** (engraving errors, obsolete, Confederate, Continental, National Bank Notes) | **0** | **39** | All 39 P1 work IDs are now listed. No required side has a licensed real photograph. Wikimedia NNC face for TYPE_003 is credit-only (obverse is not required). Imagine / Heritage files do not count. |
| **P2** (gold/silver certificates, Educational Series, fractional, large-size legal tender, Treasury notes) | **0** | **84** | All 84 P2 work IDs are now listed. None complete. |
| **P3** (FRNs, FRBNs, small-size legal tender, MPC) | **0** | **101** | All 101 P3 work IDs are now listed. None complete. Heritage `currency_batch_01` plan for TYPE_005–034 is quarantined and does not reduce this count. |
| **Unbucketed of 224** | — | **0** | `39 + 84 + 101 = 224`. |

**Status vocabulary:** `NOT_STARTED` | `SEARCHING` | `URL_FOUND` | `DOWNLOADED` | `MANIFEST_READY` | `INTAKE_BLOCKED` | `QUARANTINE_AI` | `QUARANTINE_AUCTION` | `BLOCKED_NO_PUBLIC_LICENSE`

Existing table cells still use `PENDING` / `N/A` until those rows are migrated to the vocabulary above. `PENDING` = not a complete real pair.

## Quarantine list — do not ingest, do not count as found

These files already exist on disk. They are **not** complete pairs. Do not upload them to `numista-reference-library`. Do not mark the matching TYPE row found because of them.

### QUARANTINE_AI

| Location | Files | Why |
|----------|-------|-----|
| `Gemini Advisor Documents/Grok Advisor/AI Generated Downloads/1862_confederate_and_1907_pcblic_error_images/` | `1862_confederate_states_2_dollar_t43_obverse.png`, `1862_confederate_states_2_dollar_t43_reverse.png`, `1907_5_legal_tender_woodchopper_pcblic_error_obverse.png`, `1907_5_legal_tender_woodchopper_pcblic_error_reverse.png` | Grok Imagine pairs for TYPE_003 / TYPE_004. Banknote SOP forbids AI in the reference library. |
| `Gemini Advisor Documents/Grok Advisor/AI Generated Downloads/` | `CSA-T43-$2-1862.jpg` | Sitting in the AI downloads folder; treat as synthetic until a public-domain source is attached. |
| Agent artifact path cited by superseded `STATUS_TRACKER (1).md` | `TYPE_003_obverse.png`, `TYPE_003_reverse.png`, `TYPE_004_obverse.png`, `TYPE_004_reverse.png` under `/home/workdir/artifacts/numista_image_sourcing/downloads/` | Not in this Windows repo. Imagine output. Do not restore or ingest if found. |
| `1 NUMISTA.AI/Coin Images/Coins Images to Find/Downloads from Grok/pilot_confederate_5/` and `_new_extract/pilot_confederate_5/` | `T-63_1863_50_Cents_Jefferson_Davis_Obverse.jpg`, `T-63_1863_50_Cents_Reverse.jpg`, `T-64_1864_500_Stonewall_Jackson_Obverse.jpg`, `187bffa4-…`, `1af7178f-…`, `2ea45a00-…` | Pilot README / `manifest.csv`: “Completed - High quality AI render.” `processed_renders.json` also flags T-63 as a garbled-text render. |
| `1 NUMISTA.AI/Coin Images/Coins Images to Find/Downloads from Grok/_remaining_extract/pilot_confederate_remaining_v1/` | `cbKxD.jpg`, `kenEJ.jpg`, `qvhPc.jpg`, `WhHb1.jpg`, `xLTNx.jpg` | Package README: “new renders generated” for remaining Confederate notes. |
| Same tree | `processed_renders.json`, `pilot_confederate_5.zip`, `pilot_confederate_remaining_v1.zip` | Indexes / archives of the AI pilots above. |

### QUARANTINE_AUCTION

| Location | Files | Why |
|----------|-------|-----|
| `1 NUMISTA.AI/Coin Images/Coins Images to Find/Downloads from Grok/` | `1929 Heritage Auctions $10 Federal Reserve Bank Note Obverse.jpg`, `1929 Heritage Auctions $10 Federal Reserve Bank Note Reverse.jpg` | Auction-house photography. SOP §5.B prohibits Heritage scrapers. |
| `…/Downloads from Grok/_real_extract/pilot_real_images_v1/images/` | `1864_10_Dollar_Confederate_T68_Obverse_Heritage.jpg`, `1864_10_Dollar_Confederate_T68_Reverse_Heritage.jpg`, `c1b68828-53c5-4b9d-ab69-3eb3b636f69e_obverse.jpg`, `c1b68828-53c5-4b9d-ab69-3eb3b636f69e_reverse.jpg` | `manifest.csv` credits “Heritage Auctions (HA.com) professional photography.” |
| `…/Downloads from Grok/currency_batch_01_v1/` (and the duplicate zip / `(1).zip`) | `manifest.csv`, `README.md` (no image files in the folder) | Batch of TYPE_005–TYPE_034 pre-credited “Heritage Auctions — to be downloaded by user.” Do not execute that download plan. |

Unlisted files in `Downloads from Grok/` (e.g. the 1918 FRBN / TYPE_005 JPEGs, `s-l1200.jpg`) are **not** cleared. Source is unverified; treat as `INTAKE_BLOCKED` until a license is recorded.

## Set / sheet rule

A work ID that is an **uncut sheet**, a **multi-note set**, or a **remainder pack** is not one note.

- One `TYPE_XXX_obverse.png` must never stand in for a 4-subject sheet or a 7-note set.
- Either ingest a single **sheet** image using the SOP `sheet_{issuer_slug}_{layout}_{obv|rev}` key, **or** add child rows per denomination / subject and source each note separately.
- Distinct plate varieties stay distinct. TYPE_214 (CT120G8) and TYPE_215 (CT120G10C) must never share an image.

Applies today to: **TYPE_184** (CT Bank of New England uncut), **TYPE_187** (West River 7-note set), **TYPE_192** (West River uncut sheet of 4: $1/$2/$3/$5), **TYPE_195** (large-size starter set), **TYPE_204** (Union County Bank uncut), **TYPE_205** (State Bank of New Brunswick uncut), **TYPE_216** (Farmer's Bank of Kentucky 3-note set).

## Typo → search footnotes

Source descriptions in `grok_prompt_payload.txt` carry OCR / entry typos. Use the cleaned query when hunting public-domain images. Do not search the typo string as-is.

| Work ID | Dirty string (do not search) | Clean search |
|---------|------------------------------|--------------|
| TYPE_001 | “181-Teen's” | Farmers Bank of Bucks County Hulmeville Pennsylvania $1 1810s obsolete |
| TYPE_002 / 200 / 203 | “Fereral” / “Ferderal” | Federal Reserve |
| TYPE_003 | — | Confederate T-43 $2 1864 (often cataloged from 1862 issue date); reverse / back only |
| TYPE_004 / 115 | “Ledal Tender” / “P*C*BLIC” | Legal Tender $5 1907 Woodchopper **PCBLIC** engraving error Fr. 91 |
| TYPE_047 | “$14 Federal Reserve Note” | Confirm collection doc; likely $10 or $20 1914 FRN |
| TYPE_049 | year 1978 | $2 FRN 1976 (no 1978 $2 series) |
| TYPE_071 | “% cents” | 5¢ Fractional Currency |
| TYPE_092 | “Latge size” | $20 Gold Certificate large size 1906 |
| TYPE_125 | “$! Military” | $1 Military Payment Certificate |
| TYPE_132 | “notr” | $5 National Bank Note 1902 |
| TYPE_136 | “Bote” / “1705-024” | New York Marble Manufacturing $100 obsolete Haxby NY-1705 |
| TYPE_141 | year 1823 | $1 Silver Certificate Fr. 237 (1923) |
| TYPE_171 | “Largensize” | $2 Educational Series 1896 |
| TYPE_184 | “CT Nank of NewEngland” | Bank of New England Connecticut uncut sheet W-CT-250 |
| TYPE_186 / 187 / 192 | “West Riverbank” | West River Bank Jamaica Vermont obsolete (single / 7-note set / uncut sheet of 4) |
| TYPE_188 / 212 | “Conferate” / “Confedwrate” | Confederate |
| TYPE_189 | “ilver Certificate” | Silver Certificate large size 1886 |
| TYPE_190 | “Leal Tender” | Legal Tender star note 1963 |
| TYPE_191 | “Bamk of Windsor” | Bank of Windsor Vermont $1 obsolete PMG |
| TYPE_194 / 196 | “Cerificate” | Silver Certificate |
| TYPE_204 | “sgeet” | Union County Bank Plainfield NJ uncut sheet |
| TYPE_208 / 214 / 215 | “Iton Bank” | Falls Village **Iron** Bank Connecticut CT120 (G14C / G8 / G10C) |
| TYPE_209 | — | State of Georgia Milledgeville $10 1865 |
| TYPE_210 / 223 | — | Third Bank of the United States (Haxby) $1000 New York / $500 Philadelphia |
| TYPE_224 | “Gractional” | 5¢ Fractional Currency 1862–1869 |

## Priority 1: Engraving errors, obsolete, Confederate, Continental, National Bank Notes (39)

Hunt order: NNC / Wikimedia → LOC / BEP / NARA / NNP → stop. Do not scrape Heritage / PMG / PCGS Currency.

| TYPE_ID | Description | Need Obv | Need Rev | Status Obv | Status Rev | Source / Notes | Credit |
|---------|-------------|----------|----------|------------|------------|----------------|--------|
| TYPE_001 | $1 Farmers Bank of Bucks County, Hulmeville PA (1810s obsolete) | YES | YES | PENDING | PENDING | Searching public-domain sources (NNC / NNP / Wikimedia). Auction listings are not ingestible. | - |
| TYPE_003 | $2 Confederate T-43 (1862 issue / commonly 1864 type) | NO | YES | N/A | PENDING | **Need Obv = NO. Need Rev = YES.** Wikimedia / National Numismatic Collection has a high-res **face** (credit-only; obverse is not a required side and does not complete this row). Reverse still unfound. Imagine pair in `AI Generated Downloads/` is `QUARANTINE_AI` and does **not** count as found. | National Numismatic Collection, Smithsonian — obverse reference only |
| TYPE_004 | $5 1907 Legal Tender Woodchopper PCBLIC engraving error (Fr. 91) | YES | YES | PENDING | PENDING | Error confirmed on reverse obligation (Fr. 91). Auction listings are `BLOCKED_NO_PUBLIC_LICENSE`. Imagine pair is `QUARANTINE_AI`. Hunt NNC / Wikimedia only. | - |
| TYPE_014 | $1 Federal Reserve Liars Note Six in a Row | YES | YES | PENDING | PENDING | Fancy-serial / 'liar's note' (six-in-a-row). Hunt public-domain type image; do not scrape auction photos of a specific serial. | - |
| TYPE_058 | $20 Federal Reserve inverted-back error (small size) | NO | YES | N/A | PENDING | Inverted-back error (FR1978 cited). True production error — P1. Public-domain type photo only; no Heritage. | - |
| TYPE_060 | $5 Federal Reserve Split Quad Note | YES | YES | PENDING | PENDING | Split-quad cutting error. Public-domain type photo only. | - |
| TYPE_115 | $5 1907 Legal Tender PCBLIC spelling-error reverse (Fr. 91 family) | YES | YES | PENDING | PENDING | Same PCBLIC / Fr. 91 error family as TYPE_004. Do not treat as a second complete pair if TYPE_004 is filled; still track both collection docs. | - |
| TYPE_127 | National Bank Note Type 1 Beatrice NE charter #2357 | YES | YES | PENDING | PENDING | - | - |
| TYPE_128 | $10 National bank note large size plainback | YES | YES | PENDING | PENDING | - | - |
| TYPE_129 | $10 National Bank Note Type 1 Newport NH $3404 | YES | YES | PENDING | PENDING | - | - |
| TYPE_130 | $20 National Bank Note Large size third issue (Plain back) | YES | YES | PENDING | PENDING | - | - |
| TYPE_131 | $20 National Bank Note T1 | YES | YES | PENDING | PENDING | - | - |
| TYPE_132 | $5 National Bank Note (1902) | YES | YES | PENDING | PENDING | - | - |
| TYPE_133 | $5 National Bank Note T2 | YES | YES | PENDING | PENDING | - | - |
| TYPE_134 | 19th Century Obsolete Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_135 | Obsolete Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_136 | $100 New York Marble Manufacturing obsolete (Haxby NY-1705-024) | YES | YES | PENDING | PENDING | - | - |
| TYPE_184 | Bank of New England, CT, uncut sheet W-CT-250 ($1/$1/$2/$5) | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. | - |
| TYPE_185 | 2 Continental Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_186 | #3 West River Bank Vermont Note Jamaica | YES | YES | PENDING | PENDING | Single West River Bank note (not the set/sheet). | - |
| TYPE_187 | 7 note set West Riverbank Jamaica VT | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. 7-note set. | - |
| TYPE_188 | $50 Confederate note (1864) | YES | YES | PENDING | PENDING | - | - |
| TYPE_191 | $1 Bank of Windsor, Vermont | NO | YES | N/A | PENDING | Need reverse only. | - |
| TYPE_192 | The West River Bank Jamaica Vermont Uncut sheet of 4 ($1, $2, $3, & $5) | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. $1, $2, $3, $5 subjects. | - |
| TYPE_193 | $1 Bank of America State of Rhode Island W_RI-820-001-00108 | YES | YES | PENDING | PENDING | - | - |
| TYPE_204 | Union County Bank, Plainfield NJ, uncut sheet of 4 | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. Uncut sheet of 4. | - |
| TYPE_205 | State Bank of New Brunswick $1 Uncut sheet of 4 | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. | - |
| TYPE_207 | $10 Canal Bank, New Orleans | YES | YES | PENDING | PENDING | Common remainder; prefer NNC / Wikimedia / NNP. | - |
| TYPE_208 | $10 Falls Village Iron Bank CT120G14C | NO | YES | N/A | PENDING | Catalog CT120G14C. Distinct from TYPE_214 / TYPE_215. Need reverse only. | - |
| TYPE_209 | $10 State of Georgia Note From Milledgeville | YES | YES | PENDING | PENDING | - | - |
| TYPE_210 | $1000 3rd Bank of the United States PMG New York Tear Repair Previously Mounted | NO | YES | N/A | PENDING | Same issuer family as TYPE_223 (Third Bank of the United States) but $1000 / New York. Need reverse only. Distinct work ID. | - |
| TYPE_211 | $2 New Orleans Jackson and Great Northern RR Co W-LA 380-002-G050 | YES | YES | PENDING | PENDING | - | - |
| TYPE_212 | $20 Confederate note (1864) | YES | YES | PENDING | PENDING | - | - |
| TYPE_213 | $40 continental currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_214 | $5 Falls Village Connecticut Iron Bank (CT120G8) | YES | YES | PENDING | PENDING | Catalog CT120G8. Do not share an image with TYPE_215. | - |
| TYPE_215 | $5 Falls Village Connecticut Iton Bank (CT120G10C) | YES | YES | PENDING | PENDING | Catalog CT120G10C. Do not share an image with TYPE_214. | - |
| TYPE_216 | $5, $10, and $20  Farmer's Bank of Kentucky three note set | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. $5 / $10 / $20. | - |
| TYPE_218 | $5 State of Louisiana Single Bond with red serial number | YES | YES | PENDING | PENDING | - | - |
| TYPE_223 | $500 Third Bank of the United States, Philadelphia (Haxby) | NO | YES | N/A | PENDING | Haxby Third Bank of the United States, Philadelphia $500. Need reverse only. | - |

## Priority 2: Gold & silver certificates, Educational Series, fractional, large-size legal tender, Treasury notes (84)

Same ingest rules. Large-size silver/gold and Educational Series often have NNC public-domain scans. Fractional is usually public domain.

| TYPE_ID | Description | Need Obv | Need Rev | Status Obv | Status Rev | Source / Notes | Credit |
|---------|-------------|----------|----------|------------|------------|----------------|--------|
| TYPE_071 | 5¢ Fractional Currency (1864–69) | NO | YES | N/A | PENDING | - | - |
| TYPE_072 | 10C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_073 | 10C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_074 | 10C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_075 | 10C Fractional currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_076 | 10C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_077 | 10C Fractional currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_078 | 15C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_079 | 15C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_080 | 2C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_081 | 25C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_082 | 25C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_083 | 25C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_084 | 5C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_085 | 5C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_086 | 50C Fractional currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_087 | 50C Fractional Currency | YES | YES | PENDING | PENDING | - | - |
| TYPE_088 | 50C Fractional Currency PMG EPQ CHUNC 63 | NO | YES | N/A | PENDING | - | - |
| TYPE_089 | $10 Gold Certificate Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_090 | $10 gold certificate large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_091 | $10 Gold Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_092 | $20 Gold Certificate large size (1906) | YES | YES | PENDING | PENDING | - | - |
| TYPE_093 | $20 Gold Certificate Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_094 | $20 Gold Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_095 | $50 gold certificate large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_097 | $1 Legal Tender Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_098 | $1 Legal Tender Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_100 | $10 Legal Tender Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_101 | $10 legal tender Note Bison | YES | YES | PENDING | PENDING | - | - |
| TYPE_103 | $2 Legal Tender Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_116 | $5 Legal Tender Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_137 | $! Silver certificate large size PCGS PPQ64 2 consecutive serial #s (FR238) | NO | YES | N/A | PENDING | - | - |
| TYPE_138 | 10 Silver Certificate Yellow Seal BA Block PMG EPQ65 | NO | YES | N/A | PENDING | - | - |
| TYPE_139 | 10 Silver Certificate Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_140 | 1 silver certificate Hawaii (FR2300) (SC Block) PMG CU64 EPQ | YES | YES | PENDING | PENDING | - | - |
| TYPE_141 | $1 Silver Certificate large size Fr. 237 (year 1823 is a typo for 1923) | YES | YES | PENDING | PENDING | - | - |
| TYPE_142 | $1 Silver Certificate Large Size Martha Washington | YES | YES | PENDING | PENDING | - | - |
| TYPE_143 | $1 Silver Certificate large size Educational | YES | YES | PENDING | PENDING | - | - |
| TYPE_144 | $1 silver certificate large size eagle | YES | YES | PENDING | PENDING | - | - |
| TYPE_145 | $1 Silver Certificate large size 2 consecutive Serial #s (FR237) PCGS | YES | YES | PENDING | PENDING | - | - |
| TYPE_146 | $1 Silver Certificate Funnyback | YES | YES | PENDING | PENDING | - | - |
| TYPE_147 | $1 Silver Certificate Funnyback | YES | YES | PENDING | PENDING | - | - |
| TYPE_148 | $1 Silver Certificate Funnyback | YES | YES | PENDING | PENDING | - | - |
| TYPE_149 | $1 Silver Certificate Funnyback | YES | YES | PENDING | PENDING | - | - |
| TYPE_150 | $1 Silver Certificate Funnyback | YES | YES | PENDING | PENDING | - | - |
| TYPE_151 | $1 silver certificatee funnyback | YES | YES | PENDING | PENDING | - | - |
| TYPE_152 | $1 silver certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_153 | $1 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_154 | $1 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_155 | $1 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_156 | $1 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_157 | $1 silver certificate wide design | YES | YES | PENDING | PENDING | - | - |
| TYPE_158 | $1 silver certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_159 | $1 silver certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_160 | $1 silver certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_161 | $1 Silver Certificate Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_162 | $1 silver cert star note | YES | YES | PENDING | PENDING | - | - |
| TYPE_163 | $1 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_164 | $1 silver certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_165 | $10 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_166 | $10 Silver Certificate - No Yellow Seal | YES | YES | PENDING | PENDING | - | - |
| TYPE_167 | $10 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_168 | $10 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_169 | $10 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_170 | $10 silver certificate Star note | YES | YES | PENDING | PENDING | - | - |
| TYPE_171 | $2 Silver Certificate large size Educational (1896) | YES | YES | PENDING | PENDING | - | - |
| TYPE_172 | $2 Silver Certificate Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_173 | $5 Silver Certificate Indian Large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_174 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_175 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_176 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_177 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_178 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_179 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_180 | $5 silver certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_181 | $5 Silver Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_182 | $! Treasury Note Large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_183 | $1 Treasury Note Large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_189 | Silver Certificate large size (1886) | YES | YES | PENDING | PENDING | - | - |
| TYPE_194 | $1 Silver Certificate large size Eagle (1899) | YES | YES | PENDING | PENDING | - | - |
| TYPE_195 | $1 large size note starter set | YES | YES | PENDING | PENDING | Sheet/set — see set/sheet rule. Mixed large-size starter set; child rows per type preferred. | - |
| TYPE_196 | $1 Silver Certificate large size (1923) | YES | YES | PENDING | PENDING | - | - |
| TYPE_217 | $5 Legal Tender large size (1880) PMG | NO | YES | N/A | PENDING | - | - |
| TYPE_224 | 5¢ Fractional Currency (1862–1869) | YES | YES | PENDING | PENDING | - | - |

## Priority 3: Federal Reserve Notes, Federal Reserve Bank Notes, small-size legal tender, MPC (101)

TYPE_005–TYPE_034 were pre-listed in the quarantined Heritage `currency_batch_01` manifest. That plan is **not** a sourcing path. Prefer NNC / Wikimedia / BEP for type images.

| TYPE_ID | Description | Need Obv | Need Rev | Status Obv | Status Rev | Source / Notes | Credit |
|---------|-------------|----------|----------|------------|------------|----------------|--------|
| TYPE_002 | $10 Federal Reserve Bank Note (1929) | YES | YES | PENDING | PENDING | - | - |
| TYPE_005 | Federal Reserve Bank Note Large size PMG | NO | YES | N/A | PENDING | - | - |
| TYPE_006 | $1 Federal Reserve Bank Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_007 | $10 Federal Reserve Bank Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_008 | $2 Federal Reserve Bank Note Large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_009 | $20 Federal Reserve Bank Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_010 | $5 Federal Reserve Bank Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_011 | Federal Reserve Note Hawaii LB Block PMG | NO | YES | N/A | PENDING | - | - |
| TYPE_012 | 1$ Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_013 | 1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_015 | $1 Federal Reserve Bamk Note large size PCGS 65PPQ | NO | YES | N/A | PENDING | - | - |
| TYPE_016 | $1 federal reserve star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_017 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_018 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_019 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_020 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_021 | $1 federal reserve note | YES | YES | PENDING | PENDING | - | - |
| TYPE_022 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_023 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_024 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_025 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_026 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_027 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_028 | $1 federal reserve  note | YES | YES | PENDING | PENDING | - | - |
| TYPE_029 | $1 federal reserve note | YES | YES | PENDING | PENDING | - | - |
| TYPE_030 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_031 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_032 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_033 | $1 federal reserve star note | YES | YES | PENDING | PENDING | - | - |
| TYPE_034 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_035 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_036 | $1 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_037 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_038 | $1 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_039 | $10 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_040 | $10 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_041 | $10 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_042 | $10 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_043 | $10 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_044 | $10 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_045 | $100 Federal Reserve note large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_046 | $100 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_047 | $14 Federal Reserve Note (1914) — denomination likely a typo for $10 or $20; keep as listed until collection doc is checked | YES | YES | PENDING | PENDING | - | - |
| TYPE_048 | $2 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_049 | $2 Federal Reserve Note dated 1978 — no 1978 $2 FRN series; likely 1976 | YES | YES | PENDING | PENDING | - | - |
| TYPE_050 | $2 Federal Reserve Note with courtsey signed Mary Ellen Withrow Autograph (FR193 | YES | YES | PENDING | PENDING | - | - |
| TYPE_051 | $2 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_052 | $2 Federal reserve star note | YES | YES | PENDING | PENDING | - | - |
| TYPE_053 | $2 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_054 | $2 federal reserve note | YES | YES | PENDING | PENDING | - | - |
| TYPE_055 | $20 Federal Reserve Red Seal Note Large size | YES | YES | PENDING | PENDING | - | - |
| TYPE_056 | $20 Federal Reserve Note Hawaii | YES | YES | PENDING | PENDING | - | - |
| TYPE_057 | $20 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_059 | $5 Federal Reserve Binary Repeated Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_061 | $5 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_062 | $5 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_063 | $5 Federal Reserve Note Hawaii | YES | YES | PENDING | PENDING | - | - |
| TYPE_064 | $5 federal reserve star note | YES | YES | PENDING | PENDING | - | - |
| TYPE_065 | $5 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_066 | $5 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_067 | $5 Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_068 | $50 Federal Reserve Note Large Size | YES | YES | PENDING | PENDING | - | - |
| TYPE_069 | $50 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_070 | $500 Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_096 | 5 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_099 | $1 Legal Tender Note Funny Back | YES | YES | PENDING | PENDING | - | - |
| TYPE_102 | $100 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_104 | $2 Legal Tender note | YES | YES | PENDING | PENDING | - | - |
| TYPE_105 | $2 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_106 | $2 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_107 | $2 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_108 | $2 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_109 | $2 legal tender note | YES | YES | PENDING | PENDING | - | - |
| TYPE_110 | $2 legal tender note | YES | YES | PENDING | PENDING | - | - |
| TYPE_111 | $2 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_112 | $2 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_113 | $2 legal tender note | YES | YES | PENDING | PENDING | - | - |
| TYPE_114 | $2 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_117 | $5 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_118 | $5 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_119 | $5 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_120 | $5 Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_121 | $5 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_122 | $5 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_123 | $5 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_124 | $5 Legal Tender Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_125 | $1 Military Payment Certificate (1969–70) | YES | YES | PENDING | PENDING | - | - |
| TYPE_126 | $5 Military Payment Certificate | YES | YES | PENDING | PENDING | - | - |
| TYPE_190 | $2 Legal Tender star note (1963) | YES | YES | PENDING | PENDING | - | - |
| TYPE_197 | $1Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_198 | $1Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_199 | $1Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_200 | $1 Federal Reserve Note (1969-D) | YES | YES | PENDING | PENDING | - | - |
| TYPE_201 | $1Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_202 | $1Federal Reserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_203 | $1 Federal Reserve star note (1999) | YES | YES | PENDING | PENDING | - | - |
| TYPE_206 | $1Federal Reserve Star Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_219 | $5 Federal Rserve Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_220 | $5 Legal Tender Note (1928-B) | YES | YES | PENDING | PENDING | - | - |
| TYPE_221 | $5Legal Tender Note | YES | YES | PENDING | PENDING | - | - |
| TYPE_222 | $5Legal Tender Note | YES | YES | PENDING | PENDING | - | - |

## Summary (2026-08-16)

- Complete real pairs (required sides, licensed photograph): **0**
- Partial licensed required sides: **0** (TYPE_003 NNC face is credit-only; obverse is not required)
- P1 remaining: **39**
- P2 remaining: **84**
- P3 remaining: **101**
- Unbucketed: **0** (`39 + 84 + 101 = 224`)
- Next actions: public-domain URL hunt for TYPE_004 / TYPE_115 reverse (Fr. 91 PCBLIC), TYPE_001 both sides, TYPE_003 reverse only; then remaining P1 obsolete/CSA/Continental; record source URL + license + credit; do not generate images; do not download Heritage/auction files.

**Last Updated:** 2026-08-16
