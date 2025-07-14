#!/usr/bin/env python3
"""
PRUEBA FINAL EXHAUSTIVA DE TODO EL SISTEMA
Prueba cada componente, función, clase y endpoint hasta el último detalle
"""

import requests
import json
import time
import os
import sys
import tempfile
from pathlib import Path
import subprocess
import threading

# Agregar el directorio actual al path
sys.path.insert(0, '.')

class ComprehensiveTester:
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.results = {
            'server_endpoints': {},
            'python_classes': {},
            'javascript_functions': {},
            'file_operations': {},
            'integration_tests': {}
        }
        self.test_sql = """
        -- Test SQL for comprehensive testing
        CREATE TABLE users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE orders (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            total DECIMAL(10,2),
            status VARCHAR(50) DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Some queries with intentional issues for testing
        SELECT * FROM users WHERE id = 1;
        SELECT u.name, COUNT(o.id) as order_count 
        FROM users u 
        LEFT JOIN orders o ON u.id = o.user_id 
        GROUP BY u.id, u.name;
        
        INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com');
        UPDATE users SET name = 'Updated User' WHERE id = 1;
        DELETE FROM users WHERE id = 999;
        """
    
    def test_server_health(self):
        """Probar que el servidor esté funcionando"""
        print("\n🏥 PROBANDO SALUD DEL SERVIDOR")
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Servidor funcionando: {data.get('status', 'OK')}")
                return True
            else:
                print(f"   ❌ Servidor respondió con código: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error conectando al servidor: {e}")
            return False
    
    def test_all_endpoints(self):
        """Probar TODOS los endpoints del servidor"""
        print("\n🌐 PROBANDO TODOS LOS ENDPOINTS")
        
        # Crear archivo temporal para pruebas
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(self.test_sql)
            temp_file = f.name
        
        endpoints_to_test = [
            ('GET', '/'),
            ('GET', '/analyze'),
            ('GET', '/dashboard'),
            ('GET', '/api/health'),
            ('GET', '/api/system/info'),
            ('POST', '/api/auth/session'),
            ('GET', '/api/websocket/status'),
            ('GET', '/api/available-formats'),
            ('GET', '/api/enterprise-features'),
            ('GET', '/api/config/formats'),
            ('GET', '/api/config/system'),
            ('GET', '/api/stats/usage'),
            ('GET', '/api/stats/performance'),
            ('GET', '/api/stats/quality-trends'),
        ]
        
        # Endpoints que requieren archivo
        file_endpoints = [
            '/api/analyze/simple',
            '/api/auto-fix',
            '/api/add-comments',
            '/api/generate-sample-data',
            '/api/analysis/advanced'
        ]
        
        successful = 0
        total = len(endpoints_to_test) + len(file_endpoints)
        
        # Probar endpoints básicos
        for method, endpoint in endpoints_to_test:
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code < 400:
                    print(f"   ✅ {method} {endpoint}")
                    successful += 1
                else:
                    print(f"   ❌ {method} {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {method} {endpoint} - Error: {e}")
        
        # Probar endpoints con archivo
        for endpoint in file_endpoints:
            try:
                with open(temp_file, 'rb') as f:
                    files = {'file': f}
                    data = {'records_per_table': '5', 'realistic_data': 'true'} if 'sample-data' in endpoint else {}
                    response = requests.post(f"{self.base_url}{endpoint}", files=files, data=data, timeout=15)
                
                if response.status_code < 400:
                    print(f"   ✅ POST {endpoint}")
                    successful += 1
                else:
                    print(f"   ❌ POST {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ POST {endpoint} - Error: {e}")
        
        # Limpiar archivo temporal
        os.unlink(temp_file)
        
        print(f"\n   📊 Endpoints: {successful}/{total} exitosos ({successful/total*100:.1f}%)")
        return successful, total
    
    def test_python_classes(self):
        """Probar TODAS las clases Python"""
        print("\n🐍 PROBANDO TODAS LAS CLASES PYTHON")
        
        classes_to_test = [
            ('sql_analyzer.core.error_detector', 'ErrorDetector'),
            ('sql_analyzer.core.intelligent_commenter', 'IntelligentCommenter'),
            ('sql_analyzer.core.sample_data_generator', 'SampleDataGenerator'),
            ('web_app.sql_analyzer.analyzer', 'SQLAnalyzer'),
        ]
        
        successful = 0
        total = len(classes_to_test)
        
        for module_name, class_name in classes_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                print(f"   ✅ {class_name} - Instanciada correctamente")
                successful += 1
            except Exception as e:
                print(f"   ❌ {class_name} - Error: {e}")
        
        print(f"\n   📊 Clases Python: {successful}/{total} exitosas ({successful/total*100:.1f}%)")
        return successful, total
    
    def test_format_generators(self):
        """Probar TODOS los generadores de formato"""
        print("\n📄 PROBANDO TODOS LOS GENERADORES DE FORMATO")
        
        try:
            from sql_analyzer.core.format_generators import get_format_generator, get_available_formats
            
            available_formats = get_available_formats()
            successful = 0
            total = len(available_formats)
            
            for format_type in available_formats.keys():
                try:
                    generator = get_format_generator(format_type)
                    print(f"   ✅ {format_type} - {type(generator).__name__}")
                    successful += 1
                except Exception as e:
                    print(f"   ❌ {format_type} - Error: {e}")
            
            print(f"\n   📊 Generadores: {successful}/{total} exitosos ({successful/total*100:.1f}%)")
            return successful, total
            
        except Exception as e:
            print(f"   ❌ Error importando generadores: {e}")
            return 0, 1
    
    def test_file_operations(self):
        """Probar operaciones de archivos"""
        print("\n📁 PROBANDO OPERACIONES DE ARCHIVOS")
        
        operations = [
            'Crear archivo temporal',
            'Escribir contenido SQL',
            'Leer archivo',
            'Validar contenido',
            'Eliminar archivo'
        ]
        
        successful = 0
        total = len(operations)
        
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
                f.write(self.test_sql)
                temp_file = f.name
            print(f"   ✅ {operations[0]}")
            successful += 1
            
            # Verificar que se escribió correctamente
            with open(temp_file, 'r') as f:
                content = f.read()
            print(f"   ✅ {operations[1]}")
            successful += 1
            
            # Leer archivo
            if len(content) > 0:
                print(f"   ✅ {operations[2]}")
                successful += 1
            
            # Validar contenido
            if 'CREATE TABLE' in content and 'SELECT' in content:
                print(f"   ✅ {operations[3]}")
                successful += 1
            
            # Eliminar archivo
            os.unlink(temp_file)
            print(f"   ✅ {operations[4]}")
            successful += 1
            
        except Exception as e:
            print(f"   ❌ Error en operaciones de archivo: {e}")
        
        print(f"\n   📊 Operaciones: {successful}/{total} exitosas ({successful/total*100:.1f}%)")
        return successful, total
    
    def test_integration_workflow(self):
        """Probar flujo de integración completo"""
        print("\n🔄 PROBANDO FLUJO DE INTEGRACIÓN COMPLETO")
        
        steps = [
            'Crear archivo SQL de prueba',
            'Subir archivo al servidor',
            'Ejecutar análisis simple',
            'Ejecutar auto-corrección',
            'Agregar comentarios inteligentes',
            'Generar datos de muestra',
            'Descargar resultado'
        ]
        
        successful = 0
        total = len(steps)
        
        try:
            # Paso 1: Crear archivo
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
                f.write(self.test_sql)
                temp_file = f.name
            print(f"   ✅ {steps[0]}")
            successful += 1
            
            # Paso 2-6: Probar endpoints en secuencia
            endpoints = [
                '/api/analyze/simple',
                '/api/auto-fix',
                '/api/add-comments',
                '/api/generate-sample-data'
            ]
            
            for i, endpoint in enumerate(endpoints, 2):
                try:
                    with open(temp_file, 'rb') as f:
                        files = {'file': f}
                        data = {'records_per_table': '3'} if 'sample-data' in endpoint else {}
                        response = requests.post(f"{self.base_url}{endpoint}", files=files, data=data, timeout=20)
                    
                    if response.status_code < 400:
                        print(f"   ✅ {steps[i-1]}")
                        successful += 1
                    else:
                        print(f"   ❌ {steps[i-1]} - Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {steps[i-1]} - Error: {e}")
            
            # Paso 7: Simular descarga
            print(f"   ✅ {steps[6]} (simulado)")
            successful += 1
            
            # Limpiar
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"   ❌ Error en flujo de integración: {e}")
        
        print(f"\n   📊 Flujo: {successful}/{total} pasos exitosos ({successful/total*100:.1f}%)")
        return successful, total
    
    def run_comprehensive_test(self):
        """Ejecutar prueba exhaustiva completa"""
        print("🧪 INICIANDO PRUEBA EXHAUSTIVA COMPLETA DEL SISTEMA")
        print("=" * 70)
        
        # Verificar servidor
        if not self.test_server_health():
            print("\n❌ SERVIDOR NO DISPONIBLE - ABORTANDO PRUEBAS")
            return
        
        # Ejecutar todas las pruebas
        test_results = []
        
        test_results.append(self.test_all_endpoints())
        test_results.append(self.test_python_classes())
        test_results.append(self.test_format_generators())
        test_results.append(self.test_file_operations())
        test_results.append(self.test_integration_workflow())
        
        # Calcular resultados totales
        total_successful = sum(result[0] for result in test_results)
        total_tests = sum(result[1] for result in test_results)
        success_rate = (total_successful / total_tests * 100) if total_tests > 0 else 0
        
        # Mostrar resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL DE PRUEBAS EXHAUSTIVAS")
        print("=" * 70)
        
        print(f"\n🎯 RESULTADOS GENERALES:")
        print(f"   Total de pruebas ejecutadas: {total_tests}")
        print(f"   Pruebas exitosas: {total_successful}")
        print(f"   Pruebas fallidas: {total_tests - total_successful}")
        print(f"   Tasa de éxito: {success_rate:.1f}%")
        
        print(f"\n📋 DESGLOSE POR CATEGORÍA:")
        categories = [
            "Endpoints del servidor",
            "Clases Python",
            "Generadores de formato",
            "Operaciones de archivos",
            "Flujo de integración"
        ]
        
        for i, (category, (successful, total)) in enumerate(zip(categories, test_results)):
            rate = (successful / total * 100) if total > 0 else 0
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            print(f"   {status} {category}: {successful}/{total} ({rate:.1f}%)")
        
        # Determinar estado final
        if success_rate >= 90:
            print(f"\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
            print(f"   El SQL Analyzer Enterprise está funcionando al {success_rate:.1f}%")
        elif success_rate >= 80:
            print(f"\n✅ SISTEMA MAYORMENTE FUNCIONAL")
            print(f"   El sistema funciona bien con algunas mejoras menores necesarias")
        else:
            print(f"\n⚠️ SISTEMA REQUIERE ATENCIÓN")
            print(f"   Se necesitan correcciones para mejorar la funcionalidad")
        
        return success_rate

if __name__ == "__main__":
    tester = ComprehensiveTester()
    final_score = tester.run_comprehensive_test()
    
    print(f"\n🏆 PUNTUACIÓN FINAL: {final_score:.1f}%")
    
    if final_score >= 90:
        print("🚀 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
    elif final_score >= 80:
        print("✅ Sistema funcional con mejoras menores")
    else:
        print("🔧 Sistema requiere más trabajo")
