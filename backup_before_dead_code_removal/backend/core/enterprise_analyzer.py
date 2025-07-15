"""
Enterprise-Grade SQL Analysis Engine
Real SQL parsing and comprehensive database analysis
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlparse
from sqlparse import sql, tokens as T

from .database_engines import DatabaseEngine, database_registry
from .error_detector import ErrorDetector, SQLError, ErrorSeverity
from .performance_analyzer import PerformanceAnalyzer
from .security_analyzer import SecurityAnalyzer

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analysis to perform"""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SCHEMA = "schema"
    DATA_QUALITY = "data_quality"
    COMPLIANCE = "compliance"

@dataclass
class TableInfo:
    """Database table information"""
    name: str
    columns: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    row_count_estimate: Optional[int] = None
    size_estimate: Optional[str] = None
    last_updated: Optional[str] = None

@dataclass
class SchemaInfo:
    """Database schema information"""
    database_name: str
    tables: List[TableInfo]
    views: List[Dict[str, Any]]
    procedures: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]

@dataclass
class AnalysisResult:
    """Comprehensive analysis result"""
    database_engine: DatabaseEngine
    analysis_types: List[AnalysisType]
    schema_info: Optional[SchemaInfo]
    syntax_errors: List[SQLError]
    semantic_errors: List[SQLError]
    performance_issues: List[Dict[str, Any]]
    security_vulnerabilities: List[Dict[str, Any]]
    data_quality_issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    corrected_sql: Optional[str]
    confidence_score: float
    processing_time: float

class EnterpriseAnalyzer:
    """Enterprise-grade SQL analysis engine"""
    
    def __init__(self):
        """Initialize the enterprise analyzer"""
        self.error_detector = ErrorDetector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.database_registry = database_registry
        
        # SQL parsing configuration
        self.parser_config = {}
        
        logger.info("EnterpriseAnalyzer initialized with real SQL parsing")
    
    def analyze_comprehensive(self, sql_content: str, 
                            database_engine: DatabaseEngine = DatabaseEngine.AUTO_DETECT,
                            analysis_types: List[AnalysisType] = None,
                            connection_string: str = "") -> AnalysisResult:
        """
        Perform comprehensive SQL analysis
        
        Args:
            sql_content: SQL code to analyze
            database_engine: Target database engine
            analysis_types: Types of analysis to perform
            connection_string: Database connection string for context
            
        Returns:
            Comprehensive analysis result
        """
        import time
        start_time = time.time()
        
        # Auto-detect database engine if needed
        if database_engine == DatabaseEngine.AUTO_DETECT:
            database_engine = self.database_registry.detect_database_engine(
                sql_content, connection_string
            )
        
        # Default analysis types
        if analysis_types is None:
            analysis_types = [
                AnalysisType.SYNTAX,
                AnalysisType.SEMANTIC,
                AnalysisType.PERFORMANCE,
                AnalysisType.SECURITY
            ]
        
        logger.info(f"Starting comprehensive analysis for {database_engine.value}")
        
        # Parse SQL content
        parsed_statements = self._parse_sql_content(sql_content)
        
        # Initialize result
        result = AnalysisResult(
            database_engine=database_engine,
            analysis_types=analysis_types,
            schema_info=None,
            syntax_errors=[],
            semantic_errors=[],
            performance_issues=[],
            security_vulnerabilities=[],
            data_quality_issues=[],
            recommendations=[],
            corrected_sql=None,
            confidence_score=0.0,
            processing_time=0.0
        )
        
        try:
            # Syntax analysis
            if AnalysisType.SYNTAX in analysis_types:
                result.syntax_errors = self._analyze_syntax(sql_content, parsed_statements, database_engine)
            
            # Semantic analysis
            if AnalysisType.SEMANTIC in analysis_types:
                result.semantic_errors = self._analyze_semantics(sql_content, parsed_statements, database_engine)
            
            # Performance analysis
            if AnalysisType.PERFORMANCE in analysis_types:
                result.performance_issues = self._analyze_performance(sql_content, parsed_statements, database_engine)
            
            # Security analysis
            if AnalysisType.SECURITY in analysis_types:
                result.security_vulnerabilities = self._analyze_security(sql_content, parsed_statements, database_engine)
            
            # Schema analysis
            if AnalysisType.SCHEMA in analysis_types:
                result.schema_info = self._analyze_schema(sql_content, parsed_statements, database_engine)
            
            # Data quality analysis
            if AnalysisType.DATA_QUALITY in analysis_types:
                result.data_quality_issues = self._analyze_data_quality(sql_content, parsed_statements, database_engine)
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            # Generate corrected SQL
            result.corrected_sql = self._generate_corrected_sql(sql_content, result)
            
            # Calculate confidence score
            result.confidence_score = self._calculate_confidence_score(result)
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            result.syntax_errors.append(SQLError(
                error_id="analysis_error",
                message=f"Error durante el análisis: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                category="internal_error",
                location=None,
                fixes=[],
                confidence_score=1.0,
                correction_summary="Error interno del analizador"
            ))
        
        result.processing_time = time.time() - start_time
        logger.info(f"Analysis completed in {result.processing_time:.2f}s")
        
        return result
    
    def _parse_sql_content(self, sql_content: str) -> List[sql.Statement]:
        """Parse SQL content using sqlparse"""
        try:
            # Parse the SQL content
            parsed = sqlparse.parse(sql_content, **self.parser_config)
            
            # Filter out empty statements
            statements = [stmt for stmt in parsed if str(stmt).strip()]
            
            logger.info(f"Parsed {len(statements)} SQL statements")
            return statements
            
        except Exception as e:
            logger.error(f"SQL parsing error: {e}")
            return []
    
    def _analyze_syntax(self, sql_content: str, parsed_statements: List[sql.Statement], 
                       database_engine: DatabaseEngine) -> List[SQLError]:
        """Analyze syntax using real SQL parsing"""
        errors = []
        
        try:
            # Use the error detector for basic syntax analysis
            basic_errors = self.error_detector.analyze_sql(sql_content)
            errors.extend(basic_errors)
            
            # Advanced syntax analysis using parsed statements
            for i, statement in enumerate(parsed_statements):
                statement_errors = self._analyze_statement_syntax(statement, i + 1, database_engine)
                errors.extend(statement_errors)
            
            logger.info(f"Syntax analysis found {len(errors)} errors")
            
        except Exception as e:
            logger.error(f"Syntax analysis error: {e}")
        
        return errors
    
    def _analyze_statement_syntax(self, statement: sql.Statement, stmt_num: int, 
                                 database_engine: DatabaseEngine) -> List[SQLError]:
        """Analyze syntax of individual statement"""
        errors = []
        
        try:
            # Get database-specific info
            db_info = self.database_registry.get_database_info(database_engine)
            if not db_info:
                return errors
            
            # Check for database-specific syntax issues
            statement_str = str(statement).strip()
            
            # Check reserved words usage
            tokens = list(statement.flatten())
            for token in tokens:
                if token.ttype is T.Name and token.value.upper() in db_info.features.reserved_words:
                    errors.append(SQLError(
                        error_id=f"reserved_word_{stmt_num}",
                        message=f"'{token.value}' es una palabra reservada en {database_engine.value}",
                        severity=ErrorSeverity.MEDIUM,
                        category="syntax_reserved_word",
                        location=None,
                        fixes=[],
                        confidence_score=0.9,
                        correction_summary=f"Usar comillas para el identificador '{token.value}'"
                    ))
            
            # Check identifier length
            for token in tokens:
                if token.ttype is T.Name and len(token.value) > db_info.features.max_identifier_length:
                    errors.append(SQLError(
                        error_id=f"identifier_length_{stmt_num}",
                        message=f"Identificador '{token.value}' excede la longitud máxima de {db_info.features.max_identifier_length} caracteres",
                        severity=ErrorSeverity.HIGH,
                        category="syntax_identifier_length",
                        location=None,
                        fixes=[],
                        confidence_score=1.0,
                        correction_summary=f"Acortar el identificador '{token.value}'"
                    ))
            
        except Exception as e:
            logger.error(f"Statement syntax analysis error: {e}")
        
        return errors
    
    def _analyze_semantics(self, sql_content: str, parsed_statements: List[sql.Statement], 
                          database_engine: DatabaseEngine) -> List[SQLError]:
        """Analyze semantic issues"""
        errors = []
        
        try:
            # Extract table and column references
            table_refs = self._extract_table_references(parsed_statements)
            column_refs = self._extract_column_references(parsed_statements)
            
            # Check for common semantic issues
            for statement in parsed_statements:
                # Check for SELECT without FROM (except for database-specific cases)
                if self._is_select_statement(statement) and not self._has_from_clause(statement):
                    if database_engine not in [DatabaseEngine.MYSQL, DatabaseEngine.SQLITE]:
                        errors.append(SQLError(
                            error_id="select_without_from",
                            message="SELECT sin cláusula FROM no es válido en este motor de base de datos",
                            severity=ErrorSeverity.HIGH,
                            category="semantic_missing_from",
                            location=None,
                            fixes=[],
                            confidence_score=0.8,
                            correction_summary="Agregar cláusula FROM o usar tabla dual"
                        ))
            
            logger.info(f"Semantic analysis found {len(errors)} errors")
            
        except Exception as e:
            logger.error(f"Semantic analysis error: {e}")
        
        return errors
    
    def _analyze_performance(self, sql_content: str, parsed_statements: List[sql.Statement], 
                           database_engine: DatabaseEngine) -> List[Dict[str, Any]]:
        """Analyze performance issues"""
        issues = []
        
        try:
            # Use the performance analyzer
            perf_result = self.performance_analyzer.analyze(sql_content)
            
            # Convert to standard format
            if isinstance(perf_result, dict) and 'issues' in perf_result:
                issues = perf_result['issues']
            
            # Additional performance analysis using parsed statements
            for statement in parsed_statements:
                statement_issues = self._analyze_statement_performance(statement, database_engine)
                issues.extend(statement_issues)
            
            logger.info(f"Performance analysis found {len(issues)} issues")
            
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
        
        return issues
    
    def _analyze_statement_performance(self, statement: sql.Statement, 
                                     database_engine: DatabaseEngine) -> List[Dict[str, Any]]:
        """Analyze performance of individual statement"""
        issues = []
        
        try:
            statement_str = str(statement).upper()
            
            # Check for SELECT *
            if 'SELECT *' in statement_str:
                issues.append({
                    'type': 'select_star',
                    'severity': 'medium',
                    'message': 'SELECT * puede impactar el rendimiento',
                    'recommendation': 'Especificar columnas exactas en lugar de usar *',
                    'confidence': 0.8
                })
            
            # Check for missing WHERE clause in UPDATE/DELETE
            if ('UPDATE ' in statement_str or 'DELETE ' in statement_str) and 'WHERE ' not in statement_str:
                issues.append({
                    'type': 'missing_where',
                    'severity': 'high',
                    'message': 'UPDATE/DELETE sin WHERE puede afectar todas las filas',
                    'recommendation': 'Agregar cláusula WHERE para limitar el alcance',
                    'confidence': 0.9
                })
            
            # Check for LIKE with leading wildcard
            if re.search(r"LIKE\s+['\"]%", statement_str):
                issues.append({
                    'type': 'leading_wildcard',
                    'severity': 'medium',
                    'message': 'LIKE con wildcard inicial impide el uso de índices',
                    'recommendation': 'Evitar wildcards al inicio del patrón LIKE',
                    'confidence': 0.7
                })
            
        except Exception as e:
            logger.error(f"Statement performance analysis error: {e}")
        
        return issues
    
    def _analyze_security(self, sql_content: str, parsed_statements: List[sql.Statement], 
                         database_engine: DatabaseEngine) -> List[Dict[str, Any]]:
        """Analyze security vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Use the security analyzer
            sec_result = self.security_analyzer.analyze(sql_content)
            
            # Convert to standard format
            if isinstance(sec_result, dict) and 'vulnerabilities' in sec_result:
                vulnerabilities = sec_result['vulnerabilities']
            
            logger.info(f"Security analysis found {len(vulnerabilities)} vulnerabilities")
            
        except Exception as e:
            logger.error(f"Security analysis error: {e}")
        
        return vulnerabilities
    
    def _analyze_schema(self, sql_content: str, parsed_statements: List[sql.Statement], 
                       database_engine: DatabaseEngine) -> Optional[SchemaInfo]:
        """Analyze and extract schema information"""
        try:
            tables = []
            views = []
            procedures = []
            
            for statement in parsed_statements:
                if self._is_create_table_statement(statement):
                    table_info = self._extract_table_info(statement)
                    if table_info:
                        tables.append(table_info)
                
                elif self._is_create_view_statement(statement):
                    view_info = self._extract_view_info(statement)
                    if view_info:
                        views.append(view_info)
            
            if tables or views or procedures:
                return SchemaInfo(
                    database_name="analyzed_database",
                    tables=tables,
                    views=views,
                    procedures=procedures,
                    functions=[],
                    triggers=[],
                    indexes=[]
                )
            
        except Exception as e:
            logger.error(f"Schema analysis error: {e}")
        
        return None
    
    def _analyze_data_quality(self, sql_content: str, parsed_statements: List[sql.Statement], 
                            database_engine: DatabaseEngine) -> List[Dict[str, Any]]:
        """Analyze data quality issues"""
        issues = []
        
        try:
            for statement in parsed_statements:
                # Check for potential data quality issues
                statement_str = str(statement).upper()
                
                # Check for missing NOT NULL constraints
                if 'CREATE TABLE' in statement_str and 'NOT NULL' not in statement_str:
                    issues.append({
                        'type': 'missing_not_null',
                        'severity': 'low',
                        'message': 'Considerar agregar restricciones NOT NULL para mejorar la calidad de datos',
                        'recommendation': 'Evaluar qué columnas deberían ser NOT NULL',
                        'confidence': 0.6
                    })
                
                # Check for missing primary keys
                if 'CREATE TABLE' in statement_str and 'PRIMARY KEY' not in statement_str:
                    issues.append({
                        'type': 'missing_primary_key',
                        'severity': 'medium',
                        'message': 'Tabla sin clave primaria puede causar problemas de integridad',
                        'recommendation': 'Agregar una clave primaria a la tabla',
                        'confidence': 0.8
                    })
            
            logger.info(f"Data quality analysis found {len(issues)} issues")
            
        except Exception as e:
            logger.error(f"Data quality analysis error: {e}")
        
        return issues

    def _generate_recommendations(self, result: AnalysisResult) -> List[Dict[str, Any]]:
        """Generate intelligent recommendations based on analysis results"""
        recommendations = []

        try:
            # Syntax error recommendations
            if result.syntax_errors:
                high_severity_errors = [e for e in result.syntax_errors if e.severity == ErrorSeverity.HIGH]
                if high_severity_errors:
                    recommendations.append({
                        'type': 'syntax_errors',
                        'priority': 'high',
                        'title': 'Corregir Errores de Sintaxis Críticos',
                        'message': f'Se encontraron {len(high_severity_errors)} errores de sintaxis de alta severidad que impiden la ejecución',
                        'action': 'Revisar y corregir los errores marcados en rojo',
                        'impact': 'Crítico - El código no se ejecutará correctamente'
                    })

            # Performance recommendations
            if result.performance_issues:
                select_star_issues = [i for i in result.performance_issues if i.get('type') == 'select_star']
                if select_star_issues:
                    recommendations.append({
                        'type': 'performance',
                        'priority': 'medium',
                        'title': 'Optimizar Consultas SELECT',
                        'message': f'Se encontraron {len(select_star_issues)} consultas usando SELECT *',
                        'action': 'Especificar columnas exactas en lugar de usar SELECT *',
                        'impact': 'Medio - Mejorará el rendimiento y reducirá el uso de memoria'
                    })

            # Security recommendations
            if result.security_vulnerabilities:
                injection_vulns = [v for v in result.security_vulnerabilities if 'injection' in v.get('type', '')]
                if injection_vulns:
                    recommendations.append({
                        'type': 'security',
                        'priority': 'critical',
                        'title': 'Corregir Vulnerabilidades de Seguridad',
                        'message': f'Se detectaron {len(injection_vulns)} posibles vulnerabilidades de inyección SQL',
                        'action': 'Usar consultas parametrizadas y validar todas las entradas',
                        'impact': 'Crítico - Riesgo de seguridad alto'
                    })

            # Data quality recommendations
            if result.data_quality_issues:
                missing_pk_issues = [i for i in result.data_quality_issues if i.get('type') == 'missing_primary_key']
                if missing_pk_issues:
                    recommendations.append({
                        'type': 'data_quality',
                        'priority': 'medium',
                        'title': 'Mejorar Integridad de Datos',
                        'message': f'Se encontraron {len(missing_pk_issues)} tablas sin clave primaria',
                        'action': 'Agregar claves primarias a todas las tablas',
                        'impact': 'Medio - Mejorará la integridad y rendimiento de la base de datos'
                    })

            # Sort recommendations by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        return recommendations

    def _generate_corrected_sql(self, original_sql: str, result: AnalysisResult) -> Optional[str]:
        """Generate corrected SQL based on analysis results"""
        try:
            corrected_sql = original_sql

            # Apply basic corrections for common issues
            for error in result.syntax_errors:
                if error.fixes:
                    # Apply the first fix with highest confidence
                    best_fix = max(error.fixes, key=lambda f: f.confidence)
                    if best_fix.confidence > 0.7:
                        corrected_sql = corrected_sql.replace(
                            best_fix.original_text,
                            best_fix.suggested_text
                        )

            # Add comments for performance improvements
            if result.performance_issues:
                corrected_sql = f"-- SQL Analyzer Enterprise - Versión Optimizada\n-- Se detectaron {len(result.performance_issues)} problemas de rendimiento\n\n{corrected_sql}"

            return corrected_sql if corrected_sql != original_sql else None

        except Exception as e:
            logger.error(f"Error generating corrected SQL: {e}")
            return None

    def _calculate_confidence_score(self, result: AnalysisResult) -> float:
        """Calculate overall confidence score for the analysis"""
        try:
            total_score = 0.0
            weight_sum = 0.0

            # Syntax analysis confidence (weight: 0.3)
            if result.syntax_errors:
                syntax_confidence = sum(e.confidence_score for e in result.syntax_errors) / len(result.syntax_errors)
                total_score += syntax_confidence * 0.3
                weight_sum += 0.3

            # Performance analysis confidence (weight: 0.25)
            if result.performance_issues:
                perf_confidence = sum(i.get('confidence', 0.5) for i in result.performance_issues) / len(result.performance_issues)
                total_score += perf_confidence * 0.25
                weight_sum += 0.25

            # Security analysis confidence (weight: 0.25)
            if result.security_vulnerabilities:
                sec_confidence = sum(v.get('confidence', 0.5) for v in result.security_vulnerabilities) / len(result.security_vulnerabilities)
                total_score += sec_confidence * 0.25
                weight_sum += 0.25

            # Data quality confidence (weight: 0.2)
            if result.data_quality_issues:
                dq_confidence = sum(i.get('confidence', 0.5) for i in result.data_quality_issues) / len(result.data_quality_issues)
                total_score += dq_confidence * 0.2
                weight_sum += 0.2

            # Return weighted average or default high confidence if no issues found
            return total_score / weight_sum if weight_sum > 0 else 0.95

        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5

    # Helper methods for SQL parsing

    def _extract_table_references(self, parsed_statements: List[sql.Statement]) -> List[str]:
        """Extract table references from parsed statements"""
        tables = []
        try:
            for statement in parsed_statements:
                for token in statement.flatten():
                    if token.ttype is T.Name and self._is_table_reference(token, statement):
                        tables.append(token.value)
        except Exception as e:
            logger.error(f"Error extracting table references: {e}")
        return list(set(tables))

    def _extract_column_references(self, parsed_statements: List[sql.Statement]) -> List[str]:
        """Extract column references from parsed statements"""
        columns = []
        try:
            for statement in parsed_statements:
                for token in statement.flatten():
                    if token.ttype is T.Name and self._is_column_reference(token, statement):
                        columns.append(token.value)
        except Exception as e:
            logger.error(f"Error extracting column references: {e}")
        return list(set(columns))

    def _is_select_statement(self, statement: sql.Statement) -> bool:
        """Check if statement is a SELECT statement"""
        return str(statement).strip().upper().startswith('SELECT')

    def _has_from_clause(self, statement: sql.Statement) -> bool:
        """Check if SELECT statement has FROM clause"""
        return 'FROM' in str(statement).upper()

    def _is_create_table_statement(self, statement: sql.Statement) -> bool:
        """Check if statement is CREATE TABLE"""
        return 'CREATE TABLE' in str(statement).upper()

    def _is_create_view_statement(self, statement: sql.Statement) -> bool:
        """Check if statement is CREATE VIEW"""
        return 'CREATE VIEW' in str(statement).upper()

    def _is_table_reference(self, token: sql.Token, statement: sql.Statement) -> bool:
        """Determine if token is a table reference"""
        # Simplified logic - in real implementation, this would be more sophisticated
        statement_str = str(statement).upper()
        token_pos = statement_str.find(token.value.upper())

        # Check if token appears after FROM, JOIN, INTO, UPDATE
        keywords = ['FROM ', 'JOIN ', 'INTO ', 'UPDATE ']
        for keyword in keywords:
            keyword_pos = statement_str.find(keyword)
            if keyword_pos != -1 and token_pos > keyword_pos:
                return True

        return False

    def _is_column_reference(self, token: sql.Token, statement: sql.Statement) -> bool:
        """Determine if token is a column reference"""
        # Simplified logic - in real implementation, this would be more sophisticated
        statement_str = str(statement).upper()

        # Basic heuristic: if it's after SELECT, WHERE, ORDER BY, GROUP BY
        keywords = ['SELECT ', 'WHERE ', 'ORDER BY ', 'GROUP BY ']
        for keyword in keywords:
            if keyword in statement_str:
                return True

        return False

    def _extract_table_info(self, statement: sql.Statement) -> Optional[TableInfo]:
        """Extract table information from CREATE TABLE statement"""
        try:
            statement_str = str(statement)

            # Extract table name (simplified)
            table_name_match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement_str, re.IGNORECASE)
            if not table_name_match:
                return None

            table_name = table_name_match.group(1)

            # Extract columns (simplified)
            columns = []
            column_matches = re.findall(r'(\w+)\s+(\w+(?:\(\d+\))?)', statement_str, re.IGNORECASE)
            for col_name, col_type in column_matches:
                columns.append({
                    'name': col_name,
                    'type': col_type,
                    'nullable': 'NOT NULL' not in statement_str.upper(),
                    'default': None
                })

            return TableInfo(
                name=table_name,
                columns=columns,
                indexes=[],
                constraints=[],
                triggers=[],
                relationships=[]
            )

        except Exception as e:
            logger.error(f"Error extracting table info: {e}")
            return None

    def _extract_view_info(self, statement: sql.Statement) -> Optional[Dict[str, Any]]:
        """Extract view information from CREATE VIEW statement"""
        try:
            statement_str = str(statement)

            # Extract view name (simplified)
            view_name_match = re.search(r'CREATE\s+VIEW\s+(\w+)', statement_str, re.IGNORECASE)
            if not view_name_match:
                return None

            return {
                'name': view_name_match.group(1),
                'definition': statement_str,
                'columns': [],
                'dependencies': []
            }

        except Exception as e:
            logger.error(f"Error extracting view info: {e}")
            return None
