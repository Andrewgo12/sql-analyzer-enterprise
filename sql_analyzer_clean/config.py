"""
Configuración centralizada para SQL Analyzer Enterprise
Todas las configuraciones del sistema en un solo lugar
"""

import os
import tempfile
from pathlib import Path

class Config:
    """Configuración base del sistema"""
    
    # Configuración Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sql-analyzer-enterprise-2024-secure-key'
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB máximo
    UPLOAD_FOLDER = tempfile.gettempdir()
    ALLOWED_EXTENSIONS = {'sql', 'txt'}
    
    # Configuración de análisis
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_LINES = 100000  # Máximo 100k líneas
    ANALYSIS_TIMEOUT = 300  # 5 minutos timeout
    
    # Configuración de formatos de descarga
    SUPPORTED_FORMATS = {
        'json': 'application/json',
        'txt': 'text/plain',
        'html': 'text/html',
        'csv': 'text/csv',
        'sql': 'text/plain',
        'md': 'text/markdown'
    }
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuración de seguridad
    SECURE_FILENAME = True
    VALIDATE_FILE_CONTENT = True
    SANITIZE_INPUT = True
    
    # Configuración de rendimiento
    ENABLE_CACHING = False  # Deshabilitado para simplicidad
    CACHE_TIMEOUT = 300
    
    # Configuración de la aplicación
    APP_NAME = 'SQL Analyzer Enterprise'
    APP_VERSION = '2.0 Clean'
    APP_DESCRIPTION = 'Analizador SQL profesional con arquitectura limpia'
    
    # Configuración de idioma
    DEFAULT_LANGUAGE = 'es'
    SUPPORTED_LANGUAGES = ['es', 'en']
    
    # Configuración de análisis SQL
    SQL_ANALYSIS_CONFIG = {
        'detect_syntax_errors': True,
        'detect_performance_issues': True,
        'detect_security_issues': True,
        'generate_recommendations': True,
        'add_intelligent_comments': True,
        'generate_sample_data': True,
        'analyze_schema': True,
        'calculate_quality_score': True
    }
    
    # Patrones de errores SQL
    SQL_ERROR_PATTERNS = {
        'dangerous_operations': [
            r'DELETE\s+FROM\s+\w+\s*;',
            r'UPDATE\s+\w+\s+SET\s+.*\s*;',
            r'DROP\s+TABLE',
            r'TRUNCATE\s+TABLE'
        ],
        'performance_issues': [
            r'SELECT\s+\*\s+FROM',
            r'ORDER\s+BY\s+.*\s+DESC\s+LIMIT'
        ],
        'security_issues': [
            r'=\s*NULL',
            r'!=\s*NULL',
            r'<>\s*NULL'
        ]
    }
    
    # Configuración de mensajes
    MESSAGES = {
        'es': {
            'file_uploaded': 'Archivo subido exitosamente',
            'analysis_complete': 'Análisis completado',
            'analysis_error': 'Error en el análisis',
            'file_too_large': 'Archivo demasiado grande',
            'invalid_file_type': 'Tipo de archivo no válido',
            'no_file_selected': 'No se seleccionó archivo',
            'download_ready': 'Descarga lista',
            'system_error': 'Error del sistema'
        },
        'en': {
            'file_uploaded': 'File uploaded successfully',
            'analysis_complete': 'Analysis completed',
            'analysis_error': 'Analysis error',
            'file_too_large': 'File too large',
            'invalid_file_type': 'Invalid file type',
            'no_file_selected': 'No file selected',
            'download_ready': 'Download ready',
            'system_error': 'System error'
        }
    }
    
    @staticmethod
    def get_message(key, language='es'):
        """Obtener mensaje localizado"""
        return Config.MESSAGES.get(language, {}).get(key, key)
    
    @staticmethod
    def is_allowed_file(filename):
        """Verificar si el archivo tiene extensión permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_upload_path():
        """Obtener ruta de subida de archivos"""
        upload_path = Path(Config.UPLOAD_FOLDER) / 'sql_analyzer_uploads'
        upload_path.mkdir(exist_ok=True)
        return str(upload_path)

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB para tests

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}
