"""
Export API Endpoints
Provides PDF and CSV export functionality for tariff calculations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from io import BytesIO

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.calculation import Calculation
from app.services.pdf_generator import generate_tariff_pdf
from app.services.csv_generator import generate_calculations_csv


router = APIRouter()


# Request Models
class PDFExportRequest(BaseModel):
    """Request model for PDF export"""
    hs_code: str = Field(..., description="HS code for the calculation")
    country: str = Field(..., description="Country code (CN, EU, US)")
    description: str = Field(..., description="Product description")
    rates: dict = Field(..., description="Tariff rates (mfn, vat, consumption)")
    calculation: dict = Field(..., description="Cost calculation breakdown")
    origin_country: Optional[str] = Field(None, description="Origin country")
    destination_country: Optional[str] = Field(None, description="Destination country")
    original_currency: Optional[str] = Field(None, description="Original currency code")
    exchange_rate: Optional[float] = Field(None, description="Exchange rate used")
    converted_calculation: Optional[dict] = Field(None, description="Converted calculation in target currency")


class CSVExportRequest(BaseModel):
    """Request model for CSV export"""
    calculation_ids: Optional[List[str]] = Field(None, description="Specific calculation IDs to export")
    date_from: Optional[datetime] = Field(None, description="Filter calculations from this date")
    date_to: Optional[datetime] = Field(None, description="Filter calculations to this date")
    hs_code: Optional[str] = Field(None, description="Filter by specific HS code")
    limit: int = Field(default=1000, ge=1, le=10000, description="Maximum number of records")


@router.post("/pdf")
async def export_pdf(
    request: PDFExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate and download a PDF report for a tariff calculation.
    Requires authentication.
    """
    try:
        # Convert request to dictionary for PDF generator
        calculation_data = request.model_dump()

        # Generate PDF
        pdf_bytes = generate_tariff_pdf(calculation_data)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tariff_report_{request.hs_code}_{timestamp}.pdf"

        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid calculation data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.post("/csv")
async def export_csv(
    request: CSVExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and download a CSV file of calculations.
    Requires authentication. Exports only the current user's calculations.
    """
    try:
        # Build query for user's calculations
        query = select(Calculation).where(Calculation.user_id == current_user.id)

        # Apply filters
        if request.calculation_ids:
            query = query.where(Calculation.id.in_(request.calculation_ids))

        if request.date_from:
            query = query.where(Calculation.created_at >= request.date_from)

        if request.date_to:
            query = query.where(Calculation.created_at <= request.date_to)

        if request.hs_code:
            query = query.where(Calculation.hs_code == request.hs_code)

        # Apply limit and ordering
        query = query.order_by(Calculation.created_at.desc()).limit(request.limit)

        # Execute query
        result = await db.execute(query)
        calculations = result.scalars().all()

        if not calculations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No calculations found matching the criteria"
            )

        # Convert to dictionaries
        calc_dicts = []
        for calc in calculations:
            calc_dict = {
                'id': str(calc.id),
                'created_at': calc.created_at,
                'hs_code': calc.hs_code,
                'description': calc.product_description or '',
                'origin_country': calc.origin_country or '',
                'destination_country': calc.destination_country or '',
                'cif_value': float(calc.cif_value) if calc.cif_value else 0.0,
                'currency': calc.currency or 'USD',
                'customs_duty': float(calc.customs_duty) if calc.customs_duty else 0.0,
                'vat_amount': float(calc.vat_amount) if calc.vat_amount else 0.0,
                'total_cost': float(calc.total_cost) if calc.total_cost else 0.0,
                'fta_eligible': calc.fta_eligible or False,
                'fta_savings': float(calc.fta_savings) if calc.fta_savings else 0.0
            }
            calc_dicts.append(calc_dict)

        # Generate CSV
        csv_content = generate_calculations_csv(calc_dicts)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"calculations_export_{timestamp}.csv"

        # Return as streaming response
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CSV: {str(e)}"
        )


@router.get("/test-pdf")
async def test_pdf_generation():
    """
    Test endpoint to verify PDF generation is working.
    Returns a sample PDF report.
    """
    # Sample calculation data
    sample_data = {
        "hs_code": "8517.12.00",
        "country": "CN",
        "description": "Mobile phones for cellular networks",
        "rates": {
            "mfn": 0.0,
            "vat": 13.0,
            "consumption": 0.0
        },
        "calculation": {
            "cif_value": 10000.00,
            "customs_duty": 0.00,
            "vat": 1300.00,
            "consumption_tax": 0.00,
            "total_cost": 11300.00,
            "currency": "USD"
        }
    }

    try:
        pdf_bytes = generate_tariff_pdf(sample_data)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=test_report.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation test failed: {str(e)}"
        )
