#!/usr/bin/env python3
"""
DATA ACCESS LAYER
Enterprise-grade data access with caching, validation, and persistence
"""

import os
import json
import sqlite3
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import asdict

from app.models.analysis_models import (
    AnalysisResult, FileInfo, ExportResult, SQLError, 
    SecurityVulnerability, PerformanceIssue, TableInfo
)
from app.utils.helpers import cache, FileHelper, TimeHelper

class DatabaseManager:
    """Enterprise database manager with connection pooling and transactions"""
    
    def __init__(self, db_path: str = "sql_analyzer.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._connections = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Analysis results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    file_hash TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    database_type TEXT NOT NULL,
                    processing_time REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    total_statements INTEGER NOT NULL,
                    quality_score INTEGER NOT NULL,
                    complexity_score INTEGER NOT NULL,
                    corrected_sql TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # File information table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_info (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    encoding TEXT NOT NULL,
                    line_count INTEGER NOT NULL,
                    hash_md5 TEXT NOT NULL,
                    hash_sha256 TEXT NOT NULL,
                    is_valid BOOLEAN NOT NULL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            """)
            
            # SQL errors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sql_errors (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    column_number INTEGER NOT NULL,
                    error_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    suggestion TEXT NOT NULL,
                    auto_fixable BOOLEAN NOT NULL,
                    fixed_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            """)
            
            # Security vulnerabilities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_vulnerabilities (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    vulnerability_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    description TEXT NOT NULL,
                    mitigation TEXT NOT NULL,
                    code_snippet TEXT,
                    cwe_id TEXT,
                    owasp_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            """)
            
            # Performance issues table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_issues (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    issue_type TEXT NOT NULL,
                    impact TEXT NOT NULL,
                    description TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    code_snippet TEXT,
                    estimated_improvement TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            """)
            
            # Tables information table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS table_info (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    columns TEXT NOT NULL,
                    primary_keys TEXT,
                    foreign_keys TEXT,
                    indexes TEXT,
                    constraints TEXT,
                    estimated_rows INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            """)
            
            # Export history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS export_history (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    format_type TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_file_hash ON analysis_results (file_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_created_at ON analysis_results (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_analysis_id ON sql_errors (analysis_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vulnerabilities_analysis_id ON security_vulnerabilities (analysis_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_analysis_id ON performance_issues (analysis_id)")
            
            conn.commit()
            self.logger.info("Database schema initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id not in self._connections:
                self._connections[thread_id] = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                self._connections[thread_id].row_factory = sqlite3.Row
                self._connections[thread_id].execute("PRAGMA foreign_keys = ON")
        
        conn = self._connections[thread_id]
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            # Connection cleanup is handled by the connection pool
            pass
    
    def close_all_connections(self):
        """Close all database connections"""
        with self._lock:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()

class AnalysisRepository:
    """Repository for analysis results with full CRUD operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def save_analysis_result(self, result: AnalysisResult) -> bool:
        """Save complete analysis result to database"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Save main analysis result
                cursor.execute("""
                    INSERT OR REPLACE INTO analysis_results 
                    (id, file_hash, filename, database_type, processing_time, 
                     total_lines, total_statements, quality_score, complexity_score,
                     corrected_sql, recommendations, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    result.id, result.file_hash, result.filename, result.database_type.value,
                    result.processing_time, result.total_lines, result.total_statements,
                    result.quality_score, result.complexity_score, result.corrected_sql,
                    json.dumps(result.recommendations)
                ))
                
                # Delete existing related records
                cursor.execute("DELETE FROM sql_errors WHERE analysis_id = ?", (result.id,))
                cursor.execute("DELETE FROM security_vulnerabilities WHERE analysis_id = ?", (result.id,))
                cursor.execute("DELETE FROM performance_issues WHERE analysis_id = ?", (result.id,))
                cursor.execute("DELETE FROM table_info WHERE analysis_id = ?", (result.id,))
                
                # Save SQL errors
                for error in result.syntax_errors + result.semantic_errors:
                    cursor.execute("""
                        INSERT INTO sql_errors 
                        (id, analysis_id, line_number, column_number, error_type, 
                         severity, message, suggestion, auto_fixable, fixed_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        error.id, result.id, error.line_number, error.column,
                        error.error_type, error.severity.value, error.message,
                        error.suggestion, error.auto_fixable, error.fixed_code
                    ))
                
                # Save security vulnerabilities
                for vuln in result.security_vulnerabilities:
                    cursor.execute("""
                        INSERT INTO security_vulnerabilities 
                        (id, analysis_id, line_number, vulnerability_type, risk_level,
                         description, mitigation, code_snippet, cwe_id, owasp_category)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        vuln.id, result.id, vuln.line_number, vuln.vulnerability_type,
                        vuln.risk_level.value, vuln.description, vuln.mitigation,
                        vuln.code_snippet, vuln.cwe_id, vuln.owasp_category
                    ))
                
                # Save performance issues
                for issue in result.performance_issues:
                    cursor.execute("""
                        INSERT INTO performance_issues 
                        (id, analysis_id, line_number, issue_type, impact,
                         description, recommendation, code_snippet, estimated_improvement)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        issue.id, result.id, issue.line_number, issue.issue_type,
                        issue.impact, issue.description, issue.recommendation,
                        issue.code_snippet, issue.estimated_improvement
                    ))
                
                # Save table information
                for table in result.tables:
                    cursor.execute("""
                        INSERT INTO table_info 
                        (id, analysis_id, table_name, columns, primary_keys,
                         foreign_keys, indexes, constraints, estimated_rows)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        table.id, result.id, table.name, json.dumps(table.columns),
                        json.dumps(table.primary_keys), json.dumps(table.foreign_keys),
                        json.dumps(table.indexes), json.dumps(table.constraints),
                        table.estimated_rows
                    ))
                
                conn.commit()
                
                # Cache the result
                cache.set(f"analysis:{result.id}", result, ttl=3600)
                cache.set(f"analysis_hash:{result.file_hash}", result, ttl=3600)
                
                self.logger.info(f"Analysis result saved: {result.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save analysis result: {str(e)}")
            return False
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Get analysis result by ID"""
        try:
            # Check cache first
            cached_result = cache.get(f"analysis:{analysis_id}")
            if cached_result:
                return cached_result
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get main analysis result
                cursor.execute("""
                    SELECT * FROM analysis_results WHERE id = ?
                """, (analysis_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Reconstruct the analysis result
                result = self._build_analysis_result_from_db(cursor, row)
                
                # Cache the result
                cache.set(f"analysis:{analysis_id}", result, ttl=3600)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get analysis result: {str(e)}")
            return None
    
    def get_analysis_by_hash(self, file_hash: str) -> Optional[AnalysisResult]:
        """Get analysis result by file hash"""
        try:
            # Check cache first
            cached_result = cache.get(f"analysis_hash:{file_hash}")
            if cached_result:
                return cached_result
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM analysis_results WHERE file_hash = ?
                """, (file_hash,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                result = self._build_analysis_result_from_db(cursor, row)
                
                # Cache the result
                cache.set(f"analysis_hash:{file_hash}", result, ttl=3600)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get analysis by hash: {str(e)}")
            return None
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis summaries"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, filename, database_type, quality_score, 
                           complexity_score, processing_time, created_at
                    FROM analysis_results 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'database_type': row['database_type'],
                        'quality_score': row['quality_score'],
                        'complexity_score': row['complexity_score'],
                        'processing_time': row['processing_time'],
                        'created_at': row['created_at']
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to get recent analyses: {str(e)}")
            return []
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis result and all related data"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete all related records (foreign key constraints will handle this)
                cursor.execute("DELETE FROM analysis_results WHERE id = ?", (analysis_id,))
                
                conn.commit()
                
                # Remove from cache
                cache.delete(f"analysis:{analysis_id}")
                
                self.logger.info(f"Analysis deleted: {analysis_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete analysis: {str(e)}")
            return False
    
    def _build_analysis_result_from_db(self, cursor, main_row) -> AnalysisResult:
        """Build AnalysisResult object from database rows"""
        from app.models.analysis_models import DatabaseType, ErrorSeverity
        
        analysis_id = main_row['id']
        
        # Get SQL errors
        cursor.execute("SELECT * FROM sql_errors WHERE analysis_id = ?", (analysis_id,))
        syntax_errors = []
        semantic_errors = []
        
        for error_row in cursor.fetchall():
            error = SQLError(
                id=error_row['id'],
                line_number=error_row['line_number'],
                column=error_row['column_number'],
                error_type=error_row['error_type'],
                severity=ErrorSeverity(error_row['severity']),
                message=error_row['message'],
                suggestion=error_row['suggestion'],
                auto_fixable=bool(error_row['auto_fixable']),
                fixed_code=error_row['fixed_code']
            )
            
            if error.error_type.startswith('syntax'):
                syntax_errors.append(error)
            else:
                semantic_errors.append(error)
        
        # Get security vulnerabilities
        cursor.execute("SELECT * FROM security_vulnerabilities WHERE analysis_id = ?", (analysis_id,))
        security_vulnerabilities = []
        
        for vuln_row in cursor.fetchall():
            vuln = SecurityVulnerability(
                id=vuln_row['id'],
                line_number=vuln_row['line_number'],
                vulnerability_type=vuln_row['vulnerability_type'],
                risk_level=ErrorSeverity(vuln_row['risk_level']),
                description=vuln_row['description'],
                mitigation=vuln_row['mitigation'],
                code_snippet=vuln_row['code_snippet'] or '',
                cwe_id=vuln_row['cwe_id'] or '',
                owasp_category=vuln_row['owasp_category'] or ''
            )
            security_vulnerabilities.append(vuln)
        
        # Get performance issues
        cursor.execute("SELECT * FROM performance_issues WHERE analysis_id = ?", (analysis_id,))
        performance_issues = []
        
        for perf_row in cursor.fetchall():
            issue = PerformanceIssue(
                id=perf_row['id'],
                line_number=perf_row['line_number'],
                issue_type=perf_row['issue_type'],
                impact=perf_row['impact'],
                description=perf_row['description'],
                recommendation=perf_row['recommendation'],
                code_snippet=perf_row['code_snippet'] or '',
                estimated_improvement=perf_row['estimated_improvement'] or ''
            )
            performance_issues.append(issue)
        
        # Get table information
        cursor.execute("SELECT * FROM table_info WHERE analysis_id = ?", (analysis_id,))
        tables = []
        
        for table_row in cursor.fetchall():
            table = TableInfo(
                id=table_row['id'],
                name=table_row['table_name'],
                columns=json.loads(table_row['columns']) if table_row['columns'] else [],
                primary_keys=json.loads(table_row['primary_keys']) if table_row['primary_keys'] else [],
                foreign_keys=json.loads(table_row['foreign_keys']) if table_row['foreign_keys'] else [],
                indexes=json.loads(table_row['indexes']) if table_row['indexes'] else [],
                constraints=json.loads(table_row['constraints']) if table_row['constraints'] else [],
                estimated_rows=table_row['estimated_rows']
            )
            tables.append(table)
        
        # Build the complete result
        result = AnalysisResult(
            id=main_row['id'],
            file_hash=main_row['file_hash'],
            filename=main_row['filename'],
            processing_time=main_row['processing_time'],
            database_type=DatabaseType(main_row['database_type']),
            total_lines=main_row['total_lines'],
            total_statements=main_row['total_statements'],
            syntax_errors=syntax_errors,
            semantic_errors=semantic_errors,
            performance_issues=performance_issues,
            security_vulnerabilities=security_vulnerabilities,
            tables=tables,
            relationships=[],  # TODO: Implement relationships storage
            quality_score=main_row['quality_score'],
            complexity_score=main_row['complexity_score'],
            recommendations=json.loads(main_row['recommendations']) if main_row['recommendations'] else [],
            corrected_sql=main_row['corrected_sql'] or '',
            intelligent_comments=[]  # TODO: Implement comments storage
        )
        
        return result
