#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Precise Memory Icon Fix
Fix only actual Memory icon imports, not memory properties
"""

import os
import re

def fix_memory_imports_precise():
    """Fix Memory icon imports with precision"""
    
    target_files = [
        'frontend/src/components/MetricsSystem.jsx',
        'frontend/src/components/SystemHealthMonitor.jsx',
        'frontend/src/components/views/MetricsView.jsx',
        'frontend/src/components/views/TerminalView.jsx'
    ]
    
    print("🔧 Precise Memory Icon Import Fixer")
    print("=" * 50)
    
    fixed_files = []
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Memory in import statement (very specific)
            content = re.sub(
                r'(\s+)Memory,(\s*\n)',
                r'\1MemoryStick,\2',
                content
            )
            
            # Fix 2: Memory in import destructuring
            content = re.sub(
                r'(import\s*{[^}]*),\s*Memory\s*,([^}]*})',
                r'\1, MemoryStick,\2',
                content
            )
            
            # Fix 3: Memory at start of import list
            content = re.sub(
                r'(import\s*{\s*)Memory\s*,',
                r'\1MemoryStick,',
                content
            )
            
            # Fix 4: Memory at end of import list
            content = re.sub(
                r',\s*Memory(\s*}\s*from)',
                r', MemoryStick\1',
                content
            )
            
            # Fix 5: Memory as JSX component
            content = re.sub(
                r'<Memory(\s+[^>]*>|>)',
                r'<MemoryStick\1',
                content
            )
            
            # Fix 6: Memory component with props
            content = re.sub(
                r'<Memory\s+size=',
                r'<MemoryStick size=',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path)
                print(f"✅ Fixed: {os.path.basename(file_path)}")
            else:
                print(f"✅ No changes needed: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def verify_memory_fixes():
    """Verify that Memory imports are actually fixed"""
    
    target_files = [
        'frontend/src/components/MetricsSystem.jsx',
        'frontend/src/components/SystemHealthMonitor.jsx',
        'frontend/src/components/views/MetricsView.jsx',
        'frontend/src/components/views/TerminalView.jsx'
    ]
    
    print("\n🔍 Verifying Memory Import Fixes")
    print("-" * 40)
    
    issues_found = []
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for Memory in import statements only
                if 'import' in line and 'lucide-react' in line:
                    if re.search(r'\bMemory\b', line) and 'MemoryStick' not in line:
                        issues_found.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip()
                        })
                
                # Check for Memory JSX usage
                elif re.search(r'<Memory\s', line):
                    issues_found.append({
                        'file': file_path,
                        'line': i,
                        'content': line.strip()
                    })
            
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
    
    if issues_found:
        print("❌ Memory import issues still found:")
        for issue in issues_found:
            print(f"   {os.path.basename(issue['file'])}:{issue['line']} - {issue['content']}")
    else:
        print("✅ All Memory import issues resolved!")
    
    return len(issues_found) == 0

def check_lucide_react_imports():
    """Check all lucide-react imports for correctness"""
    
    target_files = [
        'frontend/src/components/MetricsSystem.jsx',
        'frontend/src/components/SystemHealthMonitor.jsx',
        'frontend/src/components/views/MetricsView.jsx',
        'frontend/src/components/views/TerminalView.jsx'
    ]
    
    print("\n📦 Checking Lucide React Imports")
    print("-" * 40)
    
    for file_path in target_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find lucide-react import
            import_match = re.search(
                r'import\s*{([^}]+)}\s*from\s*[\'"]lucide-react[\'"]',
                content,
                re.MULTILINE
            )
            
            if import_match:
                imports = import_match.group(1)
                if 'MemoryStick' in imports:
                    print(f"✅ {os.path.basename(file_path)}: MemoryStick imported correctly")
                elif 'Memory' in imports:
                    print(f"❌ {os.path.basename(file_path)}: Still importing Memory")
                else:
                    print(f"ℹ️ {os.path.basename(file_path)}: No memory-related imports")
            else:
                print(f"⚠️ {os.path.basename(file_path)}: No lucide-react import found")
                
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")

def main():
    print("🚀 SQL Analyzer Enterprise - Precise Memory Fix")
    print("=" * 60)
    
    # Step 1: Fix Memory imports
    fixed_files = fix_memory_imports_precise()
    
    # Step 2: Verify fixes
    all_fixed = verify_memory_fixes()
    
    # Step 3: Check lucide-react imports
    check_lucide_react_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PRECISE MEMORY FIX SUMMARY")
    print("=" * 60)
    
    if fixed_files:
        print(f"🔧 Fixed {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"   - {os.path.basename(file)}")
    else:
        print("ℹ️ No files needed fixing")
    
    if all_fixed:
        print("✅ All Memory import issues resolved!")
        print("🚀 Frontend should now compile without Memory icon errors!")
    else:
        print("❌ Some Memory import issues remain")
        print("🔧 Manual intervention may be required")
    
    return all_fixed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
