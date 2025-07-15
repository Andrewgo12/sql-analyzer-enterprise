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
    
