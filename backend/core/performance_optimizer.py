"""
SQL Performance Optimizer
Advanced performance analysis and optimization recommendations
"""

import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class OptimizationType(Enum):
    """Types of performance optimizations."""
    INDEX_RECOMMENDATION = "index_recommendation"
    QUERY_REWRITE = "query_rewrite"
    JOIN_OPTIMIZATION = "join_optimization"
    SUBQUERY_OPTIMIZATION = "subquery_optimization"
    FUNCTION_OPTIMIZATION = "function_optimization"
    PAGINATION_OPTIMIZATION = "pagination_optimization"
    CACHING_RECOMMENDATION = "caching_recommendation"


class PerformanceImpact(Enum):
    """Performance impact levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PerformanceIssue:
    """Performance issue representation."""
    type: OptimizationType
    severity: PerformanceImpact
    title: str
    description: str
    line_number: Optional[int] = None
    original_sql: Optional[str] = None
    optimized_sql: Optional[str] = None
    estimated_improvement: Optional[str] = None
    explanation: Optional[str] = None
    prerequisites: Optional[List[str]] = None


@dataclass
class IndexRecommendation:
    """Index recommendation."""
    table_name: str
    columns: List[str]
    index_type: str = "NONCLUSTERED"
    estimated_improvement: str = "50-80%"
    reason: str = ""
    create_statement: str = ""


class PerformanceOptimizer:
    """Advanced SQL performance optimizer."""
    
    def __init__(self):
        self.performance_patterns = self._initialize_performance_patterns()
        self.optimization_rules = self._initialize_optimization_rules()
    
    def _initialize_performance_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize performance anti-patterns."""
        return {
            "select_star": {
                "pattern": r"SELECT\s+\*\s+FROM",
                "severity": PerformanceImpact.MEDIUM,
                "description": "SELECT * puede transferir datos innecesarios",
                "improvement": "30-50%"
            },
            "missing_where": {
                "pattern": r"SELECT\s+.*\s+FROM\s+\w+(?!\s+WHERE)",
                "severity": PerformanceImpact.HIGH,
                "description": "Consulta sin cláusula WHERE puede causar table scan",
                "improvement": "80-95%"
            },
            "inefficient_like": {
                "pattern": r"LIKE\s+['\"]%.*['\"]",
                "severity": PerformanceImpact.HIGH,
                "description": "LIKE con wildcard al inicio impide uso de índices",
                "improvement": "60-90%"
            },
            "function_in_where": {
                "pattern": r"WHERE\s+\w+\s*\([^)]*\)\s*[=<>]",
                "severity": PerformanceImpact.HIGH,
                "description": "Funciones en WHERE impiden uso de índices",
                "improvement": "70-90%"
            },
            "or_conditions": {
                "pattern": r"WHERE\s+.*\s+OR\s+",
                "severity": PerformanceImpact.MEDIUM,
                "description": "Múltiples condiciones OR pueden ser ineficientes",
                "improvement": "40-70%"
            },
            "correlated_subquery": {
                "pattern": r"WHERE\s+.*\s+IN\s*\(\s*SELECT",
                "severity": PerformanceImpact.HIGH,
                "description": "Subconsulta correlacionada puede ser ineficiente",
                "improvement": "50-80%"
            },
            "missing_limit": {
                "pattern": r"SELECT\s+.*\s+ORDER\s+BY(?!\s+.*\s+(?:TOP|LIMIT))",
                "severity": PerformanceImpact.MEDIUM,
                "description": "ORDER BY sin LIMIT puede ser costoso",
                "improvement": "60-90%"
            },
            "cartesian_product": {
                "pattern": r"FROM\s+\w+\s*,\s*\w+(?!\s+WHERE)",
                "severity": PerformanceImpact.CRITICAL,
                "description": "Posible producto cartesiano sin condición JOIN",
                "improvement": "95-99%"
            }
        }
    
    def _initialize_optimization_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize optimization rules."""
        return {
            "index_recommendations": {
                "where_columns": "Crear índices en columnas usadas en WHERE",
                "join_columns": "Crear índices en columnas de JOIN",
                "order_by_columns": "Crear índices en columnas de ORDER BY",
                "group_by_columns": "Crear índices en columnas de GROUP BY"
            },
            "query_rewrites": {
                "exists_vs_in": "Usar EXISTS en lugar de IN para subconsultas",
                "join_vs_subquery": "Convertir subconsultas a JOINs cuando sea posible",
                "union_vs_or": "Usar UNION en lugar de OR para consultas complejas"
            }
        }
    
    def analyze_performance(self, sql_content: str) -> Dict[str, Any]:
        """Analyze SQL performance and generate optimization recommendations."""
        
        start_time = time.time()
        
        # Detect performance issues
        issues = self._detect_performance_issues(sql_content)
        
        # Generate index recommendations
        index_recommendations = self._generate_index_recommendations(sql_content)
        
        # Generate query optimizations
        query_optimizations = self._generate_query_optimizations(sql_content, issues)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(issues)
        
        analysis_time = time.time() - start_time
        
        return {
            "performance_score": performance_score,
            "analysis_time": round(analysis_time, 3),
            "issues": [self._issue_to_dict(issue) for issue in issues],
            "index_recommendations": [self._index_to_dict(idx) for idx in index_recommendations],
            "query_optimizations": query_optimizations,
            "summary": {
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.severity == PerformanceImpact.CRITICAL]),
                "high_issues": len([i for i in issues if i.severity == PerformanceImpact.HIGH]),
                "medium_issues": len([i for i in issues if i.severity == PerformanceImpact.MEDIUM]),
                "low_issues": len([i for i in issues if i.severity == PerformanceImpact.LOW]),
                "estimated_improvement": self._calculate_total_improvement(issues)
            },
            "recommendations": self._generate_general_recommendations(issues, index_recommendations)
        }
    
    def _detect_performance_issues(self, sql_content: str) -> List[PerformanceIssue]:
        """Detect performance issues in SQL content."""
        
        issues = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper().strip()
            if not line_upper or line_upper.startswith('--'):
                continue
            
            # Check each performance pattern
            for pattern_name, pattern_info in self.performance_patterns.items():
                if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                    issue = self._create_performance_issue(
                        pattern_name, pattern_info, line, line_num
                    )
                    if issue:
                        issues.append(issue)
        
        return issues
    
    def _create_performance_issue(
        self, 
        pattern_name: str, 
        pattern_info: Dict[str, Any], 
        line: str, 
        line_num: int
    ) -> Optional[PerformanceIssue]:
        """Create a performance issue from pattern match."""
        
        optimization_type = OptimizationType.QUERY_REWRITE
        if "index" in pattern_name:
            optimization_type = OptimizationType.INDEX_RECOMMENDATION
        elif "join" in pattern_name:
            optimization_type = OptimizationType.JOIN_OPTIMIZATION
        elif "subquery" in pattern_name:
            optimization_type = OptimizationType.SUBQUERY_OPTIMIZATION
        
        # Generate specific recommendations based on pattern
        optimized_sql, explanation = self._generate_optimization_for_pattern(pattern_name, line)
        
        return PerformanceIssue(
            type=optimization_type,
            severity=pattern_info["severity"],
            title=f"Problema de rendimiento: {pattern_name.replace('_', ' ').title()}",
            description=pattern_info["description"],
            line_number=line_num,
            original_sql=line.strip(),
            optimized_sql=optimized_sql,
            estimated_improvement=pattern_info["improvement"],
            explanation=explanation
        )
    
    def _generate_optimization_for_pattern(self, pattern_name: str, line: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate specific optimization for a pattern."""
        
        optimizations = {
            "select_star": (
                "SELECT column1, column2, column3 FROM table_name",
                "Especificar solo las columnas necesarias reduce la transferencia de datos y mejora el rendimiento"
            ),
            "missing_where": (
                line.strip() + " WHERE condition = value",
                "Agregar cláusulas WHERE apropiadas para filtrar datos y usar índices eficientemente"
            ),
            "inefficient_like": (
                re.sub(r"LIKE\s+['\"]%(.+)['\"]", r"LIKE '\1%'", line, flags=re.IGNORECASE),
                "Mover el wildcard al final permite el uso de índices para búsquedas más eficientes"
            ),
            "function_in_where": (
                "WHERE indexed_column = value -- En lugar de WHERE FUNCTION(column) = value",
                "Evitar funciones en columnas de WHERE permite el uso de índices"
            ),
            "correlated_subquery": (
                "-- Convertir a JOIN para mejor rendimiento\nSELECT t1.* FROM table1 t1 INNER JOIN table2 t2 ON t1.id = t2.foreign_id",
                "Los JOINs son generalmente más eficientes que las subconsultas correlacionadas"
            ),
            "missing_limit": (
                line.strip() + " LIMIT 100",
                "Agregar LIMIT para evitar procesar y transferir más datos de los necesarios"
            ),
            "cartesian_product": (
                "FROM table1 t1 INNER JOIN table2 t2 ON t1.id = t2.foreign_id",
                "Usar JOIN explícito con condiciones apropiadas para evitar productos cartesianos"
            )
        }
        
        return optimizations.get(pattern_name, (None, None))
    
    def _generate_index_recommendations(self, sql_content: str) -> List[IndexRecommendation]:
        """Generate index recommendations based on SQL analysis."""
        
        recommendations = []
        
        # Extract table and column references
        table_columns = self._extract_table_column_usage(sql_content)
        
        for table, column_usage in table_columns.items():
            # Recommend indexes for WHERE columns
            if column_usage.get("where_columns"):
                for column in column_usage["where_columns"]:
                    recommendations.append(IndexRecommendation(
                        table_name=table,
                        columns=[column],
                        index_type="NONCLUSTERED",
                        estimated_improvement="60-80%",
                        reason=f"Columna '{column}' usada frecuentemente en WHERE",
                        create_statement=f"CREATE NONCLUSTERED INDEX IX_{table}_{column} ON {table}({column})"
                    ))
            
            # Recommend indexes for JOIN columns
            if column_usage.get("join_columns"):
                for column in column_usage["join_columns"]:
                    recommendations.append(IndexRecommendation(
                        table_name=table,
                        columns=[column],
                        index_type="NONCLUSTERED",
                        estimated_improvement="70-90%",
                        reason=f"Columna '{column}' usada en JOINs",
                        create_statement=f"CREATE NONCLUSTERED INDEX IX_{table}_{column}_JOIN ON {table}({column})"
                    ))
            
            # Recommend composite indexes for ORDER BY
            if column_usage.get("order_by_columns") and len(column_usage["order_by_columns"]) > 1:
                columns = column_usage["order_by_columns"][:3]  # Limit to 3 columns
                recommendations.append(IndexRecommendation(
                    table_name=table,
                    columns=columns,
                    index_type="NONCLUSTERED",
                    estimated_improvement="80-95%",
                    reason=f"Índice compuesto para ORDER BY en {', '.join(columns)}",
                    create_statement=f"CREATE NONCLUSTERED INDEX IX_{table}_SORT ON {table}({', '.join(columns)})"
                ))
        
        return recommendations
    
    def _extract_table_column_usage(self, sql_content: str) -> Dict[str, Dict[str, List[str]]]:
        """Extract table and column usage patterns."""
        
        usage = {}
        
        # Extract WHERE clause columns
        where_matches = re.findall(r'WHERE\s+(?:(\w+)\.)?(\w+)\s*[=<>!]', sql_content, re.IGNORECASE)
        for table, column in where_matches:
            table = table or "unknown_table"
            if table not in usage:
                usage[table] = {"where_columns": [], "join_columns": [], "order_by_columns": []}
            if column not in usage[table]["where_columns"]:
                usage[table]["where_columns"].append(column)
        
        # Extract JOIN columns
        join_matches = re.findall(r'JOIN\s+(\w+).*?ON\s+(?:\w+\.)?(\w+)\s*=\s*(?:\w+\.)?(\w+)', sql_content, re.IGNORECASE)
        for table, col1, col2 in join_matches:
            if table not in usage:
                usage[table] = {"where_columns": [], "join_columns": [], "order_by_columns": []}
            for col in [col1, col2]:
                if col not in usage[table]["join_columns"]:
                    usage[table]["join_columns"].append(col)
        
        # Extract ORDER BY columns
        order_matches = re.findall(r'ORDER\s+BY\s+((?:(?:\w+\.)?(\w+)(?:\s+(?:ASC|DESC))?,?\s*)+)', sql_content, re.IGNORECASE)
        for order_clause, _ in order_matches:
            columns = re.findall(r'(?:\w+\.)?(\w+)', order_clause)
            for column in columns:
                # Assume first table mentioned for simplicity
                table = "unknown_table"
                if table not in usage:
                    usage[table] = {"where_columns": [], "join_columns": [], "order_by_columns": []}
                if column not in usage[table]["order_by_columns"]:
                    usage[table]["order_by_columns"].append(column)
        
        return usage
    
    def _generate_query_optimizations(self, sql_content: str, issues: List[PerformanceIssue]) -> List[Dict[str, Any]]:
        """Generate specific query optimizations."""
        
        optimizations = []
        
        # Check for common optimization opportunities
        if re.search(r'SELECT\s+COUNT\(\*\)\s+FROM', sql_content, re.IGNORECASE):
            optimizations.append({
                "type": "count_optimization",
                "title": "Optimización de COUNT(*)",
                "description": "Usar COUNT(1) o COUNT(column) puede ser más eficiente",
                "before": "SELECT COUNT(*) FROM table",
                "after": "SELECT COUNT(1) FROM table",
                "improvement": "10-30%"
            })
        
        if re.search(r'DISTINCT', sql_content, re.IGNORECASE):
            optimizations.append({
                "type": "distinct_optimization",
                "title": "Optimización de DISTINCT",
                "description": "Considerar usar GROUP BY en lugar de DISTINCT para mejor control",
                "before": "SELECT DISTINCT column FROM table",
                "after": "SELECT column FROM table GROUP BY column",
                "improvement": "20-40%"
            })
        
        if re.search(r'UNION(?!\s+ALL)', sql_content, re.IGNORECASE):
            optimizations.append({
                "type": "union_optimization",
                "title": "Optimización de UNION",
                "description": "Usar UNION ALL si no necesita eliminar duplicados",
                "before": "SELECT ... UNION SELECT ...",
                "after": "SELECT ... UNION ALL SELECT ...",
                "improvement": "30-60%"
            })
        
        return optimizations
    
    def _calculate_performance_score(self, issues: List[PerformanceIssue]) -> int:
        """Calculate overall performance score."""
        
        base_score = 100
        
        for issue in issues:
            if issue.severity == PerformanceImpact.CRITICAL:
                base_score -= 25
            elif issue.severity == PerformanceImpact.HIGH:
                base_score -= 15
            elif issue.severity == PerformanceImpact.MEDIUM:
                base_score -= 8
            elif issue.severity == PerformanceImpact.LOW:
                base_score -= 3
        
        return max(0, base_score)
    
    def _calculate_total_improvement(self, issues: List[PerformanceIssue]) -> str:
        """Calculate estimated total improvement."""
        
        if not issues:
            return "0%"
        
        # Extract improvement percentages and calculate average
        improvements = []
        for issue in issues:
            if issue.estimated_improvement:
                # Extract percentage range (e.g., "50-80%" -> average 65%)
                match = re.search(r'(\d+)-(\d+)%', issue.estimated_improvement)
                if match:
                    low, high = int(match.group(1)), int(match.group(2))
                    improvements.append((low + high) / 2)
        
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            return f"{avg_improvement:.0f}%"
        
        return "Variable"
    
    def _generate_general_recommendations(
        self, 
        issues: List[PerformanceIssue], 
        index_recommendations: List[IndexRecommendation]
    ) -> List[str]:
        """Generate general performance recommendations."""
        
        recommendations = []
        
        if any(issue.severity == PerformanceImpact.CRITICAL for issue in issues):
            recommendations.append("🚨 CRÍTICO: Corregir problemas críticos inmediatamente")
        
        if len(index_recommendations) > 0:
            recommendations.append(f"📊 Considerar crear {len(index_recommendations)} índices recomendados")
        
        if any("subquery" in issue.type.value for issue in issues):
            recommendations.append("🔄 Convertir subconsultas a JOINs cuando sea posible")
        
        if any("select_star" in str(issue.original_sql) for issue in issues):
            recommendations.append("📋 Especificar columnas exactas en lugar de SELECT *")
        
        recommendations.extend([
            "⚡ Implementar paginación para consultas que retornan muchos registros",
            "🔍 Monitorear planes de ejecución regularmente",
            "📈 Configurar métricas de rendimiento y alertas",
            "🧪 Probar optimizaciones en entorno de desarrollo primero"
        ])
        
        return recommendations
    
    def _issue_to_dict(self, issue: PerformanceIssue) -> Dict[str, Any]:
        """Convert performance issue to dictionary."""
        return {
            "type": issue.type.value,
            "severity": issue.severity.value,
            "title": issue.title,
            "description": issue.description,
            "line_number": issue.line_number,
            "original_sql": issue.original_sql,
            "optimized_sql": issue.optimized_sql,
            "estimated_improvement": issue.estimated_improvement,
            "explanation": issue.explanation,
            "prerequisites": issue.prerequisites
        }
    
    def _index_to_dict(self, index: IndexRecommendation) -> Dict[str, Any]:
        """Convert index recommendation to dictionary."""
        return {
            "table_name": index.table_name,
            "columns": index.columns,
            "index_type": index.index_type,
            "estimated_improvement": index.estimated_improvement,
            "reason": index.reason,
            "create_statement": index.create_statement
        }
