#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Component Structure Audit
Systematic audit of all React components for structure and functionality
"""

import os
import re
import json
from pathlib import Path

class ComponentAuditor:
    def __init__(self):
        self.frontend_path = Path('frontend/src')
        self.components_path = self.frontend_path / 'components'
        self.views_path = self.components_path / 'views'
        self.issues = []
        
    def audit_main_views(self):
        """Audit all 7 main view components"""
        print("🔍 AUDITING MAIN VIEW COMPONENTS")
        print("-" * 50)
        
        required_views = [
            'DashboardView.jsx',
            'SQLAnalysisView.jsx', 
            'ConnectionsView.jsx',
            'MetricsView.jsx',
            'FileManagerView.jsx',
            'HistoryView.jsx',
            'TerminalView.jsx'
        ]
        
        view_issues = []
        
        for view_name in required_views:
            view_path = self.views_path / view_name
            
            if not view_path.exists():
                view_issues.append({
                    'view': view_name,
                    'issue': 'File does not exist',
                    'severity': 'critical'
                })
                print(f"❌ {view_name}: File missing")
                continue
            
            # Check component structure
            try:
                with open(view_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = self.check_component_structure(view_name, content)
                view_issues.extend(issues)
                
                if not issues:
                    print(f"✅ {view_name}: Structure OK")
                else:
                    print(f"⚠️ {view_name}: {len(issues)} issues found")
                    
            except Exception as e:
                view_issues.append({
                    'view': view_name,
                    'issue': f'Error reading file: {e}',
                    'severity': 'critical'
                })
                print(f"❌ {view_name}: Read error")
        
        return view_issues
    
    def check_component_structure(self, component_name, content):
        """Check individual component structure"""
        issues = []
        
        # Check for React import
        if 'import React' not in content:
            issues.append({
                'component': component_name,
                'issue': 'Missing React import',
                'severity': 'critical'
            })
        
        # Check for component definition
        component_base_name = component_name.replace('.jsx', '')
        if f'const {component_base_name}' not in content and f'function {component_base_name}' not in content:
            issues.append({
                'component': component_name,
                'issue': 'Component not properly defined',
                'severity': 'critical'
            })
        
        # Check for export
        if 'export default' not in content:
            issues.append({
                'component': component_name,
                'issue': 'Missing default export',
                'severity': 'critical'
            })
        
        # Check for JSX return
        if 'return (' not in content and 'return <' not in content:
            issues.append({
                'component': component_name,
                'issue': 'No JSX return statement found',
                'severity': 'warning'
            })
        
        # Check for proper prop handling
        if 'props' in content or '{' in content.split('const ' + component_base_name)[0] if 'const ' + component_base_name in content else False:
            # Component uses props, check for prop destructuring or proper usage
            pass
        
        return issues
    
    def audit_core_components(self):
        """Audit core components"""
        print("\n🔍 AUDITING CORE COMPONENTS")
        print("-" * 50)
        
        core_components = [
            'EnterpriseApp.jsx',
            'SystemHealthMonitor.jsx',
            'MetricsSystem.jsx',
            'ExportSystem.jsx',
            'DatabaseEngineSelector.jsx'
        ]
        
        core_issues = []
        
        for component_name in core_components:
            component_path = self.components_path / component_name
            
            if not component_path.exists():
                core_issues.append({
                    'component': component_name,
                    'issue': 'File does not exist',
                    'severity': 'critical'
                })
                print(f"❌ {component_name}: File missing")
                continue
            
            try:
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = self.check_component_structure(component_name, content)
                core_issues.extend(issues)
                
                if not issues:
                    print(f"✅ {component_name}: Structure OK")
                else:
                    print(f"⚠️ {component_name}: {len(issues)} issues found")
                    
            except Exception as e:
                core_issues.append({
                    'component': component_name,
                    'issue': f'Error reading file: {e}',
                    'severity': 'critical'
                })
                print(f"❌ {component_name}: Read error")
        
        return core_issues
    
    def audit_api_integration(self):
        """Audit API integration in components"""
        print("\n🔍 AUDITING API INTEGRATION")
        print("-" * 50)
        
        api_issues = []
        
        # Check if API utilities exist
        api_files = [
            self.frontend_path / 'utils' / 'api.js',
            self.components_path / 'utils' / 'api.js'
        ]
        
        existing_api_files = [f for f in api_files if f.exists()]
        
        if not existing_api_files:
            api_issues.append({
                'issue': 'No API utility files found',
                'severity': 'critical'
            })
            print("❌ No API utility files found")
            return api_issues
        
        # Check API functions in components
        jsx_files = list(self.components_path.rglob('*.jsx'))
        
        api_usage_count = 0
        
        for jsx_file in jsx_files:
            try:
                with open(jsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for API imports
                if 'from \'../utils/api\'' in content or 'from \'../../utils/api\'' in content or 'from \'./utils/api\'' in content:
                    api_usage_count += 1
                
                # Check for fetch or axios usage
                if 'fetch(' in content or 'axios.' in content:
                    # Direct API calls without utility
                    api_issues.append({
                        'component': jsx_file.name,
                        'issue': 'Direct API calls instead of using utility functions',
                        'severity': 'warning'
                    })
                
            except Exception as e:
                print(f"❌ Error checking API usage in {jsx_file.name}: {e}")
        
        print(f"✅ API integration found in {api_usage_count} components")
        
        if api_issues:
            for issue in api_issues:
                if 'component' in issue:
                    print(f"⚠️ {issue['component']}: {issue['issue']}")
                else:
                    print(f"⚠️ {issue['issue']}")
        
        return api_issues
    
    def audit_missing_components(self):
        """Find components referenced but not existing"""
        print("\n🔍 AUDITING MISSING COMPONENTS")
        print("-" * 50)
        
        missing_components = []
        jsx_files = list(self.components_path.rglob('*.jsx'))
        
        # Find all component imports
        for jsx_file in jsx_files:
            try:
                with open(jsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find component imports from relative paths
                imports = re.findall(
                    r'import\s+(\w+)\s+from\s+[\'"](\./[^\'"]+)[\'"]',
                    content
                )
                
                for component_name, import_path in imports:
                    # Resolve the path
                    current_dir = jsx_file.parent
                    resolved_path = current_dir / import_path
                    
                    # Check if file exists with common extensions
                    possible_files = [
                        resolved_path.with_suffix('.jsx'),
                        resolved_path.with_suffix('.js'),
                        resolved_path / 'index.jsx',
                        resolved_path / 'index.js'
                    ]
                    
                    if not any(p.exists() for p in possible_files):
                        missing_components.append({
                            'importing_file': jsx_file.name,
                            'component_name': component_name,
                            'import_path': import_path,
                            'resolved_path': str(resolved_path)
                        })
                
            except Exception as e:
                print(f"❌ Error checking imports in {jsx_file.name}: {e}")
        
        if missing_components:
            print("❌ Missing components found:")
            for missing in missing_components:
                print(f"   {missing['importing_file']} imports {missing['component_name']} from {missing['import_path']}")
        else:
            print("✅ All component imports resolve correctly")
        
        return missing_components
    
    def generate_component_audit_report(self):
        """Generate comprehensive component audit report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE COMPONENT AUDIT REPORT")
        print("=" * 70)
        
        # Run all audits
        view_issues = self.audit_main_views()
        core_issues = self.audit_core_components()
        api_issues = self.audit_api_integration()
        missing_components = self.audit_missing_components()
        
        # Summary
        total_issues = len(view_issues) + len(core_issues) + len(api_issues) + len(missing_components)
        
        print(f"\n🎯 COMPONENT AUDIT SUMMARY:")
        print(f"   Main View Issues: {len(view_issues)}")
        print(f"   Core Component Issues: {len(core_issues)}")
        print(f"   API Integration Issues: {len(api_issues)}")
        print(f"   Missing Components: {len(missing_components)}")
        print(f"   Total Issues: {total_issues}")
        
        # Categorize by severity
        critical_issues = [i for i in view_issues + core_issues + api_issues if i.get('severity') == 'critical']
        warning_issues = [i for i in view_issues + core_issues + api_issues if i.get('severity') == 'warning']
        
        print(f"\n🚨 Critical Issues: {len(critical_issues)}")
        print(f"⚠️ Warning Issues: {len(warning_issues)}")
        
        if total_issues == 0:
            print("\n🎉 ALL COMPONENT ISSUES RESOLVED!")
            print("✅ Frontend components are properly structured")
        else:
            print(f"\n⚠️ {total_issues} component issues need attention")
            
            if critical_issues:
                print("\n🚨 CRITICAL ISSUES:")
                for issue in critical_issues[:5]:  # Show first 5
                    component = issue.get('component', issue.get('view', 'Unknown'))
                    print(f"   {component}: {issue['issue']}")
        
        # Save detailed report
        report = {
            'timestamp': str(Path().resolve()),
            'view_issues': view_issues,
            'core_issues': core_issues,
            'api_issues': api_issues,
            'missing_components': missing_components,
            'total_issues': total_issues,
            'critical_count': len(critical_issues),
            'warning_count': len(warning_issues)
        }
        
        with open('component_audit_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: component_audit_report.json")
        
        return total_issues == 0

def main():
    auditor = ComponentAuditor()
    success = auditor.generate_component_audit_report()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
