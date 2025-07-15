"""
JSON Analysis Generator

Generates structured JSON analysis data with comprehensive error information.
"""

import time
import json
import re
from typing import Dict, Any
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class JSONAnalysisGenerator(BaseFormatGenerator):
    """Generator for structured JSON analysis data."""
    
    @property
    def format_name(self) -> str:
        return "Datos JSON"
    
    @property
    def file_extension(self) -> str:
        return ".json"
    
    @property
    def mime_type(self) -> str:
        return "application/json"
    
    @property
    def is_binary(self) -> bool:
        return False
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate structured JSON analysis data."""
        start_time = time.time()
        
        try:
            self.validate_context(context)
            
            # Generate JSON structure
            json_data = self._generate_json_structure(context)
            
            # Convert to formatted JSON string
            json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                json_content, context, generation_time,
                metadata={
                    "schema_version": "1.0",
                    "total_objects": len(json_data.get("errors", [])),
                    "data_size_kb": len(json_content) / 1024
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
