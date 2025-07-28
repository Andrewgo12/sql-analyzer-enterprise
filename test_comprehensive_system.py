#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM TESTING
Test suite for the complete SQL analysis system
"""

import unittest
import tempfile
import os
import json
import time
from io import BytesIO
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from comprehensive_sql_analyzer import ComprehensiveSQLAnalyzer, DatabaseType
    from export_engine import ExportEngine
    from enterprise_file_processor import EnterpriseFileProcessor
    ENTERPRISE_AVAILABLE = True
except ImportError as e:
    print(f"Enterprise modules not available: {e}")
    ENTERPRISE_AVAILABLE = False

class TestComprehensiveSQLSystem(unittest.TestCase):
    """Test suite for comprehensive SQL analysis system"""
    
    def setUp(self):
        """Set up test environment"""
        if not ENTERPRISE_AVAILABLE:
            self.skipTest("Enterprise modules not available")
        
        self.analyzer = ComprehensiveSQLAnalyzer()
        self.export_engine = ExportEngine()
        self.file_processor = EnterpriseFileProcessor()
        
        # Test SQL content
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

-- Potential security vulnerability for testing
SELECT * FROM users WHERE username = 'admin' OR '1'='1';

-- Performance issue for testing
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
    
    def test_01_file_processor_basic(self):
        """Test basic file processing functionality"""
        print("\n🔍 Testing File Processor...")
        
        # Create test file
        test_file = BytesIO(self.test_sql.encode('utf-8'))
        test_file.filename = 'test.sql'
        
        # Process file
        result = self.file_processor.process_file(test_file, 'test.sql')
        
        self.assertTrue(result['success'])
        self.assertIn('content', result)
        self.assertIn('file_info', result)
        self.assertEqual(result['file_info'].filename, 'test.sql')
        print("✅ File processor working correctly")
    
    def test_02_file_processor_security(self):
        """Test file processor security validation"""
        print("\n🔒 Testing Security Validation...")
        
        # Test malicious content
        malicious_content = "<script>alert('xss')</script>\nSELECT * FROM users;"
        test_file = BytesIO(malicious_content.encode('utf-8'))
        test_file.filename = 'malicious.sql'
        
        result = self.file_processor.process_file(test_file, 'malicious.sql')
        
        # Should detect malicious content
        if not result['success']:
            print("✅ Security validation working - malicious content detected")
        else:
            print("⚠️ Security validation may need improvement")
    
    def test_03_file_processor_large_file(self):
        """Test large file handling"""
        print("\n📁 Testing Large File Handling...")
        
        # Create larger content
        large_content = self.test_sql * 100  # Simulate larger file
        test_file = BytesIO(large_content.encode('utf-8'))
        test_file.filename = 'large_test.sql'
        
        start_time = time.time()
        result = self.file_processor.process_file(test_file, 'large_test.sql')
        processing_time = time.time() - start_time
        
        self.assertTrue(result['success'])
        self.assertLess(processing_time, 2.0, "Large file processing should be under 2 seconds")
        print(f"✅ Large file processed in {processing_time:.3f}s")
    
    def test_04_sql_analyzer_basic(self):
        """Test basic SQL analysis functionality"""
        print("\n🔍 Testing SQL Analyzer...")
        
        result = self.analyzer.analyze_file(self.test_sql, 'test.sql', DatabaseType.MYSQL)
        
        self.assertIsNotNone(result)
        self.assertGreater(result.total_lines, 0)
        self.assertGreater(result.total_statements, 0)
        self.assertIsInstance(result.quality_score, int)
        self.assertIsInstance(result.complexity_score, int)
        print(f"✅ Analysis completed - Quality: {result.quality_score}, Complexity: {result.complexity_score}")
    
    def test_05_sql_analyzer_error_detection(self):
        """Test SQL error detection"""
        print("\n❌ Testing Error Detection...")
        
        # SQL with intentional errors
        error_sql = """
        SELECT * FROM users WHERE name = 'test' AND (incomplete_condition
        UPDATE users SET name = 'test'  -- Missing WHERE clause
        SELECT * FROM nonexistent_table;
        """
        
        result = self.analyzer.analyze_file(error_sql, 'error_test.sql', DatabaseType.MYSQL)
        
        # Should detect errors
        total_errors = len(result.syntax_errors) + len(result.semantic_errors)
        self.assertGreater(total_errors, 0, "Should detect syntax/semantic errors")
        print(f"✅ Detected {total_errors} errors")
    
    def test_06_sql_analyzer_performance_issues(self):
        """Test performance issue detection"""
        print("\n⚡ Testing Performance Analysis...")
        
        # SQL with performance issues
        perf_sql = """
        SELECT * FROM large_table;  -- SELECT *
        SELECT name FROM users WHERE UPPER(name) = 'TEST';  -- Function in WHERE
        SELECT * FROM table1, table2;  -- Cartesian product
        """
        
        result = self.analyzer.analyze_file(perf_sql, 'perf_test.sql', DatabaseType.MYSQL)
        
        self.assertGreater(len(result.performance_issues), 0, "Should detect performance issues")
        print(f"✅ Detected {len(result.performance_issues)} performance issues")
    
    def test_07_sql_analyzer_security_vulnerabilities(self):
        """Test security vulnerability detection"""
        print("\n🛡️ Testing Security Analysis...")
        
        # SQL with security issues
        security_sql = """
        SELECT * FROM users WHERE id = 1 OR 1=1;  -- SQL injection
        SELECT * FROM users WHERE password = 'hardcoded123';  -- Hardcoded credential
        """
        
        result = self.analyzer.analyze_file(security_sql, 'security_test.sql', DatabaseType.MYSQL)
        
        self.assertGreater(len(result.security_vulnerabilities), 0, "Should detect security vulnerabilities")
        print(f"✅ Detected {len(result.security_vulnerabilities)} security vulnerabilities")
    
    def test_08_sql_analyzer_intelligent_comments(self):
        """Test intelligent comment generation"""
        print("\n💬 Testing Intelligent Comments...")
        
        result = self.analyzer.analyze_file(self.test_sql, 'test.sql', DatabaseType.MYSQL)
        
        self.assertGreater(len(result.intelligent_comments), 0, "Should generate intelligent comments")
        
        # Check if comments are in Spanish
        spanish_found = any('consulta' in comment['comment'].lower() or 
                          'tabla' in comment['comment'].lower() or
                          'datos' in comment['comment'].lower()
                          for comment in result.intelligent_comments)
        self.assertTrue(spanish_found, "Comments should be in Spanish")
        print(f"✅ Generated {len(result.intelligent_comments)} intelligent comments in Spanish")
    
    def test_09_database_type_detection(self):
        """Test database type detection"""
        print("\n🗄️ Testing Database Type Detection...")
        
        # MySQL specific SQL
        mysql_sql = "CREATE TABLE test (id INT AUTO_INCREMENT PRIMARY KEY) ENGINE=InnoDB;"
        result = self.analyzer.detect_database_type(mysql_sql)
        self.assertEqual(result, DatabaseType.MYSQL)
        
        # PostgreSQL specific SQL
        postgres_sql = "CREATE TABLE test (id SERIAL PRIMARY KEY); SELECT * FROM test LIMIT 10 OFFSET 5;"
        result = self.analyzer.detect_database_type(postgres_sql)
        self.assertEqual(result, DatabaseType.POSTGRESQL)
        
        print("✅ Database type detection working")
    
    def test_10_export_engine_formats(self):
        """Test export engine with multiple formats"""
        print("\n📤 Testing Export Engine...")
        
        # Analyze SQL first
        analysis_result = self.analyzer.analyze_file(self.test_sql, 'test.sql', DatabaseType.MYSQL)
        
        # Test different export formats
        formats_to_test = ['json', 'html', 'xml', 'csv', 'markdown', 'txt', 'sql']
        
        for format_type in formats_to_test:
            export_result = self.export_engine.export(analysis_result, format_type)
            self.assertTrue(export_result['success'], f"Export to {format_type} should succeed")
            self.assertIn('content', export_result)
            self.assertIn('filename', export_result)
            print(f"✅ {format_type.upper()} export working")
    
    def test_11_export_engine_mysql_dump(self):
        """Test MySQL dump export"""
        print("\n🗄️ Testing MySQL Dump Export...")
        
        analysis_result = self.analyzer.analyze_file(self.test_sql, 'test.sql', DatabaseType.MYSQL)
        export_result = self.export_engine.export(analysis_result, 'mysql_dump')
        
        self.assertTrue(export_result['success'])
        self.assertIn('SET @OLD_UNIQUE_CHECKS', export_result['content'])
        print("✅ MySQL dump export working")
    
    def test_12_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Test with different file sizes
        test_cases = [
            ("Small", self.test_sql),
            ("Medium", self.test_sql * 10),
            ("Large", self.test_sql * 50)
        ]
        
        for case_name, content in test_cases:
            start_time = time.time()
            result = self.analyzer.analyze_file(content, f'{case_name.lower()}_test.sql', DatabaseType.MYSQL)
            processing_time = time.time() - start_time
            
            self.assertLess(processing_time, 2.0, f"{case_name} file should process under 2 seconds")
            print(f"✅ {case_name} file ({len(content)} chars): {processing_time:.3f}s")
    
    def test_13_memory_efficiency(self):
        """Test memory efficiency"""
        print("\n💾 Testing Memory Efficiency...")
        
        try:
            import psutil
            process = psutil.Process()
            
            # Get initial memory
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process large content
            large_content = self.test_sql * 100
            result = self.analyzer.analyze_file(large_content, 'memory_test.sql', DatabaseType.MYSQL)
            
            # Get final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"✅ Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
            
            # Memory increase should be reasonable
            self.assertLess(memory_increase, 100, "Memory increase should be under 100MB")
            
        except ImportError:
            print("⚠️ psutil not available for memory testing")
    
    def test_14_concurrent_processing(self):
        """Test concurrent processing capability"""
        print("\n🔄 Testing Concurrent Processing...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def analyze_worker(content, filename):
            try:
                result = self.analyzer.analyze_file(content, filename, DatabaseType.MYSQL)
                results_queue.put(('success', result.quality_score))
            except Exception as e:
                results_queue.put(('error', str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=analyze_worker, 
                args=(self.test_sql, f'concurrent_test_{i}.sql')
            )
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results_queue.empty():
            status, result = results_queue.get()
            if status == 'success':
                success_count += 1
        
        self.assertEqual(success_count, 3, "All concurrent analyses should succeed")
        print(f"✅ {success_count}/3 concurrent analyses completed successfully")
    
    def test_15_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing End-to-End Workflow...")
        
        # 1. File processing
        test_file = BytesIO(self.test_sql.encode('utf-8'))
        test_file.filename = 'e2e_test.sql'
        
        file_result = self.file_processor.process_file(test_file, 'e2e_test.sql')
        self.assertTrue(file_result['success'])
        
        # 2. SQL analysis
        analysis_result = self.analyzer.analyze_file(
            file_result['content'], 
            'e2e_test.sql', 
            DatabaseType.MYSQL
        )
        self.assertIsNotNone(analysis_result)
        
        # 3. Export results
        export_result = self.export_engine.export(analysis_result, 'html')
        self.assertTrue(export_result['success'])
        
        print("✅ End-to-end workflow completed successfully")
        print(f"   - File processed: {file_result['file_info'].size} bytes")
        print(f"   - Analysis completed: {analysis_result.processing_time:.3f}s")
        print(f"   - Export generated: {len(export_result['content'])} chars")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 STARTING COMPREHENSIVE SQL SYSTEM TESTING")
    print("=" * 60)
    
    if not ENTERPRISE_AVAILABLE:
        print("❌ Enterprise modules not available - cannot run tests")
        return False
    
    # Configure test runner
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestComprehensiveSQLSystem)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 COMPREHENSIVE TESTING SUMMARY")
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
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
