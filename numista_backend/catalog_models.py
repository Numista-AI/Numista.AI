"""
catalog_models.py
-----------------
Pydantic v2 contracts for the U.S. Numismatics Master Catalog (`us_numismatics_catalog`)
and the `catalog_snapshot` embedded in user collection documents.

Spec: Plan.v2.1 sections 2.3, 3.1, 3.2. Pure module (no Firebase imports).
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from catalog_nac1 import KIND_TO_COLLECTION, nac1_cc, nac1_kind, validate_nac1

Kind = Literal["CN", "BN", "MD", "TK", "ST"]
Polity = Literal["US", "CO", "PF", "CS", "FS"]
CountryEra = Literal[
    "PRE_FEDERAL",
    "EARLY_FEDERAL",
    "FEDERAL",
    "CONFEDERATE",
    "US_PHILIPPINES",
    "FOREIGN_CIRCULATING",
]
PreciousMetal = Literal["SILVER", "GOLD", "PLATINUM", "PALLADIUM", "NONE"]
Face = Literal["OBVERSE", "REVERSE"]
ImageTier = Literal["MUSEUM", "PUBLIC_DOMAIN", "VERIFIED_COMMUNITY", "NONE"]
ImageLicense = Literal[
    "CC0",
    "US_GOV_PUBLIC_DOMAIN",
    "INSTITUTIONAL_PERMISSION",
    "COMMUNITY_VERIFIED_CC0",
    "NONE",
]


class Specifications(BaseModel):
    model_config = ConfigDict(extra="forbid")

    designer_obverse: Optional[str] = None
    designer_reverse: Optional[str] = None
    composition: str
    fineness: Optional[float] = None
    precious_metal_type: PreciousMetal = "NONE"
    actual_metal_weight_oz: Optional[float] = None
    weight_grams: Optional[float] = None
    diameter_mm: Optional[float] = None
    height_mm: Optional[float] = None
    edge: Optional[str] = None
    alignment: Literal["COIN", "MEDAL", "NOTE"]

    @model_validator(mode="after")
    def _fineness_requires_metal(self):
        # Hard ingestion rule (Plan.v2.1 2.3): fineness != null => explicit precious metal, never NONE.
        if self.fineness is not None and self.precious_metal_type == "NONE":
            raise ValueError("precious_metal_type must be SILVER|GOLD|PLATINUM|PALLADIUM when fineness is set")
        return self


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tier: Literal["TIER_A_GOV", "TIER_B_ACADEMIC"]
    source_name: str
    citation_text: str
    document_url: Optional[str] = None
    verified_date: str


class CatalogItem(BaseModel):
    model_config = ConfigDict(extra="allow")  # forward-compatible with later catalog_version fields

    nac_code: str
    nac_aliases: List[str] = Field(default_factory=list)
    seo_slug: str
    kind: Kind
    cc: Polity
    country_era: CountryEra
    state_or_entity: Optional[str] = None
    denomination_class: str
    series: str
    catalog_version: int = 1
    last_verified_at: str

    year: int = Field(ge=1776, le=2026)
    year_display: str
    facility_code: str
    mint_mark_on_coin: bool
    mint_mark: Optional[str] = None
    facility_note: Optional[str] = None
    title: str
    subtitle: str = ""

    default_face: Face = "OBVERSE"
    obverse_image_url: Optional[str] = None
    reverse_image_url: Optional[str] = None
    has_obverse_image: bool = False
    has_reverse_image: bool = False
    image_tier: ImageTier = "NONE"
    image_source_credit: Optional[str] = None
    image_license_type: ImageLicense = "NONE"

    mintage_official_mint: Optional[int] = None
    mintage_commercial: Optional[int] = None
    mintage_proof: Optional[int] = None
    mintage_estimated: bool = False
    mintage_reconciliation_note: Optional[str] = None

    specifications: Specifications
    concordance: dict = Field(default_factory=dict)
    primary_citations: List[Citation]

    @field_validator("nac_code")
    @classmethod
    def _valid_nac(cls, v):
        if not validate_nac1(v):
            raise ValueError("INVALID_NAC1_CHECKSUM")
        return v

    @field_validator("primary_citations")
    @classmethod
    def _needs_citation(cls, v):
        if not v:
            raise ValueError("at least one primary citation is required to publish")
        return v

    @model_validator(mode="after")
    def _consistency(self):
        if nac1_kind(self.nac_code) != self.kind:
            raise ValueError("kind does not match NAC1 KIND segment")
        if nac1_cc(self.nac_code) != self.cc:
            raise ValueError("cc does not match NAC1 CC segment")
        if self.mint_mark_on_coin and not self.mint_mark:
            raise ValueError("mint_mark required when mint_mark_on_coin is true")
        if not self.mint_mark_on_coin and self.mint_mark is not None:
            raise ValueError("mint_mark must be null when mint_mark_on_coin is false")

        # Plan.v2.2 §2.3.1 (SAG #1 / GB MUST-EDIT 4): CC <-> country_era <-> year & facility agreement
        if self.cc == "CO":
            if self.country_era != "PRE_FEDERAL" or not (1776 <= self.year <= 1792):
                raise ValueError("CC=CO requires country_era=PRE_FEDERAL and year in 1776..1792")
            if self.facility_code in {"M", "PH", "MO", "L", "PTS"}:
                raise ValueError(f"Invalid facility_code {self.facility_code} for CC=CO")
        elif self.cc == "PF":
            if self.country_era != "US_PHILIPPINES" or not (1903 <= self.year <= 1946):
                raise ValueError("CC=PF requires country_era=US_PHILIPPINES and year in 1903..1946")
            if self.facility_code not in {"P", "D", "S", "M", "PH"}:
                raise ValueError(f"Invalid facility_code {self.facility_code} for CC=PF")
        elif self.cc == "CS":
            if self.country_era != "CONFEDERATE" or not (1861 <= self.year <= 1865):
                raise ValueError("CC=CS requires country_era=CONFEDERATE and year in 1861..1865")
        elif self.cc == "FS":
            if self.country_era != "FOREIGN_CIRCULATING" or not (1776 <= self.year <= 1857):
                raise ValueError("CC=FS requires country_era=FOREIGN_CIRCULATING and year in 1776..1857")
            if self.facility_code not in {"MO", "L", "PTS", "XX"}:
                raise ValueError(
                    f"Invalid facility_code {self.facility_code} for CC=FS (use MO for Mexico City, never M=Manila)"
                )
        elif self.cc == "US":
            if self.country_era not in {"EARLY_FEDERAL", "FEDERAL"} or not (1792 <= self.year <= 2026):
                raise ValueError("CC=US requires country_era in {EARLY_FEDERAL, FEDERAL} and year in 1792..2026")
            if self.facility_code in {"M", "PH", "MO", "L", "PTS"}:
                raise ValueError(f"Invalid facility_code {self.facility_code} for CC=US")

        # Plan.v2.2 §2.3.2 (SAG #4 / S3 / GB MUST-EDIT 3): Tier-A mintage authority validator
        if self.mintage_official_mint is not None:
            tier_a_cites = [c for c in self.primary_citations if c.tier == "TIER_A_GOV"]
            if not tier_a_cites:
                raise ValueError(
                    f"{self.nac_code}: mintage_official_mint requires at least one TIER_A_GOV citation"
                )
            forbidden_tokens = (
                "pcgs", "coinfacts", "ngc", "ngccoin", "red book", "redbook",
                "yeoman", "whitman", "greysheet", "numista.com", "heritage", "ha.com", "cointrackers",
            )
            allowed_authorities = (
                "mint", "treasury", "bureau of engraving", "bep", "fraser",
                "national archives", "nara", "statutes at large", "act of", "congress",
            )
            for c in tier_a_cites:
                combined = f"{c.source_name} {c.citation_text} {c.document_url or ''}".lower()
                if any(bad in combined for bad in forbidden_tokens):
                    raise ValueError(
                        f"{self.nac_code}: Commercial source '{c.source_name}' forbidden as TIER_A_GOV citation"
                    )
                if not any(auth in combined for auth in allowed_authorities):
                    raise ValueError(
                        f"{self.nac_code}: TIER_A_GOV citation '{c.source_name}' must cite official Mint/Treasury/BEP/NARA authority"
                    )

        # Plan.v2.2 §2.3.3 (SAG #9 / S5 / GB MUST-EDIT 7): Zero user PII in public catalog docs
        if self.image_source_credit:
            credit_lower = self.image_source_credit.lower()
            if (
                "@" in credit_lower
                or "verified contributor:" in credit_lower
                or "uid:" in credit_lower
                or "user_" in credit_lower
            ):
                raise ValueError(
                    f"{self.nac_code}: Public image_source_credit must not contain user PII or handles"
                )
        return self

    @property
    def target_collection(self) -> str:
        return KIND_TO_COLLECTION[self.kind]


class CollectionAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Rejects client-supplied kind, slot, or tier

    nac_code: str
    new_specimen: bool = False  # True => allocate next free _SLOT{N}; False => idempotent _SLOT1
    idempotency_key: Optional[str] = None


class PhotoToggleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collection: Literal["coins", "currency", "world_items"]
    doc_id: str
    use_personal_photo: bool


def build_catalog_snapshot(item: dict) -> dict:
    """Immutable 'as-of' snapshot embedded in user docs (Plan.v2.1 3.2 item 3)."""
    return {
        "catalog_version": item.get("catalog_version", 1),
        "title_at_acquire": item.get("title"),
        "mintage_official_at_acquire": item.get("mintage_official_mint"),
        "obverse_image_url_at_acquire": item.get("obverse_image_url"),
        "reverse_image_url_at_acquire": item.get("reverse_image_url"),
    }
