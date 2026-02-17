from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class HTSCodeBase(BaseModel):
    hts_code: str = Field(..., pattern=r"^\d{4}\.\d{2}\.\d{4}$")
    description: str
    general_rate: Decimal = Field(..., ge=0, le=100)
    section_301_status: Optional[str] = None

class HTSCodeResponse(HTSCodeBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    chapter: str
    heading: str
    subheading: str
    created_at: datetime

class ClassificationRequest(BaseModel):
    product_description: str = Field(..., min_length=10, max_length=5000)
    image_url: Optional[str] = None
    material_composition: Optional[str] = None
    intended_use: Optional[str] = None

class HTSCodeSuggestion(BaseModel):
    hts_code: str
    description: str
    general_rate: Decimal
    section_301_rate: Optional[Decimal] = None
    confidence_score: float = Field(..., ge=0, le=1)
    rationale: str
    citation: Optional[str] = None
    alternatives: List[dict] = []

class ClassificationResponse(BaseModel):
    id: Optional[UUID] = None
    suggestions: List[HTSCodeSuggestion]
    processing_time_ms: int
    created_at: Optional[datetime] = None

class RouteRequest(BaseModel):
    origin_country: str = Field(..., min_length=2, max_length=2)
    origin_port: Optional[str] = Field(None, min_length=5, max_length=5)
    destination_country: str = Field(..., min_length=2, max_length=2)
    destination_port: str = Field(..., min_length=5, max_length=5)
    container_type: str = "FCL"
    weight_kg: Optional[Decimal] = None
    volume_cbm: Optional[Decimal] = None

class RouteOption(BaseModel):
    carrier: str
    service_name: str
    origin: str
    destination: str
    transit_days: int
    freight_cost: Decimal
    reliability_score: float = Field(..., ge=0, le=1)
    co2_emissions_kg: Optional[Decimal] = None
    departure_dates: List[datetime] = []

class LandedCostRequest(BaseModel):
    hts_code: str
    customs_value: Decimal = Field(..., gt=0)
    origin_country: str = Field(..., min_length=2, max_length=2)
    destination_port: str = Field(..., min_length=5, max_length=5)
    freight_cost: Decimal
    insurance_rate: Decimal = Field(default=Decimal("0.002"), ge=0, le=0.1)
    route_id: Optional[str] = None

class CostBreakdown(BaseModel):
    customs_value: Decimal
    duty: Decimal
    section_301: Decimal
    hmf: Decimal
    mpf: Decimal
    freight: Decimal
    insurance: Decimal
    drayage: Decimal
    other_fees: Decimal

class LandedCostResponse(BaseModel):
    total_landed_cost: Decimal
    breakdown: CostBreakdown
    effective_duty_rate: Decimal
    section_301_exposure: Optional[Decimal]
    fta_eligible: bool
    fta_savings_opportunity: Optional[Decimal]
    recommendation: str
    calculation_id: Optional[UUID] = None

class ShipmentCreate(BaseModel):
    origin_country: str
    destination_port: str
    hts_code: str
    product_description: str
    customs_value: Decimal
    selected_route: RouteOption
    priority: str = "balanced"

class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    total_landed_cost: Decimal
    cost_breakdown: Dict[str, Decimal]
    created_at: datetime
