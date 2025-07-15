"""
Analizador de Seguridad SQL - Módulo Reorganizado
Detecta vulnerabilidades y problemas de seguridad
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Analizador de seguridad SQL especializado"""
    
    def __init__(self):
        """Inicializar analizador de seguridad"""
        self.security_patterns = [
            # Vulnerabilidades críticas
            (r'=\s*NULL|!=\s*NULL|<>\s*NULL', 'Comparación NULL incorrecta puede causar problemas', 'high'),
            (r'UNION\s+SELECT', 'UNION SELECT puede indicar intento de inyección SQL', 'high'),
            (r';\s*--', 'Comentario después de punto y coma puede indicar inyección', 'medium'),
            (r'OR\s+1\s*=\s*1', 'Patrón típico de inyección SQL detectado', 'critical'),
            (r'DROP\s+TABLE', 'Operación DROP TABLE es destructiva', 'high'),
            (r'TRUNCATE\s+TABLE', 'Operación TRUNCATE es destructiva', 'high'),
            
            # Problemas de seguridad menores
            (r'SELECT\s+.*\s+INTO\s+OUTFILE', 'SELECT INTO OUTFILE puede ser riesgoso', 'medium'),
            (r'LOAD\s+DATA', 'LOAD DATA puede ser vulnerable', 'medium'),
            (r'EXEC\s*\(', 'Ejecución dinámica puede ser peligrosa', 'high'),
        ]
        
        self.dangerous_functions = [
            'xp_cmdshell', 'sp_executesql', 'OPENROWSET', 'OPENDATASOURCE',
            'EXEC', 'EXECUTE', 'EVAL', 'SYSTEM'
        ]
        
        logger.info("SecurityAnalyzer inicializado")
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analizar seguridad del contenido SQL
        
        Args:
            content: Contenido SQL a analizar
            
        Returns:
            Diccionario con análisis de seguridad
        """
        try:
            issues = []
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line_clean = line.strip()
                if not line_clean or line_clean.startswith('--'):
                    continue
                
                # Verificar patrones de seguridad
                line_issues = self._check_security_patterns(line_clean, line_num)
                issues.extend(line_issues)
                
                # Verificar funciones peligrosas
                function_issues = self._check_dangerous_functions(line_clean, line_num)
                issues.extend(function_issues)
            
            # Análisis estructural de seguridad
            structural_issues = self._analyze_security_structure(content)
            issues.extend(structural_issues)
            
            # Calcular score de seguridad
            security_score = self._calculate_security_score(issues)
            
            result = {
                'issues': issues,
                'total_issues': len(issues),
                'security_score': security_score,
                'recommendations': self._generate_security_recommendations(issues)
            }
            
            logger.info(f"Análisis de seguridad completado: {len(issues)} problemas encontrados")
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis de seguridad: {e}")
            return {
                'issues': [],
                'total_issues': 0,
                'security_score': 100,
                'recommendations': []
            }
    
    def _check_security_patterns(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """Verificar patrones de seguridad en una línea"""
        issues = []
        line_upper = line.upper()
        
        for pattern, message, severity in self.security_patterns:
            if re.search(pattern, line_upper, re.IGNORECASE):
                issues.append({
                    'line': line_num,
                    'type': 'security_pattern',
                    'message': message,
                    'severity': severity,
                    'code': line[:80] + '...' if len(line) > 80 else line,
                    'pattern': pattern
                })
        
        return issues
    
    def _check_dangerous_functions(self, line: str, line_num: int) -> List[Dict[str, Any]]:
        """Verificar funciones peligrosas"""
        issues = []
        line_upper = line.upper()
        
        for func in self.dangerous_functions:
            if func.upper() in line_upper:
                issues.append({
                    'line': line_num,
                    'type': 'dangerous_function',
                    'message': f'Función peligrosa detectada: {func}',
                    'severity': 'critical',
                    'code': line[:80] + '...' if len(line) > 80 else line,
                    'function': func
                })
        
        return issues
    
    def _analyze_security_structure(self, content: str) -> List[Dict[str, Any]]:
        """Analizar estructura general para problemas de seguridad"""
        issues = []
        content_upper = content.upper()
        
        # Verificar operaciones sin WHERE que pueden ser peligrosas
        dangerous_ops = ['DELETE FROM', 'UPDATE']
        for op in dangerous_ops:
            # Buscar operaciones sin WHERE
            pattern = f'{op}\\s+\\w+\\s*(?!.*WHERE).*;'
            if re.search(pattern, content_upper, re.IGNORECASE):
                issues.append({
                    'line': 1,
                    'type': 'structure_security',
                    'message': f'{op} sin WHERE puede ser peligroso',
                    'severity': 'high',
                    'code': 'Estructura general'
                })
        
        # Verificar múltiples statements en una línea (posible inyección)
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if line.count(';') > 1:
                issues.append({
                    'line': line_num,
                    'type': 'structure_security',
                    'message': 'Múltiples statements en una línea pueden indicar inyección',
                    'severity': 'medium',
                    'code': line[:80] + '...' if len(line) > 80 else line
                })
        
        return issues
    
    def _calculate_security_score(self, issues: List[Dict[str, Any]]) -> int:
        """Calcular score de seguridad basado en problemas encontrados"""
        if not issues:
            return 100
        
        # Penalizaciones por severidad
        penalty = 0
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'critical':
                penalty += 40
            elif severity == 'high':
                penalty += 25
            elif severity == 'medium':
                penalty += 15
            elif severity == 'low':
                penalty += 5
        
        # Score mínimo de 0
        score = max(0, 100 - penalty)
        return int(score)
    
    def _generate_security_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generar recomendaciones de seguridad"""
        recommendations = []
        
        # Agrupar problemas por severidad
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        high_issues = [i for i in issues if i.get('severity') == 'high']
        
        if critical_issues:
            recommendations.append({
                'title': 'Vulnerabilidades críticas detectadas',
                'description': 'Se encontraron problemas de seguridad críticos que requieren atención inmediata',
                'priority': 'CRITICAL',
                'type': 'security'
            })
        
        if high_issues:
            recommendations.append({
                'title': 'Revisar operaciones peligrosas',
                'description': 'Verifique operaciones DROP, TRUNCATE y comparaciones NULL',
                'priority': 'HIGH',
                'type': 'security'
            })
        
        # Verificar tipos específicos de problemas
        has_null_comparison = any('NULL' in i.get('message', '') for i in issues)
        if has_null_comparison:
            recommendations.append({
                'title': 'Corregir comparaciones NULL',
                'description': 'Use IS NULL o IS NOT NULL en lugar de = NULL o != NULL',
                'priority': 'HIGH',
                'type': 'syntax'
            })
        
        has_dangerous_ops = any('WHERE' in i.get('message', '') for i in issues)
        if has_dangerous_ops:
            recommendations.append({
                'title': 'Agregar cláusulas WHERE',
                'description': 'Siempre use WHERE en operaciones UPDATE y DELETE',
                'priority': 'HIGH',
                'type': 'safety'
            })
        
        return recommendations
    
    def get_security_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener resumen del análisis de seguridad"""
        issues = analysis.get('issues', [])
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            severity = issue.get('severity', 'low')
            severity_counts[severity] += 1
        
        return {
            'total_issues': len(issues),
            'security_score': analysis.get('security_score', 100),
            'severity_breakdown': severity_counts,
            'recommendations_count': len(analysis.get('recommendations', [])),
            'has_critical_issues': severity_counts['critical'] > 0
        }
