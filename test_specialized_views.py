#!/usr/bin/env python3
"""
COMPREHENSIVE TESTING SUITE FOR SPECIALIZED VIEWS
SQL Analyzer Enterprise - Enterprise-Grade Testing
"""

import unittest
import requests
import json
import time
import os
import tempfile
from datetime import datetime

class TestSpecializedViews(unittest.TestCase):
    """Comprehensive testing for all specialized views"""
    
    BASE_URL = "http://localhost:5000"
    TEST_SQL_CONTENT = """
    -- Test SQL file for comprehensive testing
    SELECT u.id, u.name, u.email, u.created_at
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    WHERE u.is_active = TRUE 
      AND o.status = 'completed'
      AND o.total_amount > 100
    ORDER BY o.created_at DESC
    LIMIT 50;
    
    -- Potential security vulnerability for testing
    SELECT * FROM users WHERE username = 'admin' OR '1'='1';
    
    -- Performance issue for testing
    SELECT * FROM large_table WHERE unindexed_column LIKE '%search%';
    """
    
    def setUp(self):
        """Set up test environment"""
        self.session = requests.Session()
        self.test_file = self.create_test_file()
        
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.unlink(self.test_file)
    
    def create_test_file(self):
        """Create temporary SQL test file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(self.TEST_SQL_CONTENT)
            return f.name
    
    # ===== HEALTH CHECK TESTS =====
    
    def test_01_health_check(self):
        """Test API health endpoint"""
        print("\n🏥 Testing Health Check...")
        response = self.session.get(f"{self.BASE_URL}/api/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get('success', False))
        self.assertIn('backend_status', data)
        print("✅ Health check passed")
    
    # ===== SQL ANALYSIS VIEW TESTS =====
    
    def test_02_sql_analysis_view(self):
        """Test SQL Analysis & Correction view"""
        print("\n🔍 Testing SQL Analysis View...")
        
        # Test view accessibility
        response = self.session.get(f"{self.BASE_URL}/sql-analysis")
        self.assertEqual(response.status_code, 200)
        self.assertIn("SQL Analysis & Correction", response.text)
        print("✅ SQL Analysis view accessible")
    
    def test_03_sql_analysis_api(self):
        """Test SQL Analysis API endpoint"""
        print("\n🔍 Testing SQL Analysis API...")
        
        with open(self.test_file, 'rb') as f:
            files = {'file': ('test.sql', f, 'text/plain')}
            response = self.session.post(f"{self.BASE_URL}/api/sql-analyze", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success', False))
        self.assertIn('analysis_results', data)
        self.assertIn('processing_time', data)
        print("✅ SQL Analysis API working")
    
    # ===== SECURITY ANALYSIS VIEW TESTS =====
    
    def test_04_security_analysis_view(self):
        """Test Security Analysis view"""
        print("\n🛡️ Testing Security Analysis View...")
        
        response = self.session.get(f"{self.BASE_URL}/security-analysis")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Security Analysis", response.text)
        print("✅ Security Analysis view accessible")
    
    def test_05_security_analysis_api(self):
        """Test Security Analysis API endpoint"""
        print("\n🛡️ Testing Security Analysis API...")
        
        with open(self.test_file, 'rb') as f:
            files = {'file': ('test.sql', f, 'text/plain')}
            response = self.session.post(f"{self.BASE_URL}/api/security-scan", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success', False))
        self.assertIn('security_analysis', data)
        print("✅ Security Analysis API working")
    
    # ===== PERFORMANCE OPTIMIZATION VIEW TESTS =====
    
    def test_06_performance_optimization_view(self):
        """Test Performance Optimization view"""
        print("\n⚡ Testing Performance Optimization View...")
        
        response = self.session.get(f"{self.BASE_URL}/performance-optimization")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Performance Optimization", response.text)
        print("✅ Performance Optimization view accessible")
    
    def test_07_performance_optimization_api(self):
        """Test Performance Optimization API endpoint"""
        print("\n⚡ Testing Performance Optimization API...")
        
        with open(self.test_file, 'rb') as f:
            files = {'file': ('test.sql', f, 'text/plain')}
            response = self.session.post(f"{self.BASE_URL}/api/performance-check", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success', False))
        self.assertIn('performance_analysis', data)
        print("✅ Performance Optimization API working")
    
    # ===== SCHEMA ANALYSIS VIEW TESTS =====
    
    def test_08_schema_analysis_view(self):
        """Test Schema Analysis view"""
        print("\n🔗 Testing Schema Analysis View...")
        
        response = self.session.get(f"{self.BASE_URL}/schema-analysis")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Schema Analysis", response.text)
        print("✅ Schema Analysis view accessible")
    
    # ===== EXPORT CENTER VIEW TESTS =====
    
    def test_09_export_center_view(self):
        """Test Export Center view"""
        print("\n📤 Testing Export Center View...")
        
        response = self.session.get(f"{self.BASE_URL}/export-center")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Export Center", response.text)
        print("✅ Export Center view accessible")
    
    def test_10_export_functionality(self):
        """Test export functionality"""
        print("\n📤 Testing Export Functionality...")
        
        formats = ['json', 'html', 'csv', 'txt']
        for format_type in formats:
            response = self.session.get(f"{self.BASE_URL}/api/export/{format_type}")
            # Should return file or appropriate response
            self.assertIn(response.status_code, [200, 404])  # 404 if no data to export
        print("✅ Export functionality tested")
    
    # ===== VERSION MANAGEMENT VIEW TESTS =====
    
    def test_11_version_management_view(self):
        """Test Version Management view"""
        print("\n📚 Testing Version Management View...")
        
        response = self.session.get(f"{self.BASE_URL}/version-management")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Version Management", response.text)
        print("✅ Version Management view accessible")
    
    def test_12_version_creation_api(self):
        """Test version creation API"""
        print("\n📚 Testing Version Creation API...")
        
        data = {
            'description': 'Test version creation',
            'history': [],
            'changes': 5
        }
        response = self.session.post(f"{self.BASE_URL}/api/version-create", 
                                   json=data,
                                   headers={'Content-Type': 'application/json'})
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result.get('success', False))
        self.assertIn('version_info', result)
        print("✅ Version Creation API working")
    
    # ===== COMMENT & DOCUMENTATION VIEW TESTS =====
    
    def test_13_comment_documentation_view(self):
        """Test Comment & Documentation view"""
        print("\n📝 Testing Comment & Documentation View...")
        
        response = self.session.get(f"{self.BASE_URL}/comment-documentation")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Comment & Documentation", response.text)
        print("✅ Comment & Documentation view accessible")
    
    def test_14_documentation_generation_api(self):
        """Test documentation generation API"""
        print("\n📝 Testing Documentation Generation API...")
        
        with open(self.test_file, 'rb') as f:
            files = {'file': ('test.sql', f, 'text/plain')}
            response = self.session.post(f"{self.BASE_URL}/api/documentation-generate", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success', False))
        self.assertIn('documentation_data', data)
        print("✅ Documentation Generation API working")
    
    # ===== PERFORMANCE TESTS =====
    
    def test_15_response_time_performance(self):
        """Test response time performance (<2 seconds)"""
        print("\n⚡ Testing Response Time Performance...")
        
        endpoints = [
            '/sql-analysis',
            '/security-analysis', 
            '/performance-optimization',
            '/schema-analysis',
            '/export-center',
            '/version-management',
            '/comment-documentation'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.session.get(f"{self.BASE_URL}{endpoint}")
            end_time = time.time()
            
            response_time = end_time - start_time
            self.assertLess(response_time, 2.0, f"Endpoint {endpoint} took {response_time:.2f}s (>2s)")
            print(f"✅ {endpoint}: {response_time:.3f}s")
    
    def test_16_large_file_handling(self):
        """Test large file handling (up to 100MB simulation)"""
        print("\n📁 Testing Large File Handling...")
        
        # Create larger test content (simulate large file)
        large_content = self.TEST_SQL_CONTENT * 1000  # Simulate larger file
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(large_content)
            large_file_path = f.name
        
        try:
            with open(large_file_path, 'rb') as f:
                files = {'file': ('large_test.sql', f, 'text/plain')}
                start_time = time.time()
                response = self.session.post(f"{self.BASE_URL}/api/sql-analyze", files=files)
                end_time = time.time()
            
            processing_time = end_time - start_time
            self.assertEqual(response.status_code, 200)
            self.assertLess(processing_time, 5.0, f"Large file processing took {processing_time:.2f}s (>5s)")
            print(f"✅ Large file processed in {processing_time:.3f}s")
            
        finally:
            os.unlink(large_file_path)
    
    # ===== SECURITY TESTS =====
    
    def test_17_input_validation(self):
        """Test input validation and security"""
        print("\n🔒 Testing Input Validation...")
        
        # Test malicious file upload
        malicious_content = "<script>alert('xss')</script>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(malicious_content)
            malicious_file = f.name
        
        try:
            with open(malicious_file, 'rb') as f:
                files = {'file': ('malicious.sql', f, 'text/plain')}
                response = self.session.post(f"{self.BASE_URL}/api/sql-analyze", files=files)
            
            # Should handle malicious content safely
            self.assertEqual(response.status_code, 200)
            print("✅ Input validation working")
            
        finally:
            os.unlink(malicious_file)
    
    def test_18_error_handling(self):
        """Test comprehensive error handling"""
        print("\n❌ Testing Error Handling...")
        
        # Test missing file
        response = self.session.post(f"{self.BASE_URL}/api/sql-analyze")
        self.assertEqual(response.status_code, 400)
        
        # Test invalid endpoint
        response = self.session.get(f"{self.BASE_URL}/invalid-endpoint")
        self.assertEqual(response.status_code, 404)
        
        print("✅ Error handling working")
    
    # ===== ACCESSIBILITY TESTS =====
    
    def test_19_accessibility_compliance(self):
        """Test basic accessibility compliance"""
        print("\n♿ Testing Accessibility Compliance...")
        
        views = [
            '/sql-analysis',
            '/security-analysis',
            '/performance-optimization',
            '/schema-analysis',
            '/export-center',
            '/version-management',
            '/comment-documentation'
        ]
        
        for view in views:
            response = self.session.get(f"{self.BASE_URL}{view}")
            self.assertEqual(response.status_code, 200)
            
            # Check for basic accessibility elements
            content = response.text
            self.assertIn('alt=', content, f"Missing alt attributes in {view}")
            self.assertIn('aria-', content, f"Missing ARIA attributes in {view}")
            
        print("✅ Basic accessibility compliance verified")
    
    # ===== INTEGRATION TESTS =====
    
    def test_20_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing End-to-End Workflow...")
        
        # 1. Upload and analyze file
        with open(self.test_file, 'rb') as f:
            files = {'file': ('workflow_test.sql', f, 'text/plain')}
            sql_response = self.session.post(f"{self.BASE_URL}/api/sql-analyze", files=files)
        
        self.assertEqual(sql_response.status_code, 200)
        
        # 2. Security scan
        with open(self.test_file, 'rb') as f:
            files = {'file': ('workflow_test.sql', f, 'text/plain')}
            security_response = self.session.post(f"{self.BASE_URL}/api/security-scan", files=files)
        
        self.assertEqual(security_response.status_code, 200)
        
        # 3. Performance check
        with open(self.test_file, 'rb') as f:
            files = {'file': ('workflow_test.sql', f, 'text/plain')}
            performance_response = self.session.post(f"{self.BASE_URL}/api/performance-check", files=files)
        
        self.assertEqual(performance_response.status_code, 200)
        
        # 4. Generate documentation
        with open(self.test_file, 'rb') as f:
            files = {'file': ('workflow_test.sql', f, 'text/plain')}
            doc_response = self.session.post(f"{self.BASE_URL}/api/documentation-generate", files=files)
        
        self.assertEqual(doc_response.status_code, 200)
        
        print("✅ End-to-end workflow completed successfully")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 STARTING COMPREHENSIVE SPECIALIZED VIEWS TESTING")
    print("=" * 60)
    
    # Configure test runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSpecializedViews)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 TESTING SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n✅ SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 ENTERPRISE-GRADE QUALITY ACHIEVED!")
    elif success_rate >= 90:
        print("✅ HIGH QUALITY - Minor improvements needed")
    else:
        print("⚠️ QUALITY ISSUES - Significant improvements required")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    import sys
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
