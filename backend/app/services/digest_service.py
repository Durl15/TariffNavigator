"""
Digest email service for sending daily and weekly notification summaries.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import async_session
from app.models.user import User
from app.models.notification import Notification
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


async def send_daily_digests():
    """
    Send daily digest emails to users who have opted in.
    Sends notifications from the past 24 hours.
    """
    logger.info("Starting daily digest email job")

    try:
        async with async_session() as db:
            # Get users who want daily digests
            result = await db.execute(
                select(User).where(
                    and_(
                        User.is_active == True,
                        User.is_email_verified == True,
                        User.preferences['email_notifications']['enabled'].as_boolean() == True,
                        User.preferences['email_notifications']['digest_frequency'].as_string() == 'daily'
                    )
                )
            )
            users = result.scalars().all()

            sent_count = 0
            failed_count = 0

            # Send digest to each user
            for user in users:
                try:
                    # Get unread notifications from last 24 hours
                    yesterday = datetime.utcnow() - timedelta(days=1)
                    notif_result = await db.execute(
                        select(Notification).where(
                            and_(
                                Notification.user_id == user.id,
                                Notification.is_read == False,
                                Notification.created_at >= yesterday
                            )
                        ).order_by(Notification.created_at.desc())
                    )
                    notifications = notif_result.scalars().all()

                    # Only send if there are notifications
                    if notifications:
                        success = await email_service.send_digest_email(
                            to_email=user.email,
                            notifications=notifications,
                            frequency='daily'
                        )

                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1

                except Exception as e:
                    logger.error(f"Failed to send daily digest to {user.email}: {str(e)}")
                    failed_count += 1

            logger.info(f"Daily digest job completed: {sent_count} sent, {failed_count} failed")

    except Exception as e:
        logger.error(f"Daily digest job failed: {str(e)}")


async def send_weekly_digests():
    """
    Send weekly digest emails to users who have opted in.
    Sends notifications from the past 7 days.
    """
    logger.info("Starting weekly digest email job")

    try:
        async with async_session() as db:
            # Get users who want weekly digests
            result = await db.execute(
                select(User).where(
                    and_(
                        User.is_active == True,
                        User.is_email_verified == True,
                        User.preferences['email_notifications']['enabled'].as_boolean() == True,
                        User.preferences['email_notifications']['digest_frequency'].as_string() == 'weekly'
                    )
                )
            )
            users = result.scalars().all()

            sent_count = 0
            failed_count = 0

            # Send digest to each user
            for user in users:
                try:
                    # Get unread notifications from last 7 days
                    last_week = datetime.utcnow() - timedelta(days=7)
                    notif_result = await db.execute(
                        select(Notification).where(
                            and_(
                                Notification.user_id == user.id,
                                Notification.is_read == False,
                                Notification.created_at >= last_week
                            )
                        ).order_by(Notification.created_at.desc())
                    )
                    notifications = notif_result.scalars().all()

                    # Only send if there are notifications
                    if notifications:
                        success = await email_service.send_digest_email(
                            to_email=user.email,
                            notifications=notifications,
                            frequency='weekly'
                        )

                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1

                except Exception as e:
                    logger.error(f"Failed to send weekly digest to {user.email}: {str(e)}")
                    failed_count += 1

            logger.info(f"Weekly digest job completed: {sent_count} sent, {failed_count} failed")

    except Exception as e:
        logger.error(f"Weekly digest job failed: {str(e)}")
