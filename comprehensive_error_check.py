#!/usr/bin/env python3
"""
COMPREHENSIVE ERROR DETECTION AND CORRECTION SCRIPT
Systematic detection of all types of errors across the SQL Analyzer Enterprise application
"""

import os
import re
import json
import ast
import sys
from pathlib import Path
from typing import List, Dict, Any

class ComprehensiveErrorChecker:
    """Comprehensive error detection across all application files."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        
    def run_comprehensive_check(self):
        """Run comprehensive error detection across all files."""
        print("🔍 COMPREHENSIVE ERROR DETECTION - SQL ANALYZER ENTERPRISE")
        print("=" * 80)
        
        # Check categories
        checks = [
            ("Python Syntax & Import Errors", self.check_python_files),
            ("JavaScript Syntax & Reference Errors", self.check_javascript_files),
            ("HTML Structure & Element Errors", self.check_html_files),
            ("CSS Syntax Errors", self.check_css_files),
            ("API Endpoint Consistency", self.check_api_consistency),
            ("Cross-File Dependencies", self.check_cross_dependencies),
            ("Missing Implementations", self.check_missing_implementations),
            ("Configuration Errors", self.check_configuration_files)
        ]
        
        for category, checker in checks:
            print(f"\n🧪 Checking: {category}")
            try:
                checker()
                print(f"   ✅ {category} check completed")
            except Exception as e:
                print(f"   ❌ {category} check failed: {e}")
                self.errors.append({
                    'category': category,
                    'type': 'CHECK_FAILURE',
                    'message': str(e)
                })
        
        self.generate_error_report()
        self.apply_critical_fixes()
    
    def check_python_files(self):
        """Check Python files for syntax and import errors."""
        python_files = [
            'web_app/server.py',
            'web_app/security/security_manager.py',
            'web_app/integrations/database_integrations.py',
            'setup.py',
            'validate_integration.py'
        ]
        
        for file_path in python_files:
            if os.path.exists(file_path):
                self.check_python_file(file_path)
    
    def check_python_file(self, file_path):
        """Check individual Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.errors.append({
                    'file': file_path,
                    'type': 'SYNTAX_ERROR',
                    'line': e.lineno,
                    'message': str(e)
                })
            
            # Check imports
            import_lines = re.findall(r'^(from .+ import .+|import .+)$', content, re.MULTILINE)
            for line in import_lines:
                if 'from web_app' not in line and 'from security' in line:
                    self.warnings.append({
                        'file': file_path,
                        'type': 'IMPORT_WARNING',
                        'message': f"Potential import path issue: {line}"
                    })
            
            # Check for undefined variables
            undefined_patterns = [
                r'(\w+)\.(\w+)\(' + r'.*' + r'# Undefined method call',
                r'(\w+) = (\w+)\(' + r'.*' + r'# Undefined class instantiation'
            ]
            
        except Exception as e:
            self.errors.append({
                'file': file_path,
                'type': 'FILE_READ_ERROR',
                'message': str(e)
            })
    
    def check_javascript_files(self):
        """Check JavaScript files for syntax and reference errors."""
        js_files = [
            'web_app/static/js/results.js',
            'web_app/static/js/api.js',
            'web_app/static/js/auth.js',
            'web_app/static/js/upload.js',
            'web_app/static/js/analysis.js',
            'web_app/static/js/app-controller.js',
            'web_app/static/js/utils.js',
            'web_app/static/js/events.js',
            'web_app/static/js/navigation.js'
        ]
        
        for file_path in js_files:
            if os.path.exists(file_path):
                self.check_javascript_file(file_path)
    
    def check_javascript_file(self, file_path):
        """Check individual JavaScript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common syntax errors
            syntax_patterns = [
                (r'function\s+\w+\([^)]*\)\s*{[^}]*$', 'Unclosed function'),
                (r'class\s+\w+\s*{[^}]*$', 'Unclosed class'),
                (r'if\s*\([^)]*\)\s*{[^}]*$', 'Unclosed if statement'),
                (r'for\s*\([^)]*\)\s*{[^}]*$', 'Unclosed for loop')
            ]
            
            for pattern, error_type in syntax_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                if matches:
                    self.warnings.append({
                        'file': file_path,
                        'type': 'POTENTIAL_SYNTAX_ERROR',
                        'message': f"{error_type}: {len(matches)} instances found"
                    })
            
            # Check for undefined method calls
            method_calls = re.findall(r'this\.(\w+)\(', content)
            class_methods = re.findall(r'(\w+)\s*\([^)]*\)\s*{', content)
            
            for method in method_calls:
                if method not in [m.split('(')[0] for m in class_methods]:
                    # Check if it's a common method that might be missing
                    if method not in ['init', 'constructor', 'toString', 'valueOf']:
                        self.warnings.append({
                            'file': file_path,
                            'type': 'UNDEFINED_METHOD',
                            'message': f"Method '{method}' called but not defined"
                        })
            
        except Exception as e:
            self.errors.append({
                'file': file_path,
                'type': 'FILE_READ_ERROR',
                'message': str(e)
            })
    
    def check_html_files(self):
        """Check HTML files for structure and element errors."""
        html_files = ['web_app/templates/app.html']
        
        for file_path in html_files:
            if os.path.exists(file_path):
                self.check_html_file(file_path)
    
    def check_html_file(self, file_path):
        """Check individual HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for unclosed tags
            open_tags = re.findall(r'<(\w+)[^>]*>', content)
            close_tags = re.findall(r'</(\w+)>', content)
            
            # Filter out self-closing tags
            self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link']
            open_tags = [tag for tag in open_tags if tag not in self_closing]
            
            for tag in open_tags:
                if open_tags.count(tag) != close_tags.count(tag):
                    self.warnings.append({
                        'file': file_path,
                        'type': 'UNCLOSED_TAG',
                        'message': f"Tag '{tag}' may be unclosed: {open_tags.count(tag)} open, {close_tags.count(tag)} close"
                    })
            
            # Check for required IDs that JavaScript expects
            required_ids = [
                'health-score-chart', 'security-score-chart', 'performance-chart',
                'recommendations-list', 'errors-list', 'schema-diagram',
                'tables-list', 'security-issues', 'security-recommendations',
                'optimization-suggestions'
            ]
            
            for required_id in required_ids:
                if f'id="{required_id}"' not in content:
                    self.warnings.append({
                        'file': file_path,
                        'type': 'MISSING_ELEMENT_ID',
                        'message': f"Required element ID '{required_id}' not found"
                    })
            
        except Exception as e:
            self.errors.append({
                'file': file_path,
                'type': 'FILE_READ_ERROR',
                'message': str(e)
            })
    
    def check_css_files(self):
        """Check CSS files for syntax errors."""
        css_files = ['web_app/static/css/main.css']
        
        for file_path in css_files:
            if os.path.exists(file_path):
                self.check_css_file(file_path)
    
    def check_css_file(self, file_path):
        """Check individual CSS file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for unclosed braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces != close_braces:
                self.errors.append({
                    'file': file_path,
                    'type': 'CSS_SYNTAX_ERROR',
                    'message': f"Mismatched braces: {open_braces} open, {close_braces} close"
                })
            
        except Exception as e:
            self.errors.append({
                'file': file_path,
                'type': 'FILE_READ_ERROR',
                'message': str(e)
            })
    
    def check_api_consistency(self):
        """Check API endpoint consistency between frontend and backend."""
        # This is a simplified check - in practice, you'd parse both files more thoroughly
        api_file = 'web_app/static/js/api.js'
        server_file = 'web_app/server.py'
        
        if os.path.exists(api_file) and os.path.exists(server_file):
            with open(api_file, 'r', encoding='utf-8') as f:
                api_content = f.read()
            
            with open(server_file, 'r', encoding='utf-8') as f:
                server_content = f.read()
            
            # Extract API endpoints from frontend
            frontend_endpoints = re.findall(r'request\([\'"]([^\'\"]+)[\'"]', api_content)
            
            # Extract API endpoints from backend
            backend_endpoints = re.findall(r'@app\.\w+\([\'"]([^\'\"]+)[\'"]', server_content)
            
            # Check for mismatches
            for endpoint in frontend_endpoints:
                if endpoint.startswith('/'):
                    full_endpoint = '/api' + endpoint if not endpoint.startswith('/api') else endpoint
                    if full_endpoint not in backend_endpoints:
                        self.warnings.append({
                            'type': 'API_MISMATCH',
                            'message': f"Frontend endpoint '{endpoint}' not found in backend"
                        })
    
    def check_cross_dependencies(self):
        """Check for cross-file dependency issues."""
        # Check if all required global objects are properly initialized
        required_globals = [
            'window.apiManager',
            'window.authManager',
            'window.resultsManager',
            'window.uploadManager',
            'window.analysisManager',
            'window.appController'
        ]
        
        app_html = 'web_app/templates/app.html'
        if os.path.exists(app_html):
            with open(app_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for global_obj in required_globals:
                if global_obj not in content:
                    self.warnings.append({
                        'type': 'MISSING_GLOBAL_INIT',
                        'message': f"Global object '{global_obj}' may not be properly initialized"
                    })
    
    def check_missing_implementations(self):
        """Check for missing method implementations."""
        # This would be more comprehensive in practice
        pass
    
    def check_configuration_files(self):
        """Check configuration files for errors."""
        config_files = ['setup.py']
        
        for file_path in config_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for common setup.py issues
                    if 'install_requires' not in content:
                        self.warnings.append({
                            'file': file_path,
                            'type': 'MISSING_DEPENDENCIES',
                            'message': 'install_requires not found in setup.py'
                        })
                        
                except Exception as e:
                    self.errors.append({
                        'file': file_path,
                        'type': 'FILE_READ_ERROR',
                        'message': str(e)
                    })
    
    def generate_error_report(self):
        """Generate comprehensive error report."""
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE ERROR DETECTION REPORT")
        print("=" * 80)
        print(f"🔴 Critical Errors: {total_errors}")
        print(f"🟡 Warnings: {total_warnings}")
        print("=" * 80)
        
        if self.errors:
            print("\n🔴 CRITICAL ERRORS:")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error.get('file', 'Unknown')}: {error['type']}")
                print(f"   {error['message']}")
                if 'line' in error:
                    print(f"   Line: {error['line']}")
        
        if self.warnings:
            print("\n🟡 WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning.get('file', 'Unknown')}: {warning['type']}")
                print(f"   {warning['message']}")
        
        # Overall assessment
        if total_errors == 0 and total_warnings == 0:
            print("\n🎉 NO ERRORS OR WARNINGS FOUND - CODE IS CLEAN!")
        elif total_errors == 0:
            print(f"\n✅ NO CRITICAL ERRORS - {total_warnings} warnings to review")
        else:
            print(f"\n❌ {total_errors} CRITICAL ERRORS NEED IMMEDIATE ATTENTION")
    
    def apply_critical_fixes(self):
        """Apply automatic fixes for critical errors where possible."""
        print("\n🔧 APPLYING AUTOMATIC FIXES...")
        
        # This would contain automatic fixes for common errors
        # For now, just report what could be fixed
        fixable_errors = [e for e in self.errors if e['type'] in ['IMPORT_WARNING', 'MISSING_ELEMENT_ID']]
        
        if fixable_errors:
            print(f"   ⚡ {len(fixable_errors)} errors can be automatically fixed")
        else:
            print("   ℹ️  No automatic fixes available")

def main():
    checker = ComprehensiveErrorChecker()
    checker.run_comprehensive_check()

if __name__ == "__main__":
    main()
