"""
AI Chatbot Assistant API - Help users with HS codes, tariffs, and app usage
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from pydantic import BaseModel
import openai
from openai import AsyncOpenAI

from app.db.session import get_db
from app.core.config import settings
from app.models.hs_code import HSCode

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[dict]] = None


SYSTEM_PROMPT = """You are TariffNavigator AI — an expert in U.S. import tariffs, customs compliance, and trade finance, built for American small business importers.

## Current U.S. Tariff Landscape (2026)
- China (CN): ~39.5% effective rate (25% Section 301 + 14.5% IEEPA reciprocal)
- Mexico/Canada: 0% under USMCA for qualifying goods; 25% IEEPA if non-qualifying
- Vietnam, Thailand, Malaysia: MFN rates (~8-12%), but transshipment scrutiny for Chinese-origin components
- South Korea: 0% under KORUS FTA
- India: MFN ~8% (GSP expired 2019)
- USMCA renegotiation due July 2026 — watch for changes

## TariffNavigator Platform Tools (route users to these)
1. **Calculator** → /calculator — Stacked duty rate lookup (Section 301 + IEEPA + USMCA + AD/CVD)
2. **Cash Flow Forecaster** → /cashflow — Duty cash obligation at port vs. revenue timing
3. **Drawback Finder** → /drawback — Recover up to 99% of duties paid (unused merchandise, manufacturing)
4. **USMCA Checker** → /usmca-check — Verify 0% eligibility for Mexico/Canada goods
5. **Supply Chain Scanner** → /supply-chain — Detect transshipment risk and Section 301 exposure from Chinese components
6. **HTS Code Audit** → /hts-audit — Catch supplier misclassifications causing overpayment
7. **Alternative Sourcing Finder** → /sourcing — Rank 13 countries by tariff rate for any HTS code
8. **Scenario Planner** → /scenarios — "What if China snaps back to 145%?" against real catalog data
9. **Catalogs** → /catalogs — Upload product CSV for portfolio-wide impact analysis
10. **Watchlists** → /watchlists — Monitor rate changes for specific HTS codes and countries

## Your Job
- Answer tariff questions accurately using current 2026 rates
- When user describes a problem, identify which tool solves it and route them there
- Suggest HTS codes when user describes products
- Give specific, actionable advice — not generic disclaimers
- Keep responses under 200 words unless a detailed explanation is needed
- Use dollar figures when possible ("at 39.5% that's $19,750 on a $50K shipment")

## Tool Routing Rules
- "how much duty on..." → Calculator + give rough estimate
- "cash flow" / "duty at port" / "need cash" → Cash Flow Forecaster
- "get money back" / "refund" / "drawback" → Drawback Finder
- "Mexico" / "Canada" / "USMCA" / "certificate of origin" → USMCA Checker
- "Vietnam" / "transshipment" / "Chinese components" / "CBP penalty" → Supply Chain Scanner
- "wrong HTS" / "overpaying" / "supplier gave me" / "misclassified" → HTS Code Audit
- "alternative sourcing" / "cheaper country" / "switch from China" → Alternative Sourcing Finder
- "what if" / "scenario" / "China at 145%" / "IEEPA struck down" → Scenario Planner
- "upload products" / "my catalog" / "all my SKUs" → Catalogs

Always be direct, specific, and financially concrete. Small businesses need to act — not just understand."""


async def search_hs_codes(db: AsyncSession, query: str, country: str = "CN", limit: int = 5) -> List[dict]:
    """Search HS codes by description or code"""
    search_term = f"%{query}%"

    stmt = select(HSCode).where(
        HSCode.country == country,
        or_(
            HSCode.code.ilike(search_term),
            HSCode.description.ilike(search_term)
        )
    ).limit(limit)

    result = await db.execute(stmt)
    hs_codes = result.scalars().all()

    return [
        {
            "code": hs.code,
            "description": hs.description,
            "mfn_rate": float(hs.mfn_rate) if hs.mfn_rate else 0,
            "vat_rate": float(hs.vat_rate) if hs.vat_rate else 0
        }
        for hs in hs_codes
    ]


@router.post("", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with TariffNavigator AI Assistant.

    The assistant can:
    - Help identify correct HS codes for products
    - Explain tariff rates and regulations
    - Guide users through app features

    **Example questions:**
    - "What's the HS code for leather shoes?"
    - "How much duty for importing cars to China?"
    - "How do I create a watchlist?"
    """
    try:
        # Build conversation history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add previous messages
        for msg in request.history[-10:]:  # Keep last 10 messages for context
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": request.message})

        msg_lower = request.message.lower()
        suggested_actions = []
        hs_context = ""

        # ── Tool routing: detect intent and pre-populate suggested actions ──
        TOOL_ROUTES = [
            (["cash flow", "duty at port", "cash gap", "cash before", "port payment", "cash needed"], "/cashflow", "Open Cash Flow Forecaster"),
            (["drawback", "get money back", "refund my duty", "recover duties", "99% back"], "/drawback", "Open Drawback Finder"),
            (["usmca", "certificate of origin", "mexico qualify", "canada qualify", "0% from mexico"], "/usmca-check", "Check USMCA Eligibility"),
            (["transshipment", "chinese components", "vietnam factory", "cbp penalty", "supply chain risk"], "/supply-chain", "Open Supply Chain Scanner"),
            (["wrong hts", "overpaying", "misclassified", "supplier code", "hts audit", "wrong code"], "/hts-audit", "Run HTS Audit"),
            (["cheaper country", "alternative sourcing", "switch from china", "lower tariff country", "sourcing alternative"], "/sourcing", "Open Sourcing Finder"),
            (["what if", "scenario", "145%", "ieepa struck", "if tariffs", "usmca fails", "model impact"], "/scenarios", "Open Scenario Planner"),
            (["upload catalog", "my products", "all my skus", "portfolio impact", "bulk analysis"], "/catalogs", "Go to Catalogs"),
            (["watchlist", "alert", "notify me", "monitor"], "/watchlists", "Manage Watchlists"),
            (["calculate", "how much duty", "tariff rate", "hs code"], "/calculator", "Open Calculator"),
        ]

        for keywords, path, label in TOOL_ROUTES:
            if any(kw in msg_lower for kw in keywords):
                suggested_actions.append({"type": "tool_link", "label": label, "url": path})
                if len(suggested_actions) >= 2:
                    break

        # ── HS code lookup if product mentioned ──
        product_keywords = ["hs code", "tariff for", "import", "what is the code", "classify"]
        should_search_hs = any(kw in msg_lower for kw in product_keywords)

        if should_search_hs:
            search_query = msg_lower
            for kw in ["hs code for", "tariff for", "importing", "import", "classify"]:
                if kw in search_query:
                    search_query = search_query.split(kw)[-1].strip()
                    break
            cn_codes = await search_hs_codes(db, search_query, "CN", 3)
            if cn_codes:
                hs_context = "\n\nRelevant HS Codes in database:\n"
                for code in cn_codes:
                    hs_context += f"- {code['code']}: {code['description']} (MFN: {code['mfn_rate']}%)\n"
                    if not any(a.get("url") == "/calculator" for a in suggested_actions):
                        suggested_actions.append({
                            "type": "calculate",
                            "label": f"Calculate tariff for {code['code']}",
                            "data": {"hs_code": code['code'], "country": "CN"},
                            "url": "/calculator"
                        })

        if hs_context:
            messages[-1]["content"] += hs_context

        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        return ChatResponse(
            response=assistant_message,
            suggested_actions=suggested_actions if suggested_actions else None
        )

    except openai.APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """Check if OpenAI API key is configured"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured"
        )
    return {"status": "ready", "model": "gpt-4o-mini"}
