"""
Cash Flow Forecaster - Predict duty obligations vs revenue timing to surface cash gaps.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import openai
from openai import AsyncOpenAI

from app.core.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

TARIFF_RATES = {
    "CN": {"default": 0.25, "section_301": 0.25, "ieepa": 0.145},
    "MX": {"default": 0.0, "ieepa": 0.25},
    "CA": {"default": 0.0, "ieepa": 0.25},
    "VN": {"default": 0.10},
    "IN": {"default": 0.08},
    "EU": {"default": 0.035},
}


class CashFlowForecastRequest(BaseModel):
    shipment_value: float
    hts_code: Optional[str] = None
    country_of_origin: str = "CN"
    ship_date: Optional[str] = None  # ISO date string
    payment_terms_days: int = 30  # days until customer pays / goods sell
    product_description: Optional[str] = None


class FinancingOption(BaseModel):
    name: str
    description: str
    typical_cost_percent: float


class CashFlowForecastResponse(BaseModel):
    shipment_value: float
    duty_rate_percent: float
    duty_due_amount: float
    due_date: str
    estimated_revenue_date: str
    cash_gap_days: int
    cash_gap_amount: float
    cash_gap_risk: str  # high | medium | low
    ai_recommendation: str
    financing_options: List[FinancingOption]
    tariff_programs_applied: List[str]


def estimate_duty_rate(country: str, hts_code: Optional[str]) -> tuple[float, List[str]]:
    """Estimate stacked duty rate based on country and HTS code."""
    rates = TARIFF_RATES.get(country.upper(), {"default": 0.035})
    programs = []
    total = rates.get("default", 0.035)

    if country.upper() == "CN":
        programs.append("Section 301 (25%)")
        if hts_code and hts_code[:4] in ["8471", "8517", "8542", "8473"]:
            programs.append("IEEPA Electronics (7.5%)")
            total = 0.145 + 0.075
        else:
            total = 0.25 + 0.145
            programs.append("IEEPA Reciprocal (14.5%)")

    elif country.upper() in ["MX", "CA"]:
        if hts_code and hts_code[:4] not in ["8703"]:
            programs.append("USMCA 0% (if qualified)")
            total = 0.0
        else:
            programs.append("IEEPA (25%)")
            total = 0.25

    return total, programs


@router.post("", response_model=CashFlowForecastResponse)
async def forecast_cash_flow(request: CashFlowForecastRequest):
    """
    Forecast duty cash flow obligations vs revenue timing.
    Identifies cash gaps so SMBs can plan financing before shipments arrive.
    """
    try:
        duty_rate, programs = estimate_duty_rate(
            request.country_of_origin, request.hts_code
        )
        duty_amount = request.shipment_value * duty_rate

        # Duty is due at port entry (same day as ship_date for simplicity)
        if request.ship_date:
            try:
                ship_dt = datetime.fromisoformat(request.ship_date)
            except ValueError:
                ship_dt = datetime.now()
        else:
            ship_dt = datetime.now()

        due_date = ship_dt
        revenue_date = ship_dt + timedelta(days=request.payment_terms_days)
        cash_gap_days = request.payment_terms_days
        cash_gap_amount = duty_amount  # duty owed before revenue arrives

        if cash_gap_days > 60 or duty_amount > 25000:
            risk = "high"
        elif cash_gap_days > 30 or duty_amount > 10000:
            risk = "medium"
        else:
            risk = "low"

        # AI recommendation
        prompt = f"""An SMB is importing ${request.shipment_value:,.0f} worth of goods from {request.country_of_origin}.
Duty owed at port: ${duty_amount:,.0f} ({duty_rate*100:.1f}% rate).
They won't receive payment/revenue for {request.payment_terms_days} days.
Cash gap risk: {risk}.
Product: {request.product_description or request.hts_code or 'not specified'}.

Give 2-3 sentences of practical advice on how to manage this cash flow gap. Be specific and actionable.
Mention: duty deferral programs, CBP bond options, or renegotiating payment terms with supplier.
Keep it plain English, no jargon."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a trade finance advisor helping small business owners manage tariff cash flow."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        recommendation = response.choices[0].message.content

        financing_options = [
            FinancingOption(
                name="CBP Continuous Bond",
                description="A $50K bond covers unlimited entries. Duty payment deferred up to 10 days after entry.",
                typical_cost_percent=0.5
            ),
            FinancingOption(
                name="Duty Deferral (FTZ)",
                description="Import into a Foreign Trade Zone — duties deferred until goods leave the zone.",
                typical_cost_percent=0.3
            ),
            FinancingOption(
                name="Trade Finance Line of Credit",
                description="Short-term revolving credit specifically for import duty payments.",
                typical_cost_percent=8.0
            ),
        ]

        return CashFlowForecastResponse(
            shipment_value=request.shipment_value,
            duty_rate_percent=round(duty_rate * 100, 2),
            duty_due_amount=round(duty_amount, 2),
            due_date=due_date.strftime("%Y-%m-%d"),
            estimated_revenue_date=revenue_date.strftime("%Y-%m-%d"),
            cash_gap_days=cash_gap_days,
            cash_gap_amount=round(cash_gap_amount, 2),
            cash_gap_risk=risk,
            ai_recommendation=recommendation,
            financing_options=financing_options,
            tariff_programs_applied=programs
        )

    except openai.APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")
