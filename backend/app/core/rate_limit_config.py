"""
Rate Limiting Configuration

Defines rate limits and quotas for different user roles and organization plans.
"""

# ============================================================================
# IP-BASED RATE LIMITS (requests per minute)
# ============================================================================
# Applied to ALL requests before authentication via RateLimitMiddleware

IP_RATE_LIMITS = {
    "global": 100,  # All IPs limited to 100 requests/minute
}


# ============================================================================
# USER-BASED RATE LIMITS BY ROLE (requests per minute)
# ============================================================================
# Applied to authenticated endpoints via check_user_rate_limit dependency
# Tiered limits based on user role

USER_RATE_LIMITS_BY_ROLE = {
    "viewer": 50,       # Read-only access, lower limit
    "user": 100,        # Standard user, default limit
    "admin": 500,       # Admin users, higher limit
    "superadmin": 999999,  # Effectively unlimited for superadmins
}


# ============================================================================
# ORGANIZATION QUOTA LIMITS BY PLAN (calculations per month)
# ============================================================================
# Applied to calculation endpoints via check_calculation_quota dependency
# Monthly limits reset on the 1st of each month

QUOTA_LIMITS_BY_PLAN = {
    "free": 100,           # Free tier: 100 calculations/month
    "pro": 1000,           # Pro tier: 1000 calculations/month
    "enterprise": 10000,   # Enterprise: 10,000 calculations/month
}


# ============================================================================
# CLEANUP SETTINGS
# ============================================================================
# How long to retain rate limiting data

RATE_LIMIT_CLEANUP_DAYS = 7         # Delete rate limit records older than 7 days
VIOLATION_LOG_RETENTION_DAYS = 30   # Keep violation logs for 30 days (security)


# ============================================================================
# RATE LIMIT WINDOW SETTINGS
# ============================================================================

RATE_LIMIT_WINDOW_SECONDS = 60  # 1 minute sliding window


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_rate_limit(user_role: str) -> int:
    """
    Get rate limit for a specific user role.
    Falls back to default user limit if role not found.

    Args:
        user_role: User's role string

    Returns:
        Rate limit (requests per minute)
    """
    return USER_RATE_LIMITS_BY_ROLE.get(user_role, USER_RATE_LIMITS_BY_ROLE["user"])


def get_quota_limit(plan: str) -> int:
    """
    Get monthly quota limit for an organization plan.
    Falls back to free tier if plan not found.

    Args:
        plan: Organization plan string

    Returns:
        Monthly quota limit (calculations per month)
    """
    return QUOTA_LIMITS_BY_PLAN.get(plan, QUOTA_LIMITS_BY_PLAN["free"])
