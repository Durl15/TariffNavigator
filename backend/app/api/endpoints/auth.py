from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import secrets

from app.db.session import get_db
from app.services.auth import (
    authenticate_user, create_user, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user_from_token
)
from app.models.user import User
from app.models.calculation import Calculation
from app.models.tool_analysis import ToolAnalysis
from app.services.email_service import email_service
from app.core.config import settings
from sqlalchemy import select, func
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await create_user(db, request.email, request.password, request.full_name)

    # Auto-login: return access token so frontend can skip the login step
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"message": "Account created successfully", "user_id": user.id, "access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Send password reset email. Always returns success to avoid email enumeration."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        await db.commit()

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        try:
            await email_service.send_password_reset_email(
                to_email=user.email,
                user_name=user.full_name or user.email,
                reset_url=reset_url,
            )
        except Exception:
            pass  # Don't expose email errors

    return {"message": "If that email address is registered, you'll receive a reset link shortly."}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using a valid reset token."""
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    result = await db.execute(
        select(User).where(User.password_reset_token == request.token)
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_reset_expires or user.password_reset_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset link. Please request a new one.")

    user.hashed_password = pwd_context.hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await db.commit()

    return {"message": "Password reset successfully. You can now log in."}

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
    try:
        calc_result = await db.execute(
            select(func.count(Calculation.id)).where(
                Calculation.user_id == current_user.id,
                Calculation.created_at >= month_start,
            )
        )
        monthly_calculations = calc_result.scalar() or 0
    except Exception:
        await db.rollback()
        monthly_calculations = 0

    # Count saved analyses
    try:
        saved_result = await db.execute(
            select(func.count(ToolAnalysis.id)).where(ToolAnalysis.user_id == current_user.id)
        )
        saved_analyses = saved_result.scalar() or 0
    except Exception:
        await db.rollback()
        saved_analyses = 0

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
