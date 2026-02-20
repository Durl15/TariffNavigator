from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NotificationResponse(BaseModel):
    """Schema for a single notification."""
    id: str
    type: str = Field(..., description="Notification type: rate_change, deadline, new_program")
    title: str
    message: str
    link: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "rate_change",
                "title": "Tariff Rate Change Detected",
                "message": "HS Code 8703.23 (CN): Rate increased from 5% to 7.5%",
                "link": "/tariff/8703.23",
                "data": {
                    "hs_code": "8703.23",
                    "country": "CN",
                    "old_rate": 5.0,
                    "new_rate": 7.5
                },
                "is_read": False,
                "read_at": None,
                "created_at": "2026-02-20T12:00:00Z"
            }
        }


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""
    notifications: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: Optional[int] = Field(None, description="Total unread notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "notifications": [],
                "total": 15,
                "page": 1,
                "page_size": 20,
                "unread_count": 3
            }
        }


class UnreadCountResponse(BaseModel):
    """Schema for unread notification count."""
    count: int = Field(..., description="Number of unread notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "count": 3
            }
        }


class MarkReadResponse(BaseModel):
    """Schema for mark as read response."""
    success: bool
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Notification marked as read"
            }
        }
