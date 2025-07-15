#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""

import sys
import json
import requests
import time
from datetime import datetime

def test_endpoint(url, description):
    """Test a single endpoint"""
    print(f"\n🧪 Testing {description}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - Status: {response.status_code}")
            
            # Print key information
            if 'total_engines' in data:
                print(f"   📊 Total engines: {data['total_engines']}")
                if 'engines' in data and len(data['engines']) > 0:
                    print(f"   🔧 Sample engines: {[e['name'] for e in data['engines'][:3]]}")
                if 'categories' in data:
                    print(f"   📂 Categories: {data['categories']}")
            elif 'total_formats' in data:
                print(f"   📊 Total formats: {data['total_formats']}")
                if 'formats' in data and len(data['formats']) > 0:
                    print(f"   📄 Sample formats: {[f['name'] for f in data['formats'][:3]]}")
            elif 'status' in data:
                print(f"   💚 Status: {data['status']}")
                if 'performance' in data:
                    print(f"   ⚡ Performance: {data['performance']}")
            else:
                print(f"   📋 Response keys: {list(data.keys())}")
                
            return True, data
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"   🔌 CONNECTION ERROR - Server not running?")
        return False, None
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT - Server too slow")
        return False, None
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        return False, None

def main():
    """Main test function"""
    print("🚀 SQL Analyzer Enterprise Backend Test")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    
    # Test endpoints
    endpoints = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/databases/supported", "Database Engines"),
        (f"{base_url}/export/formats", "Export Formats"),
        (f"{base_url}/metrics/dashboard", "Dashboard Metrics"),
        (f"{base_url}/metrics", "System Metrics")
    ]
    
    results = []
    
    for url, description in endpoints:
        success, data = test_endpoint(url, description)
        results.append((description, success, data))
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for description, success, data in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Backend is fully functional.")
        return 0
    else:
        print("⚠️  Some tests failed. Check server status.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
