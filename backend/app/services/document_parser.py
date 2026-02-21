"""
AI Document Parser - Phase 3
Uses Claude AI to extract tariff information from government documents.
"""
import logging
import json
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse government documents using Claude AI to extract tariff information."""

    def __init__(self):
        self.claude_api_key = settings.OPENAI_API_KEY  # Reuse existing API key
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def extract_tariff_changes(
        self,
        document_title: str,
        document_text: str,
        document_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Extract tariff change information from a document using Claude AI.

        Args:
            document_title: Title of the document
            document_text: Full text or abstract of the document
            document_url: Optional URL to the document

        Returns:
            Dictionary with extracted tariff information or None
        """
        try:
            prompt = self._build_extraction_prompt(
                document_title,
                document_text,
                document_url
            )

            # Use OpenAI API (which you already have configured)
            # Note: You can switch to Anthropic's Claude API if preferred
            response = await self._call_ai_api(prompt)

            if response:
                # Parse AI response
                extracted_data = self._parse_ai_response(response)
                return extracted_data

            return None

        except Exception as e:
            logger.error(f"Error extracting tariff changes: {str(e)}")
            return None

    def _build_extraction_prompt(
        self,
        title: str,
        text: str,
        url: Optional[str] = None
    ) -> str:
        """Build the prompt for AI extraction."""

        prompt = f"""You are an expert at analyzing government tariff documents. Extract structured information from this document.

Document Title: {title}

Document Text:
{text[:3000]}  # Limit text to 3000 chars

{f"Document URL: {url}" if url else ""}

Extract the following information if present. If information is not found, omit that field:

1. **HS Codes**: List of Harmonized System codes affected (e.g., ["8471.30", "8703.23"])
2. **Countries**: ISO 2-letter country codes affected (e.g., ["CN", "MX", "US"])
3. **Old Rate**: Previous duty rate (e.g., "2.5%")
4. **New Rate**: New duty rate (e.g., "25%")
5. **Effective Date**: When the change takes effect (YYYY-MM-DD format)
6. **Change Type**: Type of change (one of: "rate_increase", "rate_decrease", "new_duty", "duty_removal", "quota_change", "other")
7. **Summary**: Brief 1-2 sentence summary of the change

Return ONLY a valid JSON object with this structure:
{{
    "hs_codes": ["8471.30"],
    "countries": ["CN"],
    "old_rate": "2.5%",
    "new_rate": "25%",
    "effective_date": "2024-03-01",
    "change_type": "rate_increase",
    "summary": "Tariff increased from 2.5% to 25% on computer parts from China"
}}

If NO tariff information is found in the document, return:
{{
    "no_tariff_info": true
}}

Return ONLY the JSON, no other text."""

        return prompt

    async def _call_ai_api(self, prompt: str) -> Optional[str]:
        """
        Call AI API to get response.
        Uses OpenAI API (can be adapted for Claude/Anthropic API).
        """
        try:
            # Using OpenAI-compatible API
            from openai import OpenAI

            client = OpenAI(api_key=self.claude_api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Or your preferred model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured tariff information from government documents. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            return None

    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response text into structured data."""
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Parse JSON
            data = json.loads(cleaned)

            # Check if no tariff info found
            if data.get("no_tariff_info"):
                logger.info("AI detected no tariff information in document")
                return None

            # Validate required fields
            if not data.get("hs_codes") and not data.get("summary"):
                logger.warning("AI response missing critical fields")
                return None

            logger.info(f"Successfully extracted: {len(data.get('hs_codes', []))} HS codes")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return None

    async def batch_extract(
        self,
        documents: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Extract tariff info from multiple documents.

        Args:
            documents: List of document dictionaries

        Returns:
            List of extracted tariff information
        """
        results = []

        for doc in documents:
            title = doc.get("title", "")
            text = doc.get("abstract", "") or doc.get("text", "")
            url = doc.get("html_url", "") or doc.get("url", "")

            if title and text:
                extracted = await self.extract_tariff_changes(title, text, url)
                if extracted:
                    # Add source document info
                    extracted["source_document"] = {
                        "title": title,
                        "url": url,
                        "date": doc.get("publication_date") or doc.get("date")
                    }
                    results.append(extracted)

        logger.info(f"Batch extraction: {len(results)}/{len(documents)} documents had tariff info")
        return results


# Global instance
document_parser = DocumentParser()
