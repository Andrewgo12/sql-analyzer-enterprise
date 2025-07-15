"""
Excel Workbook Generator

Generates multi-sheet Excel workbooks with charts and analysis data.
"""

import time
import io
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult

# Optional imports for Excel generation
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import PieChart, BarChart, Reference
    from openpyxl.utils.dataframe import dataframe_to_rows
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ExcelWorkbookGenerator(BaseFormatGenerator):
    """Generator for Excel workbooks with multiple sheets and charts."""
    
    @property
    def format_name(self) -> str:
        return "Libro Excel"
    
    @property
    def file_extension(self) -> str:
        return ".xlsx"
    
    @property
    def mime_type(self) -> str:
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    @property
    def is_binary(self) -> bool:
        return True
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate Excel workbook with multiple sheets."""
        start_time = time.time()
        
        try:
            if not OPENPYXL_AVAILABLE:
                raise Exception("openpyxl no está disponible. Instale con: pip install openpyxl")
            
            self.validate_context(context)
            
            # Generate Excel content
            excel_content = self._generate_excel_workbook(context)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                excel_content, context, generation_time,
                metadata={
                    "sheets_created": 5,
                    "charts_included": 2,
                    "format": "Excel 2007+"
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
