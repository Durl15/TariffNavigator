"""
Scenario Planning Engine — Module 3 enhancement
"What if" tariff scenarios run against catalog data or manual input.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict
from openai import AsyncOpenAI

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.catalog import Catalog, CatalogItem
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "sk-not-configured")

# ─────────────────────────────────────────
# PRESET SCENARIOS
# ─────────────────────────────────────────
PRESETS: Dict[str, dict] = {
    "china_145": {
        "id": "china_145",
        "name": "China Tariffs Snap Back to 145%",
        "description": "IEEPA pause ends — China rates return to peak 145% (Section 301 25% + IEEPA 120%).",
        "icon": "🇨🇳",
        "color": "red",
        "overrides": {"CN": 1.45},
    },
    "ieepa_struck": {
        "id": "ieepa_struck",
        "name": "Supreme Court Strikes IEEPA Tariffs",
        "description": "Courts rule IEEPA tariffs unconstitutional. Only Section 301 China tariffs remain (25%).",
        "icon": "⚖️",
        "color": "green",
        "overrides": {"CN": 0.25, "MX": 0.0, "CA": 0.0},
    },
    "usmca_removed": {
        "id": "usmca_removed",
        "name": "USMCA 2026 Renegotiation Fails",
        "description": "July 2026 — USMCA collapses. Mexico and Canada revert to MFN rates (~5-15%).",
        "icon": "🇲🇽",
        "color": "orange",
        "overrides": {"MX": 0.08, "CA": 0.05},
    },
    "universal_10": {
        "id": "universal_10",
        "name": "Universal 10% Baseline Tariff",
        "description": "A flat 10% tariff is applied to all countries as a revenue measure.",
        "icon": "🌐",
        "color": "yellow",
        "overrides": "universal_10",
    },
    "china_zero": {
        "id": "china_zero",
        "name": "US-China Trade Deal (0% Truce)",
        "description": "Negotiated deal removes Section 301 and IEEPA tariffs on China.",
        "icon": "🤝",
        "color": "green",
        "overrides": {"CN": 0.035},
    },
    "custom": {
        "id": "custom",
        "name": "Custom Scenario",
        "description": "Set your own tariff rate per country.",
        "icon": "⚙️",
        "color": "blue",
        "overrides": {},
    },
}

# Current effective rates (baseline)
CURRENT_RATES = {
    "CN": 0.395,  # 25% S301 + 14.5% IEEPA
    "MX": 0.0,    # USMCA
    "CA": 0.0,    # USMCA
    "VN": 0.10,
    "IN": 0.08,
    "KR": 0.0,    # KORUS
    "TW": 0.035,
    "TH": 0.08,
    "EU": 0.035,
    "JP": 0.025,
    "MY": 0.08,
    "ID": 0.08,
}


class PresetScenario(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str


class ScenarioRunRequest(BaseModel):
    preset_id: Optional[str] = None       # Use a preset
    custom_overrides: Optional[Dict[str, float]] = None  # country → rate (0.25 = 25%)
    catalog_id: Optional[str] = None      # Run against a catalog
    # Manual mode — if no catalog
    annual_import_value: Optional[float] = None
    country_of_origin: Optional[str] = None


class ItemImpact(BaseModel):
    sku: str
    product_name: str
    country: str
    annual_volume: int
    cogs: float
    current_tariff_rate: float
    scenario_tariff_rate: float
    current_annual_tariff: float
    scenario_annual_tariff: float
    delta: float            # scenario - current (positive = more cost)
    margin_impact_pct: float


class ScenarioResult(BaseModel):
    scenario_name: str
    scenario_description: str
    current_total_tariff: float
    scenario_total_tariff: float
    total_delta: float
    total_delta_pct: float
    items_worse: int
    items_better: int
    items_unchanged: int
    item_impacts: List[ItemImpact]
    ai_executive_summary: str
    recommended_actions: List[str]


@router.get("/presets", response_model=List[PresetScenario])
async def get_presets():
    """Return list of preset scenarios."""
    return [
        PresetScenario(
            id=k,
            name=v["name"],
            description=v["description"],
            icon=v["icon"],
            color=v["color"]
        )
        for k, v in PRESETS.items()
        if k != "custom"
    ]


def get_rate_for_country(country: str, overrides: dict) -> float:
    """Get scenario rate for a country."""
    country = country.upper()
    if overrides == "universal_10":
        return 0.10
    return overrides.get(country, CURRENT_RATES.get(country, 0.035))


def get_current_rate(country: str) -> float:
    return CURRENT_RATES.get(country.upper(), 0.035)


@router.post("/run", response_model=ScenarioResult)
async def run_scenario(
    request: ScenarioRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run a what-if scenario against a product catalog or manual input.
    Returns per-item impact and executive summary.
    """
    try:
        # Resolve scenario
        if request.preset_id and request.preset_id in PRESETS:
            preset = PRESETS[request.preset_id]
            overrides = preset["overrides"]
            scenario_name = preset["name"]
            scenario_desc = preset["description"]
        elif request.custom_overrides:
            overrides = {k.upper(): v for k, v in request.custom_overrides.items()}
            scenario_name = "Custom Scenario"
            scenario_desc = "User-defined tariff rate overrides"
        else:
            raise HTTPException(status_code=400, detail="Provide preset_id or custom_overrides")

        item_impacts: List[ItemImpact] = []
        current_total = 0.0
        scenario_total = 0.0

        if request.catalog_id:
            # Verify ownership
            catalog_result = await db.execute(
                select(Catalog).where(
                    Catalog.id == request.catalog_id,
                    Catalog.user_id == current_user.id
                )
            )
            catalog = catalog_result.scalar_one_or_none()
            if not catalog:
                raise HTTPException(status_code=404, detail="Catalog not found")

            items_result = await db.execute(
                select(CatalogItem).where(CatalogItem.catalog_id == request.catalog_id).limit(500)
            )
            items = items_result.scalars().all()

            for item in items:
                country = (item.origin_country or "CN").upper()
                current_rate = get_current_rate(country)
                scenario_rate = get_rate_for_country(country, overrides)

                cogs = float(item.cogs or 0)
                volume = item.annual_volume or 0
                annual_value = cogs * volume

                current_tariff = annual_value * current_rate
                scenario_tariff = annual_value * scenario_rate
                delta = scenario_tariff - current_tariff

                retail = float(item.retail_price or cogs * 1.5)
                annual_revenue = retail * volume
                margin_impact = (delta / annual_revenue * 100) if annual_revenue > 0 else 0

                current_total += current_tariff
                scenario_total += scenario_tariff

                item_impacts.append(ItemImpact(
                    sku=item.sku or "",
                    product_name=item.product_name or item.sku or "",
                    country=country,
                    annual_volume=volume,
                    cogs=cogs,
                    current_tariff_rate=round(current_rate * 100, 2),
                    scenario_tariff_rate=round(scenario_rate * 100, 2),
                    current_annual_tariff=round(current_tariff, 2),
                    scenario_annual_tariff=round(scenario_tariff, 2),
                    delta=round(delta, 2),
                    margin_impact_pct=round(margin_impact, 2),
                ))

        elif request.annual_import_value and request.country_of_origin:
            country = request.country_of_origin.upper()
            current_rate = get_current_rate(country)
            scenario_rate = get_rate_for_country(country, overrides)
            current_total = request.annual_import_value * current_rate
            scenario_total = request.annual_import_value * scenario_rate

            item_impacts.append(ItemImpact(
                sku="manual",
                product_name=f"Import from {country}",
                country=country,
                annual_volume=1,
                cogs=request.annual_import_value,
                current_tariff_rate=round(current_rate * 100, 2),
                scenario_tariff_rate=round(scenario_rate * 100, 2),
                current_annual_tariff=round(current_total, 2),
                scenario_annual_tariff=round(scenario_total, 2),
                delta=round(scenario_total - current_total, 2),
                margin_impact_pct=0.0,
            ))
        else:
            raise HTTPException(status_code=400, detail="Provide catalog_id or annual_import_value + country_of_origin")

        total_delta = scenario_total - current_total
        total_delta_pct = (total_delta / current_total * 100) if current_total > 0 else 0
        items_worse = sum(1 for i in item_impacts if i.delta > 0)
        items_better = sum(1 for i in item_impacts if i.delta < 0)
        items_unchanged = sum(1 for i in item_impacts if i.delta == 0)

        # Sort by delta desc (worst hit first)
        item_impacts.sort(key=lambda x: -abs(x.delta))

        # AI executive summary
        direction = "increase" if total_delta > 0 else "decrease"
        top_hit = item_impacts[0] if item_impacts else None

        prompt = f"""Scenario: {scenario_name}
{scenario_desc}

Current annual tariff cost: ${current_total:,.0f}
Scenario annual tariff cost: ${scenario_total:,.0f}
Total change: ${abs(total_delta):,.0f} {direction} ({abs(total_delta_pct):.1f}%)
SKUs worse off: {items_worse}, better off: {items_better}
Hardest hit item: {f"{top_hit.product_name} from {top_hit.country} — delta ${top_hit.delta:,.0f}" if top_hit else "N/A"}

Write for a small business owner:
1. One sentence: overall impact of this scenario
2. What the owner should do RIGHT NOW to prepare (one specific action)
3. If this saves money: how to lock in the advantage. If it costs more: what's the fastest hedge.

Keep it under 100 words. Plain English."""

        summary = None
        if settings.OPENAI_API_KEY:
            try:
                ai_response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a trade finance strategist advising US small business importers. Be direct and actionable."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=200
                )
                summary = ai_response.choices[0].message.content
            except Exception:
                pass

        if not summary:
            if total_delta > 0:
                summary = (
                    f"This scenario would increase your annual tariff cost by ${total_delta:,.0f} ({total_delta_pct:.1f}%). "
                    f"Start modeling alternative sourcing options now — use the Sourcing Finder to identify lower-tariff countries "
                    f"for your highest-exposure SKUs before this scenario materializes."
                )
            elif total_delta < 0:
                summary = (
                    f"This scenario would reduce your annual tariff cost by ${abs(total_delta):,.0f} ({abs(total_delta_pct):.1f}%) — "
                    f"a significant opportunity. Position your supply chain now to capture these savings "
                    f"if this scenario occurs by locking in supplier agreements in the benefiting countries."
                )
            else:
                summary = "This scenario has minimal impact on your current tariff costs. Continue monitoring via your watchlists."

        # Recommended actions based on scenario
        actions = []
        if total_delta > 5000:
            actions.append(f"Accelerate sourcing diversification — this scenario adds ${total_delta:,.0f}/yr")
        if overrides == PRESETS.get("china_145", {}).get("overrides"):
            actions.append("Model Vietnam and Mexico alternatives using the Sourcing Finder")
        if "MX" in str(overrides) or "CA" in str(overrides):
            actions.append("Verify USMCA Certificates of Origin are current before renegotiation")
        if not actions:
            actions.append("Monitor this scenario via Watchlist alerts")
        actions.append("Export this scenario as PDF for financing or board review")

        return ScenarioResult(
            scenario_name=scenario_name,
            scenario_description=scenario_desc,
            current_total_tariff=round(current_total, 2),
            scenario_total_tariff=round(scenario_total, 2),
            total_delta=round(total_delta, 2),
            total_delta_pct=round(total_delta_pct, 2),
            items_worse=items_worse,
            items_better=items_better,
            items_unchanged=items_unchanged,
            item_impacts=item_impacts[:50],  # cap at 50 for response size
            ai_executive_summary=summary,
            recommended_actions=actions,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario run error: {str(e)}")
