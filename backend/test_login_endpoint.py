"""
Test script to simulate the login endpoint behavior
"""
import asyncio
from app.services.auth import authenticate_user, create_access_token
from app.db.session import get_db
from datetime import timedelta

async def test_login():
    async for db in get_db():
        try:
            # Simulate login request
            email = "admin@test.com"
            password = "admin123"

            print(f"1. Authenticating user: {email}")
            user = await authenticate_user(db, email, password)

            if not user:
                print("ERROR: Authentication failed")
                return

            print(f"2. User authenticated: {user.id}, {user.email}, role={user.role}")

            # Create token
            print("3. Creating access token...")
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user.email},
                expires_delta=access_token_expires
            )

            print(f"4. Token created successfully: {access_token[:50]}...")

            # Simulate response
            response = {
                "access_token": access_token,
                "token_type": "bearer"
            }
            print(f"5. Response would be: {response}")
            print("\nSUCCESS - Login endpoint simulation completed")

        except Exception as e:
            print(f"ERROR during login: {str(e)}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_login())
