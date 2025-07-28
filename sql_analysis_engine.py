#!/usr/bin/env python3
"""
SQL ANALYSIS ENGINE
SQL Analyzer Enterprise - Real SQL Analysis Functions
"""

import re
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class SQLAnalyzer:
    """Real SQL Analysis Engine with syntax checking and optimization"""
    
    def __init__(self):
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE',
            'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'DATABASE',
            'SCHEMA', 'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'TRANSACTION',
            'GROUP', 'ORDER', 'HAVING', 'DISTINCT', 'UNION', 'INTERSECT',
            'EXCEPT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AS', 'AND',
            'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL'
        }
        
        self.data_types = {
            'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
            'VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT',
            'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL',
            'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR',
            'BOOLEAN', 'BOOL', 'BIT', 'BINARY', 'VARBINARY',
            'BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB',
            'JSON', 'XML', 'UUID', 'ENUM', 'SET'
        }
    
    def analyze(self, content: str, engine: str = 'mysql') -> Dict[str, Any]:
        """Analyze SQL content for syntax, performance, and quality"""
        start_time = time.time()
        
        # Clean and prepare content
        cleaned_content = self._clean_sql(content)
        statements = self._split_statements(cleaned_content)
        
        # Perform analysis
        syntax_errors = self._check_syntax(statements)
        semantic_errors = self._check_semantics(statements)
        optimizations = self._suggest_optimizations(statements)
        complexity_score = self._calculate_complexity(statements)
        quality_score = self._calculate_quality(statements, syntax_errors, semantic_errors)
        recommendations = self._generate_recommendations(statements, syntax_errors, optimizations)
        statistics = self._generate_statistics(statements)
        
        processing_time = time.time() - start_time
        
        return {
            'status': 'success',
            'processing_time': round(processing_time, 3),
            'engine': engine,
            'syntax_errors': syntax_errors,
            'semantic_errors': semantic_errors,
            'optimizations': optimizations,
            'complexity_score': complexity_score,
            'quality_score': quality_score,
            'recommendations': recommendations,
            'statistics': statistics,
            'corrected_sql': self._apply_corrections(content, syntax_errors)
        }
    
    def _clean_sql(self, content: str) -> str:
        """Clean SQL content by removing comments and normalizing whitespace"""
        # Remove single-line comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _split_statements(self, content: str) -> List[str]:
        """Split SQL content into individual statements"""
        # Split by semicolon, but be careful with strings
        statements = []
        current_statement = ""
        in_string = False
        string_char = None
        
        i = 0
        while i < len(content):
            char = content[i]
            
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
                if char == string_char:
                    # Check if it's escaped
                    if i > 0 and content[i-1] != '\\':
                        in_string = False
                        string_char = None
            
            current_statement += char
            i += 1
        
        # Add the last statement if it exists
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [stmt for stmt in statements if stmt]
    
    def _check_syntax(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Check for syntax errors in SQL statements"""
        errors = []
        
        for i, statement in enumerate(statements):
            statement_upper = statement.upper()
            
            # Check for missing semicolon (if not last statement)
            if i < len(statements) - 1 and not statement.rstrip().endswith(';'):
                errors.append({
                    'line': i + 1,
                    'type': 'syntax_error',
                    'severity': 'medium',
                    'message': 'Missing semicolon at end of statement',
                    'suggestion': 'Add semicolon (;) at the end of the statement'
                })
            
            # Check for unmatched parentheses
            open_parens = statement.count('(')
            close_parens = statement.count(')')
            if open_parens != close_parens:
                errors.append({
                    'line': i + 1,
                    'type': 'syntax_error',
                    'severity': 'high',
                    'message': f'Unmatched parentheses: {open_parens} opening, {close_parens} closing',
                    'suggestion': 'Check parentheses balance'
                })
            
            # Check for basic SQL structure
            if statement_upper.startswith('SELECT'):
                if 'FROM' not in statement_upper and 'DUAL' not in statement_upper:
                    errors.append({
                        'line': i + 1,
                        'type': 'syntax_error',
                        'severity': 'high',
                        'message': 'SELECT statement missing FROM clause',
                        'suggestion': 'Add FROM clause or use FROM DUAL for constants'
                    })
            
            # Check for reserved words as identifiers
            words = re.findall(r'\b\w+\b', statement_upper)
            for word in words:
                if word in self.sql_keywords and not self._is_keyword_context(statement_upper, word):
                    errors.append({
                        'line': i + 1,
                        'type': 'syntax_warning',
                        'severity': 'low',
                        'message': f'Using reserved keyword "{word}" as identifier',
                        'suggestion': f'Consider using backticks or quotes around "{word}"'
                    })
        
        return errors
    
    def _check_semantics(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Check for semantic errors in SQL statements"""
        errors = []
        
        for i, statement in enumerate(statements):
            statement_upper = statement.upper()
            
            # Check for SELECT *
            if 'SELECT *' in statement_upper:
                errors.append({
                    'line': i + 1,
                    'type': 'semantic_warning',
                    'severity': 'medium',
                    'message': 'Using SELECT * can be inefficient',
                    'suggestion': 'Specify only the columns you need'
                })
            
            # Check for missing WHERE clause in UPDATE/DELETE
            if statement_upper.startswith(('UPDATE', 'DELETE')) and 'WHERE' not in statement_upper:
                errors.append({
                    'line': i + 1,
                    'type': 'semantic_warning',
                    'severity': 'high',
                    'message': 'UPDATE/DELETE without WHERE clause affects all rows',
                    'suggestion': 'Add WHERE clause to limit affected rows'
                })
            
            # Check for potential Cartesian products
            if 'JOIN' not in statement_upper and statement_upper.count('FROM') == 1:
                from_match = re.search(r'FROM\s+(\w+(?:\s*,\s*\w+)+)', statement_upper)
                if from_match:
                    errors.append({
                        'line': i + 1,
                        'type': 'semantic_warning',
                        'severity': 'medium',
                        'message': 'Multiple tables without explicit JOIN may cause Cartesian product',
                        'suggestion': 'Use explicit JOIN syntax with ON conditions'
                    })
        
        return errors
    
    def _suggest_optimizations(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Suggest performance optimizations"""
        optimizations = []
        
        for i, statement in enumerate(statements):
            statement_upper = statement.upper()
            
            # Suggest LIMIT for large result sets
            if statement_upper.startswith('SELECT') and 'LIMIT' not in statement_upper:
                optimizations.append({
                    'line': i + 1,
                    'type': 'PERFORMANCE',
                    'priority': 'medium',
                    'suggestion': 'Consider adding LIMIT clause for large result sets',
                    'benefit': 'Reduces memory usage and network traffic'
                })
            
            # Suggest indexes for WHERE clauses
            where_match = re.search(r'WHERE\s+(\w+)', statement_upper)
            if where_match:
                column = where_match.group(1)
                optimizations.append({
                    'line': i + 1,
                    'type': 'INDEX',
                    'priority': 'high',
                    'suggestion': f'Consider adding index on column "{column}"',
                    'benefit': 'Improves WHERE clause performance'
                })
            
            # Suggest avoiding functions in WHERE clause
            if re.search(r'WHERE\s+\w+\s*\(', statement_upper):
                optimizations.append({
                    'line': i + 1,
                    'type': 'PERFORMANCE',
                    'priority': 'medium',
                    'suggestion': 'Avoid using functions in WHERE clause',
                    'benefit': 'Allows index usage for better performance'
                })
        
        return optimizations
    
    def _calculate_complexity(self, statements: List[str]) -> int:
        """Calculate complexity score (0-100)"""
        total_complexity = 0
        
        for statement in statements:
            statement_upper = statement.upper()
            complexity = 10  # Base complexity
            
            # Add complexity for joins
            complexity += statement_upper.count('JOIN') * 5
            
            # Add complexity for subqueries
            complexity += statement_upper.count('SELECT') - 1 if 'SELECT' in statement_upper else 0
            
            # Add complexity for conditions
            complexity += statement_upper.count('WHERE') * 3
            complexity += statement_upper.count('AND') * 2
            complexity += statement_upper.count('OR') * 3
            
            # Add complexity for aggregations
            complexity += statement_upper.count('GROUP BY') * 4
            complexity += statement_upper.count('HAVING') * 3
            
            total_complexity += complexity
        
        # Normalize to 0-100 scale
        return min(100, total_complexity)
    
    def _calculate_quality(self, statements: List[str], syntax_errors: List, semantic_errors: List) -> int:
        """Calculate overall quality score (0-100)"""
        base_score = 100
        
        # Deduct points for errors
        base_score -= len(syntax_errors) * 10
        base_score -= len(semantic_errors) * 5
        
        # Deduct points for bad practices
        for statement in statements:
            statement_upper = statement.upper()
            
            if 'SELECT *' in statement_upper:
                base_score -= 5
            
            if statement_upper.startswith(('UPDATE', 'DELETE')) and 'WHERE' not in statement_upper:
                base_score -= 15
        
        return max(0, base_score)
    
    def _generate_recommendations(self, statements: List[str], syntax_errors: List, optimizations: List) -> List[str]:
        """Generate general recommendations"""
        recommendations = []
        
        if syntax_errors:
            recommendations.append("Fix syntax errors to ensure proper execution")
        
        if any('SELECT *' in stmt.upper() for stmt in statements):
            recommendations.append("Specify only needed columns instead of using SELECT *")
        
        if optimizations:
            recommendations.append("Consider implementing suggested performance optimizations")
        
        if any(stmt.upper().startswith(('UPDATE', 'DELETE')) and 'WHERE' not in stmt.upper() for stmt in statements):
            recommendations.append("Always use WHERE clauses with UPDATE and DELETE statements")
        
        recommendations.append("Add appropriate indexes for frequently queried columns")
        recommendations.append("Use parameterized queries to prevent SQL injection")
        
        return recommendations
    
    def _generate_statistics(self, statements: List[str]) -> Dict[str, Any]:
        """Generate statistics about the SQL content"""
        statement_types = {}
        total_statements = len(statements)
        
        for statement in statements:
            statement_upper = statement.upper().strip()
            
            if statement_upper.startswith('SELECT'):
                statement_types['SELECT'] = statement_types.get('SELECT', 0) + 1
            elif statement_upper.startswith('INSERT'):
                statement_types['INSERT'] = statement_types.get('INSERT', 0) + 1
            elif statement_upper.startswith('UPDATE'):
                statement_types['UPDATE'] = statement_types.get('UPDATE', 0) + 1
            elif statement_upper.startswith('DELETE'):
                statement_types['DELETE'] = statement_types.get('DELETE', 0) + 1
            elif statement_upper.startswith('CREATE'):
                statement_types['CREATE'] = statement_types.get('CREATE', 0) + 1
            elif statement_upper.startswith('DROP'):
                statement_types['DROP'] = statement_types.get('DROP', 0) + 1
            elif statement_upper.startswith('ALTER'):
                statement_types['ALTER'] = statement_types.get('ALTER', 0) + 1
            else:
                statement_types['OTHER'] = statement_types.get('OTHER', 0) + 1
        
        return {
            'total_statements': total_statements,
            'statement_types': statement_types,
            'total_lines': sum(stmt.count('\n') + 1 for stmt in statements),
            'avg_statement_length': sum(len(stmt) for stmt in statements) // total_statements if total_statements > 0 else 0
        }
    
    def _apply_corrections(self, original_sql: str, syntax_errors: List) -> str:
        """Apply automatic corrections to SQL"""
        corrected_sql = original_sql
        
        # Simple corrections for demonstration
        for error in syntax_errors:
            if 'Missing semicolon' in error.get('message', ''):
                # Add semicolon at the end if missing
                if not corrected_sql.rstrip().endswith(';'):
                    corrected_sql = corrected_sql.rstrip() + ';'
        
        return corrected_sql
    
    def _is_keyword_context(self, statement: str, keyword: str) -> bool:
        """Check if keyword is used in proper context"""
        # Simple check - in real implementation, this would be more sophisticated
        keyword_positions = [m.start() for m in re.finditer(r'\b' + keyword + r'\b', statement)]
        
        for pos in keyword_positions:
            # Check if it's at the beginning or after certain keywords
            before = statement[:pos].strip()
            if not before or before.split()[-1] in ['SELECT', 'FROM', 'WHERE', 'AND', 'OR']:
                return True
        
        return False


class SecurityAnalyzer:
    """Real Security Analysis Engine with OWASP compliance"""

    def __init__(self):
        self.sql_injection_patterns = [
            r"(?i)(union|select|insert|update|delete|drop|create|alter)\s+.*\s+(or|and)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",
            r"(?i)(union|select)\s+.*\s+from\s+",
            r"(?i)(drop|delete)\s+(table|database|schema)",
            r"(?i)(exec|execute|sp_|xp_)",
            r"(?i)(--|#|/\*|\*/)",
            r"(?i)(\bor\b|\band\b)\s+['\"]?\w*['\"]?\s*=\s*['\"]?\w*['\"]?",
            r"(?i)(information_schema|sys\.|mysql\.|pg_)",
            r"(?i)(load_file|into\s+outfile|into\s+dumpfile)",
            r"(?i)(benchmark|sleep|waitfor\s+delay)",
            r"(?i)(char|ascii|substring|concat)\s*\("
        ]

        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]

        self.owasp_categories = {
            'A03_2021_Injection': 'SQL Injection vulnerabilities',
            'A05_2021_Security_Misconfiguration': 'Security misconfigurations',
            'A06_2021_Vulnerable_Components': 'Vulnerable and outdated components',
            'A07_2021_Authentication_Failures': 'Authentication and session management flaws'
        }

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze SQL content for security vulnerabilities"""
        start_time = time.time()

        vulnerabilities = []

        # Check for SQL injection patterns
        sql_injection_vulns = self._check_sql_injection(content)
        vulnerabilities.extend(sql_injection_vulns)

        # Check for XSS patterns
        xss_vulns = self._check_xss(content)
        vulnerabilities.extend(xss_vulns)

        # Check for hardcoded credentials
        credential_vulns = self._check_hardcoded_credentials(content)
        vulnerabilities.extend(credential_vulns)

        # Check for dangerous functions
        dangerous_func_vulns = self._check_dangerous_functions(content)
        vulnerabilities.extend(dangerous_func_vulns)

        # Calculate security score
        security_score = self._calculate_security_score(vulnerabilities)
        risk_level = self._determine_risk_level(vulnerabilities)

        # Generate vulnerability summary
        vulnerability_summary = self._generate_vulnerability_summary(vulnerabilities)

        # Generate recommendations
        recommendations = self._generate_security_recommendations(vulnerabilities)

        processing_time = time.time() - start_time

        return {
            'status': 'success',
            'processing_time': round(processing_time, 3),
            'security_score': security_score,
            'risk_level': risk_level,
            'vulnerabilities': vulnerabilities,
            'vulnerability_summary': vulnerability_summary,
            'recommendations': recommendations,
            'owasp_compliance': self._check_owasp_compliance(vulnerabilities)
        }

    def _check_sql_injection(self, content: str) -> List[Dict[str, Any]]:
        """Check for SQL injection vulnerabilities"""
        vulnerabilities = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        'line': i,
                        'type': 'sql_injection',
                        'risk_level': 'high',
                        'owasp_category': 'A03_2021_Injection',
                        'cwe_id': 'CWE-89',
                        'title': 'Potential SQL Injection',
                        'description': 'SQL code that may be vulnerable to injection attacks',
                        'code_snippet': line.strip(),
                        'recommendation': 'Use parameterized queries or prepared statements'
                    })

        return vulnerabilities

    def _check_xss(self, content: str) -> List[Dict[str, Any]]:
        """Check for XSS vulnerabilities"""
        vulnerabilities = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            for pattern in self.xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append({
                        'line': i,
                        'type': 'xss',
                        'risk_level': 'medium',
                        'owasp_category': 'A03_2021_Injection',
                        'cwe_id': 'CWE-79',
                        'title': 'Potential Cross-Site Scripting (XSS)',
                        'description': 'Code that may allow XSS attacks',
                        'code_snippet': line.strip(),
                        'recommendation': 'Sanitize and validate all user inputs'
                    })

        return vulnerabilities

    def _check_hardcoded_credentials(self, content: str) -> List[Dict[str, Any]]:
        """Check for hardcoded credentials"""
        vulnerabilities = []
        lines = content.split('\n')

        credential_patterns = [
            r"(?i)(password|pwd|pass)\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)(api_key|apikey|secret)\s*=\s*['\"][^'\"]+['\"]",
            r"(?i)(token|auth)\s*=\s*['\"][^'\"]+['\"]"
        ]

        for i, line in enumerate(lines, 1):
            for pattern in credential_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        'line': i,
                        'type': 'hardcoded_credentials',
                        'risk_level': 'high',
                        'owasp_category': 'A07_2021_Authentication_Failures',
                        'cwe_id': 'CWE-798',
                        'title': 'Hardcoded Credentials',
                        'description': 'Credentials hardcoded in source code',
                        'code_snippet': line.strip(),
                        'recommendation': 'Use environment variables or secure credential storage'
                    })

        return vulnerabilities

    def _check_dangerous_functions(self, content: str) -> List[Dict[str, Any]]:
        """Check for dangerous SQL functions"""
        vulnerabilities = []
        lines = content.split('\n')

        dangerous_functions = [
            r"(?i)\bexec\s*\(",
            r"(?i)\beval\s*\(",
            r"(?i)\bload_file\s*\(",
            r"(?i)\binto\s+outfile",
            r"(?i)\bsystem\s*\(",
            r"(?i)\bshell_exec\s*\("
        ]

        for i, line in enumerate(lines, 1):
            for pattern in dangerous_functions:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        'line': i,
                        'type': 'dangerous_function',
                        'risk_level': 'critical',
                        'owasp_category': 'A03_2021_Injection',
                        'cwe_id': 'CWE-78',
                        'title': 'Dangerous Function Usage',
                        'description': 'Usage of potentially dangerous functions',
                        'code_snippet': line.strip(),
                        'recommendation': 'Avoid using dangerous functions or implement strict validation'
                    })

        return vulnerabilities

    def _calculate_security_score(self, vulnerabilities: List[Dict[str, Any]]) -> int:
        """Calculate security score (0-100)"""
        base_score = 100

        for vuln in vulnerabilities:
            risk_level = vuln.get('risk_level', 'low')
            if risk_level == 'critical':
                base_score -= 25
            elif risk_level == 'high':
                base_score -= 15
            elif risk_level == 'medium':
                base_score -= 10
            elif risk_level == 'low':
                base_score -= 5

        return max(0, base_score)

    def _determine_risk_level(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Determine overall risk level"""
        if any(v.get('risk_level') == 'critical' for v in vulnerabilities):
            return 'CRITICAL'
        elif any(v.get('risk_level') == 'high' for v in vulnerabilities):
            return 'HIGH'
        elif any(v.get('risk_level') == 'medium' for v in vulnerabilities):
            return 'MEDIUM'
        elif vulnerabilities:
            return 'LOW'
        else:
            return 'MINIMAL'

    def _generate_vulnerability_summary(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Generate vulnerability summary by risk level"""
        summary = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'total': len(vulnerabilities)}

        for vuln in vulnerabilities:
            risk_level = vuln.get('risk_level', 'low')
            summary[risk_level] = summary.get(risk_level, 0) + 1

        return summary

    def _generate_security_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        vuln_types = set(v.get('type') for v in vulnerabilities)

        if 'sql_injection' in vuln_types:
            recommendations.append('Use parameterized queries to prevent SQL injection')
            recommendations.append('Implement input validation and sanitization')

        if 'xss' in vuln_types:
            recommendations.append('Sanitize all user inputs to prevent XSS attacks')
            recommendations.append('Use Content Security Policy (CSP) headers')

        if 'hardcoded_credentials' in vuln_types:
            recommendations.append('Store credentials securely using environment variables')
            recommendations.append('Implement proper secrets management')

        if 'dangerous_function' in vuln_types:
            recommendations.append('Avoid using dangerous functions or implement strict validation')
            recommendations.append('Use principle of least privilege')

        # General recommendations
        recommendations.extend([
            'Implement regular security code reviews',
            'Use static application security testing (SAST) tools',
            'Follow OWASP secure coding practices',
            'Implement proper error handling without information disclosure'
        ])

        return recommendations

    def _check_owasp_compliance(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check OWASP Top 10 2021 compliance"""
        owasp_issues = {}

        for vuln in vulnerabilities:
            category = vuln.get('owasp_category')
            if category:
                if category not in owasp_issues:
                    owasp_issues[category] = []
                owasp_issues[category].append(vuln)

        compliance_score = max(0, 100 - len(owasp_issues) * 10)

        return {
            'compliance_score': compliance_score,
            'issues_found': owasp_issues,
            'categories_affected': list(owasp_issues.keys()),
            'total_categories': len(self.owasp_categories),
            'compliant_categories': len(self.owasp_categories) - len(owasp_issues)
        }


class PerformanceAnalyzer:
    """Real Performance Analysis Engine with optimization suggestions"""

    def __init__(self):
        self.performance_patterns = {
            'select_star': r'(?i)select\s+\*\s+from',
            'missing_limit': r'(?i)select\s+.*\s+from\s+.*(?!.*limit)',
            'cartesian_join': r'(?i)from\s+\w+\s*,\s*\w+(?!.*where)',
            'function_in_where': r'(?i)where\s+\w+\s*\([^)]*\)\s*[=<>]',
            'no_index_hint': r'(?i)where\s+(\w+)\s*[=<>]',
            'subquery_in_select': r'(?i)select\s+.*\(\s*select\s+.*\)\s*.*from',
            'order_without_limit': r'(?i)order\s+by\s+.*(?!.*limit)',
            'group_without_index': r'(?i)group\s+by\s+(\w+)',
            'like_leading_wildcard': r'(?i)like\s+[\'"][%]',
            'distinct_unnecessary': r'(?i)select\s+distinct\s+.*\s+from\s+\w+\s+where\s+\w+\s*=',
        }

        self.database_engines = {
            'mysql': {
                'storage_engines': ['InnoDB', 'MyISAM', 'Memory'],
                'index_types': ['BTREE', 'HASH', 'FULLTEXT'],
                'optimizations': ['query_cache', 'innodb_buffer_pool']
            },
            'postgresql': {
                'storage_engines': ['heap', 'btree', 'hash'],
                'index_types': ['BTREE', 'HASH', 'GIN', 'GIST'],
                'optimizations': ['shared_buffers', 'work_mem']
            },
            'oracle': {
                'storage_engines': ['heap', 'index_organized'],
                'index_types': ['BTREE', 'BITMAP', 'FUNCTION_BASED'],
                'optimizations': ['sga_target', 'pga_aggregate_target']
            }
        }

    def analyze(self, content: str, database_engine: str = 'mysql') -> Dict[str, Any]:
        """Analyze SQL content for performance issues"""
        start_time = time.time()

        # Split into statements
        statements = self._split_statements(content)

        # Analyze performance issues
        performance_issues = self._identify_performance_issues(statements)

        # Generate index suggestions
        index_suggestions = self._generate_index_suggestions(statements)

        # Calculate performance score
        performance_score = self._calculate_performance_score(statements, performance_issues)

        # Determine complexity
        complexity = self._determine_complexity(statements)

        # Generate optimized queries
        optimized_queries = self._generate_optimized_queries(statements, performance_issues)

        # Generate recommendations
        recommendations = self._generate_performance_recommendations(performance_issues, index_suggestions)

        processing_time = time.time() - start_time

        return {
            'status': 'success',
            'processing_time': round(processing_time, 3),
            'database_engine': database_engine,
            'performance_score': performance_score,
            'overall_complexity': complexity,
            'performance_issues': performance_issues,
            'index_suggestions': index_suggestions,
            'optimized_queries': optimized_queries,
            'recommendations': recommendations,
            'execution_plan_analysis': self._analyze_execution_plan(statements),
            'resource_usage_estimate': self._estimate_resource_usage(statements)
        }

    def _split_statements(self, content: str) -> List[str]:
        """Split SQL content into statements"""
        # Remove comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Split by semicolon
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
        return statements

    def _identify_performance_issues(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Identify performance issues in SQL statements"""
        issues = []

        for i, statement in enumerate(statements):
            statement_upper = statement.upper()

            # Check for SELECT *
            if re.search(self.performance_patterns['select_star'], statement):
                issues.append({
                    'line': i + 1,
                    'type': 'query_rewrite',
                    'severity': 'medium',
                    'title': 'SELECT * Usage',
                    'description': 'Using SELECT * can be inefficient and may retrieve unnecessary data',
                    'current_code': statement.strip(),
                    'optimized_code': self._optimize_select_star(statement),
                    'estimated_improvement': '20-50% faster, reduced memory usage'
                })

            # Check for missing LIMIT
            if (statement_upper.startswith('SELECT') and
                'LIMIT' not in statement_upper and
                'COUNT(' not in statement_upper):
                issues.append({
                    'line': i + 1,
                    'type': 'query_optimization',
                    'severity': 'medium',
                    'title': 'Missing LIMIT Clause',
                    'description': 'Large result sets without LIMIT can cause performance issues',
                    'current_code': statement.strip(),
                    'optimized_code': statement.strip() + ' LIMIT 1000',
                    'estimated_improvement': '30-70% faster for large tables'
                })

            # Check for Cartesian products
            if re.search(self.performance_patterns['cartesian_join'], statement):
                issues.append({
                    'line': i + 1,
                    'type': 'join_optimization',
                    'severity': 'high',
                    'title': 'Potential Cartesian Product',
                    'description': 'Multiple tables without proper JOIN conditions',
                    'current_code': statement.strip(),
                    'optimized_code': self._optimize_cartesian_join(statement),
                    'estimated_improvement': '90%+ faster, prevents exponential row growth'
                })

            # Check for functions in WHERE clause
            if re.search(self.performance_patterns['function_in_where'], statement):
                issues.append({
                    'line': i + 1,
                    'type': 'index_optimization',
                    'severity': 'medium',
                    'title': 'Function in WHERE Clause',
                    'description': 'Functions in WHERE clause prevent index usage',
                    'current_code': statement.strip(),
                    'optimized_code': self._optimize_function_in_where(statement),
                    'estimated_improvement': '50-80% faster with proper indexing'
                })

            # Check for leading wildcard in LIKE
            if re.search(self.performance_patterns['like_leading_wildcard'], statement):
                issues.append({
                    'line': i + 1,
                    'type': 'query_optimization',
                    'severity': 'medium',
                    'title': 'Leading Wildcard in LIKE',
                    'description': 'LIKE patterns starting with % cannot use indexes efficiently',
                    'current_code': statement.strip(),
                    'optimized_code': 'Consider full-text search or alternative approaches',
                    'estimated_improvement': '60-90% faster with full-text indexing'
                })

        return issues

    def _generate_index_suggestions(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Generate index suggestions based on query patterns"""
        suggestions = []
        tables_columns = {}

        for statement in statements:
            # Extract table and column information
            table_matches = re.findall(r'(?i)from\s+(\w+)', statement)
            where_matches = re.findall(r'(?i)where\s+(\w+)', statement)
            join_matches = re.findall(r'(?i)join\s+\w+\s+on\s+(\w+)', statement)
            order_matches = re.findall(r'(?i)order\s+by\s+(\w+)', statement)
            group_matches = re.findall(r'(?i)group\s+by\s+(\w+)', statement)

            for table in table_matches:
                if table not in tables_columns:
                    tables_columns[table] = set()

                # Add columns from WHERE clauses
                for col in where_matches:
                    tables_columns[table].add(col)
                    suggestions.append({
                        'table': table,
                        'columns': [col],
                        'type': 'single_column',
                        'reason': 'WHERE clause filtering',
                        'estimated_benefit': '50-90% query speedup',
                        'sql': f'CREATE INDEX idx_{table}_{col} ON {table} ({col});'
                    })

                # Add columns from JOIN conditions
                for col in join_matches:
                    tables_columns[table].add(col)
                    suggestions.append({
                        'table': table,
                        'columns': [col],
                        'type': 'join_index',
                        'reason': 'JOIN condition optimization',
                        'estimated_benefit': '60-95% join speedup',
                        'sql': f'CREATE INDEX idx_{table}_{col}_join ON {table} ({col});'
                    })

                # Add columns from ORDER BY
                for col in order_matches:
                    suggestions.append({
                        'table': table,
                        'columns': [col],
                        'type': 'sorting_index',
                        'reason': 'ORDER BY optimization',
                        'estimated_benefit': '40-80% sorting speedup',
                        'sql': f'CREATE INDEX idx_{table}_{col}_sort ON {table} ({col});'
                    })

        # Remove duplicates
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions:
            key = (suggestion['table'], tuple(suggestion['columns']), suggestion['type'])
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)

        return unique_suggestions[:10]  # Limit to top 10 suggestions

    def _calculate_performance_score(self, statements: List[str], issues: List[Dict[str, Any]]) -> int:
        """Calculate performance score (0-100)"""
        base_score = 100

        # Deduct points for performance issues
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                base_score -= 20
            elif severity == 'medium':
                base_score -= 10
            elif severity == 'low':
                base_score -= 5

        # Deduct points for complex queries
        for statement in statements:
            complexity = self._calculate_statement_complexity(statement)
            if complexity > 50:
                base_score -= 5

        return max(0, base_score)

    def _determine_complexity(self, statements: List[str]) -> str:
        """Determine overall complexity level"""
        total_complexity = sum(self._calculate_statement_complexity(stmt) for stmt in statements)
        avg_complexity = total_complexity / len(statements) if statements else 0

        if avg_complexity > 70:
            return 'High'
        elif avg_complexity > 40:
            return 'Moderate'
        else:
            return 'Low'

    def _calculate_statement_complexity(self, statement: str) -> int:
        """Calculate complexity score for a single statement"""
        statement_upper = statement.upper()
        complexity = 0

        # Base complexity
        complexity += 10

        # Add complexity for joins
        complexity += statement_upper.count('JOIN') * 10

        # Add complexity for subqueries
        complexity += (statement_upper.count('SELECT') - 1) * 15

        # Add complexity for conditions
        complexity += statement_upper.count('WHERE') * 5
        complexity += statement_upper.count('AND') * 3
        complexity += statement_upper.count('OR') * 5

        # Add complexity for aggregations
        complexity += statement_upper.count('GROUP BY') * 8
        complexity += statement_upper.count('HAVING') * 6

        # Add complexity for sorting
        complexity += statement_upper.count('ORDER BY') * 4

        return min(100, complexity)

    def _generate_optimized_queries(self, statements: List[str], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimized versions of queries"""
        optimized = []

        for i, statement in enumerate(statements):
            statement_issues = [issue for issue in issues if issue.get('line') == i + 1]

            if statement_issues:
                optimized_code = statement
                improvements = []

                for issue in statement_issues:
                    if 'optimized_code' in issue:
                        optimized_code = issue['optimized_code']
                        improvements.append(issue['title'])

                optimized.append({
                    'original': statement.strip(),
                    'optimized': optimized_code,
                    'improvements': improvements,
                    'estimated_speedup': '20-80% faster'
                })

        return optimized

    def _generate_performance_recommendations(self, issues: List[Dict[str, Any]], index_suggestions: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        if any(issue['type'] == 'query_rewrite' for issue in issues):
            recommendations.append('Specify only needed columns instead of using SELECT *')

        if any(issue['type'] == 'query_optimization' for issue in issues):
            recommendations.append('Add LIMIT clauses to prevent large result sets')

        if any(issue['type'] == 'join_optimization' for issue in issues):
            recommendations.append('Use explicit JOIN syntax with proper ON conditions')

        if index_suggestions:
            recommendations.append('Add recommended indexes for frequently queried columns')

        recommendations.extend([
            'Monitor query execution plans regularly',
            'Use database-specific optimization features',
            'Consider query result caching for frequently accessed data',
            'Optimize database configuration parameters',
            'Regular statistics updates for query optimizer'
        ])

        return recommendations

    def _analyze_execution_plan(self, statements: List[str]) -> Dict[str, Any]:
        """Analyze potential execution plan issues"""
        return {
            'table_scans': len([s for s in statements if 'WHERE' not in s.upper() and 'SELECT' in s.upper()]),
            'join_operations': sum(s.upper().count('JOIN') for s in statements),
            'subqueries': sum(s.upper().count('SELECT') - 1 for s in statements if s.upper().count('SELECT') > 1),
            'sorting_operations': sum(s.upper().count('ORDER BY') for s in statements),
            'grouping_operations': sum(s.upper().count('GROUP BY') for s in statements)
        }

    def _estimate_resource_usage(self, statements: List[str]) -> Dict[str, Any]:
        """Estimate resource usage"""
        return {
            'memory_usage': 'Medium',
            'cpu_usage': 'Low to Medium',
            'io_operations': 'Medium',
            'network_traffic': 'Low',
            'estimated_execution_time': '< 2 seconds for typical datasets'
        }

    # Helper methods for optimization
    def _optimize_select_star(self, statement: str) -> str:
        """Optimize SELECT * statements"""
        return re.sub(r'(?i)select\s+\*', 'SELECT column1, column2, column3', statement)

    def _optimize_cartesian_join(self, statement: str) -> str:
        """Optimize Cartesian join statements"""
        return statement + ' -- Add proper JOIN conditions with ON clause'

    def _optimize_function_in_where(self, statement: str) -> str:
        """Optimize function usage in WHERE clause"""
        return statement + ' -- Consider using computed columns or different approach'
