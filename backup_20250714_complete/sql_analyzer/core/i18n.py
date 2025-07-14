"""
Internationalization (i18n) Support
Multilingual support for SQL Analyzer Enterprise
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class Language(Enum):
    """Supported languages."""
    SPANISH = "es"
    ENGLISH = "en"
    PORTUGUESE = "pt"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"


class I18nManager:
    """Internationalization manager."""
    
    def __init__(self, default_language: Language = Language.SPANISH):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_translations: Dict[str, str] = {}
        
        # Load translations
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files."""
        # Define translations directly in code for reliability
        self.translations = {
            Language.SPANISH.value: {
                # General terms
                "analysis": "Análisis",
                "error": "Error",
                "warning": "Advertencia",
                "success": "Éxito",
                "failed": "Falló",
                "completed": "Completado",
                "processing": "Procesando",
                "loading": "Cargando",
                "saving": "Guardando",
                "uploading": "Subiendo",
                "downloading": "Descargando",
                
                # File operations
                "file": "Archivo",
                "upload_file": "Subir Archivo",
                "select_file": "Seleccionar Archivo",
                "file_uploaded": "Archivo subido exitosamente",
                "file_too_large": "El archivo es demasiado grande",
                "invalid_file_type": "Tipo de archivo no válido",
                "file_not_found": "Archivo no encontrado",
                
                # Analysis terms
                "sql_analysis": "Análisis SQL",
                "syntax_error": "Error de Sintaxis",
                "semantic_error": "Error Semántico",
                "performance_warning": "Advertencia de Rendimiento",
                "security_vulnerability": "Vulnerabilidad de Seguridad",
                "schema_issue": "Problema de Esquema",
                "quality_score": "Puntuación de Calidad",
                "errors_found": "Errores Encontrados",
                "recommendations": "Recomendaciones",
                
                # Error types
                "critical": "Crítico",
                "high": "Alto",
                "medium": "Medio",
                "low": "Bajo",
                
                # Actions
                "analyze": "Analizar",
                "fix": "Corregir",
                "download": "Descargar",
                "export": "Exportar",
                "cancel": "Cancelar",
                "retry": "Reintentar",
                "continue": "Continuar",
                "back": "Atrás",
                "next": "Siguiente",
                "finish": "Finalizar",
                
                # Enterprise features
                "ultra_large_processing": "Procesamiento Ultra-Grande",
                "schema_visualization": "Visualización de Esquemas",
                "performance_optimization": "Optimización de Rendimiento",
                "security_audit": "Auditoría de Seguridad",
                "database_migration": "Migración de Base de Datos",
                "collaborative_analysis": "Análisis Colaborativo",
                "advanced_reporting": "Reportes Avanzados",
                "code_quality_metrics": "Métricas de Calidad de Código",
                "api_integration": "Integración API",
                "ml_predictive_analysis": "Análisis Predictivo ML",
                
                # Messages
                "welcome_message": "Bienvenido al Analizador SQL Empresarial",
                "analysis_started": "Análisis iniciado",
                "analysis_completed": "Análisis completado exitosamente",
                "analysis_failed": "El análisis falló",
                "no_errors_found": "No se encontraron errores",
                "multiple_errors_found": "Se encontraron múltiples errores",
                "generating_report": "Generando reporte",
                "report_generated": "Reporte generado exitosamente",
                
                # Format descriptions
                "enhanced_sql": "SQL Mejorado con comentarios inteligentes",
                "html_report": "Reporte HTML con CSS embebido",
                "interactive_html": "Dashboard HTML interactivo",
                "pdf_report": "Reporte PDF profesional",
                "json_analysis": "Datos JSON estructurados",
                "xml_report": "Reporte XML compatible",
                "csv_summary": "Resumen CSV tabular",
                "excel_workbook": "Libro Excel multi-hoja",
                "word_document": "Documento Word profesional",
                "markdown_docs": "Documentación Markdown",
                
                # Time expressions
                "seconds": "segundos",
                "minutes": "minutos",
                "hours": "horas",
                "days": "días",
                "ago": "hace",
                "remaining": "restante",
                
                # Status messages
                "connecting": "Conectando",
                "connected": "Conectado",
                "disconnected": "Desconectado",
                "reconnecting": "Reconectando",
                "timeout": "Tiempo agotado",
                "network_error": "Error de red",
                "server_error": "Error del servidor",
                "unauthorized": "No autorizado",
                "forbidden": "Prohibido",
                "not_found": "No encontrado",
                
                # Configuration
                "settings": "Configuración",
                "preferences": "Preferencias",
                "language": "Idioma",
                "theme": "Tema",
                "notifications": "Notificaciones",
                "advanced_options": "Opciones Avanzadas",
                
                # Help and support
                "help": "Ayuda",
                "documentation": "Documentación",
                "support": "Soporte",
                "contact": "Contacto",
                "about": "Acerca de",
                "version": "Versión",
                "license": "Licencia",
                
                # Validation messages
                "required_field": "Este campo es obligatorio",
                "invalid_format": "Formato inválido",
                "value_too_large": "Valor demasiado grande",
                "value_too_small": "Valor demasiado pequeño",
                "invalid_email": "Email inválido",
                "passwords_dont_match": "Las contraseñas no coinciden",
                
                # Progress indicators
                "step": "Paso",
                "of": "de",
                "progress": "Progreso",
                "estimated_time": "Tiempo estimado",
                "elapsed_time": "Tiempo transcurrido",
                "speed": "Velocidad",
                "eta": "Tiempo estimado de finalización"
            },
            
            Language.ENGLISH.value: {
                # General terms
                "analysis": "Analysis",
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "failed": "Failed",
                "completed": "Completed",
                "processing": "Processing",
                "loading": "Loading",
                "saving": "Saving",
                "uploading": "Uploading",
                "downloading": "Downloading",
                
                # File operations
                "file": "File",
                "upload_file": "Upload File",
                "select_file": "Select File",
                "file_uploaded": "File uploaded successfully",
                "file_too_large": "File is too large",
                "invalid_file_type": "Invalid file type",
                "file_not_found": "File not found",
                
                # Analysis terms
                "sql_analysis": "SQL Analysis",
                "syntax_error": "Syntax Error",
                "semantic_error": "Semantic Error",
                "performance_warning": "Performance Warning",
                "security_vulnerability": "Security Vulnerability",
                "schema_issue": "Schema Issue",
                "quality_score": "Quality Score",
                "errors_found": "Errors Found",
                "recommendations": "Recommendations",
                
                # Error types
                "critical": "Critical",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                
                # Actions
                "analyze": "Analyze",
                "fix": "Fix",
                "download": "Download",
                "export": "Export",
                "cancel": "Cancel",
                "retry": "Retry",
                "continue": "Continue",
                "back": "Back",
                "next": "Next",
                "finish": "Finish",
                
                # Enterprise features
                "ultra_large_processing": "Ultra-Large Processing",
                "schema_visualization": "Schema Visualization",
                "performance_optimization": "Performance Optimization",
                "security_audit": "Security Audit",
                "database_migration": "Database Migration",
                "collaborative_analysis": "Collaborative Analysis",
                "advanced_reporting": "Advanced Reporting",
                "code_quality_metrics": "Code Quality Metrics",
                "api_integration": "API Integration",
                "ml_predictive_analysis": "ML Predictive Analysis",
                
                # Messages
                "welcome_message": "Welcome to SQL Analyzer Enterprise",
                "analysis_started": "Analysis started",
                "analysis_completed": "Analysis completed successfully",
                "analysis_failed": "Analysis failed",
                "no_errors_found": "No errors found",
                "multiple_errors_found": "Multiple errors found",
                "generating_report": "Generating report",
                "report_generated": "Report generated successfully",
                
                # Format descriptions
                "enhanced_sql": "Enhanced SQL with intelligent comments",
                "html_report": "HTML report with embedded CSS",
                "interactive_html": "Interactive HTML dashboard",
                "pdf_report": "Professional PDF report",
                "json_analysis": "Structured JSON data",
                "xml_report": "Compatible XML report",
                "csv_summary": "Tabular CSV summary",
                "excel_workbook": "Multi-sheet Excel workbook",
                "word_document": "Professional Word document",
                "markdown_docs": "Markdown documentation",
                
                # Time expressions
                "seconds": "seconds",
                "minutes": "minutes",
                "hours": "hours",
                "days": "days",
                "ago": "ago",
                "remaining": "remaining",
                
                # Status messages
                "connecting": "Connecting",
                "connected": "Connected",
                "disconnected": "Disconnected",
                "reconnecting": "Reconnecting",
                "timeout": "Timeout",
                "network_error": "Network error",
                "server_error": "Server error",
                "unauthorized": "Unauthorized",
                "forbidden": "Forbidden",
                "not_found": "Not found",
                
                # Configuration
                "settings": "Settings",
                "preferences": "Preferences",
                "language": "Language",
                "theme": "Theme",
                "notifications": "Notifications",
                "advanced_options": "Advanced Options",
                
                # Help and support
                "help": "Help",
                "documentation": "Documentation",
                "support": "Support",
                "contact": "Contact",
                "about": "About",
                "version": "Version",
                "license": "License",
                
                # Validation messages
                "required_field": "This field is required",
                "invalid_format": "Invalid format",
                "value_too_large": "Value too large",
                "value_too_small": "Value too small",
                "invalid_email": "Invalid email",
                "passwords_dont_match": "Passwords don't match",
                
                # Progress indicators
                "step": "Step",
                "of": "of",
                "progress": "Progress",
                "estimated_time": "Estimated time",
                "elapsed_time": "Elapsed time",
                "speed": "Speed",
                "eta": "ETA"
            }
        }
        
        # Set fallback translations (Spanish as default)
        self.fallback_translations = self.translations[Language.SPANISH.value]
    
    def set_language(self, language: Language):
        """Set the current language."""
        self.current_language = language
    
    def get_language(self) -> Language:
        """Get the current language."""
        return self.current_language
    
    def translate(self, key: str, language: Optional[Language] = None, **kwargs) -> str:
        """Translate a key to the specified or current language."""
        target_language = language or self.current_language
        
        # Get translation
        translations = self.translations.get(target_language.value, {})
        translated = translations.get(key)
        
        # Fallback to default language if not found
        if translated is None:
            translated = self.fallback_translations.get(key, key)
        
        # Format with kwargs if provided
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return the unformatted string
                pass
        
        return translated
    
    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate."""
        return self.translate(key, **kwargs)
    
    def get_available_languages(self) -> List[Language]:
        """Get list of available languages."""
        return [Language(lang) for lang in self.translations.keys()]
    
    def get_language_name(self, language: Language) -> str:
        """Get the native name of a language."""
        names = {
            Language.SPANISH: "Español",
            Language.ENGLISH: "English",
            Language.PORTUGUESE: "Português",
            Language.FRENCH: "Français",
            Language.GERMAN: "Deutsch",
            Language.ITALIAN: "Italiano"
        }
        return names.get(language, language.value)


# Global i18n manager instance
_i18n_manager: Optional[I18nManager] = None


def get_i18n_manager() -> I18nManager:
    """Get the global i18n manager instance."""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def set_language(language: Language):
    """Set the global language."""
    get_i18n_manager().set_language(language)


def translate(key: str, **kwargs) -> str:
    """Translate a key using the global i18n manager."""
    return get_i18n_manager().translate(key, **kwargs)


def t(key: str, **kwargs) -> str:
    """Shorthand for translate using the global i18n manager."""
    return translate(key, **kwargs)


# Convenience functions for common translations
def get_error_severity_text(severity: str) -> str:
    """Get localized text for error severity."""
    severity_map = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low"
    }
    return translate(severity_map.get(severity.upper(), "medium"))


def get_status_text(status: str) -> str:
    """Get localized text for status."""
    status_map = {
        "processing": "processing",
        "completed": "completed",
        "failed": "failed",
        "loading": "loading",
        "connecting": "connecting",
        "connected": "connected",
        "disconnected": "disconnected"
    }
    return translate(status_map.get(status.lower(), status))


def format_time_ago(seconds: int) -> str:
    """Format time ago in localized format."""
    if seconds < 60:
        return translate("seconds_ago", seconds=seconds)
    elif seconds < 3600:
        minutes = seconds // 60
        return translate("minutes_ago", minutes=minutes)
    elif seconds < 86400:
        hours = seconds // 3600
        return translate("hours_ago", hours=hours)
    else:
        days = seconds // 86400
        return translate("days_ago", days=days)


def format_file_size(size_bytes: int) -> str:
    """Format file size in localized format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
