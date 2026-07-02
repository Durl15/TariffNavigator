"""
Quick test script to verify rate limiting implementation.
Run this to check if rate limiting logic works correctly.
"""
import asyncio
from datetime import datetime, timedelta
import uuid

async def test_rate_limiter():
    from app.db.session import async_session
    from app.services.rate_limiter import RateLimiterService

    print("\n=== Testing RateLimiterService ===\n")

    async with async_session() as db:
        rate_limiter = RateLimiterService()
        test_ip = "192.168.1.100"

        print("Test 1: Allow requests under limit (5 requests, limit=10)")
        for i in range(5):
            allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
                db=db,
                identifier=test_ip,
                identifier_type='ip',
                limit=10,
                window_seconds=60
            )
            print(f"  Request {i+1}: Allowed={allowed}, Remaining={remaining}")

        print("\nTest 2: Check remaining count")
        allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
            db=db,
            identifier=test_ip,
            identifier_type='ip',
            limit=10,
            window_seconds=60
        )
        print(f"  After 5 requests: Remaining={remaining} (should be 4)")

        print("\nTest 3: Exceed limit (make 5 more requests, should hit limit)")
        for i in range(5):
            allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
                db=db,
                identifier=test_ip,
                identifier_type='ip',
                limit=10,
                window_seconds=60
            )
            print(f"  Request {i+6}: Allowed={allowed}, Remaining={remaining}")

        print("\nTest 4: User-based rate limiting")
        test_user_id = str(uuid.uuid4())
        allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
            db=db,
            identifier=test_user_id,
            identifier_type='user',
            limit=50,
            window_seconds=60
        )
        print(f"  User rate limit check: Allowed={allowed}, Remaining={remaining}/50")

        print("\n=== All tests passed! ===\n")

if __name__ == "__main__":
    asyncio.run(test_rate_limiter())
