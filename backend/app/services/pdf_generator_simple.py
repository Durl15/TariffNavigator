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


def _branded_doc(buffer, title: str):
    """Create a branded SimpleDocTemplate with consistent margins."""
    return SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        title=title,
        author="TariffNavigator — DJ AI Business Consultant",
    )


def _styles():
    base = getSampleStyleSheet()
    navy = colors.HexColor('#1E3A5F')
    teal = colors.HexColor('#0D9488')
    gold = colors.HexColor('#D4A843')

    h1 = ParagraphStyle('TN_H1', parent=base['Heading1'], fontSize=20, textColor=navy, spaceAfter=4)
    h2 = ParagraphStyle('TN_H2', parent=base['Heading2'], fontSize=13, textColor=navy, spaceAfter=4, spaceBefore=12)
    body = ParagraphStyle('TN_Body', parent=base['Normal'], fontSize=10, leading=14)
    small = ParagraphStyle('TN_Small', parent=base['Normal'], fontSize=8, textColor=colors.grey, leading=11)
    tag = ParagraphStyle('TN_Tag', parent=base['Normal'], fontSize=9, textColor=teal, spaceAfter=16)
    return h1, h2, body, small, tag, navy, teal, gold


def _header_table(title: str, subtitle: str, report_type: str):
    """Company + report type header."""
    from reportlab.lib import colors as c
    navy = c.HexColor('#1E3A5F')
    teal = c.HexColor('#0D9488')
    generated = datetime.now().strftime('%B %d, %Y')
    styles = getSampleStyleSheet()

    left = Paragraph(
        f'<font size="16" color="#1E3A5F"><b>{title}</b></font><br/>'
        f'<font size="9" color="#666666">{subtitle}</font>',
        styles['Normal']
    )
    right = Paragraph(
        f'<font size="8" color="#999999">TariffNavigator<br/>DJ AI Business Consultant<br/>Generated {generated}</font>',
        ParagraphStyle('right', parent=styles['Normal'], alignment=2)
    )
    t = Table([[left, right]], colWidths=[4.2 * inch, 2.5 * inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, teal),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    return t


def _section(title: str, rows: list, col_widths=None):
    """Render a labelled two-column key-value table section."""
    from reportlab.lib import colors as c
    if col_widths is None:
        col_widths = [2.4 * inch, 4.3 * inch]
    data = [[title, '']] + rows
    t = Table(data, colWidths=col_widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), c.HexColor('#1E3A5F')),
        ('TEXTCOLOR', (0, 0), (-1, 0), c.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('BACKGROUND', (0, 1), (-1, -1), c.HexColor('#F8FAFC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c.HexColor('#F8FAFC'), c.white]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 1), (0, -1), c.HexColor('#374151')),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 1), (-1, -1), 0.5, c.HexColor('#E5E7EB')),
        ('LINEBELOW', (0, 0), (-1, 0), 0, c.white),
    ]))
    return t


def generate_compliance_report_pdf(report_type: str, title: str, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> bytes:
    """
    Generate a branded compliance report PDF for any tool output.
    report_type: drawback | supply_chain | hts_audit | usmca | cashflow | sourcing | scenario
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is not installed.")

    from reportlab.lib import colors as c
    meta = metadata or {}
    buffer = BytesIO()
    subtitle_map = {
        "drawback": "Duty Drawback Eligibility Report",
        "supply_chain": "Supply Chain Risk Assessment",
        "hts_audit": "HTS Classification Audit Report",
        "usmca": "USMCA Qualification Analysis",
        "cashflow": "Import Cash Flow Forecast",
        "sourcing": "Alternative Sourcing Analysis",
        "scenario": "Tariff Scenario Impact Report",
    }
    subtitle = subtitle_map.get(report_type, "Compliance Analysis Report")
    doc = _branded_doc(buffer, title)
    h1, h2, body, small, tag, navy, teal, gold = _styles()
    sp = lambda n=0.2: Spacer(1, n * inch)
    elements = [_header_table(title, subtitle, report_type), sp(0.3)]

    # ── REPORT-TYPE SPECIFIC SECTIONS ──────────────────────────────────────

    if report_type == "drawback":
        eligible = data.get("eligible", False)
        status_color = '#0D9488' if eligible else '#C0392B'
        status_text = '✓ ELIGIBLE' if eligible else '✗ NOT ELIGIBLE'
        elements.append(Paragraph(
            f'<font color="{status_color}" size="14"><b>Drawback Status: {status_text}</b></font>',
            ParagraphStyle('status', parent=h1, fontSize=14)
        ))
        elements.append(sp(0.15))
        elements.append(_section("Refund Summary", [
            ["Drawback Type", (data.get("drawback_type") or "N/A").replace("_", " ").title()],
            ["Duties Paid", f"${float(meta.get('duty_paid', 0)):,.2f}"],
            ["Potential Refund", f"${data.get('potential_refund', 0):,.2f}  ({data.get('refund_percent', 0):.0f}%)"],
            ["Form Required", data.get("form_required", "N/A")],
            ["Filing Deadline", data.get("deadline_description", "5 years from import date")],
        ]))
        elements.append(sp(0.2))
        if data.get("steps"):
            elements.append(Paragraph("Filing Steps", h2))
            for i, step in enumerate(data["steps"], 1):
                elements.append(Paragraph(f"<b>{i}.</b> {step}", body))
        if data.get("ai_analysis"):
            elements.append(sp(0.2))
            elements.append(_section("AI Analysis", [["", data["ai_analysis"]]]))

    elif report_type == "supply_chain":
        risk_colors = {"high": "#C0392B", "medium": "#D4A843", "low": "#0D9488"}
        overall = data.get("overall_risk", "unknown")
        elements.append(Paragraph(
            f'<font color="{risk_colors.get(overall, "#666")}" size="14"><b>Overall Risk: {overall.upper()}</b></font>',
            ParagraphStyle('risk', parent=h1, fontSize=14)
        ))
        elements.append(sp(0.15))
        exposure_rows = [
            ["Supplier Country", meta.get("supplier_country", "N/A")],
            ["Transshipment Risk", data.get("transshipment_risk", "unknown").upper()],
            ["Section 301 Exposure", "YES" if data.get("section_301_exposure") else "NO"],
            ["AD/CVD Risk", "YES" if data.get("ad_cvd_risk") else "NO"],
        ]
        if data.get("estimated_penalty_exposure"):
            exposure_rows.append(["Est. Penalty Exposure", f"${data['estimated_penalty_exposure']:,.0f}+"])
        elements.append(_section("Risk Exposure Summary", exposure_rows))
        elements.append(sp(0.2))
        if data.get("risks"):
            elements.append(Paragraph("Risk Details", h2))
            for risk in data["risks"]:
                sev = risk.get("severity", "medium")
                elements.append(Paragraph(
                    f'<font color="{risk_colors.get(sev, "#666")}"><b>[{sev.upper()}] {risk["risk_type"]}</b></font>',
                    body
                ))
                elements.append(Paragraph(risk.get("description", ""), body))
                elements.append(Paragraph(f"<b>Action:</b> {risk.get('mitigation', '')}", body))
                elements.append(sp(0.1))
        if data.get("recommended_docs"):
            elements.append(sp(0.1))
            rows = [[f"{i+1}.", doc] for i, doc in enumerate(data["recommended_docs"])]
            elements.append(_section("Required Documentation", rows))
        if data.get("ai_analysis"):
            elements.append(sp(0.2))
            elements.append(_section("AI Recommendation", [["", data["ai_analysis"]]]))

    elif report_type == "hts_audit":
        risk = data.get("misclassification_risk", "medium")
        risk_colors = {"high": "#C0392B", "medium": "#D4A843", "low": "#0D9488"}
        elements.append(_section("Classification Summary", [
            ["Product Description", meta.get("product_description", "N/A")],
            ["Current HTS Code", data.get("current_code", "N/A")],
            ["Current Est. Rate", f"{data.get('current_estimated_rate', 0):.2f}%"],
            ["AI Recommended Code", data.get("ai_recommended_code") or "Same as current"],
            ["AI Recommended Rate", f"{data.get('ai_recommended_rate', 0):.2f}%"],
            ["Misclassification Risk", f'[{risk.upper()}]  {risk}'],
            ["Overpayment Likely", "YES" if data.get("overpayment_likely") else "NO"],
        ]))
        if data.get("alternative_codes"):
            elements.append(sp(0.2))
            rows = []
            for alt in data["alternative_codes"]:
                rows.append([alt["code"], f'{alt["estimated_rate"]:.2f}% — {alt.get("description", "")}'])
                if alt.get("annual_savings") and alt["annual_savings"] > 0:
                    rows.append(["  Est. Annual Savings", f'${alt["annual_savings"]:,.0f}'])
            elements.append(_section("Alternative Classifications", rows))
        if data.get("ai_analysis"):
            elements.append(sp(0.2))
            elements.append(_section("AI Analysis", [["", data["ai_analysis"]]]))
        if data.get("supplier_bias_warning"):
            elements.append(sp(0.15))
            elements.append(Paragraph(
                "<b>⚠ Supplier Bias Warning:</b> This HTS code was provided by your supplier. "
                "Suppliers have no incentive to minimize your import duties. Independent verification recommended.",
                ParagraphStyle('warn', parent=small, textColor=c.HexColor('#B45309'), fontSize=9)
            ))

    elif report_type == "usmca":
        eligible = data.get("usmca_eligible", False)
        status_color = '#0D9488' if eligible else '#C0392B'
        elements.append(Paragraph(
            f'<font color="{status_color}" size="14"><b>USMCA Status: {"LIKELY ELIGIBLE" if eligible else "MAY NOT QUALIFY"}</b></font>',
            ParagraphStyle('status', parent=h1, fontSize=14)
        ))
        elements.append(sp(0.15))
        rows = [
            ["Product", meta.get("product_description", "N/A")],
            ["HTS Code", meta.get("hts_code", "N/A")],
            ["Origin Country", data.get("origin_country", "N/A")],
            ["Confidence", data.get("confidence", "N/A").upper()],
            ["Standard Rate (Est.)", f'{data.get("standard_rate_estimate", 0):.2f}%'],
        ]
        if data.get("savings_if_qualified"):
            rows.append(["Annual Savings if Qualified", f'${data["savings_if_qualified"]:,.0f}'])
        elements.append(_section("Qualification Summary", rows))
        if data.get("missing_requirements") and any(data["missing_requirements"]):
            elements.append(sp(0.2))
            rows = [[f"{i+1}.", r] for i, r in enumerate(data["missing_requirements"]) if r]
            elements.append(_section("Issues to Address", rows))
        if data.get("required_docs"):
            elements.append(sp(0.2))
            rows = [[f"{i+1}.", d] for i, d in enumerate(data["required_docs"])]
            elements.append(_section("Required Documentation", rows))
        if data.get("ai_analysis"):
            elements.append(sp(0.2))
            elements.append(_section("AI Analysis", [["", data["ai_analysis"]]]))

    elif report_type == "cashflow":
        risk = data.get("cash_gap_risk", "medium")
        risk_colors = {"high": "#C0392B", "medium": "#D4A843", "low": "#0D9488"}
        elements.append(_section("Cash Flow Summary", [
            ["Shipment Value", f'${data.get("shipment_value", 0):,.2f}'],
            ["Country of Origin", meta.get("country_of_origin", "N/A")],
            ["Effective Duty Rate", f'{data.get("duty_rate_percent", 0):.2f}%'],
            ["Duty Due at Port", f'${data.get("duty_due_amount", 0):,.2f}'],
            ["Due Date", data.get("due_date", "N/A")],
            ["Estimated Revenue Date", data.get("estimated_revenue_date", "N/A")],
            ["Cash Gap (days)", str(data.get("cash_gap_days", 0))],
            ["Cash Gap (amount)", f'${data.get("cash_gap_amount", 0):,.2f}'],
            ["Risk Level", f'[{risk.upper()}]'],
        ]))
        if data.get("tariff_programs_applied"):
            elements.append(sp(0.2))
            rows = [[f"•", p] for p in data["tariff_programs_applied"]]
            elements.append(_section("Tariff Programs Applied", rows))
        if data.get("financing_options"):
            elements.append(sp(0.2))
            rows = []
            for opt in data["financing_options"]:
                rows.append([opt["name"], f'{opt["typical_cost_percent"]}% cost — {opt["description"]}'])
            elements.append(_section("Financing Options", rows))
        if data.get("ai_recommendation"):
            elements.append(sp(0.2))
            elements.append(_section("AI Recommendation", [["", data["ai_recommendation"]]]))

    elif report_type == "sourcing":
        elements.append(_section("Current Sourcing", [
            ["HTS Code", data.get("hts_code", "N/A")],
            ["Current Country", data.get("current_country", "N/A")],
            ["Effective Rate", f'{data.get("current_rate_percent", 0):.2f}%'],
        ]))
        if data.get("alternatives"):
            elements.append(sp(0.2))
            elements.append(Paragraph("Alternative Countries — Ranked by Savings", h2))
            rows = [["Country", "Rate", "Savings", "Lead Time", "Trade Agreement"]]
            for alt in data["alternatives"][:8]:
                rows.append([
                    alt["country_name"],
                    f'{alt["effective_rate_percent"]:.1f}%',
                    f'-{alt["savings_percent"]:.0f}%' if alt["savings_percent"] > 0 else '—',
                    f'{alt["lead_time_weeks"]}w',
                    alt.get("trade_agreement") or "—",
                ])
            t = Table(rows, colWidths=[1.5*inch, 0.8*inch, 0.9*inch, 0.9*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c.HexColor('#1E3A5F')),
                ('TEXTCOLOR', (0, 0), (-1, 0), c.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c.HexColor('#F8FAFC'), c.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, c.HexColor('#E5E7EB')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
        if data.get("ai_analysis"):
            elements.append(sp(0.2))
            elements.append(_section("AI Sourcing Recommendation", [["", data["ai_analysis"]]]))

    elif report_type == "scenario":
        delta = data.get("total_delta", 0)
        delta_color = '#C0392B' if delta > 0 else '#0D9488'
        direction = "INCREASE" if delta > 0 else "DECREASE"
        elements.append(Paragraph(
            f'<font color="{delta_color}" size="13"><b>Scenario Impact: ${abs(delta):,.0f} {direction} ({abs(data.get("total_delta_pct", 0)):.1f}%)</b></font>',
            ParagraphStyle('impact', parent=h1, fontSize=13)
        ))
        elements.append(sp(0.15))
        elements.append(_section("Scenario Summary", [
            ["Scenario", data.get("scenario_name", "N/A")],
            ["Description", data.get("scenario_description", "")],
            ["Current Annual Tariff", f'${data.get("current_total_tariff", 0):,.2f}'],
            ["Scenario Annual Tariff", f'${data.get("scenario_total_tariff", 0):,.2f}'],
            ["Net Change", f'${delta:+,.2f}  ({data.get("total_delta_pct", 0):+.1f}%)'],
            ["SKUs Worse Off", str(data.get("items_worse", 0))],
            ["SKUs Better Off", str(data.get("items_better", 0))],
        ]))
        if data.get("item_impacts"):
            elements.append(sp(0.2))
            elements.append(Paragraph("Top Impacted Products", h2))
            rows = [["Product", "Country", "Current Rate", "Scenario Rate", "Annual Δ"]]
            for item in data["item_impacts"][:15]:
                rows.append([
                    (item.get("product_name") or item.get("sku", ""))[:28],
                    item.get("country", ""),
                    f'{item.get("current_tariff_rate", 0):.1f}%',
                    f'{item.get("scenario_tariff_rate", 0):.1f}%',
                    f'${item.get("delta", 0):+,.0f}',
                ])
            t = Table(rows, colWidths=[2.3*inch, 0.7*inch, 0.9*inch, 0.9*inch, 1*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c.HexColor('#1E3A5F')),
                ('TEXTCOLOR', (0, 0), (-1, 0), c.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [c.HexColor('#F8FAFC'), c.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, c.HexColor('#E5E7EB')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(t)
        if data.get("ai_executive_summary"):
            elements.append(sp(0.2))
            elements.append(_section("AI Executive Summary", [["", data["ai_executive_summary"]]]))
        if data.get("recommended_actions"):
            elements.append(sp(0.2))
            rows = [[f"{i+1}.", a] for i, a in enumerate(data["recommended_actions"])]
            elements.append(_section("Recommended Actions", rows))

    # ── FOOTER ─────────────────────────────────────────────────────────────
    elements.append(sp(0.4))
    elements.append(Paragraph(
        "This report is for informational purposes only. Consult a licensed customs broker or trade attorney before making import decisions. "
        "Tariff rates change frequently — verify against current CBP schedules.",
        small
    ))
    elements.append(Paragraph(
        "TariffNavigator  •  DJ AI Business Consultant  •  Syracuse, NY  •  Transforming Business, Rising Above the Challenges",
        ParagraphStyle('footer', parent=small, alignment=1, textColor=colors.HexColor('#9CA3AF'))
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


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
