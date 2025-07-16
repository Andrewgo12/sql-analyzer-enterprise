#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Complete Frontend Audit
Comprehensive validation of the complete frontend system
"""

import os
import json
from pathlib import Path

class CompleteFrontendAuditor:
    def __init__(self):
        self.frontend_path = Path('frontend')
        self.src_path = self.frontend_path / 'src'
        self.styles_path = self.src_path / 'styles'
        
    def audit_file_structure(self):
        """Audit complete frontend file structure"""
        print("📁 AUDITING COMPLETE FRONTEND FILE STRUCTURE")
        print("-" * 60)
        
        required_structure = {
            'src': {
                'components': {
                    'views': [
                        'DashboardView.jsx',
                        'SQLAnalysisView.jsx',
                        'MetricsView.jsx',
                        'TerminalView.jsx',
                        'ConnectionsView.jsx',
                        'FileManagerView.jsx',
                        'HistoryView.jsx',
                        'SettingsView.jsx',
                        'DownloadsView.jsx'
                    ],
                    'modals': [
                        'AnalysisOptionsModal.jsx',
                        'ConnectionModal.jsx',
                        'ExportModal.jsx'
                    ],
                    'ui': [
                        'Button.jsx',
                        'Input.jsx',
                        'Card.jsx',
                        'Modal.jsx',
                        'Dropdown.jsx',
                        'index.js'
                    ],
                    'files': [
                        'EnterpriseApp.jsx',
                        'Sidebar.jsx'
                    ]
                },
                'styles': {
                    'base': [
                        'variables.css',
                        'reset.css',
                        'layout.css',
                        'animations.css'
                    ],
                    'components': [
                        'sidebar.css',
                        'forms.css',
                        'modals.css',
                        'ui.css'
                    ],
                    'views': [
                        'DashboardView.css',
                        'SQLAnalysisView.css',
                        'MetricsView.css',
                        'TerminalView.css',
                        'ConnectionsView.css',
                        'FileManagerView.css',
                        'HistoryView.css',
                        'SettingsView.css',
                        'DownloadsView.css'
                    ],
                    'files': [
                        'index.css',
                        'enterprise.css',
                        'EnterpriseApp.css'
                    ]
                },
                'files': [
                    'App.jsx',
                    'main.jsx'
                ]
            },
            'files': [
                'package.json',
                'vite.config.js',
                'index.html'
            ]
        }
        
        missing_files = []
        existing_files = []
        total_size = 0
        
        def check_structure(structure, base_path, prefix=""):
            nonlocal missing_files, existing_files, total_size

            if isinstance(structure, list):
                # Handle list of files
                for file in structure:
                    file_path = base_path / file
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        existing_files.append((f"{prefix}{file}", file_size))
                        total_size += file_size
                        print(f"✅ {prefix}{file} ({file_size:,} bytes)")
                    else:
                        missing_files.append(f"{prefix}{file}")
                        print(f"❌ {prefix}{file} - Missing")
                return

            for key, value in structure.items():
                if key == 'files':
                    # Check files in current directory
                    for file in value:
                        file_path = base_path / file
                        if file_path.exists():
                            file_size = file_path.stat().st_size
                            existing_files.append((f"{prefix}{file}", file_size))
                            total_size += file_size
                            print(f"✅ {prefix}{file} ({file_size:,} bytes)")
                        else:
                            missing_files.append(f"{prefix}{file}")
                            print(f"❌ {prefix}{file} - Missing")
                else:
                    # Check subdirectory
                    subdir_path = base_path / key
                    new_prefix = f"{prefix}{key}/"

                    if not subdir_path.exists():
                        print(f"❌ Directory {new_prefix} does not exist")
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey == 'files':
                                    missing_files.extend([f"{new_prefix}{f}" for f in subvalue])
                                elif isinstance(subvalue, list):
                                    missing_files.extend([f"{new_prefix}{subkey}/{f}" for f in subvalue])
                        elif isinstance(value, list):
                            missing_files.extend([f"{new_prefix}{f}" for f in value])
                        continue

                    print(f"\n📂 {new_prefix.upper()}")
                    check_structure(value, subdir_path, new_prefix)
        
        check_structure(required_structure, self.frontend_path)
        
        total_expected = self._count_expected_files(required_structure)
        completion_rate = (len(existing_files) / total_expected) * 100
        
        print(f"\n🎯 Frontend Structure Completion: {len(existing_files)}/{total_expected} ({completion_rate:.1f}%)")
        print(f"📊 Total Frontend Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        return completion_rate >= 90, existing_files, missing_files, total_size
    
    def _count_expected_files(self, structure):
        """Count total expected files in structure"""
        count = 0

        if isinstance(structure, list):
            return len(structure)

        for key, value in structure.items():
            if key == 'files':
                count += len(value)
            elif isinstance(value, dict):
                count += self._count_expected_files(value)
            elif isinstance(value, list):
                count += len(value)
        return count
    
    def audit_react_components(self):
        """Audit React component completeness"""
        print("\n⚛️ AUDITING REACT COMPONENTS")
        print("-" * 60)
        
        component_checks = {
            'Views': {
                'path': self.src_path / 'components' / 'views',
                'files': [
                    'DashboardView.jsx',
                    'SQLAnalysisView.jsx', 
                    'MetricsView.jsx',
                    'TerminalView.jsx',
                    'ConnectionsView.jsx',
                    'FileManagerView.jsx',
                    'HistoryView.jsx',
                    'SettingsView.jsx',
                    'DownloadsView.jsx'
                ]
            },
            'UI Components': {
                'path': self.src_path / 'components' / 'ui',
                'files': [
                    'Button.jsx',
                    'Input.jsx',
                    'Card.jsx',
                    'Modal.jsx',
                    'Dropdown.jsx',
                    'index.js'
                ]
            },
            'Modals': {
                'path': self.src_path / 'components' / 'modals',
                'files': [
                    'AnalysisOptionsModal.jsx',
                    'ConnectionModal.jsx',
                    'ExportModal.jsx'
                ]
            }
        }
        
        component_results = {}
        
        for category, config in component_checks.items():
            print(f"\n📦 {category}:")
            
            found_components = []
            missing_components = []
            
            for file in config['files']:
                file_path = config['path'] / file
                if file_path.exists():
                    found_components.append(file)
                    print(f"✅ {file}")
                else:
                    missing_components.append(file)
                    print(f"❌ {file} - Missing")
            
            component_results[category] = {
                'found': found_components,
                'missing': missing_components,
                'completion': len(found_components) / len(config['files']) * 100
            }
        
        overall_completion = sum(result['completion'] for result in component_results.values()) / len(component_results)
        print(f"\n🎯 React Components Completion: {overall_completion:.1f}%")
        
        return overall_completion >= 80, component_results
    
    def audit_css_system(self):
        """Audit complete CSS system"""
        print("\n🎨 AUDITING COMPLETE CSS SYSTEM")
        print("-" * 60)
        
        css_files = {
            'Base Styles': [
                'base/variables.css',
                'base/reset.css',
                'base/layout.css',
                'base/animations.css'
            ],
            'Component Styles': [
                'components/sidebar.css',
                'components/forms.css',
                'components/modals.css',
                'components/ui.css'
            ],
            'View Styles': [
                'views/DashboardView.css',
                'views/SQLAnalysisView.css',
                'views/MetricsView.css',
                'views/TerminalView.css',
                'views/ConnectionsView.css',
                'views/FileManagerView.css',
                'views/HistoryView.css',
                'views/SettingsView.css',
                'views/DownloadsView.css'
            ],
            'Main Styles': [
                'index.css',
                'enterprise.css',
                'EnterpriseApp.css'
            ]
        }
        
        css_results = {}
        total_css_size = 0
        
        for category, files in css_files.items():
            print(f"\n🎨 {category}:")
            
            found_files = []
            missing_files = []
            category_size = 0
            
            for file in files:
                file_path = self.styles_path / file
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    found_files.append((file, file_size))
                    category_size += file_size
                    total_css_size += file_size
                    print(f"✅ {file} ({file_size:,} bytes)")
                else:
                    missing_files.append(file)
                    print(f"❌ {file} - Missing")
            
            css_results[category] = {
                'found': found_files,
                'missing': missing_files,
                'size': category_size,
                'completion': len(found_files) / len(files) * 100
            }
        
        overall_css_completion = sum(result['completion'] for result in css_results.values()) / len(css_results)
        print(f"\n🎯 CSS System Completion: {overall_css_completion:.1f}%")
        print(f"📊 Total CSS Size: {total_css_size:,} bytes ({total_css_size/1024:.1f} KB)")
        
        return overall_css_completion >= 90, css_results, total_css_size
    
    def audit_package_dependencies(self):
        """Audit package.json dependencies"""
        print("\n📦 AUDITING PACKAGE DEPENDENCIES")
        print("-" * 60)
        
        package_json_path = self.frontend_path / 'package.json'
        
        if not package_json_path.exists():
            print("❌ package.json not found")
            return False, {}
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading package.json: {e}")
            return False, {}
        
        required_deps = {
            'dependencies': [
                'react',
                'react-dom',
                'lucide-react'
            ],
            'devDependencies': [
                '@vitejs/plugin-react',
                'vite'
            ]
        }
        
        dep_results = {}
        
        for dep_type, deps in required_deps.items():
            print(f"\n📋 {dep_type}:")
            
            found_deps = []
            missing_deps = []
            
            package_deps = package_data.get(dep_type, {})
            
            for dep in deps:
                if dep in package_deps:
                    version = package_deps[dep]
                    found_deps.append((dep, version))
                    print(f"✅ {dep}@{version}")
                else:
                    missing_deps.append(dep)
                    print(f"❌ {dep} - Missing")
            
            dep_results[dep_type] = {
                'found': found_deps,
                'missing': missing_deps,
                'completion': len(found_deps) / len(deps) * 100
            }
        
        overall_deps = sum(result['completion'] for result in dep_results.values()) / len(dep_results)
        print(f"\n🎯 Dependencies Completion: {overall_deps:.1f}%")
        
        return overall_deps >= 80, dep_results
    
    def run_complete_audit(self):
        """Run complete frontend audit"""
        print("=" * 80)
        print("🚀 SQL ANALYZER ENTERPRISE - COMPLETE FRONTEND AUDIT")
        print("=" * 80)
        
        # Run all audits
        structure_valid, existing_files, missing_files, total_size = self.audit_file_structure()
        components_valid, component_results = self.audit_react_components()
        css_valid, css_results, css_size = self.audit_css_system()
        deps_valid, dep_results = self.audit_package_dependencies()
        
        # Calculate overall score
        audits = [structure_valid, components_valid, css_valid, deps_valid]
        passed_audits = sum(audits)
        overall_score = (passed_audits / len(audits)) * 100
        
        print("\n" + "=" * 80)
        print("📊 COMPLETE FRONTEND AUDIT RESULTS")
        print("=" * 80)
        
        audit_names = [
            "File Structure",
            "React Components",
            "CSS System",
            "Package Dependencies"
        ]
        
        for i, (audit_name, result) in enumerate(zip(audit_names, audits)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {audit_name}")
        
        print(f"\n🎯 Overall Frontend Score: {passed_audits}/{len(audits)} ({overall_score:.1f}%)")
        
        # System statistics
        print(f"\n📊 COMPLETE FRONTEND STATISTICS:")
        print(f"   Total Files: {len(existing_files)}")
        print(f"   Missing Files: {len(missing_files)}")
        print(f"   Total Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print(f"   CSS System Size: {css_size:,} bytes ({css_size/1024:.1f} KB)")
        
        if missing_files:
            print(f"\n❌ MISSING FILES ({len(missing_files)}):")
            for file in missing_files[:10]:  # Show first 10
                print(f"   - {file}")
            if len(missing_files) > 10:
                print(f"   ... and {len(missing_files) - 10} more")
        
        if overall_score >= 95:
            print("\n🎉 EXCELLENT: Frontend is perfectly implemented!")
            final_status = "EXCELLENT"
        elif overall_score >= 85:
            print("\n✅ GOOD: Frontend meets enterprise standards")
            final_status = "GOOD"
        elif overall_score >= 75:
            print("\n⚠️ ACCEPTABLE: Minor improvements needed")
            final_status = "ACCEPTABLE"
        else:
            print("\n❌ NEEDS WORK: Significant improvements required")
            final_status = "NEEDS_WORK"
        
        print(f"\n🚀 Complete Frontend Status: {final_status}")
        print(f"📁 Files Created: {len(existing_files)}")
        print(f"💾 Total Size: {total_size/1024:.1f} KB")
        print(f"🎨 CSS Files: {len([f for f in existing_files if f[0].endswith('.css')])}")
        print(f"⚛️ React Components: {len([f for f in existing_files if f[0].endswith('.jsx')])}")
        
        return overall_score >= 85

def main():
    auditor = CompleteFrontendAuditor()
    success = auditor.run_complete_audit()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
