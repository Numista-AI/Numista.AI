# DESK NOTE - NET-751 - Argon scored NET-748 CoS v3 (FINAL, attempt 10 of 10): 92/100
Filed by Antigravity Desk, 3 Nov 2026 12:20 PM ET

BLUF: GB CoS's v3 fail-fix plan scored 92, below the 95 pass mark. Not staged for Eric YES. SAG has not scored it yet.

Review: INBOX\ARGON_REVIEW_NET-748_CoS_v3.md (12:06 ET, also on RADIO NET as GEMINI38_REVIEW_NET-748_CoS_v3_2026-11-03.md). MD5 sidecar matches.

What Argon liked: all image paths checked live (200), year fix covers 2026.0 and 2023.0, compile errors and made-up SKUs gone, Mayflower block and 45 tests untouched.

3 must-fixes:
- MF-v3-1 (critical): firestore.rules match paths are missing the leading /global_metadata segment (code reads global_metadata/usmint_sku_dictionary/skus and global_metadata/littleton_sku_dictionary/skus).
- MF-v3-2 (high): CoinImageService calls resolve() with no sku, so 2026 Morgan, Peace, Silver Eagle, 26SQRP and sets all return null. Infer sku when empty, and call resolveFromMap first on collection and detail screens.
- MF-v3-3 (high): extractSku condition uses ?? so 'Ungraded' hides Variety/Strike Type; the 26EA rule needs the 'proof' requirement dropped (keep the gold/platinum/palladium exclusion).

Decision for CoS: this was attempt 10 of 10. Standing rule (2 Nov) says notify Eric and break the work into smaller chunks. The fast-track rule (90+ then above 91 allows a fix-only 3rd pass) may also apply. CoS decides; Desk does not score or approve.
Locks unchanged: main 9f04550a, no deploys.
