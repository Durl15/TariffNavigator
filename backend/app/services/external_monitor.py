"""
External Data Monitor - Phase 3
Monitors Federal Register, CBP bulletins, and other sources for tariff changes.
"""
import logging
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import feedparser

from app.db.session import async_session
from app.models.tariff_change import TariffChangeLog
from app.services.change_monitor import match_and_notify
from app.services.document_parser import document_parser

logger = logging.getLogger(__name__)


class ExternalDataMonitor:
    """Monitor external sources for tariff changes."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.federal_register_api = "https://www.federalregister.gov/api/v1"
        self.cbp_bulletin_url = "https://www.cbp.gov/trade/quota/bulletins"

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def fetch_federal_register_updates(
        self,
        days_back: int = 7,
        keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent Federal Register documents about tariffs.

        API Docs: https://www.federalregister.gov/developers/api/v1

        Args:
            days_back: Number of days to look back
            keywords: Keywords to search for (default: tariff-related)

        Returns:
            List of document dictionaries
        """
        try:
            # Default keywords for tariff-related documents
            if keywords is None:
                keywords = [
                    "tariff",
                    "duty",
                    "harmonized tariff schedule",
                    "customs",
                    "import",
                    "section 301",
                    "section 232"
                ]

            # Build search query
            search_term = " OR ".join(keywords)
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            # Federal Register API parameters
            params = {
                "conditions[term]": search_term,
                "conditions[publication_date][gte]": start_date,
                "conditions[type][]": ["RULE", "PRORULE", "NOTICE"],
                "fields[]": [
                    "title",
                    "abstract",
                    "publication_date",
                    "html_url",
                    "document_number",
                    "agencies",
                    "type"
                ],
                "per_page": 20,
                "order": "newest"
            }

            logger.info(f"Fetching Federal Register documents from {start_date}")

            response = await self.client.get(
                f"{self.federal_register_api}/documents.json",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                documents = data.get("results", [])
                logger.info(f"Found {len(documents)} Federal Register documents")
                return documents
            else:
                logger.error(f"Federal Register API error: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching Federal Register updates: {str(e)}")
            return []

    async def fetch_cbp_bulletin(self) -> Optional[str]:
        """
        Fetch the latest CBP Weekly Bulletin.

        Returns:
            HTML content of latest bulletin or None
        """
        try:
            logger.info("Fetching CBP Weekly Bulletin")

            response = await self.client.get(self.cbp_bulletin_url)

            if response.status_code == 200:
                logger.info("Successfully fetched CBP bulletin")
                return response.text
            else:
                logger.error(f"CBP bulletin fetch error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching CBP bulletin: {str(e)}")
            return None

    async def parse_cbp_bulletin(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse CBP bulletin HTML to extract tariff-related updates.

        Args:
            html_content: HTML content of bulletin

        Returns:
            List of parsed updates
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            updates = []

            # Find bulletin links (CBP structure may vary)
            # This is a simplified parser - may need adjustment
            bulletin_links = soup.find_all('a', href=lambda x: x and 'bulletin' in x.lower())

            for link in bulletin_links[:10]:  # Limit to recent 10
                title = link.get_text(strip=True)
                url = link.get('href', '')

                # Ensure absolute URL
                if url and not url.startswith('http'):
                    url = f"https://www.cbp.gov{url}"

                if title and url:
                    updates.append({
                        'title': title,
                        'url': url,
                        'source': 'CBP Bulletin',
                        'date': datetime.now().isoformat()
                    })

            logger.info(f"Parsed {len(updates)} updates from CBP bulletin")
            return updates

        except Exception as e:
            logger.error(f"Error parsing CBP bulletin: {str(e)}")
            return []

    async def extract_tariff_info_ai(
        self,
        document: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Use Claude AI to extract tariff information from document.

        Args:
            document: Document dictionary with title, abstract, etc.

        Returns:
            Extracted tariff information or None
        """
        try:
            title = document.get('title', '')
            text = document.get('abstract', '')
            url = document.get('html_url', '')

            if not title or not text:
                return None

            # Use document parser service
            extracted = await document_parser.extract_tariff_changes(title, text, url)

            if extracted:
                logger.info(f"AI extracted tariff info from: {title[:50]}...")

            return extracted

        except Exception as e:
            logger.error(f"Error in AI extraction: {str(e)}")
            return None

    async def check_external_sources(self):
        """
        Main job: Check all external sources for tariff updates.
        Called by scheduler.
        """
        logger.info("Starting external source monitoring")

        try:
            async with async_session() as db:
                changes_detected = 0

                # 1. Check Federal Register
                fr_documents = await self.fetch_federal_register_updates(days_back=1)

                for doc in fr_documents:
                    # Extract tariff info using AI
                    tariff_info = await self.extract_tariff_info_ai(doc)

                    if tariff_info:
                        # Create change log entry
                        change = TariffChangeLog(
                            change_type='external_update',
                            hs_code=tariff_info.get('hs_codes', [''])[0] if tariff_info.get('hs_codes') else None,
                            country=tariff_info.get('countries', ['US'])[0] if tariff_info.get('countries') else 'US',
                            old_value={'rate': tariff_info.get('old_rate')},
                            new_value={'rate': tariff_info.get('new_rate')},
                            source='federal_register',
                            detected_at=datetime.utcnow(),
                            notifications_sent=False,
                            notification_count=0
                        )

                        db.add(change)
                        changes_detected += 1

                        # Match against watchlists and notify
                        await match_and_notify(change, db)

                # 2. Check CBP Bulletin
                cbp_html = await self.fetch_cbp_bulletin()
                if cbp_html:
                    cbp_updates = await self.parse_cbp_bulletin(cbp_html)
                    # Process CBP updates (similar to FR processing)
                    # Simplified for now

                if changes_detected > 0:
                    await db.commit()
                    logger.info(f"External monitoring complete: {changes_detected} changes detected")
                else:
                    logger.info("External monitoring complete: no new changes")

        except Exception as e:
            logger.error(f"Error in external source monitoring: {str(e)}", exc_info=True)


# Global instance
external_monitor = ExternalDataMonitor()


async def check_external_sources():
    """Scheduled job function."""
    await external_monitor.check_external_sources()
