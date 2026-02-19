import csv
from io import StringIO
from typing import List, Dict, Any
from datetime import datetime


def generate_calculations_csv(calculations: List[Dict[str, Any]]) -> str:
    """
    Generate CSV file content from a list of calculations.

    Args:
        calculations: List of calculation dictionaries

    Returns:
        CSV content as string

    Example calculation dict:
        {
            'id': 'uuid',
            'created_at': datetime,
            'hs_code': '8517.12.00',
            'description': 'Mobile phones',
            'origin_country': 'CN',
            'destination_country': 'US',
            'cif_value': 10000.00,
            'currency': 'USD',
            'customs_duty': 0.00,
            'vat_amount': 0.00,
            'total_cost': 10000.00,
            'fta_eligible': False,
            'fta_savings': 0.00
        }
    """
    output = StringIO()

    # Define CSV columns
    fieldnames = [
        'Date',
        'HS Code',
        'Description',
        'Origin',
        'Destination',
        'CIF Value',
        'Currency',
        'Customs Duty',
        'VAT',
        'Total Cost',
        'FTA Eligible',
        'FTA Savings'
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for calc in calculations:
        # Format date
        created_at = calc.get('created_at')
        if isinstance(created_at, datetime):
            date_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(created_at, str):
            date_str = created_at
        else:
            date_str = 'N/A'

        # Write row
        writer.writerow({
            'Date': date_str,
            'HS Code': calc.get('hs_code', ''),
            'Description': calc.get('description', calc.get('product_description', '')),
            'Origin': calc.get('origin_country', ''),
            'Destination': calc.get('destination_country', calc.get('country', '')),
            'CIF Value': f"{calc.get('cif_value', 0):.2f}",
            'Currency': calc.get('currency', 'USD'),
            'Customs Duty': f"{calc.get('customs_duty', 0):.2f}",
            'VAT': f"{calc.get('vat_amount', calc.get('vat', 0)):.2f}",
            'Total Cost': f"{calc.get('total_cost', 0):.2f}",
            'FTA Eligible': 'Yes' if calc.get('fta_eligible', False) else 'No',
            'FTA Savings': f"{calc.get('fta_savings', 0):.2f}"
        })

    csv_content = output.getvalue()
    output.close()

    return csv_content


def generate_audit_logs_csv(logs: List[Dict[str, Any]]) -> str:
    """
    Generate CSV file content from audit logs.

    Args:
        logs: List of audit log dictionaries

    Returns:
        CSV content as string
    """
    output = StringIO()

    fieldnames = [
        'Timestamp',
        'User Email',
        'Action',
        'Resource Type',
        'Resource ID',
        'IP Address',
        'Method',
        'Status Code',
        'Duration (ms)'
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for log in logs:
        created_at = log.get('created_at')
        if isinstance(created_at, datetime):
            timestamp = created_at.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(created_at, str):
            timestamp = created_at
        else:
            timestamp = 'N/A'

        writer.writerow({
            'Timestamp': timestamp,
            'User Email': log.get('user_email', 'N/A'),
            'Action': log.get('action', ''),
            'Resource Type': log.get('resource_type', ''),
            'Resource ID': log.get('resource_id', ''),
            'IP Address': log.get('ip_address', ''),
            'Method': log.get('method', ''),
            'Status Code': log.get('status_code', ''),
            'Duration (ms)': log.get('duration_ms', '')
        })

    csv_content = output.getvalue()
    output.close()

    return csv_content


def generate_comparison_csv(comparison_data: Dict[str, Any]) -> str:
    """
    Generate CSV file content for calculation comparison.
    Uses side-by-side format with calculations as columns.

    Args:
        comparison_data: Comparison response dictionary with 'calculations' and 'metrics'

    Returns:
        CSV content as string with side-by-side comparison layout
    """
    output = StringIO()

    calculations = comparison_data.get('calculations', [])
    metrics = comparison_data.get('metrics', {})

    if not calculations:
        return ""

    # Header row: Metric | Calc 1 | Calc 2 | Calc 3...
    fieldnames = ['Metric'] + [
        f"#{calc['rank']}: {calc.get('name') or 'Calculation ' + str(i+1)}"
        for i, calc in enumerate(calculations)
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    # Helper to build row
    def build_row(metric_name: str, values: List[str]) -> Dict[str, str]:
        row = {'Metric': metric_name}
        for i, calc in enumerate(calculations):
            col_name = f"#{calc['rank']}: {calc.get('name') or 'Calculation ' + str(i+1)}"
            row[col_name] = values[i] if i < len(values) else 'N/A'
        return row

    # Comparison type row
    comparison_type = metrics.get('comparison_type', 'mixed')
    type_display = {
        'same_hs_different_countries': 'Same HS Code, Different Countries',
        'different_hs_same_country': 'Different HS Codes, Same Country',
        'mixed': 'Mixed Comparison'
    }.get(comparison_type, comparison_type)

    writer.writerow(build_row('Comparison Type', [type_display] * len(calculations)))
    writer.writerow(build_row('', [''] * len(calculations)))  # Blank row

    # HS Code
    writer.writerow(build_row(
        'HS Code',
        [calc.get('hs_code', 'N/A') for calc in calculations]
    ))

    # Route
    writer.writerow(build_row(
        'Route',
        [f"{calc.get('origin_country', '')} → {calc.get('destination_country', '')}"
         for calc in calculations]
    ))

    # Product Description
    writer.writerow(build_row(
        'Product',
        [calc.get('product_description', 'N/A') for calc in calculations]
    ))

    writer.writerow(build_row('', [''] * len(calculations)))  # Blank row

    # CIF Value
    writer.writerow(build_row(
        'CIF Value',
        [f"{calc.get('currency', 'USD')} {calc.get('cif_value', 0):,.2f}"
         for calc in calculations]
    ))

    # Customs Duty
    writer.writerow(build_row(
        'Customs Duty',
        [f"{calc.get('currency', 'USD')} {calc.get('customs_duty', 0):,.2f}"
         if calc.get('customs_duty') is not None else 'N/A'
         for calc in calculations]
    ))

    # VAT
    writer.writerow(build_row(
        'VAT',
        [f"{calc.get('currency', 'USD')} {calc.get('vat_amount', 0):,.2f}"
         if calc.get('vat_amount') is not None else 'N/A'
         for calc in calculations]
    ))

    # Total Cost (highlighted)
    writer.writerow(build_row(
        'TOTAL COST',
        [f"{calc.get('currency', 'USD')} {calc.get('total_cost', 0):,.2f}"
         for calc in calculations]
    ))

    writer.writerow(build_row('', [''] * len(calculations)))  # Blank row

    # Rank
    writer.writerow(build_row(
        'Rank',
        [f"#{calc.get('rank', 0)}" +
         (' (Best)' if calc.get('is_best') else ' (Worst)' if calc.get('is_worst') else '')
         for calc in calculations]
    ))

    # vs Average
    writer.writerow(build_row(
        'vs Average',
        [f"{calc.get('cost_vs_average_percent', 0):+.1f}%"
         for calc in calculations]
    ))

    # FTA Eligible
    writer.writerow(build_row(
        'FTA Eligible',
        ['Yes' if calc.get('fta_eligible') else 'No'
         for calc in calculations]
    ))

    # FTA Savings
    writer.writerow(build_row(
        'FTA Savings',
        [f"{calc.get('currency', 'USD')} {calc.get('fta_savings', 0):,.2f}"
         if calc.get('fta_savings') else 'N/A'
         for calc in calculations]
    ))

    writer.writerow(build_row('', [''] * len(calculations)))  # Blank row

    # Summary metrics
    writer.writerow(build_row('SUMMARY METRICS', [''] * len(calculations)))
    writer.writerow(build_row('Best Option Cost', [f"${metrics.get('min_total_cost', 0):,.2f}"] * len(calculations)))
    writer.writerow(build_row('Worst Option Cost', [f"${metrics.get('max_total_cost', 0):,.2f}"] * len(calculations)))
    writer.writerow(build_row('Average Cost', [f"${metrics.get('avg_total_cost', 0):,.2f}"] * len(calculations)))
    writer.writerow(build_row('Cost Spread', [f"${metrics.get('cost_spread', 0):,.2f} ({metrics.get('cost_spread_percent', 0):.1f}%)"] * len(calculations)))

    csv_content = output.getvalue()
    output.close()

    return csv_content
