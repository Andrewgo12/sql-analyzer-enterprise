#!/usr/bin/env python3
"""
ANALYSIS SERVICE LAYER
Enterprise business logic for SQL analysis operations
"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from app.models.analysis_models import (
    AnalysisResult, DatabaseType, FileInfo, SQLError, 
    SecurityVulnerability, PerformanceIssue, ErrorSeverity
)
from app.models.data_access import DatabaseManager, AnalysisRepository
from app.utils.helpers import cache, FileHelper, ValidationHelper, LoggingHelper

# Import analysis engines
from comprehensive_sql_analyzer import ComprehensiveSQLAnalyzer
from enterprise_file_processor import EnterpriseFileProcessor
from export_engine import ExportEngine

class AnalysisService:
    """Enterprise analysis service with caching, validation, and business logic"""
    
    def __init__(self):
        self.logger = LoggingHelper.setup_logger('analysis_service')
        self.db_manager = DatabaseManager()
        self.repository = AnalysisRepository(self.db_manager)
        
        # Initialize analysis engines
        self.sql_analyzer = ComprehensiveSQLAnalyzer()
        self.file_processor = EnterpriseFileProcessor()
        self.export_engine = ExportEngine()
        
        # Performance tracking
        self.analysis_metrics = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'average_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='analysis')
        
        self.logger.info("Analysis service initialized")
    
    def analyze_sql_file(self, file_data: Any, filename: str, 
                        options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive SQL file analysis with caching and validation
        
        Args:
            file_data: File object or file-like object
            filename: Name of the file
            options: Analysis options (database_type, auto_fix, etc.)
        
        Returns:
            Dict containing analysis results or error information
        """
        start_time = time.time()
        self.analysis_metrics['total_analyses'] += 1
        
        try:
            # Validate inputs
            validation_result = self._validate_analysis_request(file_data, filename, options)
            if not validation_result['valid']:
                self.analysis_metrics['failed_analyses'] += 1
                return self._create_error_response(validation_result['error'], 'VALIDATION_ERROR')
            
            # Process file
            file_result = self._process_file_safely(file_data, filename)
            if not file_result['success']:
                self.analysis_metrics['failed_analyses'] += 1
                return self._create_error_response(file_result['error'], 'FILE_PROCESSING_ERROR')
            
            file_info = file_result['file_info']
            file_content = file_result['content']
            
            # Check cache for existing analysis
            cached_result = self._check_analysis_cache(file_info.hash_sha256)
            if cached_result:
                self.analysis_metrics['cache_hits'] += 1
                processing_time = time.time() - start_time
                self._update_performance_metrics(processing_time)
                
                return self._create_success_response({
                    'analysis_result': cached_result.to_dict(),
                    'file_info': file_info.to_dict(),
                    'processing_time': processing_time,
                    'from_cache': True
                })
            
            self.analysis_metrics['cache_misses'] += 1
            
            # Perform comprehensive analysis
            analysis_result = self._perform_comprehensive_analysis(
                file_content, filename, file_info, options or {}
            )
            
            if not analysis_result:
                self.analysis_metrics['failed_analyses'] += 1
                return self._create_error_response('Analysis failed', 'ANALYSIS_ERROR')
            
            # Save to database
            save_success = self.repository.save_analysis_result(analysis_result)
            if not save_success:
                self.logger.warning(f"Failed to save analysis result: {analysis_result.id}")
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time)
            self.analysis_metrics['successful_analyses'] += 1
            
            return self._create_success_response({
                'analysis_result': analysis_result.to_dict(),
                'file_info': file_info.to_dict(),
                'processing_time': processing_time,
                'from_cache': False
            })
            
        except Exception as e:
            self.analysis_metrics['failed_analyses'] += 1
            self.logger.error(f"Analysis service error: {str(e)}", exc_info=True)
            return self._create_error_response(f"Internal analysis error: {str(e)}", 'INTERNAL_ERROR')
    
    def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """Get analysis result by ID with validation"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return self._create_error_response('Invalid analysis ID format', 'INVALID_ID')
            
            result = self.repository.get_analysis_by_id(analysis_id)
            if not result:
                return self._create_error_response('Analysis not found', 'NOT_FOUND')
            
            return self._create_success_response({
                'analysis_result': result.to_dict()
            })
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis result: {str(e)}")
            return self._create_error_response('Failed to retrieve analysis', 'RETRIEVAL_ERROR')
    
    def get_analysis_summary(self, analysis_id: str) -> Dict[str, Any]:
        """Get condensed analysis summary"""
        try:
            result = self.repository.get_analysis_by_id(analysis_id)
            if not result:
                return self._create_error_response('Analysis not found', 'NOT_FOUND')
            
            summary = self._create_analysis_summary(result)
            return self._create_success_response(summary)
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis summary: {str(e)}")
            return self._create_error_response('Failed to retrieve summary', 'RETRIEVAL_ERROR')
    
    def get_security_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Get detailed security analysis"""
        try:
            result = self.repository.get_analysis_by_id(analysis_id)
            if not result:
                return self._create_error_response('Analysis not found', 'NOT_FOUND')
            
            security_analysis = self._create_security_analysis(result)
            return self._create_success_response(security_analysis)
            
        except Exception as e:
            self.logger.error(f"Failed to get security analysis: {str(e)}")
            return self._create_error_response('Failed to retrieve security analysis', 'RETRIEVAL_ERROR')
    
    def get_performance_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Get detailed performance analysis"""
        try:
            result = self.repository.get_analysis_by_id(analysis_id)
            if not result:
                return self._create_error_response('Analysis not found', 'NOT_FOUND')
            
            performance_analysis = self._create_performance_analysis(result)
            return self._create_success_response(performance_analysis)
            
        except Exception as e:
            self.logger.error(f"Failed to get performance analysis: {str(e)}")
            return self._create_error_response('Failed to retrieve performance analysis', 'RETRIEVAL_ERROR')
    
    def get_schema_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Get detailed schema analysis"""
        try:
            result = self.repository.get_analysis_by_id(analysis_id)
            if not result:
                return self._create_error_response('Analysis not found', 'NOT_FOUND')
            
            schema_analysis = self._create_schema_analysis(result)
            return self._create_success_response(schema_analysis)
            
        except Exception as e:
            self.logger.error(f"Failed to get schema analysis: {str(e)}")
            return self._create_error_response('Failed to retrieve schema analysis', 'RETRIEVAL_ERROR')
    
    def export_analysis(self, analysis_id: str, format_type: str,
                       options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export analysis results in specified format"""
        try:
            result = self.repository.get_analysis_by_id(analysis_id)
            if not result:
                return self._create_error_response('Analysis not found', 'NOT_FOUND')

            # Validate export format
            supported_formats = ['json', 'html', 'xml', 'csv', 'markdown', 'txt', 'sql',
                               'mysql_dump', 'postgresql_backup', 'oracle_script', 'documentation']

            if format_type not in supported_formats:
                return self._create_error_response(f'Unsupported export format: {format_type}', 'INVALID_FORMAT')

            # Perform export
            export_result = self.export_engine.export(result, format_type, options or {})

            if not export_result.get('success', True):
                return self._create_error_response(export_result.get('error', 'Export failed'), 'EXPORT_ERROR')

            # Ensure proper response format
            if isinstance(export_result, str):
                # If export_result is just the content string
                export_response = {
                    'success': True,
                    'content': export_result,
                    'filename': f'analysis_{analysis_id}.{format_type}',
                    'format': format_type,
                    'size': len(export_result),
                    'mime_type': self._get_mime_type(format_type)
                }
            else:
                # If export_result is already a dict
                export_response = export_result
                export_response['success'] = True

            return self._create_success_response(export_response)

        except Exception as e:
            self.logger.error(f"Failed to export analysis: {str(e)}")
            return self._create_error_response('Export operation failed', 'EXPORT_ERROR')
    
    def get_recent_analyses(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent analysis summaries"""
        try:
            if limit <= 0 or limit > 100:
                limit = 10
            
            analyses = self.repository.get_recent_analyses(limit)
            return self._create_success_response({
                'analyses': analyses,
                'total': len(analyses)
            })
            
        except Exception as e:
            self.logger.error(f"Failed to get recent analyses: {str(e)}")
            return self._create_error_response('Failed to retrieve recent analyses', 'RETRIEVAL_ERROR')
    
    def delete_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Delete analysis result"""
        try:
            if not ValidationHelper.validate_analysis_id(analysis_id):
                return self._create_error_response('Invalid analysis ID format', 'INVALID_ID')
            
            success = self.repository.delete_analysis(analysis_id)
            if not success:
                return self._create_error_response('Failed to delete analysis', 'DELETE_ERROR')
            
            return self._create_success_response({'deleted': True})
            
        except Exception as e:
            self.logger.error(f"Failed to delete analysis: {str(e)}")
            return self._create_error_response('Delete operation failed', 'DELETE_ERROR')
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return {
            'metrics': self.analysis_metrics.copy(),
            'cache_stats': {
                'size': len(cache._cache),
                'hit_rate': (self.analysis_metrics['cache_hits'] / 
                           max(1, self.analysis_metrics['cache_hits'] + self.analysis_metrics['cache_misses'])) * 100
            },
            'database_stats': {
                'connection_count': len(self.db_manager._connections)
            }
        }
    
    def _validate_analysis_request(self, file_data: Any, filename: str, 
                                 options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis request parameters"""
        if not file_data:
            return {'valid': False, 'error': 'No file data provided'}
        
        if not filename:
            return {'valid': False, 'error': 'No filename provided'}
        
        # Validate filename
        if not ValidationHelper.sanitize_input(filename):
            return {'valid': False, 'error': 'Invalid filename'}
        
        # Validate options
        if options:
            if 'database_type' in options:
                valid_types = [db_type.value for db_type in DatabaseType]
                if options['database_type'] not in valid_types:
                    return {'valid': False, 'error': f'Invalid database type: {options["database_type"]}'}
        
        return {'valid': True}
    
    def _process_file_safely(self, file_data: Any, filename: str) -> Dict[str, Any]:
        """Process file with comprehensive error handling"""
        try:
            result = self.file_processor.process_file(file_data, filename)
            
            if not result['success']:
                return result
            
            # Convert to our FileInfo model
            file_info_data = result['file_info']
            file_info = FileInfo(
                filename=file_info_data.filename,
                size=file_info_data.size,
                encoding=file_info_data.encoding,
                line_count=file_info_data.line_count,
                hash_md5=file_info_data.hash_md5,
                hash_sha256=file_info_data.hash_sha256,
                processing_time=file_info_data.processing_time,
                is_valid=file_info_data.is_valid,
                error_message=file_info_data.error_message
            )
            
            return {
                'success': True,
                'file_info': file_info,
                'content': result['content']
            }
            
        except Exception as e:
            self.logger.error(f"File processing error: {str(e)}")
            return {
                'success': False,
                'error': f'File processing failed: {str(e)}'
            }
    
    def _check_analysis_cache(self, file_hash: str) -> Optional[AnalysisResult]:
        """Check if analysis exists in cache or database"""
        # Check memory cache first
        cached_result = cache.get(f"analysis_hash:{file_hash}")
        if cached_result:
            return cached_result
        
        # Check database
        return self.repository.get_analysis_by_hash(file_hash)
    
    def _perform_comprehensive_analysis(self, content: str, filename: str, 
                                      file_info: FileInfo, options: Dict[str, Any]) -> Optional[AnalysisResult]:
        """Perform comprehensive SQL analysis"""
        try:
            # Determine database type
            db_type = self._determine_database_type(filename, content, options)
            
            # Perform analysis
            analysis_result = self.sql_analyzer.analyze_file(content, filename, db_type)
            
            # Convert to our model format
            converted_result = self._convert_analysis_result(analysis_result, file_info)
            
            return converted_result
            
        except Exception as e:
            self.logger.error(f"Analysis execution error: {str(e)}")
            return None
    
    def _determine_database_type(self, filename: str, content: str, options: Dict[str, Any]) -> DatabaseType:
        """Determine database type from various sources"""
        # Check options first
        if 'database_type' in options and options['database_type'] != 'generic':
            try:
                return DatabaseType(options['database_type'])
            except ValueError:
                pass
        
        # Use analyzer's detection
        return self.sql_analyzer.detect_database_type(content)
    
    def _convert_analysis_result(self, analysis_result: Any, file_info: FileInfo) -> AnalysisResult:
        """Convert analyzer result to our model format"""
        # This is the same conversion logic from the controller
        # but moved to the service layer for better separation of concerns
        
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
        
        # Convert tables (simplified for now)
        tables = []
        for table in analysis_result.tables:
            from app.models.analysis_models import TableInfo
            tables.append(TableInfo(
                name=table.name,
                columns=table.columns,
                primary_keys=table.primary_keys,
                foreign_keys=table.foreign_keys,
                indexes=table.indexes,
                constraints=table.constraints,
                estimated_rows=table.estimated_rows
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
            intelligent_comments=[]  # Convert if needed
        )
    
    def _create_analysis_summary(self, result: AnalysisResult) -> Dict[str, Any]:
        """Create condensed analysis summary"""
        return {
            'id': result.id,
            'filename': result.filename,
            'database_type': result.database_type.value,
            'quality_score': result.quality_score,
            'complexity_score': result.complexity_score,
            'total_errors': len(result.syntax_errors) + len(result.semantic_errors),
            'security_issues': len(result.security_vulnerabilities),
            'performance_issues': len(result.performance_issues),
            'tables_found': len(result.tables),
            'processing_time': result.processing_time,
            'quality_level': result.get_quality_level(),
            'complexity_level': result.get_complexity_level(),
            'error_summary': result.get_error_summary(),
            'security_summary': result.get_security_summary()
        }
    
    def _create_security_analysis(self, result: AnalysisResult) -> Dict[str, Any]:
        """Create detailed security analysis"""
        return {
            'vulnerabilities': [vuln.to_dict() for vuln in result.security_vulnerabilities],
            'summary': result.get_security_summary(),
            'total_vulnerabilities': len(result.security_vulnerabilities),
            'risk_assessment': self._assess_security_risk(result.security_vulnerabilities),
            'owasp_categories': list(set(v.owasp_category for v in result.security_vulnerabilities if v.owasp_category)),
            'cwe_ids': list(set(v.cwe_id for v in result.security_vulnerabilities if v.cwe_id)),
            'recommendations': [rec for rec in result.recommendations if 'security' in rec.lower() or 'seguridad' in rec.lower()]
        }
    
    def _create_performance_analysis(self, result: AnalysisResult) -> Dict[str, Any]:
        """Create detailed performance analysis"""
        return {
            'issues': [issue.to_dict() for issue in result.performance_issues],
            'total_issues': len(result.performance_issues),
            'performance_score': self._calculate_performance_score(result.performance_issues),
            'optimization_suggestions': self._get_optimization_suggestions(result.performance_issues),
            'impact_breakdown': self._count_by_impact(result.performance_issues),
            'recommendations': [rec for rec in result.recommendations if 'performance' in rec.lower() or 'rendimiento' in rec.lower()]
        }
    
    def _create_schema_analysis(self, result: AnalysisResult) -> Dict[str, Any]:
        """Create detailed schema analysis"""
        return {
            'tables': [table.to_dict() for table in result.tables],
            'relationships': result.relationships,
            'total_tables': len(result.tables),
            'total_relationships': len(result.relationships),
            'schema_complexity': self._calculate_schema_complexity(result.tables, result.relationships),
            'table_summary': self._create_table_summary(result.tables),
            'relationship_summary': self._create_relationship_summary(result.relationships)
        }
    
    def _assess_security_risk(self, vulnerabilities: List[SecurityVulnerability]) -> str:
        """Assess overall security risk level"""
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
        """Calculate performance score based on issues"""
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
        """Get optimization suggestions based on issues"""
        suggestions = []
        issue_types = set(issue.issue_type for issue in issues)
        
        if 'select_star' in issue_types:
            suggestions.append("Especificar solo las columnas necesarias en lugar de usar SELECT *")
        if 'missing_index' in issue_types:
            suggestions.append("Agregar índices en columnas frecuentemente consultadas")
        if 'leading_wildcard' in issue_types:
            suggestions.append("Evitar patrones LIKE con comodines al inicio")
        if 'order_without_limit' in issue_types:
            suggestions.append("Agregar cláusulas LIMIT a las declaraciones ORDER BY")
        
        return suggestions
    
    def _count_by_impact(self, issues: List[PerformanceIssue]) -> Dict[str, int]:
        """Count performance issues by impact level"""
        counts = {'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            impact = issue.impact.lower()
            if impact in counts:
                counts[impact] += 1
        return counts
    
    def _calculate_schema_complexity(self, tables: List, relationships: List) -> str:
        """Calculate schema complexity level"""
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
    
    def _create_table_summary(self, tables: List) -> Dict[str, Any]:
        """Create table summary statistics"""
        if not tables:
            return {'total_columns': 0, 'total_constraints': 0, 'avg_columns_per_table': 0}
        
        total_columns = sum(len(table.columns) for table in tables)
        total_constraints = sum(len(table.constraints) for table in tables)
        
        return {
            'total_columns': total_columns,
            'total_constraints': total_constraints,
            'avg_columns_per_table': total_columns / len(tables) if tables else 0,
            'tables_with_primary_keys': sum(1 for table in tables if table.primary_keys),
            'tables_with_foreign_keys': sum(1 for table in tables if table.foreign_keys)
        }
    
    def _create_relationship_summary(self, relationships: List) -> Dict[str, Any]:
        """Create relationship summary statistics"""
        if not relationships:
            return {'foreign_keys': 0, 'other_relationships': 0}
        
        foreign_key_count = sum(1 for rel in relationships if rel.get('type') == 'foreign_key')
        
        return {
            'foreign_keys': foreign_key_count,
            'other_relationships': len(relationships) - foreign_key_count,
            'relationship_types': list(set(rel.get('type', 'unknown') for rel in relationships))
        }
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance metrics"""
        total_analyses = self.analysis_metrics['successful_analyses'] + self.analysis_metrics['failed_analyses']
        if total_analyses > 0:
            current_avg = self.analysis_metrics['average_processing_time']
            self.analysis_metrics['average_processing_time'] = (
                (current_avg * (total_analyses - 1) + processing_time) / total_analyses
            )
    
    def _create_success_response(self, data: Any) -> Dict[str, Any]:
        """Create standardized success response"""
        return {
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_error_response(self, error: str, error_code: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'success': False,
            'error': error,
            'error_code': error_code,
            'timestamp': datetime.now().isoformat()
        }

    def _get_mime_type(self, format_type: str) -> str:
        """Get MIME type for export format"""
        mime_types = {
            'json': 'application/json',
            'html': 'text/html',
            'xml': 'application/xml',
            'csv': 'text/csv',
            'markdown': 'text/markdown',
            'txt': 'text/plain',
            'sql': 'application/sql',
            'mysql_dump': 'application/sql',
            'postgresql_backup': 'application/sql',
            'oracle_script': 'application/sql',
            'documentation': 'text/html'
        }
        return mime_types.get(format_type, 'text/plain')
    
    def shutdown(self):
        """Gracefully shutdown the service"""
        self.executor.shutdown(wait=True)
        self.db_manager.close_all_connections()
        cache.clear_all()
        self.logger.info("Analysis service shutdown complete")
