from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.db.session import get_db
from app.models.models import ClassificationHistory, CostCalculationHistory

router = APIRouter()

@router.get("/classifications")
async def get_classification_history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ClassificationHistory)
        .order_by(desc(ClassificationHistory.created_at))
        .limit(limit)
    )
    history = result.scalars().all()
    return [
        {
            "id": h.id,
            "product_description": h.product_description,
            "hts_code": h.suggested_hts_code,
            "confidence": float(h.confidence_score) if h.confidence_score else None,
            "created_at": h.created_at.isoformat() if h.created_at else None
        }
        for h in history
    ]

@router.get("/costs")
async def get_cost_history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CostCalculationHistory)
        .order_by(desc(CostCalculationHistory.created_at))
        .limit(limit)
    )
    return result.scalars().all()
