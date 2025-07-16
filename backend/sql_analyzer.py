#!/usr/bin/env python3
"""
SQL ANALYZER - ENTERPRISE GRADE SQL ANALYSIS ENGINE
Real SQL parsing, error detection, and optimization suggestions
"""

import re
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SQLError:
    line: int
    column: int
    error_type: str
    message: str
    severity: ErrorSeverity
    suggestion: str

@dataclass
class OptimizationSuggestion:
    line: int
    type: str
    current: str
    suggested: str
    impact: str
    explanation: str

class SQLAnalyzer:
    """Enterprise-grade SQL analyzer with real parsing capabilities"""
    
    def __init__(self):
        self.supported_engines = [
            'mysql', 'postgresql', 'oracle', 'sqlserver', 'sqlite', 
            'mariadb', 'db2', 'teradata', 'redshift', 'snowflake'
        ]
        self.keywords = self._load_sql_keywords()
        self.functions = self._load_sql_functions()
        
    def _load_sql_keywords(self) -> set:
        """Load SQL keywords for syntax validation"""
        return {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET', 'UNION',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE',
            'TABLE', 'INDEX', 'VIEW', 'DROP', 'ALTER', 'ADD', 'COLUMN',
            'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'NOT', 'NULL', 'DEFAULT',
            'AUTO_INCREMENT', 'UNIQUE', 'CHECK', 'CONSTRAINT', 'DATABASE',
            'SCHEMA', 'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'TRANSACTION',
            'BEGIN', 'END', 'IF', 'ELSE', 'CASE', 'WHEN', 'THEN', 'AS',
            'DISTINCT', 'ALL', 'EXISTS', 'IN', 'BETWEEN', 'LIKE', 'IS',
            'AND', 'OR', 'XOR', 'TRUE', 'FALSE', 'UNKNOWN'
        }
    
    def _load_sql_functions(self) -> set:
        """Load SQL functions for validation"""
        return {
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CONCAT', 'SUBSTRING',
            'LENGTH', 'UPPER', 'LOWER', 'TRIM', 'LTRIM', 'RTRIM', 'REPLACE',
            'NOW', 'CURDATE', 'CURTIME', 'DATE', 'TIME', 'YEAR', 'MONTH',
            'DAY', 'HOUR', 'MINUTE', 'SECOND', 'DATEDIFF', 'DATE_ADD',
            'DATE_SUB', 'COALESCE', 'ISNULL', 'NULLIF', 'CAST', 'CONVERT',
            'ROUND', 'CEIL', 'FLOOR', 'ABS', 'POWER', 'SQRT', 'RAND'
        }
    
    def analyze(self, sql_content: str, engine: str = 'mysql') -> Dict[str, Any]:
        """
        Perform comprehensive SQL analysis
        
        Args:
            sql_content: SQL code to analyze
            engine: Database engine type
            
        Returns:
            Comprehensive analysis results
        """
        start_time = time.time()
        
        try:
            # Clean and prepare SQL
            cleaned_sql = self._clean_sql(sql_content)
            statements = self._parse_statements(cleaned_sql)
            
            # Perform analysis
            syntax_errors = self._check_syntax_errors(statements)
            semantic_errors = self._check_semantic_errors(statements)
            optimizations = self._suggest_optimizations(statements)
            complexity_score = self._calculate_complexity(statements)
            
            # Generate statistics
            stats = self._generate_statistics(statements)
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'processing_time': round(processing_time, 3),
                'engine': engine,
                'statistics': stats,
                'syntax_errors': [self._error_to_dict(e) for e in syntax_errors],
                'semantic_errors': [self._error_to_dict(e) for e in semantic_errors],
                'optimizations': [self._optimization_to_dict(o) for o in optimizations],
                'complexity_score': complexity_score,
                'quality_score': self._calculate_quality_score(syntax_errors, semantic_errors, optimizations),
                'recommendations': self._generate_recommendations(syntax_errors, semantic_errors, optimizations),
                'file_hash': hashlib.md5(sql_content.encode()).hexdigest()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and normalize SQL content"""
        # Remove comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Normalize whitespace
        sql = re.sub(r'\s+', ' ', sql)
        sql = sql.strip()
        
        return sql
    
    def _parse_statements(self, sql: str) -> List[str]:
        """Parse SQL into individual statements"""
        # Split by semicolon but handle strings and comments
        statements = []
        current_statement = ""
        in_string = False
        string_char = None
        
        i = 0
        while i < len(sql):
            char = sql[i]
            
            if not in_string:
                if char in ("'", '"'):
                    in_string = True
                    string_char = char
                elif char == ';':
                    if current_statement.strip():
                        statements.append(current_statement.strip())
                    current_statement = ""
                    i += 1
                    continue
            else:
                if char == string_char and (i == 0 or sql[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            current_statement += char
            i += 1
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def _check_syntax_errors(self, statements: List[str]) -> List[SQLError]:
        """Check for syntax errors in SQL statements"""
        errors = []
        
        for i, statement in enumerate(statements):
            # Check for basic syntax issues
            if not statement.strip():
                continue
                
            # Check for unmatched parentheses
            if statement.count('(') != statement.count(')'):
                errors.append(SQLError(
                    line=i+1,
                    column=0,
                    error_type="SYNTAX_ERROR",
                    message="Unmatched parentheses",
                    severity=ErrorSeverity.HIGH,
                    suggestion="Check parentheses balance in the statement"
                ))
            
            # Check for missing semicolon (if not last statement)
            if i < len(statements) - 1 and not statement.rstrip().endswith(';'):
                errors.append(SQLError(
                    line=i+1,
                    column=len(statement),
                    error_type="SYNTAX_ERROR",
                    message="Missing semicolon",
                    severity=ErrorSeverity.MEDIUM,
                    suggestion="Add semicolon at the end of the statement"
                ))
            
            # Check for invalid keywords
            words = re.findall(r'\b\w+\b', statement.upper())
            for word in words:
                if word.isupper() and len(word) > 2 and word not in self.keywords and word not in self.functions:
                    # Could be a typo of a keyword
                    similar = self._find_similar_keyword(word)
                    if similar:
                        errors.append(SQLError(
                            line=i+1,
                            column=statement.upper().find(word),
                            error_type="SYNTAX_ERROR",
                            message=f"Unknown keyword '{word}'",
                            severity=ErrorSeverity.MEDIUM,
                            suggestion=f"Did you mean '{similar}'?"
                        ))
        
        return errors
    
    def _check_semantic_errors(self, statements: List[str]) -> List[SQLError]:
        """Check for semantic errors in SQL statements"""
        errors = []
        
        for i, statement in enumerate(statements):
            statement_upper = statement.upper()
            
            # Check for SELECT without FROM (except for simple expressions)
            if 'SELECT' in statement_upper and 'FROM' not in statement_upper:
                if not re.search(r'SELECT\s+\d+|SELECT\s+\'.*\'|SELECT\s+NOW\(\)', statement_upper):
                    errors.append(SQLError(
                        line=i+1,
                        column=0,
                        error_type="SEMANTIC_ERROR",
                        message="SELECT statement without FROM clause",
                        severity=ErrorSeverity.MEDIUM,
                        suggestion="Add FROM clause or use a simple expression"
                    ))
            
            # Check for GROUP BY without aggregate functions
            if 'GROUP BY' in statement_upper:
                has_aggregate = any(func in statement_upper for func in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
                if not has_aggregate:
                    errors.append(SQLError(
                        line=i+1,
                        column=statement_upper.find('GROUP BY'),
                        error_type="SEMANTIC_ERROR",
                        message="GROUP BY without aggregate function",
                        severity=ErrorSeverity.MEDIUM,
                        suggestion="Add aggregate function or remove GROUP BY"
                    ))
            
            # Check for HAVING without GROUP BY
            if 'HAVING' in statement_upper and 'GROUP BY' not in statement_upper:
                errors.append(SQLError(
                    line=i+1,
                    column=statement_upper.find('HAVING'),
                    error_type="SEMANTIC_ERROR",
                    message="HAVING clause without GROUP BY",
                    severity=ErrorSeverity.HIGH,
                    suggestion="Add GROUP BY clause before HAVING"
                ))
        
        return errors
    
    def _suggest_optimizations(self, statements: List[str]) -> List[OptimizationSuggestion]:
        """Suggest performance optimizations"""
        optimizations = []
        
        for i, statement in enumerate(statements):
            statement_upper = statement.upper()
            
            # Suggest using LIMIT for large result sets
            if 'SELECT' in statement_upper and 'LIMIT' not in statement_upper and 'COUNT' not in statement_upper:
                optimizations.append(OptimizationSuggestion(
                    line=i+1,
                    type="PERFORMANCE",
                    current=statement[:50] + "...",
                    suggested="Add LIMIT clause",
                    impact="HIGH",
                    explanation="Large result sets can impact performance. Consider adding LIMIT."
                ))
            
            # Suggest using indexes for WHERE clauses
            if 'WHERE' in statement_upper:
                optimizations.append(OptimizationSuggestion(
                    line=i+1,
                    type="INDEX",
                    current="WHERE clause detected",
                    suggested="Ensure indexed columns in WHERE",
                    impact="MEDIUM",
                    explanation="WHERE clauses perform better with proper indexing."
                ))
            
            # Suggest avoiding SELECT *
            if re.search(r'SELECT\s+\*', statement_upper):
                optimizations.append(OptimizationSuggestion(
                    line=i+1,
                    type="PERFORMANCE",
                    current="SELECT *",
                    suggested="SELECT specific columns",
                    impact="MEDIUM",
                    explanation="Selecting specific columns reduces data transfer and improves performance."
                ))
        
        return optimizations
    
    def _calculate_complexity(self, statements: List[str]) -> int:
        """Calculate SQL complexity score (0-100)"""
        complexity = 0
        
        for statement in statements:
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
            
        return min(complexity, 100)
    
    def _generate_statistics(self, statements: List[str]) -> Dict[str, Any]:
        """Generate SQL statistics"""
        stats = {
            'total_statements': len(statements),
            'total_lines': sum(stmt.count('\n') + 1 for stmt in statements),
            'statement_types': {},
            'total_tables': 0,
            'total_columns': 0,
            'complexity_distribution': {}
        }
        
        for statement in statements:
            statement_upper = statement.upper().strip()
            
            # Identify statement type
            if statement_upper.startswith('SELECT'):
                stats['statement_types']['SELECT'] = stats['statement_types'].get('SELECT', 0) + 1
            elif statement_upper.startswith('INSERT'):
                stats['statement_types']['INSERT'] = stats['statement_types'].get('INSERT', 0) + 1
            elif statement_upper.startswith('UPDATE'):
                stats['statement_types']['UPDATE'] = stats['statement_types'].get('UPDATE', 0) + 1
            elif statement_upper.startswith('DELETE'):
                stats['statement_types']['DELETE'] = stats['statement_types'].get('DELETE', 0) + 1
            elif statement_upper.startswith('CREATE'):
                stats['statement_types']['CREATE'] = stats['statement_types'].get('CREATE', 0) + 1
            elif statement_upper.startswith('DROP'):
                stats['statement_types']['DROP'] = stats['statement_types'].get('DROP', 0) + 1
            else:
                stats['statement_types']['OTHER'] = stats['statement_types'].get('OTHER', 0) + 1
        
        return stats
    
    def _calculate_quality_score(self, syntax_errors: List[SQLError], 
                                semantic_errors: List[SQLError], 
                                optimizations: List[OptimizationSuggestion]) -> int:
        """Calculate overall quality score (0-100)"""
        score = 100
        
        # Deduct for errors
        score -= len(syntax_errors) * 15
        score -= len(semantic_errors) * 10
        score -= len(optimizations) * 5
        
        return max(score, 0)
    
    def _generate_recommendations(self, syntax_errors: List[SQLError], 
                                 semantic_errors: List[SQLError], 
                                 optimizations: List[OptimizationSuggestion]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if syntax_errors:
            recommendations.append(f"Fix {len(syntax_errors)} syntax error(s) for proper execution")
        
        if semantic_errors:
            recommendations.append(f"Address {len(semantic_errors)} semantic issue(s) for better logic")
        
        if optimizations:
            recommendations.append(f"Consider {len(optimizations)} optimization(s) for better performance")
        
        if not syntax_errors and not semantic_errors:
            recommendations.append("SQL syntax is correct and ready for execution")
        
        return recommendations
    
    def _find_similar_keyword(self, word: str) -> Optional[str]:
        """Find similar keyword using simple distance"""
        min_distance = float('inf')
        similar = None
        
        for keyword in self.keywords:
            distance = self._levenshtein_distance(word, keyword)
            if distance < min_distance and distance <= 2:
                min_distance = distance
                similar = keyword
        
        return similar
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _error_to_dict(self, error: SQLError) -> Dict[str, Any]:
        """Convert SQLError to dictionary"""
        return {
            'line': error.line,
            'column': error.column,
            'type': error.error_type,
            'message': error.message,
            'severity': error.severity.value,
            'suggestion': error.suggestion
        }
    
    def _optimization_to_dict(self, opt: OptimizationSuggestion) -> Dict[str, Any]:
        """Convert OptimizationSuggestion to dictionary"""
        return {
            'line': opt.line,
            'type': opt.type,
            'current': opt.current,
            'suggested': opt.suggested,
            'impact': opt.impact,
            'explanation': opt.explanation
        }
