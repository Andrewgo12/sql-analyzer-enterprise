#!/usr/bin/env python3
"""
Python Code Optimization Analysis
Comprehensive review of Python code for efficiency, dead code removal, and maximum utilization
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, Counter

class PythonOptimizer:
    """Analyze and optimize Python code"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.analysis_results = {
            'dead_code_analysis': {},
            'efficiency_analysis': {},
            'utilization_analysis': {},
            'optimization_recommendations': []
        }
    
    def analyze_python_code(self) -> Dict[str, Any]:
        """Comprehensive Python code analysis"""
        print("🐍 PYTHON CODE OPTIMIZATION ANALYSIS")
        print("=" * 50)
        
        self._discover_python_files()
        self._analyze_dead_code()
        self._analyze_function_efficiency()
        self._analyze_code_utilization()
        self._generate_optimization_plan()
        
        return self.analysis_results
    
    def _discover_python_files(self):
        """Discover all Python files"""
        print("📁 Discovering Python files...")
        
        for py_file in self.project_root.rglob("*.py"):
            if not any(exclude in str(py_file) for exclude in ['__pycache__', '.venv', 'node_modules']):
                self.python_files.append(py_file)
        
        print(f"Found {len(self.python_files)} Python files")
    
    def _analyze_dead_code(self):
        """Identify dead/unused code"""
        print("🔍 Analyzing dead code...")
        
        all_functions = {}
        function_calls = defaultdict(set)
        unused_imports = []
        dead_functions = []
        
        # First pass: collect all function definitions and calls
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Collect function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_key = f"{py_file}:{node.name}"
                        all_functions[func_key] = {
                            'file': str(py_file),
                            'name': node.name,
                            'line': node.lineno,
                            'is_private': node.name.startswith('_'),
                            'is_dunder': node.name.startswith('__') and node.name.endswith('__'),
                            'docstring': ast.get_docstring(node) is not None
                        }
                    
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            function_calls[node.func.id].add(str(py_file))
                        elif isinstance(node.func, ast.Attribute):
                            function_calls[node.func.attr].add(str(py_file))
                
                # Check for unused imports
                imports_used = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        imports_used.add(node.id)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name not in imports_used:
                                unused_imports.append({
                                    'file': str(py_file),
                                    'import': alias.name,
                                    'line': node.lineno
                                })
            
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
        
        # Second pass: identify unused functions
        for func_key, func_info in all_functions.items():
            func_name = func_info['name']
            
            # Skip special methods and main functions
            if func_info['is_dunder'] or func_name == 'main':
                continue
            
            # Check if function is called
            if func_name not in function_calls or len(function_calls[func_name]) == 0:
                # Additional check: look for string references
                is_referenced = False
                for py_file in self.python_files:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if func_name in content and content.count(func_name) > 1:
                            is_referenced = True
                            break
                    except:
                        pass
                
                if not is_referenced:
                    dead_functions.append(func_info)
        
        self.analysis_results['dead_code_analysis'] = {
            'total_functions': len(all_functions),
            'dead_functions': dead_functions,
            'unused_imports': unused_imports,
            'dead_code_percentage': len(dead_functions) / len(all_functions) * 100 if all_functions else 0
        }
    
    def _analyze_function_efficiency(self):
        """Analyze function efficiency patterns"""
        print("⚡ Analyzing function efficiency...")
        
        inefficient_patterns = []
        performance_issues = []
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        issues = self._check_function_efficiency(node, content)
                        if issues:
                            inefficient_patterns.extend([{
                                'file': str(py_file),
                                'function': node.name,
                                'line': node.lineno,
                                **issue
                            } for issue in issues])
            
            except Exception as e:
                print(f"Error analyzing efficiency in {py_file}: {e}")
        
        self.analysis_results['efficiency_analysis'] = {
            'inefficient_patterns': inefficient_patterns,
            'total_issues': len(inefficient_patterns)
        }
    
    def _check_function_efficiency(self, node: ast.FunctionDef, content: str) -> List[Dict[str, Any]]:
        """Check specific function for efficiency issues"""
        issues = []
        
        # Get function source
        func_lines = content.splitlines()[node.lineno-1:node.end_lineno if hasattr(node, 'end_lineno') else node.lineno+20]
        func_source = '\n'.join(func_lines)
        
        # Check for nested loops
        loop_depth = 0
        max_loop_depth = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                loop_depth += 1
                max_loop_depth = max(max_loop_depth, loop_depth)
        
        if max_loop_depth > 2:
            issues.append({
                'type': 'nested_loops',
                'severity': 'high',
                'description': f'Nested loops detected (depth: {max_loop_depth})',
                'recommendation': 'Consider optimizing with list comprehensions or vectorized operations'
            })
        
        # Check for string concatenation in loops
        if 'for' in func_source and '+=' in func_source and any(str_op in func_source for str_op in ['str(', '"', "'"]):
            issues.append({
                'type': 'string_concatenation',
                'severity': 'medium',
                'description': 'String concatenation in loop detected',
                'recommendation': 'Use join() or f-strings for better performance'
            })
        
        # Check for repeated database queries
        if 'for' in func_source and any(db_op in func_source for db_op in ['query', 'execute', 'fetch', 'cursor']):
            issues.append({
                'type': 'db_queries_in_loop',
                'severity': 'high',
                'description': 'Database queries in loop detected',
                'recommendation': 'Batch queries or use bulk operations'
            })
        
        # Check for inefficient data structures
        if '.append(' in func_source and 'for' in func_source:
            if func_source.count('.append(') > 5:
                issues.append({
                    'type': 'inefficient_append',
                    'severity': 'medium',
                    'description': 'Multiple append operations in loop',
                    'recommendation': 'Consider list comprehension or pre-allocation'
                })
        
        # Check for synchronous operations that should be async
        if any(sync_op in func_source for sync_op in ['requests.get', 'requests.post', 'time.sleep']):
            if 'async' not in func_source:
                issues.append({
                    'type': 'blocking_operations',
                    'severity': 'medium',
                    'description': 'Blocking operations detected',
                    'recommendation': 'Consider using async/await for I/O operations'
                })
        
        return issues
    
    def _analyze_code_utilization(self):
        """Analyze how well code is being utilized"""
        print("📊 Analyzing code utilization...")
        
        utilization_stats = {
            'total_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'code_lines': 0,
            'docstring_lines': 0,
            'import_lines': 0
        }
        
        file_stats = {}
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                file_stat = {
                    'total_lines': len(lines),
                    'comment_lines': 0,
                    'blank_lines': 0,
                    'code_lines': 0,
                    'docstring_lines': 0,
                    'import_lines': 0
                }
                
                in_docstring = False
                docstring_quote = None
                
                for line in lines:
                    stripped = line.strip()
                    
                    if not stripped:
                        file_stat['blank_lines'] += 1
                    elif stripped.startswith('#'):
                        file_stat['comment_lines'] += 1
                    elif stripped.startswith(('import ', 'from ')):
                        file_stat['import_lines'] += 1
                    elif '"""' in stripped or "'''" in stripped:
                        file_stat['docstring_lines'] += 1
                        if not in_docstring:
                            in_docstring = True
                            docstring_quote = '"""' if '"""' in stripped else "'''"
                        elif docstring_quote in stripped:
                            in_docstring = False
                    elif in_docstring:
                        file_stat['docstring_lines'] += 1
                    else:
                        file_stat['code_lines'] += 1
                
                file_stats[str(py_file)] = file_stat
                
                # Add to totals
                for key in utilization_stats:
                    utilization_stats[key] += file_stat[key]
            
            except Exception as e:
                print(f"Error analyzing utilization in {py_file}: {e}")
        
        # Calculate utilization percentages
        if utilization_stats['total_lines'] > 0:
            utilization_percentages = {
                'code_percentage': utilization_stats['code_lines'] / utilization_stats['total_lines'] * 100,
                'comment_percentage': utilization_stats['comment_lines'] / utilization_stats['total_lines'] * 100,
                'docstring_percentage': utilization_stats['docstring_lines'] / utilization_stats['total_lines'] * 100,
                'blank_percentage': utilization_stats['blank_lines'] / utilization_stats['total_lines'] * 100
            }
        else:
            utilization_percentages = {}
        
        self.analysis_results['utilization_analysis'] = {
            'overall_stats': utilization_stats,
            'percentages': utilization_percentages,
            'file_stats': file_stats,
            'code_density': utilization_percentages.get('code_percentage', 0)
        }
    
    def _generate_optimization_plan(self):
        """Generate comprehensive optimization recommendations"""
        print("📋 Generating optimization plan...")
        
        recommendations = []
        
        # Dead code removal
        dead_functions = self.analysis_results['dead_code_analysis']['dead_functions']
        if dead_functions:
            recommendations.append({
                'category': 'Dead Code Removal',
                'priority': 'HIGH',
                'impact': 'High',
                'effort': 'Low',
                'description': f'Remove {len(dead_functions)} unused functions',
                'actions': [
                    f'Delete function "{func["name"]}" from {func["file"]}' 
                    for func in dead_functions[:5]  # Show first 5
                ],
                'benefits': ['Reduced codebase size', 'Improved maintainability', 'Faster builds']
            })
        
        # Efficiency improvements
        inefficient_patterns = self.analysis_results['efficiency_analysis']['inefficient_patterns']
        if inefficient_patterns:
            high_priority_issues = [p for p in inefficient_patterns if p.get('severity') == 'high']
            if high_priority_issues:
                recommendations.append({
                    'category': 'Performance Optimization',
                    'priority': 'HIGH',
                    'impact': 'High',
                    'effort': 'Medium',
                    'description': f'Fix {len(high_priority_issues)} high-priority performance issues',
                    'actions': [
                        f'{issue["type"]}: {issue["recommendation"]}' 
                        for issue in high_priority_issues[:3]
                    ],
                    'benefits': ['Improved performance', 'Better scalability', 'Reduced resource usage']
                })
        
        # Code utilization improvements
        code_density = self.analysis_results['utilization_analysis']['code_density']
        if code_density < 60:
            recommendations.append({
                'category': 'Code Density Improvement',
                'priority': 'MEDIUM',
                'impact': 'Medium',
                'effort': 'Medium',
                'description': f'Improve code density from {code_density:.1f}% to >60%',
                'actions': [
                    'Remove excessive blank lines',
                    'Consolidate related functions',
                    'Remove redundant comments',
                    'Optimize import statements'
                ],
                'benefits': ['More focused codebase', 'Easier navigation', 'Better readability']
            })
        
        self.analysis_results['optimization_recommendations'] = recommendations

def main():
    """Run Python optimization analysis"""
    optimizer = PythonOptimizer()
    results = optimizer.analyze_python_code()
    
    # Save results
    with open('python_optimization_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 PYTHON OPTIMIZATION SUMMARY")
    print("=" * 50)
    
    dead_code = results['dead_code_analysis']
    print(f"\n🗑️ DEAD CODE ANALYSIS:")
    print(f"  • Total functions: {dead_code['total_functions']}")
    print(f"  • Dead functions: {len(dead_code['dead_functions'])}")
    print(f"  • Dead code percentage: {dead_code['dead_code_percentage']:.1f}%")
    
    efficiency = results['efficiency_analysis']
    print(f"\n⚡ EFFICIENCY ANALYSIS:")
    print(f"  • Inefficient patterns found: {efficiency['total_issues']}")
    
    utilization = results['utilization_analysis']
    print(f"\n📊 CODE UTILIZATION:")
    print(f"  • Total lines: {utilization['overall_stats']['total_lines']:,}")
    print(f"  • Code density: {utilization['code_density']:.1f}%")
    
    recommendations = results['optimization_recommendations']
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS: {len(recommendations)}")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['category']} ({rec['priority']} priority)")
        print(f"     Impact: {rec['impact']}, Effort: {rec['effort']}")
    
    print(f"\n✅ Analysis complete! Detailed results saved to python_optimization_analysis.json")

if __name__ == '__main__':
    main()
