"""
Format Configuration

Configuration for all available download formats and their mappings.
"""

from typing import Dict, Any

# Mapping from UI format values to generator classes
FORMAT_MAPPING = {
    "enhanced_sql": "EnhancedSQLGenerator",
    "html_report": "HTMLReportGenerator", 
    "interactive_html": "InteractiveHTMLGenerator",
    "pdf_report": "PDFReportGenerator",
    "json_analysis": "JSONAnalysisGenerator",
    "xml_report": "XMLReportGenerator",
    "csv_summary": "CSVSummaryGenerator",
    "excel_workbook": "ExcelWorkbookGenerator",
    "word_document": "WordDocumentGenerator",
    "markdown_docs": "MarkdownDocumentationGenerator",
    "latex_report": "LaTeXReportGenerator",
    "powerpoint": "PowerPointGenerator",
    "sqlite_database": "SQLiteDatabaseGenerator",
    "zip_archive": "ZIPArchiveGenerator",
    "plain_text": "PlainTextGenerator",
    "yaml_config": "YAMLConfigurationGenerator",
    "schema_diagram": "SchemaDiagramGenerator",
    "jupyter_notebook": "JupyterNotebookGenerator",
    "python_script": "PythonScriptGenerator"
}

# Format descriptions for the API
FORMAT_DESCRIPTIONS = {
    "enhanced_sql": {
        "name": "SQL Mejorado",
        "description": "Archivo SQL con comentarios inteligentes y correcciones automáticas",
        "icon": "📄",
        "category": "code",
        "features": ["Comentarios en español", "Correcciones automáticas", "Explicaciones de consultas complejas"]
    },
    "html_report": {
        "name": "Reporte HTML",
        "description": "Reporte completo con CSS embebido y elementos interactivos",
        "icon": "🌐",
        "category": "report",
        "features": ["CSS embebido", "Gráficos Chart.js", "Responsive design"]
    },
    "interactive_html": {
        "name": "Dashboard HTML Interactivo",
        "description": "Dashboard con gráficos en tiempo real y filtros interactivos",
        "icon": "📊",
        "category": "dashboard",
        "features": ["Gráficos interactivos", "Filtros en tiempo real", "Exportación de datos"]
    },
    "pdf_report": {
        "name": "Reporte PDF",
        "description": "Reporte profesional con formato y gráficos vectoriales",
        "icon": "📋",
        "category": "report",
        "features": ["Formato profesional", "Gráficos vectoriales", "Múltiples páginas"]
    },
    "json_analysis": {
        "name": "Datos JSON",
        "description": "Datos de análisis estructurados para integración con APIs",
        "icon": "🔧",
        "category": "data",
        "features": ["Estructura completa", "Metadatos detallados", "Compatible con APIs"]
    },
    "xml_report": {
        "name": "Reporte XML",
        "description": "Resultados en formato XML compatible con sistemas empresariales",
        "icon": "📰",
        "category": "data",
        "features": ["Esquema validado", "Compatible con XSLT", "Estructura jerárquica"]
    },
    "csv_summary": {
        "name": "Resumen CSV",
        "description": "Resumen tabular de errores y métricas para análisis en Excel",
        "icon": "📊",
        "category": "data",
        "features": ["Compatible con Excel", "Datos tabulares", "Fácil importación"]
    },
    "excel_workbook": {
        "name": "Libro Excel",
        "description": "Análisis multi-hoja con gráficos y tablas dinámicas",
        "icon": "📈",
        "category": "report",
        "features": ["Múltiples hojas", "Gráficos integrados", "Tablas dinámicas"]
    },
    "word_document": {
        "name": "Documento Word",
        "description": "Reporte profesional en formato Microsoft Word",
        "icon": "📝",
        "category": "report",
        "features": ["Formato profesional", "Estilos consistentes", "Compatible con Office"]
    },
    "markdown_docs": {
        "name": "Documentación Markdown",
        "description": "Documentación compatible con GitHub y sistemas de documentación",
        "icon": "📚",
        "category": "documentation",
        "features": ["Compatible con GitHub", "Sintaxis estándar", "Fácil edición"]
    },
    "latex_report": {
        "name": "Reporte LaTeX",
        "description": "Reporte académico profesional con tipografía de alta calidad",
        "icon": "🎓",
        "category": "academic",
        "features": ["Tipografía profesional", "Fórmulas matemáticas", "Referencias automáticas"]
    },
    "powerpoint": {
        "name": "Presentación PowerPoint",
        "description": "Diapositivas de resumen ejecutivo para presentaciones",
        "icon": "🎯",
        "category": "presentation",
        "features": ["Diapositivas ejecutivas", "Gráficos integrados", "Plantillas profesionales"]
    },
    "sqlite_database": {
        "name": "Base de Datos SQLite",
        "description": "Resultados almacenados en base de datos consultable",
        "icon": "🗄️",
        "category": "database",
        "features": ["Datos consultables", "Relaciones normalizadas", "Índices optimizados"]
    },
    "zip_archive": {
        "name": "Archivo ZIP",
        "description": "Múltiples formatos empaquetados en un solo archivo",
        "icon": "📦",
        "category": "archive",
        "features": ["Múltiples formatos", "Compresión eficiente", "Fácil distribución"]
    },
    "plain_text": {
        "name": "Reporte de Texto",
        "description": "Salida compatible con consola y sistemas de texto",
        "icon": "📄",
        "category": "text",
        "features": ["Compatible con consola", "Sin formato", "Fácil procesamiento"]
    },
    "yaml_config": {
        "name": "Configuración YAML",
        "description": "Exportación estructurada para sistemas de configuración",
        "icon": "⚙️",
        "category": "config",
        "features": ["Estructura jerárquica", "Legible por humanos", "Compatible con DevOps"]
    },
    "schema_diagram": {
        "name": "Diagrama de Esquema",
        "description": "Gráficos vectoriales SVG de la estructura de la base de datos",
        "icon": "🎨",
        "category": "diagram",
        "features": ["Gráficos vectoriales", "Escalable", "Compatible con navegadores"]
    },
    "jupyter_notebook": {
        "name": "Notebook Jupyter",
        "description": "Análisis ejecutable con código Python y visualizaciones",
        "icon": "🔬",
        "category": "analysis",
        "features": ["Código ejecutable", "Visualizaciones", "Análisis interactivo"]
    },
    "python_script": {
        "name": "Script Python",
        "description": "Generador de análisis independiente en Python",
        "icon": "🐍",
        "category": "code",
        "features": ["Código independiente", "Reutilizable", "Personalizable"]
    }
}

# Enterprise features configuration
ENTERPRISE_FEATURES = {
    "ultra_large_processing": {
        "name": "Procesamiento Ultra-Grande",
        "description": "Archivos hasta 100GB con streaming y procesamiento paralelo",
        "icon": "🚀",
        "category": "performance",
        "requirements": ["Memoria: 16GB+", "CPU: 8 cores+", "Almacenamiento: SSD"]
    },
    "schema_visualization": {
        "name": "Mapeo y Visualización de Esquemas",
        "description": "Diagramas ER interactivos con detección automática de relaciones",
        "icon": "🎨",
        "category": "visualization",
        "requirements": ["Navegador moderno", "JavaScript habilitado"]
    },
    "performance_optimization": {
        "name": "Optimización de Rendimiento",
        "description": "Análisis de planes de consulta y recomendaciones de índices",
        "icon": "⚡",
        "category": "optimization",
        "requirements": ["Acceso a metadatos de BD", "Estadísticas de consulta"]
    },
    "security_audit": {
        "name": "Auditoría de Seguridad",
        "description": "Detección de inyección SQL y análisis de vulnerabilidades",
        "icon": "🔒",
        "category": "security",
        "requirements": ["Patrones de seguridad actualizados", "Base de vulnerabilidades"]
    },
    "database_migration": {
        "name": "Asistente de Migración",
        "description": "Traducción automática entre diferentes plataformas de BD",
        "icon": "🔄",
        "category": "migration",
        "requirements": ["Conectores de BD", "Mapeo de tipos de datos"]
    },
    "collaborative_analysis": {
        "name": "Análisis Colaborativo",
        "description": "Edición multi-usuario en tiempo real con control de versiones",
        "icon": "👥",
        "category": "collaboration",
        "requirements": ["WebSocket", "Sistema de autenticación"]
    },
    "advanced_reporting": {
        "name": "Generación de Reportes Avanzados",
        "description": "Documentación auto-generada con plantillas personalizables",
        "icon": "📊",
        "category": "reporting",
        "requirements": ["Motor de plantillas", "Generador de gráficos"]
    },
    "code_quality_metrics": {
        "name": "Métricas de Calidad de Código",
        "description": "Puntuación de complejidad y análisis de mantenibilidad",
        "icon": "📈",
        "category": "quality",
        "requirements": ["Analizador estático", "Base de métricas"]
    },
    "api_integration": {
        "name": "Integración Empresarial",
        "description": "Gateway API con OpenAPI y webhooks",
        "icon": "🔌",
        "category": "integration",
        "requirements": ["API Gateway", "Sistema de webhooks"]
    },
    "ml_predictive_analysis": {
        "name": "Análisis Predictivo ML",
        "description": "Reconocimiento de patrones con machine learning",
        "icon": "🤖",
        "category": "ai",
        "requirements": ["Modelos ML entrenados", "GPU recomendada"]
    }
}

def get_format_info(format_key: str) -> Dict[str, Any]:
    """Get detailed information about a format."""
    return FORMAT_DESCRIPTIONS.get(format_key, {})

def get_enterprise_feature_info(feature_key: str) -> Dict[str, Any]:
    """Get detailed information about an enterprise feature."""
    return ENTERPRISE_FEATURES.get(feature_key, {})

def get_formats_by_category(category: str = None) -> Dict[str, Dict[str, Any]]:
    """Get formats filtered by category."""
    if category is None:
        return FORMAT_DESCRIPTIONS
    
    return {
        key: value for key, value in FORMAT_DESCRIPTIONS.items()
        if value.get("category") == category
    }

def get_enterprise_features_by_category(category: str = None) -> Dict[str, Dict[str, Any]]:
    """Get enterprise features filtered by category."""
    if category is None:
        return ENTERPRISE_FEATURES
    
    return {
        key: value for key, value in ENTERPRISE_FEATURES.items()
        if value.get("category") == category
    }
