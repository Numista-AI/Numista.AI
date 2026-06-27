"""
estate_state_rules.py — State-specific estate planning rules for Numista.AI

Covers: NY, NC, NJ, FL, CA, TX, SC

Each entry contains filing deadlines, tax rules, TPP memo status, probate
form codes, and human-readable notes surfaced in PDF reports.
"""

# All dollar values are in USD; rates are decimals (0.11 = 11%).
STATE_RULES: dict[str, dict] = {

    # ──────────────────────────────────────────────────────────────────────────
    # NEW YORK — Estate tax state. Cliff rule. NO TPP memo. 9-month deadline.
    # ──────────────────────────────────────────────────────────────────────────
    'NY': {
        'display_name': 'New York',
        'estate_tax': True,
        'exemption_2026': 7_350_000.0,          # NY basic exclusion amount (2026)
        'cliff_rule': True,                       # NY "cliff": if estate > 105% of exemption,
        'cliff_multiplier': 1.05,                 #   ENTIRE estate is taxable, not just excess
        'inheritance_tax': False,
        'inheritance_tax_classes': None,
        'tpp_memo_allowed': False,                # Bequests MUST be in the Will itself
        'tpp_memo_capped': False,
        'tpp_memo_cap_per_item': None,
        'tpp_memo_cap_total': None,
        'tpp_memo_risk': False,
        'probate_form': 'NY Inventory of Assets',
        'probate_form_code': '22 NYCRR §207.20',
        'filing_deadline_days': 270,              # 9 months from date of death
        'filed_with': 'Surrogate\'s Court (County of domicile)',
        'community_property': False,
        'inventory_confidential': False,
        'dor_reporting_threshold': None,
        'governing_statute': 'SCPA §2102; EPTL §4-1.1; 22 NYCRR §207.20',
        'tpp_memo_statute': None,
        'report_deadline_warning': '270 days (9 months) from date of death — same as ET-706 NY estate tax return',
        'coins_in_statute': False,
        'special_notes': [
            'No TPP memorandum has legal force in NY — bequests must be in the Will itself',
            'ET-706 NY estate tax return required if gross estate exceeds $7,350,000',
            'CLIFF RULE: If gross estate exceeds 105% of the exemption ($7,717,500), the '
            'ENTIRE estate is subject to NY estate tax — not just the excess above the exemption',
            '3-year gift clawback: gifts made within 3 years of death are added back to the '
            'estate for purposes of the cliff calculation',
            'IRS appraisal required for any single item or group of similar items with '
            'FMV > $3,000 (IRC §170(f)(11)); required for Form 706 (federal) and ET-706 (NY)',
            'Executor appointed by Surrogate\'s Court; Letters Testamentary required before '
            'filing inventory',
            'NY does not follow community property rules — step-up applies only to decedent\'s '
            'share of jointly held property',
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # NORTH CAROLINA — No estate tax. TPP memo allowed. 90-day deadline.
    # ──────────────────────────────────────────────────────────────────────────
    'NC': {
        'display_name': 'North Carolina',
        'estate_tax': False,
        'exemption_2026': None,
        'cliff_rule': False,
        'cliff_multiplier': 1.0,
        'inheritance_tax': False,
        'inheritance_tax_classes': None,
        'tpp_memo_allowed': True,
        'tpp_memo_capped': False,
        'tpp_memo_cap_per_item': None,
        'tpp_memo_cap_total': None,
        'tpp_memo_risk': False,
        'probate_form': 'Inventory and Accounts',
        'probate_form_code': 'AOC-E-505',
        'filing_deadline_days': 90,
        'filed_with': 'Clerk of Superior Court (County of domicile)',
        'community_property': False,
        'inventory_confidential': False,
        'dor_reporting_threshold': None,
        'governing_statute': 'NCGS §28A-20-1; NCGS §31-3.10',
        'tpp_memo_statute': 'NCGS §31-3.10',
        'report_deadline_warning': '90 days from appointment of Personal Representative',
        'coins_in_statute': False,
        'special_notes': [
            'NC allows a separately signed and dated TPP memorandum incorporated by reference '
            'into the Will — a powerful planning tool for coin collectors',
            'Coins should be individually itemized — not grouped as "misc coin collection" — '
            'to support both the probate inventory and any TPP memo bequests',
            'NC has no state estate tax and no inheritance tax — federal only',
            'Inventory must be filed within 90 days of Letters Testamentary/Administration',
            'AOC-E-505 is the standard form; Clerk of Superior Court in the county of domicile',
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # NEW JERSEY — No estate tax (post-2017). Inheritance tax still active.
    # Physical situs rule. Tax waiver freeze.
    # ──────────────────────────────────────────────────────────────────────────
    'NJ': {
        'display_name': 'New Jersey',
        'estate_tax': False,
        'exemption_2026': None,
        'cliff_rule': False,
        'cliff_multiplier': 1.0,
        'inheritance_tax': True,
        'inheritance_tax_classes': {
            'A': 0.0,   # Spouse, parents, children, grandchildren — exempt
            'C': 0.11,  # Siblings, sons/daughters-in-law — 11–16% (use 11% as base)
            'D': 0.15,  # Friends, cousins, nephews, unrelated — 15–16% from dollar #1 above $499
            'E': 0.0,   # Charitable organizations — exempt
        },
        'tpp_memo_allowed': True,
        'tpp_memo_capped': False,
        'tpp_memo_cap_per_item': None,
        'tpp_memo_cap_total': None,
        'tpp_memo_risk': False,
        'probate_form': 'County Surrogate Inventory + IT-R',
        'probate_form_code': 'IT-R (Inheritance Tax Return)',
        'filing_deadline_days': 90,               # Surrogate inventory: 90 days
        'filed_with': 'County Surrogate\'s Court + NJ Division of Taxation',
        'community_property': False,
        'inventory_confidential': False,
        'dor_reporting_threshold': None,
        'governing_statute': 'N.J.S.A. 54:34-2; N.J.S.A. 3B:10-3',
        'tpp_memo_statute': 'N.J.S.A. 3B:3-11',
        'report_deadline_warning': 'Surrogate inventory: 90 days. IT-R Inheritance Tax Return: 8 months (240 days) from date of death.',
        'coins_in_statute': False,
        'special_notes': [
            'NJ inheritance tax is paid by the BENEFICIARY — rate depends on their '
            'relationship class to the decedent',
            'Class A (spouse, children, grandchildren, parents): 0% — fully exempt',
            'Class C (siblings, sons/daughters-in-law): 11–16% based on amount',
            'Class D (friends, cousins, nephews, unrelated parties): 15–16% starting '
            'at dollar #1 above $499',
            'Class E (qualifying charities): 0% — fully exempt',
            'PHYSICAL SITUS RULE: coins physically located in NJ are subject to NJ '
            'inheritance tax regardless of where the decedent resided',
            'TAX WAIVER FREEZE: estate cannot distribute coins to non-Class-A beneficiaries '
            'until NJ Division of Taxation issues official tax waivers',
            'IT-R (Inheritance Tax Return) is due 8 months from date of death; a 4-month '
            'extension may be requested',
            'NJ requires individual professional appraisal of coins for IT-R purposes',
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # FLORIDA — No estate tax. Shortest deadline (60 days). Confidential inventory.
    # ──────────────────────────────────────────────────────────────────────────
    'FL': {
        'display_name': 'Florida',
        'estate_tax': False,
        'exemption_2026': None,
        'cliff_rule': False,
        'cliff_multiplier': 1.0,
        'inheritance_tax': False,
        'inheritance_tax_classes': None,
        'tpp_memo_allowed': True,
        'tpp_memo_capped': False,
        'tpp_memo_cap_per_item': None,
        'tpp_memo_cap_total': None,
        'tpp_memo_risk': False,
        'probate_form': 'Verified Inventory',
        'probate_form_code': 'F.S. §733.604',
        'filing_deadline_days': 60,               # SHORTEST deadline of all 7 states
        'filed_with': 'Circuit Court (Probate Division), County of domicile',
        'community_property': False,
        'inventory_confidential': True,            # FL probate inventories are NOT public record
        'dor_reporting_threshold': None,
        'governing_statute': 'F.S. §733.604; F.S. §732.515',
        'tpp_memo_statute': 'F.S. §732.515',
        'report_deadline_warning': 'CRITICAL: Only 60 days from Letters of Administration — the shortest deadline of all supported states.',
        'coins_in_statute': False,
        'special_notes': [
            'FL has the SHORTEST deadline of all supported states: 60 days from Letters '
            'of Administration — act immediately',
            'FL probate inventories are CONFIDENTIAL — exempt from public records requests '
            '(unlike most other states)',
            'Surviving spouse may claim a 30% elective share of the "elective estate," '
            'which includes revocable trust assets — coin collections held in trust are included',
            'FL Community Property Trust Act (F.S. §736.1501) allows married couples to opt '
            'into community property treatment for double step-up basis benefits',
            'No FL state estate or inheritance tax; federal estate tax applies if estate '
            'exceeds federal exemption',
            'Formal vs. summary administration: estates under $75,000 (exclusive of exempt '
            'property) may qualify for summary administration with shorter timeline',
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # CALIFORNIA — Community property. TPP memo CAPPED at $5K/$25K. RLT strongly recommended.
    # ──────────────────────────────────────────────────────────────────────────
    'CA': {
        'display_name': 'California',
        'estate_tax': False,
        'exemption_2026': None,
        'cliff_rule': False,
        'cliff_multiplier': 1.0,
        'inheritance_tax': False,
        'inheritance_tax_classes': None,
        'tpp_memo_allowed': True,
        'tpp_memo_capped': True,
        'tpp_memo_cap_per_item': 5_000.0,
        'tpp_memo_cap_total': 25_000.0,
        'tpp_memo_risk': False,
        'probate_form': 'Inventory and Appraisal',
        'probate_form_code': 'DE-160',
        'filing_deadline_days': 120,              # 4 months from appointment of executor
        'filed_with': 'Superior Court (Probate Department), County of domicile',
        'community_property': True,
        'inventory_confidential': False,
        'dor_reporting_threshold': None,
        'governing_statute': 'Cal. Prob. Code §8800; Cal. Prob. Code §6132',
        'tpp_memo_statute': 'Cal. Prob. Code §6132',
        'report_deadline_warning': '120 days (4 months) from appointment of personal representative',
        'coins_in_statute': False,
        'special_notes': [
            'CA TPP memo is CAPPED at $5,000 per item and $25,000 total — nearly useless '
            'for serious collectors with high-value coins',
            'COMMUNITY PROPERTY: coins purchased with marital funds are 50% owned by each '
            'spouse; separate property coins (pre-marriage, gift, inheritance) are excluded',
            'DOUBLE STEP-UP: Under IRC §1014(b)(6), the ENTIRE community property coin '
            'collection (both halves) steps up to FMV at death — a major tax benefit',
            'CA probate costs are STATUTORY: approximately 4% of first $100K, 3% of next '
            '$100K, etc. — a Revocable Living Trust (RLT) is strongly recommended to avoid '
            'probate entirely for valuable coin collections',
            'Independent expert appraiser preferred over Probate Referee for coin collections '
            '(Cal. Prob. Code §8904) — request appointment at time of petition',
            'No CA state estate or inheritance tax; federal estate tax applies if estate '
            'exceeds federal exemption',
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # TEXAS — Community property. TPP memo risky without holographic Will.
    #         ONLY state to name "coin collections" in statute.
    # ──────────────────────────────────────────────────────────────────────────
    'TX': {
        'display_name': 'Texas',
        'estate_tax': False,
        'exemption_2026': None,
        'cliff_rule': False,
        'cliff_multiplier': 1.0,
        'inheritance_tax': False,
        'inheritance_tax_classes': None,
        'tpp_memo_allowed': True,
        'tpp_memo_capped': False,
        'tpp_memo_cap_per_item': None,
        'tpp_memo_cap_total': None,
        'tpp_memo_risk': True,                    # No independent legal force without holographic drafting
        'probate_form': 'Ch. 309 Inventory',
        'probate_form_code': 'TX Estates Code §309.051',
        'filing_deadline_days': 90,
        'filed_with': 'Probate Court (County Court at Law or District Court), County of domicile',
        'community_property': True,
        'inventory_confidential': False,
        'dor_reporting_threshold': None,
        'governing_statute': 'TX Estates Code §309.051; TX Estates Code §255.001',
        'tpp_memo_statute': 'TX Estates Code §255.001 (implicit/holographic only)',
        'report_deadline_warning': '90 days from qualification of executor or administrator',
        'coins_in_statute': True,                 # TX explicitly names coin collections
        'special_notes': [
            'UNIQUE DISTINCTION: Texas is the only state to explicitly name "coin collections" '
            'in its tangible personal property statute (TX Estates Code §255.001)',
            'COMMUNITY PROPERTY DOUBLE STEP-UP: the entire community property coin collection '
            '(both spouses\' halves) steps up to FMV at death under IRC §1014(b)(6)',
            'TPP MEMO RISK: a TPP memorandum has no independent legal force in TX without '
            'either (a) holographic Will drafting or (b) express incorporation by reference '
            'into the Will at time of execution — consult TX estate attorney',
            'INDEPENDENT ADMINISTRATION: TX executors have broad authority to manage and '
            'sell estate assets without court approval (a significant advantage)',
            'BLENDED FAMILY RISK: under TX intestacy rules, decedent\'s 50% of community '
            'property passes to children (including from prior marriages), NOT to surviving '
            'spouse — explicit Will required to address this',
            'No TX state estate or inheritance tax; federal estate tax applies if estate '
            'exceeds federal exemption',
        ],
    },

    # ──────────────────────────────────────────────────────────────────────────
    # SOUTH CAROLINA — No estate/inheritance tax. $600K DOR trigger. TPP memo allowed.
    # ──────────────────────────────────────────────────────────────────────────
    'SC': {
        'display_name': 'South Carolina',
        'estate_tax': False,
        'exemption_2026': None,
        'cliff_rule': False,
        'cliff_multiplier': 1.0,
        'inheritance_tax': False,
        'inheritance_tax_classes': None,
        'tpp_memo_allowed': True,
        'tpp_memo_capped': False,
        'tpp_memo_cap_per_item': None,
        'tpp_memo_cap_total': None,
        'tpp_memo_risk': False,
        'probate_form': 'Inventory and Appraisement',
        'probate_form_code': 'Form 350ES',
        'filing_deadline_days': 90,
        'filed_with': 'Probate Court, County of domicile',
        'community_property': False,
        'inventory_confidential': False,
        'dor_reporting_threshold': 600_000.0,     # Court MUST send copy to SC DOR above this
        'governing_statute': 'SC Code Ann. §62-3-705; SC Code Ann. §62-2-512',
        'tpp_memo_statute': 'SC Code Ann. §62-2-512',
        'report_deadline_warning': '90 days from appointment of Personal Representative. If gross probate assets ≥ $600,000, a copy of the inventory is automatically forwarded to the SC Department of Revenue.',
        'coins_in_statute': False,
        'special_notes': [
            '$600K DOR TRIGGER: if gross probate assets equal or exceed $600,000, the Probate '
            'Court MUST send a copy of the inventory to the SC Department of Revenue — '
            'this is automatic and cannot be waived',
            'No community property in SC — step-up in basis applies only to the decedent\'s '
            'proportionate inherited share, not the entire collection',
            'TPP memo is allowed with NO dollar caps (unlike CA\'s $5K/$25K limits) — '
            'an excellent option for SC coin collectors with multiple beneficiaries',
            'Professional numismatic appraisal strongly recommended; appraisers holding '
            'ISA (International Society of Appraisers) or ASA (American Society of Appraisers) '
            'credentials preferred for court and tax purposes',
            'No SC state estate or inheritance tax; federal estate tax applies if estate '
            'exceeds federal exemption',
        ],
    },
}


def get_state_rules(state_code: str) -> dict:
    """
    Return state rules dict for a given two-letter state code.
    Raises KeyError if state is not supported.
    """
    code = state_code.upper().strip()
    if code not in STATE_RULES:
        supported = ', '.join(sorted(STATE_RULES.keys()))
        raise KeyError(
            f"State '{code}' is not supported. Supported states: {supported}"
        )
    return STATE_RULES[code]


def get_supported_states() -> list[str]:
    """Return sorted list of supported state codes."""
    return sorted(STATE_RULES.keys())
