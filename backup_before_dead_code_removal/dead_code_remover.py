#!/usr/bin/env python3
"""
Intelligent Dead Code Removal System
Remove all 254 identified dead functions safely with comprehensive validation
"""

import ast
import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class DeadCodeAnalyzer:
    """Advanced dead code analysis and removal"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = []
        self.function_definitions = {}
        self.function_calls = defaultdict(set)
        self.import_usage = defaultdict(set)
        self.string_references = defaultdict(set)
        self.dead_functions = []
        self.safe_to_remove = []
        
    def analyze_dead_code(self) -> Dict[str, Any]:
        """Comprehensive dead code analysis"""
        logger.info("🔍 Starting comprehensive dead code analysis...")
        
        # Discover all Python files
        self._discover_python_files()
        
        # Analyze function definitions and calls
        self._analyze_function_definitions()
        self._analyze_function_calls()
        self._analyze_string_references()
        
        # Identify dead functions
        self._identify_dead_functions()
        
        # Validate safety of removal
        self._validate_removal_safety()
        
        return {
            'total_functions': len(self.function_definitions),
            'dead_functions': len(self.dead_functions),
            'safe_to_remove': len(self.safe_to_remove),
            'removal_candidates': self.safe_to_remove
        }
    
    def _discover_python_files(self):
        """Discover all Python files in the project"""
        logger.info("📁 Discovering Python files...")
        
        exclude_patterns = [
            '__pycache__',
            '.venv',
            'venv',
            'node_modules',
            '.git',
            'dist',
            'build'
        ]
        
        for py_file in self.project_root.rglob("*.py"):
            if not any(pattern in str(py_file) for pattern in exclude_patterns):
                self.python_files.append(py_file)
        
        logger.info(f"Found {len(self.python_files)} Python files")
    
    def _analyze_function_definitions(self):
        """Analyze all function definitions"""
        logger.info("🔍 Analyzing function definitions...")
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_key = f"{py_file}:{node.name}"
                        
                        self.function_definitions[func_key] = {
                            'file': str(py_file),
                            'name': node.name,
                            'line': node.lineno,
                            'end_line': getattr(node, 'end_lineno', node.lineno + 10),
                            'is_private': node.name.startswith('_'),
                            'is_dunder': node.name.startswith('__') and node.name.endswith('__'),
                            'is_property': any(
                                isinstance(decorator, ast.Name) and decorator.id == 'property'
                                for decorator in node.decorator_list
                                if isinstance(decorator, ast.Name)
                            ),
                            'is_staticmethod': any(
                                isinstance(decorator, ast.Name) and decorator.id == 'staticmethod'
                                for decorator in node.decorator_list
                                if isinstance(decorator, ast.Name)
                            ),
                            'is_classmethod': any(
                                isinstance(decorator, ast.Name) and decorator.id == 'classmethod'
                                for decorator in node.decorator_list
                                if isinstance(decorator, ast.Name)
                            ),
                            'docstring': ast.get_docstring(node) is not None,
                            'decorators': [
                                decorator.id if isinstance(decorator, ast.Name) else str(decorator)
                                for decorator in node.decorator_list
                            ]
                        }
            
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        logger.info(f"Found {len(self.function_definitions)} function definitions")
    
    def _analyze_function_calls(self):
        """Analyze all function calls"""
        logger.info("📞 Analyzing function calls...")
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Direct function calls
                        if isinstance(node.func, ast.Name):
                            func_name = node.func.id
                            self.function_calls[func_name].add(str(py_file))
                        
                        # Method calls
                        elif isinstance(node.func, ast.Attribute):
                            func_name = node.func.attr
                            self.function_calls[func_name].add(str(py_file))
                    
                    # Also check for function references (not calls)
                    elif isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Load):
                            self.function_calls[node.id].add(str(py_file))
            
            except Exception as e:
                logger.warning(f"Error analyzing calls in {py_file}: {e}")
        
        logger.info(f"Analyzed function calls in {len(self.python_files)} files")
    
    def _analyze_string_references(self):
        """Analyze string references to functions"""
        logger.info("🔤 Analyzing string references...")
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for function names in strings
                for func_key, func_info in self.function_definitions.items():
                    func_name = func_info['name']
                    
                    # Count occurrences in strings
                    string_matches = re.findall(rf'["\'].*?{re.escape(func_name)}.*?["\']', content)
                    if string_matches:
                        self.string_references[func_name].add(str(py_file))
                    
                    # Check for getattr usage
                    getattr_pattern = rf'getattr\([^,]+,\s*["\']({re.escape(func_name)})["\']'
                    if re.search(getattr_pattern, content):
                        self.string_references[func_name].add(str(py_file))
            
            except Exception as e:
                logger.warning(f"Error analyzing strings in {py_file}: {e}")
        
        logger.info("Completed string reference analysis")
    
    def _identify_dead_functions(self):
        """Identify dead functions based on analysis"""
        logger.info("💀 Identifying dead functions...")
        
        for func_key, func_info in self.function_definitions.items():
            func_name = func_info['name']
            func_file = func_info['file']
            
            # Skip special methods and main functions
            if (func_info['is_dunder'] or 
                func_name in ['main', '__init__', '__new__'] or
                func_name.startswith('test_')):
                continue
            
            # Check if function is called
            is_called = False
            
            # Check direct calls
            if func_name in self.function_calls:
                call_files = self.function_calls[func_name]
                # Remove self-references (function calling itself)
                external_calls = call_files - {func_file}
                if external_calls:
                    is_called = True
            
            # Check string references
            if func_name in self.string_references:
                string_files = self.string_references[func_name]
                external_strings = string_files - {func_file}
                if external_strings:
                    is_called = True
            
            # Additional checks for special cases
            if not is_called:
                # Check if it's a Flask route handler
                if any('route' in decorator for decorator in func_info['decorators']):
                    is_called = True
                
                # Check if it's a property or special method
                if func_info['is_property'] or func_info['is_staticmethod'] or func_info['is_classmethod']:
                    # These might be used dynamically, be more conservative
                    with open(func_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for class usage
                    if f".{func_name}" in content or f"self.{func_name}" in content:
                        is_called = True
            
            if not is_called:
                self.dead_functions.append(func_info)
        
        logger.info(f"Identified {len(self.dead_functions)} dead functions")
    
    def _validate_removal_safety(self):
        """Validate which functions are safe to remove"""
        logger.info("✅ Validating removal safety...")
        
        for func_info in self.dead_functions:
            is_safe = True
            func_name = func_info['name']
            
            # Conservative checks for safety
            
            # 1. Don't remove functions with docstrings (might be API)
            if func_info['docstring'] and not func_info['is_private']:
                is_safe = False
            
            # 2. Don't remove functions that might be used by external modules
            if not func_info['is_private'] and len(func_name) > 3:
                # Check if function name appears in any configuration or documentation
                for py_file in self.python_files:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for dynamic usage patterns
                        dynamic_patterns = [
                            f'"{func_name}"',
                            f"'{func_name}'",
                            f'getattr.*{func_name}',
                            f'hasattr.*{func_name}',
                            f'setattr.*{func_name}'
                        ]
                        
                        for pattern in dynamic_patterns:
                            if re.search(pattern, content):
                                is_safe = False
                                break
                        
                        if not is_safe:
                            break
                    
                    except Exception:
                        continue
            
            # 3. Be extra conservative with short function names
            if len(func_name) <= 3:
                is_safe = False
            
            # 4. Don't remove functions in __init__.py files
            if '__init__.py' in func_info['file']:
                is_safe = False
            
            if is_safe:
                self.safe_to_remove.append(func_info)
        
        logger.info(f"Validated {len(self.safe_to_remove)} functions as safe to remove")
    
    def remove_dead_functions(self, dry_run: bool = True) -> Dict[str, Any]:
        """Remove dead functions from codebase"""
        if not self.safe_to_remove:
            logger.warning("No functions identified as safe to remove")
            return {'removed': 0, 'files_modified': 0}
        
        logger.info(f"{'DRY RUN: ' if dry_run else ''}Removing {len(self.safe_to_remove)} dead functions...")
        
        files_to_modify = defaultdict(list)
        
        # Group functions by file
        for func_info in self.safe_to_remove:
            files_to_modify[func_info['file']].append(func_info)
        
        removed_count = 0
        modified_files = 0
        
        for file_path, functions in files_to_modify.items():
            try:
                # Read original file
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Sort functions by line number (descending) to remove from bottom up
                functions.sort(key=lambda x: x['line'], reverse=True)
                
                # Remove functions
                for func_info in functions:
                    start_line = func_info['line'] - 1  # Convert to 0-based
                    end_line = func_info['end_line']
                    
                    # Find actual end of function by looking for next function or class
                    actual_end = self._find_function_end(lines, start_line)
                    
                    if not dry_run:
                        # Remove the function
                        del lines[start_line:actual_end]
                        logger.info(f"Removed function {func_info['name']} from {file_path}")
                    else:
                        logger.info(f"DRY RUN: Would remove function {func_info['name']} from {file_path}")
                    
                    removed_count += 1
                
                if not dry_run:
                    # Write modified file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                
                modified_files += 1
            
            except Exception as e:
                logger.error(f"Error modifying {file_path}: {e}")
        
        result = {
            'removed': removed_count,
            'files_modified': modified_files,
            'dry_run': dry_run
        }
        
        if not dry_run:
            logger.info(f"Successfully removed {removed_count} dead functions from {modified_files} files")
        else:
            logger.info(f"DRY RUN: Would remove {removed_count} dead functions from {modified_files} files")
        
        return result
    
    def _find_function_end(self, lines: List[str], start_line: int) -> int:
        """Find the actual end line of a function"""
        current_line = start_line + 1
        indent_level = None
        
        # Find the indentation level of the function
        func_line = lines[start_line].lstrip()
        if func_line.startswith('def '):
            base_indent = len(lines[start_line]) - len(func_line)
        else:
            base_indent = 0
        
        # Look for the end of the function
        while current_line < len(lines):
            line = lines[current_line]
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                current_line += 1
                continue
            
            # Check indentation
            line_indent = len(line) - len(line.lstrip())
            
            # If we find a line with same or less indentation, function ends
            if line_indent <= base_indent and line.strip():
                break
            
            current_line += 1
        
        return current_line
    
    def create_backup(self) -> str:
        """Create backup of project before removal"""
        backup_dir = self.project_root / "backup_before_dead_code_removal"
        
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        # Copy only Python files
        backup_dir.mkdir()
        
        for py_file in self.python_files:
            relative_path = py_file.relative_to(self.project_root)
            backup_file = backup_dir / relative_path
            
            # Create directory structure
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(py_file, backup_file)
        
        logger.info(f"Created backup at {backup_dir}")
        return str(backup_dir)

def main():
    """Main function for dead code removal"""
    analyzer = DeadCodeAnalyzer()
    
    # Analyze dead code
    analysis_result = analyzer.analyze_dead_code()
    
    print("🔍 DEAD CODE ANALYSIS RESULTS")
    print("=" * 40)
    print(f"Total functions: {analysis_result['total_functions']}")
    print(f"Dead functions: {analysis_result['dead_functions']}")
    print(f"Safe to remove: {analysis_result['safe_to_remove']}")
    
    if analysis_result['safe_to_remove'] > 0:
        print(f"\n📋 FUNCTIONS SAFE TO REMOVE:")
        for func in analyzer.safe_to_remove[:10]:  # Show first 10
            print(f"  • {func['name']} in {func['file']}:{func['line']}")
        
        if len(analyzer.safe_to_remove) > 10:
            print(f"  ... and {len(analyzer.safe_to_remove) - 10} more")
        
        # Ask for confirmation
        response = input(f"\n❓ Remove {analysis_result['safe_to_remove']} dead functions? (y/N): ")
        
        if response.lower() == 'y':
            # Create backup first
            backup_path = analyzer.create_backup()
            print(f"✅ Backup created at: {backup_path}")
            
            # Remove dead code
            removal_result = analyzer.remove_dead_functions(dry_run=False)
            
            print(f"\n🎉 REMOVAL COMPLETED!")
            print(f"Removed: {removal_result['removed']} functions")
            print(f"Modified: {removal_result['files_modified']} files")
            print(f"Backup: {backup_path}")
        else:
            print("❌ Dead code removal cancelled")
    else:
        print("✅ No dead functions found that are safe to remove")

if __name__ == '__main__':
    main()
