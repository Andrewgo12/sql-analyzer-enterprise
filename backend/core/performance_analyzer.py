"""
Analizador de Rendimiento SQL - Módulo Reorganizado
Detecta problemas de rendimiento y optimización
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analizador de rendimiento SQL especializado"""
    
    def __init__(self):
        """Inicializar analizador de rendimiento"""
        self.performance_patterns = [
            # Problemas de rendimiento críticos
            (r'SELECT\s+\*\s+FROM\s+\w+\s*;', 'SELECT * puede impactar el rendimiento', 'high'),
            (r'SELECT\s+.*\s+FROM\s+\w+\s*;', 'Query sin WHERE puede ser lenta en tablas grandes', 'medium'),
            (r'ORDER\s+BY\s+.*\s+LIMIT\s+\d+', 'ORDER BY con LIMIT puede ser ineficiente sin índices', 'medium'),
            (r'LIKE\s+[\'"]%.*%[\'"]', 'LIKE con wildcard inicial previene uso de índices', 'medium'),
            (r'OR\s+.*\s+OR', 'Múltiples OR pueden ser ineficientes', 'low'),
            (r'DISTINCT\s+.*\s+ORDER\s+BY', 'DISTINCT con ORDER BY puede ser costoso', 'medium'),
        ]
        
        logger.info("PerformanceAnalyzer inicializado")
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analizar rendimiento del contenido SQL
        
        Args:
            content: Contenido SQL a analizar
            
        Returns:
            Diccionario con análisis de rendimiento
        """
        try:
            issues = []
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line_clean = line.strip()
                if not line_clean or line_clean.startswith('--'):
                    continue
                
                # Verificar patrones de rendimiento
                line_issues = self._check_performance_patterns(line_clean, line_num)
                issues.extend(line_issues)
            
            # Análisis estructural
            structural_issues = self._analyze_structure(content)
            issues.extend(structural_issues)
            
            # Calcular score de rendimiento
            performance_score = self._calculate_performance_score(issues)
            
            result = {
                'issues': issues,
                'total_issues': len(issues),
                'performance_score': performance_score,
                'recommendations': self._generate_performance_recommendations(issues)
            }
            
            logger.info(f"Análisis de rendimiento completado: {len(issues)} problemas encontrados")
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis de rendimiento: {e}")
            return {
                'issues': [],
                'total_issues': 0,
                'performance_score': 100,
                'recommendations': []
            }
    
    def _check_performance_patterns(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """Verificar patrones de rendimiento en una línea"""
        issues = []
        line_upper = line.upper()
        
        for pattern, message, severity in self.performance_patterns:
            if re.search(pattern, line_upper, re.IGNORECASE):
                issues.append({
                    'line': line_num,
                    'type': 'performance',
                    'message': message,
                    'severity': severity,
                    'code': line[:80] + '...' if len(line) > 80 else line,
                    'pattern': pattern
                })
        
        return issues
    
    def _analyze_structure(self, content: str) -> List[Dict[str, Any]]:
        """Analizar estructura general para problemas de rendimiento"""
        issues = []
        content_upper = content.upper()
        
        # Verificar subconsultas anidadas
        subquery_count = content_upper.count('SELECT')
        if subquery_count > 3:
            issues.append({
                'line': 1,
                'type': 'structure',
                'message': f'Múltiples subconsultas ({subquery_count}) pueden impactar el rendimiento',
                'severity': 'medium',
                'code': 'Estructura general'
            })
        
        # Verificar JOINs múltiples
        join_count = len(re.findall(r'\bJOIN\b', content_upper))
        if join_count > 5:
            issues.append({
                'line': 1,
                'type': 'structure',
                'message': f'Múltiples JOINs ({join_count}) pueden ser costosos',
                'severity': 'medium',
                'code': 'Estructura general'
            })
        
        # Verificar funciones agregadas sin GROUP BY
        if 'COUNT(' in content_upper or 'SUM(' in content_upper or 'AVG(' in content_upper:
            if 'GROUP BY' not in content_upper:
                issues.append({
                    'line': 1,
                    'type': 'structure',
                    'message': 'Funciones agregadas sin GROUP BY pueden ser ineficientes',
                    'severity': 'low',
                    'code': 'Estructura general'
                })
        
        return issues
    
    def _calculate_performance_score(self, issues: List[Dict[str, Any]]) -> int:
        """Calcular score de rendimiento basado en problemas encontrados"""
        if not issues:
            return 100
        
        # Penalizaciones por severidad
        penalty = 0
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                penalty += 25
            elif severity == 'medium':
                penalty += 15
            elif severity == 'low':
                penalty += 5
        
        # Score mínimo de 0
        score = max(0, 100 - penalty)
        return int(score)
    
    def _generate_performance_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generar recomendaciones de rendimiento"""
        recommendations = []
        
        # Agrupar problemas por tipo
        issue_types = {}
        for issue in issues:
            issue_type = issue.get('type', 'general')
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generar recomendaciones específicas
        if 'performance' in issue_types:
            perf_issues = issue_types['performance']
            high_severity = [i for i in perf_issues if i.get('severity') == 'high']
            
            if high_severity:
                recommendations.append({
                    'title': 'Optimizar consultas SELECT',
                    'description': 'Evite SELECT * y especifique solo las columnas necesarias',
                    'priority': 'HIGH',
                    'type': 'performance'
                })
        
        if 'structure' in issue_types:
            recommendations.append({
                'title': 'Revisar estructura de consultas',
                'description': 'Considere simplificar subconsultas y optimizar JOINs',
                'priority': 'MEDIUM',
                'type': 'structure'
            })
        
        # Recomendación general si hay muchos problemas
        if len(issues) > 5:
            recommendations.append({
                'title': 'Revisión general de rendimiento',
                'description': 'Se detectaron múltiples problemas de rendimiento que requieren atención',
                'priority': 'HIGH',
                'type': 'general'
            })
        
        return recommendations
    
    def get_performance_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener resumen del análisis de rendimiento"""
        issues = analysis.get('issues', [])
        
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            severity = issue.get('severity', 'low')
            severity_counts[severity] += 1
        
        return {
            'total_issues': len(issues),
            'performance_score': analysis.get('performance_score', 100),
            'severity_breakdown': severity_counts,
            'recommendations_count': len(analysis.get('recommendations', []))
        }
