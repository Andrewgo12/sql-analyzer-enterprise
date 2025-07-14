"""
Base Format Generator

Abstract base class for all format generators with common functionality.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, BinaryIO
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class FormatGeneratorError(Exception):
    """Exception raised by format generators."""
    pass


@dataclass
class GenerationContext:
    """Context information for format generation."""
    analysis_result: Dict[str, Any]
    original_filename: str
    analysis_timestamp: datetime
    user_options: Dict[str, Any]
    session_id: str
    output_directory: Optional[Path] = None
    include_raw_data: bool = True
    include_statistics: bool = True
    include_recommendations: bool = True
    language: str = "es"  # Spanish by default


@dataclass
class GenerationResult:
    """Result of format generation."""
    success: bool
    content: Union[str, bytes]
    filename: str
    mime_type: str
    file_size: int
    generation_time: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseFormatGenerator(ABC):
    """
    Abstract base class for all format generators.
    
    Provides common functionality and defines the interface that all
    format generators must implement.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.supported_languages = ["es", "en"]
        self.default_language = "es"
        
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Human-readable name of the format."""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for this format (including the dot)."""
        pass
    
    @property
    @abstractmethod
    def mime_type(self) -> str:
        """MIME type for this format."""
        pass
    
    @property
    @abstractmethod
    def is_binary(self) -> bool:
        """Whether this format produces binary content."""
        pass
    
    @abstractmethod
    def generate(self, context: GenerationContext) -> GenerationResult:
        """
        Generate content in this format.
        
        Args:
            context: Generation context with analysis results and options
            
        Returns:
            GenerationResult with the generated content
        """
        pass
    
    def validate_context(self, context: GenerationContext) -> None:
        """
        Validate the generation context.
        
        Args:
            context: Generation context to validate
            
        Raises:
            FormatGeneratorError: If context is invalid
        """
        if not context.analysis_result:
            raise FormatGeneratorError("Resultado de análisis requerido")
        
        if not context.original_filename:
            raise FormatGeneratorError("Nombre de archivo original requerido")
        
        if context.language not in self.supported_languages:
            self.logger.warning(f"Idioma no soportado: {context.language}, usando {self.default_language}")
            context.language = self.default_language
    
    def generate_filename(self, context: GenerationContext, suffix: str = "") -> str:
        """
        Generate a filename for the output file.
        
        Args:
            context: Generation context
            suffix: Optional suffix to add before the extension
            
        Returns:
            Generated filename
        """
        base_name = Path(context.original_filename).stem
        timestamp = context.analysis_timestamp.strftime("%Y%m%d_%H%M%S")
        
        if suffix:
            filename = f"{base_name}_{suffix}_{timestamp}{self.file_extension}"
        else:
            filename = f"{base_name}_analysis_{timestamp}{self.file_extension}"
        
        return filename
    
    def get_analysis_summary(self, context: GenerationContext) -> Dict[str, Any]:
        """
        Extract analysis summary from context.
        
        Args:
            context: Generation context
            
        Returns:
            Analysis summary dictionary
        """
        result = context.analysis_result
        
        return {
            "filename": context.original_filename,
            "analysis_date": context.analysis_timestamp.isoformat(),
            "total_errors": result.get("errors_found", 0),
            "critical_errors": len([e for e in result.get("errors", []) if e.get("severity") == "CRITICAL"]),
            "high_errors": len([e for e in result.get("errors", []) if e.get("severity") == "HIGH"]),
            "medium_errors": len([e for e in result.get("errors", []) if e.get("severity") == "MEDIUM"]),
            "low_errors": len([e for e in result.get("errors", []) if e.get("severity") == "LOW"]),
            "fixes_suggested": result.get("fixes_suggested", 0),
            "quality_score": result.get("quality_score", 0),
            "lines_analyzed": result.get("lines", 0),
            "file_size": result.get("size", 0),
            "statements_analyzed": result.get("analysis_summary", {}).get("total_statements", 0)
        }
    
    def get_error_categories(self, context: GenerationContext) -> Dict[str, int]:
        """
        Get error counts by category.
        
        Args:
            context: Generation context
            
        Returns:
            Dictionary mapping categories to error counts
        """
        errors = context.analysis_result.get("errors", [])
        categories = {}
        
        for error in errors:
            category = error.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def format_error_for_display(self, error: Dict[str, Any], language: str = "es") -> Dict[str, Any]:
        """
        Format an error for display in the output format.
        
        Args:
            error: Error dictionary
            language: Display language
            
        Returns:
            Formatted error dictionary
        """
        severity_translations = {
            "es": {
                "CRITICAL": "Crítico",
                "HIGH": "Alto",
                "MEDIUM": "Medio",
                "LOW": "Bajo",
                "INFO": "Información"
            },
            "en": {
                "CRITICAL": "Critical",
                "HIGH": "High",
                "MEDIUM": "Medium",
                "LOW": "Low",
                "INFO": "Info"
            }
        }
        
        translations = severity_translations.get(language, severity_translations["es"])
        
        return {
            "id": error.get("id", ""),
            "severity": error.get("severity", ""),
            "severity_display": translations.get(error.get("severity", ""), error.get("severity", "")),
            "category": error.get("category", ""),
            "title": error.get("title", ""),
            "message": error.get("message", ""),
            "description": error.get("description", ""),
            "line": error.get("location", {}).get("line", 0),
            "column": error.get("location", {}).get("column_start", 0),
            "fixes": error.get("fixes", []),
            "confidence": error.get("confidence", 0.0)
        }
    
    def create_generation_result(self, content: Union[str, bytes], context: GenerationContext,
                               generation_time: float, metadata: Optional[Dict[str, Any]] = None) -> GenerationResult:
        """
        Create a generation result.
        
        Args:
            content: Generated content
            context: Generation context
            generation_time: Time taken to generate
            metadata: Optional metadata
            
        Returns:
            GenerationResult instance
        """
        filename = self.generate_filename(context)
        
        if isinstance(content, str):
            file_size = len(content.encode('utf-8'))
        else:
            file_size = len(content)
        
        return GenerationResult(
            success=True,
            content=content,
            filename=filename,
            mime_type=self.mime_type,
            file_size=file_size,
            generation_time=generation_time,
            metadata=metadata
        )
    
    def handle_generation_error(self, error: Exception, context: GenerationContext) -> GenerationResult:
        """
        Handle generation errors and create error result.
        
        Args:
            error: The exception that occurred
            context: Generation context
            
        Returns:
            GenerationResult with error information
        """
        self.logger.error(f"Error generating {self.format_name}: {error}")
        
        return GenerationResult(
            success=False,
            content="",
            filename="",
            mime_type=self.mime_type,
            file_size=0,
            generation_time=0.0,
            error_message=str(error)
        )
    
    def get_template_variables(self, context: GenerationContext) -> Dict[str, Any]:
        """
        Get template variables for content generation.
        
        Args:
            context: Generation context
            
        Returns:
            Dictionary of template variables
        """
        summary = self.get_analysis_summary(context)
        categories = self.get_error_categories(context)
        
        return {
            "summary": summary,
            "categories": categories,
            "errors": [self.format_error_for_display(e, context.language) 
                      for e in context.analysis_result.get("errors", [])],
            "original_filename": context.original_filename,
            "analysis_timestamp": context.analysis_timestamp,
            "session_id": context.session_id,
            "language": context.language,
            "user_options": context.user_options,
            "generator_name": self.format_name,
            "generator_version": "1.0.0"
        }
