"""
USITC HTS Live API Client
=========================
Wraps the live USITC Harmonized Tariff Schedule REST API at
https://hts.usitc.gov/reststop with a 24-hour in-memory cache.

Endpoints used:
  GET /search?keyword={term}           — keyword / description search
  GET /getRates?htsno={code}&keyword=  — full chapter dump (used for code lookup)

Startup indexing:
  Call `await warm_cache()` during app startup to pre-load popular chapters.
"""

import re
import time
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

USITC_BASE = "https://hts.usitc.gov/reststop"

# ---------------------------------------------------------------------------
# Simple TTL cache
# ---------------------------------------------------------------------------
class _TTLCache:
    def __init__(self, ttl: int = 86400):
        self._store: dict[str, tuple[float, object]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[object]:
        entry = self._store.get(key)
        if entry and (time.time() - entry[0]) < self._ttl:
            return entry[1]
        return None

    def set(self, key: str, value: object) -> None:
        self._store[key] = (time.time(), value)

    def size(self) -> int:
        return len(self._store)


_cache = _TTLCache(ttl=86400)  # 24-hour TTL

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_HTML_TAG = re.compile(r"<[^>]+>")


def parse_rate(rate_str: str) -> Optional[float]:
    """
    Parse USITC rate strings to a float percentage.
    Handles: 'Free', '3.3%', '15¢/kg + 6.5%', 'No change', HTML-wrapped strings.
    Returns None if unparseable (e.g. specific/compound rates with no % component).
    """
    if not rate_str:
        return None
    clean = _HTML_TAG.sub("", rate_str).strip()
    if clean.lower() in ("free", "", "no change"):
        return 0.0
    m = re.search(r"(\d+\.?\d*)\s*%", clean)
    if m:
        return float(m.group(1))
    return None


def _is_real_code(htsno: str) -> bool:
    """Filter out section/chapter header rows that have no numeric HTS code."""
    return bool(htsno and re.match(r"^\d{4}", htsno))


def _normalize(entry: dict) -> dict:
    """Normalize a raw USITC API entry to a consistent shape."""
    return {
        "htsno": entry.get("htsno", ""),
        "description": _HTML_TAG.sub("", entry.get("description", "")).strip(),
        "general": entry.get("general", ""),
        "special": entry.get("special", ""),
        "other": entry.get("other", ""),
        "units": entry.get("units") or [],
        "indent": entry.get("indent", "0"),
        "general_rate": parse_rate(entry.get("general", "")),
    }


# ---------------------------------------------------------------------------
# Public search API
# ---------------------------------------------------------------------------

async def search_hts(keyword: str, limit: int = 15) -> list[dict]:
    """
    Search HTS codes by product description keyword.
    Uses the USITC /search endpoint with 24-hour result caching.

    Returns up to `limit` normalized entries with:
      htsno, description, general, special, other, units, indent, general_rate
    """
    key = keyword.lower().strip()
    cache_key = f"search:{key}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached[:limit]  # type: ignore[index]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{USITC_BASE}/search", params={"keyword": keyword})
            resp.raise_for_status()
            raw: list[dict] = resp.json()
    except Exception as exc:
        logger.warning("USITC search failed for '%s': %s", keyword, exc)
        return []

    results = [_normalize(e) for e in raw if _is_real_code(e.get("htsno", ""))]
    _cache.set(cache_key, results)
    logger.debug("USITC search '%s' → %d results (cached)", keyword, len(results))
    return results[:limit]


async def get_hts_rates(htsno: str) -> Optional[dict]:
    """
    Look up duty rates for a specific HTS code.

    Strategy:
      1. Exact htsno match in a search of that code string
      2. Dotless match  (8471.30.01.00 == 8471300100)
      3. Prefix match   (8471.30 → 8471.30.01.00)
    """
    normalized = htsno.strip()
    cache_key = f"rates:{normalized}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached  # type: ignore[return-value]

    results = await search_hts(normalized, limit=50)
    dotless = normalized.replace(".", "")

    # Exact match
    for entry in results:
        if entry["htsno"] == normalized:
            _cache.set(cache_key, entry)
            return entry

    # Dotless match
    for entry in results:
        if entry["htsno"].replace(".", "") == dotless:
            _cache.set(cache_key, entry)
            return entry

    # Prefix match — prefer entries that have a parsed rate
    prefix = normalized.rstrip("0").rstrip(".")
    for entry in results:
        if entry["htsno"].startswith(prefix) and entry.get("general_rate") is not None:
            _cache.set(cache_key, entry)
            return entry

    return None


# ---------------------------------------------------------------------------
# Startup warm-up — pre-loads the most common import chapters
# ---------------------------------------------------------------------------
_WARM_CHAPTERS = [
    "8471",   # computers / laptops
    "8517",   # phones / comms equipment
    "8528",   # monitors / TVs
    "8544",   # insulated wire / cables
    "6110",   # sweaters / knitwear
    "6109",   # T-shirts
    "6204",   # women's apparel
    "6203",   # men's apparel
    "6403",   # footwear
    "8708",   # auto parts
    "3926",   # plastic articles
    "7318",   # screws / fasteners
    "9403",   # furniture
]


async def warm_cache() -> None:
    """Pre-load popular HTS chapters into the in-memory cache at startup."""
    logger.info("Warming HTS cache for %d chapters…", len(_WARM_CHAPTERS))
    for chapter in _WARM_CHAPTERS:
        try:
            await search_hts(chapter, limit=50)
        except Exception as exc:
            logger.warning("Cache warm-up failed for chapter %s: %s", chapter, exc)
    logger.info("HTS cache warm-up complete. Cache size: %d entries", _cache.size())
