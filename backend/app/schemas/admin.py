"""
Admin Panel Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============================================================================
# USER MANAGEMENT SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = Field(default='user', pattern='^(viewer|user|admin|superadmin)$')
    organization_id: Optional[str] = None
    is_active: bool = True

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern='^(viewer|user|admin|superadmin)$')
    organization_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    organization_id: Optional[str]
    organization_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_email_verified: bool
    last_login_at: Optional[datetime]
    login_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# ORGANIZATION MANAGEMENT SCHEMAS
# ============================================================================

class OrganizationCreate(BaseModel):
    """Schema for creating organization"""
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern='^[a-z0-9-]+$')
    plan: str = Field(default='free', pattern='^(free|pro|enterprise)$')
    max_users: int = Field(default=5, ge=1, le=9999)
    max_calculations_per_month: int = Field(default=100, ge=0)
    settings: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    """Schema for updating organization"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    plan: Optional[str] = Field(None, pattern='^(free|pro|enterprise)$')
    status: Optional[str] = Field(None, pattern='^(active|suspended|deleted)$')
    max_users: Optional[int] = Field(None, ge=1, le=9999)
    max_calculations_per_month: Optional[int] = Field(None, ge=0)
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseModel):
    """Schema for organization response"""
    id: str
    name: str
    slug: str
    plan: str
    status: str
    max_users: int
    max_calculations_per_month: int
    user_count: Optional[int] = 0
    calculation_count_this_month: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AUDIT LOG SCHEMAS
# ============================================================================

class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    user_id: Optional[str]
    user_email: Optional[str]
    organization_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    changes: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    status_code: Optional[int]
    duration_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list"""
    logs: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# SYSTEM STATISTICS SCHEMAS
# ============================================================================

class SystemStats(BaseModel):
    """Schema for system statistics"""
    total_users: int
    active_users: int
    total_organizations: int
    total_calculations: int
    calculations_this_month: int
    calculations_today: int
    total_shared_links: int
    active_api_keys: int
    storage_used_mb: Optional[float] = 0

    # Growth metrics
    users_last_7_days: int = 0
    calculations_last_7_days: int = 0

    # Performance metrics
    avg_calculation_time_ms: Optional[float] = 0
    avg_api_response_time_ms: Optional[float] = 0


class UserActivityStats(BaseModel):
    """Schema for user activity statistics"""
    date: str
    new_users: int
    active_users: int
    calculations: int


class PopularHSCodes(BaseModel):
    """Schema for popular HS codes"""
    hs_code: str
    description: str
    usage_count: int
    last_used: datetime


# ============================================================================
# BULK ACTION SCHEMAS
# ============================================================================

class BulkActionRequest(BaseModel):
    """Schema for bulk actions"""
    user_ids: List[str]
    action: str = Field(..., pattern='^(activate|deactivate|delete|change_role)$')
    role: Optional[str] = Field(None, pattern='^(viewer|user|admin)$')


class BulkActionResponse(BaseModel):
    """Schema for bulk action response"""
    success_count: int
    failed_count: int
    errors: List[str] = []
