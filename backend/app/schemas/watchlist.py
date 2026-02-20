from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class WatchlistCreate(BaseModel):
    """Schema for creating a new watchlist."""
    name: str = Field(..., min_length=1, max_length=255, description="Watchlist name")
    description: Optional[str] = Field(None, description="Optional description")
    hs_codes: List[str] = Field(..., min_items=1, description="List of HS codes to watch")
    countries: List[str] = Field(..., min_items=1, description="List of countries to watch")
    alert_preferences: Optional[Dict[str, Any]] = Field(
        default={'email': True, 'digest': 'daily'},
        description="Alert preferences (email, digest frequency)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "China Electronics",
                "description": "Monitor electronics tariffs from China",
                "hs_codes": ["8517.13", "8471.30"],
                "countries": ["CN"],
                "alert_preferences": {
                    "email": True,
                    "digest": "daily"
                }
            }
        }


class WatchlistUpdate(BaseModel):
    """Schema for updating an existing watchlist."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    hs_codes: Optional[List[str]] = Field(None, min_items=1)
    countries: Optional[List[str]] = Field(None, min_items=1)
    alert_preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Watchlist Name",
                "is_active": True
            }
        }


class WatchlistResponse(BaseModel):
    """Schema for watchlist response."""
    id: str
    name: str
    description: Optional[str]
    hs_codes: List[str]
    countries: List[str]
    alert_preferences: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "China Electronics",
                "description": "Monitor electronics tariffs from China",
                "hs_codes": ["8517.13", "8471.30"],
                "countries": ["CN"],
                "alert_preferences": {"email": True, "digest": "daily"},
                "is_active": True,
                "created_at": "2026-02-20T12:00:00Z",
                "updated_at": None
            }
        }


class WatchlistListResponse(BaseModel):
    """Schema for paginated watchlist list."""
    watchlists: List[WatchlistResponse]
    total: int
    page: int
    page_size: int

    class Config:
        json_schema_extra = {
            "example": {
                "watchlists": [],
                "total": 5,
                "page": 1,
                "page_size": 20
            }
        }
