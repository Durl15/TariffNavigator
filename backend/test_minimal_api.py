"""
Minimal FastAPI test to isolate the 500 error issue
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Minimal Test API")

# Simple CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import database session
from app.db.session import get_db
from app.models.user import User

@app.get("/health")
def health():
    logger.info("=== HEALTH ENDPOINT CALLED ===")
    return {"status": "ok"}

@app.get("/test-db")
async def test_database(db: AsyncSession = Depends(get_db)):
    """Test database connectivity"""
    logger.info("=== TEST-DB ENDPOINT CALLED ===")
    try:
        logger.info("About to execute raw SQL query...")
        result = await db.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        logger.info(f"Raw SQL query successful: {row}")

        logger.info("About to query User table...")
        stmt = select(User).limit(1)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        logger.info(f"User query successful: {user.email if user else 'No users'}")

        return {
            "status": "success",
            "raw_query": row[0] if row else None,
            "user_found": user.email if user else None
        }
    except Exception as e:
        logger.error(f"ERROR in test-db: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

@app.post("/test-auth")
async def test_auth(db: AsyncSession = Depends(get_db)):
    """Test authentication flow"""
    logger.info("=== TEST-AUTH ENDPOINT CALLED ===")
    try:
        from app.services.auth import authenticate_user, create_access_token
        from datetime import timedelta

        logger.info("Authenticating user...")
        user = await authenticate_user(db, "admin@test.com", "admin123")

        if not user:
            logger.warning("Authentication failed")
            return {"status": "auth_failed"}

        logger.info(f"User authenticated: {user.email}")

        logger.info("Creating access token...")
        token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=30)
        )

        logger.info("Token created successfully")
        return {
            "status": "success",
            "user_email": user.email,
            "token_preview": token[:50] + "..."
        }
    except Exception as e:
        logger.error(f"ERROR in test-auth: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
