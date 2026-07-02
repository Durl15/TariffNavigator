import asyncio
from app.services.auth import authenticate_user
from app.db.session import get_db

async def test_auth():
    async for db in get_db():
        try:
            user = await authenticate_user(db, 'admin@test.com', 'admin123')
            if user:
                print("OK - Authentication successful!")
                print(f"User ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Role: {user.role}")
            else:
                print("FAIL - Authentication failed - user not found or wrong password")
        except Exception as e:
            print(f"ERROR - Error during authentication: {str(e)}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_auth())
