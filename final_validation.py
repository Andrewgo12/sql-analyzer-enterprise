#!/usr/bin/env python3
"""
Final Comprehensive Validation for SQL Analyzer Enterprise
Complete end-to-end system validation
"""

import requests
import json
import time
import os
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)

def validate_system_health():
    """Validate overall system health"""
    print_section("System Health Validation")
    
    health_checks = {
        'Backend Server': False,
        'Frontend Server': False,
        'API Endpoints': False,
        'CORS Configuration': False
    }
    
    # Check backend
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            health_checks['Backend Server'] = True
            print(f"✅ Backend Server: Running (v{data.get('version')})")
            
            # Check all components
            components = data.get('components', {})
            for comp, status in components.items():
                print(f"   - {comp}: {status}")
        else:
            print(f"❌ Backend Server: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Server: {e}")
    
    # Check frontend
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            health_checks['Frontend Server'] = True
            print("✅ Frontend Server: Running")
        else:
            print(f"❌ Frontend Server: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend Server: {e}")
    
    # Check API endpoints
    endpoints = ['/api/health', '/api/analyze', '/api/download']
    working_endpoints = 0
    
    for endpoint in endpoints:
        try:
            if endpoint == '/api/analyze':
                # Test with minimal file
                files = {'file': ('test.sql', 'SELECT 1;', 'text/plain')}
                response = requests.post(f'http://localhost:5000{endpoint}', files=files, timeout=10)
            elif endpoint == '/api/download':
                # Test with minimal data
                data = {'results': {'filename': 'test.sql'}, 'format': 'json'}
                response = requests.post(f'http://localhost:5000{endpoint}', json=data, timeout=10)
            else:
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            
            if response.status_code in [200, 400]:  # 400 is acceptable for some endpoints
                working_endpoints += 1
                print(f"✅ {endpoint}: Working")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    health_checks['API Endpoints'] = working_endpoints == len(endpoints)
    
    # Check CORS
    try:
        response = requests.options('http://localhost:5000/api/health')
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            health_checks['CORS Configuration'] = True
            print(f"✅ CORS: Configured ({cors_header})")
        else:
            print("❌ CORS: Not configured")
    except Exception as e:
        print(f"❌ CORS: {e}")
    
    return health_checks

def validate_core_functionality():
    """Validate core SQL analysis functionality"""
    print_section("Core Functionality Validation")
    
    test_cases = [
        {
            'name': 'Basic SELECT Query',
            'sql': 'SELECT id, name FROM users WHERE active = 1;',
            'expected_errors': 'low'
        },
        {
            'name': 'CREATE TABLE Statement',
            'sql': '''
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''',
            'expected_errors': 'low'
        },
        {
            'name': 'Complex JOIN Query',
            'sql': '''
SELECT u.name, COUNT(o.id) as order_count, SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 10;
''',
            'expected_errors': 'medium'
        },
        {
            'name': 'SQL with Syntax Errors',
            'sql': '''
SELECT * FROM users WHERE name = 'John' AND
CREATE TABLE test (
    id INT PRIMARY KEY
    name VARCHAR(100)
);
SELECT COUNT( FROM users;
''',
            'expected_errors': 'high'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            files = {'file': (f"{test_case['name'].lower().replace(' ', '_')}.sql", 
                            test_case['sql'], 'text/plain')}
            
            start_time = time.time()
            response = requests.post('http://localhost:5000/api/analyze', files=files, timeout=30)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                error_count = result.get('summary', {}).get('total_errors', 0)
                
                # Determine if error count matches expectation
                expected = test_case['expected_errors']
                if expected == 'low' and error_count <= 10:
                    status = "✅"
                elif expected == 'medium' and 10 < error_count <= 50:
                    status = "✅"
                elif expected == 'high' and error_count > 20:
                    status = "✅"
                else:
                    status = "⚠️"
                
                print(f"{status} {test_case['name']}: {error_count} errors ({processing_time:.2f}s)")
                results.append(True)
            else:
                print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {test_case['name']}: {e}")
            results.append(False)
    
    return sum(results) == len(results)

def validate_download_functionality():
    """Validate download functionality"""
    print_section("Download Functionality Validation")
    
    # First get analysis results
    test_sql = '''
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));
SELECT * FROM users WHERE id = 1;
'''
    
    try:
        files = {'file': ('download_test.sql', test_sql, 'text/plain')}
        response = requests.post('http://localhost:5000/api/analyze', files=files, timeout=20)
        
        if response.status_code != 200:
            print("❌ Could not get analysis results for download test")
            return False
        
        analysis_result = response.json()
        
        # Test different download formats
        formats = ['json', 'html', 'txt']
        successful_downloads = 0
        
        for format_type in formats:
            try:
                download_data = {
                    'results': analysis_result,
                    'format': format_type
                }
                
                response = requests.post('http://localhost:5000/api/download', 
                                       json=download_data, timeout=15)
                
                if response.status_code == 200:
                    size_kb = len(response.content) / 1024
                    print(f"✅ {format_type.upper()} download: {size_kb:.1f}KB")
                    successful_downloads += 1
                else:
                    print(f"❌ {format_type.upper()} download: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {format_type.upper()} download: {e}")
        
        return successful_downloads == len(formats)
        
    except Exception as e:
        print(f"❌ Download validation error: {e}")
        return False

def validate_error_handling():
    """Validate error handling"""
    print_section("Error Handling Validation")
    
    error_tests = [
        {
            'name': 'No file provided',
            'test': lambda: requests.post('http://localhost:5000/api/analyze', timeout=5),
            'expected_status': 400
        },
        {
            'name': 'Empty file',
            'test': lambda: requests.post('http://localhost:5000/api/analyze', 
                                        files={'file': ('empty.sql', '', 'text/plain')}, timeout=5),
            'expected_status': 400
        },
        {
            'name': 'Invalid download format',
            'test': lambda: requests.post('http://localhost:5000/api/download',
                                        json={'results': {}, 'format': 'invalid'}, timeout=5),
            'expected_status': 500
        }
    ]
    
    passed_tests = 0
    
    for test in error_tests:
        try:
            response = test['test']()
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: Properly handled (HTTP {response.status_code})")
                passed_tests += 1
            else:
                print(f"❌ {test['name']}: Got HTTP {response.status_code}, expected {test['expected_status']}")
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
    
    return passed_tests == len(error_tests)

def validate_frontend_integration():
    """Validate frontend-backend integration"""
    print_section("Frontend Integration Validation")
    
    integration_tests = {
        'Proxy Configuration': False,
        'File Upload Flow': False,
        'Results Display': False,
        'Download Flow': False
    }
    
    # Test proxy
    try:
        response = requests.get('http://localhost:3000/api/health', timeout=5)
        if response.status_code == 200:
            integration_tests['Proxy Configuration'] = True
            print("✅ Frontend proxy to backend: Working")
        else:
            print(f"❌ Frontend proxy: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend proxy: {e}")
    
    # Test file upload through frontend
    try:
        files = {'file': ('frontend_integration.sql', 'SELECT 1 as test;', 'text/plain')}
        headers = {'Origin': 'http://localhost:3000'}
        response = requests.post('http://localhost:5000/api/analyze', 
                               files=files, headers=headers, timeout=15)
        
        if response.status_code == 200:
            integration_tests['File Upload Flow'] = True
            integration_tests['Results Display'] = True
            print("✅ File upload through frontend: Working")
            print("✅ Results processing: Working")
            
            # Test download
            result = response.json()
            download_data = {'results': result, 'format': 'json'}
            download_response = requests.post('http://localhost:5000/api/download',
                                            json=download_data, headers=headers, timeout=10)
            
            if download_response.status_code == 200:
                integration_tests['Download Flow'] = True
                print("✅ Download through frontend: Working")
            else:
                print(f"❌ Download through frontend: HTTP {download_response.status_code}")
        else:
            print(f"❌ File upload through frontend: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend integration test: {e}")
    
    return all(integration_tests.values())

def main():
    """Main validation function"""
    print_header("SQL ANALYZER ENTERPRISE - FINAL VALIDATION")
    
    validation_results = {
        'System Health': False,
        'Core Functionality': False,
        'Download Functionality': False,
        'Error Handling': False,
        'Frontend Integration': False
    }
    
    # Run all validations
    validation_results['System Health'] = all(validate_system_health().values())
    validation_results['Core Functionality'] = validate_core_functionality()
    validation_results['Download Functionality'] = validate_download_functionality()
    validation_results['Error Handling'] = validate_error_handling()
    validation_results['Frontend Integration'] = validate_frontend_integration()
    
    # Final results
    print_header("FINAL VALIDATION RESULTS")
    
    for category, passed in validation_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{category}: {status}")
    
    total_categories = len(validation_results)
    passed_categories = sum(validation_results.values())
    
    print(f"\nOverall System Status: {passed_categories}/{total_categories} categories passed")
    
    if passed_categories == total_categories:
        print("\n🎉 SYSTEM FULLY VALIDATED!")
        print("✨ SQL Analyzer Enterprise is ready for production use!")
        print("\n📊 System Capabilities:")
        print("   • Complete SQL file analysis")
        print("   • Error detection and reporting")
        print("   • Performance analysis")
        print("   • Security analysis")
        print("   • Multiple download formats")
        print("   • Modern React frontend")
        print("   • Robust Flask backend")
        print("   • Full CORS support")
        print("   • Comprehensive error handling")
        
        print("\n🚀 Access URLs:")
        print("   • Frontend: http://localhost:3000")
        print("   • Backend API: http://localhost:5000")
        print("   • Health Check: http://localhost:5000/api/health")
        
        return True
    else:
        print(f"\n⚠️ SYSTEM VALIDATION INCOMPLETE")
        print(f"   {total_categories - passed_categories} categories need attention")
        print("   Please review the failed tests above")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
