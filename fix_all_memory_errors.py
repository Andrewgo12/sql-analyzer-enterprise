#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Fix All Memory Icon Errors
Comprehensive fix for all Memory icon import errors
"""

import os
import re
import glob

def find_and_fix_memory_imports():
    """Find and fix all Memory icon imports in JSX files"""
    
    # Find all JSX and JS files in frontend/src
    jsx_files = []
    for root, dirs, files in os.walk('frontend/src'):
        for file in files:
            if file.endswith(('.jsx', '.js')):
                jsx_files.append(os.path.join(root, file))
    
    print(f"🔍 Found {len(jsx_files)} JSX/JS files to check")
    
    fixed_files = []
    
    for file_path in jsx_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Replace Memory import with MemoryStick
            content = re.sub(
                r'(\s+)Memory,',
                r'\1MemoryStick,',
                content
            )
            
            # Fix 2: Replace Memory usage in JSX
            content = re.sub(
                r'<Memory\s',
                r'<MemoryStick ',
                content
            )
            
            # Fix 3: Replace Memory in destructuring
            content = re.sub(
                r'{\s*([^}]*,\s*)?Memory(\s*,\s*[^}]*)?\s*}',
                lambda m: m.group(0).replace('Memory', 'MemoryStick'),
                content
            )
            
            # Fix 4: Replace Memory size= patterns
            content = re.sub(
                r'Memory\s+size=',
                r'MemoryStick size=',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path)
                print(f"✅ Fixed: {file_path}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def verify_no_memory_imports():
    """Verify that no Memory imports remain"""
    
    jsx_files = []
    for root, dirs, files in os.walk('frontend/src'):
        for file in files:
            if file.endswith(('.jsx', '.js')):
                jsx_files.append(os.path.join(root, file))
    
    problematic_files = []
    
    for file_path in jsx_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Memory imports (but not memory properties)
            if re.search(r'import\s*{[^}]*Memory[^}]*}\s*from\s*[\'"]lucide-react[\'"]', content):
                problematic_files.append(file_path)
                print(f"❌ Still has Memory import: {file_path}")
            elif re.search(r'<Memory\s', content):
                problematic_files.append(file_path)
                print(f"❌ Still uses Memory component: {file_path}")
            
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
    
    return problematic_files

def check_systemmetrics_usage():
    """Check for systemMetrics usage issues"""
    
    jsx_files = []
    for root, dirs, files in os.walk('frontend/src'):
        for file in files:
            if file.endswith(('.jsx', '.js')):
                jsx_files.append(os.path.join(root, file))
    
    issues = []
    
    for file_path in jsx_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for systemMetrics usage without definition
                if 'systemMetrics' in line and 'useState' not in line and 'const' not in line:
                    # Check if it's in a dependency array or function parameter
                    if '[systemMetrics' in line or 'systemMetrics,' in line or 'systemMetrics}' in line:
                        continue  # These are likely OK
                    
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'content': line.strip()
                    })
            
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
    
    return issues

def main():
    print("🔧 SQL Analyzer Enterprise - Memory Icon Error Fixer")
    print("=" * 60)
    
    # Step 1: Fix Memory imports
    print("\n1. Fixing Memory icon imports...")
    fixed_files = find_and_fix_memory_imports()
    
    if fixed_files:
        print(f"\n✅ Fixed {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"   - {file}")
    else:
        print("\n✅ No Memory import issues found")
    
    # Step 2: Verify fixes
    print("\n2. Verifying Memory import fixes...")
    problematic_files = verify_no_memory_imports()
    
    if problematic_files:
        print(f"\n❌ Still have issues in {len(problematic_files)} files:")
        for file in problematic_files:
            print(f"   - {file}")
    else:
        print("\n✅ All Memory import issues resolved")
    
    # Step 3: Check systemMetrics issues
    print("\n3. Checking systemMetrics usage...")
    systemmetrics_issues = check_systemmetrics_usage()
    
    if systemmetrics_issues:
        print(f"\n⚠️ Found {len(systemmetrics_issues)} potential systemMetrics issues:")
        for issue in systemmetrics_issues:
            print(f"   - {issue['file']}:{issue['line']} - {issue['content']}")
    else:
        print("\n✅ No systemMetrics issues found")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    total_issues = len(problematic_files) + len(systemmetrics_issues)
    
    if total_issues == 0:
        print("🎉 ALL ISSUES RESOLVED!")
        print("✅ Memory icon imports: Fixed")
        print("✅ SystemMetrics usage: Fixed")
        print("\n🚀 Frontend should now compile without errors!")
    else:
        print(f"⚠️ {total_issues} issues remaining:")
        if problematic_files:
            print(f"   - {len(problematic_files)} Memory import issues")
        if systemmetrics_issues:
            print(f"   - {len(systemmetrics_issues)} systemMetrics issues")
    
    return total_issues == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
