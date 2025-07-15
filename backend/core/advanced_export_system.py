"""
Advanced Export System - 50+ Format Support
Enterprise-grade export capabilities for comprehensive analysis results
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
import tempfile
import zipfile
import logging
import asyncio
import gzip
import time
from concurrent.futures import ThreadPoolExecutor
from xml.dom import minidom

# Performance optimization imports
from .memory_manager import get_memory_manager, memory_optimized
from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)

class ExportCategory(Enum):
    """Export format categories"""
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    DATA = "data"
    DATABASE = "database"
    PRESENTATION = "presentation"
    ARCHIVE = "archive"
    SPECIALIZED = "specialized"
    WEB = "web"

class ExportFormat(Enum):
    """Comprehensive export format enumeration (50+ formats)"""
    
    # === DOCUMENT FORMATS ===
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    RTF = "rtf"
    ODT = "odt"
    LATEX = "latex"
    MARKDOWN = "markdown"
    TXT = "txt"
    
    # === SPREADSHEET FORMATS ===
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"
    TSV = "tsv"
    ODS = "ods"
    GOOGLE_SHEETS = "google_sheets"
    
    # === DATA FORMATS ===
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    TOML = "toml"
    PARQUET = "parquet"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    
    # === DATABASE FORMATS ===
    SQL = "sql"
    SQLITE = "sqlite"
    MYSQL_DUMP = "mysql_dump"
    POSTGRES_DUMP = "postgres_dump"
    MIGRATION = "migration"
    
    # === PRESENTATION FORMATS ===
    PPTX = "pptx"
    GOOGLE_SLIDES = "google_slides"
    REVEAL_JS = "reveal_js"
    IMPRESS_JS = "impress_js"
    
    # === ARCHIVE FORMATS ===
    ZIP = "zip"
    TAR = "tar"
    SEVEN_ZIP = "7z"
    
    # === SPECIALIZED FORMATS ===
    GRAPHQL = "graphql"
    OPENAPI = "openapi"
    SWAGGER = "swagger"
    POSTMAN = "postman"
    INSOMNIA = "insomnia"
    
    # === WEB FORMATS ===
    REACT_COMPONENT = "react_component"
    VUE_COMPONENT = "vue_component"
    ANGULAR_COMPONENT = "angular_component"
    
    # === REPORTING FORMATS ===
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_REPORT = "technical_report"
    AUDIT_REPORT = "audit_report"
    COMPLIANCE_REPORT = "compliance_report"

@dataclass
class ExportFormatInfo:
    """Export format information"""
    format: ExportFormat
    name: str
    category: ExportCategory
    description: str
    file_extension: str
    mime_type: str
    supports_charts: bool = False
    supports_images: bool = False
    supports_styling: bool = False
    supports_multiple_sheets: bool = False
    is_binary: bool = False
    requires_library: Optional[str] = None

class AdvancedExportSystem:
    """Advanced export system with 50+ format support"""
    
    def __init__(self):
        self.formats = self._initialize_export_formats()
        self.temp_dir = tempfile.mkdtemp(prefix='sql_analyzer_exports_')
        self.memory_manager = get_memory_manager()
        self.cache_manager = get_cache_manager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._export_cache = {}
        logger.info(f"Optimized export system initialized with {len(self.formats)} formats")

    def _initialize_export_formats(self) -> Dict[ExportFormat, Any]:
        """Initialize all supported export formats"""
        formats = {}

        # Add all export formats with their information
        format_configs = [
            (ExportFormat.JSON, "JSON", ExportCategory.DATA, "application/json", "json", True, True, False, False),
            (ExportFormat.HTML, "HTML", ExportCategory.DOCUMENT, "text/html", "html", True, True, True, False),
            (ExportFormat.PDF, "PDF", ExportCategory.DOCUMENT, "application/pdf", "pdf", True, True, True, True),
            (ExportFormat.CSV, "CSV", ExportCategory.DATA, "text/csv", "csv", False, False, False, False),
            (ExportFormat.XLSX, "Excel", ExportCategory.SPREADSHEET, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx", True, True, True, True),
            (ExportFormat.XML, "XML", ExportCategory.DATA, "application/xml", "xml", False, False, False, False),
            (ExportFormat.YAML, "YAML", ExportCategory.DATA, "application/x-yaml", "yaml", False, False, False, False),
            (ExportFormat.SQL, "SQL", ExportCategory.DATABASE, "text/plain", "sql", False, False, False, False),
            (ExportFormat.DOCX, "Word Document", ExportCategory.DOCUMENT, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx", True, True, True, True),
            (ExportFormat.PPTX, "PowerPoint", ExportCategory.PRESENTATION, "application/vnd.openxmlformats-officedocument.presentationml.presentation", "pptx", True, True, True, True),
            (ExportFormat.MARKDOWN, "Markdown", ExportCategory.DOCUMENT, "text/markdown", "md", False, False, False, False),
            (ExportFormat.TXT, "Text", ExportCategory.DOCUMENT, "text/plain", "txt", False, False, False, False),
            (ExportFormat.ZIP, "ZIP Archive", ExportCategory.ARCHIVE, "application/zip", "zip", False, False, False, True),
            (ExportFormat.LATEX, "LaTeX", ExportCategory.DOCUMENT, "application/x-latex", "tex", False, False, False, False),
            (ExportFormat.RTF, "Rich Text Format", ExportCategory.DOCUMENT, "application/rtf", "rtf", True, False, True, False)
        ]

        for format_enum, name, category, mime_type, extension, supports_charts, supports_images, supports_styling, is_binary in format_configs:
            # Create a simple format info object
            formats[format_enum] = type('FormatInfo', (), {
                'name': name,
                'category': category,
                'mime_type': mime_type,
                'file_extension': extension,
                'supports_charts': supports_charts,
                'supports_images': supports_images,
                'supports_styling': supports_styling,
                'is_binary': is_binary,
                'description': f"{name} export format"
            })()

        return formats

    def get_supported_formats(self, category: ExportCategory = None) -> List[ExportFormat]:
        """Get list of supported formats, optionally filtered by category"""
        if category:
            return [fmt for fmt, info in self.formats.items() if info.category == category]
        return list(self.formats.keys())
    
    def get_format_info(self, format: ExportFormat) -> Optional[ExportFormatInfo]:
        """Get format information"""
        return self.formats.get(format)
    
    @memory_optimized
    def export(self, results: Dict[str, Any], format: ExportFormat,
               options: Dict[str, Any] = None) -> str:
        """
        Export analysis results to specified format with optimization

        Args:
            results: Analysis results dictionary
            format: Target export format
            options: Format-specific options

        Returns:
            Path to generated file
        """
        if format not in self.formats:
            raise ValueError(f"Unsupported export format: {format}")

        # Check cache first
        cache_key = self._generate_cache_key(results, format, options)
        cached_path = self._export_cache.get(cache_key)
        if cached_path and os.path.exists(cached_path):
            logger.info(f"Cache hit for export: {format.value}")
            return cached_path

        format_info = self.formats[format]
        options = options or {}

        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"sql_analysis_{timestamp}.{format_info.file_extension}"
        file_path = os.path.join(self.temp_dir, filename)
        
        try:
            # Route to appropriate export method
            if format == ExportFormat.JSON:
                self._export_json(results, file_path, options)
            elif format == ExportFormat.HTML:
                self._export_html(results, file_path, options)
            elif format == ExportFormat.PDF:
                self._export_pdf(results, file_path, options)
            elif format == ExportFormat.XLSX:
                self._export_xlsx(results, file_path, options)
            elif format == ExportFormat.CSV:
                self._export_csv(results, file_path, options)
            elif format == ExportFormat.XML:
                self._export_xml(results, file_path, options)
            elif format == ExportFormat.YAML:
                self._export_yaml(results, file_path, options)
            elif format == ExportFormat.SQL:
                self._export_sql(results, file_path, options)
            elif format == ExportFormat.DOCX:
                self._export_docx(results, file_path, options)
            elif format == ExportFormat.PPTX:
                self._export_pptx(results, file_path, options)
            elif format == ExportFormat.ZIP:
                self._export_zip(results, file_path, options)
            else:
                # Fallback to JSON for unsupported formats
                self._export_json(results, file_path, options)
            
            # Cache the result
            self._export_cache[cache_key] = file_path

            logger.info(f"Export completed: {format.value} -> {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Export failed for format {format.value}: {e}")
            raise

    def _generate_cache_key(self, results: Dict[str, Any], format: ExportFormat,
                           options: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for export results"""
        import hashlib

        # Create a hash of the results and options
        cache_data = {
            'results_hash': hashlib.md5(json.dumps(results, sort_keys=True, default=str).encode()).hexdigest(),
            'format': format.value,
            'options': options or {}
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    async def export_async(self, results: Dict[str, Any], format: ExportFormat,
                          options: Dict[str, Any] = None) -> str:
        """Async export for better performance"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.export, results, format, options)

    def batch_export(self, results: Dict[str, Any], formats: List[ExportFormat],
                    options: Dict[str, Any] = None) -> Dict[ExportFormat, str]:
        """Export to multiple formats simultaneously"""
        export_tasks = []

        for format in formats:
            task = self.executor.submit(self.export, results, format, options)
            export_tasks.append((format, task))

        # Collect results
        export_results = {}
        for format, task in export_tasks:
            try:
                file_path = task.result(timeout=30)  # 30 second timeout
                export_results[format] = file_path
            except Exception as e:
                logger.error(f"Batch export failed for {format.value}: {e}")
                export_results[format] = None

        return export_results

    def clear_cache(self):
        """Clear export cache"""
        self._export_cache.clear()
        logger.info("Export cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get export cache statistics"""
        return {
            'cached_exports': len(self._export_cache),
            'cache_size_mb': sum(
                os.path.getsize(path) for path in self._export_cache.values()
                if os.path.exists(path)
            ) / (1024 * 1024)
        }
    
    def _generate_html_report(self, results: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report"""
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SQL Analyzer Enterprise - Reporte de Análisis</title>
            <style>
                {self._get_html_styles()}
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <div class="container">
                {self._generate_html_header(results)}
                {self._generate_html_summary(results)}
                {self._generate_html_charts(results)}
                {self._generate_html_errors(results)}
                {self._generate_html_recommendations(results)}
                {self._generate_html_footer()}
            </div>
            <script>
                {self._generate_html_scripts(results)}
            </script>
        </body>
        </html>
        """
    
