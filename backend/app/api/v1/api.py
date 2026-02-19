from fastapi import APIRouter
from app.api.v1.endpoints import tariff, export, stats
from app.api.endpoints import auth, admin

api_router = APIRouter()
api_router.include_router(tariff.router, prefix="/tariff", tags=["tariff"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])