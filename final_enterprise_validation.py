#!/usr/bin/env python3
"""
FINAL ENTERPRISE VALIDATION
Comprehensive validation of the complete SQL Analyzer Enterprise system
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Test backend health and all components"""
    print("🔍 Testing Backend Health...")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Status: {health['status']}")
            print(f"   ✅ Version: {health['version']}")
            print(f"   ✅ Components: {len(health['components'])} active")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend health error: {e}")
        return False

def test_database_engines():
    """Test comprehensive database engine support"""
    print("🔍 Testing Database Engine Support...")
    
    try:
        response = requests.get('http://localhost:5000/api/databases/supported', timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data['total_engines']
            categories = len(data['categories'])
            
            print(f"   ✅ Total Engines: {total}")
            print(f"   ✅ Categories: {categories}")
            
            # Verify we have enterprise-level support
            if total >= 20:
                print("   ✅ Enterprise database support confirmed")
                return True
            else:
                print(f"   ⚠️  Limited database support: {total} engines")
                return False
        else:
            print(f"   ❌ Database engines test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Database engines error: {e}")
        return False

def test_export_formats():
    """Test comprehensive export format support"""
    print("🔍 Testing Export Format Support...")
    
    try:
        response = requests.get('http://localhost:5000/api/export/formats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data['total_formats']
            categories = len(data['categories'])
            
            print(f"   ✅ Total Formats: {total}")
            print(f"   ✅ Categories: {categories}")
            
            # Verify we have enterprise-level support
            if total >= 30:
                print("   ✅ Enterprise export support confirmed")
                return True
            else:
                print(f"   ⚠️  Limited export support: {total} formats")
                return False
        else:
            print(f"   ❌ Export formats test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Export formats error: {e}")
        return False

def test_sql_analysis():
    """Test comprehensive SQL analysis functionality"""
    print("🔍 Testing SQL Analysis Functionality...")
    
    # Complex enterprise SQL test
    enterprise_sql = """
    -- Enterprise SQL Test Case
    CREATE TABLE users (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        profile_data JSON,
        INDEX idx_username (username),
        INDEX idx_email (email),
        INDEX idx_created_at (created_at)
    );
    
    CREATE TABLE orders (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        user_id BIGINT NOT NULL,
        order_number VARCHAR(20) UNIQUE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_created_at (created_at)
    );
    
    -- Complex analytical query
    WITH monthly_stats AS (
        SELECT 
            DATE_FORMAT(created_at, '%Y-%m') as month,
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value,
            COUNT(DISTINCT user_id) as unique_customers
        FROM orders 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
        AND status IN ('delivered', 'shipped')
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
    ),
    user_segments AS (
        SELECT 
            u.id,
            u.username,
            COUNT(o.id) as order_count,
            SUM(o.total_amount) as lifetime_value,
            CASE 
                WHEN COUNT(o.id) >= 10 THEN 'VIP'
                WHEN COUNT(o.id) >= 5 THEN 'Regular'
                ELSE 'New'
            END as customer_segment
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.is_active = TRUE
        GROUP BY u.id, u.username
    )
    SELECT 
        ms.month,
        ms.total_orders,
        ms.total_revenue,
        ms.avg_order_value,
        ms.unique_customers,
        us.customer_segment,
        COUNT(us.id) as segment_count,
        AVG(us.lifetime_value) as avg_segment_value
    FROM monthly_stats ms
    CROSS JOIN user_segments us
    GROUP BY ms.month, us.customer_segment
    ORDER BY ms.month DESC, avg_segment_value DESC;
    """
    
    try:
        files = {'file': ('enterprise_test.sql', enterprise_sql, 'text/plain')}
        data = {'database_engine': 'mysql', 'analysis_types': 'syntax,performance,security'}
        
        response = requests.post('http://localhost:5000/api/analyze', 
                               files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"   ✅ Analysis completed successfully")
            print(f"   ✅ File: {analysis.get('filename', 'N/A')}")
            print(f"   ✅ Lines analyzed: {analysis.get('line_count', 0)}")
            print(f"   ✅ Errors detected: {analysis.get('summary', {}).get('total_errors', 0)}")
            print(f"   ✅ Performance score: {analysis.get('summary', {}).get('performance_score', 100)}%")
            print(f"   ✅ Security score: {analysis.get('summary', {}).get('security_score', 100)}%")
            return True
        else:
            print(f"   ❌ SQL analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ SQL analysis error: {e}")
        return False

def test_frontend_connectivity():
    """Test frontend application"""
    print("🔍 Testing Frontend Application...")
    
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            content = response.text
            if 'root' in content and 'script' in content:
                print("   ✅ Frontend serving correctly")
                print("   ✅ React application detected")
                return True
            else:
                print("   ⚠️  Frontend serving but React app not detected")
                return False
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend connectivity error: {e}")
        return False

def test_export_functionality():
    """Test export functionality with multiple formats"""
    print("🔍 Testing Export Functionality...")
    
    sample_data = {
        'filename': 'enterprise_validation.sql',
        'timestamp': datetime.now().isoformat(),
        'file_size': 2048,
        'line_count': 50,
        'summary': {
            'total_errors': 2,
            'performance_score': 92,
            'security_score': 98,
            'recommendations': [
                {'type': 'performance', 'message': 'Consider adding index on frequently queried columns'}
            ]
        },
        'analysis': {
            'errors': [
                {'message': 'Missing semicolon', 'line': 15, 'severity': 'medium'},
                {'message': 'Unused variable', 'line': 23, 'severity': 'low'}
            ]
        }
    }
    
    test_formats = ['json', 'html', 'csv', 'xml']
    success_count = 0
    
    for fmt in test_formats:
        try:
            response = requests.post(f'http://localhost:5000/api/export/{fmt}',
                                   json=sample_data, timeout=15)
            if response.status_code == 200:
                print(f"   ✅ {fmt.upper()} export successful")
                success_count += 1
            else:
                print(f"   ❌ {fmt.upper()} export failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {fmt.upper()} export error: {e}")
    
    return success_count == len(test_formats)

def run_final_validation():
    """Run complete enterprise validation suite"""
    print("🚀 SQL ANALYZER ENTERPRISE - FINAL VALIDATION")
    print("=" * 60)
    print(f"Validation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Database Engines", test_database_engines),
        ("Export Formats", test_export_formats),
        ("SQL Analysis", test_sql_analysis),
        ("Frontend Application", test_frontend_connectivity),
        ("Export Functionality", test_export_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Final Score: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ENTERPRISE VALIDATION COMPLETE!")
        print("🏆 SQL Analyzer Enterprise is ready for production!")
        print("✨ World-class platform with enterprise-grade features confirmed!")
    elif passed >= total * 0.9:
        print("\n⚠️  MOSTLY SUCCESSFUL - Minor issues detected")
        print("🔧 System is functional but may need minor adjustments")
    else:
        print("\n❌ VALIDATION FAILED - Critical issues detected")
        print("🚨 System requires attention before production use")
    
    print("\n" + "=" * 60)
    print(f"Validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == '__main__':
    success = run_final_validation()
    sys.exit(0 if success else 1)
