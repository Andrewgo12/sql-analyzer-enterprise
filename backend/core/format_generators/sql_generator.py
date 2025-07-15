"""
Enhanced SQL Generator

Generates enhanced SQL files with intelligent comments and corrections.
"""

import time
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class EnhancedSQLGenerator(BaseFormatGenerator):
    """Generator for enhanced SQL files with comments and corrections."""
    
    @property
    def format_name(self) -> str:
        return "SQL Mejorado"
    
    @property
    def file_extension(self) -> str:
        return ".sql"
    
    @property
    def mime_type(self) -> str:
        return "text/sql"
    
    @property
    def is_binary(self) -> bool:
        return False
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate enhanced SQL with comments and corrections."""
        start_time = time.time()
        
        try:
            self.validate_context(context)
            
            # Get the original SQL content
            original_sql = context.analysis_result.get("processed_content", "")
            if not original_sql:
                original_sql = context.analysis_result.get("original_content", "")
            
            # Generate enhanced SQL
            enhanced_sql = self._enhance_sql_content(original_sql, context)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                enhanced_sql, context, generation_time,
                metadata={
                    "original_lines": len(original_sql.split('\n')),
                    "enhanced_lines": len(enhanced_sql.split('\n')),
                    "comments_added": enhanced_sql.count('--'),
                    "corrections_applied": len(context.analysis_result.get("corrections_applied", []))
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
