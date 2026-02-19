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
