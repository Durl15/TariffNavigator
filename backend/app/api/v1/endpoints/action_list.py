"""
Monday Morning Action List - AI-ranked priority actions by ROI.
Aggregates user data to surface top opportunities.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timedelta
import openai
from openai import AsyncOpenAI

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.catalog import Catalog, CatalogItem
from app.models.notification import Notification
from app.models.watchlist import Watchlist
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class Action(BaseModel):
    id: str
    title: str
    description: str
    category: str  # refund | compliance | savings | cash_flow | alert
    estimated_dollar_impact: Optional[float]
    urgency: str  # high | medium | low
    deadline: Optional[str]
    cta_label: str
    cta_url: str
    icon: str  # emoji for quick visual scan


class ActionListResponse(BaseModel):
    actions: List[Action]
    total_opportunity: float
    generated_at: str
    summary: str


@router.get("", response_model=ActionListResponse)
async def get_action_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns top 5 prioritized actions ranked by dollar impact.
    Aggregates data from catalogs, notifications, watchlists.
    """
    try:
        actions: List[Action] = []
        total_opportunity = 0.0

        # --- Check catalogs for high tariff exposure ---
        catalog_result = await db.execute(
            select(Catalog).where(Catalog.user_id == current_user.id)
            .order_by(Catalog.created_at.desc()).limit(5)
        )
        catalogs = catalog_result.scalars().all()

        if catalogs:
            latest = catalogs[0]
            # Check for high-exposure items (CN origin)
            cn_items_result = await db.execute(
                select(func.count(CatalogItem.id), func.sum(CatalogItem.tariff_cost_annual))
                .where(
                    CatalogItem.catalog_id == latest.id,
                    CatalogItem.country_of_origin == "CN"
                )
            )
            cn_row = cn_items_result.first()
            cn_count = cn_row[0] or 0
            cn_exposure = float(cn_row[1] or 0)

            if cn_count > 0 and cn_exposure > 1000:
                impact = round(cn_exposure * 0.15, 2)  # 15% potential savings via alt sourcing
                total_opportunity += impact
                actions.append(Action(
                    id="alt_sourcing",
                    title=f"Reduce ${cn_exposure:,.0f} China tariff exposure",
                    description=f"You have {cn_count} SKUs from China in '{latest.name}' with ${cn_exposure:,.0f}/yr in tariffs. Vietnam or Mexico alternatives could save ~15%.",
                    category="savings",
                    estimated_dollar_impact=impact,
                    urgency="high",
                    deadline=None,
                    cta_label="View Catalog Impact",
                    cta_url=f"/catalogs/{latest.id}/impact",
                    icon="🔄"
                ))

        # --- Drawback reminder ---
        # If user has catalogs with CN imports, drawback is likely applicable
        if catalogs:
            actions.append(Action(
                id="drawback",
                title="Recover unpaid duty drawback refunds",
                description="Most importers miss duty drawback. If you re-export any products or use them in manufacturing, you may recover 99% of duties paid.",
                category="refund",
                estimated_dollar_impact=None,
                urgency="medium",
                deadline="5 years from import date",
                cta_label="Check Drawback Eligibility",
                cta_url="/drawback",
                icon="💰"
            ))

        # --- Unread high-priority notifications ---
        notif_result = await db.execute(
            select(Notification).where(
                Notification.user_id == current_user.id,
                Notification.read == False
            ).order_by(Notification.created_at.desc()).limit(3)
        )
        notifications = notif_result.scalars().all()

        if notifications:
            actions.append(Action(
                id="unread_alerts",
                title=f"Review {len(notifications)} unread tariff alerts",
                description=f"You have {len(notifications)} unread rate change notifications that may affect your import costs.",
                category="alert",
                estimated_dollar_impact=None,
                urgency="high",
                deadline="Act before next shipment",
                cta_label="View Alerts",
                cta_url="/notifications",
                icon="🔔"
            ))

        # --- HTS audit nudge ---
        actions.append(Action(
            id="hts_audit",
            title="Audit your HTS codes for overpayment",
            description="Supplier-provided HTS codes have no incentive to minimize your duties. A 5-minute audit often finds 3-20% overpayment.",
            category="savings",
            estimated_dollar_impact=None,
            urgency="medium",
            deadline=None,
            cta_label="Run HTS Audit",
            cta_url="/hts-audit",
            icon="🔍"
        ))

        # --- Cash flow check if no forecast done recently ---
        actions.append(Action(
            id="cashflow",
            title="Forecast your next shipment's duty cash gap",
            description="Know exactly how much cash you need at port before your shipment arrives. Avoid scrambling for $10K-$50K+ on short notice.",
            category="cash_flow",
            estimated_dollar_impact=None,
            urgency="low",
            deadline=None,
            cta_label="Run Cash Flow Forecast",
            cta_url="/cashflow",
            icon="📊"
        ))

        # --- USMCA check if MX/CA in catalogs ---
        has_usmca_opportunity = False
        if catalogs:
            mx_check = await db.execute(
                select(func.count(CatalogItem.id)).where(
                    CatalogItem.catalog_id == catalogs[0].id,
                    CatalogItem.country_of_origin.in_(["MX", "CA"])
                )
            )
            mx_count = mx_check.scalar() or 0
            if mx_count > 0:
                has_usmca_opportunity = True
                actions.insert(1, Action(
                    id="usmca",
                    title=f"Verify USMCA eligibility on {mx_count} Mexico/Canada items",
                    description=f"You have {mx_count} items from Mexico/Canada. Missing USMCA documentation means paying MFN rates you don't legally owe.",
                    category="savings",
                    estimated_dollar_impact=None,
                    urgency="high",
                    deadline="Before next CBP audit",
                    cta_label="Check USMCA Eligibility",
                    cta_url="/usmca-check",
                    icon="🇺🇸"
                ))

        # Sort by urgency then dollar impact
        urgency_order = {"high": 0, "medium": 1, "low": 2}
        actions.sort(key=lambda a: (
            urgency_order.get(a.urgency, 2),
            -(a.estimated_dollar_impact or 0)
        ))

        # Keep top 6
        actions = actions[:6]

        # Generate AI summary
        action_titles = [a.title for a in actions[:3]]
        total_opportunity = sum(a.estimated_dollar_impact or 0 for a in actions)

        try:
            summary_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a trade finance advisor. Be concise and motivating."},
                    {"role": "user", "content": f"Write one sentence (max 20 words) summarizing these top actions for an SMB importer: {', '.join(action_titles)}"}
                ],
                temperature=0.3,
                max_tokens=60
            )
            summary = summary_response.choices[0].message.content
        except Exception:
            summary = "Take action on your highest-impact tariff opportunities this week."

        return ActionListResponse(
            actions=actions,
            total_opportunity=total_opportunity,
            generated_at=datetime.now().isoformat(),
            summary=summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action list error: {str(e)}")
