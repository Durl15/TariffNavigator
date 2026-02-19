"""
Calculation Management Schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============================================================================
# CALCULATION REQUEST SCHEMAS
# ============================================================================

class CalculationSaveRequest(BaseModel):
    """Schema for saving a new calculation with metadata"""
    # Metadata fields
    name: str = Field(..., min_length=1, max_length=255, description="User-friendly name for the calculation")
    description: Optional[str] = Field(None, description="Optional description or notes")
    tags: Optional[List[str]] = Field(None, max_length=20, description="List of tags for categorization")

    # Calculation data fields
    hs_code: str = Field(..., min_length=4, max_length=20, description="HS code")
    product_description: Optional[str] = Field(None, description="Product description")
    origin_country: str = Field(..., min_length=2, max_length=2, description="Origin country code")
    destination_country: str = Field(..., min_length=2, max_length=2, description="Destination country code")
    cif_value: Decimal = Field(..., description="CIF value")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code")
    result: Dict[str, Any] = Field(..., description="Full calculation result object")
    total_cost: Decimal = Field(..., description="Total cost")
    customs_duty: Optional[Decimal] = Field(None, description="Customs duty amount")
    vat_amount: Optional[Decimal] = Field(None, description="VAT amount")
    fta_eligible: bool = Field(default=False, description="FTA eligibility status")
    fta_savings: Optional[Decimal] = Field(None, description="FTA savings amount")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags list"""
        if v is not None:
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
        return v


class CalculationUpdateRequest(BaseModel):
    """Schema for updating calculation metadata only"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(None, max_length=20)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags list"""
        if v is not None:
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
            for tag in v:
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
        return v


# ============================================================================
# CALCULATION RESPONSE SCHEMAS
# ============================================================================

class CalculationResponse(BaseModel):
    """Schema for full calculation details"""
    id: str
    user_id: str
    organization_id: Optional[str]
    name: Optional[str]
    description: Optional[str]
    hs_code: str
    product_description: Optional[str]
    origin_country: str
    destination_country: str
    cif_value: Decimal
    currency: str
    result: Dict[str, Any]
    total_cost: Decimal
    customs_duty: Optional[Decimal]
    vat_amount: Optional[Decimal]
    fta_eligible: bool
    fta_savings: Optional[Decimal]
    is_favorite: bool
    tags: Optional[List[str]]
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CalculationListItem(BaseModel):
    """Schema for minimal calculation info in list views"""
    id: str
    name: Optional[str]
    hs_code: str
    product_description: Optional[str]
    origin_country: str
    destination_country: str
    total_cost: Decimal
    currency: str
    is_favorite: bool
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class CalculationListResponse(BaseModel):
    """Schema for paginated calculation list"""
    calculations: List[CalculationListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class FavoriteToggleResponse(BaseModel):
    """Schema for favorite toggle response"""
    id: str
    is_favorite: bool
    message: str = "Favorite status updated successfully"


class ShareLinkResponse(BaseModel):
    """Schema for share link creation response"""
    share_token: str
    share_url: str
    expires_at: Optional[datetime]
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# FILTER & QUERY SCHEMAS
# ============================================================================

class CalculationFilters(BaseModel):
    """Schema for calculation filtering options"""
    search: Optional[str] = Field(None, description="Search by name or HS code")
    tag: Optional[str] = Field(None, description="Filter by specific tag")
    hs_code: Optional[str] = Field(None, description="Filter by HS code")
    country: Optional[str] = Field(None, description="Filter by destination country")
    min_cost: Optional[Decimal] = Field(None, ge=0, description="Minimum total cost")
    max_cost: Optional[Decimal] = Field(None, ge=0, description="Maximum total cost")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    sort_by: str = Field(default="created_at", pattern="^(created_at|name|total_cost)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
