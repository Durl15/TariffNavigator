from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from io import BytesIO

# Try to import WeasyPrint, fall back to simple generator if not available
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    # WeasyPrint not available, will use simple generator as fallback


def generate_tariff_pdf(calculation_data: Dict[str, Any]) -> bytes:
    """
    Generate a professional PDF report for tariff calculation.

    Args:
        calculation_data: Dictionary containing calculation details
            Required keys: hs_code, country, description, rates, calculation

    Returns:
        PDF file as bytes

    Raises:
        ValueError: If required data is missing
    """
    # Use simple generator if WeasyPrint is not available
    if not WEASYPRINT_AVAILABLE:
        from app.services.pdf_generator_simple import generate_tariff_pdf_simple
        return generate_tariff_pdf_simple(calculation_data)

    # Validate required fields
    required_fields = ['hs_code', 'country', 'description']
    for field in required_fields:
        if field not in calculation_data:
            raise ValueError(f"Missing required field: {field}")

    # Setup Jinja2 template environment
    template_dir = Path(__file__).parent.parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template('tariff_report.html')

    # Add generated date and format data
    report_data = {
        **calculation_data,
        'generated_date': datetime.now().strftime('%B %d, %Y'),
        'generated_time': datetime.now().strftime('%I:%M %p'),
    }

    # Render HTML template
    html_content = template.render(**report_data)

    # Convert HTML to PDF using WeasyPrint
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()

    return pdf_bytes


def generate_tariff_pdf_from_string(html_content: str) -> bytes:
    """
    Generate PDF from raw HTML string (alternative method).

    Args:
        html_content: HTML string to convert

    Returns:
        PDF file as bytes
    """
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    return pdf_bytes
