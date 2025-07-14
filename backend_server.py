#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - BACKEND SERVER
Servidor Flask optimizado para React Frontend
Sistema robusto con API REST completa
"""

import os
import sys
import json
import tempfile
import logging
import re
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS para React
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Configuración
app.config.update(
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB
    SECRET_KEY='sql-analyzer-enterprise-2024',
    UPLOAD_FOLDER=tempfile.gettempdir()
)

class SQLAnalyzerBackend:
    """Analizador SQL optimizado para el backend"""
    
    def __init__(self):
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'JOIN', 'INNER', 'LEFT', 'RIGHT',
            'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'DISTINCT', 'AS'
        }
        
        self.error_patterns = [
            (r'DELETE\s+FROM\s+\w+\s*;', 'DELETE sin WHERE eliminará todos los registros', 'ERROR'),
            (r'UPDATE\s+\w+\s+SET\s+.*\s*;', 'UPDATE sin WHERE actualizará todos los registros', 'ERROR'),
            (r'DROP\s+TABLE\s+\w+', 'DROP TABLE es una operación destructiva', 'WARNING'),
            (r'TRUNCATE\s+TABLE\s+\w+', 'TRUNCATE eliminará todos los datos', 'WARNING'),
            (r'=\s*NULL|!=\s*NULL|<>\s*NULL', 'Comparación incorrecta con NULL. Use IS NULL o IS NOT NULL', 'ERROR'),
            (r'SELECT\s+\*\s+FROM', 'SELECT * puede impactar el rendimiento', 'WARNING')
        ]
        
        logger.info("SQLAnalyzerBackend inicializado")
    
    def analyze(self, content, filename="archivo.sql"):
        """Análisis completo del contenido SQL"""
        try:
            lines = content.split('\n')
            total_lines = len(lines)
            
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
            
            # Estadísticas
            statistics = {
                'total_lines': total_lines,
                'non_empty_lines': len([l for l in lines if l.strip()]),
                'comment_lines': len([l for l in lines if l.strip().startswith('--')]),
                'character_count': len(content),
                'sql_statements': len(self._extract_statements(content))
            }
            
            return {
                'filename': filename,
                'lines': total_lines,
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
                    'critical_errors': len([e for e in errors if e['severity'] == 'ERROR' and any(word in e['message'] for word in ['DELETE', 'UPDATE'])]),
                    'tables_found': len(schema_info.get('tables', [])),
                    'queries_found': len(self._extract_statements(content))
                },
                'analysis_timestamp': datetime.now().isoformat(),
                'processed_successfully': True,
                'analyzer_version': '2.0_react'
            }
            
        except Exception as e:
            logger.error(f"Error en análisis: {e}")
            return {
                'filename': filename,
                'error': f'Error en análisis: {str(e)}',
                'processed_successfully': False,
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _detect_errors(self, content):
        """Detectar errores y advertencias"""
        errors = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith('--'):
                continue
            
            line_upper = line_clean.upper()
            
            for pattern, message, severity in self.error_patterns:
                if re.search(pattern, line_upper, re.IGNORECASE):
                    errors.append({
                        'line': line_num,
                        'message': message,
                        'severity': severity,
                        'code': line_clean[:100] + '...' if len(line_clean) > 100 else line_clean
                    })
        
        return errors
    
    def _analyze_schema(self, content):
        """Analizar esquema de base de datos"""
        tables = []
        indexes = []
        
        # Detectar tablas
        for match in re.finditer(r'CREATE\s+TABLE\s+(\w+)', content, re.IGNORECASE):
            tables.append(match.group(1).lower())
        
        # Detectar índices
        for match in re.finditer(r'CREATE\s+INDEX\s+(\w+)', content, re.IGNORECASE):
            indexes.append(match.group(1).lower())
        
        return {
            'tables': tables,
            'table_count': len(tables),
            'indexes': indexes,
            'index_count': len(indexes)
        }
    
    def _analyze_performance(self, content):
        """Analizar rendimiento"""
        issues = []
        
        if re.search(r'SELECT\s+\*\s+FROM\s+\w+\s*;', content, re.IGNORECASE):
            issues.append({
                'type': 'select_star',
                'message': 'SELECT * puede impactar el rendimiento',
                'severity': 'medium'
            })
        
        performance_score = max(0, 100 - (len(issues) * 15))
        
        return {
            'issues': issues,
            'total_issues': len(issues),
            'performance_score': performance_score
        }
    
    def _analyze_security(self, content):
        """Analizar seguridad"""
        issues = []
        
        if re.search(r'=\s*NULL|!=\s*NULL', content, re.IGNORECASE):
            issues.append({
                'type': 'null_comparison',
                'message': 'Comparación NULL incorrecta detectada',
                'severity': 'high'
            })
        
        security_score = max(0, 100 - (len(issues) * 20))
        
        return {
            'issues': issues,
            'total_issues': len(issues),
            'security_score': security_score
        }
    
    def _calculate_quality_score(self, errors, performance_info, security_info):
        """Calcular score de calidad"""
        error_count = len([e for e in errors if e['severity'] == 'ERROR'])
        warning_count = len([e for e in errors if e['severity'] == 'WARNING'])
        
        penalty = (error_count * 20) + (warning_count * 10)
        penalty += (100 - performance_info['performance_score']) * 0.3
        penalty += (100 - security_info['security_score']) * 0.5
        
        return max(0, int(100 - penalty))
    
    def _generate_recommendations(self, errors, performance_info, security_info):
        """Generar recomendaciones"""
        recommendations = []
        
        if any('WHERE' in e['message'] for e in errors):
            recommendations.append({
                'title': 'Usar cláusulas WHERE',
                'description': 'Siempre use WHERE en UPDATE y DELETE para evitar modificaciones masivas',
                'priority': 'HIGH',
                'type': 'safety'
            })
        
        if performance_info['performance_score'] < 80:
            recommendations.append({
                'title': 'Optimizar consultas',
                'description': 'Evite SELECT * y agregue índices apropiados',
                'priority': 'MEDIUM',
                'type': 'performance'
            })
        
        if security_info['security_score'] < 90:
            recommendations.append({
                'title': 'Mejorar seguridad',
                'description': 'Revise comparaciones NULL y operaciones peligrosas',
                'priority': 'HIGH',
                'type': 'security'
            })
        
        return recommendations
    
    def _extract_statements(self, content):
        """Extraer statements SQL"""
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

# Instancia global del analizador
analyzer = SQLAnalyzerBackend()

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API para análisis de archivos SQL"""
    try:
        logger.info("Iniciando análisis de archivo SQL")
        
        # Validar archivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo en la petición'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó ningún archivo'
            }), 400
        
        # Leer contenido
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                file.seek(0)
                content = file.read().decode('latin-1')
            except:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo decodificar el archivo'
                }), 400
        
        # Validar tamaño
        if len(content) > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'success': False,
                'error': 'Archivo demasiado grande (máximo 10MB de contenido)'
            }), 400
        
        # Analizar
        result = analyzer.analyze(content, secure_filename(file.filename))
        result['success'] = True
        
        logger.info(f"Análisis completado: {file.filename}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        return jsonify({
            'success': False,
            'error': f'Error procesando archivo: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/download/<format>')
def api_download(format):
    """API para descargar resultados"""
    try:
        logger.info(f"Solicitud de descarga: {format}")
        
        # Datos de ejemplo
        data = {
            'analyzer': 'SQL Analyzer Enterprise',
            'version': '2.0 React',
            'timestamp': datetime.now().isoformat(),
            'format': format,
            'content': 'Resultado del análisis SQL'
        }
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False, encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, indent=2, ensure_ascii=False)
                mimetype = 'application/json'
            elif format == 'html':
                f.write(f"""
<!DOCTYPE html>
<html>
<head><title>SQL Analyzer Report</title></head>
<body>
<h1>SQL Analyzer Enterprise - Reporte</h1>
<p><strong>Timestamp:</strong> {data['timestamp']}</p>
<p><strong>Versión:</strong> {data['version']}</p>
<p><strong>Contenido:</strong> {data['content']}</p>
</body>
</html>
                """)
                mimetype = 'text/html'
            elif format == 'csv':
                f.write("Campo,Valor\n")
                f.write(f"Timestamp,{data['timestamp']}\n")
                f.write(f"Version,{data['version']}\n")
                f.write(f"Contenido,{data['content']}\n")
                mimetype = 'text/csv'
            else:
                f.write(f"SQL Analyzer Enterprise - Reporte\n")
                f.write(f"Timestamp: {data['timestamp']}\n")
                f.write(f"Versión: {data['version']}\n")
                f.write(f"Contenido: {data['content']}\n")
                mimetype = 'text/plain'
            
            temp_path = f.name
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        download_name = f'sql_analysis_{timestamp}.{format}'
        
        return send_file(temp_path, 
                        as_attachment=True, 
                        download_name=download_name,
                        mimetype=mimetype)
        
    except Exception as e:
        logger.error(f"Error en descarga: {e}")
        return jsonify({'error': f'Error generando descarga: {str(e)}'}), 500

@app.route('/api/health')
def api_health():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0 React',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'sql_analyzer': 'operational',
            'file_handler': 'operational'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'available_endpoints': ['/api/analyze', '/api/download/<format>', '/api/health']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 SQL ANALYZER ENTERPRISE - BACKEND SERVER")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("🔧 Modo: Producción para React")
    print("🛡️ Características:")
    print("   ✅ API REST completa")
    print("   ✅ CORS configurado para React")
    print("   ✅ Análisis SQL robusto")
    print("   ✅ Manejo de errores completo")
    print("   ✅ Logging detallado")
    print("=" * 60)
    print("🎯 Backend listo para React Frontend!")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
