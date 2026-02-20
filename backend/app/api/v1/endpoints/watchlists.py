"""
Watchlist management endpoints.
Users can create watchlists to monitor tariff changes for specific HS codes and countries.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
    WatchlistListResponse
)

router = APIRouter()


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new watchlist.

    Users can monitor specific HS codes across multiple countries.
    Notifications will be sent when tariff rates change.
    """
    # Create new watchlist
    watchlist = Watchlist(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        hs_codes=data.hs_codes,
        countries=data.countries,
        alert_preferences=data.alert_preferences or {'email': True, 'digest': 'daily'},
        is_active=True
    )

    db.add(watchlist)
    await db.commit()
    await db.refresh(watchlist)

    return watchlist


@router.get("", response_model=WatchlistListResponse)
async def list_watchlists(
    page: int = 1,
    page_size: int = 20,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's watchlists with pagination.

    Optionally filter to only show active watchlists.
    """
    # Validate pagination
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    # Build query
    query = select(Watchlist).where(Watchlist.user_id == current_user.id)

    if active_only:
        query = query.where(Watchlist.is_active == True)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination and ordering
    query = query.order_by(Watchlist.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
    result = await db.execute(query)
    watchlists = result.scalars().all()

    return WatchlistListResponse(
        watchlists=watchlists,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific watchlist.
    """
    # Query watchlist
    query = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    )
    result = await db.execute(query)
    watchlist = result.scalar_one_or_none()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    return watchlist


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: str,
    data: WatchlistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing watchlist.

    Only provided fields will be updated.
    """
    # Get watchlist
    query = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    )
    result = await db.execute(query)
    watchlist = result.scalar_one_or_none()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(watchlist, field, value)

    await db.commit()
    await db.refresh(watchlist)

    return watchlist


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a watchlist permanently.
    """
    # Get watchlist
    query = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    )
    result = await db.execute(query)
    watchlist = result.scalar_one_or_none()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    # Delete
    await db.delete(watchlist)
    await db.commit()

    return None


@router.put("/{watchlist_id}/toggle", response_model=WatchlistResponse)
async def toggle_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle watchlist active status.

    Disabled watchlists will not trigger notifications.
    """
    # Get watchlist
    query = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    )
    result = await db.execute(query)
    watchlist = result.scalar_one_or_none()

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    # Toggle
    watchlist.is_active = not watchlist.is_active

    await db.commit()
    await db.refresh(watchlist)

    return watchlist
