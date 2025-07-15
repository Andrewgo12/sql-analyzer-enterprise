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
    
    def _check_basic_syntax(self, line: str, line_num: int):
        """Check basic syntax issues."""
        line_stripped = line.strip()
        
        # Check for unmatched parentheses
        open_parens = line.count('(')
        close_parens = line.count(')')
        if open_parens != close_parens:
            self._add_error(
                f"Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados",
                ErrorLocation(line_num, 0, len(line), 0, "", "", line),
                ErrorSeverity.HIGH,
                "syntax_parentheses"
            )
        
        # Check for unmatched quotes
        single_quotes = line.count("'")
        if single_quotes % 2 != 0:
            self._add_error(
                "Comillas simples desbalanceadas",
                ErrorLocation(line_num, 0, len(line), 0, "", "", line),
                ErrorSeverity.HIGH,
                "syntax_quotes"
            )
        
        double_quotes = line.count('"')
        if double_quotes % 2 != 0:
            self._add_error(
                "Comillas dobles desbalanceadas",
                ErrorLocation(line_num, 0, len(line), 0, "", "", line),
                ErrorSeverity.HIGH,
                "syntax_quotes"
            )
    
    def _check_common_mistakes(self, line: str, line_num: int):
        """Check for common SQL mistakes."""
        line_upper = line.upper()
        
        # Check for SELECT * (performance issue)
        if 'SELECT *' in line_upper:
            self._add_error(
                "Evitar SELECT * por rendimiento - especificar columnas exactas",
                ErrorLocation(line_num, line.find('*'), line.find('*') + 1, 0, "", "", line),
                ErrorSeverity.MEDIUM,
                "performance_select_star"
            )
        
        # Check for missing semicolon at end of statement
        if any(keyword in line_upper for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']):
            if not line.rstrip().endswith(';') and not line.rstrip().endswith(','):
                self._add_error(
                    "Falta punto y coma al final de la declaración",
                    ErrorLocation(line_num, len(line.rstrip()), len(line.rstrip()), 0, "", "", line),
                    ErrorSeverity.LOW,
                    "syntax_semicolon"
                )
        
        # Check for potential SQL injection patterns
        injection_patterns = [
            r"'\s*OR\s*'1'\s*=\s*'1'",
            r"'\s*OR\s*1\s*=\s*1",
            r"--\s*$",
            r"/\*.*\*/"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self._add_error(
                    "Posible patrón de inyección SQL detectado",
                    ErrorLocation(line_num, 0, len(line), 0, "", "", line),
                    ErrorSeverity.CRITICAL,
                    "security_injection"
                )
    
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
