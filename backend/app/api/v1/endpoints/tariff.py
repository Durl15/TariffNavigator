import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db.session import get_db
from app.models.hs_code import HSCode

router = APIRouter()

@router.get("/search")
async def search_tariff(
    code: str = Query(..., description="HS code to search"),
    country: str = Query(..., description="Country code (CN, EU, US)"),
    db: AsyncSession = Depends(get_db)
):
    """Search for HS codes by prefix"""
    clean_code = code.replace(".", "").replace(" ", "")
    
    result = await db.execute(
        select(HSCode).where(
            HSCode.country == country.upper(),
            HSCode.code.like(f"{clean_code}%")
        ).limit(10)
    )
    codes = result.scalars().all()
    
    if not codes:
        raise HTTPException(status_code=404, detail="No HS codes found")
    
    return {
        "query": code,
        "country": country,
        "results": [c.to_dict() for c in codes]
    }

@router.post("/calculate")
async def calculate_tariff(
    hs_code: str,
    country: str,
    value: float,
    from_currency: str = "USD",
    to_currency: str = "USD",
    db: AsyncSession = Depends(get_db)
):
    """Calculate total import cost with currency conversion"""
    clean_code = hs_code.replace(".", "").replace(" ", "")
    result = await db.execute(
        select(HSCode).where(
            HSCode.country == country.upper(),
            HSCode.code == clean_code
        )
    )
    code_data = result.scalar_one_or_none()
    
    if not code_data:
        raise HTTPException(status_code=404, detail=f"HS code {hs_code} not found for {country}")
    
    cif_value = value
    
    if country.upper() == "CN":
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
            "currency": currency
        }
    elif country.upper() == "EU":
        duty = cif_value * ((code_data.mfn_rate or 0) / 100)
        vat = (cif_value + duty) * ((code_data.vat_rate or 0) / 100)
        total = cif_value + duty + vat
        
        breakdown = {
            "cif_value": round(cif_value, 2),
            "customs_duty": round(duty, 2),
            "vat": round(vat, 2),
            "total_cost": round(total, 2),
            "currency": currency
        }
    else:
        duty = cif_value * ((code_data.mfn_rate or 0) / 100)
        total = cif_value + duty
        
        breakdown = {
            "cif_value": round(cif_value, 2),
            "customs_duty": round(duty, 2),
            "total_cost": round(total, 2),
            "currency": from_currency
        }

    # Currency conversion
    rate = 1
    if from_currency != to_currency:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
                    timeout=5.0
                )
                data = response.json()
                rate = data["rates"].get(to_currency, 1)
        except Exception:
            mock_rates = {"USD": {"CNY": 7.2, "EUR": 0.92, "JPY": 150, "GBP": 0.79, "KRW": 1330}}
            rate = mock_rates.get(from_currency, {}).get(to_currency, 1)

    # Create converted calculation if needed
    converted_calculation = None
    if rate != 1:
        converted_calculation = {
            "cif_value": round(breakdown["cif_value"] * rate, 2),
            "customs_duty": round(breakdown["customs_duty"] * rate, 2),
            "vat": round(breakdown.get("vat", 0) * rate, 2),
            "consumption_tax": round(breakdown.get("consumption_tax", 0) * rate, 2),
            "total_cost": round(breakdown["total_cost"] * rate, 2),
            "currency": to_currency
        }

    result = {
        "hs_code": hs_code,
        "country": country,
        "description": code_data.description,
        "rates": {
            "mfn": code_data.mfn_rate or 0,
            "vat": code_data.vat_rate or 0,
            "consumption": code_data.consumption_tax or 0
        },
        "calculation": breakdown
    }

    if converted_calculation:
        result["original_currency"] = from_currency
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