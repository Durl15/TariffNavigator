"""
Alternative Sourcing Finder — Module 4
For any HTS code, find countries with lower US tariff rates and rank by savings potential.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import openai
from openai import AsyncOpenAI

from app.db.session import get_db
from app.models.hs_code import HSCode
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# US tariff rates by origin country (stacked: MFN + active programs as of 2026)
# Format: {country_code: (effective_rate, note, trade_agreement, risk_score)}
COUNTRY_PROFILES = {
    "CN": {
        "name": "China",
        "effective_rate": 0.395,   # 25% Section 301 + 14.5% IEEPA = ~39.5% stacked
        "note": "Section 301 (25%) + IEEPA reciprocal (14.5%)",
        "trade_agreement": None,
        "risk": 85,
        "supply_reliability": 70,
        "lead_time_weeks": 4,
    },
    "VN": {
        "name": "Vietnam",
        "effective_rate": 0.10,    # MFN rate ~10% average, no FTA
        "note": "MFN only — no US-Vietnam FTA. Watch for transshipment scrutiny.",
        "trade_agreement": None,
        "risk": 45,
        "supply_reliability": 75,
        "lead_time_weeks": 5,
    },
    "IN": {
        "name": "India",
        "effective_rate": 0.08,
        "note": "MFN rate. GSP expired 2019. Some sectors have 0%.",
        "trade_agreement": None,
        "risk": 40,
        "supply_reliability": 65,
        "lead_time_weeks": 6,
    },
    "MX": {
        "name": "Mexico",
        "effective_rate": 0.0,
        "note": "USMCA — 0% for qualifying goods. Non-qualifying: 25% IEEPA.",
        "trade_agreement": "USMCA",
        "risk": 30,
        "supply_reliability": 80,
        "lead_time_weeks": 2,
    },
    "CA": {
        "name": "Canada",
        "effective_rate": 0.0,
        "note": "USMCA — 0% for qualifying goods.",
        "trade_agreement": "USMCA",
        "risk": 15,
        "supply_reliability": 90,
        "lead_time_weeks": 1,
    },
    "KR": {
        "name": "South Korea",
        "effective_rate": 0.0,
        "note": "KORUS FTA — most goods 0%.",
        "trade_agreement": "KORUS",
        "risk": 20,
        "supply_reliability": 85,
        "lead_time_weeks": 3,
    },
    "TW": {
        "name": "Taiwan",
        "effective_rate": 0.035,
        "note": "MFN rate only. No US-Taiwan FTA (informal relations). Strong semiconductor sector.",
        "trade_agreement": None,
        "risk": 55,  # geopolitical
        "supply_reliability": 80,
        "lead_time_weeks": 3,
    },
    "TH": {
        "name": "Thailand",
        "effective_rate": 0.08,
        "note": "MFN rate. No US-Thailand FTA. Large electronics/auto sector.",
        "trade_agreement": None,
        "risk": 40,
        "supply_reliability": 72,
        "lead_time_weeks": 5,
    },
    "MY": {
        "name": "Malaysia",
        "effective_rate": 0.08,
        "note": "MFN rate. Major electronics exporter. Transshipment scrutiny for solar panels.",
        "trade_agreement": None,
        "risk": 45,
        "supply_reliability": 78,
        "lead_time_weeks": 4,
    },
    "JP": {
        "name": "Japan",
        "effective_rate": 0.025,
        "note": "MFN rate. No comprehensive US-Japan FTA. High quality, higher cost.",
        "trade_agreement": None,
        "risk": 10,
        "supply_reliability": 95,
        "lead_time_weeks": 3,
    },
    "EU": {
        "name": "European Union",
        "effective_rate": 0.035,
        "note": "MFN rate. No US-EU FTA. Higher labor cost but strong quality.",
        "trade_agreement": None,
        "risk": 15,
        "supply_reliability": 90,
        "lead_time_weeks": 3,
    },
    "BD": {
        "name": "Bangladesh",
        "effective_rate": 0.12,
        "note": "MFN rate. Major garment exporter. Limited non-apparel capacity.",
        "trade_agreement": None,
        "risk": 50,
        "supply_reliability": 60,
        "lead_time_weeks": 7,
    },
    "ID": {
        "name": "Indonesia",
        "effective_rate": 0.08,
        "note": "MFN rate. Growing manufacturing base.",
        "trade_agreement": None,
        "risk": 40,
        "supply_reliability": 68,
        "lead_time_weeks": 5,
    },
}


class SourcingAlternative(BaseModel):
    country_code: str
    country_name: str
    effective_rate_percent: float
    rate_note: str
    trade_agreement: Optional[str]
    annual_savings: Optional[float]
    savings_percent: float
    risk_score: int       # 0-100, lower is better
    supply_reliability: int  # 0-100, higher is better
    lead_time_weeks: int
    recommended: bool


class SourcingResponse(BaseModel):
    hts_code: str
    current_country: str
    current_rate_percent: float
    annual_import_value: Optional[float]
    alternatives: List[SourcingAlternative]
    top_pick: Optional[str]
    ai_analysis: str
    caveat: str


@router.get("/{hts_code}", response_model=SourcingResponse)
async def find_alternative_sources(
    hts_code: str,
    current_country: str = "CN",
    annual_import_value: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Find countries with lower US tariff rates for a given HTS code.
    Ranks alternatives by: tariff savings %, supply reliability, lead time, risk.
    """
    try:
        current_country = current_country.upper()
        current_profile = COUNTRY_PROFILES.get(current_country)
        if not current_profile:
            raise HTTPException(status_code=400, detail=f"Unknown country: {current_country}")

        current_rate = current_profile["effective_rate"]

        # Try to get MFN base rate from DB for this HTS code
        db_rate = None
        try:
            result = await db.execute(
                select(HSCode).where(
                    HSCode.code.ilike(f"{hts_code}%"),
                    HSCode.country == "CN"
                ).limit(1)
            )
            hs = result.scalar_one_or_none()
            if hs and hs.mfn_rate is not None:
                db_rate = float(hs.mfn_rate) / 100  # stored as percentage
        except Exception:
            pass  # fall back to profile rates

        alternatives = []
        for code, profile in COUNTRY_PROFILES.items():
            if code == current_country:
                continue

            alt_rate = profile["effective_rate"]
            # If we have a DB MFN rate, adjust non-special-program countries
            if db_rate is not None and profile["trade_agreement"] is None and code not in ["CN"]:
                # Use DB rate as base + country-specific adjustments
                alt_rate = max(alt_rate, db_rate)

            savings_pct = ((current_rate - alt_rate) / current_rate * 100) if current_rate > 0 else 0
            annual_savings = None
            if annual_import_value and savings_pct > 0:
                annual_savings = round(annual_import_value * (current_rate - alt_rate), 2)

            alternatives.append(SourcingAlternative(
                country_code=code,
                country_name=profile["name"],
                effective_rate_percent=round(alt_rate * 100, 2),
                rate_note=profile["note"],
                trade_agreement=profile["trade_agreement"],
                annual_savings=annual_savings,
                savings_percent=round(savings_pct, 1),
                risk_score=profile["risk"],
                supply_reliability=profile["supply_reliability"],
                lead_time_weeks=profile["lead_time_weeks"],
                recommended=False,
            ))

        # Sort: savings_pct desc, then risk asc, then supply_reliability desc
        alternatives.sort(key=lambda a: (-a.savings_percent, a.risk_score, -a.supply_reliability))

        # Mark top 3 as recommended
        for i, alt in enumerate(alternatives[:3]):
            if alt.savings_percent > 0:
                alternatives[i].recommended = True

        top_pick = alternatives[0].country_code if alternatives else None

        # AI analysis
        top_alts = [a for a in alternatives[:4] if a.savings_percent > 0]
        if top_alts:
            alt_summary = ", ".join([
                f"{a.country_name} ({a.effective_rate_percent}%, saves {a.savings_percent:.0f}%)"
                for a in top_alts[:3]
            ])
        else:
            alt_summary = "No significantly lower-rate alternatives found"

        prompt = f"""HTS code: {hts_code}
Current sourcing: {current_country} at {current_rate*100:.1f}% effective tariff rate
Top alternatives: {alt_summary}
Annual import value: ${annual_import_value:,.0f if annual_import_value else 'unknown'}

Write 2-3 sentences for an SMB owner:
1. Which alternative makes the most sense practically (not just lowest rate)?
2. The biggest real-world obstacle to switching (tooling, MOQ, quality, lead time)?
3. One action to take this week to evaluate the switch."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a supply chain consultant advising US small businesses on tariff-driven sourcing decisions. Be practical and honest about trade-offs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=250
        )

        return SourcingResponse(
            hts_code=hts_code,
            current_country=current_country,
            current_rate_percent=round(current_rate * 100, 2),
            annual_import_value=annual_import_value,
            alternatives=alternatives,
            top_pick=top_pick,
            ai_analysis=response.choices[0].message.content,
            caveat="Rates are estimates based on current tariff programs. Verify with CBP or a licensed customs broker before sourcing decisions."
        )

    except HTTPException:
        raise
    except openai.APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sourcing lookup error: {str(e)}")
