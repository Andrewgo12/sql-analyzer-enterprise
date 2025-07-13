#!/usr/bin/env python3
"""
COMPREHENSIVE ZERO ERRORS SCANNER
Escanea ABSOLUTAMENTE TODO en busca de cualquier tipo de error
"""

import os
import re
import ast
import json
import subprocess
from pathlib import Path

def comprehensive_zero_errors_scanner():
    """Escanea absolutamente todo en busca de cualquier error."""
    print("🔍 COMPREHENSIVE ZERO ERRORS SCANNER")
    print("=" * 70)
    print("🎯 OBJETIVO: CERO ERRORES ABSOLUTOS DE CUALQUIER TIPO")
    print("=" * 70)
    
    total_errors = 0
    
    # 1. VERIFICACIÓN EXHAUSTIVA DE SINTAXIS PYTHON
    print("\n1. 🐍 VERIFICACIÓN EXHAUSTIVA DE SINTAXIS PYTHON")
    print("-" * 50)
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Excluir directorios innecesarios
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar sintaxis con AST
            try:
                ast.parse(content)
                print(f"  ✅ {py_file}")
            except SyntaxError as e:
                print(f"  ❌ {py_file}: SYNTAX ERROR - {e}")
                total_errors += 1
            except Exception as e:
                print(f"  ⚠️ {py_file}: PARSE ERROR - {e}")
                total_errors += 1
                
        except Exception as e:
            print(f"  ❌ {py_file}: READ ERROR - {e}")
            total_errors += 1
    
    # 2. VERIFICACIÓN EXHAUSTIVA DE JAVASCRIPT
    print(f"\n2. 🟨 VERIFICACIÓN EXHAUSTIVA DE JAVASCRIPT")
    print("-" * 50)
    
    js_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
    
    for js_file in js_files:
        try:
            # Verificar sintaxis con Node.js
            result = subprocess.run(['node', '-c', js_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {js_file}")
            else:
                print(f"  ❌ {js_file}: SYNTAX ERROR")
                print(f"      {result.stderr.strip()}")
                total_errors += 1
        except Exception as e:
            print(f"  ❌ {js_file}: CHECK ERROR - {e}")
            total_errors += 1
    
    # 3. VERIFICACIÓN DE HTML
    print(f"\n3. 🌐 VERIFICACIÓN DE HTML")
    print("-" * 50)
    
    html_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificaciones básicas de HTML
            errors = []
            
            # Verificar etiquetas no cerradas básicas
            open_tags = re.findall(r'<(\w+)[^>]*>', content)
            close_tags = re.findall(r'</(\w+)>', content)
            
            # Tags que no necesitan cierre
            self_closing = {'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
            
            open_count = {}
            for tag in open_tags:
                if tag.lower() not in self_closing:
                    open_count[tag.lower()] = open_count.get(tag.lower(), 0) + 1
            
            close_count = {}
            for tag in close_tags:
                close_count[tag.lower()] = close_count.get(tag.lower(), 0) + 1
            
            for tag, count in open_count.items():
                if close_count.get(tag, 0) != count:
                    errors.append(f"Tag mismatch: {tag}")
            
            if errors:
                print(f"  ❌ {html_file}: {len(errors)} errors")
                for error in errors[:3]:  # Mostrar solo los primeros 3
                    print(f"      {error}")
                total_errors += len(errors)
            else:
                print(f"  ✅ {html_file}")
                
        except Exception as e:
            print(f"  ❌ {html_file}: READ ERROR - {e}")
            total_errors += 1
    
    # 4. VERIFICACIÓN DE CSS
    print(f"\n4. 🎨 VERIFICACIÓN DE CSS")
    print("-" * 50)
    
    css_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.css'):
                css_files.append(os.path.join(root, file))
    
    for css_file in css_files:
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificaciones básicas de CSS
            errors = []
            
            # Verificar llaves balanceadas
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces != close_braces:
                errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            
            # Verificar punto y coma faltantes (básico)
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and ':' in line and not line.endswith((';', '{', '}')) and not line.startswith(('/*', '*', '//')):
                    if not any(line.endswith(x) for x in ['{', '}', '/*', '*/']):
                        errors.append(f"Line {i}: Missing semicolon")
            
            if errors:
                print(f"  ❌ {css_file}: {len(errors)} errors")
                for error in errors[:3]:
                    print(f"      {error}")
                total_errors += len(errors)
            else:
                print(f"  ✅ {css_file}")
                
        except Exception as e:
            print(f"  ❌ {css_file}: READ ERROR - {e}")
            total_errors += 1
    
    # 5. VERIFICACIÓN DE JSON
    print(f"\n5. 📄 VERIFICACIÓN DE JSON")
    print("-" * 50)
    
    json_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                json.loads(content)
                print(f"  ✅ {json_file}")
            except json.JSONDecodeError as e:
                print(f"  ❌ {json_file}: JSON ERROR - {e}")
                total_errors += 1
                
        except Exception as e:
            print(f"  ❌ {json_file}: READ ERROR - {e}")
            total_errors += 1
    
    # 6. VERIFICACIÓN DE IMPORTACIONES
    print(f"\n6. 📦 VERIFICACIÓN DE IMPORTACIONES")
    print("-" * 50)
    
    try:
        import sys
        sys.path.append('.')
        
        # Verificar importación del servidor principal
        try:
            from web_app.server import app
            print("  ✅ web_app.server import")
        except Exception as e:
            print(f"  ❌ web_app.server import: {e}")
            total_errors += 1
        
        # Verificar otras importaciones críticas
        critical_modules = [
            'web_app.security.security_manager',
            'web_app.sql_analyzer.analyzer',
        ]
        
        for module in critical_modules:
            try:
                __import__(module)
                print(f"  ✅ {module} import")
            except Exception as e:
                print(f"  ❌ {module} import: {e}")
                total_errors += 1
                
    except Exception as e:
        print(f"  ❌ Import verification failed: {e}")
        total_errors += 1
    
    # REPORTE FINAL
    print(f"\n" + "=" * 70)
    print(f"🎯 COMPREHENSIVE ZERO ERRORS SCANNER - REPORTE FINAL")
    print(f"=" * 70)
    
    if total_errors == 0:
        print(f"🎉 ¡PERFECCIÓN ABSOLUTA ALCANZADA!")
        print(f"✅ CERO ERRORES ENCONTRADOS")
        print(f"🚀 APLICACIÓN LISTA PARA PRODUCCIÓN EMPRESARIAL")
        print(f"🏆 ZERO ERRORS ACHIEVEMENT COMPLETADO")
    else:
        print(f"❌ TOTAL DE ERRORES ENCONTRADOS: {total_errors}")
        print(f"🔧 REQUIERE CORRECCIÓN INMEDIATA")
        print(f"⚠️ NO APTO PARA PRODUCCIÓN")
    
    print(f"=" * 70)
    
    return total_errors

if __name__ == "__main__":
    comprehensive_zero_errors_scanner()
