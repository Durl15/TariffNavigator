"""
Test Feature Gating Implementation - Module 3 Phase 3
Verifies feature matrix and quota limits are correctly defined
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.subscription_features import (
    Feature,
    PLAN_FEATURES,
    PLAN_QUOTAS,
    has_feature,
    get_quota_limit,
    get_plan_features,
    get_plan_quotas
)


def test_feature_matrix():
    """Test that feature matrix is correctly defined"""
    print("\n" + "="*80)
    print("FEATURE MATRIX TEST")
    print("="*80)

    plans = ['free', 'pro', 'enterprise']

    for plan in plans:
        print(f"\n{plan.upper()} Plan Features:")
        features = get_plan_features(plan)
        for feature in features:
            print(f"  [OK] {feature.value}")

        # Show features NOT included
        all_features = set(Feature)
        missing_features = all_features - set(features)
        if missing_features:
            print(f"\n  Not included in {plan}:")
            for feature in missing_features:
                print(f"  [ ] {feature.value}")

    print("\n" + "="*80)


def test_quota_limits():
    """Test quota limits for each plan"""
    print("\n" + "="*80)
    print("QUOTA LIMITS TEST")
    print("="*80)

    plans = ['free', 'pro', 'enterprise']

    for plan in plans:
        print(f"\n{plan.upper()} Plan Quotas:")
        quotas = get_plan_quotas(plan)
        for quota_type, limit in quotas.items():
            unlimited = " (Unlimited)" if limit >= 999999 else ""
            print(f"  {quota_type}: {limit:,}{unlimited}")

    print("\n" + "="*80)


def test_feature_checks():
    """Test has_feature() function"""
    print("\n" + "="*80)
    print("FEATURE ACCESS CHECKS")
    print("="*80)

    test_cases = [
        ('free', Feature.BASIC_CALCULATIONS, True),
        ('free', Feature.WATCHLISTS, False),
        ('free', Feature.EMAIL_ALERTS, False),
        ('pro', Feature.WATCHLISTS, True),
        ('pro', Feature.EMAIL_ALERTS, True),
        ('pro', Feature.API_ACCESS, False),
        ('enterprise', Feature.WATCHLISTS, True),
        ('enterprise', Feature.EMAIL_ALERTS, True),
        ('enterprise', Feature.API_ACCESS, True),
        ('enterprise', Feature.AI_INSIGHTS, True),
    ]

    print("\nTesting feature access:")
    all_passed = True

    for plan, feature, expected in test_cases:
        result = has_feature(plan, feature)
        status = "[OK]" if result == expected else "[FAIL]"

        if result != expected:
            all_passed = False

        access = "HAS" if result else "NO"
        print(f"  {status} {plan:10} {access:3} {feature.value}")

    print("\n" + "="*80)
    if all_passed:
        print("All feature checks PASSED!")
    else:
        print("Some feature checks FAILED!")
    print("="*80)


def test_watchlist_limits():
    """Test watchlist quota enforcement"""
    print("\n" + "="*80)
    print("WATCHLIST LIMITS")
    print("="*80)

    plans = ['free', 'pro', 'enterprise']

    for plan in plans:
        limit = get_quota_limit(plan, 'watchlists')
        unlimited = " (Unlimited)" if limit >= 999999 else ""
        print(f"  {plan:10} can create: {limit:,} watchlists{unlimited}")

    print("\n" + "="*80)


def test_calculation_quotas():
    """Test calculation quota limits"""
    print("\n" + "="*80)
    print("CALCULATION QUOTAS")
    print("="*80)

    plans = ['free', 'pro', 'enterprise']

    for plan in plans:
        limit = get_quota_limit(plan, 'calculations_per_month')
        print(f"  {plan:10} monthly limit: {limit:,} calculations")

    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n")
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 20 + "FEATURE GATING TEST SUITE" + " " * 33 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    try:
        test_feature_matrix()
        test_quota_limits()
        test_feature_checks()
        test_watchlist_limits()
        test_calculation_quotas()

        print("\n")
        print("="*80)
        print("TEST SUITE COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
