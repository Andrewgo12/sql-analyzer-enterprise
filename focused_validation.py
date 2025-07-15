#!/usr/bin/env python3
"""
Focused Validation Script for SQL Analyzer Enterprise
Quick validation of all critical functionality
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(name, url, method='GET', data=None, files=None, timeout=10):
    """Test an endpoint and return result"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, files=files, timeout=timeout)
        
        if response.status_code == 200:
            print(f"✅ {name}: OK")
            return True, response.json() if 'json' in response.headers.get('content-type', '') else response.text
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False, None

def main():
    print("🚀 FOCUSED VALIDATION - SQL ANALYZER ENTERPRISE")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    frontend_url = "http://localhost:3000"
    
    tests_passed = 0
    total_tests = 0
    
    # 1. Backend Health
    total_tests += 1
    success, data = test_endpoint("Backend Health", f"{base_url}/api/health")
    if success:
        tests_passed += 1
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Version: {data.get('version', 'unknown')}")
        print(f"   Components: {len(data.get('components', {}))}")
    
    # 2. Database Engines
    total_tests += 1
    success, data = test_endpoint("Database Engines", f"{base_url}/api/databases/supported")
    if success:
        tests_passed += 1
        print(f"   Total Engines: {data.get('total_engines', 0)}")
    
    # 3. Export Formats
    total_tests += 1
    success, data = test_endpoint("Export Formats", f"{base_url}/api/export/formats")
    if success:
        tests_passed += 1
        print(f"   Total Formats: {data.get('total_formats', 0)}")
    
    # 4. Metrics Dashboard
    total_tests += 1
    success, data = test_endpoint("Metrics Dashboard", f"{base_url}/api/metrics/dashboard")
    if success:
        tests_passed += 1
        print(f"   Total Analyses: {data.get('overview', {}).get('total_analyses', 0)}")
    
    # 5. SQL Analysis Test
    total_tests += 1
    test_sql = "SELECT * FROM users WHERE id = 1;"
    files = {'file': ('test.sql', test_sql, 'text/plain')}
    try:
        response = requests.post(f"{base_url}/api/analyze", 
                               files=files, 
                               data={'database_engine': 'mysql'}, 
                               timeout=15)
        if response.status_code == 200:
            tests_passed += 1
            print("✅ SQL Analysis: OK")
            result = response.json()
            print(f"   Errors Found: {result.get('summary', {}).get('total_errors', 0)}")
        else:
            print(f"❌ SQL Analysis: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ SQL Analysis: {str(e)}")
    
    # 6. Export Test
    total_tests += 1
    sample_data = {
        'filename': 'test.sql',
        'summary': {'total_errors': 0, 'performance_score': 100},
        'analysis': {'errors': []}
    }
    success, _ = test_endpoint("Export JSON", f"{base_url}/api/export/json", 
                              method='POST', data=sample_data)
    if success:
        tests_passed += 1
    
    # 7. Frontend Application
    total_tests += 1
    success, data = test_endpoint("Frontend App", frontend_url)
    if success:
        tests_passed += 1
        if 'root' in data:
            print("   React app detected")
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    
    success_rate = (tests_passed / total_tests) * 100
    print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("\n🎉 VALIDATION PASSED!")
        print("✨ Application is ready for production!")
        return True
    else:
        print("\n⚠️ VALIDATION FAILED!")
        print("🔧 Some issues need to be fixed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
