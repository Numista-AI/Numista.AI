"""
catalog_models.py
-----------------
Pydantic v2 contracts for the U.S. Numismatics Master Catalog (`us_numismatics_catalog`)
and the `catalog_snapshot` embedded in user collection documents.

Spec: Plan.v2 sections 2.3, 3.1, 3.2. Pure module (no Firebase imports).
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from catalog_nac1 import KIND_TO_COLLECTION, nac1_kind, validate_nac1

Kind = Literal["CN", "BN", "MD", "TK", "ST"]
Polity = Literal["US", "PF", "CS"]
PreciousMetal = Literal["SILVER", "GOLD", "PLATINUM", "PALLADIUM", "NONE"]
Face = Literal["OBVERSE", "REVERSE"]


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
        # Hard ingestion rule (Plan.v2 2.3): fineness != null => explicit precious metal, never NONE.
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
    country_era: Literal["PRE_FEDERAL", "EARLY_FEDERAL", "FEDERAL", "CONFEDERATE", "US_PHILIPPINES"]
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
    image_source_credit: Optional[str] = None
    image_license_type: Literal["CC0", "US_GOV_PUBLIC_DOMAIN", "INSTITUTIONAL_PERMISSION", "NONE"] = "NONE"

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
        if self.mint_mark_on_coin and not self.mint_mark:
            raise ValueError("mint_mark required when mint_mark_on_coin is true")
        if not self.mint_mark_on_coin and self.mint_mark is not None:
            raise ValueError("mint_mark must be null when mint_mark_on_coin is false")
        return self

    @property
    def target_collection(self) -> str:
        return KIND_TO_COLLECTION[self.kind]


class CollectionAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nac_code: str
    new_specimen: bool = False  # True => allocate next free _SLOT{N}; False => idempotent _SLOT1


def build_catalog_snapshot(item: dict) -> dict:
    """Immutable 'as-of' snapshot embedded in user docs (Plan.v2 3.2 item 3)."""
    return {
        "catalog_version": item.get("catalog_version", 1),
        "title_at_acquire": item.get("title"),
        "mintage_official_at_acquire": item.get("mintage_official_mint"),
        "obverse_image_url_at_acquire": item.get("obverse_image_url"),
    }
