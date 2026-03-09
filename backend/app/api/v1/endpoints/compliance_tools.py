"""
Compliance Tools - Drawback Finder, USMCA Checker, Supply Chain Risk Scanner, HTS Audit
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import openai
from openai import AsyncOpenAI

from app.core.config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_TRADE = "You are a U.S. Customs and trade compliance expert advising small business importers. Be concise, specific, and use plain English."


# ============================================================================
# DUTY DRAWBACK FINDER
# ============================================================================

class DrawbackRequest(BaseModel):
    hts_code: str
    country_of_origin: str
    import_date: Optional[str] = None
    duty_paid: float
    product_description: Optional[str] = None
    plans_to_export: bool = False
    plans_to_manufacture: bool = False


class DrawbackResponse(BaseModel):
    eligible: bool
    drawback_type: Optional[str]
    potential_refund: float
    refund_percent: float
    deadline_description: str
    form_required: str
    steps: List[str]
    ai_analysis: str
    annual_unclaimed_estimate: Optional[float] = None


@router.post("/drawback", response_model=DrawbackResponse)
async def find_drawback_eligibility(request: DrawbackRequest):
    """
    Determine if duty drawback refund is available. Up to 99% of duties paid
    can be recovered if goods are re-exported or used in US manufacturing.
    """
    try:
        eligible = True
        drawback_type = "unused_merchandise"
        refund_pct = 0.99
        form = "CBP Form 7553 (Notice of Intent to Export)"
        steps = [
            "File CBP Form 7553 BEFORE exporting goods",
            "Keep proof of import (entry summary, duty payment receipt)",
            "Export within 3 years of original import date",
            "File drawback claim within 5 years of import",
            "Consider hiring a licensed customs broker for first claim"
        ]

        if request.plans_to_manufacture:
            drawback_type = "manufacturing_drawback"
            form = "CBP Form 7551 (Drawback Entry)"
            steps = [
                "Document which imported materials went into manufactured product",
                "File manufacturing drawback claim within 5 years",
                "Maintain production records matching import to export",
                "CBP Form 7551 required for each claim"
            ]
        elif not request.plans_to_export and not request.plans_to_manufacture:
            eligible = False
            drawback_type = None
            refund_pct = 0.0
            form = "N/A"
            steps = ["Drawback requires either re-export or use in US manufacturing"]

        refund_amount = request.duty_paid * refund_pct

        prompt = f"""Product: {request.product_description or request.hts_code}
Country of origin: {request.country_of_origin}
Duties paid: ${request.duty_paid:,.0f}
Plans to export: {request.plans_to_export}
Plans to manufacture with imported goods: {request.plans_to_manufacture}

Explain in 2-3 sentences:
1. Whether duty drawback applies and which type
2. The biggest practical gotcha or deadline to watch
3. One specific action to take this week"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_TRADE},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )

        return DrawbackResponse(
            eligible=eligible,
            drawback_type=drawback_type,
            potential_refund=round(refund_amount, 2),
            refund_percent=refund_pct * 100,
            deadline_description="5 years from import date to file; 3 years to export goods",
            form_required=form,
            steps=steps,
            ai_analysis=response.choices[0].message.content,
            annual_unclaimed_estimate=round(request.duty_paid * refund_pct * 12, 2) if eligible else None
        )

    except openai.APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drawback analysis error: {str(e)}")


# ============================================================================
# USMCA QUALIFICATION CHECKER
# ============================================================================

class UsmcaRequest(BaseModel):
    hts_code: str
    product_description: str
    origin_country: str  # MX or CA
    us_components_percent: Optional[float] = None
    mexico_canada_labor_percent: Optional[float] = None
    china_components_percent: Optional[float] = None
    annual_import_value: Optional[float] = None


class UsmcaResponse(BaseModel):
    origin_country: str
    usmca_eligible: bool
    confidence: str  # high | medium | low
    reason: str
    missing_requirements: List[str]
    required_docs: List[str]
    savings_if_qualified: Optional[float]
    standard_rate_estimate: float
    ai_analysis: str


@router.post("/usmca-check", response_model=UsmcaResponse)
async def check_usmca_eligibility(request: UsmcaRequest):
    """
    Check if product qualifies for USMCA 0% duty rate.
    Identifies missing documentation and calculates savings opportunity.
    """
    try:
        if request.origin_country.upper() not in ["MX", "CA", "US"]:
            raise HTTPException(status_code=400, detail="USMCA applies only to US, Mexico, and Canada origins")

        china_pct = request.china_components_percent or 0
        us_pct = request.us_components_percent or 0
        mx_ca_pct = request.mexico_canada_labor_percent or 0

        # Basic RVC check (USMCA requires 75% North American content for most goods)
        north_american_pct = us_pct + mx_ca_pct
        usmca_eligible = north_american_pct >= 75 and china_pct < 25

        if not request.us_components_percent and not request.mexico_canada_labor_percent:
            confidence = "low"
            usmca_eligible = True  # assume eligible until proven otherwise
        elif usmca_eligible:
            confidence = "high"
        else:
            confidence = "medium"

        missing = []
        if china_pct >= 25:
            missing.append(f"Chinese components ({china_pct:.0f}%) exceed 25% threshold — fails RVC test")
        if north_american_pct < 75 and (us_pct or mx_ca_pct):
            missing.append(f"North American content ({north_american_pct:.0f}%) below 75% USMCA threshold")
        if not missing:
            missing.append("Obtain signed Certificate of Origin from manufacturer") if usmca_eligible else None

        required_docs = [
            "USMCA Certificate of Origin (from supplier/manufacturer)",
            "Bill of Materials showing component origins",
            "Regional Value Content (RVC) calculation worksheet",
            "Tariff Shift documentation (if applicable)",
        ]

        # Estimate savings
        hts_prefix = request.hts_code[:4]
        est_standard_rate = 0.035  # default US MFN
        if hts_prefix in ["8703"]:
            est_standard_rate = 0.025
        elif hts_prefix in ["6402", "6403", "6404"]:
            est_standard_rate = 0.20

        savings = None
        if request.annual_import_value and usmca_eligible:
            savings = round(request.annual_import_value * est_standard_rate, 2)

        prompt = f"""Product: {request.product_description}
HTS: {request.hts_code}, Origin: {request.origin_country}
North American content: {north_american_pct:.0f}%, Chinese components: {china_pct:.0f}%
USMCA eligible estimate: {usmca_eligible}, Confidence: {confidence}

In 2-3 sentences: explain what the importer needs to do RIGHT NOW to either confirm USMCA eligibility
or fix the qualification gap. Be specific about the most important document to obtain."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_TRADE},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )

        return UsmcaResponse(
            origin_country=request.origin_country.upper(),
            usmca_eligible=usmca_eligible,
            confidence=confidence,
            reason="Based on provided component origins and Regional Value Content analysis",
            missing_requirements=missing,
            required_docs=required_docs,
            savings_if_qualified=savings,
            standard_rate_estimate=round(est_standard_rate * 100, 2),
            ai_analysis=response.choices[0].message.content
        )

    except openai.APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"USMCA check error: {str(e)}")


# ============================================================================
# SUPPLY CHAIN RISK SCANNER
# ============================================================================

class SupplyChainRequest(BaseModel):
    supplier_country: str
    hts_code: str
    product_description: Optional[str] = None
    known_component_origins: Optional[List[str]] = []
    annual_import_value: Optional[float] = None


class RiskItem(BaseModel):
    risk_type: str
    severity: str  # high | medium | low
    description: str
    mitigation: str


class SupplyChainResponse(BaseModel):
    overall_risk: str
    transshipment_risk: str
    section_301_exposure: bool
    ad_cvd_risk: bool
    estimated_penalty_exposure: Optional[float]
    risks: List[RiskItem]
    recommended_docs: List[str]
    ai_analysis: str


@router.post("/supply-chain-scan", response_model=SupplyChainResponse)
async def scan_supply_chain(request: SupplyChainRequest):
    """
    Scan supply chain for transshipment risks, Section 301 exposure,
    and AD/CVD liability based on component origins.
    """
    try:
        component_origins = [c.upper() for c in (request.known_component_origins or [])]
        supplier = request.supplier_country.upper()

        has_chinese_components = "CN" in component_origins
        is_chinese_supplier = supplier == "CN"
        transshipment_countries = ["VN", "TH", "MY", "ID", "PH", "BD", "KH"]
        is_transshipment_risk = supplier in transshipment_countries and has_chinese_components

        risks = []

        if is_chinese_supplier:
            risks.append(RiskItem(
                risk_type="Section 301 Tariffs",
                severity="high",
                description="Direct China sourcing triggers 25%+ Section 301 tariffs plus IEEPA reciprocal rates.",
                mitigation="Get accurate country-of-origin ruling from CBP before importing."
            ))

        if is_transshipment_risk:
            risks.append(RiskItem(
                risk_type="Transshipment / Country of Origin Fraud",
                severity="high",
                description=f"Goods assembled in {supplier} with Chinese components may still be classified as Chinese-origin under CBP 'substantial transformation' test.",
                mitigation="Obtain a binding ruling from CBP on country of origin. Require supplier to provide bill of materials showing transformation steps."
            ))

        if has_chinese_components and not is_chinese_supplier:
            risks.append(RiskItem(
                risk_type="Tier-2 Chinese Component Exposure",
                severity="medium",
                description="Chinese-origin components in your supply chain may trigger Section 301 if goods don't meet substantial transformation test.",
                mitigation="Document the manufacturing process proving substantial transformation occurs in the supplier's country."
            ))

        ad_cvd_codes = ["7210", "7211", "7212", "7213", "7214", "7215", "7216", "7217", "7218", "7219"]
        ad_cvd_risk = request.hts_code[:4] in ad_cvd_codes or (is_chinese_supplier and request.hts_code[:2] == "72")

        if ad_cvd_risk:
            risks.append(RiskItem(
                risk_type="Antidumping / Countervailing Duties",
                severity="high",
                description="Steel and aluminum products from certain countries face AD/CVD rates that can reach 200%+.",
                mitigation="Check USITC AD/CVD orders database before importing. Request a scope ruling if uncertain."
            ))

        if not risks:
            risks.append(RiskItem(
                risk_type="Standard Compliance",
                severity="low",
                description="No elevated risk factors detected based on provided information.",
                mitigation="Maintain standard import documentation: commercial invoice, packing list, bill of lading."
            ))

        overall = "high" if any(r.severity == "high" for r in risks) else "medium" if any(r.severity == "medium" for r in risks) else "low"
        transshipment = "high" if is_transshipment_risk else ("medium" if has_chinese_components else "low")

        penalty_exposure = None
        if request.annual_import_value and overall == "high":
            penalty_exposure = round(request.annual_import_value * 0.20, 2)

        recommended_docs = [
            "Commercial invoice with detailed description of goods",
            "Manufacturer's affidavit of origin",
            "Bill of materials showing component origins and percentages",
            "Proof of manufacturing process (photos, production records)",
        ]
        if is_transshipment_risk:
            recommended_docs.insert(0, "CBP Binding Ruling Request (Form 3353) — CRITICAL")

        prompt = f"""Supplier country: {request.supplier_country}
HTS code: {request.hts_code}
Product: {request.product_description or 'not specified'}
Component origins: {', '.join(component_origins) if component_origins else 'unknown'}
Risk level: {overall}, Transshipment risk: {transshipment}

In 2-3 sentences: what is the single most important action this importer should take to protect themselves from CBP penalties?
Be specific about timing and consequences of inaction."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_TRADE},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )

        return SupplyChainResponse(
            overall_risk=overall,
            transshipment_risk=transshipment,
            section_301_exposure=has_chinese_components or is_chinese_supplier,
            ad_cvd_risk=ad_cvd_risk,
            estimated_penalty_exposure=penalty_exposure,
            risks=risks,
            recommended_docs=recommended_docs,
            ai_analysis=response.choices[0].message.content
        )

    except openai.APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supply chain scan error: {str(e)}")


# ============================================================================
# HTS AUDIT — OVERPAYMENT DETECTOR
# ============================================================================

class HTSAuditRequest(BaseModel):
    product_description: str
    current_hts_code: str
    supplier_provided: bool = True
    annual_import_value: Optional[float] = None
    country_of_origin: str = "CN"


class AlternativeCode(BaseModel):
    code: str
    description: str
    estimated_rate: float
    annual_savings: Optional[float]


class HTSAuditResponse(BaseModel):
    current_code: str
    current_estimated_rate: float
    misclassification_risk: str  # high | medium | low
    overpayment_likely: bool
    alternative_codes: List[AlternativeCode]
    annual_savings_estimate: Optional[float]
    ai_recommended_code: Optional[str]
    ai_recommended_rate: Optional[float]
    supplier_bias_warning: bool
    ai_analysis: str


@router.post("/hts-audit", response_model=HTSAuditResponse)
async def audit_hts_classification(request: HTSAuditRequest):
    """
    AI-powered HTS code audit. Detects misclassifications that cause overpayment
    or penalty risk. Especially useful when supplier provided the HTS code.
    """
    try:
        prompt = f"""Product: "{request.product_description}"
Current HTS code: {request.current_hts_code}
Country of origin: {request.country_of_origin}
Provided by supplier: {request.supplier_provided}

You are a licensed customs broker. Analyze this classification:
1. Is {request.current_hts_code} correct for this product? (yes/probably/unlikely)
2. What is the most likely CORRECT 6-digit HTS code prefix?
3. What is a more favorable alternative HTS code if any?
4. Estimated US MFN duty rate for the correct code (as percentage)?
5. Is there overpayment risk? (yes/no)

Respond in this exact JSON format:
{{
  "classification_correct": "yes|probably|unlikely",
  "recommended_code": "XXXX.XX",
  "recommended_rate": 0.00,
  "alternative_code": "XXXX.XX",
  "alternative_rate": 0.00,
  "alternative_description": "brief description",
  "overpayment_risk": "yes|no",
  "misclassification_risk": "high|medium|low",
  "analysis": "2 sentence explanation"
}}"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a licensed U.S. customs broker specializing in HTS classification. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=400,
            response_format={"type": "json_object"}
        )

        import json
        ai_data = json.loads(response.choices[0].message.content)

        rec_rate = float(ai_data.get("recommended_rate", 0.035))
        alt_rate = float(ai_data.get("alternative_rate", 0.035))
        overpayment = ai_data.get("overpayment_risk", "no") == "yes"
        risk = ai_data.get("misclassification_risk", "medium")

        alternatives = []
        if ai_data.get("alternative_code") and ai_data["alternative_code"] != request.current_hts_code:
            savings = None
            if request.annual_import_value:
                # Simplified: current rate assumed from section 301 + MFN for CN
                current_est = 0.25 if request.country_of_origin.upper() == "CN" else 0.035
                savings = round((current_est - alt_rate) * request.annual_import_value, 2)
                savings = max(0, savings)

            alternatives.append(AlternativeCode(
                code=ai_data["alternative_code"],
                description=ai_data.get("alternative_description", "Alternative classification"),
                estimated_rate=alt_rate * 100,
                annual_savings=savings
            ))

        annual_savings = alternatives[0].annual_savings if alternatives else None

        return HTSAuditResponse(
            current_code=request.current_hts_code,
            current_estimated_rate=rec_rate * 100,
            misclassification_risk=risk,
            overpayment_likely=overpayment,
            alternative_codes=alternatives,
            annual_savings_estimate=annual_savings,
            ai_recommended_code=ai_data.get("recommended_code"),
            ai_recommended_rate=rec_rate * 100,
            supplier_bias_warning=request.supplier_provided,
            ai_analysis=ai_data.get("analysis", "")
        )

    except openai.APIError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTS audit error: {str(e)}")
