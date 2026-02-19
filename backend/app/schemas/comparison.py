"""
Comparison schemas for comparing multiple calculations.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime


class ComparisonRequest(BaseModel):
    """Request schema for calculation comparison"""
    calculation_ids: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="2-5 calculation IDs to compare"
    )

    @field_validator('calculation_ids')
    @classmethod
    def validate_calculation_ids(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 calculations required for comparison')
        if len(v) > 5:
            raise ValueError('Maximum 5 calculations allowed for comparison')
        if len(set(v)) != len(v):
            raise ValueError('Duplicate calculation IDs not allowed')
        return v


class ComparisonMetrics(BaseModel):
    """Summary metrics for comparison"""
    min_total_cost: Decimal
    max_total_cost: Decimal
    avg_total_cost: Decimal
    cost_spread: Decimal  # max - min
    cost_spread_percent: float

    min_duty_rate: Optional[float] = None
    max_duty_rate: Optional[float] = None
    avg_duty_rate: Optional[float] = None

    best_option_id: str
    worst_option_id: str

    has_fta_eligible: bool
    total_fta_savings: Optional[Decimal] = None

    comparison_type: str  # 'same_hs_different_countries', 'different_hs_same_country', 'mixed'

    class Config:
        from_attributes = True


class ComparisonCalculationItem(BaseModel):
    """Individual calculation in comparison with ranking information"""
    id: str
    name: Optional[str] = None
    hs_code: str
    product_description: Optional[str] = None
    origin_country: str
    destination_country: str
    cif_value: Decimal
    currency: str
    total_cost: Decimal
    customs_duty: Optional[Decimal] = None
    vat_amount: Optional[Decimal] = None
    fta_eligible: bool
    fta_savings: Optional[Decimal] = None
    result: Dict[str, Any]
    created_at: datetime

    # Comparison-specific fields
    rank: int  # 1 = best (lowest cost), 5 = worst
    cost_vs_average: Decimal
    cost_vs_average_percent: float
    is_best: bool
    is_worst: bool

    class Config:
        from_attributes = True


class ComparisonResponse(BaseModel):
    """Full comparison response with calculations and metrics"""
    calculations: List[ComparisonCalculationItem]
    metrics: ComparisonMetrics
    comparison_date: datetime = Field(default_factory=datetime.utcnow)
    total_compared: int

    class Config:
        from_attributes = True
