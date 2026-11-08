## 5 Nov update: Mint product fields (plan only, not folded into production)
Source: SCHEMA_DIFF_product_price_mint_schedule_20261105.json. All optional.
- product_price_usd: show on detail view only, labeled "U.S. Mint issue price" (never "value" or market price). Hide when null. Not on cards.
- mint_schedule_status / product_availability: prefer mint_schedule_status. Detail view only, neutral gray text. Hide when null or UNKNOWN. No buy links, no urgency wording.
- release_time_et: show with release_date only when both are set (e.g. "Nov 12, 2026, noon ET").
- These 4 fields go on the publish allow-list only after the normal route (Argon, CoS 95+, SAG, Eric's YES). Until then they are dropped by default.
