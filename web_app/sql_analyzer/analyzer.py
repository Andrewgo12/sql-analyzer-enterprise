"""
SQL Analyzer - Main Analysis Engine
Comprehensive SQL file analysis and processing
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class SQLAnalyzer:
    """Main SQL analysis engine for comprehensive SQL file processing."""
    
    def __init__(self):
        """Initialize the SQL analyzer."""
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.sql', '.txt', '.text']
        self.analysis_results = {}
        
    def analyze_file(self, file_path: str, analysis_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze a SQL file comprehensively.
        
        Args:
            file_path: Path to the SQL file
            analysis_options: Analysis configuration options
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Perform analysis
            results = {
                'file_info': self._analyze_file_info(file_path, content),
                'syntax_analysis': self._analyze_syntax(content),
                'schema_analysis': self._analyze_schema(content),
                'security_analysis': self._analyze_security(content),
                'performance_analysis': self._analyze_performance(content),
                'error_analysis': self._analyze_errors(content),
                'statistics': self._generate_statistics(content),
                'recommendations': self._generate_recommendations(content),
                'timestamp': datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_file_info(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze basic file information."""
        return {
            'name': os.path.basename(file_path),
            'size': len(content.encode('utf-8')),
            'lines': len(content.splitlines()),
            'encoding': 'utf-8',
            'type': 'sql'
        }
    
    def _analyze_syntax(self, content: str) -> Dict[str, Any]:
        """Analyze SQL syntax."""
        lines = content.splitlines()
        syntax_errors = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('--'):
                # Basic syntax checks
                if line.endswith(',') and i == len(lines):
                    syntax_errors.append({
                        'line': i,
                        'message': 'Trailing comma at end of file',
                        'severity': 'warning'
                    })
        
        return {
            'valid': len(syntax_errors) == 0,
            'errors': syntax_errors,
            'total_errors': len(syntax_errors)
        }
    
    def _analyze_schema(self, content: str) -> Dict[str, Any]:
        """Analyze database schema."""
        tables = re.findall(r'CREATE\s+TABLE\s+(\w+)', content, re.IGNORECASE)
        indexes = re.findall(r'CREATE\s+INDEX\s+(\w+)', content, re.IGNORECASE)
        
        return {
            'tables': tables,
            'table_count': len(tables),
            'indexes': indexes,
            'index_count': len(indexes)
        }
    
    def _analyze_security(self, content: str) -> Dict[str, Any]:
        """Analyze security issues."""
        security_issues = []
        
        # Check for potential SQL injection patterns
        if re.search(r"'\s*\+\s*", content):
            security_issues.append({
                'type': 'sql_injection',
                'message': 'Potential SQL injection vulnerability detected',
                'severity': 'high'
            })
        
        return {
            'issues': security_issues,
            'total_issues': len(security_issues),
            'security_score': max(0, 100 - len(security_issues) * 20)
        }
    
    def _analyze_performance(self, content: str) -> Dict[str, Any]:
        """Analyze performance issues."""
        performance_issues = []
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', content, re.IGNORECASE):
            performance_issues.append({
                'type': 'select_star',
                'message': 'SELECT * can impact performance',
                'severity': 'medium'
            })
        
        return {
            'issues': performance_issues,
            'total_issues': len(performance_issues),
            'performance_score': max(0, 100 - len(performance_issues) * 15)
        }
    
    def _analyze_errors(self, content: str) -> Dict[str, Any]:
        """Analyze common SQL errors."""
        errors = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                # Check for common errors
                if line.count('(') != line.count(')'):
                    errors.append({
                        'line': i,
                        'message': 'Unmatched parentheses',
                        'severity': 'error'
                    })
        
        return {
            'errors': errors,
            'total_errors': len(errors)
        }
    
    def _generate_statistics(self, content: str) -> Dict[str, Any]:
        """Generate content statistics."""
        lines = content.splitlines()
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'comment_lines': len([l for l in lines if l.strip().startswith('--')]),
            'sql_statements': len(re.findall(r';', content)),
            'character_count': len(content)
        }
    
    def _generate_recommendations(self, content: str) -> List[Dict[str, Any]]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if 'SELECT *' in content.upper():
            recommendations.append({
                'type': 'performance',
                'title': 'Avoid SELECT *',
                'description': 'Specify column names explicitly for better performance',
                'priority': 'medium'
            })
        
        return recommendations
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.supported_formats.copy()
    
    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if file can be analyzed.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.supported_formats:
            return False, f"Unsupported format: {ext}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Test read
            return True, ""
        except Exception as e:
            return False, f"Cannot read file: {e}"
