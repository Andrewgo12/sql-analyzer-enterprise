#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Performance Optimization
Comprehensive performance testing and optimization
"""

import requests
import time
import psutil
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os

class PerformanceOptimizer:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.performance_data = []
        
    def measure_memory_usage(self):
        """Measure current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': memory_percent,
            'available': psutil.virtual_memory().available,
            'total': psutil.virtual_memory().total
        }
    
    def measure_cpu_usage(self, duration=1):
        """Measure CPU usage over a duration"""
        return psutil.cpu_percent(interval=duration)
    
    def test_analysis_performance(self, num_tests=10):
        """Test SQL analysis performance with multiple requests"""
        print(f"\n⚡ Testing Analysis Performance ({num_tests} tests)")
        print("=" * 60)
        
        # Sample SQL queries of different complexities
        test_queries = [
            # Simple query
            "SELECT * FROM users WHERE id = 1;",
            
            # Medium complexity
            """
            SELECT u.id, u.name, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.active = 1
            GROUP BY u.id, u.name
            ORDER BY order_count DESC;
            """,
            
            # Complex query
            """
            WITH monthly_sales AS (
                SELECT 
                    DATE_TRUNC('month', order_date) as month,
                    SUM(total_amount) as monthly_total,
                    COUNT(*) as order_count
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.status = 'completed'
                GROUP BY DATE_TRUNC('month', order_date)
            ),
            growth_rates AS (
                SELECT 
                    month,
                    monthly_total,
                    LAG(monthly_total) OVER (ORDER BY month) as prev_month,
                    (monthly_total - LAG(monthly_total) OVER (ORDER BY month)) / 
                    LAG(monthly_total) OVER (ORDER BY month) * 100 as growth_rate
                FROM monthly_sales
            )
            SELECT * FROM growth_rates WHERE growth_rate > 10;
            """
        ]
        
        response_times = []
        memory_usage = []
        cpu_usage = []
        
        for i in range(num_tests):
            query = test_queries[i % len(test_queries)]
            
            # Measure memory before request
            mem_before = self.measure_memory_usage()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                temp_file.write(query)
                temp_file_path = temp_file.name
            
            try:
                start_time = time.time()
                
                # Make request
                with open(temp_file_path, 'rb') as f:
                    files = {'file': (f'test_query_{i}.sql', f, 'text/plain')}
                    data = {'database_engine': 'mysql'}
                    
                    response = self.session.post(f"{self.base_url}/api/analyze", 
                                               files=files, data=data, timeout=30)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Measure memory after request
                mem_after = self.measure_memory_usage()
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    memory_usage.append(mem_after['percent'])
                    
                    # Get analysis time from response
                    try:
                        result = response.json()
                        analysis_time = result.get('metadata', {}).get('analysis_time', response_time)
                        print(f"Test {i+1:2d}: {response_time:.3f}s total, {analysis_time:.3f}s analysis, {mem_after['percent']:.1f}% memory")
                    except:
                        print(f"Test {i+1:2d}: {response_time:.3f}s total, {mem_after['percent']:.1f}% memory")
                else:
                    print(f"Test {i+1:2d}: FAILED - HTTP {response.status_code}")
                    
            finally:
                os.unlink(temp_file_path)
        
        # Calculate statistics
        if response_times:
            avg_response = statistics.mean(response_times)
            max_response = max(response_times)
            min_response = min(response_times)
            p95_response = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            
            avg_memory = statistics.mean(memory_usage)
            max_memory = max(memory_usage)
            
            print(f"\n📊 Performance Statistics:")
            print(f"   Response Time - Avg: {avg_response:.3f}s, Max: {max_response:.3f}s, Min: {min_response:.3f}s, P95: {p95_response:.3f}s")
            print(f"   Memory Usage  - Avg: {avg_memory:.1f}%, Max: {max_memory:.1f}%")
            
            # Check enterprise standards
            performance_ok = avg_response < 2.0
            memory_ok = max_memory < 70.0
            
            print(f"\n🎯 Enterprise Standards:")
            print(f"   ✅ Response Time: {avg_response:.3f}s (target: <2s)" if performance_ok else f"   ❌ Response Time: {avg_response:.3f}s (target: <2s)")
            print(f"   ✅ Memory Usage: {max_memory:.1f}% (target: <70%)" if memory_ok else f"   ❌ Memory Usage: {max_memory:.1f}% (target: <70%)")
            
            return {
                'performance_ok': performance_ok,
                'memory_ok': memory_ok,
                'avg_response_time': avg_response,
                'max_memory_usage': max_memory,
                'total_tests': len(response_times),
                'success_rate': len(response_times) / num_tests * 100
            }
        else:
            print("❌ No successful tests completed")
            return None
    
    def test_concurrent_performance(self, concurrent_users=5, requests_per_user=3):
        """Test performance under concurrent load"""
        print(f"\n🚀 Testing Concurrent Performance ({concurrent_users} users, {requests_per_user} requests each)")
        print("=" * 80)
        
        def user_simulation(user_id):
            """Simulate a user making multiple requests"""
            user_times = []
            
            for req_id in range(requests_per_user):
                query = f"SELECT * FROM users WHERE id = {user_id + req_id};"
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                    temp_file.write(query)
                    temp_file_path = temp_file.name
                
                try:
                    start_time = time.time()
                    
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (f'user_{user_id}_req_{req_id}.sql', f, 'text/plain')}
                        data = {'database_engine': 'mysql'}
                        
                        response = self.session.post(f"{self.base_url}/api/analyze", 
                                                   files=files, data=data, timeout=30)
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status_code == 200:
                        user_times.append(response_time)
                        print(f"User {user_id+1} Request {req_id+1}: {response_time:.3f}s")
                    else:
                        print(f"User {user_id+1} Request {req_id+1}: FAILED - HTTP {response.status_code}")
                        
                finally:
                    os.unlink(temp_file_path)
            
            return user_times
        
        # Run concurrent tests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_simulation, i) for i in range(concurrent_users)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        all_times = [time for user_times in results for time in user_times]
        total_requests = sum(len(user_times) for user_times in results)
        
        if all_times:
            avg_response = statistics.mean(all_times)
            max_response = max(all_times)
            throughput = total_requests / total_time
            
            print(f"\n📊 Concurrent Performance Results:")
            print(f"   Total Time: {total_time:.3f}s")
            print(f"   Total Requests: {total_requests}")
            print(f"   Successful Requests: {len(all_times)}")
            print(f"   Throughput: {throughput:.2f} requests/second")
            print(f"   Average Response Time: {avg_response:.3f}s")
            print(f"   Maximum Response Time: {max_response:.3f}s")
            
            # Check if system handles concurrent load well
            concurrent_ok = avg_response < 3.0 and throughput > 1.0
            
            print(f"\n🎯 Concurrent Load Standards:")
            print(f"   ✅ Concurrent Performance: Acceptable" if concurrent_ok else f"   ❌ Concurrent Performance: Needs optimization")
            
            return {
                'concurrent_ok': concurrent_ok,
                'throughput': throughput,
                'avg_response_time': avg_response,
                'max_response_time': max_response,
                'success_rate': len(all_times) / (concurrent_users * requests_per_user) * 100
            }
        else:
            print("❌ No successful concurrent requests")
            return None
    
    def test_memory_stability(self, duration_minutes=2):
        """Test memory stability over time"""
        print(f"\n🧠 Testing Memory Stability ({duration_minutes} minutes)")
        print("=" * 60)
        
        memory_readings = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Make requests continuously and monitor memory
        request_count = 0
        while time.time() < end_time:
            try:
                # Make a request
                query = f"SELECT * FROM test_table WHERE id = {request_count};"
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                    temp_file.write(query)
                    temp_file_path = temp_file.name
                
                try:
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (f'stability_test_{request_count}.sql', f, 'text/plain')}
                        data = {'database_engine': 'mysql'}
                        
                        response = self.session.post(f"{self.base_url}/api/analyze", 
                                                   files=files, data=data, timeout=10)
                    
                    # Measure memory
                    memory_info = self.measure_memory_usage()
                    memory_readings.append({
                        'timestamp': time.time(),
                        'memory_percent': memory_info['percent'],
                        'memory_rss': memory_info['rss'],
                        'request_count': request_count
                    })
                    
                    if request_count % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"   {elapsed:.0f}s: {request_count} requests, {memory_info['percent']:.1f}% memory")
                    
                    request_count += 1
                    
                finally:
                    os.unlink(temp_file_path)
                    
            except Exception as e:
                print(f"   Request {request_count} failed: {e}")
            
            time.sleep(0.1)  # Small delay between requests
        
        # Analyze memory stability
        if memory_readings:
            memory_values = [reading['memory_percent'] for reading in memory_readings]
            
            initial_memory = memory_values[0]
            final_memory = memory_values[-1]
            max_memory = max(memory_values)
            avg_memory = statistics.mean(memory_values)
            memory_growth = final_memory - initial_memory
            
            print(f"\n📊 Memory Stability Results:")
            print(f"   Total Requests: {request_count}")
            print(f"   Initial Memory: {initial_memory:.1f}%")
            print(f"   Final Memory: {final_memory:.1f}%")
            print(f"   Maximum Memory: {max_memory:.1f}%")
            print(f"   Average Memory: {avg_memory:.1f}%")
            print(f"   Memory Growth: {memory_growth:+.1f}%")
            
            # Check stability criteria
            stable_memory = abs(memory_growth) < 10.0 and max_memory < 80.0
            
            print(f"\n🎯 Memory Stability Standards:")
            print(f"   ✅ Memory Stable: Growth {memory_growth:+.1f}%" if stable_memory else f"   ❌ Memory Unstable: Growth {memory_growth:+.1f}%")
            
            return {
                'stable': stable_memory,
                'memory_growth': memory_growth,
                'max_memory': max_memory,
                'avg_memory': avg_memory,
                'total_requests': request_count
            }
        else:
            print("❌ No memory readings collected")
            return None
    
    def run_comprehensive_optimization(self):
        """Run all performance optimization tests"""
        print("🚀 SQL Analyzer Enterprise - Performance Optimization")
        print("=" * 70)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Testing URL: {self.base_url}")
        
        results = {}
        
        # Test 1: Basic Performance
        results['basic_performance'] = self.test_analysis_performance(15)
        
        # Test 2: Concurrent Performance
        results['concurrent_performance'] = self.test_concurrent_performance(3, 5)
        
        # Test 3: Memory Stability
        results['memory_stability'] = self.test_memory_stability(1)
        
        # Overall Assessment
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE OPTIMIZATION SUMMARY")
        print("=" * 70)
        
        all_tests_passed = True
        
        if results['basic_performance']:
            bp = results['basic_performance']
            print(f"✅ Basic Performance: {bp['avg_response_time']:.3f}s avg, {bp['max_memory_usage']:.1f}% max memory" if bp['performance_ok'] and bp['memory_ok'] else f"❌ Basic Performance: {bp['avg_response_time']:.3f}s avg, {bp['max_memory_usage']:.1f}% max memory")
            all_tests_passed &= bp['performance_ok'] and bp['memory_ok']
        
        if results['concurrent_performance']:
            cp = results['concurrent_performance']
            print(f"✅ Concurrent Performance: {cp['throughput']:.2f} req/s, {cp['avg_response_time']:.3f}s avg" if cp['concurrent_ok'] else f"❌ Concurrent Performance: {cp['throughput']:.2f} req/s, {cp['avg_response_time']:.3f}s avg")
            all_tests_passed &= cp['concurrent_ok']
        
        if results['memory_stability']:
            ms = results['memory_stability']
            print(f"✅ Memory Stability: {ms['memory_growth']:+.1f}% growth, {ms['max_memory']:.1f}% max" if ms['stable'] else f"❌ Memory Stability: {ms['memory_growth']:+.1f}% growth, {ms['max_memory']:.1f}% max")
            all_tests_passed &= ms['stable']
        
        print(f"\n🎯 Overall Performance: {'✅ EXCELLENT - Enterprise Ready!' if all_tests_passed else '⚠️ NEEDS OPTIMIZATION'}")
        
        return all_tests_passed

if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    success = optimizer.run_comprehensive_optimization()
