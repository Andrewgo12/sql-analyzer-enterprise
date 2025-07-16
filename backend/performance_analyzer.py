#!/usr/bin/env python3
"""
PERFORMANCE ANALYZER - ENTERPRISE SQL PERFORMANCE OPTIMIZATION
Advanced query optimization and performance analysis engine
"""

import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OptimizationType(Enum):
    INDEX = "index"
    QUERY_REWRITE = "query_rewrite"
    JOIN_OPTIMIZATION = "join_optimization"
    SUBQUERY_OPTIMIZATION = "subquery_optimization"
    LIMIT_OPTIMIZATION = "limit_optimization"
    FUNCTION_OPTIMIZATION = "function_optimization"
    SCHEMA_OPTIMIZATION = "schema_optimization"

class PerformanceImpact(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PerformanceIssue:
    line: int
    issue_type: OptimizationType
    severity: PerformanceImpact
    title: str
    description: str
    current_code: str
    optimized_code: str
    estimated_improvement: str
    explanation: str

@dataclass
class IndexSuggestion:
    table: str
    columns: List[str]
    index_type: str
    reason: str
    estimated_benefit: str

class PerformanceAnalyzer:
    """Enterprise-grade SQL performance analyzer"""
    
    def __init__(self):
        self.expensive_functions = self._load_expensive_functions()
        self.join_patterns = self._load_join_patterns()
        self.optimization_rules = self._load_optimization_rules()
        
    def _load_expensive_functions(self) -> Dict[str, Dict[str, Any]]:
        """Load expensive SQL functions and their alternatives"""
        return {
            'SUBSTRING': {
                'cost': 'medium',
                'alternative': 'Use SUBSTR or optimize with proper indexing',
                'impact': PerformanceImpact.MEDIUM
            },
            'UPPER': {
                'cost': 'medium',
                'alternative': 'Use functional indexes or case-insensitive collation',
                'impact': PerformanceImpact.MEDIUM
            },
            'LOWER': {
                'cost': 'medium',
                'alternative': 'Use functional indexes or case-insensitive collation',
                'impact': PerformanceImpact.MEDIUM
            },
            'LIKE': {
                'cost': 'high',
                'alternative': 'Use full-text search or optimize with proper indexing',
                'impact': PerformanceImpact.HIGH
            },
            'REGEXP': {
                'cost': 'high',
                'alternative': 'Use simpler pattern matching or pre-process data',
                'impact': PerformanceImpact.HIGH
            },
            'RAND': {
                'cost': 'high',
                'alternative': 'Use application-level randomization',
                'impact': PerformanceImpact.HIGH
            }
        }
    
    def _load_join_patterns(self) -> List[Dict[str, Any]]:
        """Load join optimization patterns"""
        return [
            {
                'pattern': r'SELECT\s+\*\s+FROM.*?JOIN',
                'issue': 'SELECT * with JOIN',
                'optimization': 'Select only needed columns',
                'impact': PerformanceImpact.MEDIUM
            },
            {
                'pattern': r'LEFT\s+JOIN.*?WHERE.*?IS\s+NOT\s+NULL',
                'issue': 'LEFT JOIN with NOT NULL filter',
                'optimization': 'Use INNER JOIN instead',
                'impact': PerformanceImpact.HIGH
            },
            {
                'pattern': r'JOIN.*?ON.*?LIKE',
                'issue': 'JOIN with LIKE condition',
                'optimization': 'Use exact match or optimize with indexing',
                'impact': PerformanceImpact.HIGH
            }
        ]
    
    def _load_optimization_rules(self) -> List[Dict[str, Any]]:
        """Load general optimization rules"""
        return [
            {
                'pattern': r'SELECT\s+COUNT\(\*\)\s+FROM.*?WHERE',
                'rule': 'COUNT with WHERE',
                'suggestion': 'Consider using covering indexes',
                'impact': PerformanceImpact.MEDIUM
            },
            {
                'pattern': r'ORDER\s+BY.*?LIMIT\s+\d+',
                'rule': 'ORDER BY with LIMIT',
                'suggestion': 'Ensure proper indexing for ORDER BY columns',
                'impact': PerformanceImpact.HIGH
            },
            {
                'pattern': r'GROUP\s+BY.*?HAVING',
                'rule': 'GROUP BY with HAVING',
                'suggestion': 'Move conditions to WHERE clause when possible',
                'impact': PerformanceImpact.MEDIUM
            }
        ]
    
    def analyze(self, sql_content: str, database_engine: str = 'mysql') -> Dict[str, Any]:
        """
        Perform comprehensive performance analysis
        
        Args:
            sql_content: SQL code to analyze
            database_engine: Target database engine
            
        Returns:
            Performance analysis results
        """
        start_time = time.time()
        
        try:
            # Parse SQL statements
            statements = self._parse_statements(sql_content)
            
            # Analyze performance issues
            performance_issues = []
            index_suggestions = []
            
            for i, statement in enumerate(statements):
                # Analyze individual statement
                issues = self._analyze_statement_performance(statement, i + 1)
                performance_issues.extend(issues)
                
                # Generate index suggestions
                indexes = self._suggest_indexes(statement, i + 1)
                index_suggestions.extend(indexes)
            
            # Calculate performance metrics
            performance_score = self._calculate_performance_score(performance_issues)
            complexity_analysis = self._analyze_query_complexity(statements)
            execution_estimates = self._estimate_execution_times(statements)
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'processing_time': round(processing_time, 3),
                'database_engine': database_engine,
                'performance_score': performance_score,
                'overall_complexity': complexity_analysis['overall_complexity'],
                'performance_issues': [self._issue_to_dict(issue) for issue in performance_issues],
                'index_suggestions': [self._index_to_dict(idx) for idx in index_suggestions],
                'execution_estimates': execution_estimates,
                'complexity_analysis': complexity_analysis,
                'optimization_summary': self._generate_optimization_summary(performance_issues),
                'recommendations': self._generate_performance_recommendations(performance_issues, index_suggestions)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _parse_statements(self, sql: str) -> List[str]:
        """Parse SQL into individual statements"""
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Split by semicolon
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        return statements
    
    def _analyze_statement_performance(self, statement: str, line_num: int) -> List[PerformanceIssue]:
        """Analyze performance issues in a single statement"""
        issues = []
        statement_upper = statement.upper()
        
        # Check for SELECT * usage
        if re.search(r'SELECT\s+\*', statement_upper):
            issues.append(PerformanceIssue(
                line=line_num,
                issue_type=OptimizationType.QUERY_REWRITE,
                severity=PerformanceImpact.MEDIUM,
                title="SELECT * Usage",
                description="Using SELECT * retrieves all columns, which can be inefficient",
                current_code="SELECT *",
                optimized_code="SELECT column1, column2, ...",
                estimated_improvement="20-50% faster",
                explanation="Selecting only needed columns reduces data transfer and memory usage"
            ))
        
        # Check for missing LIMIT in SELECT statements
        if 'SELECT' in statement_upper and 'LIMIT' not in statement_upper and 'COUNT' not in statement_upper:
            issues.append(PerformanceIssue(
                line=line_num,
                issue_type=OptimizationType.LIMIT_OPTIMIZATION,
                severity=PerformanceImpact.HIGH,
                title="Missing LIMIT Clause",
                description="Large result sets without LIMIT can cause performance issues",
                current_code=statement[:50] + "...",
                optimized_code=statement[:50] + "... LIMIT 1000",
                estimated_improvement="50-90% faster for large tables",
                explanation="LIMIT prevents accidentally retrieving millions of rows"
            ))
        
        # Check for expensive functions
        for func_name, func_info in self.expensive_functions.items():
            if func_name in statement_upper:
                issues.append(PerformanceIssue(
                    line=line_num,
                    issue_type=OptimizationType.FUNCTION_OPTIMIZATION,
                    severity=func_info['impact'],
                    title=f"Expensive Function: {func_name}",
                    description=f"Function {func_name} can be expensive in WHERE clauses",
                    current_code=func_name,
                    optimized_code=func_info['alternative'],
                    estimated_improvement="10-80% faster",
                    explanation=f"Function {func_name} prevents index usage and requires full table scan"
                ))
        
        # Check for subquery optimization opportunities
        if 'IN (' in statement_upper and 'SELECT' in statement_upper:
            issues.append(PerformanceIssue(
                line=line_num,
                issue_type=OptimizationType.SUBQUERY_OPTIMIZATION,
                severity=PerformanceImpact.MEDIUM,
                title="Subquery in IN Clause",
                description="IN subqueries can often be optimized with JOINs",
                current_code="WHERE column IN (SELECT ...)",
                optimized_code="WHERE EXISTS (SELECT 1 FROM ...) or use JOIN",
                estimated_improvement="20-60% faster",
                explanation="EXISTS or JOINs are often more efficient than IN subqueries"
            ))
        
        # Check join patterns
        for pattern_info in self.join_patterns:
            if re.search(pattern_info['pattern'], statement_upper, re.IGNORECASE):
                issues.append(PerformanceIssue(
                    line=line_num,
                    issue_type=OptimizationType.JOIN_OPTIMIZATION,
                    severity=pattern_info['impact'],
                    title=pattern_info['issue'],
                    description=f"Join pattern that can be optimized: {pattern_info['issue']}",
                    current_code=pattern_info['pattern'],
                    optimized_code=pattern_info['optimization'],
                    estimated_improvement="30-70% faster",
                    explanation="Optimized join patterns reduce data processing overhead"
                ))
        
        # Check for ORDER BY without LIMIT
        if 'ORDER BY' in statement_upper and 'LIMIT' not in statement_upper:
            issues.append(PerformanceIssue(
                line=line_num,
                issue_type=OptimizationType.QUERY_REWRITE,
                severity=PerformanceImpact.MEDIUM,
                title="ORDER BY without LIMIT",
                description="Sorting large result sets without LIMIT is expensive",
                current_code="ORDER BY column",
                optimized_code="ORDER BY column LIMIT n",
                estimated_improvement="40-80% faster",
                explanation="Sorting is expensive; LIMIT reduces the sorting overhead"
            ))
        
        return issues
    
    def _suggest_indexes(self, statement: str, line_num: int) -> List[IndexSuggestion]:
        """Suggest indexes for better performance"""
        suggestions = []
        statement_upper = statement.upper()
        
        # Extract table names and WHERE conditions
        tables = self._extract_table_names(statement)
        where_columns = self._extract_where_columns(statement)
        join_columns = self._extract_join_columns(statement)
        order_columns = self._extract_order_columns(statement)
        
        # Suggest indexes for WHERE clauses
        for table, columns in where_columns.items():
            if columns:
                suggestions.append(IndexSuggestion(
                    table=table,
                    columns=columns,
                    index_type="BTREE",
                    reason="WHERE clause filtering",
                    estimated_benefit="50-90% query speedup"
                ))
        
        # Suggest indexes for JOIN conditions
        for table, columns in join_columns.items():
            if columns:
                suggestions.append(IndexSuggestion(
                    table=table,
                    columns=columns,
                    index_type="BTREE",
                    reason="JOIN condition optimization",
                    estimated_benefit="30-70% join speedup"
                ))
        
        # Suggest indexes for ORDER BY
        for table, columns in order_columns.items():
            if columns:
                suggestions.append(IndexSuggestion(
                    table=table,
                    columns=columns,
                    index_type="BTREE",
                    reason="ORDER BY optimization",
                    estimated_benefit="40-80% sorting speedup"
                ))
        
        return suggestions
    
    def _extract_table_names(self, statement: str) -> List[str]:
        """Extract table names from SQL statement"""
        tables = []
        
        # FROM clause
        from_match = re.search(r'FROM\s+(\w+)', statement, re.IGNORECASE)
        if from_match:
            tables.append(from_match.group(1))
        
        # JOIN clauses
        join_matches = re.findall(r'JOIN\s+(\w+)', statement, re.IGNORECASE)
        tables.extend(join_matches)
        
        return list(set(tables))
    
    def _extract_where_columns(self, statement: str) -> Dict[str, List[str]]:
        """Extract columns used in WHERE clauses"""
        where_columns = {}
        
        # Simple WHERE column extraction
        where_matches = re.findall(r'WHERE\s+(\w+)\.?(\w+)', statement, re.IGNORECASE)
        for match in where_matches:
            table = match[0] if match[1] else 'unknown'
            column = match[1] if match[1] else match[0]
            
            if table not in where_columns:
                where_columns[table] = []
            where_columns[table].append(column)
        
        return where_columns
    
    def _extract_join_columns(self, statement: str) -> Dict[str, List[str]]:
        """Extract columns used in JOIN conditions"""
        join_columns = {}
        
        # JOIN ON conditions
        join_matches = re.findall(r'JOIN\s+(\w+).*?ON\s+\w+\.(\w+)', statement, re.IGNORECASE)
        for match in join_matches:
            table = match[0]
            column = match[1]
            
            if table not in join_columns:
                join_columns[table] = []
            join_columns[table].append(column)
        
        return join_columns
    
    def _extract_order_columns(self, statement: str) -> Dict[str, List[str]]:
        """Extract columns used in ORDER BY"""
        order_columns = {}
        
        # ORDER BY columns
        order_matches = re.findall(r'ORDER\s+BY\s+(?:(\w+)\.)?(\w+)', statement, re.IGNORECASE)
        for match in order_matches:
            table = match[0] if match[0] else 'unknown'
            column = match[1]
            
            if table not in order_columns:
                order_columns[table] = []
            order_columns[table].append(column)
        
        return order_columns
    
    def _calculate_performance_score(self, issues: List[PerformanceIssue]) -> int:
        """Calculate performance score (0-100, higher is better)"""
        if not issues:
            return 100
        
        score = 100
        
        for issue in issues:
            if issue.severity == PerformanceImpact.CRITICAL:
                score -= 25
            elif issue.severity == PerformanceImpact.HIGH:
                score -= 15
            elif issue.severity == PerformanceImpact.MEDIUM:
                score -= 10
            elif issue.severity == PerformanceImpact.LOW:
                score -= 5
        
        return max(score, 0)
    
    def _analyze_query_complexity(self, statements: List[str]) -> Dict[str, Any]:
        """Analyze query complexity"""
        total_complexity = 0
        complexity_breakdown = {
            'simple': 0,
            'moderate': 0,
            'complex': 0,
            'very_complex': 0
        }
        
        for statement in statements:
            complexity = self._calculate_statement_complexity(statement)
            total_complexity += complexity
            
            if complexity <= 25:
                complexity_breakdown['simple'] += 1
            elif complexity <= 50:
                complexity_breakdown['moderate'] += 1
            elif complexity <= 75:
                complexity_breakdown['complex'] += 1
            else:
                complexity_breakdown['very_complex'] += 1
        
        avg_complexity = total_complexity / len(statements) if statements else 0
        
        return {
            'overall_complexity': round(avg_complexity, 2),
            'total_statements': len(statements),
            'complexity_breakdown': complexity_breakdown,
            'complexity_level': self._get_complexity_level(avg_complexity)
        }
    
    def _calculate_statement_complexity(self, statement: str) -> int:
        """Calculate complexity score for a single statement"""
        complexity = 0
        statement_upper = statement.upper()
        
        # Base complexity
        complexity += 10
        
        # Add complexity for joins
        complexity += statement_upper.count('JOIN') * 15
        
        # Add complexity for subqueries
        complexity += statement_upper.count('SELECT') * 10
        
        # Add complexity for functions
        complexity += len(re.findall(r'\w+\(', statement)) * 5
        
        # Add complexity for conditions
        complexity += statement_upper.count('WHERE') * 10
        complexity += statement_upper.count('HAVING') * 15
        complexity += statement_upper.count('CASE') * 10
        
        # Add complexity for aggregations
        complexity += statement_upper.count('GROUP BY') * 15
        complexity += statement_upper.count('ORDER BY') * 10
        
        return min(complexity, 100)
    
    def _get_complexity_level(self, complexity: float) -> str:
        """Get complexity level description"""
        if complexity <= 25:
            return "Simple"
        elif complexity <= 50:
            return "Moderate"
        elif complexity <= 75:
            return "Complex"
        else:
            return "Very Complex"
    
    def _estimate_execution_times(self, statements: List[str]) -> Dict[str, Any]:
        """Estimate execution times for statements"""
        estimates = []
        
        for i, statement in enumerate(statements):
            complexity = self._calculate_statement_complexity(statement)
            
            # Simple estimation based on complexity
            if complexity <= 25:
                estimate = "< 100ms"
                category = "fast"
            elif complexity <= 50:
                estimate = "100ms - 1s"
                category = "moderate"
            elif complexity <= 75:
                estimate = "1s - 10s"
                category = "slow"
            else:
                estimate = "> 10s"
                category = "very_slow"
            
            estimates.append({
                'statement_number': i + 1,
                'estimated_time': estimate,
                'category': category,
                'complexity_score': complexity
            })
        
        return {
            'individual_estimates': estimates,
            'total_estimated_time': self._calculate_total_estimate(estimates)
        }
    
    def _calculate_total_estimate(self, estimates: List[Dict[str, Any]]) -> str:
        """Calculate total estimated execution time"""
        slow_count = len([e for e in estimates if e['category'] in ['slow', 'very_slow']])
        
        if slow_count > 0:
            return f"Several minutes (contains {slow_count} slow queries)"
        elif len(estimates) > 10:
            return "Several seconds (many queries)"
        else:
            return "< 10 seconds"
    
    def _generate_optimization_summary(self, issues: List[PerformanceIssue]) -> Dict[str, Any]:
        """Generate optimization summary"""
        summary = {
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i.severity == PerformanceImpact.CRITICAL]),
            'high_impact_issues': len([i for i in issues if i.severity == PerformanceImpact.HIGH]),
            'optimization_types': {},
            'potential_improvement': self._estimate_potential_improvement(issues)
        }
        
        # Count optimization types
        for issue in issues:
            opt_type = issue.issue_type.value
            summary['optimization_types'][opt_type] = summary['optimization_types'].get(opt_type, 0) + 1
        
        return summary
    
    def _estimate_potential_improvement(self, issues: List[PerformanceIssue]) -> str:
        """Estimate potential performance improvement"""
        if not issues:
            return "Already optimized"
        
        critical_count = len([i for i in issues if i.severity == PerformanceImpact.CRITICAL])
        high_count = len([i for i in issues if i.severity == PerformanceImpact.HIGH])
        
        if critical_count > 0:
            return "50-90% improvement possible"
        elif high_count > 2:
            return "30-70% improvement possible"
        elif len(issues) > 5:
            return "20-50% improvement possible"
        else:
            return "10-30% improvement possible"
    
    def _generate_performance_recommendations(self, issues: List[PerformanceIssue], 
                                            indexes: List[IndexSuggestion]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if issues:
            recommendations.append(f"Address {len(issues)} performance issues identified")
        
        if indexes:
            recommendations.append(f"Consider adding {len(indexes)} suggested indexes")
        
        # Specific recommendations based on issue types
        issue_types = [issue.issue_type for issue in issues]
        
        if OptimizationType.QUERY_REWRITE in issue_types:
            recommendations.append("Rewrite queries to select only needed columns")
        
        if OptimizationType.INDEX in issue_types:
            recommendations.append("Add indexes for frequently queried columns")
        
        if OptimizationType.JOIN_OPTIMIZATION in issue_types:
            recommendations.append("Optimize JOIN operations and conditions")
        
        if not issues:
            recommendations.append("Queries are well-optimized for performance")
        
        return recommendations
    
    def _issue_to_dict(self, issue: PerformanceIssue) -> Dict[str, Any]:
        """Convert PerformanceIssue to dictionary"""
        return {
            'line': issue.line,
            'type': issue.issue_type.value,
            'severity': issue.severity.value,
            'title': issue.title,
            'description': issue.description,
            'current_code': issue.current_code,
            'optimized_code': issue.optimized_code,
            'estimated_improvement': issue.estimated_improvement,
            'explanation': issue.explanation
        }
    
    def _index_to_dict(self, index: IndexSuggestion) -> Dict[str, Any]:
        """Convert IndexSuggestion to dictionary"""
        return {
            'table': index.table,
            'columns': index.columns,
            'index_type': index.index_type,
            'reason': index.reason,
            'estimated_benefit': index.estimated_benefit,
            'sql_command': f"CREATE INDEX idx_{index.table}_{'_'.join(index.columns)} ON {index.table} ({', '.join(index.columns)})"
        }
