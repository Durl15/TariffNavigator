from typing import Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, func
from app.models.rate_limit import RateLimit, RateLimitViolation
import uuid


class RateLimiterService:
    """
    Core rate limiting service using sliding window algorithm.
    Database-backed for now, can migrate to Redis later without changing API.
    """

    async def check_rate_limit(
        self,
        db: AsyncSession,
        identifier: str,
        identifier_type: str,  # 'ip' or 'user'
        limit: int,
        window_seconds: int = 60
    ) -> Tuple[bool, int, datetime]:
        """
        Check if identifier is within rate limit using sliding window algorithm.

        Args:
            db: Database session
            identifier: IP address or user_id
            identifier_type: Type of identifier ('ip' or 'user')
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds (default 60 = 1 minute)

        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
                - is_allowed: True if request should be allowed
                - remaining_requests: Number of requests remaining in window
                - reset_time: When the current window will reset
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        window_end = now + timedelta(seconds=window_seconds)

        # Query for existing rate limit record in current window
        stmt = select(RateLimit).where(
            and_(
                RateLimit.identifier == identifier,
                RateLimit.identifier_type == identifier_type,
                RateLimit.window_start >= window_start,
                RateLimit.window_end > now
            )
        ).order_by(RateLimit.window_start.desc())

        result = await db.execute(stmt)
        rate_limit_record = result.scalar_one_or_none()

        if rate_limit_record:
            # Existing window found - check if limit exceeded
            if rate_limit_record.request_count >= limit:
                # Limit exceeded
                remaining = 0
                reset_time = rate_limit_record.window_end
                return False, remaining, reset_time
            else:
                # Still under limit - increment count
                rate_limit_record.request_count += 1
                await db.commit()

                remaining = limit - rate_limit_record.request_count
                reset_time = rate_limit_record.window_end
                return True, remaining, reset_time
        else:
            # No existing window - create new one
            new_rate_limit = RateLimit(
                id=str(uuid.uuid4()),
                identifier=identifier,
                identifier_type=identifier_type,
                request_count=1,
                window_start=now,
                window_end=window_end
            )
            db.add(new_rate_limit)
            await db.commit()

            remaining = limit - 1
            reset_time = window_end
            return True, remaining, reset_time

    async def log_violation(
        self,
        db: AsyncSession,
        identifier: str,
        identifier_type: str,
        violation_type: str,  # 'ip_rate', 'user_rate', 'quota'
        attempted_count: int,
        limit: int,
        endpoint: str,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a rate limit violation for security monitoring and analytics.

        Args:
            db: Database session
            identifier: IP, user_id, or organization_id
            identifier_type: Type of identifier ('ip', 'user', 'organization')
            violation_type: Type of violation ('ip_rate', 'user_rate', 'quota')
            attempted_count: Number of requests attempted
            limit: The limit that was exceeded
            endpoint: The endpoint being accessed
            user_id: User ID if known (optional)
            user_agent: Browser/client user agent (optional)
        """
        violation = RateLimitViolation(
            id=str(uuid.uuid4()),
            identifier=identifier,
            identifier_type=identifier_type,
            user_id=user_id,
            violation_type=violation_type,
            attempted_count=attempted_count,
            limit=limit,
            endpoint=endpoint,
            user_agent=user_agent
        )
        db.add(violation)
        await db.commit()

    async def cleanup_old_records(self, db: AsyncSession, days: int = 7):
        """
        Clean up old rate limit records to prevent database bloat.
        This should be run periodically (daily recommended).

        Args:
            db: Database session
            days: Number of days to retain records (default 7)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old rate limit records
        stmt = delete(RateLimit).where(RateLimit.created_at < cutoff_date)
        result = await db.execute(stmt)
        await db.commit()

        deleted_count = result.rowcount
        return deleted_count

    async def cleanup_old_violations(self, db: AsyncSession, days: int = 30):
        """
        Clean up old violation logs.
        Keep violations longer than rate limit records for security analysis.

        Args:
            db: Database session
            days: Number of days to retain violation logs (default 30)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old violations
        stmt = delete(RateLimitViolation).where(RateLimitViolation.created_at < cutoff_date)
        result = await db.execute(stmt)
        await db.commit()

        deleted_count = result.rowcount
        return deleted_count

    async def get_violation_stats(
        self,
        db: AsyncSession,
        hours: int = 24,
        violation_type: Optional[str] = None
    ):
        """
        Get statistics about rate limit violations.

        Args:
            db: Database session
            hours: Number of hours to look back (default 24)
            violation_type: Filter by specific violation type (optional)

        Returns:
            List of violation records
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        stmt = select(RateLimitViolation).where(
            RateLimitViolation.created_at >= cutoff_time
        )

        if violation_type:
            stmt = stmt.where(RateLimitViolation.violation_type == violation_type)

        stmt = stmt.order_by(RateLimitViolation.created_at.desc())

        result = await db.execute(stmt)
        violations = result.scalars().all()
        return violations

    async def get_top_violators(
        self,
        db: AsyncSession,
        days: int = 7,
        limit: int = 20
    ):
        """
        Get top rate limit violators by identifier.

        Args:
            db: Database session
            days: Number of days to analyze (default 7)
            limit: Maximum number of results (default 20)

        Returns:
            List of tuples (identifier, identifier_type, violation_count)
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        stmt = select(
            RateLimitViolation.identifier,
            RateLimitViolation.identifier_type,
            func.count(RateLimitViolation.id).label('violation_count')
        ).where(
            RateLimitViolation.created_at >= cutoff_time
        ).group_by(
            RateLimitViolation.identifier,
            RateLimitViolation.identifier_type
        ).order_by(
            func.count(RateLimitViolation.id).desc()
        ).limit(limit)

        result = await db.execute(stmt)
        top_violators = result.all()
        return top_violators
