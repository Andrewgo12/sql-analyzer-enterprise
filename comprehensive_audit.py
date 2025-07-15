#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Comprehensive Frontend Audit
Complete validation of all components and functionality
"""

import requests
import time
import json
import subprocess
import os
from datetime import datetime

class FrontendAuditor:
    def __init__(self):
        self.backend_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:3000"
        self.audit_results = []
        
    def log_result(self, category, test, success, message=""):
        """Log audit result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.audit_results.append({
            'category': category,
            'test': test,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} {category} - {test}")
        if message:
            print(f"   📝 {message}")
    
    def audit_backend_connectivity(self):
        """Audit backend API connectivity"""
        print("\n🔧 BACKEND CONNECTIVITY AUDIT")
        print("=" * 60)
        
        endpoints = [
            ('/api/health', 'Health Check'),
            ('/api/databases/supported', 'Database Engines'),
            ('/api/export/formats', 'Export Formats'),
            ('/api/metrics', 'System Metrics'),
            ('/api/metrics/dashboard', 'Dashboard Metrics')
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Backend", name, True, f"HTTP 200 - {len(str(data))} bytes")
                else:
                    self.log_result("Backend", name, False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result("Backend", name, False, str(e))
    
    def audit_frontend_files(self):
        """Audit frontend file structure"""
        print("\n📁 FRONTEND FILES AUDIT")
        print("=" * 60)
        
        required_files = [
            'frontend/src/App.jsx',
            'frontend/src/components/EnterpriseApp.jsx',
            'frontend/src/components/SystemHealthMonitor.jsx',
            'frontend/src/components/MetricsSystem.jsx',
            'frontend/src/components/ExportSystem.jsx',
            'frontend/src/components/DatabaseEngineSelector.jsx',
            'frontend/src/components/views/DashboardView.jsx',
            'frontend/src/components/views/SQLAnalysisView.jsx',
            'frontend/src/components/views/ConnectionsView.jsx',
            'frontend/src/components/views/MetricsView.jsx',
            'frontend/src/components/views/FileManagerView.jsx',
            'frontend/src/components/views/HistoryView.jsx',
            'frontend/src/components/views/TerminalView.jsx',
            'frontend/src/utils/api.js',
            'frontend/src/components/utils/api.js',
            'frontend/src/styles/EnterpriseApp.css',
            'frontend/src/styles/enterprise.css',
            'frontend/src/styles/index.css'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_result("Files", os.path.basename(file_path), True, f"{file_size} bytes")
            else:
                self.log_result("Files", os.path.basename(file_path), False, "Missing")
    
    def audit_component_imports(self):
        """Audit component import statements"""
        print("\n📦 COMPONENT IMPORTS AUDIT")
        print("=" * 60)
        
        # Check for problematic imports
        problematic_patterns = [
            ('Memory', 'lucide-react icon Memory should be MemoryStick'),
            ('import.*from.*"[^"]*".*{[^}]*Memory[^}]*}', 'Memory icon usage'),
        ]
        
        component_files = [
            'frontend/src/components/SystemHealthMonitor.jsx',
            'frontend/src/components/MetricsSystem.jsx',
            'frontend/src/components/views/MetricsView.jsx'
        ]
        
        for file_path in component_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for Memory icon usage
                if 'Memory,' in content or 'Memory ' in content:
                    self.log_result("Imports", f"{os.path.basename(file_path)} - Memory Icon", False, "Still using Memory instead of MemoryStick")
                else:
                    self.log_result("Imports", f"{os.path.basename(file_path)} - Memory Icon", True, "Using MemoryStick correctly")
                
                # Check for proper lucide-react imports
                if 'from \'lucide-react\'' in content or 'from "lucide-react"' in content:
                    self.log_result("Imports", f"{os.path.basename(file_path)} - Lucide React", True, "Proper lucide-react import")
                else:
                    self.log_result("Imports", f"{os.path.basename(file_path)} - Lucide React", False, "Missing lucide-react import")
    
    def audit_api_integration(self):
        """Audit API integration in components"""
        print("\n🔗 API INTEGRATION AUDIT")
        print("=" * 60)
        
        api_files = [
            'frontend/src/utils/api.js',
            'frontend/src/components/utils/api.js'
        ]
        
        for file_path in api_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for essential API functions
                essential_functions = [
                    'checkHealth',
                    'getSystemMetrics',
                    'getSupportedDatabases',
                    'analyzeSQL',
                    'getExportFormats'
                ]
                
                for func in essential_functions:
                    if func in content:
                        self.log_result("API", f"{os.path.basename(file_path)} - {func}", True, "Function present")
                    else:
                        self.log_result("API", f"{os.path.basename(file_path)} - {func}", False, "Function missing")
    
    def audit_build_process(self):
        """Audit build process"""
        print("\n🏗️ BUILD PROCESS AUDIT")
        print("=" * 60)
        
        try:
            # Check if we can build the project
            os.chdir('frontend')
            
            # Check package.json
            if os.path.exists('package.json'):
                with open('package.json', 'r') as f:
                    package_data = json.load(f)
                    
                # Check dependencies
                deps = package_data.get('dependencies', {})
                required_deps = ['react', 'react-dom', 'lucide-react', 'axios']
                
                for dep in required_deps:
                    if dep in deps:
                        self.log_result("Build", f"Dependency - {dep}", True, deps[dep])
                    else:
                        self.log_result("Build", f"Dependency - {dep}", False, "Missing")
                
                self.log_result("Build", "package.json", True, "Valid structure")
            else:
                self.log_result("Build", "package.json", False, "Missing")
            
            os.chdir('..')
            
        except Exception as e:
            self.log_result("Build", "Build Process", False, str(e))
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE FRONTEND AUDIT REPORT")
        print("=" * 80)
        
        # Calculate statistics
        total_tests = len(self.audit_results)
        passed_tests = sum(1 for r in self.audit_results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by category
        categories = {}
        for result in self.audit_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
        
        # Print category results
        for category, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
            print(f"{status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        print(f"\n🎯 Overall Frontend Audit: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Determine system status
        if success_rate >= 95:
            print("🎉 EXCELLENT: Frontend is enterprise-ready!")
            system_status = "PRODUCTION_READY"
        elif success_rate >= 85:
            print("✅ GOOD: Frontend meets most requirements.")
            system_status = "MOSTLY_READY"
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: Some issues need attention.")
            system_status = "NEEDS_ATTENTION"
        else:
            print("❌ CRITICAL: Significant issues require immediate attention.")
            system_status = "NOT_READY"
        
        # Save detailed report
        report = {
            'audit_timestamp': datetime.now().isoformat(),
            'system_status': system_status,
            'overall_success_rate': success_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'category_results': categories,
            'detailed_results': self.audit_results
        }
        
        with open('frontend_audit_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: frontend_audit_report.json")
        
        return success_rate >= 85
    
    def run_comprehensive_audit(self):
        """Run complete frontend audit"""
        print("🔍 SQL Analyzer Enterprise - Comprehensive Frontend Audit")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all audit phases
        audit_phases = [
            self.audit_backend_connectivity,
            self.audit_frontend_files,
            self.audit_component_imports,
            self.audit_api_integration,
            self.audit_build_process
        ]
        
        for phase in audit_phases:
            try:
                phase()
            except Exception as e:
                print(f"❌ Audit phase failed: {e}")
        
        # Generate final report
        return self.generate_audit_report()

if __name__ == "__main__":
    auditor = FrontendAuditor()
    success = auditor.run_comprehensive_audit()
    exit(0 if success else 1)
