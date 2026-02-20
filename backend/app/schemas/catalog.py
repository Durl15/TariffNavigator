"""
Catalog Management Schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============================================================================
# CATALOG REQUEST SCHEMAS
# ============================================================================

class CatalogCreateRequest(BaseModel):
    """Schema for creating a new catalog"""
    name: str = Field(..., min_length=1, max_length=255, description="Catalog name")
    description: Optional[str] = Field(None, description="Optional catalog description")


class CatalogUpdateRequest(BaseModel):
    """Schema for updating catalog metadata"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


# ============================================================================
# CATALOG RESPONSE SCHEMAS
# ============================================================================

class CatalogResponse(BaseModel):
    """Schema for full catalog details"""
    id: str
    user_id: str
    organization_id: Optional[str]
    name: str
    description: Optional[str]
    currency: str
    total_skus: int
    uploaded_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CatalogListItem(BaseModel):
    """Schema for catalog in list view"""
    id: str
    name: str
    description: Optional[str]
    total_skus: int
    uploaded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class CatalogListResponse(BaseModel):
    """Schema for paginated catalog list"""
    catalogs: List[CatalogListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# CATALOG ITEM SCHEMAS
# ============================================================================

class CatalogItemResponse(BaseModel):
    """Schema for catalog item details"""
    id: str
    catalog_id: str
    sku: str
    product_name: Optional[str]
    hs_code: Optional[str]
    origin_country: str
    cogs: Decimal
    retail_price: Decimal
    annual_volume: int
    category: Optional[str]
    weight_kg: Optional[Decimal]
    notes: Optional[str]
    # Calculated fields
    tariff_cost: Optional[Decimal]
    landed_cost: Optional[Decimal]
    gross_margin: Optional[Decimal]
    margin_percent: Optional[Decimal]
    annual_tariff_exposure: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CatalogItemsResponse(BaseModel):
    """Schema for paginated catalog items list"""
    items: List[CatalogItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# UPLOAD RESPONSE SCHEMAS
# ============================================================================

class UploadError(BaseModel):
    """Schema for upload error details"""
    row: int
    sku: str
    error: str


class CatalogUploadResponse(BaseModel):
    """Schema for catalog upload result"""
    catalog_id: str
    name: str
    total_skus: int
    success_count: int
    error_count: int
    errors: List[UploadError]


# ============================================================================
# IMPACT ANALYSIS SCHEMAS
# ============================================================================

class CategoryMetrics(BaseModel):
    """Metrics grouped by product category"""
    category: str
    total_tariff: float
    total_revenue: float
    avg_margin: float
    item_count: int


class OriginMetrics(BaseModel):
    """Metrics grouped by origin country"""
    origin_country: str
    total_tariff: float
    total_revenue: float
    avg_margin: float
    item_count: int


class PortfolioMetrics(BaseModel):
    """Aggregate portfolio-level metrics"""
    total_tariff_exposure: float = Field(..., description="Total annual tariff cost across all products")
    total_revenue: float = Field(..., description="Total annual revenue across all products")
    total_landed_cost: float = Field(..., description="Total annual landed cost across all products")
    avg_margin_percent: float = Field(..., description="Weighted average margin percentage")
    total_items: int = Field(..., description="Total number of products in catalog")
    negative_margin_count: int = Field(..., description="Count of products with negative margins")
    zero_tariff_count: int = Field(..., description="Count of products with zero tariff")
    by_category: List[CategoryMetrics] = Field(..., description="Metrics grouped by category")
    by_origin: List[OriginMetrics] = Field(..., description="Metrics grouped by origin country")


class CatalogImpactResponse(BaseModel):
    """Schema for catalog impact analysis"""
    catalog_id: str
    catalog_name: str
    destination_country: str
    portfolio_metrics: PortfolioMetrics
    items: List[CatalogItemResponse]
    calculation_date: datetime

    class Config:
        from_attributes = True
