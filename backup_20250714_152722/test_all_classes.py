#!/usr/bin/env python3
"""
PRUEBA EXHAUSTIVA DE TODAS LAS CLASES PYTHON
Prueba cada método de cada clase hasta el último detalle
"""

import sys
import os
import traceback
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, '.')

class ClassTester:
    def __init__(self):
        self.results = {}
        self.test_sql = """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE
        );
        
        SELECT * FROM users WHERE id = 1;
        INSERT INTO users (name, email) VALUES ('Test', 'test@example.com');
        """
    
    def test_method(self, obj, method_name, *args, **kwargs):
        """Probar un método específico de una clase"""
        try:
            method = getattr(obj, method_name)
            if callable(method):
                result = method(*args, **kwargs)
                return {
                    'success': True,
                    'result_type': type(result).__name__,
                    'result_length': len(str(result)) if result else 0,
                    'has_result': result is not None
                }
            else:
                return {'success': False, 'error': 'Not callable'}
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def test_error_detector(self):
        """Probar TODOS los métodos de ErrorDetector"""
        print("\n🔍 PROBANDO ErrorDetector")
        try:
            from sql_analyzer.core.error_detector import ErrorDetector
            detector = ErrorDetector()
            
            methods_to_test = [
                ('analyze_sql', self.test_sql),
                ('correct_sql', self.test_sql),
                ('detect_syntax_errors', self.test_sql),
                ('detect_semantic_errors', self.test_sql),
                ('generate_error_report', []),
            ]
            
            results = {}
            for method_name, arg in methods_to_test:
                if hasattr(detector, method_name):
                    results[method_name] = self.test_method(detector, method_name, arg)
                    status = "✅" if results[method_name]['success'] else "❌"
                    print(f"   {status} {method_name}")
                    if not results[method_name]['success']:
                        print(f"      Error: {results[method_name].get('error', 'Unknown')}")
            
            self.results['ErrorDetector'] = results
            return True
            
        except Exception as e:
            print(f"   ❌ Error importing ErrorDetector: {e}")
            return False
    
    def test_intelligent_commenter(self):
        """Probar TODOS los métodos de IntelligentCommenter"""
        print("\n💬 PROBANDO IntelligentCommenter")
        try:
            from sql_analyzer.core.intelligent_commenter import IntelligentCommenter
            commenter = IntelligentCommenter()
            
            methods_to_test = [
                ('add_comments', self.test_sql),
                ('analyze_sql_structure', self.test_sql),
                ('generate_table_comments', self.test_sql),
                ('generate_column_comments', self.test_sql),
            ]
            
            results = {}
            for method_name, arg in methods_to_test:
                if hasattr(commenter, method_name):
                    results[method_name] = self.test_method(commenter, method_name, arg)
                    status = "✅" if results[method_name]['success'] else "❌"
                    print(f"   {status} {method_name}")
                    if not results[method_name]['success']:
                        print(f"      Error: {results[method_name].get('error', 'Unknown')}")
            
            self.results['IntelligentCommenter'] = results
            return True
            
        except Exception as e:
            print(f"   ❌ Error importing IntelligentCommenter: {e}")
            return False
    
    def test_sample_data_generator(self):
        """Probar TODOS los métodos de SampleDataGenerator"""
        print("\n🎲 PROBANDO SampleDataGenerator")
        try:
            from sql_analyzer.core.sample_data_generator import SampleDataGenerator
            generator = SampleDataGenerator()
            
            methods_to_test = [
                ('generate_sample_data', self.test_sql, 5),
                ('analyze_schema', self.test_sql),
                ('generate_realistic_data', 'users', {'name': 'VARCHAR(100)', 'email': 'VARCHAR(100)'}, 3),
            ]
            
            results = {}
            for method_name, *args in methods_to_test:
                if hasattr(generator, method_name):
                    results[method_name] = self.test_method(generator, method_name, *args)
                    status = "✅" if results[method_name]['success'] else "❌"
                    print(f"   {status} {method_name}")
                    if not results[method_name]['success']:
                        print(f"      Error: {results[method_name].get('error', 'Unknown')}")
            
            self.results['SampleDataGenerator'] = results
            return True
            
        except Exception as e:
            print(f"   ❌ Error importing SampleDataGenerator: {e}")
            return False
    
    def test_sql_analyzer(self):
        """Probar TODOS los métodos de SQLAnalyzer"""
        print("\n🔬 PROBANDO SQLAnalyzer")
        try:
            from web_app.sql_analyzer.analyzer import SQLAnalyzer
            analyzer = SQLAnalyzer()
            
            # Crear archivo temporal para prueba
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
                f.write(self.test_sql)
                temp_file = f.name
            
            methods_to_test = [
                ('analyze_file', temp_file),
                ('_analyze_syntax', self.test_sql),
                ('_analyze_schema', self.test_sql),
                ('_analyze_security', self.test_sql),
                ('_analyze_performance', self.test_sql),
                ('_generate_statistics', self.test_sql),
            ]
            
            results = {}
            for method_name, arg in methods_to_test:
                if hasattr(analyzer, method_name):
                    results[method_name] = self.test_method(analyzer, method_name, arg)
                    status = "✅" if results[method_name]['success'] else "❌"
                    print(f"   {status} {method_name}")
                    if not results[method_name]['success']:
                        print(f"      Error: {results[method_name].get('error', 'Unknown')}")
            
            # Limpiar archivo temporal
            os.unlink(temp_file)
            
            self.results['SQLAnalyzer'] = results
            return True
            
        except Exception as e:
            print(f"   ❌ Error importing SQLAnalyzer: {e}")
            return False
    
    def test_format_generators(self):
        """Probar TODOS los generadores de formato"""
        print("\n📄 PROBANDO Format Generators")
        try:
            from sql_analyzer.core.format_generators import get_format_generator
            from sql_analyzer.core.format_generators.base_generator import GenerationContext
            from datetime import datetime
            
            # Crear contexto de prueba
            context = GenerationContext(
                analysis_result={'test': 'data'},
                original_filename='test.sql',
                analysis_timestamp=datetime.now(),
                user_options={},
                session_id='test-session'
            )
            
            formats_to_test = [
                'enhanced_sql',
                'html_report',
                'json_analysis',
                'csv_summary',
                'plain_text'
            ]
            
            results = {}
            for format_name in formats_to_test:
                try:
                    generator = get_format_generator(format_name)
                    result = self.test_method(generator, 'generate', context)
                    results[format_name] = result
                    status = "✅" if result['success'] else "❌"
                    print(f"   {status} {format_name}")
                    if not result['success']:
                        print(f"      Error: {result.get('error', 'Unknown')}")
                except Exception as e:
                    results[format_name] = {'success': False, 'error': str(e)}
                    print(f"   ❌ {format_name} - Error: {e}")
            
            self.results['FormatGenerators'] = results
            return True
            
        except Exception as e:
            print(f"   ❌ Error testing format generators: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas de clases"""
        print("🧪 INICIANDO PRUEBA EXHAUSTIVA DE TODAS LAS CLASES PYTHON")
        print("=" * 60)
        
        test_methods = [
            self.test_error_detector,
            self.test_intelligent_commenter,
            self.test_sample_data_generator,
            self.test_sql_analyzer,
            self.test_format_generators,
        ]
        
        successful_classes = 0
        total_classes = len(test_methods)
        
        for test_method in test_methods:
            if test_method():
                successful_classes += 1
        
        self.print_summary(successful_classes, total_classes)
    
    def print_summary(self, successful_classes, total_classes):
        """Imprimir resumen de todas las pruebas"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS DE CLASES")
        print("=" * 60)
        
        print(f"\n📈 RESUMEN GENERAL:")
        print(f"   Clases probadas: {total_classes}")
        print(f"   Clases exitosas: {successful_classes}")
        print(f"   Tasa de éxito: {(successful_classes/total_classes)*100:.1f}%")
        
        print(f"\n📋 MÉTODOS PROBADOS POR CLASE:")
        for class_name, methods in self.results.items():
            successful_methods = sum(1 for m in methods.values() if m.get('success', False))
            total_methods = len(methods)
            print(f"   {class_name}: {successful_methods}/{total_methods} métodos exitosos")
            
            for method_name, result in methods.items():
                status = "✅" if result.get('success', False) else "❌"
                print(f"      {status} {method_name}")

if __name__ == "__main__":
    tester = ClassTester()
    tester.run_all_tests()
