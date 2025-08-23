"""
Data export utilities with optional pandas dependency.
Provides graceful fallback when pandas is not available.
"""
import csv
import json
from io import StringIO, BytesIO
from typing import List, Dict, Any, Optional
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import logging

logger = logging.getLogger(__name__)

# Try to import pandas, but don't fail if it's not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    logger.info("Pandas is available for advanced data export")
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("Pandas not available - using fallback data export methods")


def export_to_excel_with_pandas(data: List[Dict[str, Any]], filename: str = "export.xlsx") -> BytesIO:
    """
    Export data to Excel using pandas (if available).
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("Pandas is required for advanced Excel export but is not installed")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create BytesIO buffer
    buffer = BytesIO()
    
    # Write to Excel
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    buffer.seek(0)
    return buffer


def export_to_excel_fallback(data: List[Dict[str, Any]], filename: str = "export.xlsx") -> BytesIO:
    """
    Export data to Excel using openpyxl (fallback method without pandas).
    """
    if not data:
        # Handle empty data
        wb = Workbook()
        ws = wb.active
        ws.title = "Data"
        ws.append(["No data available"])
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Data"
        
        # Add headers
        headers = list(data[0].keys())
        ws.append(headers)
        
        # Add data rows
        for row_data in data:
            row = [row_data.get(header, "") for header in headers]
            ws.append(row)
    
    # Save to BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_to_excel(data: List[Dict[str, Any]], filename: str = "export.xlsx", use_pandas: bool = True) -> BytesIO:
    """
    Export data to Excel with automatic fallback.
    
    Args:
        data: List of dictionaries to export
        filename: Name for the file (for reference)
        use_pandas: Whether to try using pandas first (if available)
    
    Returns:
        BytesIO buffer containing Excel file
    """
    if use_pandas and PANDAS_AVAILABLE:
        try:
            return export_to_excel_with_pandas(data, filename)
        except Exception as e:
            logger.warning(f"Pandas export failed: {e}. Falling back to openpyxl method.")
            return export_to_excel_fallback(data, filename)
    else:
        return export_to_excel_fallback(data, filename)


def export_to_csv(data: List[Dict[str, Any]], filename: str = "export.csv") -> StringIO:
    """
    Export data to CSV format.
    """
    if not data:
        buffer = StringIO()
        buffer.write("No data available\n")
        buffer.seek(0)
        return buffer
    
    buffer = StringIO()
    headers = list(data[0].keys())
    
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)
    
    buffer.seek(0)
    return buffer


def export_to_json(data: List[Dict[str, Any]], filename: str = "export.json") -> StringIO:
    """
    Export data to JSON format.
    """
    buffer = StringIO()
    json.dump(data, buffer, indent=2, default=str)
    buffer.seek(0)
    return buffer


def get_supported_formats() -> List[str]:
    """
    Get list of supported export formats.
    """
    formats = ["csv", "json", "xlsx"]
    if PANDAS_AVAILABLE:
        formats.extend(["xlsx_advanced"])
    return formats


def is_pandas_available() -> bool:
    """
    Check if pandas is available for advanced features.
    """
    return PANDAS_AVAILABLE