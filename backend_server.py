#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Backend Server
Flask server with comprehensive SQL analysis capabilities
"""

import os
import sys
import json
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
    from backend.utils.file_handler import FileHandler
    from backend.utils.validators import FileValidator
    from backend.config import get_config, get_server_config, get_file_config
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
    
    logger.info("All components initialized successfully")
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
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'components': {
                'sql_analyzer': 'ready',
                'error_detector': 'ready',
                'performance_analyzer': 'ready',
                'security_analyzer': 'ready',
                'format_converter': 'ready'
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        logger.info(f"Analysis completed for file: {filename}")
        return jsonify(results)
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413
    except Exception as e:
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
