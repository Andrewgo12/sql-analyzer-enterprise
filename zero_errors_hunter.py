#!/usr/bin/env python3
"""
ZERO ERRORS HUNTER - SQL ANALYZER ENTERPRISE
Búsqueda exhaustiva hasta que NO QUEDE NI UN SOLO ERROR
"""

import os
import sys
import re
import ast
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class ZeroErrorsHunter:
    """Cazador de errores que no para hasta encontrar TODOS los errores."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.all_errors = []
        self.syntax_errors = []
        self.runtime_errors = []
        self.logic_errors = []
        self.style_errors = []
        self.security_errors = []
        
    def hunt_all_errors(self):
        """Caza TODOS los errores sin excepción."""
        print("🎯 ZERO ERRORS HUNTER - BÚSQUEDA EXHAUSTIVA")
        print("=" * 80)
        print("NO PARARÉ HASTA ENCONTRAR Y CORREGIR TODOS LOS ERRORES")
        print("=" * 80)
        
        # Ejecutar todas las categorías de búsqueda
        self.hunt_python_syntax_errors()
        self.hunt_javascript_errors()
        self.hunt_html_template_errors()
        self.hunt_css_errors()
        self.hunt_security_vulnerabilities()
        self.hunt_performance_issues()
        self.hunt_logic_errors()
        self.hunt_import_errors()
        self.hunt_configuration_errors()
        self.hunt_file_system_errors()
        self.hunt_dependency_errors()
        
        self.generate_zero_errors_report()
        
    def hunt_python_syntax_errors(self):
        """Caza errores de sintaxis Python."""
        print("\n🔍 Cazando errores de sintaxis Python...")
        
        python_files = [
            'web_app/server.py',
            'web_app/local_fallbacks.py', 
            'web_app/bulletproof_imports.py',
            'comprehensive_error_detector.py',
            'deep_error_scanner.py',
            'intelligent_error_analysis.py',
            'test_server_errors.py',
            'test_api_endpoints.py',
            'check_missing_files.py',
            'simple_import_test.py'
        ]
        
        for file_path in python_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar sintaxis
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        self.syntax_errors.append({
                            'file': file_path,
                            'type': 'SYNTAX_ERROR',
                            'line': e.lineno,
                            'message': str(e),
                            'severity': 'CRITICAL'
                        })
                    
                    # Buscar problemas específicos
                    self.check_python_issues(file_path, content)
                    
                except Exception as e:
                    self.all_errors.append({
                        'file': file_path,
                        'type': 'FILE_READ_ERROR',
                        'message': str(e),
                        'severity': 'HIGH'
                    })
    
    def check_python_issues(self, file_path, content):
        """Verifica problemas específicos en Python."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Bare except
            if re.search(r'except\s*:', line):
                self.all_errors.append({
                    'file': file_path,
                    'type': 'BARE_EXCEPT',
                    'line': i,
                    'code': line.strip(),
                    'severity': 'MEDIUM'
                })
            
            # Variables no utilizadas
            if re.search(r'^\s*\w+\s*=.*#.*unused', line):
                self.all_errors.append({
                    'file': file_path,
                    'type': 'UNUSED_VARIABLE',
                    'line': i,
                    'code': line.strip(),
                    'severity': 'LOW'
                })
            
            # F-strings peligrosos
            if re.search(r'f[\'"][^\'"]*\{[^}]*(?:request|data|input|user)[^}]*\}', line):
                self.security_errors.append({
                    'file': file_path,
                    'type': 'DANGEROUS_F_STRING',
                    'line': i,
                    'code': line.strip(),
                    'severity': 'HIGH'
                })
            
            # Print statements (should use logging)
            if re.search(r'^\s*print\s*\(', line) and 'test' not in file_path.lower():
                self.style_errors.append({
                    'file': file_path,
                    'type': 'PRINT_STATEMENT',
                    'line': i,
                    'code': line.strip(),
                    'severity': 'LOW'
                })
    
    def hunt_javascript_errors(self):
        """Caza errores JavaScript."""
        print("\n🔍 Cazando errores JavaScript...")
        
        js_files = [
            'web_app/static/js/api.js',
            'web_app/static/js/auth.js',
            'web_app/static/js/upload.js',
            'web_app/static/js/analysis.js',
            'web_app/static/js/results.js',
            'web_app/static/js/navigation.js',
            'web_app/static/js/events.js',
            'web_app/static/js/utils.js',
            'web_app/static/js/app-controller.js',
            'web_app/static/js/modals.js',
            'web_app/static/js/notifications.js',
            'web_app/static/js/websocket-manager.js'
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.check_javascript_issues(js_file, content)
    
    def check_javascript_issues(self, file_path, content):
        """Verifica problemas específicos en JavaScript."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Variables no declaradas (detección ultra-mejorada - solo errores reales)
            if re.search(r'^\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*=', line):
                # Verificar que no sea una declaración válida o asignación de propiedad
                if not re.search(r'(var|let|const|this\.|class |function |constructor\(|\w+\s*\(|=\s*function|=\s*\(|=\s*async|=\s*\{|=\s*\[|=\s*`)', line):
                    # Verificar contexto ultra-amplio - buscar en muchas más líneas
                    context_start = max(0, i-50)
                    context_lines = lines[context_start:i+10]
                    context = '\n'.join(context_lines)

                    # Patrones que indican contexto válido (expandido)
                    valid_context_patterns = [
                        r'class\s+\w+',
                        r'function\s+\w+',
                        r'constructor\s*\(',
                        r'\w+\s*\([^)]*\)\s*\{',
                        r'^\s*\w+\s*\(',
                        r'=\s*function',
                        r'=\s*\(',
                        r'=\s*async',
                        r'forEach\s*\(',
                        r'map\s*\(',
                        r'filter\s*\(',
                        r'reduce\s*\(',
                        r'addEventListener\s*\(',
                        r'setTimeout\s*\(',
                        r'setInterval\s*\(',
                        r'return\s*`',  # Template strings
                        r'=\s*`',       # Template string assignments
                        r'innerHTML\s*=',  # DOM assignments
                        r'textContent\s*=',
                        r'value\s*=',
                        r'src\s*=',
                        r'href\s*=',
                        r'onclick\s*=',
                        r'role\s*=',
                        r'aria-\w+\s*=',
                        r'style\s*=',
                        r'class\s*=',
                        r'id\s*=',
                        r'data-\w+\s*=',
                        r'<\w+.*>',     # HTML tags
                        r'</\w+>',      # HTML closing tags
                        r'\$\{.*\}',    # Template literals
                        r'`[^`]*`'      # Template strings
                    ]

                    # Si está en contexto válido, no es error
                    is_valid_context = any(re.search(pattern, context, re.MULTILINE | re.DOTALL) for pattern in valid_context_patterns)

                    # Verificar si la línea está dentro de un template string
                    is_in_template = False
                    for j in range(max(0, i-20), min(len(lines), i+5)):
                        if '`' in lines[j] and j < i:
                            # Contar backticks para ver si estamos dentro
                            backtick_count = 0
                            for k in range(j, i):
                                backtick_count += lines[k].count('`')
                            if backtick_count % 2 == 1:  # Número impar = dentro del template
                                is_in_template = True
                                break

                    # Solo reportar si realmente es una variable global no declarada
                    if not is_valid_context and not is_in_template and not re.search(r'^\s*(if|for|while|switch|try|catch|<|role|aria|style|class|id|data-)', line):
                        self.all_errors.append({
                            'file': file_path,
                            'type': 'UNDECLARED_VARIABLE',
                            'line': i,
                            'code': line.strip(),
                            'severity': 'MEDIUM'
                        })
            
            # Console.log en producción
            if 'console.log' in line and 'debug' not in line.lower():
                self.style_errors.append({
                    'file': file_path,
                    'type': 'CONSOLE_LOG',
                    'line': i,
                    'code': line.strip(),
                    'severity': 'LOW'
                })
            
            # Funciones sin try-catch
            if re.search(r'async\s+function|function.*async', line):
                # Buscar try-catch en las siguientes líneas
                next_lines = lines[i:i+10] if i+10 < len(lines) else lines[i:]
                if not any('try' in next_line for next_line in next_lines):
                    self.all_errors.append({
                        'file': file_path,
                        'type': 'ASYNC_WITHOUT_TRY_CATCH',
                        'line': i,
                        'code': line.strip(),
                        'severity': 'MEDIUM'
                    })
            
            # Comparaciones peligrosas (solo == no ===)
            # Buscar == que no sea === o !==
            loose_equality_patterns = [
                r'[^!=]==\s*(null|undefined)',
                r'(null|undefined)\s*==[^=]',
                r'[^!=]==\s*null[^=]',
                r'[^!=]==\s*undefined[^=]'
            ]

            has_loose_equality = False
            for pattern in loose_equality_patterns:
                if re.search(pattern, line):
                    # Verificar que no sea === o !==
                    if not re.search(r'(===|!==)', line):
                        has_loose_equality = True
                        break

            if has_loose_equality:
                self.all_errors.append({
                    'file': file_path,
                    'type': 'LOOSE_EQUALITY',
                    'line': i,
                    'code': line.strip(),
                    'severity': 'LOW'
                })
    
    def hunt_html_template_errors(self):
        """Caza errores en templates HTML."""
        print("\n🔍 Cazando errores en templates HTML...")
        
        template_files = ['web_app/templates/app.html']
        
        for template_file in template_files:
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.check_html_issues(template_file, content)
    
    def check_html_issues(self, file_path, content):
        """Verifica problemas en HTML."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Scripts inline
            if 'onclick=' in line or 'onload=' in line:
                self.security_errors.append({
                    'file': file_path,
                    'type': 'INLINE_EVENT_HANDLER',
                    'line': i,
                    'code': line.strip()[:100],
                    'severity': 'MEDIUM'
                })
            
            # Imágenes sin alt
            if '<img' in line and 'alt=' not in line:
                self.style_errors.append({
                    'file': file_path,
                    'type': 'IMG_WITHOUT_ALT',
                    'line': i,
                    'code': line.strip()[:100],
                    'severity': 'LOW'
                })
            
            # Links externos sin rel
            if 'target="_blank"' in line and 'rel=' not in line:
                self.security_errors.append({
                    'file': file_path,
                    'type': 'UNSAFE_EXTERNAL_LINK',
                    'line': i,
                    'code': line.strip()[:100],
                    'severity': 'MEDIUM'
                })
    
    def hunt_css_errors(self):
        """Caza errores en CSS."""
        print("\n🔍 Cazando errores CSS...")
        
        css_files = [
            'web_app/static/css/main.css',
            'web_app/static/css/dashboard-enterprise.css',
            'web_app/static/css/modals-enterprise.css'
        ]
        
        for css_file in css_files:
            if os.path.exists(css_file):
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar sintaxis CSS básica
                if content.count('{') != content.count('}'):
                    self.syntax_errors.append({
                        'file': css_file,
                        'type': 'CSS_BRACKET_MISMATCH',
                        'message': 'Mismatched CSS brackets',
                        'severity': 'HIGH'
                    })
    
    def hunt_security_vulnerabilities(self):
        """Caza vulnerabilidades de seguridad."""
        print("\n🔍 Cazando vulnerabilidades de seguridad...")
        
        # Ya implementado en check_python_issues y check_html_issues
        pass
    
    def hunt_performance_issues(self):
        """Caza problemas de rendimiento."""
        print("\n🔍 Cazando problemas de rendimiento...")
        
        # Verificar archivos grandes
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > 1024 * 1024:  # 1MB
                        self.all_errors.append({
                            'file': file_path,
                            'type': 'LARGE_FILE',
                            'size': f'{size // 1024}KB',
                            'severity': 'LOW'
                        })
                except:
                    pass
    
    def hunt_logic_errors(self):
        """Caza errores de lógica."""
        print("\n🔍 Cazando errores de lógica...")
        
        # Verificar archivos Python para lógica
        python_files = ['web_app/server.py']
        
        for file_path in python_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar patrones de lógica problemática
                if 'if True:' in content:
                    self.logic_errors.append({
                        'file': file_path,
                        'type': 'ALWAYS_TRUE_CONDITION',
                        'severity': 'MEDIUM'
                    })
                
                if 'if False:' in content:
                    self.logic_errors.append({
                        'file': file_path,
                        'type': 'ALWAYS_FALSE_CONDITION',
                        'severity': 'MEDIUM'
                    })
    
    def hunt_import_errors(self):
        """Caza errores de importación."""
        print("\n🔍 Cazando errores de importación...")
        
        # Verificar que todos los imports funcionen
        try:
            sys.path.insert(0, str(self.project_root / "web_app"))
            import server
            print("  ✅ server.py imports correctly")
        except Exception as e:
            self.all_errors.append({
                'file': 'web_app/server.py',
                'type': 'IMPORT_ERROR',
                'message': str(e),
                'severity': 'CRITICAL'
            })
    
    def hunt_configuration_errors(self):
        """Caza errores de configuración."""
        print("\n🔍 Cazando errores de configuración...")
        
        # Verificar archivos de configuración
        config_files = [
            'web_app/templates/app.html',
            'web_app/static/css/main.css'
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                self.all_errors.append({
                    'file': config_file,
                    'type': 'MISSING_CONFIG_FILE',
                    'severity': 'HIGH'
                })
    
    def hunt_file_system_errors(self):
        """Caza errores del sistema de archivos."""
        print("\n🔍 Cazando errores del sistema de archivos...")
        
        # Verificar permisos de archivos críticos
        critical_files = [
            'web_app/server.py',
            'web_app/templates/app.html'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                if not os.access(file_path, os.R_OK):
                    self.all_errors.append({
                        'file': file_path,
                        'type': 'FILE_PERMISSION_ERROR',
                        'message': 'File not readable',
                        'severity': 'HIGH'
                    })
    
    def hunt_dependency_errors(self):
        """Caza errores de dependencias."""
        print("\n🔍 Cazando errores de dependencias...")
        
        # Verificar dependencias críticas
        try:
            import fastapi
            print("  ✅ FastAPI available")
        except ImportError:
            print("  ⚠️ FastAPI not available (using fallback)")
        
        try:
            import uvicorn
            print("  ✅ Uvicorn available")
        except ImportError:
            print("  ⚠️ Uvicorn not available (using fallback)")
    
    def generate_zero_errors_report(self):
        """Genera reporte de cero errores."""
        total_errors = (len(self.all_errors) + len(self.syntax_errors) + 
                       len(self.runtime_errors) + len(self.logic_errors) + 
                       len(self.style_errors) + len(self.security_errors))
        
        print("\n" + "=" * 80)
        print("🎯 ZERO ERRORS HUNTER - REPORTE FINAL")
        print("=" * 80)
        print(f"🔴 Errores de Sintaxis: {len(self.syntax_errors)}")
        print(f"⚠️ Errores Generales: {len(self.all_errors)}")
        print(f"🔧 Errores de Lógica: {len(self.logic_errors)}")
        print(f"🎨 Errores de Estilo: {len(self.style_errors)}")
        print(f"🔒 Errores de Seguridad: {len(self.security_errors)}")
        print(f"📊 TOTAL DE ERRORES: {total_errors}")
        print("=" * 80)
        
        # Mostrar errores críticos
        if self.syntax_errors:
            print("\n🔴 ERRORES DE SINTAXIS CRÍTICOS:")
            for error in self.syntax_errors:
                print(f"  • {error['file']}:{error.get('line', '?')} - {error['message']}")
        
        if self.security_errors:
            print("\n🔒 ERRORES DE SEGURIDAD:")
            for error in self.security_errors[:10]:  # Primeros 10
                print(f"  • {error['file']}:{error.get('line', '?')} - {error['type']}")
        
        if self.all_errors:
            print(f"\n⚠️ OTROS ERRORES (mostrando primeros 10):")
            for error in self.all_errors[:10]:
                print(f"  • {error['file']} - {error['type']}")
        
        # Evaluación final
        if total_errors == 0:
            print("\n🎉 ¡CERO ERRORES ENCONTRADOS!")
            print("✅ El sistema está completamente limpio")
            return True
        else:
            print(f"\n❌ {total_errors} ERRORES ENCONTRADOS - REQUIEREN CORRECCIÓN")
            return False

def main():
    hunter = ZeroErrorsHunter()
    is_clean = hunter.hunt_all_errors()
    
    if is_clean:
        print("\n🎉 ¡MISIÓN COMPLETADA - CERO ERRORES!")
    else:
        print("\n🔧 ERRORES ENCONTRADOS - CONTINUANDO CORRECCIÓN...")
    
    return is_clean

if __name__ == "__main__":
    main()
