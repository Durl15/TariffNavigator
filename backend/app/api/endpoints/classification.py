from fastapi import APIRouter
from typing import List
import time

from app.schemas.schemas import ClassificationRequest, ClassificationResponse, HTSCodeSuggestion
from app.services.agents.trade_compliance import TradeComplianceEngine

router = APIRouter()

@router.post("/", response_model=ClassificationResponse)
async def classify_product(request: ClassificationRequest):
    start = time.time()
    engine = TradeComplianceEngine()
    suggestions = await engine.classify_product(request)
    
    # Convert dicts to proper schema objects
    suggestion_objects = [HTSCodeSuggestion(**s) for s in suggestions]
    
    return ClassificationResponse(
        suggestions=suggestion_objects,
        processing_time_ms=int((time.time() - start) * 1000)
    )
