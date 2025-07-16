#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - CSS Validation Report
Comprehensive validation of the new Mega.nz-inspired CSS system
"""

import os
import re
from pathlib import Path

class CSSValidator:
    def __init__(self):
        self.styles_path = Path('frontend/src/styles')
        self.validation_results = []
        
    def validate_file_structure(self):
        """Validate CSS file structure"""
        print("🔍 VALIDATING CSS FILE STRUCTURE")
        print("-" * 50)
        
        required_files = [
            'base/variables.css',
            'base/reset.css', 
            'base/layout.css',
            'components/sidebar.css',
            'views/DashboardView.css',
            'views/SQLAnalysisView.css',
            'views/MetricsView.css',
            'views/TerminalView.css',
            'views/ConnectionsView.css',
            'views/FileManagerView.css',
            'views/HistoryView.css',
            'index.css'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = self.styles_path / file_path
            if full_path.exists():
                file_size = full_path.stat().st_size
                existing_files.append((file_path, file_size))
                print(f"✅ {file_path} ({file_size} bytes)")
            else:
                missing_files.append(file_path)
                print(f"❌ {file_path} - Missing")
        
        return len(missing_files) == 0, existing_files, missing_files
    
    def validate_css_variables(self):
        """Validate CSS variables are properly defined"""
        print("\n🎨 VALIDATING CSS VARIABLES")
        print("-" * 50)
        
        variables_file = self.styles_path / 'base/variables.css'
        if not variables_file.exists():
            print("❌ Variables file not found")
            return False
        
        with open(variables_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_variables = [
            '--primary-blue',
            '--bg-primary',
            '--bg-secondary',
            '--text-primary',
            '--text-secondary',
            '--border-primary',
            '--spacing-md',
            '--spacing-lg',
            '--font-family-primary',
            '--font-size-sm',
            '--radius-md',
            '--shadow-card',
            '--transition-fast',
            '--sidebar-width'
        ]
        
        missing_vars = []
        found_vars = []
        
        for var in required_variables:
            if var in content:
                found_vars.append(var)
                print(f"✅ {var}")
            else:
                missing_vars.append(var)
                print(f"❌ {var} - Missing")
        
        return len(missing_vars) == 0, found_vars, missing_vars
    
    def validate_imports(self):
        """Validate CSS imports in index.css"""
        print("\n📦 VALIDATING CSS IMPORTS")
        print("-" * 50)
        
        index_file = self.styles_path / 'index.css'
        if not index_file.exists():
            print("❌ index.css not found")
            return False
        
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_imports = [
            './base/variables.css',
            './base/reset.css',
            './base/layout.css',
            './components/sidebar.css',
            './views/DashboardView.css',
            './views/SQLAnalysisView.css',
            './views/MetricsView.css',
            './views/TerminalView.css',
            './views/ConnectionsView.css',
            './views/FileManagerView.css',
            './views/HistoryView.css'
        ]
        
        missing_imports = []
        found_imports = []
        
        for import_path in required_imports:
            if f"@import '{import_path}'" in content:
                found_imports.append(import_path)
                print(f"✅ {import_path}")
            else:
                missing_imports.append(import_path)
                print(f"❌ {import_path} - Missing import")
        
        return len(missing_imports) == 0, found_imports, missing_imports
    
    def validate_mega_nz_design_elements(self):
        """Validate Mega.nz-inspired design elements"""
        print("\n🎯 VALIDATING MEGA.NZ DESIGN ELEMENTS")
        print("-" * 50)
        
        design_elements = {
            'Sidebar Navigation': ['sidebar', 'nav-button', 'nav-icon'],
            'Card System': ['card', 'card-header', 'card-body'],
            'Color Palette': ['primary-blue', 'bg-card', 'text-primary'],
            'Layout System': ['main-content', 'content-area', 'grid-layout'],
            'Professional Styling': ['shadow-card', 'border-radius', 'transition']
        }
        
        all_files = list(self.styles_path.rglob('*.css'))
        all_content = ""
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
        
        validation_results = {}
        
        for element_group, selectors in design_elements.items():
            found_selectors = []
            missing_selectors = []
            
            for selector in selectors:
                # Check for class selectors, CSS variables, or general presence
                patterns = [
                    f'.{selector}',
                    f'--{selector}',
                    selector
                ]
                
                found = any(pattern in all_content for pattern in patterns)
                
                if found:
                    found_selectors.append(selector)
                else:
                    missing_selectors.append(selector)
            
            validation_results[element_group] = {
                'found': found_selectors,
                'missing': missing_selectors,
                'success_rate': len(found_selectors) / len(selectors) * 100
            }
            
            status = "✅" if len(missing_selectors) == 0 else "⚠️"
            rate = validation_results[element_group]['success_rate']
            print(f"{status} {element_group}: {len(found_selectors)}/{len(selectors)} ({rate:.1f}%)")
        
        return validation_results
    
    def validate_responsive_design(self):
        """Validate responsive design implementation"""
        print("\n📱 VALIDATING RESPONSIVE DESIGN")
        print("-" * 50)
        
        all_files = list(self.styles_path.rglob('*.css'))
        responsive_features = {
            'Mobile Breakpoints': ['@media (max-width: 768px)', '@media (max-width: 640px)'],
            'Tablet Breakpoints': ['@media (max-width: 1024px)'],
            'Flexible Layouts': ['grid-template-columns', 'flex-direction: column'],
            'Responsive Utilities': ['sm\\:', 'md\\:', 'lg\\:']
        }
        
        all_content = ""
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_content += f.read() + "\n"
            except Exception:
                continue
        
        responsive_results = {}
        
        for feature_group, patterns in responsive_features.items():
            found_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, all_content):
                    found_patterns.append(pattern)
            
            responsive_results[feature_group] = {
                'found': found_patterns,
                'total': len(patterns),
                'success_rate': len(found_patterns) / len(patterns) * 100
            }
            
            status = "✅" if len(found_patterns) > 0 else "❌"
            rate = responsive_results[feature_group]['success_rate']
            print(f"{status} {feature_group}: {len(found_patterns)}/{len(patterns)} ({rate:.1f}%)")
        
        return responsive_results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive CSS validation report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE CSS VALIDATION REPORT")
        print("=" * 80)
        
        # Run all validations
        structure_valid, existing_files, missing_files = self.validate_file_structure()
        variables_valid, found_vars, missing_vars = self.validate_css_variables()
        imports_valid, found_imports, missing_imports = self.validate_imports()
        design_results = self.validate_mega_nz_design_elements()
        responsive_results = self.validate_responsive_design()
        
        # Calculate overall scores
        structure_score = (len(existing_files) / (len(existing_files) + len(missing_files)) * 100) if (len(existing_files) + len(missing_files)) > 0 else 0
        variables_score = (len(found_vars) / (len(found_vars) + len(missing_vars)) * 100) if (len(found_vars) + len(missing_vars)) > 0 else 0
        imports_score = (len(found_imports) / (len(found_imports) + len(missing_imports)) * 100) if (len(found_imports) + len(missing_imports)) > 0 else 0
        
        design_avg = sum(result['success_rate'] for result in design_results.values()) / len(design_results)
        responsive_avg = sum(result['success_rate'] for result in responsive_results.values()) / len(responsive_results)
        
        overall_score = (structure_score + variables_score + imports_score + design_avg + responsive_avg) / 5
        
        # Print summary
        print(f"\n🎯 CSS VALIDATION SUMMARY:")
        print(f"   File Structure: {structure_score:.1f}%")
        print(f"   CSS Variables: {variables_score:.1f}%")
        print(f"   Import System: {imports_score:.1f}%")
        print(f"   Design Elements: {design_avg:.1f}%")
        print(f"   Responsive Design: {responsive_avg:.1f}%")
        print(f"   Overall Score: {overall_score:.1f}%")
        
        # Determine status
        if overall_score >= 95:
            print("\n🎉 EXCELLENT: CSS system is perfectly implemented!")
            status = "EXCELLENT"
        elif overall_score >= 85:
            print("\n✅ GOOD: CSS system meets enterprise standards")
            status = "GOOD"
        elif overall_score >= 70:
            print("\n⚠️ ACCEPTABLE: Minor improvements needed")
            status = "ACCEPTABLE"
        else:
            print("\n❌ NEEDS WORK: Significant improvements required")
            status = "NEEDS_WORK"
        
        # File size analysis
        total_size = sum(size for _, size in existing_files)
        print(f"\n📊 CSS SYSTEM STATISTICS:")
        print(f"   Total Files: {len(existing_files)}")
        print(f"   Total Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print(f"   Average File Size: {total_size/len(existing_files):.0f} bytes")
        
        return {
            'overall_score': overall_score,
            'status': status,
            'structure_score': structure_score,
            'variables_score': variables_score,
            'imports_score': imports_score,
            'design_score': design_avg,
            'responsive_score': responsive_avg,
            'total_files': len(existing_files),
            'total_size': total_size
        }

def main():
    validator = CSSValidator()
    results = validator.generate_comprehensive_report()
    return results['overall_score'] >= 85

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
