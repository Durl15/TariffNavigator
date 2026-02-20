"""
Catalogs API Endpoints - Product Catalog Management & Impact Analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import Optional
from datetime import datetime
import uuid
import math

from app.db.session import get_db
from app.api.deps import get_current_user
from app.api.deps_rate_limit import check_user_rate_limit
from app.models.user import User
from app.models.catalog import Catalog, CatalogItem
from app.models.organization import Organization
from app.services.catalog_parser import CatalogParser
from app.services.impact_calculator import ImpactCalculator
from app.schemas.catalog import (
    CatalogResponse,
    CatalogListItem,
    CatalogListResponse,
    CatalogUpdateRequest,
    CatalogUploadResponse,
    UploadError,
    CatalogItemResponse,
    CatalogItemsResponse,
    CatalogImpactResponse,
    PortfolioMetrics,
    CategoryMetrics,
    OriginMetrics
)

router = APIRouter()


# ============================================================================
# TIER LIMITS
# ============================================================================

TIER_SKU_LIMITS = {
    'free': 1000,
    'pro': 10000,
    'enterprise': float('inf'),
    'consultant': float('inf')
}


async def check_sku_limit(user: User, db: AsyncSession, sku_count: int):
    """Check if user has exceeded their SKU limit"""
    tier = user.subscription_tier or 'free'
    limit = TIER_SKU_LIMITS.get(tier, 1000)

    if sku_count > limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"SKU limit exceeded. Your {tier} tier allows up to {int(limit)} SKUs. Upload contains {sku_count} SKUs. Upgrade to Pro for 10,000 SKUs or Enterprise for unlimited."
        )


# ============================================================================
# UPLOAD ENDPOINT
# ============================================================================

@router.post("/upload", response_model=CatalogUploadResponse, dependencies=[Depends(check_user_rate_limit)])
async def upload_catalog(
    file: UploadFile = File(..., description="CSV file containing product catalog"),
    name: str = Form(..., description="Catalog name"),
    description: Optional[str] = Form(None, description="Optional catalog description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a product catalog CSV file and calculate tariff impact.

    CSV Required Columns:
    - sku: Unique product identifier
    - product_name: Product display name
    - hs_code: 8-10 digit HS/HTS code
    - origin_country: 2-letter ISO country code (CN, US, EU, JP, KR, MX, CA)
    - cogs: Cost of goods sold (USD)
    - retail_price: Selling price (USD)
    - annual_volume: Units sold per year

    Optional Columns:
    - category: Product category
    - weight_kg: Shipping weight
    - notes: Free text notes
    """
    # Read file content
    file_content = await file.read()

    # Parse CSV
    try:
        items_data, errors = await CatalogParser.parse_csv(file_content, file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not items_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid products found in CSV"
        )

    # Check tier limits
    await check_sku_limit(current_user, db, len(items_data))

    # Create catalog
    catalog = Catalog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        name=name,
        description=description,
        currency='USD',
        total_skus=len(items_data),
        uploaded_at=datetime.utcnow()
    )

    db.add(catalog)
    await db.flush()

    # Create catalog items
    catalog_items = []
    for item_data in items_data:
        item = CatalogItem(
            id=str(uuid.uuid4()),
            catalog_id=catalog.id,
            **item_data
        )
        catalog_items.append(item)

    db.add_all(catalog_items)
    await db.commit()
    await db.refresh(catalog)

    # Format errors for response
    upload_errors = [
        UploadError(row=err['row'], sku=err['sku'], error=err['error'])
        for err in errors
    ]

    return CatalogUploadResponse(
        catalog_id=catalog.id,
        name=catalog.name,
        total_skus=catalog.total_skus,
        success_count=len(items_data),
        error_count=len(errors),
        errors=upload_errors
    )


# ============================================================================
# LIST & RETRIEVE ENDPOINTS
# ============================================================================

@router.get("", response_model=CatalogListResponse, dependencies=[Depends(check_user_rate_limit)])
async def list_catalogs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", pattern="^(created_at|name|total_skus)$", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's product catalogs with pagination.
    Only returns catalogs that have not been deleted.
    """
    # Build base query
    query = select(Catalog).where(
        and_(
            Catalog.user_id == current_user.id,
            Catalog.deleted_at.is_(None)
        )
    )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    if sort_by == "created_at":
        order_col = Catalog.created_at
    elif sort_by == "name":
        order_col = Catalog.name
    else:  # total_skus
        order_col = Catalog.total_skus

    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    catalogs = result.scalars().all()

    # Convert to response models
    catalog_items = [CatalogListItem.model_validate(cat) for cat in catalogs]

    return CatalogListResponse(
        catalogs=catalog_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/{catalog_id}", response_model=CatalogResponse, dependencies=[Depends(check_user_rate_limit)])
async def get_catalog(
    catalog_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single catalog by ID"""
    result = await db.execute(
        select(Catalog).where(
            and_(
                Catalog.id == catalog_id,
                Catalog.user_id == current_user.id,
                Catalog.deleted_at.is_(None)
            )
        )
    )
    catalog = result.scalar_one_or_none()

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found"
        )

    return CatalogResponse.model_validate(catalog)


@router.get("/{catalog_id}/items", response_model=CatalogItemsResponse, dependencies=[Depends(check_user_rate_limit)])
async def list_catalog_items(
    catalog_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List items in a catalog with pagination"""
    # Verify catalog ownership
    catalog_result = await db.execute(
        select(Catalog).where(
            and_(
                Catalog.id == catalog_id,
                Catalog.user_id == current_user.id,
                Catalog.deleted_at.is_(None)
            )
        )
    )
    catalog = catalog_result.scalar_one_or_none()

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found"
        )

    # Get items
    query = select(CatalogItem).where(CatalogItem.catalog_id == catalog_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()

    # Convert to response models
    item_responses = [CatalogItemResponse.model_validate(item) for item in items]

    return CatalogItemsResponse(
        items=item_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


# ============================================================================
# IMPACT ANALYSIS ENDPOINT
# ============================================================================

@router.get("/{catalog_id}/impact", response_model=CatalogImpactResponse, dependencies=[Depends(check_user_rate_limit)])
async def get_catalog_impact(
    catalog_id: str,
    destination_country: str = Query(..., min_length=2, max_length=2, description="2-letter ISO country code where goods are imported to"),
    recalculate: bool = Query(False, description="Force recalculation even if values exist"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate tariff impact analysis for a catalog.

    Calculates per-SKU tariff costs, landed costs, margins, and portfolio metrics.
    Groups data by category and origin country.
    """
    # Verify catalog ownership
    catalog_result = await db.execute(
        select(Catalog).where(
            and_(
                Catalog.id == catalog_id,
                Catalog.user_id == current_user.id,
                Catalog.deleted_at.is_(None)
            )
        )
    )
    catalog = catalog_result.scalar_one_or_none()

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found"
        )

    # Get all catalog items
    items_result = await db.execute(
        select(CatalogItem).where(CatalogItem.catalog_id == catalog_id)
    )
    items = list(items_result.scalars().all())

    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog has no items"
        )

    # Calculate impact
    updated_items, portfolio_metrics_dict = await ImpactCalculator.calculate_catalog_impact(
        items, destination_country, db, recalculate
    )

    # Save updated items if recalculating
    if recalculate:
        await db.commit()
        for item in updated_items:
            await db.refresh(item)

    # Convert to response models
    item_responses = [CatalogItemResponse.model_validate(item) for item in updated_items]

    # Build portfolio metrics response
    portfolio_metrics = PortfolioMetrics(
        total_tariff_exposure=portfolio_metrics_dict['total_tariff_exposure'],
        total_revenue=portfolio_metrics_dict['total_revenue'],
        total_landed_cost=portfolio_metrics_dict['total_landed_cost'],
        avg_margin_percent=portfolio_metrics_dict['avg_margin_percent'],
        total_items=portfolio_metrics_dict['total_items'],
        negative_margin_count=portfolio_metrics_dict['negative_margin_count'],
        zero_tariff_count=portfolio_metrics_dict['zero_tariff_count'],
        by_category=[CategoryMetrics(**cat) for cat in portfolio_metrics_dict['by_category']],
        by_origin=[OriginMetrics(**origin) for origin in portfolio_metrics_dict['by_origin']]
    )

    return CatalogImpactResponse(
        catalog_id=catalog.id,
        catalog_name=catalog.name,
        destination_country=destination_country,
        portfolio_metrics=portfolio_metrics,
        items=item_responses,
        calculation_date=datetime.utcnow()
    )


# ============================================================================
# UPDATE & DELETE ENDPOINTS
# ============================================================================

@router.put("/{catalog_id}", response_model=CatalogResponse, dependencies=[Depends(check_user_rate_limit)])
async def update_catalog(
    catalog_id: str,
    update_data: CatalogUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update catalog metadata (name, description)"""
    result = await db.execute(
        select(Catalog).where(
            and_(
                Catalog.id == catalog_id,
                Catalog.user_id == current_user.id,
                Catalog.deleted_at.is_(None)
            )
        )
    )
    catalog = result.scalar_one_or_none()

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found"
        )

    # Update fields
    if update_data.name is not None:
        catalog.name = update_data.name
    if update_data.description is not None:
        catalog.description = update_data.description

    catalog.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(catalog)

    return CatalogResponse.model_validate(catalog)


@router.delete("/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_user_rate_limit)])
async def delete_catalog(
    catalog_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a catalog (sets deleted_at timestamp)"""
    result = await db.execute(
        select(Catalog).where(
            and_(
                Catalog.id == catalog_id,
                Catalog.user_id == current_user.id,
                Catalog.deleted_at.is_(None)
            )
        )
    )
    catalog = result.scalar_one_or_none()

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog not found"
        )

    # Soft delete
    catalog.deleted_at = datetime.utcnow()

    await db.commit()

    return None
