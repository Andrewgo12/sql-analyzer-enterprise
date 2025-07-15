#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Complete CSS System Validation
Comprehensive validation of the reconstructed GitHub-authentic CSS system
"""

import os
import time
from pathlib import Path

class CompleteCSSValidator:
    def __init__(self):
        self.styles_path = Path('frontend/src/styles')
        
    def validate_complete_file_structure(self):
        """Validate complete CSS file structure"""
        print("📁 VALIDATING COMPLETE CSS FILE STRUCTURE")
        print("-" * 60)
        
        required_structure = {
            'base': [
                'variables.css',
                'reset.css', 
                'layout.css',
                'animations.css'
            ],
            'components': [
                'sidebar.css',
                'forms.css',
                'modals.css'
            ],
            'views': [
                'DashboardView.css',
                'SQLAnalysisView.css',
                'MetricsView.css',
                'TerminalView.css',
                'ConnectionsView.css',
                'FileManagerView.css',
                'HistoryView.css'
            ]
        }
        
        missing_files = []
        existing_files = []
        total_size = 0
        
        for folder, files in required_structure.items():
            folder_path = self.styles_path / folder
            print(f"\n📂 {folder.upper()} FOLDER:")
            
            if not folder_path.exists():
                print(f"❌ Folder {folder} does not exist")
                missing_files.extend([f"{folder}/{file}" for file in files])
                continue
            
            for file in files:
                file_path = folder_path / file
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    existing_files.append((f"{folder}/{file}", file_size))
                    total_size += file_size
                    print(f"✅ {file} ({file_size:,} bytes)")
                else:
                    missing_files.append(f"{folder}/{file}")
                    print(f"❌ {file} - Missing")
        
        # Check index.css
        index_path = self.styles_path / 'index.css'
        if index_path.exists():
            index_size = index_path.stat().st_size
            existing_files.append(('index.css', index_size))
            total_size += index_size
            print(f"\n📄 INDEX FILE:")
            print(f"✅ index.css ({index_size:,} bytes)")
        else:
            missing_files.append('index.css')
            print(f"\n📄 INDEX FILE:")
            print(f"❌ index.css - Missing")
        
        total_expected = sum(len(files) for files in required_structure.values()) + 1  # +1 for index.css
        completion_rate = (len(existing_files) / total_expected) * 100
        
        print(f"\n🎯 File Structure Completion: {len(existing_files)}/{total_expected} ({completion_rate:.1f}%)")
        print(f"📊 Total CSS System Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        return completion_rate >= 95, existing_files, missing_files, total_size
    
    def validate_index_imports(self):
        """Validate index.css imports all required files"""
        print("\n📋 VALIDATING INDEX.CSS IMPORTS")
        print("-" * 60)
        
        index_path = self.styles_path / 'index.css'
        if not index_path.exists():
            print("❌ index.css file not found")
            return False, []
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_imports = [
            './base/variables.css',
            './base/reset.css',
            './base/layout.css',
            './base/animations.css',
            './components/sidebar.css',
            './components/forms.css',
            './components/modals.css',
            './views/DashboardView.css',
            './views/SQLAnalysisView.css',
            './views/MetricsView.css',
            './views/TerminalView.css',
            './views/ConnectionsView.css',
            './views/FileManagerView.css',
            './views/HistoryView.css'
        ]
        
        found_imports = []
        missing_imports = []
        
        for import_path in expected_imports:
            if f"@import '{import_path}'" in content:
                found_imports.append(import_path)
                print(f"✅ {import_path}")
            else:
                missing_imports.append(import_path)
                print(f"❌ {import_path} - Missing import")
        
        import_completion = (len(found_imports) / len(expected_imports)) * 100
        print(f"\n🎯 Import Completion: {len(found_imports)}/{len(expected_imports)} ({import_completion:.1f}%)")
        
        return import_completion >= 95, found_imports
    
    def validate_github_authenticity_complete(self):
        """Validate complete GitHub authenticity across all files"""
        print("\n🎨 VALIDATING COMPLETE GITHUB AUTHENTICITY")
        print("-" * 60)
        
        github_patterns = {
            'GitHub Colors': [
                '#ffffff', '#f6f8fa', '#d0d7de', '#24292f', '#0969da',
                'var(--github-white)', 'var(--github-gray-0)', 'var(--github-blue)'
            ],
            'GitHub Typography': [
                '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"',
                'ui-monospace', 'SFMono-Regular', 'var(--font-family-primary)'
            ],
            'GitHub Spacing': [
                'var(--spacing-1)', 'var(--spacing-2)', 'var(--spacing-4)',
                '0.25rem', '0.5rem', '1rem', '1.5rem', '2rem'
            ],
            'GitHub Components': [
                'border-radius: 6px', 'var(--radius-base)', 'min-height: 32px',
                'var(--github-button-height)', 'var(--github-input-height)'
            ],
            'GitHub Transitions': [
                'transition:', 'var(--transition-fast)', 'var(--transition-base)',
                '0.15s ease', '0.2s ease', 'ease-out'
            ]
        }
        
        all_content = ""
        for file_path in self.styles_path.rglob('*.css'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
            except Exception:
                continue
        
        authenticity_results = {}
        
        for pattern_group, patterns in github_patterns.items():
            found_patterns = []
            
            for pattern in patterns:
                if pattern in all_content:
                    found_patterns.append(pattern)
            
            authenticity_results[pattern_group] = {
                'found': found_patterns,
                'total': len(patterns),
                'success_rate': len(found_patterns) / len(patterns) * 100
            }
            
            status = "✅" if len(found_patterns) >= len(patterns) * 0.7 else "⚠️" if len(found_patterns) >= len(patterns) * 0.4 else "❌"
            rate = authenticity_results[pattern_group]['success_rate']
            print(f"{status} {pattern_group}: {len(found_patterns)}/{len(patterns)} ({rate:.1f}%)")
        
        overall_authenticity = sum(result['success_rate'] for result in authenticity_results.values()) / len(authenticity_results)
        print(f"\n🎯 Overall GitHub Authenticity: {overall_authenticity:.1f}%")
        
        return overall_authenticity >= 75, authenticity_results
    
    def validate_viewport_utilization_complete(self):
        """Validate 100% viewport utilization across all views"""
        print("\n🖥️ VALIDATING COMPLETE VIEWPORT UTILIZATION")
        print("-" * 60)
        
        viewport_patterns = {
            'Full Viewport': ['100vh', '100vw', 'height: 100vh', 'width: 100%'],
            'Absolute Positioning': ['position: absolute', 'top: 0', 'left: 0', 'right: 0', 'bottom: 0'],
            'Flex Layout': ['display: flex', 'flex: 1', 'flex-direction: column'],
            'Overflow Control': ['overflow: hidden', 'overflow-y: auto', 'overflow-x: hidden'],
            'Calc Functions': ['calc(100vh -', 'calc(100vw -', 'calc(100% -']
        }
        
        view_files = [
            'views/DashboardView.css',
            'views/SQLAnalysisView.css', 
            'views/MetricsView.css',
            'views/TerminalView.css',
            'views/ConnectionsView.css',
            'views/FileManagerView.css',
            'views/HistoryView.css'
        ]
        
        all_view_content = ""
        for view_file in view_files:
            view_path = self.styles_path / view_file
            if view_path.exists():
                with open(view_path, 'r', encoding='utf-8') as f:
                    all_view_content += f.read() + "\n"
        
        viewport_results = {}
        
        for pattern_group, patterns in viewport_patterns.items():
            found_patterns = []
            
            for pattern in patterns:
                if pattern in all_view_content:
                    found_patterns.append(pattern)
            
            viewport_results[pattern_group] = {
                'found': found_patterns,
                'total': len(patterns),
                'success_rate': len(found_patterns) / len(patterns) * 100
            }
            
            status = "✅" if len(found_patterns) >= len(patterns) * 0.6 else "⚠️" if len(found_patterns) >= len(patterns) * 0.3 else "❌"
            rate = viewport_results[pattern_group]['success_rate']
            print(f"{status} {pattern_group}: {len(found_patterns)}/{len(patterns)} ({rate:.1f}%)")
        
        overall_viewport = sum(result['success_rate'] for result in viewport_results.values()) / len(viewport_results)
        print(f"\n🎯 Overall Viewport Utilization: {overall_viewport:.1f}%")
        
        return overall_viewport >= 70, viewport_results
    
    def validate_responsive_design_complete(self):
        """Validate responsive design across all components"""
        print("\n📱 VALIDATING COMPLETE RESPONSIVE DESIGN")
        print("-" * 60)
        
        responsive_patterns = [
            '@media (max-width: 1024px)',
            '@media (max-width: 768px)',
            '@media (max-width: 640px)',
            'grid-template-columns: 1fr',
            'flex-direction: column',
            'min-height: 44px'
        ]
        
        all_content = ""
        for file_path in self.styles_path.rglob('*.css'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
            except Exception:
                continue
        
        found_responsive = sum(1 for pattern in responsive_patterns if pattern in all_content)
        responsive_score = (found_responsive / len(responsive_patterns)) * 100
        
        for pattern in responsive_patterns:
            status = "✅" if pattern in all_content else "❌"
            print(f"{status} {pattern}")
        
        print(f"\n🎯 Responsive Design Score: {found_responsive}/{len(responsive_patterns)} ({responsive_score:.1f}%)")
        
        return responsive_score >= 80, responsive_score
    
    def run_complete_validation(self):
        """Run complete CSS system validation"""
        print("=" * 80)
        print("🚀 SQL ANALYZER ENTERPRISE - COMPLETE CSS SYSTEM VALIDATION")
        print("=" * 80)
        
        # Run all validations
        structure_valid, existing_files, missing_files, total_size = self.validate_complete_file_structure()
        imports_valid, found_imports = self.validate_index_imports()
        auth_valid, auth_results = self.validate_github_authenticity_complete()
        viewport_valid, viewport_results = self.validate_viewport_utilization_complete()
        responsive_valid, responsive_score = self.validate_responsive_design_complete()
        
        # Calculate overall score
        validations = [structure_valid, imports_valid, auth_valid, viewport_valid, responsive_valid]
        passed_validations = sum(validations)
        overall_score = (passed_validations / len(validations)) * 100
        
        print("\n" + "=" * 80)
        print("📊 COMPLETE CSS SYSTEM VALIDATION RESULTS")
        print("=" * 80)
        
        validation_names = [
            "Complete File Structure",
            "Index.css Imports",
            "GitHub Authenticity",
            "Viewport Utilization", 
            "Responsive Design"
        ]
        
        for i, (validation_name, result) in enumerate(zip(validation_names, validations)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {validation_name}")
        
        print(f"\n🎯 Overall CSS System Score: {passed_validations}/{len(validations)} ({overall_score:.1f}%)")
        
        # System statistics
        print(f"\n📊 COMPLETE CSS SYSTEM STATISTICS:")
        print(f"   Total CSS Files: {len(existing_files)}")
        print(f"   Missing Files: {len(missing_files)}")
        print(f"   Total System Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print(f"   Import Coverage: {len(found_imports)}/14 files")
        print(f"   Responsive Score: {responsive_score:.1f}%")
        
        if missing_files:
            print(f"\n❌ MISSING FILES:")
            for file in missing_files:
                print(f"   - {file}")
        
        if overall_score >= 90:
            print("\n🎉 EXCELLENT: Complete CSS system is perfectly implemented!")
            final_status = "EXCELLENT"
        elif overall_score >= 80:
            print("\n✅ GOOD: CSS system meets enterprise standards")
            final_status = "GOOD"
        elif overall_score >= 70:
            print("\n⚠️ ACCEPTABLE: Minor improvements needed")
            final_status = "ACCEPTABLE"
        else:
            print("\n❌ NEEDS WORK: Significant improvements required")
            final_status = "NEEDS_WORK"
        
        print(f"\n🚀 Complete CSS System Status: {final_status}")
        print(f"📁 Total Files Created: {len(existing_files)}")
        print(f"💾 System Size: {total_size/1024:.1f} KB")
        
        return overall_score >= 80

def main():
    validator = CompleteCSSValidator()
    success = validator.run_complete_validation()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
