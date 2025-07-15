#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - GitHub System Validation
Complete validation of the reconstructed GitHub-authentic CSS system
"""

import os
import time
import requests
from pathlib import Path

class GitHubSystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:3000"
        self.styles_path = Path('frontend/src/styles')
        
    def validate_css_reconstruction(self):
        """Validate complete CSS system reconstruction"""
        print("🎨 VALIDATING CSS SYSTEM RECONSTRUCTION")
        print("-" * 60)
        
        required_files = {
            'base/variables.css': 'GitHub authentic color palette and design tokens',
            'base/reset.css': 'Modern CSS reset with GitHub base styles',
            'base/layout.css': 'Layout system with 100% viewport utilization',
            'components/sidebar.css': 'GitHub-style sidebar navigation',
            'components/forms.css': 'GitHub-authentic form components',
            'views/DashboardView.css': 'Dashboard with GitHub design patterns',
            'views/SQLAnalysisView.css': 'Split-pane SQL analysis interface',
            'views/MetricsView.css': 'System monitoring dashboard',
            'index.css': 'Main stylesheet with utilities'
        }
        
        missing_files = []
        existing_files = []
        total_size = 0
        
        for file_path, description in required_files.items():
            full_path = self.styles_path / file_path
            if full_path.exists():
                file_size = full_path.stat().st_size
                existing_files.append((file_path, file_size, description))
                total_size += file_size
                print(f"✅ {file_path} ({file_size:,} bytes)")
            else:
                missing_files.append((file_path, description))
                print(f"❌ {file_path} - Missing")
        
        reconstruction_score = (len(existing_files) / len(required_files)) * 100
        print(f"\n🎯 CSS Reconstruction Score: {reconstruction_score:.1f}%")
        print(f"📊 Total CSS Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        return reconstruction_score >= 90, existing_files, missing_files
    
    def validate_github_authenticity(self):
        """Validate GitHub design authenticity"""
        print("\n🎨 VALIDATING GITHUB DESIGN AUTHENTICITY")
        print("-" * 60)
        
        variables_file = self.styles_path / 'base/variables.css'
        if not variables_file.exists():
            print("❌ Variables file missing - cannot validate authenticity")
            return False, {}
        
        with open(variables_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        github_features = {
            'GitHub Colors': [
                '--github-white: #ffffff',
                '--github-gray-0: #f6f8fa',
                '--github-gray-2: #d0d7de',
                '--github-gray-9: #24292f',
                '--github-blue: #0969da'
            ],
            'GitHub Typography': [
                '-apple-system',
                'BlinkMacSystemFont',
                '"Segoe UI"',
                'ui-monospace',
                'SFMono-Regular'
            ],
            'GitHub Spacing': [
                '--spacing-1: 0.25rem',
                '--spacing-2: 0.5rem',
                '--spacing-4: 1rem',
                '--spacing-6: 1.5rem',
                '--spacing-8: 2rem'
            ],
            'GitHub Components': [
                '--radius-base: 6px',
                '--github-button-height: 32px',
                '--github-input-height: 32px',
                '--github-icon-size: 16px'
            ]
        }
        
        authenticity_results = {}
        
        for feature_group, patterns in github_features.items():
            found_patterns = []
            
            for pattern in patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            
            authenticity_results[feature_group] = {
                'found': found_patterns,
                'total': len(patterns),
                'success_rate': len(found_patterns) / len(patterns) * 100
            }
            
            status = "✅" if len(found_patterns) >= len(patterns) * 0.8 else "⚠️" if len(found_patterns) >= len(patterns) * 0.5 else "❌"
            rate = authenticity_results[feature_group]['success_rate']
            print(f"{status} {feature_group}: {len(found_patterns)}/{len(patterns)} ({rate:.1f}%)")
        
        overall_authenticity = sum(result['success_rate'] for result in authenticity_results.values()) / len(authenticity_results)
        print(f"\n🎯 GitHub Authenticity Score: {overall_authenticity:.1f}%")
        
        return overall_authenticity >= 80, authenticity_results
    
    def validate_viewport_utilization(self):
        """Validate 100% viewport utilization"""
        print("\n🖥️ VALIDATING 100% VIEWPORT UTILIZATION")
        print("-" * 60)
        
        viewport_patterns = {
            'Full Viewport': ['100vh', '100vw', 'height: 100vh', 'width: 100%'],
            'Absolute Positioning': ['position: absolute', 'top: 0', 'left: 0', 'right: 0', 'bottom: 0'],
            'Flex Layout': ['display: flex', 'flex: 1', 'flex-direction: column'],
            'Overflow Control': ['overflow: hidden', 'overflow-y: auto', 'overflow-x: hidden']
        }
        
        all_content = ""
        view_files = ['views/DashboardView.css', 'views/SQLAnalysisView.css', 'views/MetricsView.css']
        
        for view_file in view_files:
            view_path = self.styles_path / view_file
            if view_path.exists():
                with open(view_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
        
        viewport_results = {}
        
        for pattern_group, patterns in viewport_patterns.items():
            found_patterns = []
            
            for pattern in patterns:
                if pattern in all_content:
                    found_patterns.append(pattern)
            
            viewport_results[pattern_group] = {
                'found': found_patterns,
                'total': len(patterns),
                'success_rate': len(found_patterns) / len(patterns) * 100
            }
            
            status = "✅" if len(found_patterns) >= len(patterns) * 0.75 else "⚠️" if len(found_patterns) >= len(patterns) * 0.5 else "❌"
            rate = viewport_results[pattern_group]['success_rate']
            print(f"{status} {pattern_group}: {len(found_patterns)}/{len(patterns)} ({rate:.1f}%)")
        
        overall_viewport = sum(result['success_rate'] for result in viewport_results.values()) / len(viewport_results)
        print(f"\n🎯 Viewport Utilization Score: {overall_viewport:.1f}%")
        
        return overall_viewport >= 75, viewport_results
    
    def validate_component_completeness(self):
        """Validate component system completeness"""
        print("\n🧩 VALIDATING COMPONENT SYSTEM COMPLETENESS")
        print("-" * 60)
        
        component_tests = {
            'Sidebar Component': {
                'file': 'components/sidebar.css',
                'patterns': ['.sidebar', '.nav-item', '.nav-icon', '.sidebar-toggle', '.nav-tooltip']
            },
            'Form Components': {
                'file': 'components/forms.css',
                'patterns': ['.form-input', '.form-label', '.form-checkbox', '.form-select', '.form-error']
            },
            'Layout System': {
                'file': 'base/layout.css',
                'patterns': ['.enterprise-app', '.main-content', '.btn', '.card', '.view-container']
            }
        }
        
        component_results = {}
        
        for component_name, test_data in component_tests.items():
            file_path = self.styles_path / test_data['file']
            
            if not file_path.exists():
                component_results[component_name] = {
                    'found': [],
                    'total': len(test_data['patterns']),
                    'success_rate': 0
                }
                print(f"❌ {component_name}: File missing")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_patterns = []
            for pattern in test_data['patterns']:
                if pattern in content:
                    found_patterns.append(pattern)
            
            component_results[component_name] = {
                'found': found_patterns,
                'total': len(test_data['patterns']),
                'success_rate': len(found_patterns) / len(test_data['patterns']) * 100
            }
            
            status = "✅" if len(found_patterns) >= len(test_data['patterns']) * 0.8 else "⚠️" if len(found_patterns) >= len(test_data['patterns']) * 0.5 else "❌"
            rate = component_results[component_name]['success_rate']
            print(f"{status} {component_name}: {len(found_patterns)}/{len(test_data['patterns'])} ({rate:.1f}%)")
        
        overall_components = sum(result['success_rate'] for result in component_results.values()) / len(component_results)
        print(f"\n🎯 Component Completeness Score: {overall_components:.1f}%")
        
        return overall_components >= 75, component_results
    
    def validate_backend_integration(self):
        """Validate backend integration"""
        print("\n🔗 VALIDATING BACKEND INTEGRATION")
        print("-" * 60)
        
        # Test key endpoints
        endpoints = [
            ('/api/health', 'Health Check'),
            ('/api/engines', 'Database Engines'),
            ('/api/formats', 'Export Formats')
        ]
        
        working_endpoints = 0
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"✅ {name}: OK ({response.status_code})")
                else:
                    print(f"⚠️ {name}: {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"❌ {name}: Connection failed")
        
        # Test frontend accessibility
        try:
            response = requests.get(self.frontend_url, timeout=5)
            frontend_status = response.status_code == 200
            print(f"✅ Frontend: {'OK' if frontend_status else 'Error'} ({response.status_code if 'response' in locals() else 'No response'})")
        except:
            frontend_status = False
            print("❌ Frontend: Connection failed")
        
        integration_score = ((working_endpoints / len(endpoints)) * 70 + (frontend_status * 30))
        print(f"\n🎯 Backend Integration Score: {integration_score:.1f}%")
        
        return integration_score >= 60, working_endpoints, frontend_status
    
    def run_comprehensive_validation(self):
        """Run comprehensive system validation"""
        print("=" * 80)
        print("🚀 SQL ANALYZER ENTERPRISE - GITHUB SYSTEM VALIDATION")
        print("=" * 80)
        
        # Run all validations
        css_valid, existing_files, missing_files = self.validate_css_reconstruction()
        auth_valid, auth_results = self.validate_github_authenticity()
        viewport_valid, viewport_results = self.validate_viewport_utilization()
        comp_valid, comp_results = self.validate_component_completeness()
        backend_valid, working_endpoints, frontend_status = self.validate_backend_integration()
        
        # Calculate overall score
        validations = [css_valid, auth_valid, viewport_valid, comp_valid, backend_valid]
        passed_validations = sum(validations)
        overall_score = (passed_validations / len(validations)) * 100
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE VALIDATION RESULTS")
        print("=" * 80)
        
        validation_names = [
            "CSS System Reconstruction",
            "GitHub Design Authenticity",
            "100% Viewport Utilization",
            "Component System Completeness",
            "Backend Integration"
        ]
        
        for i, (validation_name, result) in enumerate(zip(validation_names, validations)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {validation_name}")
        
        print(f"\n🎯 Overall Validation Score: {passed_validations}/{len(validations)} ({overall_score:.1f}%)")
        
        # System statistics
        total_css_size = sum(size for _, size, _ in existing_files)
        print(f"\n📊 SYSTEM STATISTICS:")
        print(f"   CSS Files Created: {len(existing_files)}/{len(existing_files) + len(missing_files)}")
        print(f"   Total CSS Size: {total_css_size:,} bytes ({total_css_size/1024:.1f} KB)")
        print(f"   Backend Endpoints: {working_endpoints}/3 working")
        print(f"   Frontend Status: {'Online' if frontend_status else 'Offline'}")
        
        if overall_score >= 90:
            print("\n🎉 EXCELLENT: GitHub system is perfectly implemented!")
            final_status = "EXCELLENT"
        elif overall_score >= 75:
            print("\n✅ GOOD: GitHub system meets enterprise standards")
            final_status = "GOOD"
        elif overall_score >= 60:
            print("\n⚠️ ACCEPTABLE: Minor improvements needed")
            final_status = "ACCEPTABLE"
        else:
            print("\n❌ NEEDS WORK: Significant improvements required")
            final_status = "NEEDS_WORK"
        
        print(f"\n🚀 SQL Analyzer Enterprise System Status: {final_status}")
        print(f"📍 Frontend: {self.frontend_url}")
        print(f"🔧 Backend: {self.base_url}")
        
        return overall_score >= 75

def main():
    validator = GitHubSystemValidator()
    success = validator.run_comprehensive_validation()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
