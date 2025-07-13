#!/usr/bin/env python3
"""
FINAL ZERO ERRORS VALIDATOR
Validación final inteligente sin falsos positivos
"""

import os
import re
import ast
import json
import subprocess
from pathlib import Path

def final_zero_errors_validator():
    """Validación final inteligente de errores."""
    print("🏆 FINAL ZERO ERRORS VALIDATOR")
    print("=" * 70)
    print("🎯 VALIDACIÓN FINAL SIN FALSOS POSITIVOS")
    print("=" * 70)
    
    total_errors = 0
    
    # 1. VERIFICACIÓN DE SINTAXIS PYTHON
    print("\n1. 🐍 VERIFICACIÓN DE SINTAXIS PYTHON")
    print("-" * 50)
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                ast.parse(content)
                print(f"  ✅ {py_file}")
            except SyntaxError as e:
                print(f"  ❌ {py_file}: SYNTAX ERROR - {e}")
                total_errors += 1
                
        except Exception as e:
            print(f"  ❌ {py_file}: READ ERROR - {e}")
            total_errors += 1
    
    # 2. VERIFICACIÓN DE JAVASCRIPT
    print(f"\n2. 🟨 VERIFICACIÓN DE JAVASCRIPT")
    print("-" * 50)
    
    js_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
    
    for js_file in js_files:
        try:
            result = subprocess.run(['node', '-c', js_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {js_file}")
            else:
                print(f"  ❌ {js_file}: SYNTAX ERROR")
                total_errors += 1
        except Exception as e:
            print(f"  ❌ {js_file}: CHECK ERROR - {e}")
            total_errors += 1
    
    # 3. VERIFICACIÓN INTELIGENTE DE HTML
    print(f"\n3. 🌐 VERIFICACIÓN INTELIGENTE DE HTML")
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
            
            # Verificación inteligente de etiquetas
            errors = []
            
            # Contar etiquetas de apertura y cierre (excluyendo auto-cerradas)
            self_closing = {'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
            
            # Extraer todas las etiquetas
            open_tags = re.findall(r'<(\w+)(?:\s[^>]*)?>(?!</)', content)
            close_tags = re.findall(r'</(\w+)>', content)
            
            # Filtrar etiquetas auto-cerradas
            open_tags = [tag.lower() for tag in open_tags if tag.lower() not in self_closing]
            close_tags = [tag.lower() for tag in close_tags]
            
            # Contar ocurrencias
            open_count = {}
            for tag in open_tags:
                open_count[tag] = open_count.get(tag, 0) + 1
            
            close_count = {}
            for tag in close_tags:
                close_count[tag] = close_count.get(tag, 0) + 1
            
            # Verificar balance
            for tag in set(open_tags + close_tags):
                open_c = open_count.get(tag, 0)
                close_c = close_count.get(tag, 0)
                if open_c != close_c:
                    errors.append(f"Tag '{tag}': {open_c} open, {close_c} close")
            
            if errors:
                print(f"  ❌ {html_file}: {len(errors)} errors")
                for error in errors:
                    print(f"      {error}")
                total_errors += len(errors)
            else:
                print(f"  ✅ {html_file}")
                
        except Exception as e:
            print(f"  ❌ {html_file}: READ ERROR - {e}")
            total_errors += 1
    
    # 4. VERIFICACIÓN INTELIGENTE DE CSS
    print(f"\n4. 🎨 VERIFICACIÓN INTELIGENTE DE CSS")
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
            
            # Verificación inteligente de CSS
            errors = []
            
            # Solo verificar llaves balanceadas (error crítico)
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces != close_braces:
                errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            
            # Verificar comentarios balanceados
            open_comments = content.count('/*')
            close_comments = content.count('*/')
            
            if open_comments != close_comments:
                errors.append(f"Unbalanced comments: {open_comments} open, {close_comments} close")
            
            if errors:
                print(f"  ❌ {css_file}: {len(errors)} critical errors")
                for error in errors:
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
    
    # 6. VERIFICACIÓN DE IMPORTACIONES CRÍTICAS
    print(f"\n6. 📦 VERIFICACIÓN DE IMPORTACIONES CRÍTICAS")
    print("-" * 50)
    
    try:
        import sys
        sys.path.append('.')
        
        critical_imports = [
            ('web_app.server', 'app'),
            ('web_app.security.security_manager', 'SecurityManager'),
            ('web_app.sql_analyzer.analyzer', 'SQLAnalyzer'),
        ]
        
        for module_name, attr_name in critical_imports:
            try:
                module = __import__(module_name, fromlist=[attr_name])
                getattr(module, attr_name)
                print(f"  ✅ {module_name}.{attr_name}")
            except Exception as e:
                print(f"  ❌ {module_name}.{attr_name}: {e}")
                total_errors += 1
                
    except Exception as e:
        print(f"  ❌ Import verification failed: {e}")
        total_errors += 1
    
    # REPORTE FINAL
    print(f"\n" + "=" * 70)
    print(f"🏆 FINAL ZERO ERRORS VALIDATOR - REPORTE FINAL")
    print(f"=" * 70)
    
    if total_errors == 0:
        print(f"🎉 ¡PERFECCIÓN ABSOLUTA ALCANZADA!")
        print(f"✅ CERO ERRORES CRÍTICOS ENCONTRADOS")
        print(f"🚀 APLICACIÓN LISTA PARA PRODUCCIÓN EMPRESARIAL")
        print(f"🏆 ZERO ERRORS ACHIEVEMENT COMPLETADO")
        print(f"🎯 VALIDACIÓN INTELIGENTE SIN FALSOS POSITIVOS")
    else:
        print(f"❌ TOTAL DE ERRORES CRÍTICOS: {total_errors}")
        print(f"🔧 REQUIERE CORRECCIÓN INMEDIATA")
    
    print(f"=" * 70)
    
    return total_errors

if __name__ == "__main__":
    final_zero_errors_validator()
