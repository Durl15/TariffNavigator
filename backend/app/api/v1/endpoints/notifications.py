"""
Notification endpoints.
Users receive notifications about tariff changes affecting their watchlists.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
    MarkReadResponse
)

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's notifications with pagination and filters.

    Filters:
    - unread_only: Show only unread notifications
    - notification_type: Filter by type (rate_change, deadline, new_program)
    """
    # Validate pagination
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")

    # Build query
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    if notification_type:
        query = query.where(Notification.type == notification_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get unread count (always return this)
    unread_query = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar_one()

    # Apply pagination and ordering (newest first)
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=notifications,
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count
    )


@router.get("/unread", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications.

    Used for the notification bell badge in the UI.
    """
    query = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )
    result = await db.execute(query)
    count = result.scalar_one()

    return UnreadCountResponse(count=count)


@router.put("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a single notification as read.
    """
    # Get notification
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Mark as read
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await db.commit()

    return MarkReadResponse(
        success=True,
        message="Notification marked as read"
    )


@router.put("/read-all", response_model=MarkReadResponse)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read.
    """
    # Update all unread notifications
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
        .values(
            is_read=True,
            read_at=datetime.utcnow()
        )
    )

    result = await db.execute(stmt)
    await db.commit()

    count = result.rowcount

    return MarkReadResponse(
        success=True,
        message=f"{count} notifications marked as read"
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a single notification.
    """
    # Get notification
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Delete
    await db.delete(notification)
    await db.commit()

    return None
