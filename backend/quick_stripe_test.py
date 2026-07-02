from dotenv import load_dotenv
load_dotenv()
import os
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

try:
    customers = stripe.Customer.list(limit=1)
    print('=' * 60)
    print('SUCCESS: Stripe API connection working!')
    print('=' * 60)
    print(f'API Key: {stripe.api_key[:20]}...')
    print('Test Mode: Yes')
    print('\nNext step: Create product prices in Stripe Dashboard')
    print('  Go to: https://dashboard.stripe.com/test/products')
except Exception as e:
    print(f'ERROR: {str(e)}')
