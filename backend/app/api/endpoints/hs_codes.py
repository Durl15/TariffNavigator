from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.crud import hs_code as crud_hs
from app.schemas.hs_code import HSCodeResponse, HSCodeSearchResult

router = APIRouter()


@router.get("/search", response_model=HSCodeSearchResult)
async def search_hs_codes(
    q: str = Query(..., min_length=2, description="Search query for HS code or description"),
    country: str = Query("US", regex="^(US|EU|CN)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    results = await crud_hs.search_hs_codes(db, query=q, country=country, limit=limit)
    
    return HSCodeSearchResult(
        results=results,
        total=len(results),
        query=q
    )


@router.get("/{code}", response_model=HSCodeResponse)
async def get_hs_code(
    code: str,
    country: str = Query("US", regex="^(US|EU|CN)$"),
    db: AsyncSession = Depends(get_db)
):
    hs_code = await crud_hs.get_hs_code_by_code(db, code=code, country=country)
    if not hs_code:
        raise HTTPException(status_code=404, detail="HS code not found")
    return hs_code


@router.get("/{code}/children", response_model=List[HSCodeResponse])
async def get_hs_code_children(
    code: str,
    country: str = Query("US", regex="^(US|EU|CN)$"),
    db: AsyncSession = Depends(get_db)
):
    children = await crud_hs.get_hs_code_children(db, parent_code=code, country=country)
    return children
