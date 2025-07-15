#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Final System Validation
Comprehensive end-to-end validation of the complete system
"""

import requests
import time
import sys
import json
import tempfile
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import subprocess

class SystemValidator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.validation_results = []
        
    def log_result(self, category, test, success, message="", details=None):
        """Log validation result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.validation_results.append({
            'category': category,
            'test': test,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {category} - {test}")
        if message:
            print(f"   📝 {message}")
    
    def validate_backend_health(self):
        """Validate backend health and core functionality"""
        print("\n🏥 BACKEND HEALTH VALIDATION")
        print("=" * 60)
        
        try:
            # Health check
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Backend", "Health Check", True, 
                              f"Status: {health_data.get('status', 'unknown')}")
                
                # Validate health response structure
                required_fields = ['status', 'timestamp', 'version']
                missing_fields = [f for f in required_fields if f not in health_data]
                
                if not missing_fields:
                    self.log_result("Backend", "Health Response Structure", True)
                else:
                    self.log_result("Backend", "Health Response Structure", False,
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("Backend", "Health Check", False,
                              f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Backend", "Health Check", False, str(e))
            return False
        
        return True
    
    def validate_database_engines(self):
        """Validate database engine support"""
        print("\n🔧 DATABASE ENGINES VALIDATION")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{self.base_url}/api/databases/supported")
            if response.status_code == 200:
                data = response.json()
                engines = data.get('engines', [])
                categories = data.get('categories', [])
                
                # Validate engine count
                if len(engines) >= 20:
                    self.log_result("Database", "Engine Count", True,
                                  f"{len(engines)} engines available")
                else:
                    self.log_result("Database", "Engine Count", False,
                                  f"Only {len(engines)} engines (expected ≥20)")
                
                # Validate categories
                if len(categories) >= 10:
                    self.log_result("Database", "Category Count", True,
                                  f"{len(categories)} categories available")
                else:
                    self.log_result("Database", "Category Count", False,
                                  f"Only {len(categories)} categories (expected ≥10)")
                
                # Validate engine structure
                if engines and all('engine' in e and 'name' in e for e in engines):
                    self.log_result("Database", "Engine Structure", True)
                else:
                    self.log_result("Database", "Engine Structure", False,
                                  "Invalid engine structure")
                
                return True
            else:
                self.log_result("Database", "Engines API", False,
                              f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Database", "Engines API", False, str(e))
            return False
    
    def validate_sql_analysis(self):
        """Validate SQL analysis functionality"""
        print("\n🔍 SQL ANALYSIS VALIDATION")
        print("=" * 60)
        
        # Test queries of different complexities
        test_queries = [
            {
                'name': 'Simple Query',
                'sql': 'SELECT * FROM users WHERE id = 1;',
                'expected_time': 1.0
            },
            {
                'name': 'Complex Query',
                'sql': '''
                WITH monthly_sales AS (
                    SELECT 
                        DATE_TRUNC('month', order_date) as month,
                        SUM(total_amount) as monthly_total
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    WHERE o.status = 'completed'
                    GROUP BY DATE_TRUNC('month', order_date)
                )
                SELECT * FROM monthly_sales ORDER BY month;
                ''',
                'expected_time': 2.0
            }
        ]
        
        for query_test in test_queries:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                    temp_file.write(query_test['sql'])
                    temp_file_path = temp_file.name
                
                try:
                    start_time = time.time()
                    
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (f'{query_test["name"]}.sql', f, 'text/plain')}
                        data = {'database_engine': 'mysql'}
                        
                        response = self.session.post(f"{self.base_url}/api/analyze",
                                                   files=files, data=data, timeout=30)
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Validate response structure
                        required_fields = ['summary', 'analysis', 'metadata']
                        if all(field in result for field in required_fields):
                            self.log_result("Analysis", f"{query_test['name']} Structure", True)
                            
                            # Validate performance
                            analysis_time = result.get('metadata', {}).get('analysis_time', response_time)
                            performance_ok = analysis_time < query_test['expected_time']
                            
                            self.log_result("Analysis", f"{query_test['name']} Performance", 
                                          performance_ok, f"{analysis_time:.3f}s")
                            
                            # Validate summary data
                            summary = result.get('summary', {})
                            has_scores = all(key in summary for key in ['performance_score', 'security_score'])
                            
                            self.log_result("Analysis", f"{query_test['name']} Summary", has_scores)
                            
                        else:
                            missing = [f for f in required_fields if f not in result]
                            self.log_result("Analysis", f"{query_test['name']} Structure", False,
                                          f"Missing: {missing}")
                    else:
                        self.log_result("Analysis", f"{query_test['name']} Request", False,
                                      f"HTTP {response.status_code}")
                        
                finally:
                    os.unlink(temp_file_path)
                    
            except Exception as e:
                self.log_result("Analysis", f"{query_test['name']} Request", False, str(e))
    
    def validate_export_system(self):
        """Validate export functionality"""
        print("\n📤 EXPORT SYSTEM VALIDATION")
        print("=" * 60)
        
        try:
            # Get available formats
            response = self.session.get(f"{self.base_url}/api/export/formats")
            if response.status_code == 200:
                data = response.json()
                formats = data.get('formats', [])
                
                if len(formats) >= 10:
                    self.log_result("Export", "Format Count", True,
                                  f"{len(formats)} formats available")
                    
                    # Test export with sample data
                    sample_data = {
                        'summary': {'total_errors': 0, 'performance_score': 85},
                        'analysis': {'syntax_valid': True},
                        'metadata': {'analysis_time': 1.2}
                    }
                    
                    # Test JSON export
                    export_response = self.session.post(f"{self.base_url}/api/export/json",
                                                      json=sample_data, timeout=15)
                    
                    if export_response.status_code == 200:
                        self.log_result("Export", "JSON Export", True)
                    else:
                        self.log_result("Export", "JSON Export", False,
                                      f"HTTP {export_response.status_code}")
                else:
                    self.log_result("Export", "Format Count", False,
                                  f"Only {len(formats)} formats")
            else:
                self.log_result("Export", "Formats API", False,
                              f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Export", "Export System", False, str(e))
    
    def validate_metrics_system(self):
        """Validate metrics and monitoring"""
        print("\n📊 METRICS SYSTEM VALIDATION")
        print("=" * 60)
        
        try:
            # Test dashboard metrics
            response = self.session.get(f"{self.base_url}/api/metrics/dashboard")
            if response.status_code == 200:
                data = response.json()
                required_sections = ['overview', 'real_time', 'trends']
                
                if all(section in data for section in required_sections):
                    self.log_result("Metrics", "Dashboard Structure", True)
                else:
                    missing = [s for s in required_sections if s not in data]
                    self.log_result("Metrics", "Dashboard Structure", False,
                                  f"Missing: {missing}")
            else:
                self.log_result("Metrics", "Dashboard API", False,
                              f"HTTP {response.status_code}")
            
            # Test system metrics
            metrics_response = self.session.get(f"{self.base_url}/api/metrics")
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                
                # Check memory usage
                memory_usage = metrics_data.get('memory', {}).get('usage_percent', 0)
                memory_ok = memory_usage < 70
                
                self.log_result("Metrics", "Memory Usage", memory_ok,
                              f"{memory_usage}% (target: <70%)")
                
                self.log_result("Metrics", "System Metrics", True)
            else:
                self.log_result("Metrics", "System Metrics", False,
                              f"HTTP {metrics_response.status_code}")
                
        except Exception as e:
            self.log_result("Metrics", "Metrics System", False, str(e))
    
    def validate_performance_standards(self):
        """Validate enterprise performance standards"""
        print("\n⚡ PERFORMANCE STANDARDS VALIDATION")
        print("=" * 60)
        
        # Test multiple requests for performance consistency
        response_times = []
        
        for i in range(5):
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/api/health", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                    
            except Exception:
                pass
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            
            # Enterprise standards: <500ms average, <2s maximum
            avg_ok = avg_response < 0.5
            max_ok = max_response < 2.0
            
            self.log_result("Performance", "Average Response Time", avg_ok,
                          f"{avg_response:.3f}s (target: <0.5s)")
            
            self.log_result("Performance", "Maximum Response Time", max_ok,
                          f"{max_response:.3f}s (target: <2s)")
        else:
            self.log_result("Performance", "Response Time Test", False,
                          "No successful requests")
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 80)
        print("📊 FINAL SYSTEM VALIDATION REPORT")
        print("=" * 80)
        
        # Calculate statistics
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for r in self.validation_results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by category
        categories = {}
        for result in self.validation_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        # Print category results
        for category, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
            print(f"{status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        print(f"\n🎯 Overall System Validation: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Determine system status
        if success_rate >= 95:
            print("🎉 EXCELLENT: System is enterprise-ready for production deployment!")
            system_status = "PRODUCTION_READY"
        elif success_rate >= 85:
            print("✅ GOOD: System meets most enterprise standards with minor issues.")
            system_status = "MOSTLY_READY"
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: System has some issues that should be addressed.")
            system_status = "NEEDS_ATTENTION"
        else:
            print("❌ CRITICAL: System has significant issues requiring immediate attention.")
            system_status = "NOT_READY"
        
        # Save detailed report
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'system_status': system_status,
            'overall_success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'category_results': categories,
            'detailed_results': self.validation_results
        }
        
        with open('system_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: system_validation_report.json")
        
        return success_rate >= 85
    
    def run_complete_validation(self):
        """Run complete system validation"""
        print("🚀 SQL Analyzer Enterprise - Final System Validation")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Testing URL: {self.base_url}")
        
        # Run all validation tests
        validation_tests = [
            self.validate_backend_health,
            self.validate_database_engines,
            self.validate_sql_analysis,
            self.validate_export_system,
            self.validate_metrics_system,
            self.validate_performance_standards
        ]
        
        for test in validation_tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Validation test failed: {e}")
        
        # Generate final report
        return self.generate_validation_report()

if __name__ == "__main__":
    validator = SystemValidator()
    success = validator.run_complete_validation()
    sys.exit(0 if success else 1)
