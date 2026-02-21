"""
Test Stripe Connection - Module 3 Phase 1
Verify Stripe SDK is working correctly
"""
import asyncio
from app.services.stripe_service import stripe_service
from app.core.config import settings


def test_stripe_connection():
    """Test basic Stripe API connection"""
    print("=" * 60)
    print("STRIPE CONNECTION TEST")
    print("=" * 60)

    # Check if API key is set
    if not settings.STRIPE_SECRET_KEY:
        print("❌ STRIPE_SECRET_KEY not set in environment")
        print("\nTo set up Stripe:")
        print("1. Go to https://dashboard.stripe.com/test/apikeys")
        print("2. Copy your secret key (starts with sk_test_)")
        print("3. Add to .env file: STRIPE_SECRET_KEY=sk_test_...")
        return False

    print(f"\n✓ Stripe API key configured")
    print(f"  Key: {settings.STRIPE_SECRET_KEY[:12]}...")

    # Test connection
    print("\nTesting Stripe API connection...")
    try:
        success = stripe_service.test_connection()
        if success:
            print("✓ Stripe API connection successful!")
            print("\n✅ Phase 1 Stripe setup COMPLETE")
            print("\nNext steps:")
            print("  - Configure STRIPE_PUBLISHABLE_KEY")
            print("  - Configure STRIPE_WEBHOOK_SECRET")
            print("  - Create price IDs in Stripe Dashboard")
            return True
        else:
            print("❌ Stripe API connection failed")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    test_stripe_connection()
