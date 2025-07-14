"""
Analizador SQL principal - Arquitectura limpia
Sistema completo de análisis SQL sin dependencias problemáticas
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SQLAnalyzer:
    """Analizador SQL completo y robusto"""
    
    def __init__(self):
        """Inicializar el analizador SQL"""
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'JOIN', 'INNER', 'LEFT', 'RIGHT',
            'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'DISTINCT', 'AS', 'INTO'
        }
        
        self.data_types = {
            'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
            'VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT',
            'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL',
            'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR',
            'BOOLEAN', 'BOOL', 'BIT', 'JSON', 'UUID'
        }
        
        self.error_patterns = [
            (r'DELETE\s+FROM\s+\w+\s*;', 'DELETE sin WHERE eliminará todos los registros', 'ERROR'),
            (r'UPDATE\s+\w+\s+SET\s+.*\s*;', 'UPDATE sin WHERE actualizará todos los registros', 'ERROR'),
            (r'DROP\s+TABLE\s+\w+', 'DROP TABLE es una operación destructiva', 'WARNING'),
            (r'TRUNCATE\s+TABLE\s+\w+', 'TRUNCATE eliminará todos los datos', 'WARNING'),
            (r'=\s*NULL|!=\s*NULL|<>\s*NULL', 'Comparación incorrecta con NULL. Use IS NULL o IS NOT NULL', 'ERROR'),
            (r'SELECT\s+\*\s+FROM', 'SELECT * puede impactar el rendimiento', 'WARNING')
        ]
        
        logger.info("SQLAnalyzer inicializado correctamente")
    
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
            logger.info(f"Iniciando análisis de {filename}")
            
            # Estadísticas básicas
            lines = content.split('\n')
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])
            comment_lines = len([line for line in lines if line.strip().startswith('--')])
            
            # Análisis de errores
            errors = self._detect_errors(content)
            
            # Análisis de esquema
            schema_info = self._analyze_schema(content)
            
            # Análisis de rendimiento
            performance_info = self._analyze_performance(content)
            
            # Análisis de seguridad
            security_info = self._analyze_security(content)
            
            # Calcular score de calidad
            quality_score = self._calculate_quality_score(errors, performance_info, security_info)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(errors, performance_info, security_info)
            
            # Resultado completo
            result = {
                'filename': filename,
                'lines': total_lines,
                'quality_score': quality_score,
                'statistics': {
                    'total_lines': total_lines,
                    'non_empty_lines': non_empty_lines,
                    'comment_lines': comment_lines,
                    'character_count': len(content),
                    'sql_statements': len(self._extract_statements(content))
                },
                'errors': errors,
                'schema_analysis': schema_info,
                'performance_analysis': performance_info,
                'security_analysis': security_info,
                'recommendations': recommendations,
                'summary': {
                    'total_errors': len([e for e in errors if e['severity'] == 'ERROR']),
                    'total_warnings': len([e for e in errors if e['severity'] == 'WARNING']),
                    'critical_errors': len([e for e in errors if e['severity'] == 'ERROR' and 'DELETE' in e['message'] or 'UPDATE' in e['message']]),
                    'tables_found': len(schema_info.get('tables', [])),
                    'queries_found': len(self._extract_statements(content))
                },
                'analysis_timestamp': datetime.now().isoformat(),
                'processed_successfully': True,
                'analyzer_version': '2.0_clean'
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
    
    def _detect_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detectar errores y advertencias en el SQL"""
        errors = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith('--'):
                continue
            
            line_upper = line_clean.upper()
            
            # Aplicar patrones de error
            for pattern, message, severity in self.error_patterns:
                if re.search(pattern, line_upper, re.IGNORECASE):
                    errors.append({
                        'line': line_num,
                        'message': message,
                        'severity': severity,
                        'code': line_clean[:100] + '...' if len(line_clean) > 100 else line_clean,
                        'pattern': pattern
                    })
        
        return errors
    
    def _analyze_schema(self, content: str) -> Dict[str, Any]:
        """Analizar esquema de base de datos"""
        tables = []
        indexes = []
        
        # Detectar tablas
        table_pattern = r'CREATE\s+TABLE\s+(\w+)'
        for match in re.finditer(table_pattern, content, re.IGNORECASE):
            tables.append(match.group(1).lower())
        
        # Detectar índices
        index_pattern = r'CREATE\s+INDEX\s+(\w+)'
        for match in re.finditer(index_pattern, content, re.IGNORECASE):
            indexes.append(match.group(1).lower())
        
        return {
            'tables': tables,
            'table_count': len(tables),
            'indexes': indexes,
            'index_count': len(indexes)
        }
    
    def _analyze_performance(self, content: str) -> Dict[str, Any]:
        """Analizar problemas de rendimiento"""
        issues = []
        
        # SELECT * sin WHERE
        if re.search(r'SELECT\s+\*\s+FROM\s+\w+\s*;', content, re.IGNORECASE):
            issues.append({
                'type': 'select_star',
                'message': 'SELECT * can impact performance',
                'severity': 'medium'
            })
        
        # Consultas sin WHERE en tablas grandes
        if re.search(r'SELECT\s+.*\s+FROM\s+\w+\s*;', content, re.IGNORECASE):
            issues.append({
                'type': 'no_where_clause',
                'message': 'Query without WHERE clause may be slow',
                'severity': 'low'
            })
        
        performance_score = max(0, 100 - (len(issues) * 15))
        
        return {
            'issues': issues,
            'total_issues': len(issues),
            'performance_score': performance_score
        }
    
    def _analyze_security(self, content: str) -> Dict[str, Any]:
        """Analizar problemas de seguridad"""
        issues = []
        
        # Comparaciones NULL incorrectas
        if re.search(r'=\s*NULL|!=\s*NULL', content, re.IGNORECASE):
            issues.append({
                'type': 'null_comparison',
                'message': 'Incorrect NULL comparison detected',
                'severity': 'high'
            })
        
        # Operaciones peligrosas sin WHERE
        dangerous_ops = ['DELETE FROM', 'UPDATE', 'DROP TABLE', 'TRUNCATE']
        for op in dangerous_ops:
            if re.search(f'{op}.*(?!WHERE)', content, re.IGNORECASE):
                issues.append({
                    'type': 'dangerous_operation',
                    'message': f'Dangerous {op} operation without proper conditions',
                    'severity': 'critical'
                })
        
        security_score = max(0, 100 - (len(issues) * 20))
        
        return {
            'issues': issues,
            'total_issues': len(issues),
            'security_score': security_score
        }
    
    def _calculate_quality_score(self, errors: List, performance_info: Dict, security_info: Dict) -> int:
        """Calcular score de calidad general"""
        error_count = len([e for e in errors if e['severity'] == 'ERROR'])
        warning_count = len([e for e in errors if e['severity'] == 'WARNING'])
        
        # Penalizaciones
        error_penalty = error_count * 20
        warning_penalty = warning_count * 10
        performance_penalty = (100 - performance_info['performance_score']) * 0.3
        security_penalty = (100 - security_info['security_score']) * 0.5
        
        total_penalty = error_penalty + warning_penalty + performance_penalty + security_penalty
        quality_score = max(0, 100 - total_penalty)
        
        return int(quality_score)
    
    def _generate_recommendations(self, errors: List, performance_info: Dict, security_info: Dict) -> List[Dict[str, str]]:
        """Generar recomendaciones de mejora"""
        recommendations = []
        
        # Recomendaciones por errores
        if any('WHERE' in e['message'] for e in errors):
            recommendations.append({
                'title': 'Usar cláusulas WHERE',
                'description': 'Siempre use WHERE en UPDATE y DELETE para evitar modificaciones masivas',
                'priority': 'HIGH',
                'type': 'safety'
            })
        
        # Recomendaciones por rendimiento
        if performance_info['performance_score'] < 80:
            recommendations.append({
                'title': 'Optimizar consultas',
                'description': 'Evite SELECT * y agregue índices apropiados',
                'priority': 'MEDIUM',
                'type': 'performance'
            })
        
        # Recomendaciones por seguridad
        if security_info['security_score'] < 90:
            recommendations.append({
                'title': 'Mejorar seguridad',
                'description': 'Revise comparaciones NULL y operaciones peligrosas',
                'priority': 'HIGH',
                'type': 'security'
            })
        
        return recommendations
    
    def _extract_statements(self, content: str) -> List[str]:
        """Extraer statements SQL individuales"""
        # Dividir por punto y coma, ignorando comentarios
        statements = []
        current_statement = ""
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement += line + " "
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [s for s in statements if s]
