"""
Subscription Feature Matrix - Module 3 Phase 3
Defines which features are available for each subscription plan
"""
from enum import Enum
from typing import Dict, List


class Feature(str, Enum):
    """Available features that can be gated by subscription plan"""
    BASIC_CALCULATIONS = "basic_calculations"
    WATCHLISTS = "watchlists"
    EMAIL_ALERTS = "email_alerts"
    EXTERNAL_MONITORING = "external_monitoring"
    PDF_EXPORT = "pdf_export"
    CSV_EXPORT = "csv_export"
    API_ACCESS = "api_access"
    AI_INSIGHTS = "ai_insights"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_INTEGRATIONS = "custom_integrations"


PLAN_FEATURES: Dict[str, List[Feature]] = {
    "free": [
        Feature.BASIC_CALCULATIONS,
        # Free users can view but not create additional watchlists
    ],
    "pro": [
        Feature.BASIC_CALCULATIONS,
        Feature.WATCHLISTS,
        Feature.EMAIL_ALERTS,
        Feature.EXTERNAL_MONITORING,
        Feature.PDF_EXPORT,
        Feature.CSV_EXPORT,
    ],
    "enterprise": [
        Feature.BASIC_CALCULATIONS,
        Feature.WATCHLISTS,
        Feature.EMAIL_ALERTS,
        Feature.EXTERNAL_MONITORING,
        Feature.PDF_EXPORT,
        Feature.CSV_EXPORT,
        Feature.API_ACCESS,
        Feature.AI_INSIGHTS,
        Feature.PRIORITY_SUPPORT,
        Feature.CUSTOM_INTEGRATIONS,
    ]
}


PLAN_QUOTAS = {
    "free": {
        "calculations_per_month": 100,
        "watchlists": 1,
        "saved_calculations": 10,
        "comparisons_per_month": 50,
    },
    "pro": {
        "calculations_per_month": 1000,
        "watchlists": 10,
        "saved_calculations": 100,
        "comparisons_per_month": 500,
    },
    "enterprise": {
        "calculations_per_month": 10000,
        "watchlists": 999999,  # Effectively unlimited
        "saved_calculations": 999999,
        "comparisons_per_month": 999999,
    }
}


def has_feature(plan: str, feature: Feature) -> bool:
    """
    Check if a subscription plan has access to a specific feature.

    Args:
        plan: Plan name ('free', 'pro', 'enterprise')
        feature: Feature to check

    Returns:
        True if plan has access to feature, False otherwise
    """
    return feature in PLAN_FEATURES.get(plan, [])


def get_quota_limit(plan: str, quota_type: str) -> int:
    """
    Get the quota limit for a specific plan and quota type.

    Args:
        plan: Plan name ('free', 'pro', 'enterprise')
        quota_type: Type of quota ('calculations_per_month', 'watchlists', etc.)

    Returns:
        Quota limit as integer, 0 if not found
    """
    return PLAN_QUOTAS.get(plan, {}).get(quota_type, 0)


def get_plan_features(plan: str) -> List[Feature]:
    """
    Get all features available for a plan.

    Args:
        plan: Plan name ('free', 'pro', 'enterprise')

    Returns:
        List of available features
    """
    return PLAN_FEATURES.get(plan, [])


def get_plan_quotas(plan: str) -> Dict[str, int]:
    """
    Get all quotas for a plan.

    Args:
        plan: Plan name ('free', 'pro', 'enterprise')

    Returns:
        Dictionary of quota limits
    """
    return PLAN_QUOTAS.get(plan, {})
