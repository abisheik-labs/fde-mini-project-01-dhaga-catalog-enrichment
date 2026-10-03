"""
Pydantic schemas for the Dhaga & Co. Cataloging Pipeline.
Enforces structured outputs across every model and deterministic boundary.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ListingStatus(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
    SPECS_STAGED = "SPECS_STAGED"


class DepartmentEnum(str, Enum):
    WOMENSWEAR = "Womenswear"
    KIDSWEAR = "Kidswear"
    MENSWEAR = "Menswear"
    UNKNOWN = "Unknown"

class RawVendorInput(BaseModel):
    sku_id: str = Field(description="Unique SKU identifier (e.g. DHG-101)")
    vendor_location: str = Field(description="Vendor hub: Tiruppur or Jaipur")
    raw_title: str = Field(description="Raw title provided by vendor")
    raw_category: str = Field(description="Unstructured category string")
    raw_color: str = Field(description="Messy color name typed by vendor")
    raw_fabric: str = Field(description="Free-text fabric specification")
    raw_price: float = Field(description="Wholesale/retail listing price in INR")
    vendor_notes: Optional[str] = Field(default="", description="Vendor comments, care notes, occasions")

class CategoryRoutingResult(BaseModel):
    department: DepartmentEnum = Field(description="Standardized department: Womenswear, Kidswear, Menswear, or Unknown")
    sub_category: str = Field(description="Normalized garment sub-category (e.g., Kurti, Polo T-Shirt, Frock, Saree)")
    clean_fabric: str = Field(description="Standardized fabric description extracted from free text")
    extracted_raw_color: str = Field(description="Primary color string isolated for normalization")

class ColorNormalizationResult(BaseModel):
    original_color: str = Field(description="Input raw color string")
    canonical_color: str = Field(description="One of the 16 canonical colors, or UNMAPPED_AMBIGUOUS")
    confidence: float = Field(description="Match confidence score between 0.0 and 1.0")
    is_canonical: bool = Field(description="True if successfully mapped to canonical taxonomy")

class GeneratedCopy(BaseModel):
    seo_title: str = Field(
        description=(
            "Customer-focused SEO title in the format "
            "'Product or Style | Canonical Color | Fabric'. "
            "Omit unavailable attributes; exclude brand, price, and occasion phrases."
        )
    )
    bullet_highlights: List[str] = Field(description="3 to 4 key garment highlights")
    hinglish_occasion_tags: List[str] = Field(
        description=(
            "2 to 4 concise Hinglish search tags relevant to the exact garment and supported "
            "by vendor title, category, or notes. Do not invent occasions or infer them from "
            "color or fabric; use broad everyday-use terms when context has no specific occasion."
        )
    )
    wash_care: str = Field(description="Practical wash instructions based on fabric")
    product_description: str = Field(description="Two-sentence appealing, natural brand description")

class EvaluatorResult(BaseModel):
    is_valid: bool = Field(description="True if output passes schema and consistency checks")
    confidence_score: float = Field(description="Overall reliability score (0.0 to 1.0)")
    has_fabric_contradiction: bool = Field(default=False, description="True if conflicting fabric claims exist (e.g., denim silk)")
    has_impossible_care: bool = Field(default=False, description="True if care instructions are contradictory or absurd")
    review_reasons: List[str] = Field(default_factory=list, description="Explanations for why item requires human review")

class ListingItemOutput(BaseModel):
    sku_id: str
    vendor_location: str
    raw_title: Optional[str] = ""
    raw_category: Optional[str] = ""
    raw_fabric: Optional[str] = ""
    vendor_notes: Optional[str] = ""
    department: str
    sub_category: str
    original_color: str
    canonical_color: str
    fabric: str
    price: float
    seo_title: str
    bullet_highlights: List[str]
    hinglish_occasion_tags: List[str]
    wash_care: str
    product_description: str
    status: ListingStatus
    review_reasons: List[str] = Field(default_factory=list)
