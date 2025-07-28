#!/usr/bin/env python3
"""
COMPREHENSIVE SQL ANALYSIS SYSTEM
Enterprise-grade SQL analysis with multi-database support and real-time processing
"""

import re
import json
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import logging

class DatabaseType(Enum):
    """Supported database types"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQL_SERVER = "sql_server"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    REDIS = "redis"
    GENERIC = "generic"

@dataclass
class SQLError:
    """SQL Error representation"""
    line_number: int
    column: int
    error_type: str
    severity: str
    message: str
    suggestion: str
    auto_fixable: bool = False
    fixed_code: Optional[str] = None

@dataclass
class TableInfo:
    """Database table information"""
    name: str
    columns: List[Dict[str, Any]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[str]
    constraints: List[str]
    estimated_rows: Optional[int] = None

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    file_hash: str
    processing_time: float
    database_type: DatabaseType
    total_lines: int
    total_statements: int
    syntax_errors: List[SQLError]
    semantic_errors: List[SQLError]
    performance_issues: List[Dict[str, Any]]
    security_vulnerabilities: List[Dict[str, Any]]
    tables: List[TableInfo]
    relationships: List[Dict[str, Any]]
    quality_score: int
    complexity_score: int
    recommendations: List[str]
    corrected_sql: str
    intelligent_comments: List[Dict[str, Any]]

class ComprehensiveSQLAnalyzer:
    """Main SQL Analysis Engine with multi-database support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_database_patterns()
        self.setup_analysis_rules()
        self._analysis_cache = {}
        self._cache_lock = threading.Lock()
    
    def setup_database_patterns(self):
        """Setup database-specific patterns and keywords"""
        self.db_keywords = {
            DatabaseType.MYSQL: {
                'data_types': ['INT', 'VARCHAR', 'TEXT', 'DATETIME', 'DECIMAL', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'JSON', 'BLOB'],
                'functions': ['NOW()', 'CONCAT()', 'SUBSTRING()', 'LENGTH()', 'IFNULL()', 'COALESCE()'],
                'engines': ['InnoDB', 'MyISAM', 'Memory'],
                'syntax_patterns': [
                    r'(?i)AUTO_INCREMENT',
                    r'(?i)ENGINE\s*=\s*(InnoDB|MyISAM)',
                    r'(?i)CHARSET\s*=\s*utf8',
                    r'(?i)LIMIT\s+\d+(?:\s*,\s*\d+)?'
                ]
            },
            DatabaseType.POSTGRESQL: {
                'data_types': ['INTEGER', 'VARCHAR', 'TEXT', 'TIMESTAMP', 'NUMERIC', 'REAL', 'BOOLEAN', 'JSON', 'BYTEA'],
                'functions': ['NOW()', 'CONCAT()', 'SUBSTRING()', 'LENGTH()', 'COALESCE()', 'NULLIF()'],
                'features': ['SERIAL', 'BIGSERIAL', 'UUID'],
                'syntax_patterns': [
                    r'(?i)SERIAL',
                    r'(?i)RETURNING\s+',
                    r'(?i)LIMIT\s+\d+\s+OFFSET\s+\d+',
                    r'(?i)\$\$.*\$\$'
                ]
            },
            DatabaseType.ORACLE: {
                'data_types': ['NUMBER', 'VARCHAR2', 'CLOB', 'DATE', 'TIMESTAMP', 'BLOB', 'RAW'],
                'functions': ['SYSDATE', 'CONCAT()', 'SUBSTR()', 'LENGTH()', 'NVL()', 'NVL2()'],
                'features': ['SEQUENCE', 'TRIGGER', 'PACKAGE'],
                'syntax_patterns': [
                    r'(?i)ROWNUM\s*<=?\s*\d+',
                    r'(?i)CONNECT\s+BY',
                    r'(?i)START\s+WITH',
                    r'(?i)DUAL'
                ]
            },
            DatabaseType.SQL_SERVER: {
                'data_types': ['INT', 'NVARCHAR', 'TEXT', 'DATETIME', 'DECIMAL', 'FLOAT', 'BIT', 'UNIQUEIDENTIFIER'],
                'functions': ['GETDATE()', 'CONCAT()', 'SUBSTRING()', 'LEN()', 'ISNULL()', 'COALESCE()'],
                'features': ['IDENTITY', 'CLUSTERED', 'NONCLUSTERED'],
                'syntax_patterns': [
                    r'(?i)IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)',
                    r'(?i)TOP\s+\d+',
                    r'(?i)\[.*\]',
                    r'(?i)WITH\s*\(.*\)'
                ]
            }
        }
    
    def setup_analysis_rules(self):
        """Setup analysis rules and patterns"""
        self.syntax_rules = [
            {
                'pattern': r'(?i)select\s+.*\s+from\s+\w+(?!\s+where|\s+group|\s+order|\s+limit|\s*;)',
                'error_type': 'missing_where',
                'severity': 'medium',
                'message': 'SELECT statement without WHERE clause may return all rows',
                'suggestion': 'Consider adding WHERE clause to filter results'
            },
            {
                'pattern': r'(?i)(update|delete)\s+.*(?!\s+where)',
                'error_type': 'dangerous_operation',
                'severity': 'high',
                'message': 'UPDATE/DELETE without WHERE clause affects all rows',
                'suggestion': 'Add WHERE clause to limit affected rows'
            },
            {
                'pattern': r'\(\s*\)',
                'error_type': 'empty_parentheses',
                'severity': 'low',
                'message': 'Empty parentheses found',
                'suggestion': 'Remove empty parentheses or add content'
            }
        ]
        
        self.performance_rules = [
            {
                'pattern': r'(?i)select\s+\*\s+from',
                'issue_type': 'select_star',
                'impact': 'medium',
                'description': 'SELECT * retrieves all columns, potentially unnecessary data',
                'recommendation': 'Specify only needed columns'
            },
            {
                'pattern': r'(?i)like\s+[\'"][%]',
                'issue_type': 'leading_wildcard',
                'impact': 'high',
                'description': 'LIKE with leading wildcard cannot use indexes',
                'recommendation': 'Avoid leading wildcards or use full-text search'
            },
            {
                'pattern': r'(?i)order\s+by\s+.*(?!\s+limit)',
                'issue_type': 'order_without_limit',
                'impact': 'medium',
                'description': 'ORDER BY without LIMIT sorts entire result set',
                'recommendation': 'Add LIMIT clause if appropriate'
            }
        ]
        
        self.security_rules = [
            {
                'pattern': r'(?i)(union|select|insert|update|delete)\s+.*\s+(or|and)\s+[\'"]?\d+[\'"]?\s*=\s*[\'"]?\d+[\'"]?',
                'vulnerability_type': 'sql_injection',
                'risk_level': 'critical',
                'description': 'Potential SQL injection vulnerability',
                'mitigation': 'Use parameterized queries'
            },
            {
                'pattern': r'(?i)(password|pwd|pass)\s*=\s*[\'"][^\'\"]+[\'"]',
                'vulnerability_type': 'hardcoded_credentials',
                'risk_level': 'high',
                'description': 'Hardcoded credentials in SQL',
                'mitigation': 'Use environment variables or secure storage'
            }
        ]
    
    def analyze_file(self, file_content: str, filename: str = "unknown.sql", 
                    database_type: DatabaseType = DatabaseType.GENERIC) -> AnalysisResult:
        """Analyze SQL file comprehensively"""
        start_time = time.time()
        
        # Generate file hash for caching
        file_hash = hashlib.sha256(file_content.encode()).hexdigest()
        
        # Check cache
        with self._cache_lock:
            if file_hash in self._analysis_cache:
                cached_result = self._analysis_cache[file_hash]
                cached_result.processing_time = time.time() - start_time
                return cached_result
        
        try:
            # Detect database type if not specified
            if database_type == DatabaseType.GENERIC:
                database_type = self.detect_database_type(file_content)
            
            # Split into lines and statements
            lines = file_content.split('\n')
            statements = self.split_statements(file_content)
            
            # Parallel analysis
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Submit analysis tasks
                syntax_future = executor.submit(self.analyze_syntax, statements, lines, database_type)
                semantic_future = executor.submit(self.analyze_semantics, statements, lines)
                performance_future = executor.submit(self.analyze_performance, statements, lines)
                security_future = executor.submit(self.analyze_security, statements, lines)
                schema_future = executor.submit(self.analyze_schema, statements, database_type)
                
                # Collect results
                syntax_errors = syntax_future.result()
                semantic_errors = semantic_future.result()
                performance_issues = performance_future.result()
                security_vulnerabilities = security_future.result()
                tables, relationships = schema_future.result()
            
            # Generate intelligent comments
            intelligent_comments = self.generate_intelligent_comments(statements, lines)
            
            # Calculate scores
            quality_score = self.calculate_quality_score(syntax_errors, semantic_errors, performance_issues)
            complexity_score = self.calculate_complexity_score(statements)
            
            # Generate corrected SQL
            corrected_sql = self.generate_corrected_sql(file_content, syntax_errors, semantic_errors)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(
                syntax_errors, semantic_errors, performance_issues, security_vulnerabilities
            )
            
            # Create result
            result = AnalysisResult(
                file_hash=file_hash,
                processing_time=time.time() - start_time,
                database_type=database_type,
                total_lines=len(lines),
                total_statements=len(statements),
                syntax_errors=syntax_errors,
                semantic_errors=semantic_errors,
                performance_issues=performance_issues,
                security_vulnerabilities=security_vulnerabilities,
                tables=tables,
                relationships=relationships,
                quality_score=quality_score,
                complexity_score=complexity_score,
                recommendations=recommendations,
                corrected_sql=corrected_sql,
                intelligent_comments=intelligent_comments
            )
            
            # Cache result
            with self._cache_lock:
                self._analysis_cache[file_hash] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def detect_database_type(self, content: str) -> DatabaseType:
        """Detect database type from SQL content"""
        content_upper = content.upper()
        
        # Check for database-specific patterns
        if any(pattern in content_upper for pattern in ['AUTO_INCREMENT', 'ENGINE=', 'CHARSET=']):
            return DatabaseType.MYSQL
        elif any(pattern in content_upper for pattern in ['SERIAL', 'RETURNING', 'OFFSET']):
            return DatabaseType.POSTGRESQL
        elif any(pattern in content_upper for pattern in ['ROWNUM', 'CONNECT BY', 'DUAL']):
            return DatabaseType.ORACLE
        elif any(pattern in content_upper for pattern in ['IDENTITY(', 'TOP ', 'NVARCHAR']):
            return DatabaseType.SQL_SERVER
        elif 'PRAGMA' in content_upper:
            return DatabaseType.SQLITE
        else:
            return DatabaseType.GENERIC
    
    def split_statements(self, content: str) -> List[str]:
        """Split SQL content into individual statements"""
        # Remove comments first
        content = self.remove_comments(content)
        
        statements = []
        current_statement = ""
        in_string = False
        string_char = None
        
        i = 0
        while i < len(content):
            char = content[i]
            
            if not in_string:
                if char in ("'", '"'):
                    in_string = True
                    string_char = char
                elif char == ';':
                    if current_statement.strip():
                        statements.append(current_statement.strip())
                    current_statement = ""
                    i += 1
                    continue
            else:
                if char == string_char:
                    # Check if it's escaped
                    if i == 0 or content[i-1] != '\\':
                        in_string = False
                        string_char = None
            
            current_statement += char
            i += 1
        
        # Add the last statement if it exists
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [stmt for stmt in statements if stmt.strip()]
    
    def remove_comments(self, content: str) -> str:
        """Remove SQL comments from content"""
        # Remove single-line comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
    
    def analyze_syntax(self, statements: List[str], lines: List[str], 
                      database_type: DatabaseType) -> List[SQLError]:
        """Analyze syntax errors"""
        errors = []
        
        for i, statement in enumerate(statements):
            # Check parentheses balance
            open_parens = statement.count('(')
            close_parens = statement.count(')')
            if open_parens != close_parens:
                errors.append(SQLError(
                    line_number=i + 1,
                    column=0,
                    error_type='syntax_error',
                    severity='high',
                    message=f'Unmatched parentheses: {open_parens} opening, {close_parens} closing',
                    suggestion='Balance parentheses',
                    auto_fixable=False
                ))
            
            # Check for basic SQL structure
            statement_upper = statement.upper().strip()
            if statement_upper.startswith('SELECT'):
                if 'FROM' not in statement_upper and 'DUAL' not in statement_upper:
                    errors.append(SQLError(
                        line_number=i + 1,
                        column=0,
                        error_type='syntax_error',
                        severity='high',
                        message='SELECT statement missing FROM clause',
                        suggestion='Add FROM clause or use FROM DUAL for constants',
                        auto_fixable=True,
                        fixed_code=statement + ' FROM DUAL'
                    ))
            
            # Check for missing semicolon
            if i < len(statements) - 1 and not statement.rstrip().endswith(';'):
                errors.append(SQLError(
                    line_number=i + 1,
                    column=len(statement),
                    error_type='syntax_warning',
                    severity='low',
                    message='Missing semicolon at end of statement',
                    suggestion='Add semicolon (;) at the end',
                    auto_fixable=True,
                    fixed_code=statement + ';'
                ))
        
        return errors
    
    def analyze_semantics(self, statements: List[str], lines: List[str]) -> List[SQLError]:
        """Analyze semantic errors"""
        errors = []
        
        for i, statement in enumerate(statements):
            statement_upper = statement.upper()
            
            # Check for dangerous operations
            if statement_upper.startswith(('UPDATE', 'DELETE')) and 'WHERE' not in statement_upper:
                errors.append(SQLError(
                    line_number=i + 1,
                    column=0,
                    error_type='semantic_warning',
                    severity='high',
                    message='UPDATE/DELETE without WHERE clause affects all rows',
                    suggestion='Add WHERE clause to limit affected rows',
                    auto_fixable=False
                ))
            
            # Check for SELECT *
            if 'SELECT *' in statement_upper:
                errors.append(SQLError(
                    line_number=i + 1,
                    column=statement_upper.find('SELECT *'),
                    error_type='semantic_warning',
                    severity='medium',
                    message='Using SELECT * can be inefficient',
                    suggestion='Specify only the columns you need',
                    auto_fixable=False
                ))
        
        return errors

    def analyze_performance(self, statements: List[str], lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze performance issues"""
        issues = []

        for i, statement in enumerate(statements):
            statement_upper = statement.upper()

            # Check performance rules
            for rule in self.performance_rules:
                if re.search(rule['pattern'], statement):
                    issues.append({
                        'line_number': i + 1,
                        'type': rule['issue_type'],
                        'impact': rule['impact'],
                        'description': rule['description'],
                        'recommendation': rule['recommendation'],
                        'code_snippet': statement.strip()[:100] + '...' if len(statement) > 100 else statement.strip()
                    })

            # Check for missing indexes (heuristic)
            if 'WHERE' in statement_upper:
                where_columns = re.findall(r'(?i)where\s+(\w+)', statement)
                for column in where_columns:
                    issues.append({
                        'line_number': i + 1,
                        'type': 'missing_index',
                        'impact': 'high',
                        'description': f'Column "{column}" in WHERE clause may need an index',
                        'recommendation': f'Consider adding index on column "{column}"',
                        'suggested_sql': f'CREATE INDEX idx_{column} ON table_name ({column});'
                    })

        return issues

    def analyze_security(self, statements: List[str], lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze security vulnerabilities"""
        vulnerabilities = []

        for i, statement in enumerate(statements):
            # Check security rules
            for rule in self.security_rules:
                if re.search(rule['pattern'], statement):
                    vulnerabilities.append({
                        'line_number': i + 1,
                        'vulnerability_type': rule['vulnerability_type'],
                        'risk_level': rule['risk_level'],
                        'description': rule['description'],
                        'mitigation': rule['mitigation'],
                        'code_snippet': statement.strip()[:100] + '...' if len(statement) > 100 else statement.strip(),
                        'cwe_id': self.get_cwe_id(rule['vulnerability_type']),
                        'owasp_category': self.get_owasp_category(rule['vulnerability_type'])
                    })

        return vulnerabilities

    def analyze_schema(self, statements: List[str], database_type: DatabaseType) -> Tuple[List[TableInfo], List[Dict[str, Any]]]:
        """Analyze database schema"""
        tables = []
        relationships = []

        for statement in statements:
            statement_upper = statement.upper()

            # Extract CREATE TABLE statements
            if statement_upper.startswith('CREATE TABLE'):
                table_info = self.parse_create_table(statement, database_type)
                if table_info:
                    tables.append(table_info)

            # Extract foreign key relationships
            fk_matches = re.findall(r'(?i)foreign\s+key\s*\(\s*(\w+)\s*\)\s+references\s+(\w+)\s*\(\s*(\w+)\s*\)', statement)
            for fk_match in fk_matches:
                relationships.append({
                    'type': 'foreign_key',
                    'from_column': fk_match[0],
                    'to_table': fk_match[1],
                    'to_column': fk_match[2]
                })

        return tables, relationships

    def parse_create_table(self, statement: str, database_type: DatabaseType) -> Optional[TableInfo]:
        """Parse CREATE TABLE statement"""
        try:
            # Extract table name
            table_match = re.search(r'(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?(\w+)', statement)
            if not table_match:
                return None

            table_name = table_match.group(1)

            # Extract columns
            columns = []
            column_pattern = r'(\w+)\s+(\w+(?:\(\d+(?:,\s*\d+)?\))?)\s*([^,\)]*)'
            column_matches = re.findall(column_pattern, statement)

            for col_match in column_matches:
                column_info = {
                    'name': col_match[0],
                    'data_type': col_match[1],
                    'constraints': col_match[2].strip()
                }
                columns.append(column_info)

            # Extract primary keys
            pk_matches = re.findall(r'(?i)primary\s+key\s*\(\s*([^)]+)\s*\)', statement)
            primary_keys = []
            if pk_matches:
                primary_keys = [pk.strip() for pk in pk_matches[0].split(',')]

            # Extract foreign keys
            fk_matches = re.findall(r'(?i)foreign\s+key\s*\(\s*(\w+)\s*\)\s+references\s+(\w+)\s*\(\s*(\w+)\s*\)', statement)
            foreign_keys = []
            for fk_match in fk_matches:
                foreign_keys.append({
                    'column': fk_match[0],
                    'references_table': fk_match[1],
                    'references_column': fk_match[2]
                })

            return TableInfo(
                name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys,
                indexes=[],
                constraints=[]
            )

        except Exception as e:
            self.logger.error(f"Error parsing CREATE TABLE: {str(e)}")
            return None

    def generate_intelligent_comments(self, statements: List[str], lines: List[str]) -> List[Dict[str, Any]]:
        """Generate intelligent comments in Spanish"""
        comments = []

        for i, statement in enumerate(statements):
            statement_upper = statement.upper().strip()

            # Generate comments based on statement type
            if statement_upper.startswith('SELECT'):
                if 'JOIN' in statement_upper:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- Consulta con JOIN para combinar datos de múltiples tablas',
                        'type': 'explanation'
                    })
                elif 'WHERE' in statement_upper:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- Consulta SELECT con filtros WHERE para obtener datos específicos',
                        'type': 'explanation'
                    })
                else:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- Consulta SELECT básica para obtener datos',
                        'type': 'explanation'
                    })

            elif statement_upper.startswith('INSERT'):
                comments.append({
                    'line_number': i + 1,
                    'comment': '-- Inserción de nuevos registros en la tabla',
                    'type': 'explanation'
                })

            elif statement_upper.startswith('UPDATE'):
                if 'WHERE' in statement_upper:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- Actualización de registros específicos con condiciones WHERE',
                        'type': 'explanation'
                    })
                else:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- ⚠️ CUIDADO: Actualización sin WHERE afecta TODOS los registros',
                        'type': 'warning'
                    })

            elif statement_upper.startswith('DELETE'):
                if 'WHERE' in statement_upper:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- Eliminación de registros específicos con condiciones WHERE',
                        'type': 'explanation'
                    })
                else:
                    comments.append({
                        'line_number': i + 1,
                        'comment': '-- ⚠️ PELIGRO: Eliminación sin WHERE borra TODOS los registros',
                        'type': 'warning'
                    })

            elif statement_upper.startswith('CREATE TABLE'):
                comments.append({
                    'line_number': i + 1,
                    'comment': '-- Creación de nueva tabla con estructura definida',
                    'type': 'explanation'
                })

            elif statement_upper.startswith('CREATE INDEX'):
                comments.append({
                    'line_number': i + 1,
                    'comment': '-- Creación de índice para mejorar el rendimiento de consultas',
                    'type': 'optimization'
                })

        return comments

    def calculate_quality_score(self, syntax_errors: List[SQLError], semantic_errors: List[SQLError],
                               performance_issues: List[Dict[str, Any]]) -> int:
        """Calculate overall quality score (0-100)"""
        base_score = 100

        # Deduct points for errors
        for error in syntax_errors:
            if error.severity == 'high':
                base_score -= 15
            elif error.severity == 'medium':
                base_score -= 10
            else:
                base_score -= 5

        for error in semantic_errors:
            if error.severity == 'high':
                base_score -= 12
            elif error.severity == 'medium':
                base_score -= 8
            else:
                base_score -= 4

        # Deduct points for performance issues
        for issue in performance_issues:
            if issue.get('impact') == 'high':
                base_score -= 8
            elif issue.get('impact') == 'medium':
                base_score -= 5
            else:
                base_score -= 3

        return max(0, base_score)

    def calculate_complexity_score(self, statements: List[str]) -> int:
        """Calculate complexity score (0-100)"""
        total_complexity = 0

        for statement in statements:
            statement_upper = statement.upper()
            complexity = 10  # Base complexity

            # Add complexity for various SQL features
            complexity += statement_upper.count('JOIN') * 5
            complexity += statement_upper.count('UNION') * 8
            complexity += (statement_upper.count('SELECT') - 1) * 10  # Subqueries
            complexity += statement_upper.count('CASE') * 6
            complexity += statement_upper.count('GROUP BY') * 4
            complexity += statement_upper.count('HAVING') * 5
            complexity += statement_upper.count('ORDER BY') * 3
            complexity += statement_upper.count('WINDOW') * 12

            total_complexity += complexity

        # Normalize to 0-100 scale
        avg_complexity = total_complexity / len(statements) if statements else 0
        return min(100, int(avg_complexity))

    def generate_corrected_sql(self, original_sql: str, syntax_errors: List[SQLError],
                              semantic_errors: List[SQLError]) -> str:
        """Generate corrected SQL with auto-fixes applied"""
        corrected_sql = original_sql

        # Apply auto-fixes for syntax errors
        for error in syntax_errors:
            if error.auto_fixable and error.fixed_code:
                # Simple replacement for demonstration
                # In a real implementation, this would be more sophisticated
                corrected_sql = corrected_sql.replace(
                    error.fixed_code.replace(';', '').strip(),
                    error.fixed_code
                )

        return corrected_sql

    def generate_recommendations(self, syntax_errors: List[SQLError], semantic_errors: List[SQLError],
                               performance_issues: List[Dict[str, Any]],
                               security_vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []

        if syntax_errors:
            recommendations.append("Corregir errores de sintaxis para asegurar la ejecución correcta")

        if semantic_errors:
            recommendations.append("Revisar advertencias semánticas para mejorar la lógica del código")

        if performance_issues:
            recommendations.append("Implementar optimizaciones de rendimiento sugeridas")
            if any(issue.get('type') == 'select_star' for issue in performance_issues):
                recommendations.append("Especificar columnas específicas en lugar de usar SELECT *")
            if any(issue.get('type') == 'missing_index' for issue in performance_issues):
                recommendations.append("Agregar índices en columnas frecuentemente consultadas")

        if security_vulnerabilities:
            recommendations.append("Abordar vulnerabilidades de seguridad identificadas")
            if any(vuln.get('vulnerability_type') == 'sql_injection' for vuln in security_vulnerabilities):
                recommendations.append("Usar consultas parametrizadas para prevenir inyección SQL")

        # General recommendations
        recommendations.extend([
            "Usar nombres descriptivos para tablas y columnas",
            "Agregar comentarios para explicar lógica compleja",
            "Implementar manejo adecuado de errores",
            "Realizar pruebas exhaustivas antes del despliegue",
            "Mantener copias de seguridad regulares"
        ])

        return recommendations

    def get_cwe_id(self, vulnerability_type: str) -> str:
        """Get CWE ID for vulnerability type"""
        cwe_mapping = {
            'sql_injection': 'CWE-89',
            'hardcoded_credentials': 'CWE-798',
            'information_disclosure': 'CWE-200',
            'authentication_bypass': 'CWE-287'
        }
        return cwe_mapping.get(vulnerability_type, 'CWE-Unknown')

    def get_owasp_category(self, vulnerability_type: str) -> str:
        """Get OWASP Top 10 category for vulnerability type"""
        owasp_mapping = {
            'sql_injection': 'A03:2021 – Injection',
            'hardcoded_credentials': 'A07:2021 – Identification and Authentication Failures',
            'information_disclosure': 'A01:2021 – Broken Access Control',
            'authentication_bypass': 'A07:2021 – Identification and Authentication Failures'
        }
        return owasp_mapping.get(vulnerability_type, 'A10:2021 – Server-Side Request Forgery')
