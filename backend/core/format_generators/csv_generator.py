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
    
    def _generate_csv_content(self, context: GenerationContext) -> str:
        """Generate the complete CSV content."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        template_vars = self.get_template_variables(context)
        
        # Write header
        writer.writerow([
            "ID", "Severidad", "Categoria", "Titulo", "Mensaje", "Descripcion",
            "Linea", "Columna", "Confianza", "Correcciones_Disponibles",
            "Mejor_Correccion", "Confianza_Correccion"
        ])
        
        # Write error data
        for error in template_vars['errors']:
            # Get best fix if available
            fixes = error.get('fixes', [])
            best_fix = ""
            fix_confidence = 0.0
            
            if fixes:
                best_fix_obj = max(fixes, key=lambda f: f.get('confidence', 0))
                best_fix = best_fix_obj.get('description', '')
                fix_confidence = best_fix_obj.get('confidence', 0.0)
            
            writer.writerow([
                error.get('id', ''),
                error.get('severity', ''),
                error.get('category', ''),
                error.get('title', ''),
                error.get('message', ''),
                error.get('description', ''),
                error.get('line', 0),
                error.get('column', 0),
                error.get('confidence', 1.0),
                len(fixes),
                best_fix,
                fix_confidence
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
