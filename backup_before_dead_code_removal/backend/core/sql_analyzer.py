"""
SQL Analyzer Principal - Arquitectura Reorganizada
Analizador SQL completo con todos los módulos integrados
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .error_detector import ErrorDetector
from .performance_analyzer import PerformanceAnalyzer
from .security_analyzer import SecurityAnalyzer
from ..utils.sql_utils import SQLUtils

logger = logging.getLogger(__name__)

class SQLAnalyzer:
    """Analizador SQL principal con arquitectura reorganizada"""
    
    def __init__(self):
        """Inicializar el analizador con todos los módulos"""
        self.error_detector = ErrorDetector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.sql_utils = SQLUtils()
        
        logger.info("SQLAnalyzer inicializado con arquitectura reorganizada")
    
    def analyze(self, content: str, filename: str = "archivo.sql") -> Dict[str, Any]:
        """
        Realizar análisis completo del contenido SQL
        
        Args:
            content: Contenido SQL a analizar
            filename: Nombre del archivo
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            logger.info(f"Iniciando análisis completo de {filename}")
            
            # Estadísticas básicas
            statistics = self._calculate_statistics(content)
            
            # Análisis de errores
            error_objects = self.error_detector.analyze_sql(content)
            errors = [error.to_dict() for error in error_objects]
            
            # Análisis de esquema
            schema_info = self._analyze_schema(content)
            
            # Análisis de rendimiento
            performance_info = self.performance_analyzer.analyze(content)
            
            # Análisis de seguridad
            security_info = self.security_analyzer.analyze(content)
            
            # Calcular score de calidad
            quality_score = self._calculate_quality_score(
                errors, performance_info, security_info
            )
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(
                errors, performance_info, security_info
            )
            
            # Resultado completo
            result = {
                'filename': filename,
                'lines': statistics['total_lines'],
                'quality_score': quality_score,
                'statistics': statistics,
                'errors': errors,
                'schema_analysis': schema_info,
                'performance_analysis': performance_info,
                'security_analysis': security_info,
                'recommendations': recommendations,
                'summary': {
                    'total_errors': len([e for e in errors if e['severity'] == 'ERROR']),
                    'total_warnings': len([e for e in errors if e['severity'] == 'WARNING']),
                    'critical_errors': len([e for e in errors if e['severity'] == 'ERROR' and self._is_critical_error(e)]),
                    'tables_found': len(schema_info.get('tables', [])),
                    'queries_found': len(self.sql_utils.split_sql_statements(content))
                },
                'analysis_timestamp': datetime.now().isoformat(),
                'processed_successfully': True,
                'analyzer_version': '2.0_reorganized'
            }
            
            logger.info(f"Análisis completado para {filename}: {quality_score}% calidad")
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis de {filename}: {e}")
            return {
                'filename': filename,
                'error': f'Error en análisis: {str(e)}',
                'processed_successfully': False,
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _calculate_statistics(self, content: str) -> Dict[str, int]:
        """Calcular estadísticas básicas del contenido"""
        lines = content.split('\n')
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'comment_lines': len([l for l in lines if l.strip().startswith('--')]),
            'character_count': len(content),
            'sql_statements': len(self.sql_utils.split_sql_statements(content))
        }
    
    def _analyze_schema(self, content: str) -> Dict[str, Any]:
        """Analizar esquema de base de datos"""
        tables = []
        indexes = []
        views = []
        
        # Detectar tablas
        for match in re.finditer(r'CREATE\s+TABLE\s+(\w+)', content, re.IGNORECASE):
            tables.append(match.group(1).lower())
        
        # Detectar índices
        for match in re.finditer(r'CREATE\s+INDEX\s+(\w+)', content, re.IGNORECASE):
            indexes.append(match.group(1).lower())
        
        # Detectar vistas
        for match in re.finditer(r'CREATE\s+VIEW\s+(\w+)', content, re.IGNORECASE):
            views.append(match.group(1).lower())
        
        return {
            'tables': tables,
            'table_count': len(tables),
            'indexes': indexes,
            'index_count': len(indexes),
            'views': views,
            'view_count': len(views)
        }
    
    def _calculate_quality_score(self, errors: List, performance_info: Dict, security_info: Dict) -> int:
        """Calcular score de calidad general"""
        error_count = len([e for e in errors if e['severity'] == 'ERROR'])
        warning_count = len([e for e in errors if e['severity'] == 'WARNING'])
        
        # Penalizaciones
        error_penalty = error_count * 20
        warning_penalty = warning_count * 10
        performance_penalty = (100 - performance_info.get('performance_score', 100)) * 0.3
        security_penalty = (100 - security_info.get('security_score', 100)) * 0.5
        
        total_penalty = error_penalty + warning_penalty + performance_penalty + security_penalty
        quality_score = max(0, 100 - total_penalty)
        
        return int(quality_score)
    
    def _generate_recommendations(self, errors: List, performance_info: Dict, security_info: Dict) -> List[Dict[str, str]]:
        """Generar recomendaciones de mejora"""
        recommendations = []
        
        # Recomendaciones por errores
        if any('WHERE' in e.get('message', '') for e in errors):
            recommendations.append({
                'title': 'Usar cláusulas WHERE',
                'description': 'Siempre use WHERE en UPDATE y DELETE para evitar modificaciones masivas',
                'priority': 'HIGH',
                'type': 'safety'
            })
        
        # Recomendaciones por rendimiento
        if performance_info.get('performance_score', 100) < 80:
            recommendations.append({
                'title': 'Optimizar consultas',
                'description': 'Evite SELECT * y agregue índices apropiados',
                'priority': 'MEDIUM',
                'type': 'performance'
            })
        
        # Recomendaciones por seguridad
        if security_info.get('security_score', 100) < 90:
            recommendations.append({
                'title': 'Mejorar seguridad',
                'description': 'Revise comparaciones NULL y operaciones peligrosas',
                'priority': 'HIGH',
                'type': 'security'
            })
        
        return recommendations
    
    def _is_critical_error(self, error: Dict) -> bool:
        """Determinar si un error es crítico"""
        critical_keywords = ['DELETE', 'UPDATE', 'DROP', 'TRUNCATE']
        message = error.get('message', '').upper()
        return any(keyword in message for keyword in critical_keywords)
