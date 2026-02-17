from fastapi import APIRouter
from app.api.endpoints import auth, hs_codes, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(hs_codes.router, prefix="/hs-codes", tags=["hs-codes"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
