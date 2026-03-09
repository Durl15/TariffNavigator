"""
US Import Tariff Stacking Engine — 2026
Calculates effective duty rates for goods imported INTO the United States
by stacking all applicable tariff programs.

Sources:
  - Base MFN: US Harmonized Tariff Schedule (USITC), chapter averages
  - Section 301: USTR List 1-4A actions against China
  - IEEPA: Executive Orders (March 2026) — China 14.5%, MX/CA 25% non-qualifying
  - Section 232: National security tariffs (steel 25%, aluminum 10%, autos 25%)
  - USMCA: Free Trade Agreement with Mexico and Canada
"""

from typing import Optional

# ---------------------------------------------------------------------------
# US MFN rate by 2-digit HTS chapter (weighted averages, USITC 2025)
# ---------------------------------------------------------------------------
US_MFN_CHAPTER: dict[str, float] = {
    "01": 0.0,   "02": 3.0,   "03": 0.8,   "04": 17.5,  "05": 0.0,
    "06": 3.0,   "07": 5.5,   "08": 4.9,   "09": 0.0,   "10": 1.1,
    "11": 4.2,   "12": 0.9,   "13": 1.2,   "14": 0.0,   "15": 3.2,
    "16": 5.9,   "17": 5.5,   "18": 4.5,   "19": 4.3,   "20": 10.6,
    "21": 6.4,   "22": 5.0,   "23": 1.4,   "24": 91.6,  "25": 0.1,
    "26": 0.0,   "27": 1.4,   "28": 3.7,   "29": 3.7,   "30": 0.0,
    "31": 0.0,   "32": 3.7,   "33": 4.9,   "34": 2.2,   "35": 3.5,
    "36": 2.0,   "37": 3.0,   "38": 3.7,   "39": 5.3,   "40": 3.5,
    "41": 3.3,   "42": 9.0,   "43": 4.0,   "44": 3.2,   "45": 2.6,
    "46": 4.5,   "47": 0.0,   "48": 0.3,   "49": 0.0,   "50": 0.8,
    "51": 6.0,   "52": 10.0,  "53": 5.0,   "54": 8.0,   "55": 12.5,
    "56": 6.9,   "57": 5.8,   "58": 9.1,   "59": 7.0,   "60": 10.0,
    "61": 19.7,  "62": 16.0,  "63": 9.1,   "64": 10.0,  "65": 6.5,
    "66": 5.7,   "67": 3.6,   "68": 4.6,   "69": 5.4,   "70": 5.0,
    "71": 3.0,   "72": 0.5,   "73": 2.9,   "74": 3.0,   "75": 3.0,
    "76": 2.6,   "78": 2.5,   "79": 3.0,   "80": 2.0,   "81": 3.7,
    "82": 5.5,   "83": 5.7,   "84": 1.7,   "85": 1.5,   "86": 1.8,
    "87": 2.5,   "88": 0.0,   "89": 1.0,   "90": 2.0,   "91": 4.3,
    "92": 5.0,   "93": 3.0,   "94": 3.8,   "95": 0.0,   "96": 4.0,
    "97": 0.0,   "98": 0.0,   "99": 0.0,
}

# ---------------------------------------------------------------------------
# Section 301 (China) by 2-digit chapter
# List 4A = 7.5% (consumer goods); all others = 25%
# ---------------------------------------------------------------------------
_LIST_4A_CHAPTERS = {
    "61", "62", "63", "64",          # apparel & footwear (consumer)
    "85",                             # consumer electronics (phones, laptops)
    "95",                             # toys and games
    "42",                             # handbags / leather goods
    "71",                             # jewelry
    "90",                             # cameras, watches
}

def _section_301_rate(chapter: str) -> float:
    """Return Section 301 rate for a China-origin HTS chapter."""
    return 7.5 if chapter in _LIST_4A_CHAPTERS else 25.0

# ---------------------------------------------------------------------------
# IEEPA reciprocal tariffs (March 2026)
# ---------------------------------------------------------------------------
_IEEPA_RATES: dict[str, float] = {
    "CN": 14.5,   # Executive Order — China
    "MX": 25.0,   # IEEPA (non-USMCA goods)
    "CA": 25.0,   # IEEPA (non-USMCA goods)
}

# ---------------------------------------------------------------------------
# Section 232 national-security surcharges (all origins)
# ---------------------------------------------------------------------------
_SECTION_232: dict[str, float] = {
    "72": 25.0,   # steel mill products
    "73": 25.0,   # steel articles
    "74": 0.0,    # copper (proposed but not enacted as of Mar 2026)
    "76": 10.0,   # aluminum
    "87": 25.0,   # passenger automobiles & light trucks
}

# ---------------------------------------------------------------------------
# Countries where USMCA/KORUS/etc. eliminates MFN duty
# ---------------------------------------------------------------------------
_FTA_ZERO_COUNTRIES = {
    "MX": "USMCA",   # qualifying goods
    "CA": "USMCA",   # qualifying goods
    "KR": "KORUS",
    "AU": "AUSFTA",
    "SG": "USSFTA",
    "IL": "US-Israel FTA",
    "JO": "US-Jordan FTA",
}

# USMCA-qualified chapters (simplified — goods with sufficient North American content)
# In practice every chapter can qualify; we default to qualifying unless user says otherwise
_USMCA_QUALIFYING = True   # frontend can expose an override


def get_us_mfn_rate(hts_code: str, db_mfn_rate: Optional[float] = None) -> float:
    """
    Return the US MFN base rate for an HTS code.
    Prefers db_mfn_rate if provided (from USITC-sourced DB entry),
    falls back to chapter average.
    """
    if db_mfn_rate is not None and db_mfn_rate > 0:
        return float(db_mfn_rate)
    chapter = hts_code.replace(".", "").replace(" ", "")[:2]
    return US_MFN_CHAPTER.get(chapter, 3.5)


def calculate_us_import(
    hts_code: str,
    origin_country: str,
    cif_value: float,
    db_mfn_rate: Optional[float] = None,
    usmca_qualifying: bool = True,
) -> dict:
    """
    Calculate stacked US import duty for a shipment.

    Returns a dict with:
      - rates: dict of each program's rate and dollar amount
      - total_duty_rate: effective combined rate
      - total_duty_amount: $ amount
      - total_landed_cost: cif_value + total_duty_amount
      - programs: list of applied programs (for display)
    """
    origin = origin_country.upper()
    chapter = hts_code.replace(".", "").replace(" ", "")[:2]
    programs = []

    # 1. Base MFN rate -------------------------------------------------------
    base_mfn = get_us_mfn_rate(hts_code, db_mfn_rate)

    # FTA / USMCA override
    fta_name = None
    effective_mfn = base_mfn
    if origin in _FTA_ZERO_COUNTRIES and usmca_qualifying:
        fta_name = _FTA_ZERO_COUNTRIES[origin]
        effective_mfn = 0.0
        programs.append({
            "name": f"Base MFN ({fta_name} — 0%)",
            "authority": fta_name,
            "rate": 0.0,
            "savings_vs_mfn": round(base_mfn * cif_value / 100, 2),
            "amount": 0.0,
            "note": f"Qualifies for {fta_name} preferential rate",
        })
    else:
        mfn_amount = round(cif_value * effective_mfn / 100, 2)
        programs.append({
            "name": f"Base MFN Rate",
            "authority": "USITC HTS",
            "rate": effective_mfn,
            "amount": mfn_amount,
        })

    total_rate = effective_mfn

    # 2. Section 232 ---------------------------------------------------------
    s232_rate = _SECTION_232.get(chapter, 0.0)
    if s232_rate > 0:
        s232_amount = round(cif_value * s232_rate / 100, 2)
        programs.append({
            "name": "Section 232 National Security",
            "authority": "Commerce Dept",
            "rate": s232_rate,
            "amount": s232_amount,
            "note": "Steel / aluminum / auto national security tariff",
        })
        total_rate += s232_rate

    # 3. Section 301 (China only) -------------------------------------------
    s301_rate = 0.0
    if origin == "CN":
        s301_rate = _section_301_rate(chapter)
        s301_amount = round(cif_value * s301_rate / 100, 2)
        list_name = "List 4A" if s301_rate == 7.5 else "List 1-3"
        programs.append({
            "name": f"Section 301 ({list_name})",
            "authority": "USTR",
            "rate": s301_rate,
            "amount": s301_amount,
            "note": "Unfair trade practice tariff on Chinese goods",
        })
        total_rate += s301_rate

    # 4. IEEPA reciprocal ---------------------------------------------------
    ieepa_rate = 0.0
    if origin == "CN":
        ieepa_rate = _IEEPA_RATES.get("CN", 0.0)
        ieepa_amount = round(cif_value * ieepa_rate / 100, 2)
        programs.append({
            "name": "IEEPA Reciprocal Tariff",
            "authority": "Executive Order",
            "rate": ieepa_rate,
            "amount": ieepa_amount,
            "note": "Emergency economic powers — reciprocal trade balance",
        })
        total_rate += ieepa_rate
    elif origin in ("MX", "CA") and not (usmca_qualifying and origin in _FTA_ZERO_COUNTRIES):
        ieepa_rate = _IEEPA_RATES.get(origin, 0.0)
        if ieepa_rate > 0:
            ieepa_amount = round(cif_value * ieepa_rate / 100, 2)
            programs.append({
                "name": "IEEPA Tariff (Non-USMCA)",
                "authority": "Executive Order",
                "rate": ieepa_rate,
                "amount": ieepa_amount,
                "note": "Non-qualifying goods from MX/CA subject to IEEPA",
            })
            total_rate += ieepa_rate

    # 5. Totals -------------------------------------------------------------
    total_duty = round(cif_value * total_rate / 100, 2)
    total_landed = round(cif_value + total_duty, 2)

    return {
        "hts_code": hts_code,
        "origin_country": origin,
        "cif_value": cif_value,
        "programs": programs,
        "rates": {
            "base_mfn": base_mfn,
            "fta_applied": fta_name,
            "section_232": s232_rate,
            "section_301": s301_rate,
            "ieepa": ieepa_rate,
            "total_effective": round(total_rate, 2),
        },
        "calculation": {
            "cif_value": cif_value,
            "total_duty": total_duty,
            "total_landed_cost": total_landed,
            "effective_rate": round(total_rate, 2),
            "currency": "USD",
        },
        "fta_name": fta_name,
        "usmca_qualifying": usmca_qualifying if origin in ("MX", "CA") else None,
    }


# Country metadata for the frontend selector
ORIGIN_COUNTRIES = [
    {"code": "CN", "name": "China",            "flag": "🇨🇳", "note": "Section 301 + IEEPA"},
    {"code": "MX", "name": "Mexico",           "flag": "🇲🇽", "note": "0% (USMCA qualifying)"},
    {"code": "CA", "name": "Canada",           "flag": "🇨🇦", "note": "0% (USMCA qualifying)"},
    {"code": "KR", "name": "South Korea",      "flag": "🇰🇷", "note": "0% (KORUS FTA)"},
    {"code": "VN", "name": "Vietnam",          "flag": "🇻🇳", "note": "MFN only (~8-12%)"},
    {"code": "IN", "name": "India",            "flag": "🇮🇳", "note": "MFN only (~8%)"},
    {"code": "TH", "name": "Thailand",         "flag": "🇹🇭", "note": "MFN only (~8-12%)"},
    {"code": "MY", "name": "Malaysia",         "flag": "🇲🇾", "note": "MFN only (~8-12%)"},
    {"code": "ID", "name": "Indonesia",        "flag": "🇮🇩", "note": "MFN only (~8-10%)"},
    {"code": "JP", "name": "Japan",            "flag": "🇯🇵", "note": "MFN only (~2-3%)"},
    {"code": "TW", "name": "Taiwan",           "flag": "🇹🇼", "note": "MFN only (~3-4%)"},
    {"code": "EU", "name": "European Union",   "flag": "🇪🇺", "note": "MFN only (~2-4%)"},
    {"code": "BD", "name": "Bangladesh",       "flag": "🇧🇩", "note": "MFN only (~12-25%)"},
]
