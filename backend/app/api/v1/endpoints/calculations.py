"""
Calculations API Endpoints - Saved Calculations & Favorites
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import Optional
from datetime import datetime, timedelta
import uuid
import secrets
import math

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.calculation import Calculation, SharedLink
from app.schemas.calculation import (
    CalculationSaveRequest,
    CalculationUpdateRequest,
    CalculationResponse,
    CalculationListItem,
    CalculationListResponse,
    FavoriteToggleResponse,
    ShareLinkResponse
)

router = APIRouter()


# ============================================================================
# LIST & RETRIEVE ENDPOINTS
# ============================================================================

@router.get("/saved", response_model=CalculationListResponse)
async def list_saved_calculations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or HS code"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort_by: str = Query("created_at", pattern="^(created_at|name|total_cost)$", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's saved calculations with pagination and filtering.
    Only returns calculations that have been explicitly saved (name is not NULL).
    """
    # Build base query - only user's calculations, not deleted, with name (indicates "saved")
    query = select(Calculation).where(
        and_(
            Calculation.user_id == current_user.id,
            Calculation.deleted_at.is_(None),
            Calculation.name.isnot(None)  # Only explicitly saved calculations
        )
    )

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Calculation.name.ilike(search_pattern),
                Calculation.hs_code.ilike(search_pattern),
                Calculation.product_description.ilike(search_pattern)
            )
        )

    # Apply tag filter (JSON contains check)
    if tag:
        query = query.where(Calculation.tags.contains([tag]))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    if sort_by == "created_at":
        order_col = Calculation.created_at
    elif sort_by == "name":
        order_col = Calculation.name
    else:  # total_cost
        order_col = Calculation.total_cost

    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    calculations = result.scalars().all()

    # Convert to response models
    calc_items = []
    for calc in calculations:
        calc_dict = {
            'id': calc.id,
            'name': calc.name,
            'hs_code': calc.hs_code,
            'product_description': calc.product_description,
            'origin_country': calc.origin_country,
            'destination_country': calc.destination_country,
            'total_cost': calc.total_cost,
            'currency': calc.currency,
            'is_favorite': calc.is_favorite,
            'tags': calc.tags,
            'created_at': calc.created_at
        }
        calc_items.append(CalculationListItem(**calc_dict))

    return CalculationListResponse(
        calculations=calc_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/favorites", response_model=CalculationListResponse)
async def list_favorite_calculations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's favorited calculations.
    Returns only calculations marked as favorite.
    """
    # Build query - only favorited calculations
    query = select(Calculation).where(
        and_(
            Calculation.user_id == current_user.id,
            Calculation.deleted_at.is_(None),
            Calculation.is_favorite == True
        )
    ).order_by(desc(Calculation.updated_at))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    calculations = result.scalars().all()

    # Convert to response models
    calc_items = []
    for calc in calculations:
        calc_dict = {
            'id': calc.id,
            'name': calc.name,
            'hs_code': calc.hs_code,
            'product_description': calc.product_description,
            'origin_country': calc.origin_country,
            'destination_country': calc.destination_country,
            'total_cost': calc.total_cost,
            'currency': calc.currency,
            'is_favorite': calc.is_favorite,
            'tags': calc.tags,
            'created_at': calc.created_at
        }
        calc_items.append(CalculationListItem(**calc_dict))

    return CalculationListResponse(
        calculations=calc_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/{calc_id}", response_model=CalculationResponse)
async def get_calculation(
    calc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed calculation by ID.
    Increments view_count on each access.
    """
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id == calc_id,
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    calc = result.scalar_one_or_none()

    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have access to it"
        )

    # Increment view count
    calc.view_count += 1
    await db.commit()
    await db.refresh(calc)

    # Convert to response model
    calc_dict = {
        'id': calc.id,
        'user_id': calc.user_id,
        'organization_id': calc.organization_id,
        'name': calc.name,
        'description': calc.description,
        'hs_code': calc.hs_code,
        'product_description': calc.product_description,
        'origin_country': calc.origin_country,
        'destination_country': calc.destination_country,
        'cif_value': calc.cif_value,
        'currency': calc.currency,
        'result': calc.result,
        'total_cost': calc.total_cost,
        'customs_duty': calc.customs_duty,
        'vat_amount': calc.vat_amount,
        'fta_eligible': calc.fta_eligible,
        'fta_savings': calc.fta_savings,
        'is_favorite': calc.is_favorite,
        'tags': calc.tags,
        'view_count': calc.view_count,
        'created_at': calc.created_at,
        'updated_at': calc.updated_at
    }

    return CalculationResponse(**calc_dict)


# ============================================================================
# CREATE & SAVE ENDPOINTS
# ============================================================================

@router.post("/save", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
async def save_calculation(
    save_data: CalculationSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a new calculation with metadata.
    Creates a Calculation record in the database.
    """
    # Create new calculation
    calculation = Calculation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        name=save_data.name,
        description=save_data.description,
        tags=save_data.tags,
        hs_code=save_data.hs_code,
        product_description=save_data.product_description,
        origin_country=save_data.origin_country,
        destination_country=save_data.destination_country,
        cif_value=save_data.cif_value,
        currency=save_data.currency,
        result=save_data.result,
        total_cost=save_data.total_cost,
        customs_duty=save_data.customs_duty,
        vat_amount=save_data.vat_amount,
        fta_eligible=save_data.fta_eligible,
        fta_savings=save_data.fta_savings,
        is_favorite=False,
        view_count=0,
        created_at=datetime.utcnow()
    )

    db.add(calculation)
    await db.commit()
    await db.refresh(calculation)

    # Convert to response model
    calc_dict = {
        'id': calculation.id,
        'user_id': calculation.user_id,
        'organization_id': calculation.organization_id,
        'name': calculation.name,
        'description': calculation.description,
        'hs_code': calculation.hs_code,
        'product_description': calculation.product_description,
        'origin_country': calculation.origin_country,
        'destination_country': calculation.destination_country,
        'cif_value': calculation.cif_value,
        'currency': calculation.currency,
        'result': calculation.result,
        'total_cost': calculation.total_cost,
        'customs_duty': calculation.customs_duty,
        'vat_amount': calculation.vat_amount,
        'fta_eligible': calculation.fta_eligible,
        'fta_savings': calculation.fta_savings,
        'is_favorite': calculation.is_favorite,
        'tags': calculation.tags,
        'view_count': calculation.view_count,
        'created_at': calculation.created_at,
        'updated_at': calculation.updated_at
    }

    return CalculationResponse(**calc_dict)


# ============================================================================
# UPDATE ENDPOINTS
# ============================================================================

@router.put("/{calc_id}/favorite", response_model=FavoriteToggleResponse)
async def toggle_favorite(
    calc_id: str,
    is_favorite: bool = Query(..., description="New favorite status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle favorite status of a calculation.
    Supports optimistic updates from frontend.
    """
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id == calc_id,
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    calc = result.scalar_one_or_none()

    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have access to it"
        )

    calc.is_favorite = is_favorite
    calc.updated_at = datetime.utcnow()

    await db.commit()

    return FavoriteToggleResponse(
        id=calc.id,
        is_favorite=calc.is_favorite,
        message=f"Calculation {'added to' if is_favorite else 'removed from'} favorites"
    )


@router.put("/{calc_id}", response_model=CalculationResponse)
async def update_calculation(
    calc_id: str,
    update_data: CalculationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update calculation metadata (name, description, tags).
    Does not update calculation results or values.
    """
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id == calc_id,
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    calc = result.scalar_one_or_none()

    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have access to it"
        )

    # Update only provided fields
    if update_data.name is not None:
        calc.name = update_data.name
    if update_data.description is not None:
        calc.description = update_data.description
    if update_data.tags is not None:
        calc.tags = update_data.tags

    calc.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(calc)

    # Convert to response model
    calc_dict = {
        'id': calc.id,
        'user_id': calc.user_id,
        'organization_id': calc.organization_id,
        'name': calc.name,
        'description': calc.description,
        'hs_code': calc.hs_code,
        'product_description': calc.product_description,
        'origin_country': calc.origin_country,
        'destination_country': calc.destination_country,
        'cif_value': calc.cif_value,
        'currency': calc.currency,
        'result': calc.result,
        'total_cost': calc.total_cost,
        'customs_duty': calc.customs_duty,
        'vat_amount': calc.vat_amount,
        'fta_eligible': calc.fta_eligible,
        'fta_savings': calc.fta_savings,
        'is_favorite': calc.is_favorite,
        'tags': calc.tags,
        'view_count': calc.view_count,
        'created_at': calc.created_at,
        'updated_at': calc.updated_at
    }

    return CalculationResponse(**calc_dict)


# ============================================================================
# DELETE & DUPLICATE ENDPOINTS
# ============================================================================

@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calculation(
    calc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a calculation.
    Sets deleted_at timestamp instead of removing from database.
    """
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id == calc_id,
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    calc = result.scalar_one_or_none()

    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have access to it"
        )

    calc.deleted_at = datetime.utcnow()
    await db.commit()

    return None


@router.post("/{calc_id}/duplicate", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_calculation(
    calc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a duplicate of a calculation for modification.
    All fields copied except: id (new UUID), name (append ' (Copy)'), created_at (now).
    Favorite status is NOT inherited.
    """
    # Get original calculation
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id == calc_id,
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have access to it"
        )

    # Create duplicate
    duplicate = Calculation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        organization_id=original.organization_id,
        name=f"{original.name} (Copy)" if original.name else "Calculation (Copy)",
        description=original.description,
        hs_code=original.hs_code,
        product_description=original.product_description,
        origin_country=original.origin_country,
        destination_country=original.destination_country,
        cif_value=original.cif_value,
        currency=original.currency,
        result=original.result.copy() if original.result else {},
        total_cost=original.total_cost,
        customs_duty=original.customs_duty,
        vat_amount=original.vat_amount,
        fta_eligible=original.fta_eligible,
        fta_savings=original.fta_savings,
        is_favorite=False,  # Don't copy favorite status
        tags=original.tags.copy() if original.tags else None,
        view_count=0,
        created_at=datetime.utcnow()
    )

    db.add(duplicate)
    await db.commit()
    await db.refresh(duplicate)

    # Convert to response model
    calc_dict = {
        'id': duplicate.id,
        'user_id': duplicate.user_id,
        'organization_id': duplicate.organization_id,
        'name': duplicate.name,
        'description': duplicate.description,
        'hs_code': duplicate.hs_code,
        'product_description': duplicate.product_description,
        'origin_country': duplicate.origin_country,
        'destination_country': duplicate.destination_country,
        'cif_value': duplicate.cif_value,
        'currency': duplicate.currency,
        'result': duplicate.result,
        'total_cost': duplicate.total_cost,
        'customs_duty': duplicate.customs_duty,
        'vat_amount': duplicate.vat_amount,
        'fta_eligible': duplicate.fta_eligible,
        'fta_savings': duplicate.fta_savings,
        'is_favorite': duplicate.is_favorite,
        'tags': duplicate.tags,
        'view_count': duplicate.view_count,
        'created_at': duplicate.created_at,
        'updated_at': duplicate.updated_at
    }

    return CalculationResponse(**calc_dict)


# ============================================================================
# SHARING ENDPOINTS
# ============================================================================

@router.post("/{calc_id}/share", response_model=ShareLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_share_link(
    calc_id: str,
    expires_hours: Optional[int] = Query(None, ge=1, le=8760, description="Expiry in hours (max 1 year)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a shareable link for a calculation.
    Link expires after specified hours (default: never expires).
    """
    # Verify calculation exists and belongs to user
    result = await db.execute(
        select(Calculation).where(
            and_(
                Calculation.id == calc_id,
                Calculation.user_id == current_user.id,
                Calculation.deleted_at.is_(None)
            )
        )
    )
    calc = result.scalar_one_or_none()

    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found or you don't have access to it"
        )

    # Generate secure token
    token = secrets.token_urlsafe(32)

    # Calculate expiry
    expires_at = None
    if expires_hours:
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

    # Create shared link
    shared_link = SharedLink(
        id=str(uuid.uuid4()),
        token=token,
        calculation_id=calc_id,
        created_by_user_id=current_user.id,
        access_level='view',
        expires_at=expires_at,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(shared_link)
    await db.commit()

    # Generate URL (use app's base URL - will be replaced with actual domain)
    share_url = f"https://tariffnavigator.vercel.app/shared/{token}"

    return ShareLinkResponse(
        share_token=token,
        share_url=share_url,
        expires_at=expires_at,
        created_at=shared_link.created_at
    )
