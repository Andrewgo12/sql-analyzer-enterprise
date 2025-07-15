"""
SQL Analyzer Enterprise Backend
Módulos reorganizados para arquitectura limpia
"""

__version__ = '2.0.0'
__author__ = 'SQL Analyzer Team'

from .core.sql_analyzer import SQLAnalyzer
from .utils.file_handler import FileHandler
from .utils.validators import FileValidator

__all__ = ['SQLAnalyzer', 'FileHandler', 'FileValidator']
