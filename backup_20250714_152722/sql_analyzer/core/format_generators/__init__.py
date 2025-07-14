"""
Format Generators Package

Comprehensive download format generators for SQL analysis results.
Supports 20+ different output formats with professional styling and content.
"""

from .base_generator import BaseFormatGenerator, FormatGeneratorError
from .sql_generator import EnhancedSQLGenerator
from .html_generator import HTMLReportGenerator, InteractiveHTMLGenerator
from .pdf_generator import PDFReportGenerator
from .json_generator import JSONAnalysisGenerator
from .xml_generator import XMLReportGenerator
from .csv_generator import CSVSummaryGenerator
from .excel_generator import ExcelWorkbookGenerator
from .word_generator import WordDocumentGenerator
from .markdown_generator import MarkdownDocumentationGenerator
from .latex_generator import LaTeXReportGenerator
from .remaining_generators import (
    PowerPointGenerator, SQLiteDatabaseGenerator, ZIPArchiveGenerator,
    PlainTextGenerator, YAMLConfigurationGenerator, SchemaDiagramGenerator,
    JupyterNotebookGenerator, PythonScriptGenerator
)

__all__ = [
    'BaseFormatGenerator',
    'FormatGeneratorError',
    'EnhancedSQLGenerator',
    'HTMLReportGenerator',
    'InteractiveHTMLGenerator',
    'PDFReportGenerator',
    'JSONAnalysisGenerator',
    'XMLReportGenerator',
    'CSVSummaryGenerator',
    'ExcelWorkbookGenerator',
    'WordDocumentGenerator',
    'MarkdownDocumentationGenerator',
    'LaTeXReportGenerator',
    'PowerPointGenerator',
    'SQLiteDatabaseGenerator',
    'ZIPArchiveGenerator',
    'PlainTextGenerator',
    'YAMLConfigurationGenerator',
    'SchemaDiagramGenerator',
    'JupyterNotebookGenerator',
    'PythonScriptGenerator'
]

# Format registry for easy access
FORMAT_REGISTRY = {
    'enhanced_sql': EnhancedSQLGenerator,
    'html_report': HTMLReportGenerator,
    'interactive_html': InteractiveHTMLGenerator,
    'pdf_report': PDFReportGenerator,
    'json_analysis': JSONAnalysisGenerator,
    'xml_report': XMLReportGenerator,
    'csv_summary': CSVSummaryGenerator,
    'excel_workbook': ExcelWorkbookGenerator,
    'word_document': WordDocumentGenerator,
    'markdown_docs': MarkdownDocumentationGenerator,
    'latex_report': LaTeXReportGenerator,
    'powerpoint': PowerPointGenerator,
    'sqlite_database': SQLiteDatabaseGenerator,
    'zip_archive': ZIPArchiveGenerator,
    'plain_text': PlainTextGenerator,
    'yaml_config': YAMLConfigurationGenerator,
    'schema_diagram': SchemaDiagramGenerator,
    'jupyter_notebook': JupyterNotebookGenerator,
    'python_script': PythonScriptGenerator
}

def get_format_generator(format_type_or_class: str) -> BaseFormatGenerator:
    """
    Get a format generator instance by type or class name.

    Args:
        format_type_or_class: The format type identifier or class name

    Returns:
        Format generator instance

    Raises:
        FormatGeneratorError: If format type is not supported
    """
    # First try as format type
    if format_type_or_class in FORMAT_REGISTRY:
        generator_class = FORMAT_REGISTRY[format_type_or_class]
        return generator_class()

    # Then try as class name
    class_registry = {
        'EnhancedSQLGenerator': EnhancedSQLGenerator,
        'HTMLReportGenerator': HTMLReportGenerator,
        'InteractiveHTMLGenerator': InteractiveHTMLGenerator,
        'PDFReportGenerator': PDFReportGenerator,
        'JSONAnalysisGenerator': JSONAnalysisGenerator,
        'XMLReportGenerator': XMLReportGenerator,
        'CSVSummaryGenerator': CSVSummaryGenerator,
        'ExcelWorkbookGenerator': ExcelWorkbookGenerator,
        'WordDocumentGenerator': WordDocumentGenerator,
        'MarkdownDocumentationGenerator': MarkdownDocumentationGenerator,
        'LaTeXReportGenerator': LaTeXReportGenerator,
        'PowerPointGenerator': PowerPointGenerator,
        'SQLiteDatabaseGenerator': SQLiteDatabaseGenerator,
        'ZIPArchiveGenerator': ZIPArchiveGenerator,
        'PlainTextGenerator': PlainTextGenerator,
        'YAMLConfigurationGenerator': YAMLConfigurationGenerator,
        'SchemaDiagramGenerator': SchemaDiagramGenerator,
        'JupyterNotebookGenerator': JupyterNotebookGenerator,
        'PythonScriptGenerator': PythonScriptGenerator
    }

    if format_type_or_class in class_registry:
        generator_class = class_registry[format_type_or_class]
        return generator_class()

    raise FormatGeneratorError(f"Formato no soportado: {format_type_or_class}")

def get_available_formats() -> dict:
    """
    Get all available format types with their descriptions.
    
    Returns:
        Dictionary mapping format types to descriptions
    """
    return {
        'enhanced_sql': {
            'name': 'SQL Mejorado',
            'description': 'Archivo SQL con comentarios inteligentes y correcciones',
            'extension': '.sql',
            'mime_type': 'text/sql'
        },
        'html_report': {
            'name': 'Reporte HTML',
            'description': 'Reporte HTML con CSS embebido y elementos interactivos',
            'extension': '.html',
            'mime_type': 'text/html'
        },
        'interactive_html': {
            'name': 'Dashboard HTML Interactivo',
            'description': 'Dashboard HTML con gráficos en tiempo real usando Chart.js',
            'extension': '.html',
            'mime_type': 'text/html'
        },
        'pdf_report': {
            'name': 'Reporte PDF',
            'description': 'Reporte PDF profesional con formato y gráficos',
            'extension': '.pdf',
            'mime_type': 'application/pdf'
        },
        'json_analysis': {
            'name': 'Datos JSON',
            'description': 'Datos de análisis estructurados en formato JSON',
            'extension': '.json',
            'mime_type': 'application/json'
        },
        'xml_report': {
            'name': 'Reporte XML',
            'description': 'Resultados de análisis en formato XML compatible con esquemas',
            'extension': '.xml',
            'mime_type': 'application/xml'
        },
        'csv_summary': {
            'name': 'Resumen CSV',
            'description': 'Resumen tabular de errores y métricas en formato CSV',
            'extension': '.csv',
            'mime_type': 'text/csv'
        },
        'excel_workbook': {
            'name': 'Libro Excel',
            'description': 'Análisis multi-hoja con gráficos usando Excel',
            'extension': '.xlsx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        },
        'word_document': {
            'name': 'Documento Word',
            'description': 'Reporte profesional en formato Microsoft Word',
            'extension': '.docx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        },
        'markdown_docs': {
            'name': 'Documentación Markdown',
            'description': 'Documentación compatible con GitHub en formato Markdown',
            'extension': '.md',
            'mime_type': 'text/markdown'
        },
        'latex_report': {
            'name': 'Reporte LaTeX',
            'description': 'Reporte académico con formato LaTeX profesional',
            'extension': '.tex',
            'mime_type': 'application/x-latex'
        },
        'powerpoint': {
            'name': 'Presentación PowerPoint',
            'description': 'Diapositivas de resumen ejecutivo en PowerPoint',
            'extension': '.pptx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        },
        'sqlite_database': {
            'name': 'Base de Datos SQLite',
            'description': 'Resultados de análisis consultables en base de datos SQLite',
            'extension': '.db',
            'mime_type': 'application/x-sqlite3'
        },
        'zip_archive': {
            'name': 'Archivo ZIP',
            'description': 'Múltiples formatos empaquetados en archivo ZIP',
            'extension': '.zip',
            'mime_type': 'application/zip'
        },
        'plain_text': {
            'name': 'Reporte de Texto',
            'description': 'Salida compatible con consola en texto plano',
            'extension': '.txt',
            'mime_type': 'text/plain'
        },
        'yaml_config': {
            'name': 'Configuración YAML',
            'description': 'Exportación de configuración estructurada en YAML',
            'extension': '.yaml',
            'mime_type': 'application/x-yaml'
        },
        'schema_diagram': {
            'name': 'Diagrama de Esquema',
            'description': 'Gráficos vectoriales del esquema de base de datos',
            'extension': '.svg',
            'mime_type': 'image/svg+xml'
        },
        'jupyter_notebook': {
            'name': 'Notebook Jupyter',
            'description': 'Notebook de análisis ejecutable en Jupyter',
            'extension': '.ipynb',
            'mime_type': 'application/x-ipynb+json'
        },
        'python_script': {
            'name': 'Script Python',
            'description': 'Generador de script de análisis independiente en Python',
            'extension': '.py',
            'mime_type': 'text/x-python'
        }
    }
