#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - TEST RUNNER
Comprehensive test execution script with reporting and CI/CD integration
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class TestRunner:
    """Comprehensive test runner for SQL Analyzer Enterprise."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_tests(self, test_type: str = "all", verbose: bool = False, coverage: bool = False):
        """Run specified tests with options."""
        self.start_time = time.time()
        
        print("🧪 SQL ANALYZER ENTERPRISE - TEST EXECUTION")
        print("=" * 60)
        print(f"Test Type: {test_type.upper()}")
        print(f"Verbose: {verbose}")
        print(f"Coverage: {coverage}")
        print("=" * 60)
        
        # Check if server is running
        if not self.check_server_status():
            print("⚠️  Server is not running. Starting server for tests...")
            if not self.start_test_server():
                print("❌ Failed to start server. Some tests may fail.")
        
        # Run tests based on type
        if test_type == "unit" or test_type == "all":
            self.run_unit_tests(verbose, coverage)
        
        if test_type == "integration" or test_type == "all":
            self.run_integration_tests(verbose)
        
        if test_type == "frontend" or test_type == "all":
            self.run_frontend_tests(verbose)
        
        if test_type == "performance" or test_type == "all":
            self.run_performance_tests(verbose)
        
        self.end_time = time.time()
        self.generate_final_report()
    
    def check_server_status(self) -> bool:
        """Check if the server is running."""
        try:
            import requests
            response = requests.get("http://localhost:8081/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_test_server(self) -> bool:
        """Start server for testing."""
        try:
            # Start server in background
            server_process = subprocess.Popen([
                sys.executable, "web_app/server.py"
            ], cwd=self.project_root)
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if server is now running
            return self.check_server_status()
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def run_unit_tests(self, verbose: bool = False, coverage: bool = False):
        """Run unit tests."""
        print("\n🔬 Running Unit Tests...")
        
        try:
            cmd = [sys.executable, "-m", "pytest", "tests/", "-v" if verbose else "-q"]
            
            if coverage:
                cmd.extend(["--cov=web_app", "--cov-report=html", "--cov-report=term"])
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            self.test_results['unit_tests'] = {
                'status': 'PASSED' if result.returncode == 0 else 'FAILED',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if result.returncode == 0:
                print("✅ Unit tests passed")
            else:
                print("❌ Unit tests failed")
                if verbose:
                    print(result.stdout)
                    print(result.stderr)
        
        except Exception as e:
            print(f"❌ Error running unit tests: {e}")
            self.test_results['unit_tests'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def run_integration_tests(self, verbose: bool = False):
        """Run integration tests."""
        print("\n🔗 Running Integration Tests...")
        
        try:
            cmd = [sys.executable, "tests/test_framework.py", "--integration"]
            
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            
            self.test_results['integration_tests'] = {
                'status': 'PASSED' if result.returncode == 0 else 'FAILED',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if result.returncode == 0:
                print("✅ Integration tests passed")
            else:
                print("❌ Integration tests failed")
                if verbose:
                    print(result.stdout)
                    print(result.stderr)
        
        except Exception as e:
            print(f"❌ Error running integration tests: {e}")
            self.test_results['integration_tests'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def run_frontend_tests(self, verbose: bool = False):
        """Run frontend tests."""
        print("\n🌐 Running Frontend Tests...")
        
        # Check if frontend test files exist
        frontend_test_dir = self.project_root / "web_app" / "static" / "js" / "tests"
        
        if not frontend_test_dir.exists():
            print("⏭️  Frontend tests not found, skipping...")
            self.test_results['frontend_tests'] = {
                'status': 'SKIPPED',
                'reason': 'No frontend test files found'
            }
            return
        
        try:
            # Run JavaScript tests (if Jest or similar is configured)
            # For now, we'll run a basic validation
            js_files = list((self.project_root / "web_app" / "static" / "js").glob("*.js"))
            
            validation_passed = True
            validation_errors = []
            
            for js_file in js_files:
                # Basic syntax validation
                try:
                    with open(js_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check for basic syntax issues
                        if content.count('{') != content.count('}'):
                            validation_errors.append(f"{js_file.name}: Mismatched braces")
                            validation_passed = False
                        if content.count('(') != content.count(')'):
                            validation_errors.append(f"{js_file.name}: Mismatched parentheses")
                            validation_passed = False
                except Exception as e:
                    validation_errors.append(f"{js_file.name}: {str(e)}")
                    validation_passed = False
            
            self.test_results['frontend_tests'] = {
                'status': 'PASSED' if validation_passed else 'FAILED',
                'files_checked': len(js_files),
                'errors': validation_errors
            }
            
            if validation_passed:
                print(f"✅ Frontend validation passed ({len(js_files)} files checked)")
            else:
                print(f"❌ Frontend validation failed ({len(validation_errors)} errors)")
                if verbose:
                    for error in validation_errors:
                        print(f"  - {error}")
        
        except Exception as e:
            print(f"❌ Error running frontend tests: {e}")
            self.test_results['frontend_tests'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def run_performance_tests(self, verbose: bool = False):
        """Run performance tests."""
        print("\n⚡ Running Performance Tests...")
        
        try:
            import requests
            import time
            
            # Test response times
            endpoints = [
                "/",
                "/dashboard",
                "/upload",
                "/history"
            ]
            
            performance_results = []
            
            for endpoint in endpoints:
                start_time = time.time()
                try:
                    response = requests.get(f"http://localhost:8081{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    performance_results.append({
                        'endpoint': endpoint,
                        'response_time': response_time,
                        'status_code': response.status_code,
                        'passed': response_time < 2.0  # 2 second threshold
                    })
                    
                except Exception as e:
                    performance_results.append({
                        'endpoint': endpoint,
                        'error': str(e),
                        'passed': False
                    })
            
            passed_tests = len([r for r in performance_results if r.get('passed', False)])
            total_tests = len(performance_results)
            
            self.test_results['performance_tests'] = {
                'status': 'PASSED' if passed_tests == total_tests else 'FAILED',
                'passed': passed_tests,
                'total': total_tests,
                'results': performance_results
            }
            
            if passed_tests == total_tests:
                print(f"✅ Performance tests passed ({passed_tests}/{total_tests})")
            else:
                print(f"❌ Performance tests failed ({passed_tests}/{total_tests})")
                if verbose:
                    for result in performance_results:
                        if not result.get('passed', False):
                            print(f"  - {result['endpoint']}: {result.get('error', 'Slow response')}")
        
        except Exception as e:
            print(f"❌ Error running performance tests: {e}")
            self.test_results['performance_tests'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def generate_final_report(self):
        """Generate final test report."""
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print("\n" + "=" * 60)
        print("📊 FINAL TEST REPORT")
        print("=" * 60)
        print(f"Total Duration: {duration:.2f} seconds")
        print()
        
        overall_status = "PASSED"
        
        for test_category, results in self.test_results.items():
            status = results.get('status', 'UNKNOWN')
            status_icon = "✅" if status == 'PASSED' else "❌" if status == 'FAILED' else "⏭️" if status == 'SKIPPED' else "❓"
            
            print(f"{status_icon} {test_category.replace('_', ' ').title()}: {status}")
            
            if status == 'FAILED' or status == 'ERROR':
                overall_status = "FAILED"
        
        print()
        print(f"🎯 Overall Status: {overall_status}")
        print("=" * 60)
        
        # Save detailed report
        report_file = self.project_root / "test_results.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'duration': duration,
                'overall_status': overall_status,
                'results': self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if overall_status == "PASSED" else 1)

def main():
    parser = argparse.ArgumentParser(description='SQL Analyzer Enterprise Test Runner')
    parser.add_argument('--type', choices=['unit', 'integration', 'frontend', 'performance', 'all'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate coverage report')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    runner.run_tests(args.type, args.verbose, args.coverage)

if __name__ == "__main__":
    main()
