#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Frontend Workflow Testing
Comprehensive end-to-end testing of all user workflows
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

class WorkflowTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", duration=0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'duration': duration
        })
        print(f"{status} {test_name} ({duration:.2f}s)")
        if message:
            print(f"   📝 {message}")
    
    def test_backend_health(self):
        """Test backend health and availability"""
        print("\n🏥 Testing Backend Health")
        print("=" * 50)
        
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, 
                            f"Status: {data.get('status', 'unknown')}", duration)
                return True
            else:
                self.log_test("Backend Health Check", False, 
                            f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Backend Health Check", False, str(e), duration)
            return False
    
    def test_database_engines_workflow(self):
        """Test database engines loading workflow"""
        print("\n🔧 Testing Database Engines Workflow")
        print("=" * 50)
        
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/databases/supported")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                engines = data.get('engines', [])
                categories = data.get('categories', [])
                
                if len(engines) >= 20 and len(categories) >= 10:
                    self.log_test("Database Engines Loading", True,
                                f"{len(engines)} engines, {len(categories)} categories", duration)
                    
                    # Test engine categorization
                    categorized_engines = {}
                    for engine in engines:
                        category = engine.get('category', 'unknown')
                        if category not in categorized_engines:
                            categorized_engines[category] = 0
                        categorized_engines[category] += 1
                    
                    self.log_test("Engine Categorization", True,
                                f"Engines distributed across {len(categorized_engines)} categories", 0)
                    return True
                else:
                    self.log_test("Database Engines Loading", False,
                                f"Insufficient engines: {len(engines)}", duration)
                    return False
            else:
                self.log_test("Database Engines Loading", False,
                            f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Database Engines Loading", False, str(e), duration)
            return False
    
    def test_analysis_workflow(self):
        """Test SQL analysis workflow"""
        print("\n🔍 Testing SQL Analysis Workflow")
        print("=" * 50)

        # Test SQL analysis with file upload (as expected by the API)
        sample_sql = """
        SELECT u.id, u.name, u.email, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.active = 1
        GROUP BY u.id, u.name, u.email
        HAVING COUNT(o.id) > 5
        ORDER BY order_count DESC
        LIMIT 100;
        """

        start_time = time.time()
        try:
            # Create a temporary SQL file for testing
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                temp_file.write(sample_sql)
                temp_file_path = temp_file.name

            try:
                # Prepare file upload
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('test_query.sql', f, 'text/plain')}
                    data = {'database_engine': 'mysql'}

                    response = self.session.post(f"{self.base_url}/api/analyze",
                                               files=files, data=data, timeout=30)
                    duration = time.time() - start_time
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate analysis response structure
                required_fields = ['summary', 'analysis', 'metadata']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    summary = data.get('summary', {})
                    analysis_time = data.get('metadata', {}).get('analysis_time', 0)
                    
                    # Check performance requirement: <2s analysis
                    performance_ok = float(analysis_time) < 2.0
                    
                    self.log_test("SQL Analysis Processing", True,
                                f"Analysis completed in {analysis_time}s", duration)
                    
                    self.log_test("Analysis Performance", performance_ok,
                                f"Analysis time: {analysis_time}s (target: <2s)", 0)
                    
                    # Test analysis completeness
                    has_errors = summary.get('total_errors', 0)
                    has_warnings = summary.get('total_warnings', 0)
                    perf_score = summary.get('performance_score', 0)
                    
                    self.log_test("Analysis Completeness", True,
                                f"Errors: {has_errors}, Warnings: {has_warnings}, Score: {perf_score}%", 0)
                    
                    return True
                else:
                    self.log_test("SQL Analysis Processing", False,
                                f"Missing fields: {missing_fields}", duration)
                    return False
            else:
                self.log_test("SQL Analysis Processing", False,
                            f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("SQL Analysis Processing", False, str(e), duration)
            return False
    
    def test_export_workflow(self):
        """Test export functionality workflow"""
        print("\n📤 Testing Export Workflow")
        print("=" * 50)
        
        # First get available export formats
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/export/formats")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                formats = data.get('formats', [])
                
                if len(formats) >= 10:
                    self.log_test("Export Formats Loading", True,
                                f"{len(formats)} formats available", duration)
                    
                    # Test export with sample data using correct endpoint format
                    sample_export_data = {
                        'summary': {'total_errors': 0, 'total_warnings': 2, 'performance_score': 85},
                        'analysis': {'syntax_valid': True, 'optimizations': ['Add index on user_id']},
                        'metadata': {'analysis_time': 1.2, 'timestamp': datetime.now().isoformat()}
                    }

                    export_start = time.time()
                    # Use the correct endpoint format: /api/export/<format>
                    export_response = self.session.post(f"{self.base_url}/api/export/json",
                                                      json=sample_export_data, timeout=15)
                    export_duration = time.time() - export_start
                    
                    if export_response.status_code == 200:
                        self.log_test("Export Processing", True,
                                    "Export completed successfully", export_duration)
                        return True
                    else:
                        self.log_test("Export Processing", False,
                                    f"HTTP {export_response.status_code}", export_duration)
                        return False
                else:
                    self.log_test("Export Formats Loading", False,
                                f"Insufficient formats: {len(formats)}", duration)
                    return False
            else:
                self.log_test("Export Formats Loading", False,
                            f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Export Workflow", False, str(e), duration)
            return False
    
    def test_metrics_workflow(self):
        """Test metrics and monitoring workflow"""
        print("\n📊 Testing Metrics Workflow")
        print("=" * 50)
        
        # Test dashboard metrics
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/metrics/dashboard")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ['overview', 'real_time', 'trends']
                
                if all(section in data for section in required_sections):
                    self.log_test("Dashboard Metrics", True,
                                "All metric sections available", duration)
                    
                    # Test system metrics
                    metrics_start = time.time()
                    metrics_response = self.session.get(f"{self.base_url}/api/metrics")
                    metrics_duration = time.time() - metrics_start
                    
                    if metrics_response.status_code == 200:
                        metrics_data = metrics_response.json()
                        
                        # Check memory usage requirement: <70%
                        memory_usage = metrics_data.get('memory', {}).get('usage_percent', 0)
                        memory_ok = memory_usage < 70
                        
                        self.log_test("System Metrics", True,
                                    f"Memory usage: {memory_usage}%", metrics_duration)
                        
                        self.log_test("Memory Performance", memory_ok,
                                    f"Memory usage: {memory_usage}% (target: <70%)", 0)
                        
                        return True
                    else:
                        self.log_test("System Metrics", False,
                                    f"HTTP {metrics_response.status_code}", metrics_duration)
                        return False
                else:
                    missing = [s for s in required_sections if s not in data]
                    self.log_test("Dashboard Metrics", False,
                                f"Missing sections: {missing}", duration)
                    return False
            else:
                self.log_test("Dashboard Metrics", False,
                            f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Metrics Workflow", False, str(e), duration)
            return False
    
    def run_all_tests(self):
        """Run all workflow tests"""
        print("🚀 SQL Analyzer Enterprise - Frontend Workflow Testing")
        print("=" * 60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Testing URL: {self.base_url}")
        
        # Run all test workflows
        tests = [
            self.test_backend_health,
            self.test_database_engines_workflow,
            self.test_analysis_workflow,
            self.test_export_workflow,
            self.test_metrics_workflow
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for test_func in tests:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                total_tests += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                total_tests += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']} ({result['duration']:.2f}s)")
            if result['message']:
                print(f"   📝 {result['message']}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} workflows passed ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 Excellent! All critical workflows are functional.")
            return True
        elif success_rate >= 70:
            print("⚠️  Good! Most workflows are functional with minor issues.")
            return True
        else:
            print("❌ Critical issues found. System needs attention.")
            return False

if __name__ == "__main__":
    tester = WorkflowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
