"""
Admin Panel API Endpoints
Provides complete user management, organization management, and system statistics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, case
from typing import Optional, List
from datetime import datetime, timedelta
import math
import uuid

from app.db.session import get_db
from app.api.deps import get_current_admin_user, get_current_superuser
from app.models.user import User
from app.models.organization import Organization
from app.models.calculation import Calculation, AuditLog, SharedLink
from app.schemas.admin import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    AuditLogResponse, AuditLogListResponse,
    SystemStats, UserActivityStats, PopularHSCodes,
    BulkActionRequest, BulkActionResponse
)
from app.services.auth import get_password_hash

router = APIRouter()


# ============================================================================
# USER MANAGEMENT ENDPOINTS (7 endpoints)
# ============================================================================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by email or name"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all users with pagination and filtering.
    Requires admin or superuser role.
    """
    # Build base query - exclude soft-deleted users
    query = select(User).where(User.deleted_at.is_(None))

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )

    # Apply role filter
    if role:
        query = query.where(User.role == role)

    # Apply active status filter
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Apply organization filter
    if organization_id:
        query = query.where(User.organization_id == organization_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and ordering
    offset = (page - 1) * page_size
    query = query.order_by(desc(User.created_at)).offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Convert to response models
    user_responses = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": user.organization_id,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_email_verified": user.is_email_verified,
            "last_login_at": user.last_login_at,
            "login_count": user.login_count if hasattr(user, 'login_count') else 0,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        user_responses.append(UserResponse(**user_dict))

    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new user.
    Requires admin or superuser role.
    """
    # Check if email already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate organization exists if provided
    if user_data.organization_id:
        org_result = await db.execute(
            select(Organization).where(Organization.id == user_data.organization_id)
        )
        if not org_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        organization_id=user_data.organization_id,
        is_active=True,
        is_superuser=False,
        is_email_verified=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Convert to response
    user_dict = {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.role,
        "organization_id": new_user.organization_id,
        "is_active": new_user.is_active,
        "is_superuser": new_user.is_superuser,
        "is_email_verified": new_user.is_email_verified,
        "last_login_at": new_user.last_login_at,
        "login_count": new_user.login_count if hasattr(new_user, 'login_count') else 0,
        "created_at": new_user.created_at,
        "updated_at": new_user.updated_at
    }

    return UserResponse(**user_dict)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get a specific user by ID.
    Requires admin or superuser role.
    """
    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_dict = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "organization_id": user.organization_id,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_email_verified": user.is_email_verified,
        "last_login_at": user.last_login_at,
        "login_count": user.login_count if hasattr(user, 'login_count') else 0,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

    return UserResponse(**user_dict)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a user's information.
    Requires admin or superuser role.
    """
    # Get user
    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.deleted_at.is_(None)
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if user_data.email is not None:
        # Check if new email is already taken
        existing = await db.execute(
            select(User).where(
                and_(
                    User.email == user_data.email,
                    User.id != user_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_data.email

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.organization_id is not None:
        # Validate organization exists
        org_result = await db.execute(
            select(Organization).where(Organization.id == user_data.organization_id)
        )
        if not org_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        user.organization_id = user_data.organization_id

    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    user_dict = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "organization_id": user.organization_id,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_email_verified": user.is_email_verified,
        "last_login_at": user.last_login_at,
        "login_count": user.login_count if hasattr(user, 'login_count') else 0,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

    return UserResponse(**user_dict)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    hard_delete: bool = Query(False, description="Permanently delete (cannot be undone)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a user (soft delete by default, hard delete requires superuser).
    Only superusers can delete users.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    if hard_delete:
        # Hard delete - permanent removal
        await db.delete(user)
    else:
        # Soft delete - mark as deleted
        user.deleted_at = datetime.utcnow()
        user.is_active = False

    await db.commit()
    return None


@router.post("/users/bulk-action", response_model=BulkActionResponse)
async def bulk_user_action(
    action_data: BulkActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Perform bulk actions on multiple users.
    Actions: activate, deactivate, delete, change_role
    Requires admin or superuser role.
    """
    if not action_data.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No users specified"
        )

    # Get all users
    result = await db.execute(
        select(User).where(
            and_(
                User.id.in_(action_data.user_ids),
                User.deleted_at.is_(None)
            )
        )
    )
    users = result.scalars().all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )

    success_count = 0
    failed_count = 0
    errors = []

    for user in users:
        try:
            # Prevent action on self
            if user.id == current_user.id and action_data.action in ['deactivate', 'delete']:
                errors.append(f"Cannot {action_data.action} your own account")
                failed_count += 1
                continue

            if action_data.action == "activate":
                user.is_active = True
                success_count += 1
            elif action_data.action == "deactivate":
                user.is_active = False
                success_count += 1
            elif action_data.action == "delete":
                # Only superusers can delete
                if not current_user.is_superuser:
                    errors.append(f"User {user.email}: deletion requires superuser")
                    failed_count += 1
                    continue
                user.deleted_at = datetime.utcnow()
                user.is_active = False
                success_count += 1
            elif action_data.action == "change_role":
                if not action_data.new_role:
                    errors.append("new_role is required for change_role action")
                    failed_count += 1
                    continue
                user.role = action_data.new_role
                success_count += 1
            else:
                errors.append(f"Unknown action: {action_data.action}")
                failed_count += 1

        except Exception as e:
            errors.append(f"User {user.email}: {str(e)}")
            failed_count += 1

    await db.commit()

    return BulkActionResponse(
        success_count=success_count,
        failed_count=failed_count,
        errors=errors if errors else None
    )


# ============================================================================
# ORGANIZATION MANAGEMENT ENDPOINTS (3 endpoints)
# ============================================================================

@router.get("/organizations", response_model=List[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all organizations.
    Requires admin or superuser role.
    """
    result = await db.execute(
        select(Organization).where(Organization.deleted_at.is_(None))
        .order_by(Organization.name)
    )
    organizations = result.scalars().all()

    org_responses = []
    for org in organizations:
        # Count active users
        user_count_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.organization_id == org.id,
                    User.is_active == True,
                    User.deleted_at.is_(None)
                )
            )
        )
        user_count = user_count_result.scalar()

        org_dict = {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "plan": org.plan,
            "max_users": org.max_users,
            "max_calculations_per_month": org.max_calculations_per_month,
            "status": org.status,
            "is_active": org.status == "active",
            "created_at": org.created_at,
            "updated_at": org.updated_at,
            "user_count": user_count
        }
        org_responses.append(OrganizationResponse(**org_dict))

    return org_responses


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new organization.
    Requires admin or superuser role.
    """
    # Check if slug already exists
    existing = await db.execute(
        select(Organization).where(Organization.slug == org_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )

    # Create organization
    new_org = Organization(
        id=str(uuid.uuid4()),
        name=org_data.name,
        slug=org_data.slug,
        plan=org_data.plan or "free",
        max_users=org_data.max_users or 5,
        max_calculations_per_month=org_data.max_calculations_per_month or 100,
        is_active=True
    )

    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)

    org_dict = {
        "id": new_org.id,
        "name": new_org.name,
        "slug": new_org.slug,
        "plan": new_org.plan,
        "max_users": new_org.max_users,
        "max_calculations_per_month": new_org.max_calculations_per_month,
        "is_active": new_org.is_active,
        "created_at": new_org.created_at,
        "updated_at": new_org.updated_at,
        "user_count": 0
    }

    return OrganizationResponse(**org_dict)


@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update an organization.
    Requires admin or superuser role.
    """
    # Get organization
    result = await db.execute(
        select(Organization).where(
            and_(
                Organization.id == org_id,
                Organization.deleted_at.is_(None)
            )
        )
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Update fields if provided
    if org_data.name is not None:
        org.name = org_data.name

    if org_data.slug is not None:
        # Check if new slug is taken
        existing = await db.execute(
            select(Organization).where(
                and_(
                    Organization.slug == org_data.slug,
                    Organization.id != org_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug already in use"
            )
        org.slug = org_data.slug

    if org_data.plan is not None:
        org.plan = org_data.plan

    if org_data.max_users is not None:
        org.max_users = org_data.max_users

    if org_data.max_calculations_per_month is not None:
        org.max_calculations_per_month = org_data.max_calculations_per_month

    if org_data.is_active is not None:
        org.is_active = org_data.is_active

    org.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(org)

    # Get user count
    user_count_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.organization_id == org.id,
                User.is_active == True,
                User.deleted_at.is_(None)
            )
        )
    )
    user_count = user_count_result.scalar()

    org_dict = {
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "plan": org.plan,
        "max_users": org.max_users,
        "max_calculations_per_month": org.max_calculations_per_month,
        "status": org.status,
            "is_active": org.status == "active",
        "created_at": org.created_at,
        "updated_at": org.updated_at,
        "user_count": user_count
    }

    return OrganizationResponse(**org_dict)


# ============================================================================
# AUDIT & STATISTICS ENDPOINTS (4 endpoints)
# ============================================================================

@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List audit logs with filtering.
    Requires admin or superuser role.
    """
    query = select(AuditLog)

    # Apply filters
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    if action:
        query = query.where(AuditLog.action == action)

    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    if date_from:
        query = query.where(AuditLog.created_at >= date_from)

    if date_to:
        query = query.where(AuditLog.created_at <= date_to)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size)

    # Execute
    result = await db.execute(query)
    logs = result.scalars().all()

    # Convert to response
    log_responses = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": None,  # TODO: Join with users table to get email
            "organization_id": log.organization_id if hasattr(log, 'organization_id') else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "changes": log.changes if hasattr(log, 'changes') else None,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "endpoint": log.endpoint,
            "method": log.method,
            "status_code": log.status_code,
            "duration_ms": log.duration_ms,
            "created_at": log.created_at
        }
        log_responses.append(AuditLogResponse(**log_dict))

    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get overall system statistics.
    Requires admin or superuser role.
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)

    # Total users
    total_users_result = await db.execute(
        select(func.count(User.id)).where(User.deleted_at.is_(None))
    )
    total_users = total_users_result.scalar()

    # Active users
    active_users_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.is_active == True,
                User.deleted_at.is_(None)
            )
        )
    )
    active_users = active_users_result.scalar()

    # Total organizations
    total_orgs_result = await db.execute(
        select(func.count(Organization.id)).where(Organization.deleted_at.is_(None))
    )
    total_organizations = total_orgs_result.scalar()

    # Total calculations
    total_calcs_result = await db.execute(
        select(func.count(Calculation.id))
    )
    total_calculations = total_calcs_result.scalar()

    # Calculations today
    calcs_today_result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.created_at >= today_start
        )
    )
    calculations_today = calcs_today_result.scalar()

    # Calculations this month
    calcs_month_result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.created_at >= month_start
        )
    )
    calculations_this_month = calcs_month_result.scalar()

    # Shared links
    shared_links_result = await db.execute(
        select(func.count(SharedLink.id))
    )
    total_shared_links = shared_links_result.scalar()

    # Active API keys (count from api_keys table if it exists)
    try:
        from app.models.calculation import APIKey
        api_keys_result = await db.execute(
            select(func.count(APIKey.id)).where(APIKey.is_active == True)
        )
        active_api_keys = api_keys_result.scalar()
    except:
        active_api_keys = 0

    # Users created in last 7 days
    seven_days_ago = now - timedelta(days=7)
    users_last_7_days_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.created_at >= seven_days_ago,
                User.deleted_at.is_(None)
            )
        )
    )
    users_last_7_days = users_last_7_days_result.scalar()

    # Calculations in last 7 days
    calcs_last_7_days_result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.created_at >= seven_days_ago
        )
    )
    calculations_last_7_days = calcs_last_7_days_result.scalar()

    # Average calculation time (if duration_ms exists in Calculation)
    try:
        avg_calc_time_result = await db.execute(
            select(func.avg(Calculation.duration_ms)).where(
                Calculation.duration_ms.isnot(None)
            )
        )
        avg_calculation_time_ms = avg_calc_time_result.scalar() or 0
    except:
        avg_calculation_time_ms = 0

    # Average API response time from audit logs
    try:
        avg_api_time_result = await db.execute(
            select(func.avg(AuditLog.duration_ms)).where(
                AuditLog.duration_ms.isnot(None)
            )
        )
        avg_api_response_time_ms = avg_api_time_result.scalar() or 0
    except:
        avg_api_response_time_ms = 0

    # Storage calculation (rough estimate based on database size)
    storage_used_mb = 0.0  # TODO: Implement actual storage calculation

    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_organizations=total_organizations,
        total_calculations=total_calculations,
        calculations_today=calculations_today,
        calculations_this_month=calculations_this_month,
        total_shared_links=total_shared_links,
        active_api_keys=active_api_keys,
        storage_used_mb=storage_used_mb,
        users_last_7_days=users_last_7_days,
        calculations_last_7_days=calculations_last_7_days,
        avg_calculation_time_ms=avg_calculation_time_ms,
        avg_api_response_time_ms=avg_api_response_time_ms
    )


@router.get("/stats/activity", response_model=List[UserActivityStats])
async def get_activity_stats(
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get daily user activity statistics.
    Requires admin or superuser role.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get daily calculation counts
    result = await db.execute(
        select(
            func.date(Calculation.created_at).label('date'),
            func.count(Calculation.id).label('calculation_count'),
            func.count(func.distinct(Calculation.user_id)).label('active_user_count')
        )
        .where(Calculation.created_at >= start_date)
        .group_by(func.date(Calculation.created_at))
        .order_by(func.date(Calculation.created_at))
    )

    activity_data = []
    for row in result:
        activity_data.append(UserActivityStats(
            date=str(row.date) if row.date else "",
            new_users=0,  # TODO: Add query to count new users per day
            active_users=row.active_user_count,
            calculations=row.calculation_count
        ))

    return activity_data


@router.get("/stats/popular-hs-codes", response_model=List[PopularHSCodes])
async def get_popular_hs_codes(
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get most frequently used HS codes.
    Requires admin or superuser role.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            Calculation.hs_code,
            func.count(Calculation.id).label('usage_count'),
            func.count(func.distinct(Calculation.user_id)).label('unique_users')
        )
        .where(
            and_(
                Calculation.created_at >= start_date,
                Calculation.hs_code.isnot(None)
            )
        )
        .group_by(Calculation.hs_code)
        .order_by(desc('usage_count'))
        .limit(limit)
    )

    popular_codes = []
    for row in result:
        popular_codes.append(PopularHSCodes(
            hs_code=row.hs_code,
            usage_count=row.usage_count,
            unique_users=row.unique_users
        ))

    return popular_codes
