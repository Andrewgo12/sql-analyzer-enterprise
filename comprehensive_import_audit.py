#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Comprehensive Import Audit
Complete audit and repair of all frontend imports
"""

import os
import re
import json
from pathlib import Path

class ImportAuditor:
    def __init__(self):
        self.frontend_path = Path('frontend/src')
        self.issues = []
        self.fixes_applied = []
        
    def find_all_jsx_files(self):
        """Find all JSX and JS files"""
        jsx_files = []
        for root, dirs, files in os.walk(self.frontend_path):
            for file in files:
                if file.endswith(('.jsx', '.js')):
                    jsx_files.append(Path(root) / file)
        return jsx_files
    
    def audit_lucide_react_imports(self):
        """Audit all lucide-react imports"""
        print("🔍 AUDITING LUCIDE-REACT IMPORTS")
        print("-" * 50)
        
        jsx_files = self.find_all_jsx_files()
        lucide_issues = []
        
        for file_path in jsx_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find lucide-react imports
                lucide_imports = re.findall(
                    r'import\s*{([^}]+)}\s*from\s*[\'"]lucide-react[\'"]',
                    content,
                    re.MULTILINE
                )
                
                for import_list in lucide_imports:
                    # Check for Memory icon (should be MemoryStick)
                    if 'Memory,' in import_list or ', Memory' in import_list or import_list.strip() == 'Memory':
                        lucide_issues.append({
                            'file': str(file_path),
                            'issue': 'Memory icon should be MemoryStick',
                            'import_list': import_list.strip()
                        })
                    
                    # Check for common icon issues
                    icons = [icon.strip() for icon in import_list.split(',')]
                    for icon in icons:
                        if icon and not re.match(r'^[A-Z][a-zA-Z0-9]*$', icon):
                            lucide_issues.append({
                                'file': str(file_path),
                                'issue': f'Invalid icon name: {icon}',
                                'import_list': import_list.strip()
                            })
                
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
        
        if lucide_issues:
            print("❌ Lucide-React Import Issues Found:")
            for issue in lucide_issues:
                print(f"   {Path(issue['file']).name}: {issue['issue']}")
        else:
            print("✅ All Lucide-React imports are correct")
        
        return lucide_issues
    
    def audit_relative_imports(self):
        """Audit all relative imports"""
        print("\n🔍 AUDITING RELATIVE IMPORTS")
        print("-" * 50)
        
        jsx_files = self.find_all_jsx_files()
        relative_issues = []
        
        for file_path in jsx_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find relative imports
                relative_imports = re.findall(
                    r'import\s+.*?\s+from\s+[\'"](\.\./[^\'"]+)[\'"]',
                    content,
                    re.MULTILINE
                )
                
                for import_path in relative_imports:
                    # Resolve the path
                    current_dir = file_path.parent
                    resolved_path = (current_dir / import_path).resolve()
                    
                    # Check if file exists (try different extensions)
                    possible_files = [
                        resolved_path,
                        resolved_path.with_suffix('.js'),
                        resolved_path.with_suffix('.jsx'),
                        resolved_path / 'index.js',
                        resolved_path / 'index.jsx'
                    ]
                    
                    if not any(p.exists() for p in possible_files):
                        relative_issues.append({
                            'file': str(file_path),
                            'import_path': import_path,
                            'resolved_path': str(resolved_path),
                            'issue': 'File not found'
                        })
                
            except Exception as e:
                print(f"❌ Error checking {file_path}: {e}")
        
        if relative_issues:
            print("❌ Relative Import Issues Found:")
            for issue in relative_issues:
                print(f"   {Path(issue['file']).name}: {issue['import_path']} -> {issue['issue']}")
        else:
            print("✅ All relative imports resolve correctly")
        
        return relative_issues
    
    def audit_component_exports(self):
        """Audit component exports and imports"""
        print("\n🔍 AUDITING COMPONENT EXPORTS")
        print("-" * 50)
        
        jsx_files = self.find_all_jsx_files()
        export_issues = []
        
        # Map of files and their exports
        exports_map = {}
        
        for file_path in jsx_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find default exports
                default_exports = re.findall(
                    r'export\s+default\s+(\w+)',
                    content
                )
                
                # Find named exports
                named_exports = re.findall(
                    r'export\s+(?:const|function|class)\s+(\w+)',
                    content
                )
                
                # Find export { ... } statements
                export_statements = re.findall(
                    r'export\s*{\s*([^}]+)\s*}',
                    content
                )
                
                all_exports = default_exports + named_exports
                for stmt in export_statements:
                    all_exports.extend([e.strip() for e in stmt.split(',')])
                
                exports_map[str(file_path)] = all_exports
                
            except Exception as e:
                print(f"❌ Error checking exports in {file_path}: {e}")
        
        # Check if imported components exist
        for file_path in jsx_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find component imports from relative paths
                component_imports = re.findall(
                    r'import\s+(\w+)\s+from\s+[\'"](\.\./[^\'"]+)[\'"]',
                    content
                )
                
                for component_name, import_path in component_imports:
                    # Resolve the path
                    current_dir = file_path.parent
                    resolved_path = (current_dir / import_path).resolve()
                    
                    # Check if the component is exported from that file
                    found_export = False
                    for export_file, exports in exports_map.items():
                        if Path(export_file).resolve() == resolved_path or \
                           Path(export_file).resolve() == resolved_path.with_suffix('.jsx') or \
                           Path(export_file).resolve() == resolved_path.with_suffix('.js'):
                            if component_name in exports:
                                found_export = True
                                break
                    
                    if not found_export:
                        export_issues.append({
                            'file': str(file_path),
                            'component': component_name,
                            'import_path': import_path,
                            'issue': 'Component not exported from target file'
                        })
                
            except Exception as e:
                print(f"❌ Error checking component imports in {file_path}: {e}")
        
        if export_issues:
            print("❌ Component Export Issues Found:")
            for issue in export_issues:
                print(f"   {Path(issue['file']).name}: {issue['component']} from {issue['import_path']}")
        else:
            print("✅ All component imports have corresponding exports")
        
        return export_issues
    
    def fix_memory_icon_imports(self):
        """Fix Memory icon imports automatically"""
        print("\n🔧 FIXING MEMORY ICON IMPORTS")
        print("-" * 50)
        
        jsx_files = self.find_all_jsx_files()
        fixed_files = []
        
        for file_path in jsx_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix Memory in imports
                content = re.sub(
                    r'(\s+)Memory,',
                    r'\1MemoryStick,',
                    content
                )
                
                # Fix Memory in JSX
                content = re.sub(
                    r'<Memory\s',
                    r'<MemoryStick ',
                    content
                )
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files.append(str(file_path))
                    print(f"✅ Fixed Memory imports in {file_path.name}")
                
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
        
        return fixed_files
    
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE IMPORT AUDIT REPORT")
        print("=" * 70)
        
        # Run all audits
        lucide_issues = self.audit_lucide_react_imports()
        relative_issues = self.audit_relative_imports()
        export_issues = self.audit_component_exports()
        
        # Fix Memory icons
        fixed_files = self.fix_memory_icon_imports()
        
        # Summary
        total_issues = len(lucide_issues) + len(relative_issues) + len(export_issues)
        
        print(f"\n🎯 AUDIT SUMMARY:")
        print(f"   Lucide-React Issues: {len(lucide_issues)}")
        print(f"   Relative Import Issues: {len(relative_issues)}")
        print(f"   Component Export Issues: {len(export_issues)}")
        print(f"   Total Issues: {total_issues}")
        print(f"   Files Fixed: {len(fixed_files)}")
        
        if total_issues == 0:
            print("\n🎉 ALL IMPORT ISSUES RESOLVED!")
            print("✅ Frontend imports are clean and functional")
        else:
            print(f"\n⚠️ {total_issues} issues need attention")
        
        # Save detailed report
        report = {
            'timestamp': str(Path().resolve()),
            'lucide_issues': lucide_issues,
            'relative_issues': relative_issues,
            'export_issues': export_issues,
            'fixed_files': fixed_files,
            'total_issues': total_issues
        }
        
        with open('import_audit_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: import_audit_report.json")
        
        return total_issues == 0

def main():
    auditor = ImportAuditor()
    success = auditor.generate_audit_report()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
