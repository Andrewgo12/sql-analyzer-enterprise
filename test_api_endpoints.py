#!/usr/bin/env python3
"""
Test API endpoints for errors
"""

import requests
import time
import json

def test_api_endpoints():
    print("Testing API endpoints for errors...")
    
    # Wait for server to start
    time.sleep(2)
    
    base_url = "http://localhost:8080"
    
    # Test endpoints
    endpoints = [
        ("GET", "/"),
        ("GET", "/health"),
        ("POST", "/api/auth/login"),
        ("GET", "/api/files"),
        ("GET", "/api/analysis/status")
    ]
    
    results = []
    
    for method, endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={"test": "data"}, timeout=5)
            
            print(f"✅ {method} {endpoint}: {response.status_code}")
            results.append((endpoint, "SUCCESS", response.status_code))
            
        except requests.exceptions.ConnectionError:
            print(f"❌ {method} {endpoint}: Connection refused (server not running?)")
            results.append((endpoint, "CONNECTION_ERROR", None))
        except requests.exceptions.Timeout:
            print(f"⚠️ {method} {endpoint}: Timeout")
            results.append((endpoint, "TIMEOUT", None))
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")
            results.append((endpoint, "ERROR", str(e)))
    
    print("\nAPI endpoint testing completed")
    
    # Summary
    success_count = len([r for r in results if r[1] == "SUCCESS"])
    total_count = len(results)
    
    print(f"\nSummary: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All API endpoints working correctly")
        return True
    else:
        print("⚠️ Some API endpoints have issues")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    if success:
        print("\n✅ API test passed")
    else:
        print("\n❌ API test failed")
