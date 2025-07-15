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
