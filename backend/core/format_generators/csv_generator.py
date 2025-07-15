"""
CSV Summary Generator

Generates CSV files with tabular error summary and metrics.
"""

import time
import csv
import io
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class CSVSummaryGenerator(BaseFormatGenerator):
    """Generator for CSV summary files."""
    
    @property
    def format_name(self) -> str:
        return "Resumen CSV"
    
    @property
    def file_extension(self) -> str:
        return ".csv"
    
    @property
    def mime_type(self) -> str:
        return "text/csv"
    
    @property
    def is_binary(self) -> bool:
        return False
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate CSV summary file."""
        start_time = time.time()
        
        try:
            self.validate_context(context)
            
            # Generate CSV content
            csv_content = self._generate_csv_content(context)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                csv_content, context, generation_time,
                metadata={
                    "rows_generated": csv_content.count('\n'),
                    "encoding": "utf-8",
                    "delimiter": ","
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
