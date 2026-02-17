from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.crud import tariff as crud_tariff
from app.schemas.tariff import (
    TariffResponse, 
    TariffSearchResult, 
    TariffRateRequest, 
    TariffRateResponse
)
from decimal import Decimal

router = APIRouter()


@router.get("/search", response_model=TariffSearchResult)
async def search_tariffs(
    hs_code: str = Query(..., min_length=2, description="HS code to search"),
    origin: Optional[str] = Query(None, regex="^(CN|US|EU)$", description="Origin country code"),
    destination: Optional[str] = Query(None, regex="^(CN|US|EU)$", description="Destination country code"),
    rate_type: Optional[str] = Query(None, description="Rate type: MFN, USMCA, RCEP, GSP"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search tariff rates by HS code and trade lane.
    
    Examples:
    - /tariffs/search?hs_code=8703.23.00&origin=CN&destination=US
    - /tariffs/search?hs_code=8517.13.00&origin=US&destination=EU
    """
    results = await crud_tariff.search_tariffs(
        db, hs_code=hs_code, origin=origin, destination=destination, rate_type=rate_type
    )
    
    return TariffSearchResult(
        results=results,
        total=len(results),
        query={"hs_code": hs_code, "origin": origin, "destination": destination, "rate_type": rate_type}
    )


@router.post("/calculate", response_model=TariffRateResponse)
async def calculate_tariff(
    request: TariffRateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate applicable tariff rates for a shipment.
    
    Returns all applicable rates and identifies the best (lowest) rate.
    """
    rates = await crud_tariff.get_applicable_tariffs(
        db, 
        hs_code=request.hs_code,
        origin=request.origin,
        destination=request.destination
    )
    
    if not rates:
        raise HTTPException(
            status_code=404, 
            detail=f"No tariff rates found for {request.hs_code} from {request.origin} to {request.destination}"
        )
    
    best_rate = rates[0] if rates else None
    estimated_duty = None
    
    if best_rate and request.value:
        estimated_duty = (request.value * best_rate.duty_rate) / 100
    
    return TariffRateResponse(
        hs_code=request.hs_code,
        origin=request.origin,
        destination=request.destination,
        applicable_rates=rates,
        best_rate=best_rate,
        estimated_duty=estimated_duty
    )


@router.get("/trade-lanes", response_model=List[dict])
async def get_supported_trade_lanes():
    """
    Get list of supported trade lanes for the MVP.
    """
    return [
        {"origin": "CN", "destination": "US", "name": "China to US", "fta": None},
        {"origin": "US", "destination": "CN", "name": "US to China", "fta": None},
        {"origin": "US", "destination": "EU", "name": "US to EU", "fta": None},
        {"origin": "EU", "destination": "US", "name": "EU to US", "fta": None},
    ]
