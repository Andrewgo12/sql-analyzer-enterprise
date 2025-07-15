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

