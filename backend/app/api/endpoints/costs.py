from fastapi import APIRouter
from decimal import Decimal

router = APIRouter()

@router.post("/calculate")
async def calculate_costs(request: dict):
    # Extract values from request
    customs_value = Decimal(str(request.get("customs_value", 0)))
    hts_rate = Decimal(str(request.get("hts_rate", 0)))
    section_301_rate = Decimal(str(request.get("section_301_rate", 0)))
    freight_cost = Decimal(str(request.get("freight_cost", 0)))
    
    # Calculate all fees
    duty = customs_value * hts_rate / 100
    section_301 = customs_value * section_301_rate
    hmf = customs_value * Decimal("0.00125")  # Harbor Maintenance Fee (0.125%)
    mpf = min(max(customs_value * Decimal("0.003464"), Decimal("31.67")), Decimal("614.35"))  # Merchandise Processing Fee
    insurance = (customs_value + freight_cost) * Decimal("0.002")
    drayage = Decimal("450.00")
    other_fees = Decimal("150.00")
    
    total = customs_value + duty + section_301 + hmf + mpf + freight_cost + insurance + drayage + other_fees
    
    return {
        "total_landed_cost": float(total),
        "breakdown": {
            "customs_value": float(customs_value),
            "duty": float(duty),
            "section_301": float(section_301),
            "hmf": float(hmf),
            "mpf": float(mpf),
            "freight": float(freight_cost),
            "insurance": float(insurance),
            "drayage": float(drayage),
            "other_fees": float(other_fees)
        },
        "recommendation": "Standard routing" if section_301 == 0 else f"Consider alternative sourcing - Section 301 adds ${float(section_301):,.2f}"
    }
