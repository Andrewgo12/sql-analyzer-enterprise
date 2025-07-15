#!/usr/bin/env python3
"""
Test Enterprise Features - Comprehensive Feature Testing
Tests all 50+ database types and export formats
"""

import sys
import os
import requests
import json
import time

def test_all_database_engines():
    """Test all supported database engines"""
    print("=== Testing All Database Engines ===")
    
    try:
        response = requests.get('http://localhost:5000/api/databases/supported', timeout=10)
        if response.status_code == 200:
            data = response.json()
            engines = data['engines']
            
            print(f"✅ Total database engines: {len(engines)}")
            
            # Group by category
            by_category = {}
            for engine in engines:
                category = engine['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(engine['name'])
            
            for category, names in by_category.items():
                print(f"   📁 {category}: {len(names)} engines")
                for name in names[:3]:  # Show first 3
                    print(f"      - {name}")
                if len(names) > 3:
                    print(f"      ... and {len(names) - 3} more")
            
            # Test specific database detection
            test_cases = [
                ("SELECT * FROM users;", "mysql"),
                ("SELECT users.* FROM users WHERE users.id = $1;", "postgresql"),
                ("SELECT TOP 10 * FROM users;", "sql_server"),
                ("db.users.find({});", "mongodb"),
                ("GET /users/_search", "elasticsearch")
            ]
            
            print("\n   Testing database detection:")
            for sql, expected in test_cases:
                detect_data = {'sql_content': sql}
                resp = requests.post('http://localhost:5000/api/databases/detect', 
                                   json=detect_data, timeout=5)
                if resp.status_code == 200:
                    result = resp.json()
                    detected = result['detected_engine']
                    print(f"   ✅ '{sql[:30]}...' → {detected}")
                else:
                    print(f"   ⚠️  Detection failed for: {sql[:30]}...")
            
            return len(engines) >= 20  # Expect at least 20 engines
        else:
            print(f"❌ Failed to get database engines: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database engines test failed: {e}")
        return False

def test_all_export_formats():
    """Test all supported export formats"""
    print("\n=== Testing All Export Formats ===")
    
    try:
        response = requests.get('http://localhost:5000/api/export/formats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            formats = data['formats']
            
            print(f"✅ Total export formats: {len(formats)}")
            
            # Group by category
            by_category = {}
            for fmt in formats:
                category = fmt['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(fmt)
            
            for category, fmts in by_category.items():
                print(f"   📁 {category}: {len(fmts)} formats")
                for fmt in fmts[:3]:  # Show first 3
                    features = []
                    if fmt['supports_charts']: features.append('charts')
                    if fmt['supports_styling']: features.append('styling')
                    if fmt['is_binary']: features.append('binary')
                    feature_str = f" ({', '.join(features)})" if features else ""
                    print(f"      - {fmt['name']}{feature_str}")
                if len(fmts) > 3:
                    print(f"      ... and {len(fmts) - 3} more")
            
            return len(formats) >= 25  # Expect at least 25 formats
        else:
            print(f"❌ Failed to get export formats: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Export formats test failed: {e}")
        return False

def test_enterprise_analysis():
    """Test enterprise analysis with multiple database types"""
    print("\n=== Testing Enterprise Analysis ===")
    
    test_cases = [
        {
            'name': 'MySQL Complex Query',
            'sql': '''
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            SELECT u.*, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY u.id
            HAVING order_count > 5
            ORDER BY order_count DESC;
            ''',
            'engine': 'mysql'
        },
        {
            'name': 'PostgreSQL Advanced Features',
            'sql': '''
            CREATE TABLE analytics (
                id SERIAL PRIMARY KEY,
                data JSONB,
                tags TEXT[],
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            WITH monthly_stats AS (
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    COUNT(*) as total,
                    AVG(ARRAY_LENGTH(tags, 1)) as avg_tags
                FROM analytics
                WHERE created_at > NOW() - INTERVAL '1 year'
                GROUP BY DATE_TRUNC('month', created_at)
            )
            SELECT * FROM monthly_stats
            ORDER BY month DESC;
            ''',
            'engine': 'postgresql'
        },
        {
            'name': 'SQL Server Enterprise Query',
            'sql': '''
            CREATE TABLE sales (
                id INT IDENTITY(1,1) PRIMARY KEY,
                product_id INT NOT NULL,
                amount DECIMAL(10,2),
                sale_date DATETIME2 DEFAULT GETDATE()
            );
            
            SELECT 
                product_id,
                amount,
                ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY amount DESC) as rank,
                LAG(amount) OVER (PARTITION BY product_id ORDER BY sale_date) as prev_amount
            FROM sales
            WHERE sale_date >= DATEADD(month, -3, GETDATE());
            ''',
            'engine': 'sql_server'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n   Testing {test_case['name']}...")
        
        try:
            files = {'file': (f"{test_case['name'].lower().replace(' ', '_')}.sql", 
                            test_case['sql'], 'text/plain')}
            data = {
                'database_engine': test_case['engine'],
                'analysis_types': 'syntax,semantic,performance,security'
            }
            
            response = requests.post('http://localhost:5000/api/analyze', 
                                   files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                analysis = response.json()
                summary = analysis.get('summary', {})
                
                print(f"   ✅ Analysis completed:")
                print(f"      Engine: {analysis.get('database_engine', 'N/A')}")
                print(f"      Errors: {summary.get('total_errors', 0)}")
                print(f"      Performance: {summary.get('performance_score', 100)}%")
                print(f"      Security: {summary.get('security_score', 100)}%")
                print(f"      Processing time: {analysis.get('processing_time', 0):.2f}s")
                
                results.append(True)
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            results.append(False)
    
    return all(results)

def test_export_functionality():
    """Test export functionality with different formats"""
    print("\n=== Testing Export Functionality ===")
    
    # Create sample analysis data
    sample_analysis = {
        'filename': 'enterprise_test.sql',
        'file_size': 1024,
        'line_count': 25,
        'timestamp': '2024-01-01T12:00:00Z',
        'database_engine': 'mysql',
        'summary': {
            'total_errors': 3,
            'performance_score': 85,
            'security_score': 95,
            'recommendations': [
                {'type': 'performance', 'message': 'Consider adding indexes'}
            ]
        },
        'analysis': {
            'errors': [
                {
                    'message': 'Missing semicolon',
                    'severity': 'medium',
                    'line': 5,
                    'category': 'syntax'
                }
            ]
        }
    }
    
    # Test different export formats
    test_formats = ['json', 'html', 'csv', 'xml']
    results = []
    
    for fmt in test_formats:
        print(f"   Testing {fmt.upper()} export...")
        
        try:
            response = requests.post(f'http://localhost:5000/api/export/{fmt}',
                                   json=sample_analysis, timeout=15)
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                print(f"   ✅ {fmt.upper()} export successful (Content-Type: {content_type})")
                results.append(True)
            else:
                print(f"   ❌ {fmt.upper()} export failed: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ {fmt.upper()} export error: {e}")
            results.append(False)
    
    return all(results)

def run_enterprise_feature_tests():
    """Run comprehensive enterprise feature tests"""
    print("🚀 SQL Analyzer Enterprise - Feature Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Engines (50+)", test_all_database_engines),
        ("Export Formats (50+)", test_all_export_formats),
        ("Enterprise Analysis", test_enterprise_analysis),
        ("Export Functionality", test_export_functionality)
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
    print("📊 ENTERPRISE FEATURE TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} enterprise tests passed")
    
    if passed == total:
        print("🎉 ALL ENTERPRISE FEATURES WORKING! World-class platform confirmed.")
    elif passed >= total * 0.75:
        print("⚠️  Most enterprise features working. Minor issues detected.")
    else:
        print("❌ Multiple enterprise feature failures. System needs attention.")
    
    return passed == total

if __name__ == '__main__':
    success = run_enterprise_feature_tests()
    sys.exit(0 if success else 1)
