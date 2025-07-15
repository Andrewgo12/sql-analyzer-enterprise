#!/usr/bin/env python3
"""
Comprehensive Test Suite for SQL Analyzer Enterprise
Tests all functionality, performance, and edge cases
"""

import sys
import os
import requests
import json
import time
import threading
from datetime import datetime
import tempfile
import random
import string

class ComprehensiveTestSuite:
    def __init__(self):
        self.backend_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {details}")
        
        if status == "FAIL":
            self.failed_tests.append(result)
    
    def test_backend_health(self):
        """Test backend health and all components"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                health = response.json()
                if health['status'] in ['healthy', 'warning']:
                    self.log_test("Backend Health", "PASS", f"Status: {health['status']}")
                    return True
                else:
                    self.log_test("Backend Health", "FAIL", f"Unhealthy status: {health['status']}")
                    return False
            else:
                self.log_test("Backend Health", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", "FAIL", str(e))
            return False
    
    def test_all_database_engines(self):
        """Test all 22+ database engines"""
        try:
            response = requests.get(f"{self.backend_url}/api/databases/supported", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total_engines = data['total_engines']
                
                if total_engines >= 22:
                    self.log_test("Database Engines", "PASS", f"{total_engines} engines supported")
                    
                    # Test specific engines
                    test_engines = ['mysql', 'postgresql', 'mongodb', 'elasticsearch']
                    for engine in test_engines:
                        if any(e['engine'] == engine for e in data['engines']):
                            self.log_test(f"Engine {engine}", "PASS", "Engine available")
                        else:
                            self.log_test(f"Engine {engine}", "FAIL", "Engine missing")
                    
                    return True
                else:
                    self.log_test("Database Engines", "FAIL", f"Only {total_engines} engines (need 22+)")
                    return False
            else:
                self.log_test("Database Engines", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Engines", "FAIL", str(e))
            return False
    
    def test_all_export_formats(self):
        """Test all 38+ export formats"""
        try:
            response = requests.get(f"{self.backend_url}/api/export/formats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total_formats = data['total_formats']
                
                if total_formats >= 38:
                    self.log_test("Export Formats", "PASS", f"{total_formats} formats supported")
                    
                    # Test specific format categories
                    categories = data.get('categories', [])
                    expected_categories = ['document', 'spreadsheet', 'data', 'database']
                    for category in expected_categories:
                        if category in categories:
                            self.log_test(f"Format Category {category}", "PASS", "Category available")
                        else:
                            self.log_test(f"Format Category {category}", "FAIL", "Category missing")
                    
                    return True
                else:
                    self.log_test("Export Formats", "FAIL", f"Only {total_formats} formats (need 38+)")
                    return False
            else:
                self.log_test("Export Formats", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Export Formats", "FAIL", str(e))
            return False
    
    def test_sql_analysis_comprehensive(self):
        """Test comprehensive SQL analysis with various scenarios"""
        test_cases = [
            {
                'name': 'Simple SELECT',
                'sql': 'SELECT * FROM users WHERE id = 1;',
                'engine': 'mysql'
            },
            {
                'name': 'Complex JOIN',
                'sql': '''
                SELECT u.name, COUNT(o.id) as order_count
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                WHERE u.created_at > '2024-01-01'
                GROUP BY u.id
                HAVING order_count > 5;
                ''',
                'engine': 'postgresql'
            },
            {
                'name': 'Window Functions',
                'sql': '''
                SELECT 
                    product_id,
                    sales_amount,
                    ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY sales_amount DESC) as rank
                FROM sales
                WHERE sale_date >= DATEADD(month, -3, GETDATE());
                ''',
                'engine': 'sql_server'
            },
            {
                'name': 'CTE Query',
                'sql': '''
                WITH RECURSIVE category_tree AS (
                    SELECT id, name, parent_id, 0 as level
                    FROM categories
                    WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, c.parent_id, ct.level + 1
                    FROM categories c
                    JOIN category_tree ct ON c.parent_id = ct.id
                )
                SELECT * FROM category_tree ORDER BY level, name;
                ''',
                'engine': 'postgresql'
            }
        ]
        
        success_count = 0
        for test_case in test_cases:
            try:
                files = {'file': (f"{test_case['name'].lower().replace(' ', '_')}.sql", 
                                test_case['sql'], 'text/plain')}
                data = {
                    'database_engine': test_case['engine'],
                    'analysis_types': 'syntax,performance,security'
                }
                
                response = requests.post(f"{self.backend_url}/api/analyze", 
                                       files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test(f"SQL Analysis: {test_case['name']}", "PASS", 
                                f"Engine: {test_case['engine']}")
                    success_count += 1
                else:
                    self.log_test(f"SQL Analysis: {test_case['name']}", "FAIL", 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"SQL Analysis: {test_case['name']}", "FAIL", str(e))
        
        return success_count == len(test_cases)
    
    def test_export_functionality(self):
        """Test export functionality with multiple formats"""
        # Create sample analysis data
        sample_analysis = {
            'filename': 'comprehensive_test.sql',
            'timestamp': datetime.now().isoformat(),
            'file_size': 2048,
            'line_count': 50,
            'database_engine': 'mysql',
            'summary': {
                'total_errors': 2,
                'performance_score': 92,
                'security_score': 98
            },
            'analysis': {
                'errors': [
                    {'message': 'Missing index', 'line': 15, 'severity': 'medium'},
                    {'message': 'Unused variable', 'line': 23, 'severity': 'low'}
                ]
            }
        }
        
        test_formats = ['json', 'html', 'csv', 'xml', 'pdf']
        success_count = 0
        
        for fmt in test_formats:
            try:
                response = requests.post(f"{self.backend_url}/api/export/{fmt}",
                                       json=sample_analysis, timeout=20)
                
                if response.status_code == 200:
                    self.log_test(f"Export {fmt.upper()}", "PASS", 
                                f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                    success_count += 1
                else:
                    self.log_test(f"Export {fmt.upper()}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Export {fmt.upper()}", "FAIL", str(e))
        
        return success_count >= 3  # At least 3 formats should work
    
    def test_metrics_dashboard(self):
        """Test metrics dashboard functionality"""
        try:
            response = requests.get(f"{self.backend_url}/api/metrics/dashboard", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                
                # Check required metrics sections
                required_sections = ['overview', 'real_time', 'trends']
                for section in required_sections:
                    if section in metrics:
                        self.log_test(f"Metrics {section}", "PASS", "Section available")
                    else:
                        self.log_test(f"Metrics {section}", "FAIL", "Section missing")
                        return False
                
                self.log_test("Metrics Dashboard", "PASS", "All sections available")
                return True
            else:
                self.log_test("Metrics Dashboard", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Metrics Dashboard", "FAIL", str(e))
            return False
    
    def test_frontend_application(self):
        """Test frontend application"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for React app indicators
                if 'root' in content and 'script' in content:
                    self.log_test("Frontend App", "PASS", "React application serving")
                    
                    # Check for key components
                    if 'EnterpriseApp' in content or 'enterprise' in content.lower():
                        self.log_test("Frontend Enterprise", "PASS", "Enterprise components detected")
                    else:
                        self.log_test("Frontend Enterprise", "FAIL", "Enterprise components not detected")
                    
                    return True
                else:
                    self.log_test("Frontend App", "FAIL", "React app not detected")
                    return False
            else:
                self.log_test("Frontend App", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend App", "FAIL", str(e))
            return False
    
    def test_stress_performance(self):
        """Test performance with large SQL files"""
        # Generate large SQL content
        large_sql = "-- Large SQL Test File\n"
        for i in range(1000):
            large_sql += f"SELECT * FROM table_{i} WHERE id = {i};\n"
        
        try:
            files = {'file': ('large_test.sql', large_sql, 'text/plain')}
            data = {'database_engine': 'mysql', 'analysis_types': 'syntax'}
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/api/analyze", 
                                   files=files, data=data, timeout=60)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if response.status_code == 200 and processing_time < 30:
                self.log_test("Stress Test", "PASS", f"Processed in {processing_time:.2f}s")
                return True
            else:
                self.log_test("Stress Test", "FAIL", 
                            f"Time: {processing_time:.2f}s, Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Stress Test", "FAIL", str(e))
            return False
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        def make_request():
            try:
                response = requests.get(f"{self.backend_url}/api/health", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Make 10 concurrent requests
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        success_rate = sum(results) / len(results) * 100
        
        if success_rate >= 90:
            self.log_test("Concurrent Requests", "PASS", f"Success rate: {success_rate:.1f}%")
            return True
        else:
            self.log_test("Concurrent Requests", "FAIL", f"Success rate: {success_rate:.1f}%")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE TEST SUITE - SQL ANALYZER ENTERPRISE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Database Engines (22+)", self.test_all_database_engines),
            ("Export Formats (38+)", self.test_all_export_formats),
            ("SQL Analysis Comprehensive", self.test_sql_analysis_comprehensive),
            ("Export Functionality", self.test_export_functionality),
            ("Metrics Dashboard", self.test_metrics_dashboard),
            ("Frontend Application", self.test_frontend_application),
            ("Stress Performance", self.test_stress_performance),
            ("Concurrent Requests", self.test_concurrent_requests)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test crashed: {e}")
        
        # Final Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for failed in self.failed_tests:
                print(f"   - {failed['test']}: {failed['details']}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate >= 95:
            print("\n🎉 COMPREHENSIVE TESTING PASSED!")
            print("✨ Application is ready for production deployment!")
            return True
        else:
            print("\n⚠️ COMPREHENSIVE TESTING FAILED!")
            print("🔧 Please fix the issues before deployment.")
            return False

if __name__ == '__main__':
    suite = ComprehensiveTestSuite()
    success = suite.run_comprehensive_tests()
    sys.exit(0 if success else 1)
