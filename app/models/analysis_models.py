#!/usr/bin/env python3
"""
ANALYSIS MODELS
Core data models for SQL analysis system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import uuid

class DatabaseType(Enum):
    """Supported database types"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQL_SERVER = "sql_server"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    CASSANDRA = "cassandra"
    REDIS = "redis"
    GENERIC = "generic"

class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisType(Enum):
    """Types of analysis"""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SCHEMA = "schema"
    COMPREHENSIVE = "comprehensive"

@dataclass
class SQLError:
    """SQL Error representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    line_number: int = 0
    column: int = 0
    error_type: str = ""
    severity: ErrorSeverity = ErrorSeverity.LOW
    message: str = ""
    suggestion: str = ""
    auto_fixable: bool = False
    fixed_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'line_number': self.line_number,
            'column': self.column,
            'error_type': self.error_type,
            'severity': self.severity.value,
            'message': self.message,
            'suggestion': self.suggestion,
            'auto_fixable': self.auto_fixable,
            'fixed_code': self.fixed_code,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class SecurityVulnerability:
    """Security vulnerability representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    line_number: int = 0
    vulnerability_type: str = ""
    risk_level: ErrorSeverity = ErrorSeverity.LOW
    description: str = ""
    mitigation: str = ""
    code_snippet: str = ""
    cwe_id: str = ""
    owasp_category: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'line_number': self.line_number,
            'vulnerability_type': self.vulnerability_type,
            'risk_level': self.risk_level.value,
            'description': self.description,
            'mitigation': self.mitigation,
            'code_snippet': self.code_snippet,
            'cwe_id': self.cwe_id,
            'owasp_category': self.owasp_category,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class PerformanceIssue:
    """Performance issue representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    line_number: int = 0
    issue_type: str = ""
    impact: str = ""
    description: str = ""
    recommendation: str = ""
    code_snippet: str = ""
    estimated_improvement: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'line_number': self.line_number,
            'issue_type': self.issue_type,
            'impact': self.impact,
            'description': self.description,
            'recommendation': self.recommendation,
            'code_snippet': self.code_snippet,
            'estimated_improvement': self.estimated_improvement,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class TableInfo:
    """Database table information"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    columns: List[Dict[str, Any]] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    estimated_rows: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'columns': self.columns,
            'primary_keys': self.primary_keys,
            'foreign_keys': self.foreign_keys,
            'indexes': self.indexes,
            'constraints': self.constraints,
            'estimated_rows': self.estimated_rows,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class IntelligentComment:
    """Intelligent comment representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    line_number: int = 0
    comment: str = ""
    comment_type: str = "explanation"  # explanation, warning, optimization
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'line_number': self.line_number,
            'comment': self.comment,
            'comment_type': self.comment_type,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_hash: str = ""
    filename: str = ""
    processing_time: float = 0.0
    database_type: DatabaseType = DatabaseType.GENERIC
    total_lines: int = 0
    total_statements: int = 0
    syntax_errors: List[SQLError] = field(default_factory=list)
    semantic_errors: List[SQLError] = field(default_factory=list)
    performance_issues: List[PerformanceIssue] = field(default_factory=list)
    security_vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    tables: List[TableInfo] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    quality_score: int = 0
    complexity_score: int = 0
    recommendations: List[str] = field(default_factory=list)
    corrected_sql: str = ""
    intelligent_comments: List[IntelligentComment] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'file_hash': self.file_hash,
            'filename': self.filename,
            'processing_time': self.processing_time,
            'database_type': self.database_type.value,
            'total_lines': self.total_lines,
            'total_statements': self.total_statements,
            'syntax_errors': [error.to_dict() for error in self.syntax_errors],
            'semantic_errors': [error.to_dict() for error in self.semantic_errors],
            'performance_issues': [issue.to_dict() for issue in self.performance_issues],
            'security_vulnerabilities': [vuln.to_dict() for vuln in self.security_vulnerabilities],
            'tables': [table.to_dict() for table in self.tables],
            'relationships': self.relationships,
            'quality_score': self.quality_score,
            'complexity_score': self.complexity_score,
            'recommendations': self.recommendations,
            'corrected_sql': self.corrected_sql,
            'intelligent_comments': [comment.to_dict() for comment in self.intelligent_comments],
            'created_at': self.created_at.isoformat()
        }
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error summary by severity"""
        summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        all_errors = self.syntax_errors + self.semantic_errors
        for error in all_errors:
            summary[error.severity.value] += 1
        
        return summary
    
    def get_security_summary(self) -> Dict[str, int]:
        """Get security vulnerability summary"""
        summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for vuln in self.security_vulnerabilities:
            summary[vuln.risk_level.value] += 1
        
        return summary
    
    def get_quality_level(self) -> str:
        """Get quality level description"""
        if self.quality_score >= 90:
            return "Excellent"
        elif self.quality_score >= 75:
            return "Good"
        elif self.quality_score >= 60:
            return "Fair"
        else:
            return "Poor"
    
    def get_complexity_level(self) -> str:
        """Get complexity level description"""
        if self.complexity_score <= 25:
            return "Low"
        elif self.complexity_score <= 50:
            return "Moderate"
        elif self.complexity_score <= 75:
            return "High"
        else:
            return "Very High"

@dataclass
class FileInfo:
    """File information model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    size: int = 0
    encoding: str = "utf-8"
    line_count: int = 0
    hash_md5: str = ""
    hash_sha256: str = ""
    processing_time: float = 0.0
    is_valid: bool = True
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'size': self.size,
            'encoding': self.encoding,
            'line_count': self.line_count,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256,
            'processing_time': self.processing_time,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class ExportResult:
    """Export result model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    format_type: str = ""
    filename: str = ""
    content: str = ""
    size: int = 0
    mime_type: str = ""
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'format_type': self.format_type,
            'filename': self.filename,
            'size': self.size,
            'mime_type': self.mime_type,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }
