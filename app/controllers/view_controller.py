#!/usr/bin/env python3
"""
VIEW CONTROLLER
Controller for handling view rendering and data preparation
"""

import logging
from typing import Dict, Any, Optional
from flask import render_template, request, session
from datetime import datetime

from app.models.analysis_models import AnalysisResult, DatabaseType
from app.controllers.analysis_controller import AnalysisController
from app.config.settings import Constants, APP_METADATA

class ViewController:
    """Controller for view rendering and data preparation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_controller = AnalysisController()
        self.app_metadata = APP_METADATA
        self.constants = Constants()
    
    def render_sql_analysis_view(self) -> str:
        """Render SQL Analysis & Correction view"""
        try:
            context = {
                'page_title': 'SQL Analysis & Correction',
                'active_view': 'sql-analysis',
                'database_types': self.constants.DATABASE_TYPES,
                'export_formats': self.constants.EXPORT_FORMAT_DESCRIPTIONS,
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'features': {
                    'syntax_checking': True,
                    'auto_correction': True,
                    'intelligent_comments': True,
                    'multi_database': True
                }
            }
            
            return render_template('sql_analysis_correction.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render SQL analysis view: {str(e)}")
            return self._render_error_view(str(e))
    
    def render_security_analysis_view(self) -> str:
        """Render Security & Vulnerability Scanning view"""
        try:
            context = {
                'page_title': 'Security & Vulnerability Scanning',
                'active_view': 'security-analysis',
                'severity_levels': self.constants.SEVERITY_LEVELS,
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'security_features': {
                    'owasp_compliance': True,
                    'cwe_classification': True,
                    'sql_injection_detection': True,
                    'credential_scanning': True,
                    'risk_assessment': True
                },
                'owasp_categories': [
                    'A01:2021 – Broken Access Control',
                    'A02:2021 – Cryptographic Failures',
                    'A03:2021 – Injection',
                    'A04:2021 – Insecure Design',
                    'A05:2021 – Security Misconfiguration',
                    'A06:2021 – Vulnerable and Outdated Components',
                    'A07:2021 – Identification and Authentication Failures',
                    'A08:2021 – Software and Data Integrity Failures',
                    'A09:2021 – Security Logging and Monitoring Failures',
                    'A10:2021 – Server-Side Request Forgery'
                ]
            }
            
            return render_template('security_analysis.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render security analysis view: {str(e)}")
            return self._render_error_view(str(e))
    
    def render_performance_optimization_view(self) -> str:
        """Render Performance Optimization view"""
        try:
            context = {
                'page_title': 'Performance Optimization',
                'active_view': 'performance-optimization',
                'performance_thresholds': self.constants.PERFORMANCE_THRESHOLDS,
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'optimization_features': {
                    'query_optimization': True,
                    'index_suggestions': True,
                    'execution_plan_analysis': True,
                    'resource_estimation': True,
                    'bottleneck_detection': True
                },
                'performance_metrics': [
                    'Query Execution Time',
                    'Memory Usage',
                    'CPU Utilization',
                    'I/O Operations',
                    'Index Efficiency',
                    'Join Performance',
                    'Subquery Optimization'
                ]
            }
            
            return render_template('performance_optimization.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render performance optimization view: {str(e)}")
            return self._render_error_view(str(e))
    
    def render_schema_analysis_view(self) -> str:
        """Render Schema & Relationship Analysis view"""
        try:
            context = {
                'page_title': 'Schema & Relationship Analysis',
                'active_view': 'schema-analysis',
                'database_types': self.constants.DATABASE_TYPES,
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'schema_features': {
                    'table_detection': True,
                    'relationship_mapping': True,
                    'constraint_analysis': True,
                    'data_type_validation': True,
                    'normalization_check': True
                },
                'analysis_types': [
                    'Table Structure',
                    'Primary Keys',
                    'Foreign Keys',
                    'Indexes',
                    'Constraints',
                    'Data Types',
                    'Relationships',
                    'Normalization'
                ]
            }
            
            return render_template('schema_analysis.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render schema analysis view: {str(e)}")
            return self._render_error_view(str(e))
    
    def render_export_center_view(self) -> str:
        """Render Export & Format Conversion view"""
        try:
            context = {
                'page_title': 'Export & Format Conversion',
                'active_view': 'export-center',
                'export_formats': self.constants.EXPORT_FORMAT_DESCRIPTIONS,
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'export_features': {
                    'multi_format_support': True,
                    'batch_export': True,
                    'custom_templates': True,
                    'compression': True,
                    'email_delivery': True
                },
                'format_categories': {
                    'documents': ['html', 'pdf', 'markdown', 'txt', 'documentation'],
                    'data': ['json', 'xml', 'csv', 'yaml'],
                    'database': ['sql', 'mysql_dump', 'postgresql_backup', 'oracle_script'],
                    'office': ['excel', 'word', 'powerpoint']
                }
            }
            
            return render_template('export_center.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render export center view: {str(e)}")
            return self._render_error_view(str(e))
    
    def render_version_management_view(self) -> str:
        """Render Version Management view"""
        try:
            context = {
                'page_title': 'Version Management',
                'active_view': 'version-management',
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'version_features': {
                    'change_tracking': True,
                    'diff_analysis': True,
                    'rollback_support': True,
                    'branch_management': True,
                    'merge_conflict_detection': True
                },
                'version_operations': [
                    'Create Version',
                    'Compare Versions',
                    'Merge Changes',
                    'Rollback Changes',
                    'Branch Management',
                    'Tag Management'
                ]
            }
            
            return render_template('version_management.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render version management view: {str(e)}")
            return self._render_error_view(str(e))
    
    def render_comment_documentation_view(self) -> str:
        """Render Comment & Documentation view"""
        try:
            context = {
                'page_title': 'Comment & Documentation',
                'active_view': 'comment-documentation',
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat(),
                'documentation_features': {
                    'intelligent_comments': True,
                    'spanish_language': True,
                    'context_aware': True,
                    'auto_documentation': True,
                    'best_practices': True
                },
                'comment_types': [
                    'Explanation',
                    'Warning',
                    'Optimization',
                    'Security',
                    'Performance',
                    'Best Practice'
                ],
                'documentation_formats': [
                    'Inline Comments',
                    'Function Documentation',
                    'Schema Documentation',
                    'API Documentation',
                    'User Manual',
                    'Technical Specification'
                ]
            }
            
            return render_template('comment_documentation.html', **context)
            
        except Exception as e:
            self.logger.error(f"Failed to render comment documentation view: {str(e)}")
            return self._render_error_view(str(e))
    
    def prepare_analysis_data(self, analysis_id: str) -> Dict[str, Any]:
        """Prepare analysis data for view rendering"""
        try:
            # Get analysis details
            analysis_result = self.analysis_controller.get_analysis_details(analysis_id)
            
            if not analysis_result['success']:
                return {
                    'success': False,
                    'error': analysis_result['error']
                }
            
            details = analysis_result['details']
            
            # Prepare view-specific data
            view_data = {
                'analysis_summary': {
                    'id': details['id'],
                    'filename': details['filename'],
                    'database_type': details['database_type'],
                    'quality_score': details['quality_score'],
                    'complexity_score': details['complexity_score'],
                    'processing_time': details['processing_time']
                },
                'error_summary': self._prepare_error_summary(details),
                'security_summary': self._prepare_security_summary(details),
                'performance_summary': self._prepare_performance_summary(details),
                'schema_summary': self._prepare_schema_summary(details),
                'recommendations': details['recommendations'],
                'intelligent_comments': details['intelligent_comments']
            }
            
            return {
                'success': True,
                'data': view_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to prepare analysis data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_error_summary(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare error summary for views"""
        syntax_errors = details.get('syntax_errors', [])
        semantic_errors = details.get('semantic_errors', [])
        
        return {
            'total_errors': len(syntax_errors) + len(semantic_errors),
            'syntax_errors': len(syntax_errors),
            'semantic_errors': len(semantic_errors),
            'severity_breakdown': self._count_by_severity(syntax_errors + semantic_errors),
            'auto_fixable': sum(1 for error in syntax_errors if error.get('auto_fixable', False))
        }
    
    def _prepare_security_summary(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare security summary for views"""
        vulnerabilities = details.get('security_vulnerabilities', [])
        
        return {
            'total_vulnerabilities': len(vulnerabilities),
            'risk_breakdown': self._count_by_risk_level(vulnerabilities),
            'owasp_categories': list(set(v.get('owasp_category', '') for v in vulnerabilities if v.get('owasp_category'))),
            'cwe_ids': list(set(v.get('cwe_id', '') for v in vulnerabilities if v.get('cwe_id')))
        }
    
    def _prepare_performance_summary(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare performance summary for views"""
        issues = details.get('performance_issues', [])
        
        return {
            'total_issues': len(issues),
            'impact_breakdown': self._count_by_impact(issues),
            'issue_types': list(set(issue.get('issue_type', '') for issue in issues)),
            'optimization_potential': self._calculate_optimization_potential(issues)
        }
    
    def _prepare_schema_summary(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare schema summary for views"""
        tables = details.get('tables', [])
        relationships = details.get('relationships', [])
        
        return {
            'total_tables': len(tables),
            'total_relationships': len(relationships),
            'table_names': [table.get('name', '') for table in tables],
            'relationship_types': list(set(rel.get('type', '') for rel in relationships))
        }
    
    def _count_by_severity(self, errors: list) -> Dict[str, int]:
        """Count errors by severity"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for error in errors:
            severity = error.get('severity', 'low')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_risk_level(self, vulnerabilities: list) -> Dict[str, int]:
        """Count vulnerabilities by risk level"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for vuln in vulnerabilities:
            risk_level = vuln.get('risk_level', 'low')
            counts[risk_level] = counts.get(risk_level, 0) + 1
        return counts
    
    def _count_by_impact(self, issues: list) -> Dict[str, int]:
        """Count performance issues by impact"""
        counts = {'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            impact = issue.get('impact', 'low')
            counts[impact] = counts.get(impact, 0) + 1
        return counts
    
    def _calculate_optimization_potential(self, issues: list) -> str:
        """Calculate optimization potential"""
        if not issues:
            return "Minimal"
        
        high_impact = sum(1 for issue in issues if issue.get('impact') == 'high')
        
        if high_impact >= 5:
            return "Very High"
        elif high_impact >= 3:
            return "High"
        elif len(issues) >= 5:
            return "Medium"
        else:
            return "Low"
    
    def _render_error_view(self, error_message: str) -> str:
        """Render error view"""
        try:
            context = {
                'page_title': 'Error',
                'error_message': error_message,
                'app_metadata': self.app_metadata,
                'current_time': datetime.now().isoformat()
            }
            
            return render_template('error.html', **context)
            
        except Exception as e:
            # Fallback to simple error message
            return f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Application Error</h1>
                    <p>An error occurred: {error_message}</p>
                    <p>Additional error: {str(e)}</p>
                </body>
            </html>
            """
