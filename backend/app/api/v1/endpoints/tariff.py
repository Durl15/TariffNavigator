import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime
from app.db.session import get_db
from app.models.hs_code import HSCode
from app.models.calculation import Calculation
from app.models.user import User
from app.services.tariff_stacking import calculate_us_import, ORIGIN_COUNTRIES

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Free tier monthly lookup limit
FREE_TIER_LIMIT = 10

# Tier limits — None means unlimited
TIER_LIMITS: dict[str, Optional[int]] = {
    "free": FREE_TIER_LIMIT,
    "user": FREE_TIER_LIMIT,
    "viewer": 5,
    "pro": None,
    "enterprise": None,
    "consultant": None,
    "admin": None,
    "superadmin": None,
}


async def _get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Return authenticated user if token present, else None."""
    if not credentials:
        return None
    try:
        from app.services.auth import get_current_user_from_token
        return await get_current_user_from_token(credentials.credentials, db)
    except Exception:
        return None


async def _check_free_tier(user: Optional[User], db: AsyncSession) -> int:
    """
    Return number of lookups used this month for authenticated free-tier users.
    Raises HTTP 429 if limit exceeded.
    Returns remaining lookups (None = unlimited).
    """
    if user is None:
        return FREE_TIER_LIMIT  # unauthenticated: rely on IP rate limiting

    limit = TIER_LIMITS.get(user.role)
    if limit is None:
        return 9999  # paid tier — unlimited

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.user_id == user.id,
            Calculation.created_at >= month_start,
        )
    )
    used = result.scalar() or 0

    if used >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": f"Monthly lookup limit of {limit} reached for your free plan.",
                "used": used,
                "limit": limit,
                "upgrade_url": "/pricing",
            },
        )
    return limit - used

# Request validation models
class CalculateRequest(BaseModel):
    """Request model for tariff calculation with input validation"""
    hs_code: str = Field(..., min_length=4, max_length=12, description="HS code (4-10 digits, dots/spaces allowed)")
    country: str = Field(..., min_length=2, max_length=2, description="Country code (CN, EU, US)")
    value: float = Field(..., gt=0, le=999999999, description="CIF value in USD (must be positive)")
    from_currency: str = Field(default="USD", min_length=3, max_length=3, description="Source currency code")
    to_currency: str = Field(default="USD", min_length=3, max_length=3, description="Target currency code")

    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v: str) -> str:
        """Validate HS code format - must contain only digits, dots, spaces"""
        clean = v.replace(".", "").replace(" ", "")
        if not re.match(r'^\d{4,10}$', clean):
            raise ValueError('HS code must be 4-10 digits (dots and spaces are stripped)')
        return v

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate country code - must be CN, EU, or US"""
        allowed = ['CN', 'EU', 'US']
        if v.upper() not in allowed:
            raise ValueError(f'Country must be one of: {", ".join(allowed)}')
        return v.upper()

    @field_validator('from_currency', 'to_currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code"""
        allowed = ['USD', 'CNY', 'EUR', 'JPY', 'GBP', 'KRW']
        if v.upper() not in allowed:
            raise ValueError(f'Currency must be one of: {", ".join(allowed)}')
        return v.upper()

@router.get("/search")
async def search_tariff(
    code: str = Query(..., description="HS code to search"),
    country: str = Query(..., description="Country code (CN, EU, US)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_rate: Optional[float] = Query(None, ge=0, le=100, description="Minimum duty rate"),
    max_rate: Optional[float] = Query(None, ge=0, le=100, description="Maximum duty rate"),
    sort_by: Optional[str] = Query("relevance", description="Sort order: relevance, rate_asc, rate_desc, code"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """Search for HS codes by prefix with enhanced filtering and sorting"""
    clean_code = code.replace(".", "").replace(" ", "")

    # Build query with filters
    query = select(HSCode).where(
        HSCode.country == country.upper(),
        HSCode.code.like(f"{clean_code}%")
    )

    # Apply category filter (if category column exists)
    if category:
        query = query.where(HSCode.category == category)

    # Apply duty rate range filters
    if min_rate is not None:
        query = query.where(HSCode.mfn_rate >= min_rate)

    if max_rate is not None:
        query = query.where(HSCode.mfn_rate <= max_rate)

    # Apply sorting
    if sort_by == "rate_asc":
        query = query.order_by(HSCode.mfn_rate.asc())
    elif sort_by == "rate_desc":
        query = query.order_by(HSCode.mfn_rate.desc())
    elif sort_by == "code":
        query = query.order_by(HSCode.code.asc())
    else:  # relevance (default) - exact matches first, then by code
        query = query.order_by(HSCode.code.asc())

    # Apply limit
    query = query.limit(limit)

    result = await db.execute(query)
    codes = result.scalars().all()

    if not codes:
        raise HTTPException(status_code=404, detail="No HS codes found")

    return {
        "query": code,
        "country": country,
        "category": category,
        "min_rate": min_rate,
        "max_rate": max_rate,
        "sort_by": sort_by,
        "results": [c.to_dict() for c in codes]
    }

@router.post("/calculate")
async def calculate_tariff(
    hs_code: str = Query(..., description="HS code"),
    country: str = Query(..., description="Country code"),
    value: float = Query(..., gt=0, description="CIF value"),
    from_currency: str = Query(default="USD", description="Source currency"),
    to_currency: str = Query(default="USD", description="Target currency"),
    db: AsyncSession = Depends(get_db)
):
    """Calculate total import cost with currency conversion and input validation"""
    # Validate inputs using Pydantic model
    try:
        validated = CalculateRequest(
            hs_code=hs_code,
            country=country,
            value=value,
            from_currency=from_currency,
            to_currency=to_currency
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    clean_code = validated.hs_code.replace(".", "").replace(" ", "")
    result = await db.execute(
        select(HSCode).where(
            HSCode.country == validated.country,
            HSCode.code == clean_code
        )
    )
    code_data = result.scalar_one_or_none()

    if not code_data:
        raise HTTPException(
            status_code=404,
            detail=f"HS code {validated.hs_code} not found for {validated.country}"
        )

    cif_value = validated.value
    
    if validated.country == "CN":
        duty = cif_value * ((code_data.mfn_rate or 0) / 100)
        vat = (cif_value + duty) * ((code_data.vat_rate or 0) / 100)
        consumption_tax_rate = code_data.consumption_tax or 0
        consumption = (cif_value + duty) / (1 - consumption_tax_rate / 100) * (consumption_tax_rate / 100) if consumption_tax_rate > 0 else 0
        total = cif_value + duty + vat + consumption
        
        breakdown = {
            "cif_value": round(cif_value, 2),
            "customs_duty": round(duty, 2),
            "vat": round(vat, 2),
            "consumption_tax": round(consumption, 2),
            "total_cost": round(total, 2),
            "currency": validated.from_currency
        }
    elif validated.country == "EU":
        duty = cif_value * ((code_data.mfn_rate or 0) / 100)
        vat = (cif_value + duty) * ((code_data.vat_rate or 0) / 100)
        total = cif_value + duty + vat
        
        breakdown = {
            "cif_value": round(cif_value, 2),
            "customs_duty": round(duty, 2),
            "vat": round(vat, 2),
            "total_cost": round(total, 2),
            "currency": validated.from_currency
        }
    else:
        duty = cif_value * ((code_data.mfn_rate or 0) / 100)
        total = cif_value + duty
        
        breakdown = {
            "cif_value": round(cif_value, 2),
            "customs_duty": round(duty, 2),
            "total_cost": round(total, 2),
            "currency": validated.from_currency
        }

    # Currency conversion
    rate = 1
    if validated.from_currency != validated.to_currency:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.exchangerate-api.com/v4/latest/{validated.from_currency}",
                    timeout=5.0
                )
                data = response.json()
                rate = data["rates"].get(validated.to_currency, 1)
        except Exception:
            mock_rates = {"USD": {"CNY": 7.2, "EUR": 0.92, "JPY": 150, "GBP": 0.79, "KRW": 1330}}
            rate = mock_rates.get(validated.from_currency, {}).get(validated.to_currency, 1)

    # Create converted calculation if needed
    converted_calculation = None
    if rate != 1:
        converted_calculation = {
            "cif_value": round(breakdown["cif_value"] * rate, 2),
            "customs_duty": round(breakdown["customs_duty"] * rate, 2),
            "vat": round(breakdown.get("vat", 0) * rate, 2),
            "consumption_tax": round(breakdown.get("consumption_tax", 0) * rate, 2),
            "total_cost": round(breakdown["total_cost"] * rate, 2),
            "currency": validated.to_currency
        }

    result = {
        "hs_code": validated.hs_code,
        "country": validated.country,
        "description": code_data.description,
        "rates": {
            "mfn": code_data.mfn_rate or 0,
            "vat": code_data.vat_rate or 0,
            "consumption": code_data.consumption_tax or 0
        },
        "calculation": breakdown
    }

    if converted_calculation:
        result["original_currency"] = validated.from_currency
        result["exchange_rate"] = rate
        result["converted_calculation"] = converted_calculation

    return result

@router.get("/autocomplete")
async def autocomplete_hs(
    query: str = Query(..., min_length=2),
    country: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Search HS codes by description or code"""
    result = await db.execute(
        select(HSCode).where(
            HSCode.country == country.upper(),
            (HSCode.code.like(f"{query}%")) | 
            (HSCode.description.ilike(f"%{query}%"))
        ).limit(10)
    )
    codes = result.scalars().all()
    return [{"code": c.code, "description": c.description, "mfn_rate": c.mfn_rate} for c in codes]

@router.get("/fta-check")
async def check_fta_eligibility(
    hs_code: str = Query(...),
    origin_country: str = Query(..., description="Origin country code"),
    dest_country: str = Query(..., description="Destination country code"),
    db: AsyncSession = Depends(get_db)
):
    """Check if FTA preferential rates apply"""
    
    clean_code = hs_code.replace(".", "").replace(" ", "")
    result = await db.execute(
        select(HSCode).where(
            HSCode.code == clean_code
        )
    )
    code_data = result.scalar_one_or_none()
    
    if not code_data:
        raise HTTPException(status_code=404, detail="HS code not found")
    
    fta_countries_list = code_data.fta_countries.split(",") if code_data.fta_countries else []
    is_eligible = origin_country.upper() in fta_countries_list
    
    standard_rate = code_data.mfn_rate
    preferential_rate = code_data.fta_rate if is_eligible else standard_rate
    savings_percent = standard_rate - preferential_rate
    
    return {
        "hs_code": hs_code,
        "origin_country": origin_country,
        "destination_country": dest_country,
        "eligible": is_eligible,
        "fta_name": code_data.fta_name if is_eligible else None,
        "standard_rate": standard_rate,
        "preferential_rate": preferential_rate,
        "savings_percent": savings_percent,
        "requirements": [
            "Certificate of Origin",
            "Direct shipment rule",
            "Product specific rules of origin compliance"
        ] if is_eligible else []
    }

@router.get("/exchange-rate")
async def get_exchange_rate(
    from_currency: str = Query(default="USD", description="Source currency (e.g., USD)"),
    to_currency: str = Query(default="CNY", description="Target currency (e.g., CNY, EUR)")
):
    """Get real-time exchange rate from free API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
                timeout=5.0
            )
            data = response.json()
            rate = data["rates"].get(to_currency, 0)
            last_updated = data.get("date", "N/A")
    except Exception:
        mock_rates = {
            "USD": {"CNY": 7.2, "EUR": 0.92, "JPY": 150, "GBP": 0.79, "KRW": 1330},
            "CNY": {"USD": 0.14, "EUR": 0.13, "JPY": 21, "GBP": 0.11, "KRW": 185},
            "EUR": {"USD": 1.09, "CNY": 7.8, "JPY": 163, "GBP": 0.86, "KRW": 1445},
        }
        rate = mock_rates.get(from_currency, {}).get(to_currency, 1.0)
        last_updated = "mock data"
    
    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": rate,
        "inverse_rate": 1 / rate if rate > 0 else 0,
        "last_updated": last_updated
    }

# Removed duplicate calculate endpoint - currency conversion now integrated into main /calculate endpoint above


# ─────────────────────────────────────────────────────────────────────────────
# US IMPORT CALCULATOR — Stacked tariff engine
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/origin-countries")
async def get_origin_countries():
    """Return list of supported origin countries for the US import calculator."""
    return ORIGIN_COUNTRIES


@router.post("/us-import")
async def calculate_us_import_tariff(
    hts_code: str = Query(..., description="US HTS code (4-10 digits)"),
    origin_country: str = Query(..., description="Country of origin code (CN, MX, CA, VN, KR, etc.)"),
    cif_value: float = Query(..., gt=0, description="CIF value in USD"),
    usmca_qualifying: bool = Query(default=True, description="Does the product qualify for USMCA? (MX/CA only)"),
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Calculate total US import cost with full tariff stacking.

    Applies all applicable programs:
    - Base MFN rate (US Harmonized Tariff Schedule)
    - USMCA / KORUS / FTA preferential rates
    - Section 232 (steel, aluminum, autos)
    - Section 301 (China unfair trade practices)
    - IEEPA reciprocal tariffs (China, MX/CA non-qualifying)
    """
    # Clean HTS code
    clean_code = hts_code.replace(".", "").replace(" ", "")
    if not re.match(r'^\d{4,10}$', clean_code):
        raise HTTPException(status_code=422, detail="HTS code must be 4-10 digits")

    origin = origin_country.upper()

    # Optional auth + free tier check
    user = await _get_optional_user(credentials, db)
    await _check_free_tier(user, db)

    # Look up HTS code in DB for description and DB MFN rate
    db_code = None
    description = f"HTS {hts_code}"
    db_mfn_rate = None

    # Try CN table first (largest dataset), then EU
    for search_country in ("CN", "EU"):
        result = await db.execute(
            select(HSCode).where(
                HSCode.country == search_country,
                HSCode.code == clean_code,
            )
        )
        db_code = result.scalar_one_or_none()
        if db_code:
            description = db_code.description
            db_mfn_rate = float(db_code.mfn_rate) if db_code.mfn_rate else None
            break

    # Run stacking engine
    stacked = calculate_us_import(
        hts_code=clean_code,
        origin_country=origin,
        cif_value=cif_value,
        db_mfn_rate=db_mfn_rate,
        usmca_qualifying=usmca_qualifying,
    )

    return {
        "hs_code": hts_code,
        "description": description,
        "origin_country": origin,
        "cif_value": cif_value,
        "mode": "us_import",
        **stacked,
    }


@router.get("/us-import/usage")
async def get_lookup_usage(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Return current month lookup usage for authenticated users."""
    user = await _get_optional_user(credentials, db)
    if not user:
        return {"authenticated": False, "used": 0, "limit": FREE_TIER_LIMIT, "unlimited": False}

    limit = TIER_LIMITS.get(user.role)
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(Calculation.id)).where(
            Calculation.user_id == user.id,
            Calculation.created_at >= month_start,
        )
    )
    used = result.scalar() or 0

    return {
        "authenticated": True,
        "role": user.role,
        "used": used,
        "limit": limit,
        "unlimited": limit is None,
        "remaining": (limit - used) if limit is not None else None,
        "upgrade_url": "/pricing" if limit is not None and used >= int(limit * 0.8) else None,
    }