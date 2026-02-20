import csv
from io import StringIO
from typing import List, Dict, Tuple
from decimal import Decimal, InvalidOperation


class CatalogParser:
    """Service for parsing and validating CSV product catalog uploads"""

    REQUIRED_COLUMNS = [
        'sku',
        'product_name',
        'hs_code',
        'origin_country',
        'cogs',
        'retail_price',
        'annual_volume'
    ]

    OPTIONAL_COLUMNS = ['category', 'weight_kg', 'notes']

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    VALID_COUNTRIES = ['CN', 'US', 'EU', 'JP', 'KR', 'MX', 'CA']

    @staticmethod
    async def parse_csv(file_content: bytes, filename: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse CSV content and return valid items and errors

        Args:
            file_content: Raw CSV file bytes
            filename: Name of the uploaded file

        Returns:
            Tuple of (valid_items, errors)
            - valid_items: List of dictionaries with parsed product data
            - errors: List of dictionaries with row number, sku, and error message
        """
        # Validate file size
        if len(file_content) > CatalogParser.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds 5MB limit. File size: {len(file_content) / (1024 * 1024):.2f}MB")

        # Validate file extension
        if not filename.lower().endswith('.csv'):
            raise ValueError("File must be a CSV file with .csv extension")

        # Decode content
        try:
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try with UTF-8-sig (handles BOM)
                content_str = file_content.decode('utf-8-sig')
            except UnicodeDecodeError:
                raise ValueError("File must be UTF-8 encoded")

        # Parse CSV
        try:
            reader = csv.DictReader(StringIO(content_str))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        # Validate headers
        if not reader.fieldnames:
            raise ValueError("CSV file appears to be empty or has no headers")

        missing_columns = set(CatalogParser.REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

        # Parse rows
        valid_items = []
        errors = []

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
            try:
                # Skip completely empty rows
                if all(not value.strip() for value in row.values()):
                    continue

                item = CatalogParser._parse_row(row, row_num)
                valid_items.append(item)
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'sku': row.get('sku', 'Unknown').strip() if row.get('sku') else 'Unknown',
                    'error': str(e)
                })

        # Ensure at least one valid row
        if not valid_items and errors:
            raise ValueError(f"No valid rows found. {len(errors)} row(s) had errors.")

        return valid_items, errors

    @staticmethod
    def _parse_row(row: Dict, row_num: int) -> Dict:
        """
        Parse and validate a single CSV row

        Args:
            row: Dictionary of row data
            row_num: Row number for error reporting

        Returns:
            Dictionary with validated and parsed data
        """
        parsed = {}

        # Required: SKU
        sku = row.get('sku', '').strip()
        if not sku:
            raise ValueError("SKU is required")
        if len(sku) > 100:
            raise ValueError(f"SKU too long (max 100 characters): {sku}")
        parsed['sku'] = sku

        # Required: Product Name
        product_name = row.get('product_name', '').strip()
        if not product_name:
            raise ValueError("Product name is required")
        if len(product_name) > 255:
            raise ValueError(f"Product name too long (max 255 characters)")
        parsed['product_name'] = product_name

        # Required: HS Code
        hs_code = row.get('hs_code', '').strip()
        if not hs_code:
            raise ValueError("HS code is required")
        # Remove dots and spaces
        hs_code = hs_code.replace('.', '').replace(' ', '')
        if not hs_code.isdigit():
            raise ValueError(f"HS code must contain only digits (periods allowed): {hs_code}")
        if len(hs_code) < 6 or len(hs_code) > 10:
            raise ValueError(f"HS code must be 6-10 digits: {hs_code}")
        parsed['hs_code'] = hs_code

        # Required: Origin Country
        origin_country = row.get('origin_country', '').strip().upper()
        if not origin_country:
            raise ValueError("Origin country is required")
        if origin_country not in CatalogParser.VALID_COUNTRIES:
            raise ValueError(f"Invalid origin country: {origin_country}. Must be one of: {', '.join(CatalogParser.VALID_COUNTRIES)}")
        parsed['origin_country'] = origin_country

        # Required: COGS
        try:
            cogs_str = row.get('cogs', '').strip()
            if not cogs_str:
                raise ValueError("COGS is required")
            # Remove currency symbols and commas
            cogs_str = cogs_str.replace('$', '').replace(',', '')
            cogs = Decimal(cogs_str)
            if cogs <= 0:
                raise ValueError(f"COGS must be greater than 0: {cogs}")
            if cogs > Decimal('9999999999.99'):
                raise ValueError(f"COGS too large: {cogs}")
            parsed['cogs'] = cogs
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid COGS value: {row.get('cogs')} - {str(e)}")

        # Required: Retail Price
        try:
            retail_str = row.get('retail_price', '').strip()
            if not retail_str:
                raise ValueError("Retail price is required")
            # Remove currency symbols and commas
            retail_str = retail_str.replace('$', '').replace(',', '')
            retail_price = Decimal(retail_str)
            if retail_price <= 0:
                raise ValueError(f"Retail price must be greater than 0: {retail_price}")
            if retail_price > Decimal('9999999999.99'):
                raise ValueError(f"Retail price too large: {retail_price}")
            parsed['retail_price'] = retail_price
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid retail price value: {row.get('retail_price')} - {str(e)}")

        # Required: Annual Volume
        try:
            volume_str = row.get('annual_volume', '').strip()
            if not volume_str:
                raise ValueError("Annual volume is required")
            # Remove commas
            volume_str = volume_str.replace(',', '')
            annual_volume = int(volume_str)
            if annual_volume < 0:
                raise ValueError(f"Annual volume cannot be negative: {annual_volume}")
            if annual_volume > 999999999:
                raise ValueError(f"Annual volume too large: {annual_volume}")
            parsed['annual_volume'] = annual_volume
        except (ValueError) as e:
            raise ValueError(f"Invalid annual volume value: {row.get('annual_volume')} - {str(e)}")

        # Optional: Category
        category = row.get('category', '').strip()
        if category:
            if len(category) > 100:
                raise ValueError(f"Category too long (max 100 characters)")
            parsed['category'] = category
        else:
            parsed['category'] = None

        # Optional: Weight (kg)
        weight_str = row.get('weight_kg', '').strip()
        if weight_str:
            try:
                # Remove commas
                weight_str = weight_str.replace(',', '')
                weight_kg = Decimal(weight_str)
                if weight_kg < 0:
                    raise ValueError(f"Weight cannot be negative: {weight_kg}")
                if weight_kg > Decimal('99999999.99'):
                    raise ValueError(f"Weight too large: {weight_kg}")
                parsed['weight_kg'] = weight_kg
            except (InvalidOperation, ValueError) as e:
                raise ValueError(f"Invalid weight value: {row.get('weight_kg')} - {str(e)}")
        else:
            parsed['weight_kg'] = None

        # Optional: Notes
        notes = row.get('notes', '').strip()
        if notes:
            if len(notes) > 1000:
                raise ValueError(f"Notes too long (max 1000 characters)")
            parsed['notes'] = notes
        else:
            parsed['notes'] = None

        return parsed
