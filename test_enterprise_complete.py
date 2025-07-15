#!/usr/bin/env python3
"""
Test Enterprise Complete Integration
Comprehensive testing of all enterprise features
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_health():
    """Test backend health and basic endpoints"""
    print("=== Testing Backend Health ===")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend health: {health_data['status']}")
            print(f"   Components: {list(health_data['components'].keys())}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Backend health test failed: {e}")
        return False

def test_database_support():
    """Test database engine support"""
    print("\n=== Testing Database Support ===")
    
    try:
        # Test supported databases endpoint
        response = requests.get('http://localhost:5000/api/databases/supported', timeout=10)
        if response.status_code == 200:
            db_data = response.json()
            print(f"✅ Supported databases: {db_data['total_engines']} engines")
            print(f"   Categories: {db_data['categories']}")
            
            # Show some examples
            for engine in db_data['engines'][:5]:
                print(f"   - {engine['name']} ({engine['category']})")
            
            if db_data['total_engines'] >= 10:
                print("✅ Enterprise database support confirmed")
            else:
                print("⚠️  Limited database support")
        else:
            print(f"❌ Database support test failed: {response.status_code}")
            return False
        
        # Test database detection
        test_sql = "SELECT * FROM users WHERE id = 1;"
        detection_data = {
            'sql_content': test_sql,
            'connection_string': 'mysql://localhost:3306/test'
        }
        
        response = requests.post('http://localhost:5000/api/databases/detect', 
                               json=detection_data, timeout=5)
        if response.status_code == 200:
            detect_data = response.json()
            print(f"✅ Database detection: {detect_data['detected_engine']}")
        else:
            print(f"⚠️  Database detection test failed: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Database support test failed: {e}")
        return False

def test_export_formats():
    """Test export format support"""
    print("\n=== Testing Export Formats ===")
    
    try:
        # Test export formats endpoint
        response = requests.get('http://localhost:5000/api/export/formats', timeout=10)
        if response.status_code == 200:
            export_data = response.json()
            print(f"✅ Supported export formats: {export_data['total_formats']} formats")
            print(f"   Categories: {export_data['categories']}")
            
            # Show some examples by category
            formats_by_category = {}
            for fmt in export_data['formats']:
                category = fmt['category']
                if category not in formats_by_category:
                    formats_by_category[category] = []
                formats_by_category[category].append(fmt['name'])
            
            for category, formats in formats_by_category.items():
                print(f"   {category}: {', '.join(formats[:3])}")
            
            if export_data['total_formats'] >= 15:
                print("✅ Enterprise export support confirmed")
            else:
                print("⚠️  Limited export support")
        else:
            print(f"❌ Export formats test failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Export formats test failed: {e}")
        return False

def test_analysis_functionality():
    """Test SQL analysis functionality"""
    print("\n=== Testing Analysis Functionality ===")
    
    try:
        # Create test SQL file
        test_sql = """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255)
        );
        
        SELECT * FROM users WHERE name LIKE '%test%';
        
        INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com');
        """
        
        # Test analysis endpoint
        files = {'file': ('test.sql', test_sql, 'text/plain')}
        data = {
            'database_engine': 'mysql',
            'analysis_types': 'syntax,performance,security'
        }
        
        print("   Sending analysis request...")
        response = requests.post('http://localhost:5000/api/analyze', 
                               files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"✅ Analysis completed successfully")
            print(f"   File: {analysis_data.get('filename', 'N/A')}")
            print(f"   Lines: {analysis_data.get('line_count', 0)}")
            print(f"   Errors: {analysis_data.get('summary', {}).get('total_errors', 0)}")
            print(f"   Performance: {analysis_data.get('summary', {}).get('performance_score', 100)}%")
            print(f"   Security: {analysis_data.get('summary', {}).get('security_score', 100)}%")
            
            # Test export with analysis data
            print("   Testing export functionality...")
            export_response = requests.post('http://localhost:5000/api/export/json',
                                          json=analysis_data, timeout=10)
            
            if export_response.status_code == 200:
                print("✅ Export functionality working")
            else:
                print(f"⚠️  Export test failed: {export_response.status_code}")
            
            return True
        else:
            print(f"❌ Analysis test failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}")
            return False
        
    except Exception as e:
        print(f"❌ Analysis functionality test failed: {e}")
        return False

def test_frontend_connectivity():
    """Test frontend connectivity"""
    print("\n=== Testing Frontend Connectivity ===")
    
    try:
        # Test frontend is serving
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is serving correctly")
            
            # Check if it contains React app
            if 'root' in response.text and 'script' in response.text:
                print("✅ React application detected")
            else:
                print("⚠️  React application not detected")
            
            return True
        else:
            print(f"❌ Frontend connectivity test failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Frontend connectivity test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive enterprise test suite"""
    print("🚀 SQL Analyzer Enterprise - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Database Support", test_database_support),
        ("Export Formats", test_export_formats),
        ("Analysis Functionality", test_analysis_functionality),
        ("Frontend Connectivity", test_frontend_connectivity)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enterprise system is fully functional.")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed. Minor issues detected.")
    else:
        print("❌ Multiple test failures. System needs attention.")
    
    return passed == total

if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
