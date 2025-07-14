"""
SQL Analyzer and Corrector
A comprehensive Python tool for SQL file analysis, error detection, and database format conversion.

Author: SQL Analyzer Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "SQL Analyzer Team"

from .core.file_processor import FileProcessor
from .core.sql_parser import SQLParser
from .core.error_detector import ErrorDetector
from .core.schema_analyzer import SchemaAnalyzer
from .core.format_converter import FormatConverter
from .ui.cli_interface import CLIInterface

__all__ = [
    'FileProcessor',
    'SQLParser', 
    'ErrorDetector',
    'SchemaAnalyzer',
    'FormatConverter',
    'CLIInterface'
]
