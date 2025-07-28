#!/usr/bin/env python3
"""
ENTERPRISE SYSTEM TESTING
Comprehensive test suite for the complete enterprise system
"""

import unittest
import tempfile
import os
import json
import time
from io import BytesIO
import sys

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.analysis_models import AnalysisResult, DatabaseType, ErrorSeverity
from app.models.data_access import DatabaseManager, AnalysisRepository
from app.services.analysis_service import AnalysisService
from app.services.business_logic import QualityAssessmentEngine
from app.controllers.analysis_controller import AnalysisController
from app.utils.validation import EnterpriseValidator
from app.utils.helpers import cache, FileHelper, ValidationHelper

class TestEnterpriseSystem(unittest.TestCase):
    """Comprehensive enterprise system test suite"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_sql = """
-- Test SQL file for comprehensive analysis
SELECT u.id, u.name, u.email, u.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.is_active = TRUE 
  AND o.status = 'completed'
  AND o.total_amount > 100
ORDER BY o.created_at DESC
LIMIT 50;

-- Potential security vulnerability
SELECT * FROM users WHERE username = 'admin' OR '1'='1';

-- Performance issue
SELECT * FROM large_table WHERE unindexed_column LIKE '%search%';

-- Missing WHERE clause (dangerous)
UPDATE users SET last_login = NOW();

-- Create table example
CREATE TABLE test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        
        # Initialize components
        self.db_manager = DatabaseManager(':memory:')  # In-memory database for testing
        self.repository = AnalysisRepository(self.db_manager)
        self.analysis_service = AnalysisService()
        self.quality_engine = QualityAssessmentEngine()
        self.controller = AnalysisController()
        self.validator = EnterpriseValidator()
    
    def tearDown(self):
        """Clean up test environment"""
        self.db_manager.close_all_connections()
        cache.clear_all()
    
    def test_01_database_manager_initialization(self):
        """Test database manager initialization"""
        print("\n🗄️ Testing Database Manager...")
        
        # Test connection
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Should have all required tables
            table_names = [table[0] for table in tables]
            required_tables = [
                'analysis_results', 'file_info', 'sql_errors',
                'security_vulnerabilities', 'performance_issues',
                'table_info', 'export_history'
            ]
            
            for table in required_tables:
                self.assertIn(table, table_names, f"Table {table} should exist")
        
        print("✅ Database manager initialized correctly")
    
    def test_02_enterprise_validator_file_validation(self):
        """Test enterprise validator file validation"""
        print("\n🔍 Testing Enterprise Validator...")
        
        # Create test file
        test_file = BytesIO(self.test_sql.encode('utf-8'))
        test_file.filename = 'test.sql'
        
        # Test file validation
        validation_result = self.validator.validate_file_upload(test_file, 'test.sql')
        
        self.assertTrue(validation_result.is_valid, "File validation should pass")
        self.assertGreater(len(validation_result.passed_rules), 0, "Should have passed rules")
        self.assertIsInstance(validation_result.validation_time, float, "Should track validation time")
        
        print(f"✅ File validation passed: {len(validation_result.passed_rules)} rules")
    
    def test_03_enterprise_validator_content_validation(self):
        """Test enterprise validator content validation"""
        print("\n📝 Testing Content Validation...")
        
        # Test content validation
        validation_result = self.validator.validate_content(self.test_sql, 'test.sql')
        
        self.assertTrue(validation_result.is_valid, "Content validation should pass")
        self.assertGreater(len(validation_result.passed_rules), 0, "Should have passed rules")
        
        # Test malicious content detection
        malicious_sql = "SELECT * FROM users; <script>alert('xss')</script>"
        malicious_result = self.validator.validate_content(malicious_sql, 'malicious.sql')
        
        self.assertFalse(malicious_result.is_valid, "Should detect malicious content")
        self.assertGreater(len(malicious_result.errors), 0, "Should have errors for malicious content")
        
        print("✅ Content validation working correctly")
    
    def test_04_analysis_service_file_analysis(self):
        """Test analysis service file analysis"""
        print("\n🔬 Testing Analysis Service...")
        
        # Create test file
        test_file = BytesIO(self.test_sql.encode('utf-8'))
        test_file.filename = 'test.sql'
        
        # Test analysis
        start_time = time.time()
        result = self.analysis_service.analyze_sql_file(test_file, 'test.sql')
        analysis_time = time.time() - start_time
        
        self.assertTrue(result['success'], f"Analysis should succeed: {result.get('error', '')}")
        self.assertIn('data', result, "Should contain analysis data")
        self.assertLess(analysis_time, 5.0, "Analysis should complete within 5 seconds")
        
        # Verify analysis data structure
        analysis_data = result['data']['analysis_result']
        self.assertIn('id', analysis_data, "Should have analysis ID")
        self.assertIn('quality_score', analysis_data, "Should have quality score")
        self.assertIn('complexity_score', analysis_data, "Should have complexity score")
        
        print(f"✅ Analysis completed in {analysis_time:.3f}s")
        print(f"   Quality Score: {analysis_data['quality_score']}")
        print(f"   Complexity Score: {analysis_data['complexity_score']}")
    
    def test_05_quality_assessment_engine(self):
        """Test quality assessment engine"""
        print("\n⭐ Testing Quality Assessment Engine...")
        
        # Create mock analysis result
        from app.models.analysis_models import AnalysisResult, SQLError, SecurityVulnerability
        
        mock_result = AnalysisResult(
            filename='test.sql',
            database_type=DatabaseType.MYSQL,
            quality_score=85,
            complexity_score=45,
            syntax_errors=[
                SQLError(
                    line_number=10,
                    error_type='syntax_error',
                    severity=ErrorSeverity.MEDIUM,
                    message='Missing semicolon',
                    suggestion='Add semicolon at end of statement'
                )
            ],
            security_vulnerabilities=[
                SecurityVulnerability(
                    line_number=15,
                    vulnerability_type='sql_injection',
                    risk_level=ErrorSeverity.HIGH,
                    description='Potential SQL injection vulnerability',
                    mitigation='Use parameterized queries'
                )
            ]
        )
        
        # Test quality assessment
        assessment = self.quality_engine.assess_overall_quality(mock_result)
        
        self.assertIn('overall_score', assessment, "Should have overall score")
        self.assertIn('quality_level', assessment, "Should have quality level")
        self.assertIn('component_scores', assessment, "Should have component scores")
        self.assertIn('recommendations', assessment, "Should have recommendations")
        
        print(f"✅ Quality assessment completed")
        print(f"   Overall Score: {assessment['overall_score']}")
        print(f"   Quality Level: {assessment['quality_level']}")
    
    def test_06_analysis_controller_integration(self):
        """Test analysis controller integration"""
        print("\n🎮 Testing Analysis Controller...")
        
        # Create test file
        test_file = BytesIO(self.test_sql.encode('utf-8'))
        test_file.filename = 'controller_test.sql'
        
        # Test controller analysis
        result = self.controller.analyze_sql_file(test_file, 'controller_test.sql')
        
        self.assertTrue(result['success'], f"Controller analysis should succeed: {result.get('error', '')}")
        
        # Test getting analysis summary
        if result['success']:
            analysis_id = result['data']['analysis_result']['id']
            summary_result = self.controller.get_analysis_summary(analysis_id)
            
            self.assertTrue(summary_result['success'], "Should get analysis summary")
            self.assertIn('data', summary_result, "Should contain summary data")
        
        print("✅ Controller integration working correctly")
    
    def test_07_data_persistence(self):
        """Test data persistence and retrieval"""
        print("\n💾 Testing Data Persistence...")
        
        # Create and save analysis result
        from app.models.analysis_models import AnalysisResult
        
        test_result = AnalysisResult(
            filename='persistence_test.sql',
            file_hash='test_hash_123',
            database_type=DatabaseType.MYSQL,
            quality_score=90,
            complexity_score=30,
            total_lines=25,
            total_statements=5,
            processing_time=1.5
        )
        
        # Save to repository
        save_success = self.repository.save_analysis_result(test_result)
        self.assertTrue(save_success, "Should save analysis result")
        
        # Retrieve by ID
        retrieved_result = self.repository.get_analysis_by_id(test_result.id)
        self.assertIsNotNone(retrieved_result, "Should retrieve analysis result")
        self.assertEqual(retrieved_result.filename, test_result.filename, "Should match filename")
        
        # Retrieve by hash
        hash_result = self.repository.get_analysis_by_hash(test_result.file_hash)
        self.assertIsNotNone(hash_result, "Should retrieve by hash")
        self.assertEqual(hash_result.id, test_result.id, "Should match ID")
        
        print("✅ Data persistence working correctly")
    
    def test_08_caching_system(self):
        """Test caching system"""
        print("\n🚀 Testing Caching System...")
        
        # Test cache operations
        test_key = 'test_cache_key'
        test_value = {'data': 'test_value', 'timestamp': time.time()}
        
        # Set cache
        cache.set(test_key, test_value, ttl=60)
        
        # Get from cache
        cached_value = cache.get(test_key)
        self.assertIsNotNone(cached_value, "Should retrieve cached value")
        self.assertEqual(cached_value['data'], test_value['data'], "Should match cached data")
        
        # Test cache expiration
        cache.set('expire_test', 'expire_value', ttl=0.1)
        time.sleep(0.2)
        cache.clear_expired()
        expired_value = cache.get('expire_test')
        self.assertIsNone(expired_value, "Should expire cached value")
        
        print("✅ Caching system working correctly")
    
    def test_09_error_handling(self):
        """Test comprehensive error handling"""
        print("\n❌ Testing Error Handling...")
        
        # Test invalid file
        invalid_file = BytesIO(b'')
        invalid_file.filename = ''
        
        result = self.analysis_service.analyze_sql_file(invalid_file, '')
        self.assertFalse(result['success'], "Should fail with invalid file")
        self.assertIn('error', result, "Should contain error message")
        
        # Test invalid analysis ID
        invalid_result = self.controller.get_analysis_summary('invalid-id')
        self.assertFalse(invalid_result['success'], "Should fail with invalid ID")
        
        print("✅ Error handling working correctly")
    
    def test_10_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Test different file sizes
        test_cases = [
            ("Small", self.test_sql),
            ("Medium", self.test_sql * 10),
            ("Large", self.test_sql * 50)
        ]
        
        for case_name, content in test_cases:
            test_file = BytesIO(content.encode('utf-8'))
            test_file.filename = f'{case_name.lower()}_test.sql'
            
            start_time = time.time()
            result = self.analysis_service.analyze_sql_file(test_file, test_file.filename)
            processing_time = time.time() - start_time
            
            self.assertTrue(result['success'], f"{case_name} analysis should succeed")
            self.assertLess(processing_time, 5.0, f"{case_name} should process within 5 seconds")
            
            print(f"✅ {case_name} file ({len(content)} chars): {processing_time:.3f}s")
    
    def test_11_concurrent_operations(self):
        """Test concurrent operations"""
        print("\n🔄 Testing Concurrent Operations...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def analyze_worker(worker_id):
            try:
                test_file = BytesIO(self.test_sql.encode('utf-8'))
                test_file.filename = f'concurrent_test_{worker_id}.sql'
                
                result = self.analysis_service.analyze_sql_file(test_file, test_file.filename)
                results_queue.put(('success', worker_id, result['success']))
            except Exception as e:
                results_queue.put(('error', worker_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=analyze_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results_queue.empty():
            status, worker_id, result = results_queue.get()
            if status == 'success' and result:
                success_count += 1
        
        self.assertEqual(success_count, 3, "All concurrent operations should succeed")
        print(f"✅ {success_count}/3 concurrent operations completed successfully")
    
    def test_12_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing End-to-End Workflow...")
        
        # 1. File validation
        test_file = BytesIO(self.test_sql.encode('utf-8'))
        test_file.filename = 'e2e_test.sql'
        
        validation_result = self.validator.validate_file_upload(test_file, 'e2e_test.sql')
        self.assertTrue(validation_result.is_valid, "File validation should pass")
        
        # 2. Analysis
        analysis_result = self.analysis_service.analyze_sql_file(test_file, 'e2e_test.sql')
        self.assertTrue(analysis_result['success'], "Analysis should succeed")
        
        # 3. Quality assessment
        analysis_id = analysis_result['data']['analysis_result']['id']
        quality_result = self.controller.get_analysis_summary(analysis_id)
        self.assertTrue(quality_result['success'], "Quality assessment should succeed")
        
        # 4. Export (mock)
        export_result = self.controller.export_analysis(analysis_id, 'json')
        self.assertTrue(export_result['success'], "Export should succeed")
        
        print("✅ End-to-end workflow completed successfully")
        print(f"   - File validated: {validation_result.validation_time:.3f}s")
        print(f"   - Analysis completed: {analysis_result['data']['processing_time']:.3f}s")
        print(f"   - Quality assessed: Available")
        print(f"   - Export generated: Available")

def run_enterprise_tests():
    """Run all enterprise tests"""
    print("🚀 STARTING ENTERPRISE SYSTEM TESTING")
    print("=" * 60)
    
    # Configure test runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEnterpriseSystem)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 ENTERPRISE TESTING SUMMARY")
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
    success = run_enterprise_tests()
    sys.exit(0 if success else 1)
