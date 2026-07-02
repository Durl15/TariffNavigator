"""
Setup Stripe Products and Prices - Module 3
Creates Pro and Enterprise subscription products in Stripe
"""
from dotenv import load_dotenv
load_dotenv()

import os
import stripe

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def setup_stripe_products():
    """Create Stripe products and prices for TariffNavigator"""

    print("=" * 70)
    print("STRIPE PRODUCT SETUP - TariffNavigator")
    print("=" * 70)
    print()

    # Check API key
    if not stripe.api_key:
        print("ERROR: STRIPE_SECRET_KEY not found in .env file")
        return

    print(f"Using API Key: {stripe.api_key[:20]}...")
    print("Mode: TEST")
    print()

    try:
        # Create Pro Plan Product
        print("Creating Pro Plan...")
        pro_product = stripe.Product.create(
            name="TariffNavigator Pro",
            description="1,000 calculations/month, 10 watchlists, email alerts, external monitoring",
            metadata={
                "plan": "pro",
                "calculations_per_month": "1000",
                "watchlists": "10"
            }
        )

        # Create Pro Plan Price
        pro_price = stripe.Price.create(
            product=pro_product.id,
            unit_amount=4900,  # $49.00 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"plan": "pro"}
        )

        print(f"[OK] Pro Product Created: {pro_product.id}")
        print(f"[OK] Pro Price Created: {pro_price.id}")
        print(f"  Amount: ${pro_price.unit_amount / 100:.2f}/month")
        print()

        # Create Enterprise Plan Product
        print("Creating Enterprise Plan...")
        enterprise_product = stripe.Product.create(
            name="TariffNavigator Enterprise",
            description="10,000 calculations/month, unlimited watchlists, AI insights, API access, priority support",
            metadata={
                "plan": "enterprise",
                "calculations_per_month": "10000",
                "watchlists": "unlimited"
            }
        )

        # Create Enterprise Plan Price
        enterprise_price = stripe.Price.create(
            product=enterprise_product.id,
            unit_amount=19900,  # $199.00 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"plan": "enterprise"}
        )

        print(f"[OK] Enterprise Product Created: {enterprise_product.id}")
        print(f"[OK] Enterprise Price Created: {enterprise_price.id}")
        print(f"  Amount: ${enterprise_price.unit_amount / 100:.2f}/month")
        print()

        # Display results
        print("=" * 70)
        print("SUCCESS! Products and Prices Created")
        print("=" * 70)
        print()
        print("Add these to your backend/.env file:")
        print()
        # Create Consultant Plan Product
        print("Creating Consultant Plan...")
        consultant_product = stripe.Product.create(
            name="TariffNavigator Consultant",
            description="Unlimited everything, white-label exports, 50 users, API access, priority support",
            metadata={"plan": "consultant", "users": "50"}
        )
        consultant_price = stripe.Price.create(
            product=consultant_product.id,
            unit_amount=49900,  # $499.00 in cents
            currency="usd",
            recurring={"interval": "month"},
            metadata={"plan": "consultant"}
        )
        print(f"[OK] Consultant Product Created: {consultant_product.id}")
        print(f"[OK] Consultant Price Created: {consultant_price.id}")
        print()

        print(f"STRIPE_PRICE_ID_PRO={pro_price.id}")
        print(f"STRIPE_PRICE_ID_ENTERPRISE={enterprise_price.id}")
        print(f"STRIPE_PRICE_ID_CONSULTANT={consultant_price.id}")
        print()
        print("=" * 70)
        print()
        print("View in Stripe Dashboard:")
        print(f"  Pro Plan:     https://dashboard.stripe.com/test/products/{pro_product.id}")
        print(f"  Enterprise:   https://dashboard.stripe.com/test/products/{enterprise_product.id}")
        print(f"  Consultant:   https://dashboard.stripe.com/test/products/{consultant_product.id}")
        print()

        return {
            "pro_price_id": pro_price.id,
            "enterprise_price_id": enterprise_price.id,
            "consultant_price_id": consultant_price.id,
        }

    except stripe.error.StripeError as e:
        print(f"ERROR: {str(e)}")
        return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None


if __name__ == "__main__":
    setup_stripe_products()
