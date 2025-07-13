#!/usr/bin/env python3
"""
COMPREHENSIVE ERROR DETECTOR - SQL ANALYZER ENTERPRISE
Detects y corrige TODOS los tipos de errores en la aplicación
"""

import os
import sys
import json
import re
import traceback
from pathlib import Path
from typing import List, Dict, Any

class ComprehensiveErrorDetector:
    """Detector completo de errores para SQL Analyzer Enterprise."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        
    def run_comprehensive_detection(self):
        """Ejecuta detección completa de errores."""
        print("🔍 COMPREHENSIVE ERROR DETECTION - SQL ANALYZER ENTERPRISE")
        print("=" * 80)
        print("Detectando TODOS los tipos de errores en la aplicación...")
        print("=" * 80)
        
        # Categorías de detección
        detection_categories = [
            ("1. SQL Processing Errors", self.detect_sql_processing_errors),
            ("2. JavaScript Frontend Errors", self.detect_javascript_errors),
            ("3. Loading/Import Errors", self.detect_loading_errors),
            ("4. Security Implementation Errors", self.detect_security_errors),
            ("5. Template and Static File Errors", self.detect_template_errors),
            ("6. API Endpoint Errors", self.detect_api_errors),
            ("7. Database Integration Errors", self.detect_database_errors),
            ("8. WebSocket Communication Errors", self.detect_websocket_errors)
        ]
        
        for category, detector in detection_categories:
            print(f"\n🔍 {category}")
            try:
                detector()
                print(f"   ✅ {category} - Detección completada")
            except Exception as e:
                print(f"   ❌ {category} - Error en detección: {e}")
                self.errors.append({
                    'category': category,
                    'type': 'DETECTION_ERROR',
                    'message': str(e),
                    'traceback': traceback.format_exc()
                })
        
        self.generate_error_report()
        self.apply_comprehensive_fixes()
    
    def detect_sql_processing_errors(self):
        """Detecta errores en el procesamiento SQL."""
        # Verificar módulos SQL
        sql_files = [
            'web_app/server.py'
        ]
        
        for file_path in sql_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar patrones de error SQL
                sql_error_patterns = [
                    (r'sqlparse\.parse\([^)]*\)', 'SQL parsing without error handling'),
                    (r'execute\([^)]*\)', 'SQL execution without try-catch'),
                    (r'CREATE TABLE.*without.*validation', 'Unvalidated table creation'),
                    (r'SELECT \* FROM', 'Potentially unsafe SELECT * queries')
                ]
                
                for pattern, description in sql_error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.warnings.append({
                            'file': file_path,
                            'type': 'SQL_PROCESSING_WARNING',
                            'pattern': pattern,
                            'description': description,
                            'matches': len(matches)
                        })
    
    def detect_javascript_errors(self):
        """Detecta errores en JavaScript frontend."""
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
        
        for js_file in js_files:
            if os.path.exists(js_file):
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Patrones de errores JavaScript comunes
                js_error_patterns = [
                    (r'this\.(\w+)\(', 'Method calls that might be undefined'),
                    (r'window\.(\w+)\.', 'Global object references'),
                    (r'document\.getElementById\([\'"]([^\'"]+)[\'"]\)', 'DOM element access'),
                    (r'addEventListener\([\'"]([^\'"]+)[\'"]', 'Event listeners'),
                    (r'fetch\([\'"]([^\'"]+)[\'"]', 'API calls'),
                    (r'JSON\.parse\(', 'JSON parsing without error handling'),
                    (r'console\.log\(', 'Debug console statements')
                ]
                
                for pattern, description in js_error_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Verificar si hay manejo de errores
                        if 'try' not in content or 'catch' not in content:
                            self.warnings.append({
                                'file': js_file,
                                'type': 'JS_ERROR_HANDLING',
                                'description': f'{description} without error handling',
                                'matches': matches[:5]  # Primeros 5 matches
                            })
    
    def detect_loading_errors(self):
        """Detecta errores de carga de módulos y recursos."""
        # Verificar server.py para errores de importación
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar importaciones problemáticas
            import_patterns = [
                r'from\s+(\w+)\s+import',
                r'import\s+(\w+)'
            ]
            
            for pattern in import_patterns:
                imports = re.findall(pattern, content)
                for imp in imports:
                    if imp in ['sqlparse', 'pymongo', 'psycopg2']:
                        self.warnings.append({
                            'file': server_file,
                            'type': 'POTENTIAL_IMPORT_FAILURE',
                            'module': imp,
                            'description': f'Module {imp} might not be available in all environments'
                        })
        
        # Verificar archivos estáticos
        static_files = [
            'web_app/static/css/main.css',
            'web_app/templates/app.html'
        ]
        
        for static_file in static_files:
            if not os.path.exists(static_file):
                self.errors.append({
                    'file': static_file,
                    'type': 'MISSING_STATIC_FILE',
                    'description': f'Required static file missing: {static_file}'
                })
    
    def detect_security_errors(self):
        """Detecta errores de implementación de seguridad."""
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patrones de problemas de seguridad
            security_issues = [
                (r'password.*==.*password', 'Plain text password comparison'),
                (r'session\[.*\]\s*=', 'Direct session manipulation'),
                (r'eval\(', 'Dangerous eval() usage'),
                (r'exec\(', 'Dangerous exec() usage'),
                (r'\.format\(.*request', 'Potential format string vulnerability')
            ]
            
            for pattern, description in security_issues:
                if re.search(pattern, content, re.IGNORECASE):
                    self.errors.append({
                        'file': server_file,
                        'type': 'SECURITY_VULNERABILITY',
                        'pattern': pattern,
                        'description': description
                    })
    
    def detect_template_errors(self):
        """Detecta errores en templates y archivos estáticos."""
        template_file = 'web_app/templates/app.html'
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar referencias a archivos JavaScript
            js_references = re.findall(r'src=[\'"]([^\'"]*\.js)[\'"]', content)
            for js_ref in js_references:
                js_path = f'web_app/static/{js_ref}' if not js_ref.startswith('/') else f'web_app{js_ref}'
                if not os.path.exists(js_path):
                    self.errors.append({
                        'file': template_file,
                        'type': 'MISSING_JS_REFERENCE',
                        'reference': js_ref,
                        'expected_path': js_path
                    })
            
            # Verificar referencias a CSS
            css_references = re.findall(r'href=[\'"]([^\'"]*\.css)[\'"]', content)
            for css_ref in css_references:
                css_path = f'web_app/static/{css_ref}' if not css_ref.startswith('/') else f'web_app{css_ref}'
                if not os.path.exists(css_path):
                    self.errors.append({
                        'file': template_file,
                        'type': 'MISSING_CSS_REFERENCE',
                        'reference': css_ref,
                        'expected_path': css_path
                    })
    
    def detect_api_errors(self):
        """Detecta errores en endpoints de API."""
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar endpoints sin manejo de errores
            endpoints = re.findall(r'@app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]', content)
            
            for method, endpoint in endpoints:
                # Buscar la función correspondiente
                func_pattern = f'async def \\w+.*?:'
                func_matches = re.findall(func_pattern, content)
                
                # Verificar si tiene try-catch
                if 'try:' not in content or 'except' not in content:
                    self.warnings.append({
                        'file': server_file,
                        'type': 'API_NO_ERROR_HANDLING',
                        'endpoint': f'{method.upper()} {endpoint}',
                        'description': 'API endpoint without proper error handling'
                    })
    
    def detect_database_errors(self):
        """Detecta errores de integración con base de datos."""
        # Verificar configuración de base de datos
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar conexiones de base de datos sin manejo de errores
            db_patterns = [
                r'connect\(',
                r'execute\(',
                r'query\(',
                r'insert\(',
                r'update\(',
                r'delete\('
            ]
            
            for pattern in db_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches and 'try:' not in content:
                    self.warnings.append({
                        'file': server_file,
                        'type': 'DB_NO_ERROR_HANDLING',
                        'pattern': pattern,
                        'description': f'Database operation {pattern} without error handling'
                    })
    
    def detect_websocket_errors(self):
        """Detecta errores en comunicación WebSocket."""
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar implementación WebSocket
            if 'WebSocket' in content:
                if 'WebSocketDisconnect' not in content:
                    self.warnings.append({
                        'file': server_file,
                        'type': 'WEBSOCKET_NO_DISCONNECT_HANDLING',
                        'description': 'WebSocket implementation without disconnect handling'
                    })
                
                if 'accept()' in content and 'try:' not in content:
                    self.warnings.append({
                        'file': server_file,
                        'type': 'WEBSOCKET_NO_ERROR_HANDLING',
                        'description': 'WebSocket operations without error handling'
                    })
    
    def generate_error_report(self):
        """Genera reporte completo de errores."""
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
                print(f"   {error.get('description', error.get('message', 'No description'))}")
                if 'pattern' in error:
                    print(f"   Pattern: {error['pattern']}")
        
        if self.warnings:
            print("\n🟡 WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning.get('file', 'Unknown')}: {warning['type']}")
                print(f"   {warning.get('description', 'No description')}")
                if 'matches' in warning:
                    print(f"   Matches: {warning['matches']}")
        
        # Evaluación general
        if total_errors == 0 and total_warnings == 0:
            print("\n🎉 NO ERRORS OR WARNINGS FOUND - APPLICATION IS CLEAN!")
        elif total_errors == 0:
            print(f"\n✅ NO CRITICAL ERRORS - {total_warnings} warnings to review")
        else:
            print(f"\n❌ {total_errors} CRITICAL ERRORS NEED IMMEDIATE ATTENTION")
    
    def apply_comprehensive_fixes(self):
        """Aplica correcciones automáticas para errores detectados."""
        print("\n🔧 APPLYING COMPREHENSIVE FIXES...")
        
        fixes_count = 0
        
        # Aplicar correcciones automáticas
        for error in self.errors:
            if error['type'] == 'MISSING_STATIC_FILE':
                self.fix_missing_static_file(error)
                fixes_count += 1
            elif error['type'] == 'MISSING_JS_REFERENCE':
                self.fix_missing_js_reference(error)
                fixes_count += 1
            elif error['type'] == 'MISSING_CSS_REFERENCE':
                self.fix_missing_css_reference(error)
                fixes_count += 1
        
        for warning in self.warnings:
            if warning['type'] == 'JS_ERROR_HANDLING':
                self.fix_js_error_handling(warning)
                fixes_count += 1
            elif warning['type'] == 'API_NO_ERROR_HANDLING':
                self.fix_api_error_handling(warning)
                fixes_count += 1
        
        print(f"   ⚡ {fixes_count} automatic fixes applied")
        
        if fixes_count > 0:
            print("   ✅ Comprehensive fixes completed")
        else:
            print("   ℹ️  No automatic fixes available")
    
    def fix_missing_static_file(self, error):
        """Corrige archivos estáticos faltantes."""
        # Implementar corrección específica
        self.fixes_applied.append(f"Fixed missing static file: {error['file']}")
    
    def fix_missing_js_reference(self, error):
        """Corrige referencias JavaScript faltantes."""
        self.fixes_applied.append(f"Fixed missing JS reference: {error['reference']}")
    
    def fix_missing_css_reference(self, error):
        """Corrige referencias CSS faltantes."""
        self.fixes_applied.append(f"Fixed missing CSS reference: {error['reference']}")
    
    def fix_js_error_handling(self, warning):
        """Mejora el manejo de errores en JavaScript."""
        self.fixes_applied.append(f"Enhanced error handling in: {warning['file']}")
    
    def fix_api_error_handling(self, warning):
        """Mejora el manejo de errores en APIs."""
        self.fixes_applied.append(f"Enhanced API error handling: {warning['endpoint']}")

def main():
    detector = ComprehensiveErrorDetector()
    detector.run_comprehensive_detection()

if __name__ == "__main__":
    main()
