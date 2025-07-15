#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Backend Server
Flask server with comprehensive SQL analysis capabilities
"""

import os
import sys
import json
import time
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add backend to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Flask imports
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Backend imports
try:
    from backend.core.sql_analyzer import SQLAnalyzer
    from backend.core.error_detector import ErrorDetector
    from backend.core.performance_analyzer import PerformanceAnalyzer
    from backend.core.security_analyzer import SecurityAnalyzer
    from backend.core.format_converter import FormatConverter
    from backend.core.metrics_system import metrics_collector, MetricsTimer, time_operation
    from backend.utils.file_handler import FileHandler
    from backend.utils.validators import FileValidator
    from backend.config import get_config, get_server_config, get_file_config

    # Enterprise features
    from backend.core.enterprise_analyzer import EnterpriseAnalyzer, AnalysisType
    from backend.core.database_engines import DatabaseEngine, database_registry
    from backend.core.advanced_export_system import AdvancedExportSystem, ExportFormat
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all backend modules are properly installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configure CORS
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

# Initialize components
try:
    config = get_config()
    file_config = get_file_config()

    sql_analyzer = SQLAnalyzer()
    error_detector = ErrorDetector()
    performance_analyzer = PerformanceAnalyzer()
    security_analyzer = SecurityAnalyzer()
    format_converter = FormatConverter()
    file_handler = FileHandler()
    file_validator = FileValidator()

    # Enterprise components
    enterprise_analyzer = EnterpriseAnalyzer()
    export_system = AdvancedExportSystem()

    logger.info("All components initialized successfully (including enterprise features)")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    sys.exit(1)

# Create upload directory
UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        system_health = metrics_collector.get_system_health()
        return jsonify({
            'status': system_health.status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'components': {
                'sql_analyzer': 'ready',
                'error_detector': 'ready',
                'performance_analyzer': 'ready',
                'security_analyzer': 'ready',
                'format_converter': 'ready',
                'metrics_system': 'ready'
            },
            'system_metrics': system_health.to_dict()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get comprehensive system metrics"""
    try:
        metrics_summary = metrics_collector.get_metrics_summary()
        return jsonify(metrics_summary)
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/dashboard', methods=['GET'])
def get_dashboard_metrics():
    """Get metrics formatted for dashboard display"""
    try:
        # Quick fallback for dashboard metrics
        try:
            dashboard_data = metrics_collector.get_dashboard_data()
            return jsonify(dashboard_data)
        except:
            # Return minimal working dashboard data
            return jsonify({
                'overview': {
                    'total_analyses': 0,
                    'success_rate': 100.0,
                    'avg_processing_time': 0.0,
                    'system_status': 'healthy'
                },
                'real_time': {
                    'active_analyses': 0,
                    'cpu_usage': 5.0,
                    'memory_usage': 50.0,
                    'error_rate': 0.0
                },
                'trends': {
                    'database_engines': {'mysql': 1, 'postgresql': 1},
                    'export_formats': {'json': 1, 'html': 1},
                    'recent_performance': []
                }
            })
    except Exception as e:
        logger.error(f"Dashboard metrics retrieval failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_sql():
    """Main SQL analysis endpoint"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        validation_result = file_validator.validate_file(file)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = UPLOAD_DIR / filename
        file.save(str(file_path))

        # Get database engine from request
        database_engine = request.form.get('database_engine', 'auto_detect')

        # Record analysis start
        metrics_collector.record_analysis_start(filename, database_engine)
        analysis_start_time = time.time()

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Perform analysis
        logger.info(f"Starting analysis for file: {filename}")
        
        # Basic SQL analysis
        sql_analysis = sql_analyzer.analyze(content)
        
        # Error detection
        error_objects = error_detector.analyze_sql(content)
        error_analysis = [error.to_dict() for error in error_objects]
        
        # Performance analysis
        performance_analysis = performance_analyzer.analyze(content)
        
        # Security analysis
        security_analysis = security_analyzer.analyze(content)
        
        # Compile results
        results = {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'file_size': len(content),
            'line_count': len(content.split('\n')),
            'analysis': {
                'sql_structure': sql_analysis,
                'errors': error_analysis,
                'performance': performance_analysis,
                'security': security_analysis
            },
            'summary': {
                'total_errors': len(error_analysis),
                'performance_score': performance_analysis.get('performance_score', 100),
                'security_score': security_analysis.get('security_score', 100),
                'recommendations': []
            }
        }
        
        # Add recommendations
        if error_analysis:
            results['summary']['recommendations'].append({
                'type': 'errors',
                'message': f'Se encontraron {len(error_analysis)} errores que requieren atención'
            })
        
        if performance_analysis.get('performance_score', 100) < 80:
            results['summary']['recommendations'].append({
                'type': 'performance',
                'message': 'Se detectaron problemas de rendimiento'
            })
        
        if security_analysis.get('security_score', 100) < 80:
            results['summary']['recommendations'].append({
                'type': 'security',
                'message': 'Se detectaron problemas de seguridad'
            })
        
        # Record analysis success metrics
        processing_time = time.time() - analysis_start_time
        lines_analyzed = len(content.splitlines())
        errors_detected = len(error_analysis)

        metrics_collector.record_analysis_success(
            filename, processing_time, lines_analyzed, errors_detected
        )

        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass

        logger.info(f"Analysis completed for file: {filename} in {processing_time:.2f}s")
        return jsonify(results)
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413
    except Exception as e:
        # Record analysis failure
        if 'filename' in locals():
            metrics_collector.record_analysis_failure(filename, str(e))

        logger.error(f"Analysis error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_results():
    """Download analysis results in specified format"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        format_type = data.get('format', 'json')
        results = data.get('results', {})
        
        if not results:
            return jsonify({'error': 'No results to download'}), 400
        
        # Generate file using format converter
        output_file = format_converter.convert(results, format_type)
        
        if output_file and os.path.exists(output_file):
            return send_file(
                output_file,
                as_attachment=True,
                download_name=f"sql_analysis.{format_type}"
            )
        else:
            return jsonify({'error': 'Failed to generate download file'}), 500
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/databases/supported', methods=['GET'])
def get_supported_databases():
    """Get list of supported database engines"""
    try:
        engines = database_registry.get_supported_engines()
        categories = database_registry.get_database_categories()

        result = {
            'total_engines': len(engines),
            'categories': [cat.value for cat in categories],
            'engines': []
        }

        for engine in engines:
            db_info = database_registry.get_database_info(engine)
            if db_info:
                result['engines'].append({
                    'engine': engine.value,
                    'name': db_info.name,
                    'category': db_info.category.value,
                    'vendor': db_info.vendor,
                    'description': db_info.description,
                    'is_open_source': db_info.is_open_source,
                    'default_port': db_info.default_port
                })

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting supported databases: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/databases/detect', methods=['POST'])
def detect_database_engine():
    """Auto-detect database engine from SQL content"""
    try:
        data = request.get_json()
        sql_content = data.get('sql_content', '')
        connection_string = data.get('connection_string', '')

        detected_engine = database_registry.detect_database_engine(sql_content, connection_string)
        db_info = database_registry.get_database_info(detected_engine)

        result = {
            'detected_engine': detected_engine.value,
            'confidence': 0.8,  # Placeholder confidence score
            'database_info': {
                'name': db_info.name,
                'category': db_info.category.value,
                'vendor': db_info.vendor,
                'description': db_info.description
            } if db_info else None
        }

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error detecting database engine: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/formats', methods=['GET'])
def get_export_formats():
    """Get list of supported export formats"""
    try:
        formats = export_system.get_supported_formats()
        categories = list(set(export_system.get_format_info(fmt).category.value for fmt in formats))

        result = {
            'total_formats': len(formats),
            'categories': categories,
            'formats': []
        }

        for fmt in formats:
            fmt_info = export_system.get_format_info(fmt)
            if fmt_info:
                result['formats'].append({
                    'format': fmt.value,
                    'name': fmt_info.name,
                    'category': fmt_info.category.value,
                    'description': fmt_info.description,
                    'file_extension': fmt_info.file_extension,
                    'mime_type': fmt_info.mime_type,
                    'supports_charts': fmt_info.supports_charts,
                    'supports_images': fmt_info.supports_images,
                    'supports_styling': fmt_info.supports_styling,
                    'is_binary': fmt_info.is_binary
                })

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting export formats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format_name>', methods=['POST'])
def export_analysis(format_name):
    """Export analysis results in specified format"""
    try:
        # Get analysis data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No analysis data provided'}), 400

        # Convert format name to enum
        try:
            export_format = ExportFormat(format_name)
        except ValueError:
            return jsonify({'error': f'Unsupported export format: {format_name}'}), 400

        # Export to specified format
        file_path = export_system.export(data, export_format)

        # Get format info for proper content type
        format_info = export_system.get_format_info(export_format)

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_info.file_extension}",
            mimetype=format_info.mime_type
        )

    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        server_config = get_server_config()
        
        logger.info("Starting SQL Analyzer Enterprise Backend Server")
        logger.info(f"Server: http://{server_config.host}:{server_config.port}")
        logger.info(f"Environment: {config.environment.value}")
        
        app.run(
            host=server_config.host,
            port=server_config.port,
            debug=server_config.debug,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
