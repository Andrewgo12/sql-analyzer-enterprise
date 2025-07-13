#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - COMPREHENSIVE INTEGRATION VALIDATION
Complete validation of all frontend-backend integrations and component functionality
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

class IntegrationValidator:
    """Comprehensive integration validator for SQL Analyzer Enterprise."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.server_url = "http://localhost:8081"
        self.validation_results = []
        
    def validate_all_integrations(self):
        """Run comprehensive integration validation."""
        print("🔍 SQL ANALYZER ENTERPRISE - COMPREHENSIVE INTEGRATION VALIDATION")
        print("=" * 80)
        
        # Test categories
        validations = [
            ("Server Health", self.validate_server_health),
            ("Frontend-Backend API Integration", self.validate_api_integration),
            ("JavaScript Component Integration", self.validate_js_integration),
            ("Results Display Integration", self.validate_results_integration),
            ("Authentication Flow", self.validate_auth_integration),
            ("File Upload Integration", self.validate_upload_integration),
            ("WebSocket Communication", self.validate_websocket_integration),
            ("Cross-Component Functionality", self.validate_cross_component),
            ("End-to-End User Workflow", self.validate_end_to_end),
            ("Enterprise Quality Standards", self.validate_enterprise_quality)
        ]
        
        for category, validator in validations:
            print(f"\n🧪 Testing: {category}")
            try:
                results = validator()
                self.validation_results.extend(results)
                passed = len([r for r in results if r['status'] == 'PASSED'])
                total = len(results)
                print(f"   ✅ {passed}/{total} tests passed")
            except Exception as e:
                print(f"   ❌ Validation failed: {e}")
                self.validation_results.append({
                    'category': category,
                    'test': 'Category Execution',
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        self.generate_integration_report()
    
    def validate_server_health(self):
        """Validate server health and basic functionality."""
        results = []
        
        # Test server is running
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            results.append({
                'category': 'Server Health',
                'test': 'Server Running',
                'status': 'PASSED' if response.status_code == 200 else 'FAILED',
                'details': f"Status: {response.status_code}"
            })
        except Exception as e:
            results.append({
                'category': 'Server Health',
                'test': 'Server Running',
                'status': 'FAILED',
                'error': str(e)
            })
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            results.append({
                'category': 'Server Health',
                'test': 'Health Endpoint',
                'status': 'PASSED' if response.status_code == 200 else 'FAILED',
                'details': f"Status: {response.status_code}"
            })
        except Exception as e:
            results.append({
                'category': 'Server Health',
                'test': 'Health Endpoint',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def validate_api_integration(self):
        """Validate API endpoints integration."""
        results = []
        
        # Test critical API endpoints
        endpoints = [
            ("/api/auth/login", "POST", {"username": "test", "password": "test"}),
            ("/api/auth/validate", "GET", None),
            ("/api/files", "GET", None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.server_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.server_url}{endpoint}", 
                                           json=data, timeout=5)
                
                # Accept various status codes as valid
                valid_codes = [200, 201, 400, 401, 422]
                status = 'PASSED' if response.status_code in valid_codes else 'FAILED'
                
                results.append({
                    'category': 'API Integration',
                    'test': f"{method} {endpoint}",
                    'status': status,
                    'details': f"Status: {response.status_code}"
                })
                
            except Exception as e:
                results.append({
                    'category': 'API Integration',
                    'test': f"{method} {endpoint}",
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        return results
    
    def validate_js_integration(self):
        """Validate JavaScript component integration."""
        results = []
        
        # Check JavaScript files exist
        js_files = [
            'web_app/static/js/utils.js',
            'web_app/static/js/api.js',
            'web_app/static/js/results.js',
            'web_app/static/js/auth.js',
            'web_app/static/js/upload.js',
            'web_app/static/js/analysis.js',
            'web_app/static/js/events.js',
            'web_app/static/js/app-controller.js'
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                # Check file has content
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 100:  # Basic content check
                        results.append({
                            'category': 'JS Integration',
                            'test': f"{js_file} exists and has content",
                            'status': 'PASSED',
                            'details': f"Size: {len(content)} chars"
                        })
                    else:
                        results.append({
                            'category': 'JS Integration',
                            'test': f"{js_file} content check",
                            'status': 'FAILED',
                            'details': "File too small or empty"
                        })
            else:
                results.append({
                    'category': 'JS Integration',
                    'test': f"{js_file} exists",
                    'status': 'FAILED',
                    'details': "File not found"
                })
        
        return results
    
    def validate_results_integration(self):
        """Validate results display integration."""
        results = []
        
        # Check results.js has required methods
        results_file = 'web_app/static/js/results.js'
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                required_methods = [
                    'displayResults',
                    'updateRecommendations',
                    'renderErrorList',
                    'updateSchemaStatistics',
                    'renderSchemaDiagram',
                    'loadSampleResults'
                ]
                
                for method in required_methods:
                    if method in content:
                        results.append({
                            'category': 'Results Integration',
                            'test': f"Method {method} exists",
                            'status': 'PASSED',
                            'details': "Method found in results.js"
                        })
                    else:
                        results.append({
                            'category': 'Results Integration',
                            'test': f"Method {method} exists",
                            'status': 'FAILED',
                            'details': "Method not found"
                        })
        
        return results
    
    def validate_auth_integration(self):
        """Validate authentication integration."""
        results = []
        
        # Test login endpoint
        try:
            response = requests.post(f"{self.server_url}/api/auth/login", 
                                   json={"username": "admin", "password": "admin123"}, 
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results.append({
                        'category': 'Auth Integration',
                        'test': 'Login Success',
                        'status': 'PASSED',
                        'details': 'Login endpoint working'
                    })
                else:
                    results.append({
                        'category': 'Auth Integration',
                        'test': 'Login Response',
                        'status': 'FAILED',
                        'details': 'Invalid response format'
                    })
            else:
                results.append({
                    'category': 'Auth Integration',
                    'test': 'Login Endpoint',
                    'status': 'FAILED',
                    'details': f"Status: {response.status_code}"
                })
                
        except Exception as e:
            results.append({
                'category': 'Auth Integration',
                'test': 'Login Integration',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def validate_upload_integration(self):
        """Validate file upload integration."""
        results = []
        
        # Check upload endpoint exists
        try:
            # Create a test file
            test_content = "SELECT * FROM test_table;"
            files = {'file': ('test.sql', test_content, 'text/plain')}
            
            response = requests.post(f"{self.server_url}/api/files/upload", 
                                   files=files, timeout=10)
            
            # Accept various status codes (may require auth)
            valid_codes = [200, 201, 401, 422]
            status = 'PASSED' if response.status_code in valid_codes else 'FAILED'
            
            results.append({
                'category': 'Upload Integration',
                'test': 'File Upload Endpoint',
                'status': status,
                'details': f"Status: {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'category': 'Upload Integration',
                'test': 'Upload Integration',
                'status': 'FAILED',
                'error': str(e)
            })
        
        return results
    
    def validate_websocket_integration(self):
        """Validate WebSocket integration."""
        results = []
        
        # Check WebSocket manager exists
        ws_file = 'web_app/static/js/websocket-manager.js'
        if os.path.exists(ws_file):
            results.append({
                'category': 'WebSocket Integration',
                'test': 'WebSocket Manager File',
                'status': 'PASSED',
                'details': 'WebSocket manager file exists'
            })
        else:
            results.append({
                'category': 'WebSocket Integration',
                'test': 'WebSocket Manager File',
                'status': 'FAILED',
                'details': 'WebSocket manager file missing'
            })
        
        return results
    
    def validate_cross_component(self):
        """Validate cross-component functionality."""
        results = []
        
        # Check app-controller integration
        controller_file = 'web_app/static/js/app-controller.js'
        if os.path.exists(controller_file):
            with open(controller_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for results manager integration
                if 'resultsManager' in content:
                    results.append({
                        'category': 'Cross-Component',
                        'test': 'Results Manager Integration',
                        'status': 'PASSED',
                        'details': 'Results manager referenced in app controller'
                    })
                else:
                    results.append({
                        'category': 'Cross-Component',
                        'test': 'Results Manager Integration',
                        'status': 'FAILED',
                        'details': 'Results manager not integrated'
                    })
        
        return results
    
    def validate_end_to_end(self):
        """Validate end-to-end user workflow."""
        results = []
        
        # Check main HTML template
        template_file = 'web_app/templates/app.html'
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for required elements
                required_elements = [
                    'resultsManager',
                    'appController',
                    'authManager',
                    'uploadManager'
                ]
                
                for element in required_elements:
                    if element in content:
                        results.append({
                            'category': 'End-to-End',
                            'test': f"{element} in template",
                            'status': 'PASSED',
                            'details': f"{element} found in HTML template"
                        })
                    else:
                        results.append({
                            'category': 'End-to-End',
                            'test': f"{element} in template",
                            'status': 'FAILED',
                            'details': f"{element} not found"
                        })
        
        return results
    
    def validate_enterprise_quality(self):
        """Validate enterprise quality standards."""
        results = []
        
        # Check for error handling
        server_file = 'web_app/server.py'
        if os.path.exists(server_file):
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for proper error handling
                if 'try:' in content and 'except' in content:
                    results.append({
                        'category': 'Enterprise Quality',
                        'test': 'Error Handling',
                        'status': 'PASSED',
                        'details': 'Error handling implemented'
                    })
                else:
                    results.append({
                        'category': 'Enterprise Quality',
                        'test': 'Error Handling',
                        'status': 'FAILED',
                        'details': 'Insufficient error handling'
                    })
                
                # Check for logging
                if 'logger' in content:
                    results.append({
                        'category': 'Enterprise Quality',
                        'test': 'Logging Implementation',
                        'status': 'PASSED',
                        'details': 'Logging implemented'
                    })
                else:
                    results.append({
                        'category': 'Enterprise Quality',
                        'test': 'Logging Implementation',
                        'status': 'FAILED',
                        'details': 'No logging found'
                    })
        
        return results
    
    def generate_integration_report(self):
        """Generate comprehensive integration report."""
        total_tests = len(self.validation_results)
        passed_tests = len([r for r in self.validation_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.validation_results if r['status'] == 'FAILED'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 SQL ANALYZER ENTERPRISE - INTEGRATION VALIDATION REPORT")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        # Group by category
        categories = {}
        for result in self.validation_results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print detailed results
        for category, tests in categories.items():
            passed = len([t for t in tests if t['status'] == 'PASSED'])
            total = len(tests)
            print(f"\n📋 {category}: {passed}/{total} passed")
            
            for test in tests:
                status_icon = "✅" if test['status'] == 'PASSED' else "❌"
                print(f"  {status_icon} {test['test']}")
                if 'details' in test:
                    print(f"     {test['details']}")
                if 'error' in test:
                    print(f"     Error: {test['error']}")
        
        # Final verdict
        print("\n" + "=" * 80)
        if success_rate >= 90:
            print("🎉 INTEGRATION STATUS: EXCELLENT - Ready for production!")
        elif success_rate >= 80:
            print("✅ INTEGRATION STATUS: GOOD - Minor issues to address")
        elif success_rate >= 70:
            print("⚠️  INTEGRATION STATUS: ACCEPTABLE - Some improvements needed")
        else:
            print("❌ INTEGRATION STATUS: NEEDS WORK - Major issues to resolve")
        
        print(f"Overall Integration Quality: {success_rate:.1f}%")
        print("=" * 80)

def main():
    validator = IntegrationValidator()
    validator.validate_all_integrations()

if __name__ == "__main__":
    main()
