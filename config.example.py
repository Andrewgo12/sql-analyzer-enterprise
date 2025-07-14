"""
Archivo de Configuración de Ejemplo para SQL Analyzer Enterprise

Copie este archivo como 'config.py' y modifique los valores según sus necesidades.
"""

# ============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================================

# Configuración del servidor web
SERVER_CONFIG = {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": True,
    "reload": True,
    "workers": 1,
    "max_connections": 100
}

# Configuración de CORS
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}

# ============================================================================
# CONFIGURACIÓN DE ANÁLISIS
# ============================================================================

# Límites de archivos
FILE_LIMITS = {
    "max_file_size": 100 * 1024 * 1024 * 1024,  # 100GB
    "max_files_per_batch": 10,
    "allowed_extensions": [".sql", ".txt"],
    "chunk_size": 1024 * 1024  # 1MB chunks para archivos grandes
}

# Configuración de análisis
ANALYSIS_CONFIG = {
    "max_errors_per_file": 1000,
    "enable_auto_fix": True,
    "enable_intelligent_comments": True,
    "enable_sample_data_generation": True,
    "default_language": "es",
    "supported_languages": ["es", "en"],
    "analysis_timeout": 300  # 5 minutos
}

# Tipos de análisis disponibles
ANALYSIS_TYPES = {
    "syntax": {
        "enabled": True,
        "description": "Análisis de sintaxis SQL",
        "weight": 1.0
    },
    "schema": {
        "enabled": True,
        "description": "Análisis de esquema de base de datos",
        "weight": 1.2
    },
    "security": {
        "enabled": True,
        "description": "Análisis de seguridad y vulnerabilidades",
        "weight": 1.5
    },
    "performance": {
        "enabled": True,
        "description": "Análisis de rendimiento",
        "weight": 1.3
    },
    "relationships": {
        "enabled": True,
        "description": "Análisis de relaciones entre tablas",
        "weight": 1.1
    },
    "constraints": {
        "enabled": True,
        "description": "Análisis de restricciones",
        "weight": 1.0
    }
}

# ============================================================================
# CONFIGURACIÓN DE FORMATOS DE EXPORTACIÓN
# ============================================================================

# Formatos habilitados (True = habilitado, False = deshabilitado)
EXPORT_FORMATS = {
    "enhanced_sql": True,
    "html_report": True,
    "interactive_html": True,
    "pdf_report": True,
    "json_analysis": True,
    "xml_report": True,
    "csv_summary": True,
    "excel_workbook": True,
    "word_document": False,  # Requiere python-docx
    "markdown_docs": True,
    "latex_report": False,   # Requiere LaTeX
    "powerpoint": False,     # Requiere python-pptx
    "sqlite_database": True,
    "zip_archive": True,
    "plain_text": True,
    "yaml_config": True,
    "schema_diagram": True,
    "jupyter_notebook": True,
    "python_script": True
}

# Configuración específica de formatos
FORMAT_CONFIG = {
    "pdf": {
        "page_size": "A4",
        "include_charts": True,
        "max_errors_per_page": 5
    },
    "excel": {
        "include_charts": True,
        "max_sheets": 10,
        "chart_types": ["pie", "bar", "line"]
    },
    "html": {
        "include_css": True,
        "include_javascript": True,
        "responsive": True,
        "dark_mode": False
    }
}

# ============================================================================
# CONFIGURACIÓN DE FUNCIONALIDADES EMPRESARIALES
# ============================================================================

# Funcionalidades empresariales habilitadas
ENTERPRISE_FEATURES = {
    "ultra_large_processing": True,
    "schema_visualization": True,
    "performance_optimization": True,
    "security_audit": True,
    "database_migration": True,
    "collaborative_analysis": False,  # Requiere Redis
    "advanced_reporting": True,
    "code_quality_metrics": True,
    "api_integration": True,
    "ml_predictive_analysis": False   # Requiere TensorFlow/PyTorch
}

# Configuración de procesamiento ultra-grande
ULTRA_LARGE_CONFIG = {
    "max_file_size": 100 * 1024 * 1024 * 1024,  # 100GB
    "chunk_size": 10 * 1024 * 1024,  # 10MB chunks
    "parallel_workers": 4,
    "memory_limit": 8 * 1024 * 1024 * 1024,  # 8GB
    "temp_directory": "/tmp/sql_analyzer"
}

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

# Configuración de base de datos (para funcionalidades avanzadas)
DATABASE_CONFIG = {
    "enabled": False,
    "url": "sqlite:///sql_analyzer.db",
    "echo": False,
    "pool_size": 10,
    "max_overflow": 20
}

# ============================================================================
# CONFIGURACIÓN DE CACHE
# ============================================================================

# Configuración de cache
CACHE_CONFIG = {
    "enabled": True,
    "type": "memory",  # "memory", "redis", "file"
    "ttl": 3600,  # 1 hora
    "max_size": 1000,
    "redis_url": "redis://localhost:6379/0"
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "sql_analyzer.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "console": True
}

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# Configuración de seguridad
SECURITY_CONFIG = {
    "secret_key": "your-secret-key-here-change-in-production",
    "session_timeout": 3600,  # 1 hora
    "max_login_attempts": 5,
    "csrf_protection": True,
    "rate_limiting": {
        "enabled": True,
        "requests_per_minute": 60,
        "burst": 10
    }
}

# ============================================================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ============================================================================

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your-email@gmail.com",
        "password": "your-app-password",
        "from_address": "sql-analyzer@yourcompany.com"
    },
    "webhook": {
        "enabled": False,
        "url": "https://your-webhook-url.com/notifications",
        "timeout": 30
    }
}

# ============================================================================
# CONFIGURACIÓN DE INTEGRACIÓN
# ============================================================================

# Configuración de integraciones externas
INTEGRATION_CONFIG = {
    "github": {
        "enabled": False,
        "token": "your-github-token",
        "webhook_secret": "your-webhook-secret"
    },
    "slack": {
        "enabled": False,
        "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        "channel": "#sql-analysis"
    },
    "jira": {
        "enabled": False,
        "url": "https://yourcompany.atlassian.net",
        "username": "your-username",
        "api_token": "your-api-token"
    }
}

# ============================================================================
# CONFIGURACIÓN DE DESARROLLO
# ============================================================================

# Configuración específica para desarrollo
DEVELOPMENT_CONFIG = {
    "debug": True,
    "auto_reload": True,
    "show_sql": False,
    "mock_external_services": True,
    "test_data_enabled": True
}

# ============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ============================================================================

# Configuración específica para producción
PRODUCTION_CONFIG = {
    "debug": False,
    "auto_reload": False,
    "workers": 4,
    "access_log": True,
    "error_log": True,
    "ssl_enabled": True,
    "ssl_cert": "/path/to/cert.pem",
    "ssl_key": "/path/to/key.pem"
}

# ============================================================================
# CONFIGURACIÓN DE MONITOREO
# ============================================================================

# Configuración de monitoreo y métricas
MONITORING_CONFIG = {
    "enabled": True,
    "metrics_endpoint": "/metrics",
    "health_endpoint": "/health",
    "prometheus": {
        "enabled": False,
        "port": 9090
    },
    "sentry": {
        "enabled": False,
        "dsn": "your-sentry-dsn"
    }
}

# ============================================================================
# CONFIGURACIÓN PERSONALIZADA
# ============================================================================

# Aquí puede agregar su configuración personalizada
CUSTOM_CONFIG = {
    "company_name": "Su Empresa",
    "logo_url": "/static/images/logo.png",
    "theme_color": "#667eea",
    "contact_email": "support@yourcompany.com",
    "documentation_url": "https://docs.yourcompany.com/sql-analyzer"
}
