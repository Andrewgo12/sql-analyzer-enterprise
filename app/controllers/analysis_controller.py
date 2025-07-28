#!/usr/bin/env python3
"""
ANALYSIS CONTROLLER
Enterprise controller for SQL analysis operations with service layer integration
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from flask import request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename

# Import models
from app.models.analysis_models import (
    AnalysisResult, DatabaseType, SQLError, SecurityVulnerability,
    PerformanceIssue, TableInfo, IntelligentComment, FileInfo, ErrorSeverity
)

# Import services
from app.services.analysis_service import AnalysisService

# Import utilities
from app.utils.helpers import ValidationHelper, ResponseHelper, LoggingHelper

class AnalysisController:
    """Enterprise analysis controller with comprehensive business logic"""

    def __init__(self):
        self.logger = LoggingHelper.setup_logger('analysis_controller')
        self.analysis_service = AnalysisService()

        # Performance tracking
        self.request_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }

        self.logger.info("Analysis controller initialized")
    
    def analyze_sql_file(self, file_data: Any, filename: str = None,
                        options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze uploaded SQL file with comprehensive validation and processing

        Args:
            file_data: File object or file-like object
            filename: Name of the file
            options: Analysis options (database_type, auto_fix, etc.)

        Returns:
            Dict containing analysis results or error information
        """
        start_time = time.time()
        self.request_metrics['total_requests'] += 1

        try:
            # Validate request parameters
            validation_result = self._validate_request(file_data, filename, options)
            if not validation_result['valid']:
                self.request_metrics['failed_requests'] += 1
                return ResponseHelper.error_response(
                    validation_result['error'],
                    'VALIDATION_ERROR'
                )

            # Use service layer for analysis
            service_result = self.analysis_service.analyze_sql_file(
                file_data, filename, options
            )

            # Update metrics
            response_time = time.time() - start_time
            self._update_request_metrics(response_time, service_result['success'])

            # Log performance
            LoggingHelper.log_performance(
                self.logger,
                'sql_file_analysis',
                response_time,
                {
                    'filename': filename,
                    'success': service_result['success'],
                    'from_cache': service_result.get('data', {}).get('from_cache', False)
                }
            )

            return service_result

        except Exception as e:
            self.request_metrics['failed_requests'] += 1
            self.logger.error(f"Controller analysis error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Analysis controller error: {str(e)}",
                'CONTROLLER_ERROR'
            )
    
    def get_analysis_summary(self, analysis_id: str) -> Dict[str, Any]:
        """Get analysis summary by ID with comprehensive validation"""
        try:
            # Validate analysis ID
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.get_analysis_summary(analysis_id)

            # Log request
            self.logger.debug(f"Analysis summary requested: {analysis_id}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller summary error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get analysis summary: {str(e)}",
                'CONTROLLER_ERROR'
            )
    
    def export_analysis(self, analysis_id: str, format_type: str,
                       options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export analysis results in specified format with validation"""
        try:
            # Validate parameters
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.export_analysis(
                analysis_id, format_type, options
            )

            # Log export request
            self.logger.info(f"Export requested: {analysis_id} -> {format_type}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller export error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Export operation failed: {str(e)}",
                'CONTROLLER_ERROR'
            )

    def get_recent_analyses(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent analysis summaries with validation"""
        try:
            # Validate limit
            if limit <= 0 or limit > 100:
                limit = 10

            # Use service layer
            service_result = self.analysis_service.get_recent_analyses(limit)

            # Log request
            self.logger.debug(f"Recent analyses requested: limit={limit}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller recent analyses error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get recent analyses: {str(e)}",
                'CONTROLLER_ERROR'
            )

    def delete_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Delete analysis result with validation"""
        try:
            # Validate analysis ID
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.delete_analysis(analysis_id)

            # Log request
            self.logger.info(f"Analysis deletion requested: {analysis_id}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller delete analysis error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to delete analysis: {str(e)}",
                'CONTROLLER_ERROR'
            )

    def get_controller_metrics(self) -> Dict[str, Any]:
        """Get controller performance metrics"""
        try:
            # Get service metrics
            service_metrics = self.analysis_service.get_service_metrics()

            # Combine with controller metrics
            combined_metrics = {
                'controller_metrics': self.request_metrics.copy(),
                'service_metrics': service_metrics['metrics'],
                'cache_stats': service_metrics['cache_stats'],
                'database_stats': service_metrics['database_stats']
            }

            return ResponseHelper.success_response(combined_metrics)

        except Exception as e:
            self.logger.error(f"Controller metrics error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get controller metrics: {str(e)}",
                'CONTROLLER_ERROR'
            )

    def _validate_request(self, file_data: Any, filename: str,
                         options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request parameters comprehensively"""
        try:
            # Basic validation
            if not file_data:
                return {'valid': False, 'error': 'No file data provided'}

            if not filename:
                return {'valid': False, 'error': 'No filename provided'}

            # Sanitize filename
            sanitized_filename = ValidationHelper.sanitize_input(filename)
            if not sanitized_filename:
                return {'valid': False, 'error': 'Invalid filename format'}

            # Validate options if provided
            if options:
                if 'database_type' in options:
                    valid_types = [db_type.value for db_type in DatabaseType]
                    if options['database_type'] not in valid_types:
                        return {
                            'valid': False,
                            'error': f'Invalid database type: {options["database_type"]}'
                        }

                # Validate boolean options
                boolean_options = ['auto_fix', 'intelligent_comments', 'security_scan']
                for opt in boolean_options:
                    if opt in options and not isinstance(options[opt], bool):
                        return {
                            'valid': False,
                            'error': f'Option {opt} must be boolean'
                        }

            return {'valid': True}

        except Exception as e:
            self.logger.error(f"Request validation error: {str(e)}")
            return {'valid': False, 'error': f'Validation error: {str(e)}'}

    def _update_request_metrics(self, response_time: float, success: bool):
        """Update request performance metrics"""
        try:
            if success:
                self.request_metrics['successful_requests'] += 1
            else:
                self.request_metrics['failed_requests'] += 1

            # Update average response time
            total_requests = (self.request_metrics['successful_requests'] +
                            self.request_metrics['failed_requests'])

            if total_requests > 0:
                current_avg = self.request_metrics['average_response_time']
                self.request_metrics['average_response_time'] = (
                    (current_avg * (total_requests - 1) + response_time) / total_requests
                )

        except Exception as e:
            self.logger.error(f"Metrics update error: {str(e)}")

    def shutdown(self):
        """Gracefully shutdown the controller"""
        try:
            self.analysis_service.shutdown()
            self.logger.info("Analysis controller shutdown complete")
        except Exception as e:
            self.logger.error(f"Controller shutdown error: {str(e)}")
    
    def get_analysis_details(self, analysis_id: str) -> Dict[str, Any]:
        """Get detailed analysis results with comprehensive validation"""
        try:
            # Validate analysis ID
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.get_analysis_result(analysis_id)

            # Log request
            self.logger.debug(f"Analysis details requested: {analysis_id}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller details error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get analysis details: {str(e)}",
                'CONTROLLER_ERROR'
            )
    
    def get_security_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Get security analysis details with comprehensive assessment"""
        try:
            # Validate analysis ID
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.get_security_analysis(analysis_id)

            # Log request
            self.logger.debug(f"Security analysis requested: {analysis_id}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller security analysis error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get security analysis: {str(e)}",
                'CONTROLLER_ERROR'
            )
    
    def get_performance_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Get performance analysis details with comprehensive assessment"""
        try:
            # Validate analysis ID
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.get_performance_analysis(analysis_id)

            # Log request
            self.logger.debug(f"Performance analysis requested: {analysis_id}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller performance analysis error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get performance analysis: {str(e)}",
                'CONTROLLER_ERROR'
            )
    
    def get_schema_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Get schema analysis details with comprehensive assessment"""
        try:
            # Validate analysis ID
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return ResponseHelper.error_response(
                    'Invalid analysis ID format',
                    'INVALID_ID'
                )

            # Use service layer
            service_result = self.analysis_service.get_schema_analysis(analysis_id)

            # Log request
            self.logger.debug(f"Schema analysis requested: {analysis_id}")

            return service_result

        except Exception as e:
            self.logger.error(f"Controller schema analysis error: {str(e)}", exc_info=True)
            return ResponseHelper.error_response(
                f"Failed to get schema analysis: {str(e)}",
                'CONTROLLER_ERROR'
            )
    
    def _detect_database_type(self, filename: str, content: str) -> DatabaseType:
        """Detect database type from filename and content"""
        if filename:
            filename_lower = filename.lower()
            if 'mysql' in filename_lower:
                return DatabaseType.MYSQL
            elif 'postgres' in filename_lower or 'psql' in filename_lower:
                return DatabaseType.POSTGRESQL
            elif 'oracle' in filename_lower:
                return DatabaseType.ORACLE
            elif 'sqlserver' in filename_lower or 'mssql' in filename_lower:
                return DatabaseType.SQL_SERVER
            elif 'sqlite' in filename_lower:
                return DatabaseType.SQLITE
        
        # Use analyzer's detection
        return self.analyzer.detect_database_type(content)
    
    def _convert_analysis_result(self, analysis_result: Any, file_info: FileInfo) -> AnalysisResult:
        """Convert analyzer result to our model format"""
        # Convert syntax errors
        syntax_errors = []
        for error in analysis_result.syntax_errors:
            syntax_errors.append(SQLError(
                line_number=error.line_number,
                column=error.column,
                error_type=error.error_type,
                severity=ErrorSeverity(error.severity),
                message=error.message,
                suggestion=error.suggestion,
                auto_fixable=error.auto_fixable,
                fixed_code=error.fixed_code
            ))
        
        # Convert semantic errors
        semantic_errors = []
        for error in analysis_result.semantic_errors:
            semantic_errors.append(SQLError(
                line_number=error.line_number,
                column=error.column,
                error_type=error.error_type,
                severity=ErrorSeverity(error.severity),
                message=error.message,
                suggestion=error.suggestion,
                auto_fixable=error.auto_fixable
            ))
        
        # Convert performance issues
        performance_issues = []
        for issue in analysis_result.performance_issues:
            performance_issues.append(PerformanceIssue(
                line_number=issue.get('line_number', 0),
                issue_type=issue.get('type', ''),
                impact=issue.get('impact', ''),
                description=issue.get('description', ''),
                recommendation=issue.get('recommendation', ''),
                code_snippet=issue.get('code_snippet', ''),
                estimated_improvement=issue.get('estimated_improvement', '')
            ))
        
        # Convert security vulnerabilities
        security_vulnerabilities = []
        for vuln in analysis_result.security_vulnerabilities:
            security_vulnerabilities.append(SecurityVulnerability(
                line_number=vuln.get('line_number', 0),
                vulnerability_type=vuln.get('vulnerability_type', ''),
                risk_level=ErrorSeverity(vuln.get('risk_level', 'low')),
                description=vuln.get('description', ''),
                mitigation=vuln.get('mitigation', ''),
                code_snippet=vuln.get('code_snippet', ''),
                cwe_id=vuln.get('cwe_id', ''),
                owasp_category=vuln.get('owasp_category', '')
            ))
        
        # Convert tables
        tables = []
        for table in analysis_result.tables:
            tables.append(TableInfo(
                name=table.name,
                columns=table.columns,
                primary_keys=table.primary_keys,
                foreign_keys=table.foreign_keys,
                indexes=table.indexes,
                constraints=table.constraints,
                estimated_rows=table.estimated_rows
            ))
        
        # Convert intelligent comments
        intelligent_comments = []
        for comment in analysis_result.intelligent_comments:
            intelligent_comments.append(IntelligentComment(
                line_number=comment.get('line_number', 0),
                comment=comment.get('comment', ''),
                comment_type=comment.get('type', 'explanation')
            ))
        
        return AnalysisResult(
            file_hash=analysis_result.file_hash,
            filename=file_info.filename,
            processing_time=analysis_result.processing_time,
            database_type=analysis_result.database_type,
            total_lines=analysis_result.total_lines,
            total_statements=analysis_result.total_statements,
            syntax_errors=syntax_errors,
            semantic_errors=semantic_errors,
            performance_issues=performance_issues,
            security_vulnerabilities=security_vulnerabilities,
            tables=tables,
            relationships=analysis_result.relationships,
            quality_score=analysis_result.quality_score,
            complexity_score=analysis_result.complexity_score,
            recommendations=analysis_result.recommendations,
            corrected_sql=analysis_result.corrected_sql,
            intelligent_comments=intelligent_comments
        )
    
    def _assess_security_risk(self, vulnerabilities: List[SecurityVulnerability]) -> str:
        """Assess overall security risk"""
        if not vulnerabilities:
            return "Low"
        
        critical_count = sum(1 for v in vulnerabilities if v.risk_level == ErrorSeverity.CRITICAL)
        high_count = sum(1 for v in vulnerabilities if v.risk_level == ErrorSeverity.HIGH)
        
        if critical_count > 0:
            return "Critical"
        elif high_count > 0:
            return "High"
        elif len(vulnerabilities) > 5:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_performance_score(self, issues: List[PerformanceIssue]) -> int:
        """Calculate performance score"""
        if not issues:
            return 100
        
        base_score = 100
        for issue in issues:
            if issue.impact == 'high':
                base_score -= 15
            elif issue.impact == 'medium':
                base_score -= 10
            else:
                base_score -= 5
        
        return max(0, base_score)
    
    def _get_optimization_suggestions(self, issues: List[PerformanceIssue]) -> List[str]:
        """Get optimization suggestions"""
        suggestions = []
        issue_types = set(issue.issue_type for issue in issues)
        
        if 'select_star' in issue_types:
            suggestions.append("Specify only needed columns instead of using SELECT *")
        if 'missing_index' in issue_types:
            suggestions.append("Add indexes on frequently queried columns")
        if 'leading_wildcard' in issue_types:
            suggestions.append("Avoid LIKE patterns with leading wildcards")
        if 'order_without_limit' in issue_types:
            suggestions.append("Add LIMIT clauses to ORDER BY statements")
        
        return suggestions
    
    def _calculate_schema_complexity(self, tables: List[TableInfo], relationships: List[Dict[str, Any]]) -> str:
        """Calculate schema complexity"""
        total_tables = len(tables)
        total_relationships = len(relationships)
        
        if total_tables == 0:
            return "None"
        elif total_tables <= 5 and total_relationships <= 5:
            return "Low"
        elif total_tables <= 15 and total_relationships <= 20:
            return "Medium"
        else:
            return "High"
