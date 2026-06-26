# Numista.AI Canonical Database Breakdown

To support the "Stump Numista.AI!" marketing campaign ("The most complete database of American coins and currency in the world!"), here is a complete breakdown of our canonical reference catalog.

## Quick Statistics

| Metric | Count | Coverage |
| --- | --- | --- |
| **Total Items in Catalog** | **11,928** | 100% |
| **Items with Rich History** | **11,786** | 98.8% |
| **Items with Obverse Images** | **262** | 2.2% |
| **Items with Reverse Images** | **232** | 1.9% |
| **AI Audited & Verified** | **11,928** | 100% |

> [!TIP]
> **Marketing Strategy: "Stump Numista.AI!"**
> With **98.8%** of the 11,928 items containing rich historical text (e.g., standard issue histories, unique privy mark details, minting background), Numista.AI's text engine is incredibly comprehensive! 
> 
> The current bottleneck for the "Stump Numista.AI!" campaign will be **Image Coverage** (currently hovering around 2%). To build a robust AI training board and confidently launch the campaign, we should focus beta testers on finding and reporting missing obverse/reverse images, prioritizing our structurally verified AI Audited dataset as our "gold standard" control group.

## Raw Data Export

You can download the full, row-by-row CSV breakdown for every single coin, banknote, and medal here: 
👉 [numista_marketing_breakdown.csv](file:///C:/Users/ericd/Documents/MyVertexProject/numista_backend/numista_marketing_breakdown.csv)

The CSV strictly maps the canonical schema and includes the following columns:
* **Category** (Coin, Note, Medal)
* **Series** (Programs - ex. America The Beautiful, 50 US States and Territory's, Morgan Dollars)
* **Denomination**
* **Year** (Strictly 4-digit mapping)
* **Mint Mark**
* **Variety**
* **Has History** (Yes/No)
* **Has Obverse Image** (Yes/No - based on actual `reference_library_export.csv` data)
* **Has Reverse Image** (Yes/No - based on actual `reference_library_export.csv` data)
* **AI_Audited_Status** (Yes)
