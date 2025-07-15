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
    
    def _check_create_table_data_types(self, line: str, line_num: int):
        """Check data types in CREATE TABLE statements."""
        # Extract column definitions
        paren_match = re.search(r'\((.*)\)', line, re.DOTALL)
        if not paren_match:
            return
        
        columns_text = paren_match.group(1)
        column_defs = [col.strip() for col in columns_text.split(',')]
        
        for col_def in column_defs:
            if not col_def or col_def.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK')):
                continue
            
            # Parse column definition: name type(size) constraints
            parts = col_def.split()
            if len(parts) < 2:
                continue
            
            column_name = parts[0]
            data_type = parts[1]
            
            # Check for invalid data type
            self._validate_data_type(data_type, line, line_num, column_name)
    
    def _validate_data_type(self, data_type: str, line: str, line_num: int, column_name: str = ""):
        """Validate a data type against the current database engine."""
        # Extract base type and size
        type_match = re.match(r'([A-Za-z_]+)(\([^)]*\))?', data_type)
        if not type_match:
            return
        
        base_type = type_match.group(1).upper()
        size_spec = type_match.group(2) or ""
        
        # Get valid types for current database engine
        valid_types = set()
        if self.database_engine in self.data_types:
            for type_category in self.data_types[self.database_engine].values():
                valid_types.update(type_category)
        
        # Check if type is valid
        if base_type not in valid_types:
            # Try to find similar valid type
            suggestions = self._find_similar_data_types(base_type, valid_types)
            
            type_pos = line.upper().find(base_type)
            error_message = f"Tipo de dato '{base_type}' no válido para {self.database_engine.value}"
            if column_name:
                error_message += f" en la columna '{column_name}'"
            
            fixes = []
            for suggestion, confidence in suggestions:
                fixes.append(ErrorFix(
                    f"Cambiar a '{suggestion}'",
                    data_type,
                    data_type.replace(base_type, suggestion),
                    confidence,
                    "data_type_correction",
                    f"'{suggestion}' es un tipo de dato válido similar a '{base_type}'"
                ))
            
            self._add_error(
                ErrorSeverity.HIGH,
                ErrorCategory.SYNTAX_DATA_TYPES,
                "INVALID_DATA_TYPE",
                "Tipo de dato inválido",
                error_message,
                f"El tipo '{base_type}' no está disponible en {self.database_engine.value}",
                ErrorLocation(line_num, type_pos, type_pos + len(base_type), 0, "", "", line),
                fixes
            )
        
        # Check size specifications
        if size_spec:
            self._validate_size_specification(base_type, size_spec, line, line_num)
    
    def _find_similar_data_types(self, invalid_type: str, valid_types: Set[str]) -> List[Tuple[str, float]]:
        """Find similar valid data types."""
        suggestions = []
        
        for valid_type in valid_types:
            similarity = self._calculate_similarity(invalid_type, valid_type)
            if similarity > 0.6:
                suggestions.append((valid_type, similarity))
        
        # Sort by similarity
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:3]  # Return top 3 suggestions
    
    def _validate_size_specification(self, data_type: str, size_spec: str, line: str, line_num: int):
        """Validate size specifications for data types."""
        # Remove parentheses
        size_content = size_spec.strip('()')
        
        # Check for valid size format
        if ',' in size_content:
            # Precision and scale (e.g., DECIMAL(10,2))
            parts = [p.strip() for p in size_content.split(',')]
            if len(parts) != 2:
                self._add_size_error(line, line_num, size_spec, "Formato de precisión y escala inválido")
                return
            
            try:
                precision = int(parts[0])
                scale = int(parts[1])
                
                if scale > precision:
                    self._add_size_error(
                        line, line_num, size_spec,
                        f"La escala ({scale}) no puede ser mayor que la precisión ({precision})"
                    )
                
                # Check type-specific limits
                if data_type.upper() == 'DECIMAL':
                    if precision > 65:  # MySQL limit
                        self._add_size_error(
                            line, line_num, size_spec,
                            f"La precisión máxima para DECIMAL es 65, se especificó {precision}"
                        )
                    if scale > 30:  # MySQL limit
                        self._add_size_error(
                            line, line_num, size_spec,
                            f"La escala máxima para DECIMAL es 30, se especificó {scale}"
                        )
                        
            except ValueError:
                self._add_size_error(line, line_num, size_spec, "Los valores de precisión y escala deben ser números")
        
        else:
            # Single size value (e.g., VARCHAR(255))
            try:
                size = int(size_content)
                
                # Check type-specific limits
                if data_type.upper() == 'VARCHAR':
                    max_size = self._get_varchar_max_size()
                    if size > max_size:
                        self._add_size_error(
                            line, line_num, size_spec,
                            f"El tamaño máximo para VARCHAR es {max_size}, se especificó {size}"
                        )
                elif data_type.upper() == 'CHAR':
                    if size > 255:  # Common limit
                        self._add_size_error(
                            line, line_num, size_spec,
                            f"El tamaño máximo para CHAR es 255, se especificó {size}"
                        )
                        
            except ValueError:
                self._add_size_error(line, line_num, size_spec, "El tamaño debe ser un número")
    
    def _get_varchar_max_size(self) -> int:
        """Get maximum VARCHAR size for current database engine."""
        limits = {
            'mysql': 65535,
            'postgresql': 10485760,  # 10MB
            'sql_server': 8000,
            'oracle': 4000,
            'sqlite': 1000000000  # 1GB
        }
        return limits.get(self.database_engine.value, 65535)
    
    def _add_size_error(self, line: str, line_num: int, size_spec: str, message: str):
        """Add a size specification error."""
        size_pos = line.find(size_spec)
        self._add_error(
            ErrorSeverity.HIGH,
            ErrorCategory.SYNTAX_DATA_TYPES,
            "INVALID_SIZE_SPEC",
            "Especificación de tamaño inválida",
            message,
            "La especificación de tamaño no cumple con los requisitos del tipo de dato",
            ErrorLocation(line_num, size_pos, size_pos + len(size_spec), 0, "", "", line)
        )
    
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
    
    def _check_primary_key_syntax(self, line: str, line_num: int):
        """Check PRIMARY KEY constraint syntax."""
        # Look for PRIMARY KEY without column specification
        pk_pattern = r'PRIMARY\s+KEY\s*(?!\()'
        if re.search(pk_pattern, line, re.IGNORECASE):
            # Check if this is a column-level constraint
            if not re.search(r'\w+\s+\w+.*PRIMARY\s+KEY', line, re.IGNORECASE):
                pk_pos = line.upper().find('PRIMARY KEY')
                self._add_error(
                    ErrorSeverity.HIGH,
                    ErrorCategory.SYNTAX_CONSTRAINTS,
                    "INCOMPLETE_PRIMARY_KEY",
                    "Clave primaria incompleta",
                    "PRIMARY KEY requiere especificación de columnas",
                    "Debe especificar las columnas que forman la clave primaria",
                    ErrorLocation(line_num, pk_pos, pk_pos + 11, 0, "", "", line),
                    [ErrorFix(
                        "Agregar especificación de columnas",
                        "PRIMARY KEY",
                        "PRIMARY KEY (column_name)",
                        0.8,
                        "add_pk_columns",
                        "Especificar las columnas de la clave primaria"
                    )]
                )
    
    def _check_foreign_key_syntax(self, line: str, line_num: int):
        """Check FOREIGN KEY constraint syntax."""
        # Check for FOREIGN KEY without REFERENCES
        if 'FOREIGN KEY' in line.upper() and 'REFERENCES' not in line.upper():
            fk_pos = line.upper().find('FOREIGN KEY')
            self._add_error(
                ErrorSeverity.HIGH,
                ErrorCategory.SYNTAX_CONSTRAINTS,
                "INCOMPLETE_FOREIGN_KEY",
                "Clave foránea incompleta",
                "FOREIGN KEY requiere cláusula REFERENCES",
                "Debe especificar la tabla y columna referenciada",
                ErrorLocation(line_num, fk_pos, fk_pos + 11, 0, "", "", line),
                [ErrorFix(
                    "Agregar cláusula REFERENCES",
                    line.strip(),
                    line.strip() + " REFERENCES table_name(column_name)",
                    0.7,
                    "add_references",
                    "Especificar la tabla y columna referenciada"
                )]
            )
        
        # Check REFERENCES syntax
        if 'REFERENCES' in line.upper():
            # Should have format: REFERENCES table_name(column_name)
            ref_pattern = r'REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)'
            if not re.search(ref_pattern, line, re.IGNORECASE):
                ref_pos = line.upper().find('REFERENCES')
                self._add_error(
                    ErrorSeverity.HIGH,
                    ErrorCategory.SYNTAX_CONSTRAINTS,
                    "INVALID_REFERENCES_SYNTAX",
                    "Sintaxis REFERENCES inválida",
                    "La cláusula REFERENCES tiene sintaxis incorrecta",
                    "Formato correcto: REFERENCES tabla(columna)",
                    ErrorLocation(line_num, ref_pos, ref_pos + 10, 0, "", "", line)
                )
    
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
    
    def _detect_security_vulnerabilities(self, sql_content: str, parsed_statements: List):
        """Detect SQL injection and security vulnerabilities."""
        for pattern_category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = sql_content[:match.start()].count('\n') + 1
                    line = sql_content.split('\n')[line_num - 1]
                    
                    severity = ErrorSeverity.CRITICAL if pattern_category == 'sql_injection' else ErrorSeverity.HIGH
                    
                    self._add_error(
                        severity,
                        ErrorCategory.LOGICAL_SECURITY,
                        f"SECURITY_{pattern_category.upper()}",
                        f"Vulnerabilidad de seguridad: {pattern_category}",
                        f"Patrón de seguridad detectado: {match.group(0)}",
                        f"Este patrón puede indicar una vulnerabilidad de {pattern_category}",
                        ErrorLocation(line_num, match.start(), match.end(), 0, "", "", line),
                        confidence=0.8,
                        tags=['security', pattern_category]
                    )
    
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
