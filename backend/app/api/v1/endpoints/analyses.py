"""
Saved Tool Analyses API
Save and retrieve compliance tool analysis results.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.tool_analysis import ToolAnalysis

router = APIRouter()

VALID_TOOL_TYPES = {"cashflow", "drawback", "usmca", "supply_chain", "hts_audit", "sourcing", "scenario"}


class SaveAnalysisRequest(BaseModel):
    tool_type: str
    title: str
    form_data: Optional[dict] = None
    result_data: dict


class AnalysisResponse(BaseModel):
    id: str
    tool_type: str
    title: str
    form_data: Optional[dict]
    result_data: dict
    created_at: str


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def save_analysis(
    request: SaveAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a compliance tool analysis result."""
    if request.tool_type not in VALID_TOOL_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tool_type. Must be one of: {', '.join(sorted(VALID_TOOL_TYPES))}"
        )

    analysis = ToolAnalysis(
        user_id=current_user.id,
        tool_type=request.tool_type,
        title=request.title,
        form_data=request.form_data,
        result_data=request.result_data,
        created_at=datetime.utcnow(),
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return AnalysisResponse(**analysis.to_dict())


@router.get("", response_model=List[AnalysisResponse])
async def list_analyses(
    tool_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List saved analyses for the current user."""
    stmt = select(ToolAnalysis).where(ToolAnalysis.user_id == current_user.id)
    if tool_type:
        stmt = stmt.where(ToolAnalysis.tool_type == tool_type)
    stmt = stmt.order_by(ToolAnalysis.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    analyses = result.scalars().all()
    return [AnalysisResponse(**a.to_dict()) for a in analyses]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single saved analysis."""
    result = await db.execute(
        select(ToolAnalysis).where(
            ToolAnalysis.id == analysis_id,
            ToolAnalysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return AnalysisResponse(**analysis.to_dict())


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a saved analysis."""
    result = await db.execute(
        select(ToolAnalysis).where(
            ToolAnalysis.id == analysis_id,
            ToolAnalysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    await db.delete(analysis)
    await db.commit()
