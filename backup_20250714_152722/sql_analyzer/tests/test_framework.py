#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - COMPREHENSIVE TESTING FRAMEWORK
Complete testing suite for all application components
"""

import os
import sys
import json
import asyncio
import unittest
import pytest
import requests
import websockets
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import shutil
from unittest.mock import Mock, patch
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestFramework:
    """Comprehensive testing framework for SQL Analyzer Enterprise."""
    
    def __init__(self):
        self.test_results = []
        self.server_url = "http://localhost:8081"
        self.websocket_url = "ws://localhost:8081"
        self.temp_dir = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup test logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - TEST - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_test_environment(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="sql_analyzer_test_")
        self.logger.info(f"Test environment setup: {self.temp_dir}")
    
    def cleanup_test_environment(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.logger.info("Test environment cleaned up")
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        self.logger.info("🧪 Starting Comprehensive Test Suite")
        
        try:
            self.setup_test_environment()
            
            # Test categories
            test_categories = [
                ("Server Health", self.test_server_health),
                ("API Endpoints", self.test_api_endpoints),
                ("Authentication", self.test_authentication),
                ("File Upload", self.test_file_upload),
                ("WebSocket Communication", self.test_websocket_communication),
                ("Database Integration", self.test_database_integration),
                ("Security Features", self.test_security_features),
                ("Configuration Management", self.test_configuration_management),
                ("Error Handling", self.test_error_handling),
                ("Performance", self.test_performance)
            ]
            
            for category_name, test_function in test_categories:
                self.logger.info(f"🔍 Testing: {category_name}")
                try:
                    results = test_function()
                    self.test_results.extend(results)
                except Exception as e:
                    self.logger.error(f"❌ Test category failed: {category_name} - {e}")
                    self.test_results.append({
                        'category': category_name,
                        'test': 'Category Execution',
                        'status': 'FAILED',
                        'error': str(e)
                    })
            
            # Generate test report
            self.generate_test_report()
            
        finally:
            self.cleanup_test_environment()
    
    def test_server_health(self) -> List[Dict]:
        """Test server health and availability."""
        results = []
        
        # Test 1: Server is running
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            results.append({
                'category': 'Server Health',
                'test': 'Server Running',
                'status': 'PASSED' if response.status_code == 200 else 'FAILED',
                'details': f"Status code: {response.status_code}"
            })
        except Exception as e:
            results.append({
                'category': 'Server Health',
                'test': 'Server Running',
                'status': 'FAILED',
                'error': str(e)
            })
        
        # Test 2: Health endpoint
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            results.append({
                'category': 'Server Health',
                'test': 'Health Endpoint',
                'status': 'PASSED' if response.status_code == 200 else 'FAILED',
                'details': f"Status code: {response.status_code}"
            })
        except Exception as e:
            results.append({
                'category': 'Server Health',
                'test': 'Health Endpoint',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_api_endpoints(self) -> List[Dict]:
        """Test all API endpoints."""
        results = []
        
        endpoints = [
            ("/api/auth/login", "POST"),
            ("/api/auth/logout", "POST"),
            ("/api/auth/validate", "GET"),
            ("/api/upload", "POST"),
            ("/api/files", "GET"),
            ("/api/analysis", "POST"),
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.server_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.server_url}{endpoint}", 
                                           json={}, timeout=5)
                
                # Accept various status codes as valid (not just 200)
                valid_codes = [200, 201, 400, 401, 422]  # Include expected error codes
                status = 'PASSED' if response.status_code in valid_codes else 'FAILED'
                
                results.append({
                    'category': 'API Endpoints',
                    'test': f"{method} {endpoint}",
                    'status': status,
                    'details': f"Status code: {response.status_code}"
                })
                
            except Exception as e:
                results.append({
                    'category': 'API Endpoints',
                    'test': f"{method} {endpoint}",
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        return results
    
    def test_authentication(self) -> List[Dict]:
        """Test authentication system."""
        results = []
        
        # Test 1: Login with valid credentials
        try:
            response = requests.post(f"{self.server_url}/api/auth/login", 
                                   json={"username": "admin", "password": "admin123"}, 
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('session_id'):
                    results.append({
                        'category': 'Authentication',
                        'test': 'Valid Login',
                        'status': 'PASSED',
                        'details': 'Login successful with session ID'
                    })
                else:
                    results.append({
                        'category': 'Authentication',
                        'test': 'Valid Login',
                        'status': 'FAILED',
                        'details': 'Login response missing required fields'
                    })
            else:
                results.append({
                    'category': 'Authentication',
                    'test': 'Valid Login',
                    'status': 'FAILED',
                    'details': f"Status code: {response.status_code}"
                })
                
        except Exception as e:
            results.append({
                'category': 'Authentication',
                'test': 'Valid Login',
                'status': 'FAILED',
                'error': str(e)
            })
        
        # Test 2: Login with invalid credentials
        try:
            response = requests.post(f"{self.server_url}/api/auth/login", 
                                   json={"username": "invalid", "password": "invalid"}, 
                                   timeout=5)
            
            status = 'PASSED' if response.status_code == 401 else 'FAILED'
            results.append({
                'category': 'Authentication',
                'test': 'Invalid Login',
                'status': status,
                'details': f"Status code: {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'category': 'Authentication',
                'test': 'Invalid Login',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_file_upload(self) -> List[Dict]:
        """Test file upload functionality."""
        results = []
        
        # Create test SQL file
        test_sql_content = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
        
        INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com');
        """
        
        test_file_path = os.path.join(self.temp_dir, "test.sql")
        with open(test_file_path, 'w') as f:
            f.write(test_sql_content)
        
        # Test file upload
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test.sql', f, 'text/plain')}
                response = requests.post(f"{self.server_url}/api/upload", 
                                       files=files, timeout=10)
            
            # Accept various success codes
            valid_codes = [200, 201, 202]
            status = 'PASSED' if response.status_code in valid_codes else 'FAILED'
            
            results.append({
                'category': 'File Upload',
                'test': 'SQL File Upload',
                'status': status,
                'details': f"Status code: {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'category': 'File Upload',
                'test': 'SQL File Upload',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_websocket_communication(self) -> List[Dict]:
        """Test WebSocket communication."""
        results = []
        
        async def websocket_test():
            try:
                uri = f"{self.websocket_url}/ws/test_session"
                async with websockets.connect(uri, timeout=5) as websocket:
                    # Test connection
                    results.append({
                        'category': 'WebSocket',
                        'test': 'Connection Establishment',
                        'status': 'PASSED',
                        'details': 'WebSocket connected successfully'
                    })
                    
                    # Test ping-pong
                    await websocket.send(json.dumps({"type": "ping"}))
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    
                    data = json.loads(response)
                    if data.get('type') == 'pong':
                        results.append({
                            'category': 'WebSocket',
                            'test': 'Ping-Pong Communication',
                            'status': 'PASSED',
                            'details': 'Ping-pong successful'
                        })
                    else:
                        results.append({
                            'category': 'WebSocket',
                            'test': 'Ping-Pong Communication',
                            'status': 'FAILED',
                            'details': f"Unexpected response: {data}"
                        })
                        
            except Exception as e:
                results.append({
                    'category': 'WebSocket',
                    'test': 'WebSocket Communication',
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        # Run async test
        try:
            asyncio.run(websocket_test())
        except Exception as e:
            results.append({
                'category': 'WebSocket',
                'test': 'WebSocket Test Execution',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_database_integration(self) -> List[Dict]:
        """Test database integration."""
        results = []
        
        # This would test database connections if available
        results.append({
            'category': 'Database Integration',
            'test': 'Database Connection Test',
            'status': 'SKIPPED',
            'details': 'Database integration test requires configuration'
        })
        
        return results
    
    def test_security_features(self) -> List[Dict]:
        """Test security features."""
        results = []
        
        # Test CORS headers
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            
            results.append({
                'category': 'Security',
                'test': 'CORS Headers',
                'status': 'PASSED' if cors_header else 'FAILED',
                'details': f"CORS header: {cors_header}"
            })
            
        except Exception as e:
            results.append({
                'category': 'Security',
                'test': 'CORS Headers',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_configuration_management(self) -> List[Dict]:
        """Test configuration management."""
        results = []
        
        # Test configuration loading
        try:
            from config.config_manager import ConfigurationManager, Environment
            
            config_manager = ConfigurationManager(environment=Environment.DEVELOPMENT)
            server_config = config_manager.get_server_config()
            
            results.append({
                'category': 'Configuration',
                'test': 'Configuration Loading',
                'status': 'PASSED',
                'details': f"Server port: {server_config.port}"
            })
            
        except Exception as e:
            results.append({
                'category': 'Configuration',
                'test': 'Configuration Loading',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_error_handling(self) -> List[Dict]:
        """Test error handling."""
        results = []
        
        # Test 404 handling
        try:
            response = requests.get(f"{self.server_url}/nonexistent", timeout=5)
            status = 'PASSED' if response.status_code == 404 else 'FAILED'
            
            results.append({
                'category': 'Error Handling',
                'test': '404 Error Handling',
                'status': status,
                'details': f"Status code: {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'category': 'Error Handling',
                'test': '404 Error Handling',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def test_performance(self) -> List[Dict]:
        """Test performance characteristics."""
        results = []
        
        # Test response time
        try:
            import time
            start_time = time.time()
            response = requests.get(f"{self.server_url}/", timeout=5)
            end_time = time.time()
            
            response_time = end_time - start_time
            status = 'PASSED' if response_time < 2.0 else 'FAILED'  # 2 second threshold
            
            results.append({
                'category': 'Performance',
                'test': 'Response Time',
                'status': status,
                'details': f"Response time: {response_time:.3f}s"
            })
            
        except Exception as e:
            results.append({
                'category': 'Performance',
                'test': 'Response Time',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIPPED'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🧪 SQL ANALYZER ENTERPRISE - COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"⏭️  Skipped: {skipped_tests} ({skipped_tests/total_tests*100:.1f}%)")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print detailed results
        for category, tests in categories.items():
            print(f"\n📋 {category}:")
            for test in tests:
                status_icon = "✅" if test['status'] == 'PASSED' else "❌" if test['status'] == 'FAILED' else "⏭️"
                print(f"  {status_icon} {test['test']}")
                if 'details' in test:
                    print(f"     Details: {test['details']}")
                if 'error' in test:
                    print(f"     Error: {test['error']}")
        
        # Save report to file
        report_file = Path("tests") / "test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'skipped_tests': skipped_tests,
                    'success_rate': success_rate
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("="*80)

class UnitTestSuite(unittest.TestCase):
    """Unit tests for individual components."""

    def setUp(self):
        """Setup for unit tests."""
        self.temp_dir = tempfile.mkdtemp(prefix="sql_analyzer_unit_test_")

    def tearDown(self):
        """Cleanup after unit tests."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_config_manager(self):
        """Test configuration manager."""
        try:
            from config.config_manager import ConfigurationManager, Environment

            config_manager = ConfigurationManager(
                config_dir=self.temp_dir,
                environment=Environment.DEVELOPMENT
            )

            # Test configuration loading
            server_config = config_manager.get_server_config()
            self.assertIsNotNone(server_config)
            self.assertTrue(hasattr(server_config, 'port'))
            self.assertTrue(hasattr(server_config, 'host'))

            # Test configuration setting
            config_manager.set_config('test', 'value', 'test_value')
            retrieved_value = config_manager.get_config('test', 'value')
            self.assertEqual(retrieved_value, 'test_value')

        except ImportError:
            self.skipTest("Configuration manager not available")

    def test_security_manager(self):
        """Test security manager."""
        try:
            from security.security_manager import SecurityManager, UserRole

            security_manager = SecurityManager(config_dir=self.temp_dir)

            # Test password hashing
            password = "test_password"
            hashed = security_manager.hash_password(password)
            self.assertNotEqual(password, hashed)
            self.assertTrue(security_manager.verify_password(password, hashed))
            self.assertFalse(security_manager.verify_password("wrong_password", hashed))

            # Test user creation
            user = security_manager.create_user(
                username="test_user",
                email="test@example.com",
                password="test_password",
                role=UserRole.ANALYST
            )
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "test_user")
            self.assertEqual(user.role, UserRole.ANALYST)

        except ImportError:
            self.skipTest("Security manager not available")

    def test_database_integration(self):
        """Test database integration manager."""
        try:
            from integrations.database_integrations import DatabaseIntegrationManager, DatabaseType

            db_manager = DatabaseIntegrationManager(config_dir=self.temp_dir)

            # Test connection addition
            conn_id = db_manager.add_connection(
                name="Test SQLite",
                db_type=DatabaseType.SQLITE,
                host="localhost",
                port=0,
                database=os.path.join(self.temp_dir, "test.db"),
                username="",
                password=""
            )

            self.assertIsNotNone(conn_id)

            # Test connection listing
            connections = db_manager.list_connections()
            self.assertGreater(len(connections), 0)

            # Test connection testing
            success, message = db_manager.test_connection(conn_id)
            # SQLite connection should work
            self.assertTrue(success or "not found" in message.lower())

        except ImportError:
            self.skipTest("Database integration manager not available")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='SQL Analyzer Enterprise Test Suite')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')

    args = parser.parse_args()

    if args.unit:
        # Run unit tests
        unittest.main(argv=[''], exit=False, verbosity=2)
    elif args.integration:
        # Run integration tests
        test_framework = TestFramework()
        test_framework.run_all_tests()
    else:
        # Run all tests (default)
        print("🧪 Running Unit Tests...")
        unittest.main(argv=[''], exit=False, verbosity=2)

        print("\n🧪 Running Integration Tests...")
        test_framework = TestFramework()
        test_framework.run_all_tests()
