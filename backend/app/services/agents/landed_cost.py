from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
import structlog

from app.schemas.schemas import LandedCostRequest, LandedCostResponse, CostBreakdown

logger = structlog.get_logger()

class LandedCostCalculator:
    HMF_RATE = Decimal("0.00125")
    MPF_RATE = Decimal("0.003464")
    MPF_MIN = Decimal("31.67")
    MPF_MAX = Decimal("614.35")
    DEFAULT_DRAYAGE = Decimal("450.00")
    
    async def calculate(self, request: LandedCostRequest, hts_general_rate: Decimal, section_301_rate: Optional[Decimal] = None, fta_rate: Optional[Decimal] = None) -> LandedCostResponse:
        cv = request.customs_value
        
        applicable_rate = fta_rate if fta_rate is not None else hts_general_rate
        duty = (cv * applicable_rate / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        section_301 = Decimal("0")
        if section_301_rate and request.origin_country == "CN":
            section_301 = (cv * section_301_rate).quantize(Decimal("0.01"))
        
        hmf = (cv * self.HMF_RATE).quantize(Decimal("0.01"))
        mpf_calc = cv * self.MPF_RATE
        mpf = max(min(mpf_calc, self.MPF_MAX), self.MPF_MIN).quantize(Decimal("0.01"))
        
        freight = request.freight_cost
        cif_value = cv + freight
        insurance = (cif_value * Decimal("0.002")).quantize(Decimal("0.01"))
        drayage = self.DEFAULT_DRAYAGE
        other_fees = Decimal("150.00")
        
        total = cv + duty + section_301 + hmf + mpf + freight + insurance + drayage + other_fees
        
        return LandedCostResponse(
            total_landed_cost=total,
            breakdown=CostBreakdown(
                customs_value=cv, duty=duty, section_301=section_301,
                hmf=hmf, mpf=mpf, freight=freight, insurance=insurance,
                drayage=drayage, other_fees=other_fees
            ),
            effective_duty_rate=Decimal("0"),
            section_301_exposure=section_301 if section_301 > 0 else None,
            fta_eligible=fta_rate is not None,
            fta_savings_opportunity=None,
            recommendation="Standard routing"
        )
