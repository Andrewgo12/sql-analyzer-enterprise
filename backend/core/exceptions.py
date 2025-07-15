"""
Comprehensive Exception Handling System
Custom exceptions for SQL Analyzer Enterprise
"""

import traceback
from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories."""
    SYNTAX = "SYNTAX"
    SEMANTIC = "SEMANTIC"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    SCHEMA = "SCHEMA"
    LOGIC = "LOGIC"
    SYSTEM = "SYSTEM"
    VALIDATION = "VALIDATION"
    CONFIGURATION = "CONFIGURATION"
    NETWORK = "NETWORK"


class SQLAnalyzerException(Exception):
    """Base exception for SQL Analyzer."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.suggestions = suggestions or []
        self.traceback_info = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "details": self.details,
            "suggestions": self.suggestions,
            "traceback": self.traceback_info
        }


class SQLSyntaxError(SQLAnalyzerException):
    """SQL syntax error."""
    
    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        sql_snippet: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYNTAX,
            **kwargs
        )
        self.line = line
        self.column = column
        self.sql_snippet = sql_snippet
        
        if line is not None:
            self.details["line"] = line
        if column is not None:
            self.details["column"] = column
        if sql_snippet is not None:
            self.details["sql_snippet"] = sql_snippet


class SQLSemanticError(SQLAnalyzerException):
    """SQL semantic error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SEMANTIC,
            **kwargs
        )


class SQLPerformanceWarning(SQLAnalyzerException):
    """SQL performance warning."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            **kwargs
        )


class SQLSecurityError(SQLAnalyzerException):
    """SQL security vulnerability."""
    
    def __init__(
        self,
        message: str,
        vulnerability_type: Optional[str] = None,
        cwe_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            **kwargs
        )
        if vulnerability_type:
            self.details["vulnerability_type"] = vulnerability_type
        if cwe_id:
            self.details["cwe_id"] = cwe_id


class SchemaError(SQLAnalyzerException):
    """Schema-related error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SCHEMA,
            **kwargs
        )


class ValidationError(SQLAnalyzerException):
    """Validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )
        if field:
            self.details["field"] = field


class ConfigurationError(SQLAnalyzerException):
    """Configuration error."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )
        if config_key:
            self.details["config_key"] = config_key


class FileProcessingError(SQLAnalyzerException):
    """File processing error."""
    
    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
        if filename:
            self.details["filename"] = filename
        if file_size:
            self.details["file_size"] = file_size


class AnalysisError(SQLAnalyzerException):
    """Analysis process error."""
    
    def __init__(
        self,
        message: str,
        analysis_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
        if analysis_type:
            self.details["analysis_type"] = analysis_type


class FormatGenerationError(SQLAnalyzerException):
    """Format generation error."""
    
    def __init__(
        self,
        message: str,
        format_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
        if format_type:
            self.details["format_type"] = format_type


class NetworkError(SQLAnalyzerException):
    """Network-related error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class DatabaseConnectionError(SQLAnalyzerException):
    """Database connection error."""
    
    def __init__(
        self,
        message: str,
        database_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
        if database_url:
            # Don't include sensitive information in details
            self.details["database_type"] = database_url.split("://")[0] if "://" in database_url else "unknown"


class AuthenticationError(SQLAnalyzerException):
    """Authentication error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            **kwargs
        )


class AuthorizationError(SQLAnalyzerException):
    """Authorization error."""
    
    def __init__(self, message: str, required_permission: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            **kwargs
        )
        if required_permission:
            self.details["required_permission"] = required_permission


class RateLimitError(SQLAnalyzerException):
    """Rate limit exceeded error."""
    
    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        reset_time: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
        if limit:
            self.details["limit"] = limit
        if reset_time:
            self.details["reset_time"] = reset_time


class ResourceExhaustedError(SQLAnalyzerException):
    """Resource exhausted error."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            **kwargs
        )
        if resource_type:
            self.details["resource_type"] = resource_type


def handle_exception(exc: Exception) -> SQLAnalyzerException:
    """Convert generic exceptions to SQLAnalyzerException."""
    if isinstance(exc, SQLAnalyzerException):
        return exc
    
    # Map common exceptions
    if isinstance(exc, FileNotFoundError):
        return FileProcessingError(
            f"File not found: {exc}",
            suggestions=["Check if the file path is correct", "Ensure the file exists"]
        )
    
    if isinstance(exc, PermissionError):
        return FileProcessingError(
            f"Permission denied: {exc}",
            suggestions=["Check file permissions", "Run with appropriate privileges"]
        )
    
    if isinstance(exc, MemoryError):
        return ResourceExhaustedError(
            "Out of memory",
            resource_type="memory",
            suggestions=["Reduce file size", "Increase available memory", "Use streaming processing"]
        )
    
    if isinstance(exc, TimeoutError):
        return AnalysisError(
            f"Operation timed out: {exc}",
            suggestions=["Increase timeout limit", "Optimize query complexity", "Use batch processing"]
        )
    
    # Generic exception
    return SQLAnalyzerException(
        f"Unexpected error: {exc}",
        severity=ErrorSeverity.HIGH,
        details={"original_exception": str(exc)},
        suggestions=["Check logs for more details", "Contact support if issue persists"]
    )
