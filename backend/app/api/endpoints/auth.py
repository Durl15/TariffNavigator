from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.services.auth import (
    authenticate_user, create_user, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user_from_token
)
from app.models.user import User
from app.models.calculation import Calculation
from app.models.tool_analysis import ToolAnalysis
from sqlalchemy import select, func

router = APIRouter()
security = HTTPBearer()

# Dependency to get current user from JWT token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate JWT token, return current user"""
    token = credentials.credentials
    return await get_current_user_from_token(token, db)

# Request models
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None

@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await create_user(db, request.email, request.password, request.full_name)
    return {"message": "User created successfully", "user_id": user.id}

@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user information with usage stats."""
    # Count calculator lookups this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    calc_result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.user_id == current_user.id,
            Calculation.created_at >= month_start,
        )
    )
    monthly_calculations = calc_result.scalar() or 0

    # Count saved analyses
    saved_result = await db.execute(
        select(func.count(ToolAnalysis.id)).where(ToolAnalysis.user_id == current_user.id)
    )
    saved_analyses = saved_result.scalar() or 0

    # Tier limits
    tier_limits = {
        'free': 10, 'pro': None, 'enterprise': None, 'consultant': None,
        'user': 10, 'admin': None, 'superadmin': None, 'viewer': 5,
    }
    lookup_limit = tier_limits.get(current_user.role, 10)

    preferences = current_user.preferences or {}

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": preferences.get("company_name"),
        "role": current_user.role,
        "is_active": current_user.is_active,
        "organization_id": current_user.organization_id,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "usage": {
            "monthly_calculations": monthly_calculations,
            "lookup_limit": lookup_limit,
            "saved_analyses": saved_analyses,
        },
    }


@router.put("/me")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile."""
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.company_name is not None:
        prefs = dict(current_user.preferences or {})
        prefs["company_name"] = request.company_name
        current_user.preferences = prefs
    await db.commit()
    await db.refresh(current_user)
    return {"message": "Profile updated successfully"}
