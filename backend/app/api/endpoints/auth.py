from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.services.auth import (
    authenticate_user, create_user, create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User
from sqlalchemy import select

router = APIRouter()

# Request models
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = None

class LoginRequest(BaseModel):
    email: str
    password: str

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
async def read_users_me(current_user: User = Depends(get_db)):
    # Simplified - just return first user for now
    result = await get_db()
    async for db in result:
        user = await db.execute(select(User))
        first_user = user.scalar_one_or_none()
        if first_user:
            return {
                "id": first_user.id,
                "email": first_user.email,
                "full_name": first_user.full_name
            }
    return {"message": "No users found"}
