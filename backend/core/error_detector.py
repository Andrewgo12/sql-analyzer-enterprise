"""
Simplified SQL Error Detector
Focused on core functionality without complex features
"""

import re
import logging
from typing import List, Dict, Any
from enum import IntEnum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ErrorSeverity(IntEnum):
    """Error severity levels with numeric values for sorting."""
    CRITICAL = 4    # Prevents execution, data corruption risk
    HIGH = 3        # Major functionality issues, security risks
    MEDIUM = 2      # Performance issues, best practice violations
    LOW = 1         # Style issues, minor optimizations
    INFO = 0        # Informational messages, suggestions

@dataclass
class ErrorLocation:
    """Error location information."""
    line_number: int
    column_start: int
    column_end: int
    context_start: int
    context_before: str
    context_after: str
    full_line: str

@dataclass
class ErrorFix:
    """Suggested fix for an error."""
    description: str
    original_text: str
    suggested_text: str
    confidence: float
    fix_type: str
    explanation: str

@dataclass
class SQLError:
    """SQL error with detailed information."""
    error_id: str
    message: str
    severity: ErrorSeverity
    category: str
    location: ErrorLocation
    fixes: List[ErrorFix]
    confidence_score: float
    correction_summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            'error_id': self.error_id,
            'message': self.message,
            'severity': self.severity.name,
            'severity_value': self.severity.value,
            'category': self.category,
            'line': self.location.line_number,
            'column_start': self.location.column_start,
            'column_end': self.location.column_end,
            'full_line': self.location.full_line,
            'fixes': [
                {
                    'description': fix.description,
                    'original': fix.original_text,
                    'suggested': fix.suggested_text,
                    'confidence': fix.confidence,
                    'type': fix.fix_type,
                    'explanation': fix.explanation
                }
                for fix in self.fixes
            ],
            'confidence': self.confidence_score,
            'correction_summary': self.correction_summary
        }

class ErrorDetector:
    """Simplified SQL error detector."""
    
    def __init__(self):
        """Initialize the error detector."""
        self.errors = []
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'ALTER', 'DROP', 'TABLE', 'INDEX', 'VIEW',
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'ON',
            'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET',
            'UNION', 'INTERSECT', 'EXCEPT', 'AND', 'OR', 'NOT',
            'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL',
            'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE',
            'CHECK', 'DEFAULT', 'AUTO_INCREMENT', 'IDENTITY'
        }
        
        logger.info("ErrorDetector inicializado (versión simplificada)")
    
    def analyze_sql(self, sql_content: str) -> List[SQLError]:
        """
        Analyze SQL content for errors.
        
        Args:
            sql_content: SQL code to analyze
            
        Returns:
            List of detected errors
        """
        self.errors = []
        
        try:
            lines = sql_content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    self._check_basic_syntax(line, line_num)
                    self._check_common_mistakes(line, line_num)
            
            # Sort errors by severity and line number
            self.errors.sort(key=lambda e: (-e.severity.value, e.location.line_number))
            
            logger.info(f"Análisis completado: {len(self.errors)} errores encontrados")
            
        except Exception as e:
            logger.error(f"Error durante análisis SQL: {e}")
            self._add_error(
                f"Error interno durante análisis: {str(e)}",
                ErrorLocation(1, 0, 0, 0, "", "", ""),
                ErrorSeverity.CRITICAL,
                "internal_error"
            )
        
        return self.errors
    
    def _add_error(self, message: str, location: ErrorLocation, severity: ErrorSeverity, category: str):
        """Add an error to the list."""
        error = SQLError(
            error_id=f"{category}_{len(self.errors) + 1}",
            message=message,
            severity=severity,
            category=category,
            location=location,
            fixes=[],
            confidence_score=0.8,
            correction_summary=f"Error de {category}: {message}"
        )
        
        self.errors.append(error)
