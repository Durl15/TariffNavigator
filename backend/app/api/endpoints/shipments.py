from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.schemas import ShipmentCreate, ShipmentResponse
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=ShipmentResponse)
async def create_shipment(shipment: ShipmentCreate, db: AsyncSession = Depends(get_db)):
    return {"status": "created", "id": "mock-id", "total_landed_cost": 0, "cost_breakdown": {}, "created_at": "2024-01-01"}

@router.get("/", response_model=List[ShipmentResponse])
async def list_shipments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return []
