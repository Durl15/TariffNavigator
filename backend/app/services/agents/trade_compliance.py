import json
import structlog
import re
from typing import List
from decimal import Decimal
from openai import AsyncOpenAI

from app.core.config import settings

logger = structlog.get_logger()

class TradeComplianceEngine:
    SECTION_301_RATES = {
        "LIST_1": Decimal("0.25"), "LIST_2": Decimal("0.25"),
        "LIST_3": Decimal("0.25"), "LIST_4A": Decimal("0.075"),
        "LIST_4B": Decimal("0.25"),
    }
    
    def __init__(self):
        if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 50:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        else:
            self.client = None
            logger.warning("No valid OpenAI API key found")
    
    async def classify_product(self, request) -> List[dict]:
        if self.client is None:
            return self._mock_classify(request)
        
        try:
            return await self._openai_classify(request)
        except Exception as e:
            logger.error("OpenAI error, falling back to mock", error=str(e))
            return self._mock_classify(request)
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from text, handling various formats"""
        # Try to find JSON object in text
        patterns = [
            r'\{[\s\S]*\}',  # Match anything between { and }
            r'```json\s*([\s\S]*?)\s*```',  # Markdown JSON
            r'```\s*([\s\S]*?)\s*```',  # Generic markdown
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        
        # Try parsing the whole text
        return json.loads(text)
    
    async def _openai_classify(self, request) -> List[dict]:
        system_prompt = """You are a senior customs broker. Classify products and return ONLY a JSON object.

Example response:
{
  "hts_code": "8518.30.20",
  "description": "Headphones, whether or not combined with microphone",
  "general_rate": 0.0,
  "confidence": 0.92,
  "rationale": "Product is wireless headphones for audio playback",
  "section_301_applicable": true
}

Rules:
- hts_code: must be format xxxx.xx.xx
- general_rate: number between 0-100
- confidence: number between 0-1
- section_301_applicable: true/false (true for China electronics)"""

        user_prompt = f"""Product: {request.product_description}
Materials: {request.material_composition or 'Not specified'}
Use: {request.intended_use or 'General'}

Return ONLY the JSON object, no other text."""

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI raw response: {content[:200]}...")
        
        # Parse JSON
        result = self._extract_json(content)
        logger.info("OpenAI JSON parsed successfully")
        
        # Ensure it's a list
        if isinstance(result, dict):
            suggestions = [result]
        elif isinstance(result, list):
            suggestions = result
        else:
            raise ValueError("Unexpected response format")
        
        # Convert to our format
        formatted = []
        for s in suggestions:
            hts = s.get("hts_code", "9999.99.99")
            
            # Determine Section 301 based on HTS code patterns
            section_301 = None
            if hts.startswith(("8471", "8517", "8518", "8528")):
                section_301 = Decimal("0.075")  # 7.5% for electronics
            
            formatted.append({
                "hts_code": hts,
                "description": s.get("description", "Unknown"),
                "general_rate": Decimal(str(s.get("general_rate", 0))),
                "section_301_rate": section_301,
                "confidence_score": s.get("confidence", 0.9),
                "rationale": s.get("rationale", "AI classification"),
                "citation": None,
                "alternatives": []
            })
        
        return formatted
    
    def _mock_classify(self, request) -> List[dict]:
        logger.info("Using mock classification")
        return [{
            "hts_code": "8471.30.01",
            "description": "Portable automatic data processing machines",
            "general_rate": Decimal("0.00"),
            "section_301_rate": Decimal("0.075"),
            "confidence_score": 0.94,
            "rationale": f"Based on: {request.product_description[:50]}... [MOCK]",
            "citation": "CBP Ruling HQ H087529",
            "alternatives": []
        }]
