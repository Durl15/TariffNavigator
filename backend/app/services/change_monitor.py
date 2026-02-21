"""
Tariff change monitoring service.
Detects rate changes and triggers notifications to watchlist subscribers.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

from app.db.session import async_session
from app.models.hs_code import HSCode
from app.models.watchlist import Watchlist
from app.models.notification import Notification
from app.models.tariff_change import TariffChangeLog
from app.models.user import User
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


async def check_tariff_changes():
    """
    Main scheduled job: Check for tariff rate changes.

    Phase 1: Monitor internal database for changes
    Future phases: Monitor external sources (Federal Register, CBP)
    """
    logger.info("Running tariff change detection...")

    async with async_session() as db:
        try:
            # Detect changes in the last hour (since scheduler runs hourly)
            changes = await detect_internal_changes(db)

            if changes:
                logger.info(f"Detected {len(changes)} tariff changes")

                # Match changes against watchlists and create notifications
                for change in changes:
                    await match_and_notify(change, db)

                logger.info("Tariff change detection complete")
            else:
                logger.info("No tariff changes detected")

        except Exception as e:
            logger.error(f"Error in tariff change detection: {str(e)}", exc_info=True)


async def detect_internal_changes(db: AsyncSession) -> List[TariffChangeLog]:
    """
    Detect changes in the hs_codes table since last check.

    Phase 1: Simple approach - detect new/updated records
    Phase 2: Track historical snapshots for precise change detection
    """
    changes = []

    # For Phase 1, we'll detect records updated in the last 2 hours
    # (2 hours to account for potential scheduler delays)
    cutoff_time = datetime.utcnow() - timedelta(hours=2)

    # Query recently updated tariffs
    query = select(HSCode).where(
        HSCode.updated_at >= cutoff_time
    ) if hasattr(HSCode, 'updated_at') else select(HSCode).limit(0)

    # If no updated_at column exists, skip internal monitoring for now
    # (External monitoring in Phase 3 will be the primary source)
    try:
        result = await db.execute(query)
        updated_tariffs = result.scalars().all()

        for tariff in updated_tariffs:
            # Check if we've already logged this change
            existing_query = select(TariffChangeLog).where(
                and_(
                    TariffChangeLog.hs_code == tariff.code,
                    TariffChangeLog.country == tariff.country,
                    TariffChangeLog.detected_at >= cutoff_time,
                    TariffChangeLog.change_type == 'rate_update'
                )
            )
            existing_result = await db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()

            if not existing:
                # Create new change log entry
                # Note: We don't have old_value in Phase 1, so just log current state
                change = TariffChangeLog(
                    change_type='rate_update',
                    hs_code=tariff.code,
                    country=tariff.country,
                    old_value=None,  # Phase 2: Track historical values
                    new_value={
                        'mfn_rate': float(tariff.mfn_rate) if tariff.mfn_rate else 0,
                        'general_rate': float(tariff.general_rate) if tariff.general_rate else 0,
                        'vat_rate': float(tariff.vat_rate) if tariff.vat_rate else 0,
                    },
                    source='internal',
                    detected_at=datetime.utcnow(),
                    notifications_sent=False,
                    notification_count=0
                )

                db.add(change)
                changes.append(change)

        if changes:
            await db.commit()

    except Exception as e:
        logger.warning(f"Internal change detection skipped: {str(e)}")

    return changes


async def match_and_notify(change: TariffChangeLog, db: AsyncSession):
    """
    Find users watching this change and create notifications.
    """
    try:
        # Find active watchlists that match this change
        query = select(Watchlist).where(
            Watchlist.is_active == True
        )
        result = await db.execute(query)
        watchlists = result.scalars().all()

        notifications_created = 0

        for watchlist in watchlists:
            # Check if this watchlist matches the change
            if watchlist.matches_change(change.hs_code, change.country):
                # Create notification for the user
                notification = Notification(
                    id=str(uuid.uuid4()),
                    user_id=watchlist.user_id,
                    type='rate_change',
                    title=f"Tariff Rate Change: {change.hs_code}",
                    message=change.get_summary(),
                    link=f"/tariff/{change.hs_code}?country={change.country}",
                    data={
                        'hs_code': change.hs_code,
                        'country': change.country,
                        'old_value': change.old_value,
                        'new_value': change.new_value,
                        'watchlist_id': watchlist.id,
                        'watchlist_name': watchlist.name
                    },
                    is_read=False,
                    created_at=datetime.utcnow()
                )

                db.add(notification)
                notifications_created += 1

                # Send instant email if user has it enabled (Phase 2)
                try:
                    # Get user to check email preferences
                    user_result = await db.execute(
                        select(User).where(User.id == watchlist.user_id)
                    )
                    user = user_result.scalar_one_or_none()

                    if user and user.is_email_verified:
                        # Check if instant emails are enabled
                        prefs = user.preferences or {}
                        email_prefs = prefs.get('email_notifications', {})

                        if email_prefs.get('enabled') and email_prefs.get('instant_notifications'):
                            # Send instant email notification
                            await email_service.send_notification_email(
                                to_email=user.email,
                                notification=notification
                            )
                            logger.info(f"Sent instant email to {user.email} for {change.hs_code}")

                except Exception as e:
                    logger.error(f"Failed to send instant email: {str(e)}")

        if notifications_created > 0:
            # Mark change as notified
            change.notifications_sent = True
            change.notification_count = notifications_created

            await db.commit()

            logger.info(
                f"Created {notifications_created} notifications for "
                f"change: {change.get_summary()}"
            )

    except Exception as e:
        logger.error(f"Error creating notifications: {str(e)}", exc_info=True)
        await db.rollback()
