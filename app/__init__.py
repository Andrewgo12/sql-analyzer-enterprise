#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE APPLICATION
Production-ready Flask application with MVC architecture
"""

import os
import logging
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.exceptions import RequestEntityTooLarge

# Import configuration
from app.config.settings import get_config, APP_METADATA

# Import controllers
from app.controllers.analysis_controller import AnalysisController
from app.controllers.view_controller import ViewController

# Import utilities
from app.utils.helpers import (
    FileHelper, TimeHelper, ValidationHelper, ResponseHelper,
    LoggingHelper, SecurityHelper, cache
)

def create_app(config_name: str = None) -> Flask:
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize configuration
    config.init_app(app)
    
    # Setup logging
    logger = LoggingHelper.setup_logger(
        'sql_analyzer',
        app.config.get('LOG_LEVEL', 'INFO'),
        app.config.get('LOG_FILE')
    )
    
    # Initialize controllers
    analysis_controller = AnalysisController()
    view_controller = ViewController()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app, analysis_controller, view_controller)
    
    # Register template filters
    register_template_filters(app)
    
    logger.info(f"SQL Analyzer Enterprise v{APP_METADATA['version']} initialized")
    
    return app

def register_error_handlers(app: Flask):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', 
                             error_message="Page not found",
                             error_code=404), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html',
                             error_message="Internal server error",
                             error_code=500), 500
    
    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error):
        return jsonify(ResponseHelper.error_response(
            "File too large. Maximum size is 100MB",
            "FILE_TOO_LARGE",
            413
        )), 413

def register_routes(app: Flask, analysis_controller: AnalysisController, view_controller: ViewController):
    """Register application routes"""
    
    # ===== VIEW ROUTES =====
    
    @app.route('/')
    def index():
        """Main page - SQL Analysis"""
        return view_controller.render_sql_analysis_view()
    
    @app.route('/sql-analysis')
    def sql_analysis():
        """SQL Analysis & Correction view"""
        return view_controller.render_sql_analysis_view()
    
    @app.route('/security-analysis')
    def security_analysis():
        """Security & Vulnerability Scanning view"""
        return view_controller.render_security_analysis_view()
    
    @app.route('/performance-optimization')
    def performance_optimization():
        """Performance Optimization view"""
        return view_controller.render_performance_optimization_view()
    
    @app.route('/schema-analysis')
    def schema_analysis():
        """Schema & Relationship Analysis view"""
        return view_controller.render_schema_analysis_view()
    
    @app.route('/export-center')
    def export_center():
        """Export & Format Conversion view"""
        return view_controller.render_export_center_view()
    
    @app.route('/version-management')
    def version_management():
        """Version Management view"""
        return view_controller.render_version_management_view()
    
    @app.route('/comment-documentation')
    def comment_documentation():
        """Comment & Documentation view"""
        return view_controller.render_comment_documentation_view()
    
    # ===== API ROUTES =====
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        return jsonify(ResponseHelper.success_response({
            'status': 'healthy',
            'version': APP_METADATA['version'],
            'timestamp': TimeHelper.format_timestamp(TimeHelper.datetime.now())
        }))
    
    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        """Main analysis endpoint"""
        try:
            # Validate request
            if 'file' not in request.files:
                return jsonify(ResponseHelper.error_response(
                    "No file provided",
                    "NO_FILE",
                    400
                )), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify(ResponseHelper.error_response(
                    "No file selected",
                    "NO_FILE_SELECTED",
                    400
                )), 400
            
            # Validate file type
            if not FileHelper.is_allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                return jsonify(ResponseHelper.error_response(
                    f"File type not allowed. Allowed types: {', '.join(app.config['ALLOWED_EXTENSIONS'])}",
                    "INVALID_FILE_TYPE",
                    400
                )), 400
            
            # Perform analysis
            result = analysis_controller.analyze_sql_file(file, file.filename)
            
            if result['success']:
                return jsonify(ResponseHelper.success_response(result))
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    result.get('error_type', 'ANALYSIS_ERROR'),
                    400
                )), 400
            
        except Exception as e:
            app.logger.error(f"Analysis API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500
    
    @app.route('/api/analysis/<analysis_id>')
    def api_get_analysis(analysis_id):
        """Get analysis details"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return jsonify(ResponseHelper.error_response(
                    "Invalid analysis ID",
                    "INVALID_ID",
                    400
                )), 400
            
            result = analysis_controller.get_analysis_details(analysis_id)
            
            if result['success']:
                return jsonify(ResponseHelper.success_response(result['details']))
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    "ANALYSIS_NOT_FOUND",
                    404
                )), 404
            
        except Exception as e:
            app.logger.error(f"Get analysis API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500
    
    @app.route('/api/analysis/<analysis_id>/summary')
    def api_get_analysis_summary(analysis_id):
        """Get analysis summary"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return jsonify(ResponseHelper.error_response(
                    "Invalid analysis ID",
                    "INVALID_ID",
                    400
                )), 400
            
            result = analysis_controller.get_analysis_summary(analysis_id)
            
            if result['success']:
                return jsonify(ResponseHelper.success_response(result['summary']))
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    "ANALYSIS_NOT_FOUND",
                    404
                )), 404
            
        except Exception as e:
            app.logger.error(f"Get analysis summary API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500
    
    @app.route('/api/analysis/<analysis_id>/security')
    def api_get_security_analysis(analysis_id):
        """Get security analysis details"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return jsonify(ResponseHelper.error_response(
                    "Invalid analysis ID",
                    "INVALID_ID",
                    400
                )), 400
            
            result = analysis_controller.get_security_analysis(analysis_id)
            
            if result['success']:
                return jsonify(ResponseHelper.success_response(result['security_analysis']))
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    "ANALYSIS_NOT_FOUND",
                    404
                )), 404
            
        except Exception as e:
            app.logger.error(f"Get security analysis API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500
    
    @app.route('/api/analysis/<analysis_id>/performance')
    def api_get_performance_analysis(analysis_id):
        """Get performance analysis details"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return jsonify(ResponseHelper.error_response(
                    "Invalid analysis ID",
                    "INVALID_ID",
                    400
                )), 400
            
            result = analysis_controller.get_performance_analysis(analysis_id)
            
            if result['success']:
                return jsonify(ResponseHelper.success_response(result['performance_analysis']))
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    "ANALYSIS_NOT_FOUND",
                    404
                )), 404
            
        except Exception as e:
            app.logger.error(f"Get performance analysis API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500
    
    @app.route('/api/analysis/<analysis_id>/schema')
    def api_get_schema_analysis(analysis_id):
        """Get schema analysis details"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return jsonify(ResponseHelper.error_response(
                    "Invalid analysis ID",
                    "INVALID_ID",
                    400
                )), 400
            
            result = analysis_controller.get_schema_analysis(analysis_id)
            
            if result['success']:
                return jsonify(ResponseHelper.success_response(result['schema_analysis']))
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    "ANALYSIS_NOT_FOUND",
                    404
                )), 404
            
        except Exception as e:
            app.logger.error(f"Get schema analysis API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500
    
    @app.route('/api/export/<analysis_id>/<format_type>')
    def api_export_analysis(analysis_id, format_type):
        """Export analysis results"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return jsonify(ResponseHelper.error_response(
                    "Invalid analysis ID",
                    "INVALID_ID",
                    400
                )), 400
            
            if not ValidationHelper.validate_export_format(format_type, app.config['EXPORT_FORMATS']):
                return jsonify(ResponseHelper.error_response(
                    f"Invalid export format. Allowed formats: {', '.join(app.config['EXPORT_FORMATS'])}",
                    "INVALID_FORMAT",
                    400
                )), 400
            
            result = analysis_controller.export_analysis(analysis_id, format_type)
            
            if result['success']:
                # Create temporary file for download
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=f'.{format_type}',
                    delete=False,
                    encoding='utf-8'
                )
                temp_file.write(result['content'])
                temp_file.close()
                
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name=result['filename'],
                    mimetype=result['mime_type']
                )
            else:
                return jsonify(ResponseHelper.error_response(
                    result['error'],
                    "EXPORT_ERROR",
                    400
                )), 400
            
        except Exception as e:
            app.logger.error(f"Export API error: {str(e)}")
            return jsonify(ResponseHelper.error_response(
                "Internal server error",
                "INTERNAL_ERROR",
                500
            )), 500

def register_template_filters(app: Flask):
    """Register custom template filters"""
    
    @app.template_filter('format_duration')
    def format_duration_filter(seconds):
        return TimeHelper.format_duration(seconds)
    
    @app.template_filter('format_file_size')
    def format_file_size_filter(size_bytes):
        return FileHelper.format_file_size(size_bytes)
    
    @app.template_filter('format_timestamp')
    def format_timestamp_filter(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
        return TimeHelper.format_timestamp(timestamp, format_str)
    
    @app.template_filter('relative_time')
    def relative_time_filter(timestamp):
        return TimeHelper.get_relative_time(timestamp)
