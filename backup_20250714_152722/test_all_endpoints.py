#!/usr/bin/env python3
"""
PRUEBA EXHAUSTIVA DE TODOS LOS ENDPOINTS
Prueba cada endpoint del servidor para verificar funcionalidad completa
"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8081"
TEST_SQL_FILE = "web_app/test_sample.sql"

class EndpointTester:
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        
    def test_endpoint(self, method, endpoint, **kwargs):
        """Probar un endpoint específico"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **kwargs)
            elif method.upper() == 'PUT':
                response = self.session.put(url, **kwargs)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, **kwargs)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'response_size': len(response.content),
                'content_type': response.headers.get('content-type', ''),
                'response_time': response.elapsed.total_seconds()
            }
            
            # Try to parse JSON response
            try:
                result['json_response'] = response.json()
            except:
                result['text_response'] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                
            return result
        except Exception as e:
            return {
                'status_code': 0,
                'success': False,
                'error': str(e),
                'response_time': 0
            }
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas de endpoints"""
        
        print("🚀 INICIANDO PRUEBA EXHAUSTIVA DE TODOS LOS ENDPOINTS")
        print("=" * 60)
        
        # 1. Endpoints básicos
        print("\n📍 1. ENDPOINTS BÁSICOS")
        self.results['root'] = self.test_endpoint('GET', '/')
        self.results['analyze'] = self.test_endpoint('GET', '/analyze')
        self.results['dashboard'] = self.test_endpoint('GET', '/dashboard')
        
        # 2. Endpoints de salud y sistema
        print("\n📍 2. ENDPOINTS DE SALUD Y SISTEMA")
        self.results['health'] = self.test_endpoint('GET', '/api/health')
        self.results['system_info'] = self.test_endpoint('GET', '/api/system/info')
        
        # 3. Endpoints de autenticación
        print("\n📍 3. ENDPOINTS DE AUTENTICACIÓN")
        self.results['create_session'] = self.test_endpoint('POST', '/api/auth/session')
        self.results['validate_session'] = self.test_endpoint('GET', '/api/auth/validate')
        
        # 4. Endpoints de WebSocket
        print("\n📍 4. ENDPOINTS DE WEBSOCKET")
        self.results['websocket_status'] = self.test_endpoint('GET', '/api/websocket/status')
        self.results['events_poll'] = self.test_endpoint('GET', '/api/events/poll')
        
        # 5. Endpoints de formatos
        print("\n📍 5. ENDPOINTS DE FORMATOS")
        self.results['available_formats'] = self.test_endpoint('GET', '/api/available-formats')
        self.results['enterprise_features'] = self.test_endpoint('GET', '/api/enterprise-features')
        
        # 6. Endpoints de configuración
        print("\n📍 6. ENDPOINTS DE CONFIGURACIÓN")
        self.results['config_formats'] = self.test_endpoint('GET', '/api/config/formats')
        self.results['config_system'] = self.test_endpoint('GET', '/api/config/system')
        
        # 7. Endpoints de estadísticas
        print("\n📍 7. ENDPOINTS DE ESTADÍSTICAS")
        self.results['stats_usage'] = self.test_endpoint('GET', '/api/stats/usage')
        self.results['stats_performance'] = self.test_endpoint('GET', '/api/stats/performance')
        self.results['stats_quality'] = self.test_endpoint('GET', '/api/stats/quality-trends')
        
        # 8. Endpoints de análisis (requieren archivo)
        print("\n📍 8. ENDPOINTS DE ANÁLISIS CON ARCHIVO")
        if os.path.exists(TEST_SQL_FILE):
            with open(TEST_SQL_FILE, 'rb') as f:
                files = {'file': f}
                
                # Análisis simple
                self.results['analyze_simple'] = self.test_endpoint('POST', '/api/analyze/simple', files=files)
                
                # Auto-fix
                f.seek(0)
                self.results['auto_fix'] = self.test_endpoint('POST', '/api/auto-fix', files=files)
                
                # Add comments
                f.seek(0)
                self.results['add_comments'] = self.test_endpoint('POST', '/api/add-comments', files=files)
                
                # Generate sample data
                f.seek(0)
                data = {'records_per_table': '5', 'realistic_data': 'true'}
                self.results['generate_sample'] = self.test_endpoint('POST', '/api/generate-sample-data', 
                                                                   files=files, data=data)
        
        # 9. Endpoints de análisis avanzado
        print("\n📍 9. ENDPOINTS DE ANÁLISIS AVANZADO")
        if os.path.exists(TEST_SQL_FILE):
            with open(TEST_SQL_FILE, 'rb') as f:
                files = {'file': f}
                data = {'analysis_types': 'syntax,schema', 'include_recommendations': 'true'}
                self.results['advanced_analysis'] = self.test_endpoint('POST', '/api/analysis/advanced', 
                                                                     files=files, data=data)
        
        # 10. Endpoints de esquema
        print("\n📍 10. ENDPOINTS DE ESQUEMA")
        data = {'sql_content': 'CREATE TABLE test (id INT PRIMARY KEY);'}
        self.results['schema_analyze'] = self.test_endpoint('POST', '/api/schema/analyze', data=data)
        
        self.print_results()
    
    def print_results(self):
        """Imprimir resultados de todas las pruebas"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE PRUEBAS EXHAUSTIVAS")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r.get('success', False))
        
        print(f"\n📈 RESUMEN GENERAL:")
        print(f"   Total de endpoints probados: {total_tests}")
        print(f"   Endpoints exitosos: {successful_tests}")
        print(f"   Endpoints fallidos: {total_tests - successful_tests}")
        print(f"   Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 RESULTADOS DETALLADOS:")
        for endpoint, result in self.results.items():
            status = "✅" if result.get('success', False) else "❌"
            status_code = result.get('status_code', 0)
            response_time = result.get('response_time', 0)
            
            print(f"   {status} {endpoint:25} | Status: {status_code:3} | Time: {response_time:.3f}s")
            
            if not result.get('success', False) and 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Mostrar algunos ejemplos de respuestas exitosas
        print(f"\n🔍 EJEMPLOS DE RESPUESTAS EXITOSAS:")
        for endpoint, result in list(self.results.items())[:3]:
            if result.get('success', False) and 'json_response' in result:
                print(f"\n   {endpoint}:")
                response = result['json_response']
                if isinstance(response, dict):
                    for key, value in list(response.items())[:3]:
                        print(f"      {key}: {str(value)[:50]}...")

if __name__ == "__main__":
    tester = EndpointTester()
    tester.run_all_tests()
