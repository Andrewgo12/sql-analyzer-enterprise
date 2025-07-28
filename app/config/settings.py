#!/usr/bin/env python3
"""
APPLICATION CONFIGURATION
Enterprise-grade configuration management
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sql-analyzer-enterprise-2024-secure-key'
    DEBUG = False
    TESTING = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'.sql', '.txt', '.ddl', '.dml', '.psql', '.mysql', '.oracle'}
    
    # Analysis settings
    ANALYSIS_TIMEOUT = 300  # 5 minutes
    MAX_CONCURRENT_ANALYSES = 5
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 3600  # 1 hour
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///sql_analyzer.db'
    
    # Security settings
    SECURITY_ENABLED = True
    OWASP_COMPLIANCE = True
    CWE_CLASSIFICATION = True
    
    # Performance settings
    PERFORMANCE_TARGET = 2.0  # seconds
    MEMORY_LIMIT_PERCENT = 70
    
    # Export settings
    EXPORT_FORMATS = [
        'json', 'html', 'xml', 'csv', 'markdown', 'txt', 'sql',
        'mysql_dump', 'postgresql_backup', 'oracle_script', 'documentation'
    ]
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/sql_analyzer.log'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    CACHE_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """Get configuration by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

# Application constants
class Constants:
    """Application constants"""
    
    # Database types
    DATABASE_TYPES = {
        'mysql': 'MySQL',
        'postgresql': 'PostgreSQL', 
        'oracle': 'Oracle',
        'sql_server': 'SQL Server',
        'sqlite': 'SQLite',
        'mongodb': 'MongoDB',
        'generic': 'Generic SQL'
    }
    
    # Error severity levels
    SEVERITY_LEVELS = {
        'critical': 'Critical',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    }
    
    # Analysis types
    ANALYSIS_TYPES = {
        'syntax': 'Syntax Analysis',
        'semantic': 'Semantic Analysis',
        'performance': 'Performance Analysis',
        'security': 'Security Analysis',
        'schema': 'Schema Analysis'
    }
    
    # Export formats with descriptions
    EXPORT_FORMAT_DESCRIPTIONS = {
        'json': 'JSON - Structured data format',
        'html': 'HTML - Interactive web report',
        'xml': 'XML - Hierarchical data format',
        'csv': 'CSV - Comma-separated values',
        'markdown': 'Markdown - Documentation format',
        'txt': 'TXT - Plain text summary',
        'sql': 'SQL - Corrected SQL with comments',
        'mysql_dump': 'MySQL Dump - MySQL-compatible export',
        'postgresql_backup': 'PostgreSQL Backup - PostgreSQL-compatible export',
        'oracle_script': 'Oracle Script - Oracle-compatible export',
        'documentation': 'Documentation - Comprehensive HTML documentation'
    }
    
    # Quality thresholds
    QUALITY_THRESHOLDS = {
        'excellent': 90,
        'good': 75,
        'fair': 60,
        'poor': 40
    }
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        'excellent': 0.5,  # seconds
        'good': 1.0,
        'fair': 2.0,
        'poor': 5.0
    }

# Application metadata
APP_METADATA = {
    'name': 'SQL Analyzer Enterprise',
    'version': '2.0.0',
    'description': 'Enterprise-grade SQL analysis with multi-database support',
    'author': 'SQL Analysis Team',
    'license': 'MIT',
    'url': 'https://github.com/sql-analyzer-enterprise',
    'documentation': 'https://docs.sql-analyzer-enterprise.com',
    'support': 'support@sql-analyzer-enterprise.com'
}
