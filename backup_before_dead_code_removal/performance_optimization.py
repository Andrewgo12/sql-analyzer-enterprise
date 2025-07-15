#!/usr/bin/env python3
"""
Performance Optimization Analysis
Identify bottlenecks and optimize system performance for enterprise workloads
"""

import time
import psutil
import json
import requests
import threading
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyze and optimize system performance"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.analysis_results = {
            'system_performance': {},
            'api_performance': {},
            'code_performance': {},
            'bottlenecks': [],
            'optimization_recommendations': []
        }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        print("⚡ PERFORMANCE OPTIMIZATION ANALYSIS")
        print("=" * 50)
        
        # System performance baseline
        self._analyze_system_performance()
        
        # API performance testing
        self._analyze_api_performance()
        
        # Code performance analysis
        self._analyze_code_performance()
        
        # Identify bottlenecks
        self._identify_bottlenecks()
        
        # Generate optimization recommendations
        self._generate_optimization_recommendations()
        
        return self.analysis_results
    
    def _analyze_system_performance(self):
        """Analyze system resource usage"""
        print("🖥️ Analyzing system performance...")
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        system_metrics = {
            'cpu_usage': cpu_percent,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent,
            'disk_total': disk.total,
            'disk_free': disk.free,
            'disk_percent': disk.percent,
            'network_bytes_sent': network.bytes_sent,
            'network_bytes_recv': network.bytes_recv,
            'process_memory_rss': process_memory.rss,
            'process_memory_vms': process_memory.vms
        }
        
        # Performance assessment
        performance_issues = []
        
        if cpu_percent > 80:
            performance_issues.append({
                'type': 'high_cpu',
                'severity': 'high',
                'value': cpu_percent,
                'recommendation': 'Optimize CPU-intensive operations'
            })
        
        if memory.percent > 85:
            performance_issues.append({
                'type': 'high_memory',
                'severity': 'high',
                'value': memory.percent,
                'recommendation': 'Optimize memory usage and implement caching'
            })
        
        if disk.percent > 90:
            performance_issues.append({
                'type': 'low_disk_space',
                'severity': 'medium',
                'value': disk.percent,
                'recommendation': 'Clean up temporary files and logs'
            })
        
        self.analysis_results['system_performance'] = {
            'metrics': system_metrics,
            'issues': performance_issues,
            'overall_health': 'good' if not performance_issues else 'needs_attention'
        }
        
        print(f"✅ System metrics: CPU {cpu_percent}%, Memory {memory.percent}%, Disk {disk.percent}%")
    
    def _analyze_api_performance(self):
        """Analyze API endpoint performance"""
        print("🌐 Analyzing API performance...")
        
        # Test endpoints with timing
        endpoints = [
            ("/api/health", "GET"),
            ("/api/databases/supported", "GET"),
            ("/api/export/formats", "GET"),
            ("/api/metrics/dashboard", "GET")
        ]
        
        endpoint_performance = {}
        
        for endpoint, method in endpoints:
            try:
                # Warm-up request
                requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                # Performance test
                times = []
                for _ in range(5):
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    endpoint_performance[endpoint] = {
                        'avg_response_time': avg_time,
                        'min_response_time': min_time,
                        'max_response_time': max_time,
                        'successful_requests': len(times),
                        'performance_grade': self._grade_response_time(avg_time)
                    }
                    
                    print(f"✅ {endpoint}: {avg_time:.3f}s avg ({self._grade_response_time(avg_time)})")
                else:
                    endpoint_performance[endpoint] = {
                        'error': 'No successful requests',
                        'performance_grade': 'F'
                    }
                    print(f"❌ {endpoint}: Failed")
            
            except Exception as e:
                endpoint_performance[endpoint] = {
                    'error': str(e),
                    'performance_grade': 'F'
                }
                print(f"❌ {endpoint}: {str(e)[:50]}...")
        
        # Load testing
        self._perform_load_test(endpoint_performance)
        
        self.analysis_results['api_performance'] = endpoint_performance
    
    def _grade_response_time(self, response_time: float) -> str:
        """Grade response time performance"""
        if response_time < 0.1:
            return 'A+'
        elif response_time < 0.2:
            return 'A'
        elif response_time < 0.5:
            return 'B'
        elif response_time < 1.0:
            return 'C'
        elif response_time < 2.0:
            return 'D'
        else:
            return 'F'
    
    def _perform_load_test(self, endpoint_performance: Dict[str, Any]):
        """Perform basic load testing"""
        print("🔄 Performing load test...")
        
        # Test with concurrent requests
        test_endpoint = "/api/health"
        concurrent_requests = 10
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{test_endpoint}", timeout=5)
                end_time = time.time()
                return {
                    'success': response.status_code == 200,
                    'response_time': end_time - start_time
                }
            except:
                return {'success': False, 'response_time': 5.0}
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_requests)]
            results = [future.result() for future in as_completed(futures)]
        end_time = time.time()
        
        # Analyze results
        successful_requests = sum(1 for r in results if r['success'])
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        total_time = end_time - start_time
        requests_per_second = concurrent_requests / total_time
        
        load_test_results = {
            'concurrent_requests': concurrent_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / concurrent_requests * 100,
            'avg_response_time': avg_response_time,
            'requests_per_second': requests_per_second,
            'total_time': total_time
        }
        
        endpoint_performance['load_test'] = load_test_results
        print(f"✅ Load test: {successful_requests}/{concurrent_requests} success, {requests_per_second:.1f} req/s")
    
    def _analyze_code_performance(self):
        """Analyze code performance patterns"""
        print("📊 Analyzing code performance...")
        
        performance_issues = []
        
        # Analyze Python files for performance anti-patterns
        python_files = list(Path(".").rglob("*.py"))
        
        for py_file in python_files[:20]:  # Analyze first 20 files
            if any(exclude in str(py_file) for exclude in ['__pycache__', '.venv', 'node_modules']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for performance anti-patterns
                issues = self._check_performance_patterns(str(py_file), content)
                performance_issues.extend(issues)
            
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        # Categorize issues by severity
        high_priority = [i for i in performance_issues if i.get('severity') == 'high']
        medium_priority = [i for i in performance_issues if i.get('severity') == 'medium']
        low_priority = [i for i in performance_issues if i.get('severity') == 'low']
        
        self.analysis_results['code_performance'] = {
            'total_issues': len(performance_issues),
            'high_priority_issues': len(high_priority),
            'medium_priority_issues': len(medium_priority),
            'low_priority_issues': len(low_priority),
            'issues': performance_issues[:10],  # Top 10 issues
            'performance_score': max(0, 100 - len(performance_issues) * 2)
        }
        
        print(f"✅ Code analysis: {len(performance_issues)} performance issues found")
    
    def _check_performance_patterns(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for performance anti-patterns in code"""
        issues = []
        
        # Check for synchronous operations
        if 'requests.get' in content and 'async' not in content:
            issues.append({
                'file': file_path,
                'type': 'synchronous_http',
                'severity': 'medium',
                'description': 'Synchronous HTTP requests detected',
                'recommendation': 'Use async/await with aiohttp for better performance'
            })
        
        # Check for inefficient loops
        if content.count('for') > 3 and '+=' in content:
            issues.append({
                'file': file_path,
                'type': 'inefficient_loops',
                'severity': 'medium',
                'description': 'Potentially inefficient loops with string concatenation',
                'recommendation': 'Use join() or list comprehensions'
            })
        
        # Check for database queries in loops
        if 'for' in content and any(db_term in content for db_term in ['query', 'execute', 'cursor']):
            issues.append({
                'file': file_path,
                'type': 'db_queries_in_loop',
                'severity': 'high',
                'description': 'Database queries inside loops',
                'recommendation': 'Batch queries or use bulk operations'
            })
        
        # Check for large file operations
        if 'read()' in content and 'with open' in content:
            issues.append({
                'file': file_path,
                'type': 'large_file_read',
                'severity': 'low',
                'description': 'Reading entire file into memory',
                'recommendation': 'Consider streaming for large files'
            })
        
        # Check for inefficient data structures
        if content.count('.append(') > 10:
            issues.append({
                'file': file_path,
                'type': 'inefficient_append',
                'severity': 'low',
                'description': 'Multiple append operations',
                'recommendation': 'Pre-allocate list size or use list comprehension'
            })
        
        return issues
    
    def _identify_bottlenecks(self):
        """Identify system bottlenecks"""
        print("🔍 Identifying bottlenecks...")
        
        bottlenecks = []
        
        # System bottlenecks
        system_perf = self.analysis_results.get('system_performance', {})
        for issue in system_perf.get('issues', []):
            bottlenecks.append({
                'category': 'system',
                'type': issue['type'],
                'severity': issue['severity'],
                'impact': 'high',
                'description': f"System {issue['type']}: {issue['value']}%",
                'recommendation': issue['recommendation']
            })
        
        # API bottlenecks
        api_perf = self.analysis_results.get('api_performance', {})
        for endpoint, data in api_perf.items():
            if isinstance(data, dict) and data.get('performance_grade', 'A') in ['D', 'F']:
                bottlenecks.append({
                    'category': 'api',
                    'type': 'slow_endpoint',
                    'severity': 'medium',
                    'impact': 'medium',
                    'description': f"Slow API endpoint: {endpoint}",
                    'recommendation': 'Optimize endpoint logic and add caching'
                })
        
        # Code bottlenecks
        code_perf = self.analysis_results.get('code_performance', {})
        high_priority_issues = code_perf.get('high_priority_issues', 0)
        if high_priority_issues > 0:
            bottlenecks.append({
                'category': 'code',
                'type': 'performance_anti_patterns',
                'severity': 'high',
                'impact': 'high',
                'description': f"{high_priority_issues} high-priority code performance issues",
                'recommendation': 'Refactor code to eliminate performance anti-patterns'
            })
        
        self.analysis_results['bottlenecks'] = bottlenecks
        print(f"✅ Bottlenecks identified: {len(bottlenecks)} issues")
    
    def _generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        print("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # High-impact optimizations
        if self.analysis_results['bottlenecks']:
            high_severity_bottlenecks = [b for b in self.analysis_results['bottlenecks'] if b['severity'] == 'high']
            if high_severity_bottlenecks:
                recommendations.append({
                    'category': 'Critical Performance',
                    'priority': 'HIGH',
                    'impact': 'Very High',
                    'effort': 'Medium',
                    'title': 'Fix Critical Performance Bottlenecks',
                    'description': f'Address {len(high_severity_bottlenecks)} critical performance issues',
                    'actions': [b['recommendation'] for b in high_severity_bottlenecks[:3]],
                    'expected_improvement': '30-50% performance gain'
                })
        
        # API optimizations
        api_perf = self.analysis_results.get('api_performance', {})
        slow_endpoints = [ep for ep, data in api_perf.items() 
                         if isinstance(data, dict) and data.get('avg_response_time', 0) > 1.0]
        if slow_endpoints:
            recommendations.append({
                'category': 'API Performance',
                'priority': 'HIGH',
                'impact': 'High',
                'effort': 'Medium',
                'title': 'Optimize Slow API Endpoints',
                'description': f'Optimize {len(slow_endpoints)} slow API endpoints',
                'actions': [
                    'Implement response caching',
                    'Optimize database queries',
                    'Add request/response compression',
                    'Implement connection pooling'
                ],
                'expected_improvement': '50-70% faster API responses'
            })
        
        # Code optimizations
        code_perf = self.analysis_results.get('code_performance', {})
        if code_perf.get('performance_score', 100) < 80:
            recommendations.append({
                'category': 'Code Optimization',
                'priority': 'MEDIUM',
                'impact': 'Medium',
                'effort': 'High',
                'title': 'Optimize Code Performance Patterns',
                'description': 'Refactor code to eliminate performance anti-patterns',
                'actions': [
                    'Convert synchronous operations to async',
                    'Optimize loops and data structures',
                    'Implement efficient caching strategies',
                    'Batch database operations'
                ],
                'expected_improvement': '20-40% overall performance gain'
            })
        
        # System optimizations
        system_perf = self.analysis_results.get('system_performance', {})
        if system_perf.get('overall_health') == 'needs_attention':
            recommendations.append({
                'category': 'System Optimization',
                'priority': 'MEDIUM',
                'impact': 'Medium',
                'effort': 'Low',
                'title': 'Optimize System Resources',
                'description': 'Improve system resource utilization',
                'actions': [
                    'Implement memory management strategies',
                    'Optimize CPU-intensive operations',
                    'Clean up disk space and logs',
                    'Configure system monitoring'
                ],
                'expected_improvement': '15-25% better resource utilization'
            })
        
        self.analysis_results['optimization_recommendations'] = recommendations
        print(f"✅ Generated {len(recommendations)} optimization recommendations")

def main():
    """Run performance optimization analysis"""
    analyzer = PerformanceAnalyzer()
    results = analyzer.analyze_performance()
    
    # Save results
    with open('performance_optimization.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE OPTIMIZATION SUMMARY")
    print("=" * 50)
    
    system_perf = results.get('system_performance', {})
    print(f"\n🖥️ SYSTEM PERFORMANCE:")
    if 'metrics' in system_perf:
        metrics = system_perf['metrics']
        print(f"  • CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
        print(f"  • Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
        print(f"  • Disk Usage: {metrics.get('disk_percent', 0):.1f}%")
    
    api_perf = results.get('api_performance', {})
    working_endpoints = sum(1 for data in api_perf.values() 
                           if isinstance(data, dict) and 'avg_response_time' in data)
    print(f"\n🌐 API PERFORMANCE:")
    print(f"  • Working endpoints: {working_endpoints}")
    
    code_perf = results.get('code_performance', {})
    print(f"\n📊 CODE PERFORMANCE:")
    print(f"  • Performance issues: {code_perf.get('total_issues', 0)}")
    print(f"  • Performance score: {code_perf.get('performance_score', 0):.1f}%")
    
    bottlenecks = results.get('bottlenecks', [])
    print(f"\n🔍 BOTTLENECKS: {len(bottlenecks)} identified")
    for bottleneck in bottlenecks[:3]:
        print(f"  • {bottleneck['category']}: {bottleneck['description']}")
    
    recommendations = results.get('optimization_recommendations', [])
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS: {len(recommendations)}")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['title']} ({rec['priority']} priority)")
        print(f"     Expected improvement: {rec.get('expected_improvement', 'Significant')}")
    
    print(f"\n✅ Analysis complete! Detailed results saved to performance_optimization.json")

if __name__ == '__main__':
    main()
