"""
Advanced Error Detection Methods
Part 2 of the Enterprise-Grade SQL Error Detection Engine

Contains Level 2-4 detection methods and correction functionality.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any, Set, Union
from .error_detector import ErrorDetector, SQLError, ErrorSeverity, ErrorCategory, ErrorLocation, ErrorFix, CorrectionResult

logger = logging.getLogger(__name__)


class AdvancedErrorDetector(ErrorDetector):
    """Extended error detector with advanced semantic and logical analysis."""
    
    def _detect_data_type_errors(self, sql_content: str, parsed_statements: List):
        """Detect data type syntax errors."""
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper().strip()
            if not line_upper or line_upper.startswith('--'):
                continue
            
            # Check CREATE TABLE statements for data type errors
            if 'CREATE TABLE' in line_upper:
                self._check_create_table_data_types(line, line_num)
            
            # Check ALTER TABLE statements
            if 'ALTER TABLE' in line_upper and ('ADD' in line_upper or 'MODIFY' in line_upper):
                self._check_alter_table_data_types(line, line_num)
    
    def _detect_constraint_syntax_errors(self, sql_content: str, parsed_statements: List):
        """Detect constraint syntax errors."""
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper().strip()
            if not line_upper or line_upper.startswith('--'):
                continue
            
            # Check PRIMARY KEY constraints
            if 'PRIMARY KEY' in line_upper:
                self._check_primary_key_syntax(line, line_num)
            
            # Check FOREIGN KEY constraints
            if 'FOREIGN KEY' in line_upper:
                self._check_foreign_key_syntax(line, line_num)
            
            # Check UNIQUE constraints
            if 'UNIQUE' in line_upper and 'KEY' not in line_upper:
                self._check_unique_constraint_syntax(line, line_num)
            
            # Check CHECK constraints
            if 'CHECK' in line_upper:
                self._check_check_constraint_syntax(line, line_num)
    
    def _detect_semantic_errors(self, sql_content: str, parsed_statements: List):
        """Level 2: Semantic error detection."""
        # Schema validation
        self._detect_schema_errors(sql_content, parsed_statements)
        
        # Type compatibility
        self._detect_type_compatibility_errors(sql_content, parsed_statements)
        
        # Referential integrity
        self._detect_referential_integrity_errors(sql_content, parsed_statements)
        
        # Function usage
        self._detect_function_usage_errors(sql_content, parsed_statements)
    
    def _detect_logical_errors(self, sql_content: str, parsed_statements: List):
        """Level 3: Advanced logical error detection."""
        # Query structure
        self._detect_query_structure_errors(sql_content, parsed_statements)
        
        # Performance issues
        self._detect_performance_issues(sql_content, parsed_statements)
        
        # Security vulnerabilities
        self._detect_security_vulnerabilities(sql_content, parsed_statements)
    
    def _detect_database_specific_errors(self, sql_content: str, parsed_statements: List):
        """Level 4: Database-specific validation."""
        # Version compatibility
        self._detect_version_compatibility_issues(sql_content)
        
        # Dialect-specific syntax
        self._detect_dialect_issues(sql_content)
    
    def _detect_performance_issues(self, sql_content: str, parsed_statements: List):
        """Detect performance anti-patterns."""
        for issue_category, patterns in self.performance_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = sql_content[:match.start()].count('\n') + 1
                    line = sql_content.split('\n')[line_num - 1]
                    
                    self._add_error(
                        ErrorSeverity.MEDIUM,
                        ErrorCategory.LOGICAL_PERFORMANCE,
                        f"PERFORMANCE_{issue_category.upper()}",
                        f"Problema de rendimiento: {issue_category}",
                        f"Patrón de rendimiento detectado: {match.group(0)}",
                        f"Este patrón puede causar problemas de {issue_category}",
                        ErrorLocation(line_num, match.start(), match.end(), 0, "", "", line),
                        confidence=0.7,
                        tags=['performance', issue_category]
                    )
    
    def _post_process_errors(self):
        """Post-process errors: remove duplicates, sort by severity."""
        # Remove duplicate errors
        seen_errors = set()
        unique_errors = []
        
        for error in self.errors:
            error_key = (error.code, error.location.line_number, error.location.column_start)
            if error_key not in seen_errors:
                seen_errors.add(error_key)
                unique_errors.append(error)
        
        # Sort by severity (highest first), then by line number
        self.errors = sorted(unique_errors, key=lambda e: (-e.severity.value, e.location.line_number))
    
    def correct_sql(self, sql_content: str) -> CorrectionResult:
        """Automatically correct SQL errors."""
        # First, analyze to find errors
        errors = self.analyze_sql(sql_content)
        
        corrected_sql = sql_content
        corrections_applied = []
        remaining_errors = []
        
        # Apply fixes for high-confidence errors
        for error in errors:
            if error.fixes and error.confidence > 0.8:
                # Apply the highest confidence fix
                best_fix = max(error.fixes, key=lambda f: f.confidence)
                if best_fix.confidence > 0.8:
                    corrected_sql = corrected_sql.replace(best_fix.original_text, best_fix.corrected_text)
                    corrections_applied.append(best_fix)
                else:
                    remaining_errors.append(error)
            else:
                remaining_errors.append(error)
        
        # Calculate overall confidence
        if corrections_applied:
            confidence_score = sum(fix.confidence for fix in corrections_applied) / len(corrections_applied)
        else:
            confidence_score = 1.0 if not errors else 0.0
        
        # Generate summary
        summary_parts = []
        if corrections_applied:
            summary_parts.append(f"Se aplicaron {len(corrections_applied)} correcciones automáticas")
        if remaining_errors:
            summary_parts.append(f"Quedan {len(remaining_errors)} errores que requieren atención manual")
        
        correction_summary = ". ".join(summary_parts) if summary_parts else "No se encontraron errores"
        
        return CorrectionResult(
            original_sql=sql_content,
            corrected_sql=corrected_sql,
            corrections_applied=corrections_applied,
            remaining_errors=remaining_errors,
            confidence_score=confidence_score,
            correction_summary=correction_summary
        )
