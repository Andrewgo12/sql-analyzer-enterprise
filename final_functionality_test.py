#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Final Functionality Test
Test all critical functionality after Memory icon fixes
"""

import requests
import time
import tempfile
import os
from datetime import datetime

def test_backend_endpoints():
    """Test all critical backend endpoints"""
    print("🔧 Testing Backend Endpoints")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    endpoints = [
        ('/api/health', 'Health Check'),
        ('/api/databases/supported', 'Database Engines'),
        ('/api/export/formats', 'Export Formats'),
        ('/api/metrics', 'System Metrics'),
        ('/api/metrics/dashboard', 'Dashboard Metrics')
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: OK ({len(str(data))} bytes)")
                results.append(True)
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            results.append(False)
    
    return all(results)

def test_sql_analysis():
    """Test SQL analysis functionality"""
    print("\n🔍 Testing SQL Analysis")
    print("-" * 40)
    
    # Create test SQL file
    test_sql = """
    SELECT u.id, u.name, u.email, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.active = 1
    GROUP BY u.id, u.name, u.email
    HAVING COUNT(o.id) > 5
    ORDER BY order_count DESC
    LIMIT 100;
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write(test_sql)
            temp_file_path = temp_file.name
        
        start_time = time.time()
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_query.sql', f, 'text/plain')}
            data = {'database_engine': 'mysql'}
            
            response = requests.post("http://localhost:5000/api/analyze",
                                   files=files, data=data, timeout=30)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Check required fields
            required_fields = ['summary', 'analysis', 'metadata']
            has_all_fields = all(field in result for field in required_fields)
            
            if has_all_fields:
                analysis_time = result.get('metadata', {}).get('analysis_time', response_time)
                print(f"✅ SQL Analysis: OK ({response_time:.3f}s total, {analysis_time:.3f}s analysis)")
                
                # Check performance
                if analysis_time < 2.0:
                    print(f"✅ Performance: Excellent (<2s target)")
                else:
                    print(f"⚠️ Performance: Acceptable but slow ({analysis_time:.3f}s)")
                
                return True
            else:
                missing = [f for f in required_fields if f not in result]
                print(f"❌ SQL Analysis: Missing fields {missing}")
                return False
        else:
            print(f"❌ SQL Analysis: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SQL Analysis: {str(e)}")
        return False
    finally:
        if 'temp_file_path' in locals():
            os.unlink(temp_file_path)

def test_export_functionality():
    """Test export functionality"""
    print("\n📤 Testing Export Functionality")
    print("-" * 40)
    
    try:
        # Get available formats
        response = requests.get("http://localhost:5000/api/export/formats", timeout=10)
        if response.status_code != 200:
            print(f"❌ Export Formats: HTTP {response.status_code}")
            return False
        
        formats_data = response.json()
        formats = formats_data.get('formats', [])
        
        if len(formats) >= 10:
            print(f"✅ Export Formats: {len(formats)} formats available")
        else:
            print(f"⚠️ Export Formats: Only {len(formats)} formats (expected ≥10)")
        
        # Test JSON export
        sample_data = {
            'summary': {'total_errors': 0, 'performance_score': 85},
            'analysis': {'syntax_valid': True},
            'metadata': {'analysis_time': 1.2}
        }
        
        export_response = requests.post("http://localhost:5000/api/export/json",
                                      json=sample_data, timeout=15)
        
        if export_response.status_code == 200:
            print("✅ JSON Export: OK")
            return True
        else:
            print(f"❌ JSON Export: HTTP {export_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Export Functionality: {str(e)}")
        return False

def test_frontend_accessibility():
    """Test frontend accessibility"""
    print("\n🌐 Testing Frontend Accessibility")
    print("-" * 40)
    
    try:
        # Test if frontend is accessible
        response = requests.get("http://localhost:3000", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for basic HTML structure
            has_html = '<html' in content
            has_react_root = 'id="root"' in content or 'id="app"' in content
            has_title = '<title>' in content
            
            if has_html and (has_react_root or 'React' in content) and has_title:
                print("✅ Frontend: Accessible and properly structured")
                return True
            else:
                print("⚠️ Frontend: Accessible but structure issues detected")
                return False
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend: {str(e)}")
        return False

def main():
    print("🚀 SQL Analyzer Enterprise - Final Functionality Test")
    print("=" * 70)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Backend Endpoints", test_backend_endpoints),
        ("SQL Analysis", test_sql_analysis),
        ("Export Functionality", test_export_functionality),
        ("Frontend Accessibility", test_frontend_accessibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name}: Test failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL FUNCTIONALITY TEST SUMMARY")
    print("=" * 70)
    
    passed_tests = sum(results)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 100:
        print("🎉 PERFECT: All functionality tests passed!")
        print("🚀 SQL Analyzer Enterprise is fully operational!")
    elif success_rate >= 75:
        print("✅ GOOD: Most functionality is working correctly")
        print("🔧 Minor issues may need attention")
    else:
        print("❌ CRITICAL: Major functionality issues detected")
        print("🛠️ Immediate attention required")
    
    # Final status
    print(f"\n📍 Application Status:")
    print(f"   🔧 Backend: http://localhost:5000")
    print(f"   🌐 Frontend: http://localhost:3000")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
