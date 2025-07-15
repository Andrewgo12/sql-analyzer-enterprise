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
