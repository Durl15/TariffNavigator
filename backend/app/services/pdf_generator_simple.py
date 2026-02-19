"""
Simple PDF generator using reportlab (no system dependencies required).
Fallback for Windows/environments where WeasyPrint can't be installed.
"""
from typing import Dict, Any
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_tariff_pdf_simple(calculation_data: Dict[str, Any]) -> bytes:
    """
    Generate a simple PDF report using ReportLab.

    Args:
        calculation_data: Dictionary containing calculation details

    Returns:
        PDF file as bytes
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is not installed. Install with: pip install reportlab")

    # Validate required fields
    required_fields = ['hs_code', 'country', 'description']
    for field in required_fields:
        if field not in calculation_data:
            raise ValueError(f"Missing required field: {field}")

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()

    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
    )

    # Add title
    elements.append(Paragraph("Tariff Calculation Report", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Report metadata
    generated_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    elements.append(Paragraph(f"<b>Generated:</b> {generated_date}", styles['Normal']))
    elements.append(Paragraph(f"<b>Country:</b> {calculation_data['country']}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # HS Code section
    elements.append(Paragraph("Product Classification", styles['Heading2']))
    elements.append(Paragraph(f"<b>HS Code:</b> {calculation_data['hs_code']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Description:</b> {calculation_data['description']}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Tariff Rates section
    if 'rates' in calculation_data and calculation_data['rates']:
        elements.append(Paragraph("Applicable Tariff Rates", styles['Heading2']))

        rates_data = [['Rate Type', 'Rate (%)']]
        rates = calculation_data['rates']

        if 'mfn' in rates:
            rates_data.append(['MFN (Most Favored Nation)', f"{rates['mfn']:.2f}%"])
        if 'vat' in rates and rates.get('vat', 0) > 0:
            rates_data.append(['VAT (Value Added Tax)', f"{rates['vat']:.2f}%"])
        if 'consumption' in rates and rates.get('consumption', 0) > 0:
            rates_data.append(['Consumption Tax', f"{rates['consumption']:.2f}%"])

        rates_table = Table(rates_data, colWidths=[4*inch, 2*inch])
        rates_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(rates_table)
        elements.append(Spacer(1, 0.3*inch))

    # Cost Calculation section
    if 'calculation' in calculation_data and calculation_data['calculation']:
        elements.append(Paragraph("Cost Calculation", styles['Heading2']))

        calc = calculation_data['calculation']
        currency = calc.get('currency', 'USD')

        cost_data = [['Item', 'Amount']]
        cost_data.append(['CIF Value', f"{calc.get('cif_value', 0):.2f} {currency}"])

        if 'customs_duty' in calc:
            cost_data.append(['Customs Duty', f"{calc.get('customs_duty', 0):.2f} {currency}"])
        if 'vat' in calc and calc.get('vat', 0) > 0:
            cost_data.append(['VAT', f"{calc.get('vat', 0):.2f} {currency}"])
        if 'consumption_tax' in calc and calc.get('consumption_tax', 0) > 0:
            cost_data.append(['Consumption Tax', f"{calc.get('consumption_tax', 0):.2f} {currency}"])

        cost_data.append(['TOTAL LANDED COST', f"{calc.get('total_cost', 0):.2f} {currency}"])

        cost_table = Table(cost_data, colWidths=[4*inch, 2*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(cost_table)
        elements.append(Spacer(1, 0.3*inch))

    # Disclaimer
    elements.append(Spacer(1, 0.5*inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        leading=12,
    )
    disclaimer_text = """
    <b>Disclaimer:</b> This calculation is for reference purposes only.
    Actual duties and taxes may vary based on specific circumstances, product classification,
    trade agreements, and regulatory changes. Please consult with a licensed customs broker
    or trade compliance professional for official guidance.
    """
    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    # Build PDF
    doc.build(elements)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
