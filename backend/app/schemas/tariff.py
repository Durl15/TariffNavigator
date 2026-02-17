from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class TariffBase(BaseModel):
    hs_code: str
    country_origin: str
    country_destination: str
    rate_type: str
    duty_rate: Decimal
    min_duty: Optional[Decimal] = None
    max_duty: Optional[Decimal] = None
    unit: Optional[str] = None
    quota_limit: Optional[Decimal] = None
    quota_year: Optional[str] = None
    notes: Optional[str] = None


class TariffResponse(TariffBase):
    id: str
    
    class Config:
        from_attributes = True


class TariffSearchResult(BaseModel):
    results: List[TariffResponse]
    total: int
    query: dict


class TariffRateRequest(BaseModel):
    hs_code: str
    origin: str  # 'CN', 'US', 'EU'
    destination: str  # 'US', 'EU', 'CN'
    value: Optional[Decimal] = None  # Customs value for calculation
    quantity: Optional[Decimal] = None  # Quantity for specific duties


class TariffRateResponse(BaseModel):
    hs_code: str
    origin: str
    destination: str
    applicable_rates: List[TariffResponse]
    best_rate: Optional[TariffResponse] = None
    estimated_duty: Optional[Decimal] = None
    currency: str = "USD"
