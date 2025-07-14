#!/usr/bin/env python3
"""
Servidor Simple para SQL Analyzer Enterprise
Servidor Flask básico para pruebas inmediatas
"""

import os
import sys
from pathlib import Path

# Configurar paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importaciones básicas
from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import json
from datetime import datetime

# Crear aplicación Flask
app = Flask(__name__, 
           template_folder='web_app/templates',
           static_folder='web_app/static')

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def home():
    """Página principal"""
    return render_template('simple_home.html')

@app.route('/analyze')
def analyze():
    """Página de análisis"""
    return render_template('simple_analyze.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API para análisis de archivos SQL usando el analizador completo"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400

        # Leer contenido del archivo
        content = file.read().decode('utf-8')

        # Usar el analizador completo
        try:
            # Importar el analizador SQL completo
            sys.path.append('.')
            from web_app.sql_analyzer.analyzer import SQLAnalyzer

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name

            # Analizar con el sistema completo
            analyzer = SQLAnalyzer()
            result = analyzer.analyze_file(temp_path)

            # Limpiar archivo temporal
            os.unlink(temp_path)

            return jsonify(result)

        except Exception as analyzer_error:
            print(f"Error en analizador completo: {analyzer_error}")

            # Fallback: análisis básico
            lines = content.split('\n')
            line_count = len(lines)

            # Detectar errores básicos
            errors = []
            warnings = []

            for i, line in enumerate(lines, 1):
                line_clean = line.strip().upper()

                # Detectar errores comunes
                if 'SELECT *' in line_clean and 'WHERE' not in line_clean and 'FROM' in line_clean:
                    warnings.append({
                        'line': i,
                        'message': 'SELECT * sin WHERE puede ser ineficiente',
                        'severity': 'WARNING'
                    })

                if 'DELETE FROM' in line_clean and 'WHERE' not in line_clean:
                    errors.append({
                        'line': i,
                        'message': 'DELETE sin WHERE eliminará todos los registros',
                        'severity': 'ERROR'
                    })

                if 'UPDATE' in line_clean and 'WHERE' not in line_clean and 'SET' in line_clean:
                    errors.append({
                        'line': i,
                        'message': 'UPDATE sin WHERE actualizará todos los registros',
                        'severity': 'ERROR'
                    })

                if '= NULL' in line_clean or '!= NULL' in line_clean:
                    errors.append({
                        'line': i,
                        'message': 'Comparación incorrecta con NULL. Use IS NULL o IS NOT NULL',
                        'severity': 'ERROR'
                    })

            # Calcular score de calidad
            total_issues = len(errors) + len(warnings)
            quality_score = max(0, 100 - (total_issues * 10))

            # Resultado del análisis básico
            result = {
                'filename': file.filename,
                'lines': line_count,
                'quality_score': quality_score,
                'errors': errors + warnings,
                'summary': {
                    'total_errors': len(errors),
                    'total_warnings': len(warnings),
                    'critical_errors': len([e for e in errors if e['severity'] == 'ERROR']),
                    'tables_found': len([line for line in lines if 'CREATE TABLE' in line.upper()]),
                    'queries_found': len([line for line in lines if any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE'])])
                },
                'analysis_timestamp': datetime.now().isoformat(),
                'processed_successfully': True,
                'analyzer_used': 'basic_fallback'
            }

            return jsonify(result)

    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({
            'error': f'Error procesando archivo: {str(e)}',
            'processed_successfully': False
        }), 500

@app.route('/api/download/<format>')
def api_download(format):
    """API para descargar resultados en diferentes formatos"""
    try:
        # Datos de ejemplo para descarga
        sample_data = {
            'filename': 'analysis_result',
            'timestamp': datetime.now().isoformat(),
            'content': 'Resultado del análisis SQL'
        }
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as f:
            if format == 'json':
                json.dump(sample_data, f, indent=2)
                mimetype = 'application/json'
            elif format == 'txt':
                f.write(f"Análisis SQL - {sample_data['timestamp']}\n")
                f.write(f"Archivo: {sample_data['filename']}\n")
                f.write(f"Contenido: {sample_data['content']}\n")
                mimetype = 'text/plain'
            else:
                f.write("Formato no soportado")
                mimetype = 'text/plain'
            
            temp_path = f.name
        
        return send_file(temp_path, 
                        as_attachment=True, 
                        download_name=f'sql_analysis.{format}',
                        mimetype=mimetype)
        
    except Exception as e:
        return jsonify({'error': f'Error generando descarga: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    print("🚀 Iniciando SQL Analyzer Enterprise - Servidor Simple")
    print("📍 Servidor disponible en: http://localhost:5000")
    print("🔧 Modo de desarrollo activado")
    print("=" * 60)
    
    # Verificar archivos necesarios
    template_dir = Path('web_app/templates')
    static_dir = Path('web_app/static')
    
    if template_dir.exists():
        print(f"✅ Templates encontrados: {template_dir}")
    else:
        print(f"❌ Templates no encontrados: {template_dir}")
    
    if static_dir.exists():
        print(f"✅ Archivos estáticos encontrados: {static_dir}")
    else:
        print(f"❌ Archivos estáticos no encontrados: {static_dir}")
    
    print("=" * 60)
    
    # Iniciar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Evitar problemas con el reloader
    )
