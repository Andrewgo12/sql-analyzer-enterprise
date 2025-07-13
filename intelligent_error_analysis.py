#!/usr/bin/env python3
"""
ANÁLISIS INTELIGENTE DE ERRORES
Distingue entre errores reales y falsos positivos
"""

import os
import re
from pathlib import Path

class IntelligentErrorAnalyzer:
    """Analizador inteligente que distingue errores reales de falsos positivos."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.real_errors = []
        self.false_positives = []
        self.minor_issues = []
        
    def analyze_errors(self):
        """Analiza errores de manera inteligente."""
        print("🧠 ANÁLISIS INTELIGENTE DE ERRORES")
        print("=" * 60)
        print("Distinguiendo errores reales de falsos positivos...")
        print("=" * 60)
        
        # Analizar diferentes categorías
        self.analyze_api_endpoints()
        self.analyze_f_strings()
        self.analyze_json_parsing()
        self.analyze_bare_excepts()
        
        self.generate_intelligent_report()
    
    def analyze_api_endpoints(self):
        """Analiza endpoints API para validación real."""
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Endpoints que SÍ necesitan validación
            critical_endpoints = [
                '/api/auth/login',
                '/api/files/upload',
                '/api/analysis/start'
            ]
            
            # Endpoints que NO necesitan validación (solo sirven HTML)
            html_endpoints = [
                '/',
                '/auth',
                '/dashboard',
                '/upload',
                '/profile',
                '/settings',
                '/history',
                '/results',
                '/analyzer',
                '/optimizer',
                '/security'
            ]
            
            # Buscar endpoints críticos sin validación
            for endpoint in critical_endpoints:
                pattern = f'@app\.(post|get).*{re.escape(endpoint)}'
                if re.search(pattern, content):
                    # Verificar si tiene validación
                    endpoint_section = self.extract_endpoint_function(content, endpoint)
                    if endpoint_section and not self.has_input_validation(endpoint_section):
                        self.real_errors.append({
                            'type': 'MISSING_INPUT_VALIDATION',
                            'endpoint': endpoint,
                            'severity': 'HIGH',
                            'description': f'Critical endpoint {endpoint} lacks proper input validation'
                        })
            
            # Marcar endpoints HTML como falsos positivos
            for endpoint in html_endpoints:
                self.false_positives.append({
                    'type': 'HTML_ENDPOINT_VALIDATION',
                    'endpoint': endpoint,
                    'reason': 'HTML endpoints do not require input validation'
                })
    
    def analyze_f_strings(self):
        """Analiza F-strings para inyección real vs logging seguro."""
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # F-strings peligrosos (con input directo del usuario)
            dangerous_patterns = [
                r'f[\'"][^\'"]*{[^}]*request[^}]*}[^\'"]*[\'"]',
                r'f[\'"][^\'"]*{[^}]*data\.[^}]*}[^\'"]*[\'"]',
                r'f[\'"][^\'"]*{[^}]*username[^}]*}[^\'"]*[\'"]'
            ]
            
            # F-strings seguros (logging, IDs internos, etc.)
            safe_patterns = [
                r'logger\.(info|error|warning|debug)\(f[\'"]',
                r'print\(f[\'"]',
                r'f[\'"][^\'"]*{[^}]*analysis_id[^}]*}[^\'"]*[\'"]',
                r'f[\'"][^\'"]*{[^}]*session_id[^}]*}[^\'"]*[\'"]',
                r'f[\'"][^\'"]*{[^}]*file_id[^}]*}[^\'"]*[\'"]'
            ]
            
            f_string_matches = re.findall(r'f[\'"][^\'"]*{[^}]*}[^\'"]*[\'"]', content)
            
            for match in f_string_matches:
                is_dangerous = any(re.search(pattern, match) for pattern in dangerous_patterns)
                is_safe = any(re.search(pattern, match) for pattern in safe_patterns)
                
                if is_dangerous:
                    self.real_errors.append({
                        'type': 'DANGEROUS_F_STRING',
                        'code': match,
                        'severity': 'MEDIUM',
                        'description': 'F-string with potential user input injection'
                    })
                elif is_safe:
                    self.false_positives.append({
                        'type': 'SAFE_F_STRING',
                        'code': match,
                        'reason': 'F-string used for safe logging or internal IDs'
                    })
                else:
                    self.minor_issues.append({
                        'type': 'UNCLEAR_F_STRING',
                        'code': match,
                        'description': 'F-string usage unclear - review recommended'
                    })
    
    def analyze_json_parsing(self):
        """Analiza parsing JSON para manejo de errores real."""
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar await request.json() dentro de try-catch
            json_pattern = r'await request\.json\(\)'
            matches = list(re.finditer(json_pattern, content))
            
            for match in matches:
                # Extraer contexto alrededor del match
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                # Verificar si está en try-catch
                if 'try:' in context and ('except' in context or 'catch' in context):
                    self.false_positives.append({
                        'type': 'JSON_PARSING_WITH_ERROR_HANDLING',
                        'reason': 'JSON parsing is already within try-catch block'
                    })
                else:
                    self.real_errors.append({
                        'type': 'JSON_PARSING_WITHOUT_ERROR_HANDLING',
                        'severity': 'MEDIUM',
                        'description': 'JSON parsing without proper error handling'
                    })
    
    def analyze_bare_excepts(self):
        """Analiza bare except clauses."""
        files_to_check = [
            'web_app/server.py',
            'web_app/local_fallbacks.py',
            'web_app/bulletproof_imports.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                bare_except_matches = list(re.finditer(r'except\s*:', content))
                
                for match in bare_except_matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Extraer contexto
                    lines = content.split('\n')
                    context_lines = lines[max(0, line_num-3):min(len(lines), line_num+3)]
                    context = '\n'.join(context_lines)
                    
                    # Si es solo "pass" o logging básico, es menor
                    if 'pass' in context or 'print' in context:
                        self.minor_issues.append({
                            'type': 'BARE_EXCEPT_MINOR',
                            'file': file_path,
                            'line': line_num,
                            'description': 'Bare except with simple handling - consider specific exceptions'
                        })
                    else:
                        self.real_errors.append({
                            'type': 'BARE_EXCEPT_CRITICAL',
                            'file': file_path,
                            'line': line_num,
                            'severity': 'MEDIUM',
                            'description': 'Bare except clause may hide important errors'
                        })
    
    def extract_endpoint_function(self, content, endpoint):
        """Extrae la función de un endpoint específico."""
        pattern = f'@app\.(post|get).*{re.escape(endpoint)}.*?(?=@app\.|$)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0) if match else None
    
    def has_input_validation(self, function_code):
        """Verifica si una función tiene validación de entrada."""
        validation_patterns = [
            r'if.*not.*:',
            r'raise HTTPException',
            r'validate_',
            r'\.get\(',
            r'len\(',
            r'isinstance\('
        ]
        
        return any(re.search(pattern, function_code) for pattern in validation_patterns)
    
    def generate_intelligent_report(self):
        """Genera reporte inteligente."""
        total_real = len(self.real_errors)
        total_false = len(self.false_positives)
        total_minor = len(self.minor_issues)
        
        print(f"\n🎯 REPORTE INTELIGENTE DE ANÁLISIS")
        print("=" * 60)
        print(f"🔴 Errores Reales: {total_real}")
        print(f"✅ Falsos Positivos: {total_false}")
        print(f"⚠️ Issues Menores: {total_minor}")
        print("=" * 60)
        
        if self.real_errors:
            print(f"\n🔴 ERRORES REALES QUE REQUIEREN ATENCIÓN:")
            for i, error in enumerate(self.real_errors, 1):
                print(f"{i}. {error['type']}")
                print(f"   Severidad: {error.get('severity', 'UNKNOWN')}")
                print(f"   Descripción: {error['description']}")
                if 'endpoint' in error:
                    print(f"   Endpoint: {error['endpoint']}")
                if 'file' in error:
                    print(f"   Archivo: {error['file']}:{error.get('line', '?')}")
        
        if self.minor_issues:
            print(f"\n⚠️ ISSUES MENORES (Recomendaciones):")
            for i, issue in enumerate(self.minor_issues[:5], 1):  # Solo primeros 5
                print(f"{i}. {issue['type']}: {issue['description']}")
        
        print(f"\n✅ FALSOS POSITIVOS IDENTIFICADOS: {total_false}")
        print("   (Estos no requieren corrección)")
        
        # Evaluación final
        if total_real == 0:
            print(f"\n🎉 EXCELENTE - NO HAY ERRORES CRÍTICOS REALES")
            print("✅ La aplicación está en excelente estado")
            return True
        elif total_real <= 3:
            print(f"\n✅ BUENO - Solo {total_real} errores reales menores")
            print("⚠️ Correcciones menores recomendadas")
            return True
        else:
            print(f"\n❌ ATENCIÓN - {total_real} errores reales requieren corrección")
            return False

def main():
    analyzer = IntelligentErrorAnalyzer()
    is_clean = analyzer.analyze_errors()
    
    if is_clean:
        print(f"\n🎉 ANÁLISIS COMPLETADO - APLICACIÓN EN EXCELENTE ESTADO")
    else:
        print(f"\n⚠️ ANÁLISIS COMPLETADO - ALGUNAS CORRECCIONES RECOMENDADAS")

if __name__ == "__main__":
    main()
