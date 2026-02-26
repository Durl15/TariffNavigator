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


SYSTEM_PROMPT = """You are TariffNavigator AI Assistant, an expert in international trade, customs duties, and HS codes.

Your capabilities:
1. **HS Code Identification**: Help users find the correct HS code for their products
2. **Tariff Explanations**: Explain customs duties, VAT rates, and trade regulations
3. **App Guidance**: Help users navigate and use TariffNavigator features

Key Features of TariffNavigator:
- Calculator: Calculate import duties for China (CN) and European Union (EU)
- Watchlists: Monitor tariff changes for specific HS codes (Pro feature)
- Catalogs: Bulk analyze product catalogs (Pro feature)
- Dashboard: View calculation history and statistics

Common Tariff Rates:
- China: Electronics (HS 8517, 8471) = 0% duty + 13% VAT
- China: Cars (HS 8703) = 15% duty + 13% VAT
- EU: Cars (HS 8703) = 10% duty + 20% VAT
- EU: Footwear (HS 6402) = 17% duty + 20% VAT

How to respond:
- Be concise and helpful
- When users describe products, suggest likely HS codes
- Explain tariff calculations clearly
- Guide users to relevant app features
- Use simple language, avoid jargon

If user asks to calculate tariffs, tell them to:
1. Use the Calculator page
2. Search for their product
3. Enter the CIF value
4. Click Calculate

Always be friendly, professional, and accurate."""


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

        # Check if user is asking about a product (potential HS code search)
        product_keywords = ["what is", "hs code", "tariff for", "importing", "import", "product", "item"]
        should_search_hs = any(keyword in request.message.lower() for keyword in product_keywords)

        # Search HS codes if relevant
        hs_context = ""
        suggested_actions = []

        if should_search_hs:
            # Extract potential product name from message
            search_query = request.message.lower()
            for keyword in ["hs code for", "tariff for", "importing", "import"]:
                if keyword in search_query:
                    search_query = search_query.split(keyword)[-1].strip()
                    break

            # Search both CN and EU
            cn_codes = await search_hs_codes(db, search_query, "CN", 3)

            if cn_codes:
                hs_context = f"\n\nRelevant HS Codes found:\n"
                for code in cn_codes:
                    hs_context += f"- {code['code']}: {code['description']} (CN: {code['mfn_rate']}% duty, {code['vat_rate']}% VAT)\n"
                    suggested_actions.append({
                        "type": "calculate",
                        "label": f"Calculate for {code['code']}",
                        "data": {"hs_code": code['code'], "country": "CN"}
                    })

        # Add HS context to last message if found
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
