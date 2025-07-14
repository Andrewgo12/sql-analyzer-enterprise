"""
Error Detection and Correction Engine

Comprehensive SQL error detection with detailed commenting and automatic 
correction suggestions. Provides intelligent analysis of SQL syntax errors,
logic issues, and best practice violations.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import sqlparse
from sqlparse import sql, tokens as T

# Optional imports for enhanced functionality
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False

try:
    from textdistance import levenshtein
    TEXTDISTANCE_AVAILABLE = True
except ImportError:
    TEXTDISTANCE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "CRITICAL"  # Prevents execution
    ERROR = "ERROR"        # Causes runtime errors
    WARNING = "WARNING"    # Potential issues
    INFO = "INFO"         # Best practice suggestions
    STYLE = "STYLE"       # Code style improvements


class ErrorCategory(Enum):
    """Categories of SQL errors."""
    SYNTAX = "Syntax Error"
    LOGIC = "Logic Error"
    PERFORMANCE = "Performance Issue"
    SECURITY = "Security Issue"
    BEST_PRACTICE = "Best Practice Violation"
    DATA_INTEGRITY = "Data Integrity Issue"
    NAMING = "Naming Convention"
    COMPATIBILITY = "Database Compatibility"


@dataclass
class SQLError:
    """Represents a detected SQL error."""
    line_number: int
    column_number: int = 0
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.SYNTAX
    message: str = ""
    description: str = ""
    original_code: str = ""
    suggested_fix: str = ""
    explanation: str = ""
    rule_id: str = ""
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class CorrectionResult:
    """Result of SQL correction process."""
    original_sql: str
    corrected_sql: str
    errors_found: List[SQLError] = field(default_factory=list)
    corrections_applied: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


class ErrorDetector:
    """
    Comprehensive SQL error detection and correction engine.
    
    Features:
    - Syntax error detection and correction
    - Logic error identification
    - Performance issue detection
    - Security vulnerability scanning
    - Best practice enforcement
    - Automatic correction suggestions
    - Detailed error explanations
    """
    
    # Common SQL keywords for validation
    SQL_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
        'ALTER', 'TABLE', 'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION', 'TRIGGER',
        'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS', 'ON', 'USING',
        'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'INTERSECT',
        'EXCEPT', 'DISTINCT', 'ALL', 'AS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
    }
    
    # Common data types
    DATA_TYPES = {
        'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
        'VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT',
        'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL',
        'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR',
        'BOOLEAN', 'BOOL', 'BIT', 'BINARY', 'VARBINARY',
        'BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB',
        'JSON', 'XML', 'UUID', 'ENUM', 'SET'
    }
    
    # Dangerous SQL patterns (security)
    DANGEROUS_PATTERNS = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+.*\s+SET',
        r'UNION\s+SELECT.*--',
        r'OR\s+1\s*=\s*1',
        r'OR\s+\'1\'\s*=\s*\'1\'',
        r'EXEC\s*\(',
        r'EXECUTE\s*\(',
        r'xp_cmdshell',
        r'sp_executesql'
    ]
    
    def __init__(self):
        """Initialize the error detector."""
        self.detected_errors: List[SQLError] = []
        self.correction_rules = self._load_correction_rules()
    
    def analyze_sql(self, sql_content: str, line_offset: int = 0) -> List[SQLError]:
        """
        Analyze SQL content and detect errors.
        
        Args:
            sql_content: SQL content to analyze
            line_offset: Line number offset for error reporting
            
        Returns:
            List of detected errors
        """
        self.detected_errors = []
        
        # Split into statements for analysis
        statements = sqlparse.split(sql_content)
        current_line = line_offset + 1
        
        for statement in statements:
            if statement.strip():
                try:
                    self._analyze_statement(statement, current_line)
                    current_line += statement.count('\n') + 1
                except Exception as e:
                    logger.warning(f"Error analyzing statement at line {current_line}: {e}")
        
        return self.detected_errors
    
    def _analyze_statement(self, statement: str, line_number: int):
        """Analyze a single SQL statement for errors."""
        # Parse the statement
        try:
            parsed = sqlparse.parse(statement)[0]
        except Exception as e:
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SYNTAX,
                message="Failed to parse SQL statement",
                description=f"Parser error: {str(e)}",
                original_code=statement.strip(),
                rule_id="PARSE_ERROR"
            )
            return
        
        # Run various error detection checks
        self._check_syntax_errors(statement, parsed, line_number)
        self._check_logic_errors(statement, parsed, line_number)
        self._check_performance_issues(statement, parsed, line_number)
        self._check_security_issues(statement, parsed, line_number)
        self._check_best_practices(statement, parsed, line_number)
        self._check_naming_conventions(statement, parsed, line_number)
    
    def _check_syntax_errors(self, statement: str, parsed, line_number: int):
        """Check for syntax errors."""
        statement_upper = statement.upper()
        
        # Check for unmatched parentheses
        open_parens = statement.count('(')
        close_parens = statement.count(')')
        if open_parens != close_parens:
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SYNTAX,
                message="Unmatched parentheses",
                description=f"Found {open_parens} opening and {close_parens} closing parentheses",
                original_code=statement.strip(),
                suggested_fix="Balance the parentheses",
                explanation="Each opening parenthesis must have a corresponding closing parenthesis",
                rule_id="UNMATCHED_PARENS"
            )
        
        # Check for trailing commas
        if re.search(r',\s*\)', statement):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.SYNTAX,
                message="Trailing comma before closing parenthesis",
                description="Found comma immediately before closing parenthesis",
                original_code=statement.strip(),
                suggested_fix=re.sub(r',\s*\)', ')', statement),
                explanation="Remove the trailing comma before the closing parenthesis",
                rule_id="TRAILING_COMMA"
            )
        
        # Check for missing semicolon
        if not statement.strip().endswith(';') and not statement.strip().endswith('*/'):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.BEST_PRACTICE,
                message="Missing semicolon",
                description="SQL statement should end with semicolon",
                original_code=statement.strip(),
                suggested_fix=statement.strip() + ';',
                explanation="Adding semicolon improves SQL readability and is required in many contexts",
                rule_id="MISSING_SEMICOLON"
            )
        
        # Check for invalid keywords
        tokens = list(parsed.flatten())
        for token in tokens:
            if token.ttype is T.Name and token.value.upper() in self.SQL_KEYWORDS:
                # Check if it's being used as an identifier
                if self._is_used_as_identifier(token, tokens):
                    self._add_error(
                        line_number=line_number,
                        severity=ErrorSeverity.WARNING,
                        category=ErrorCategory.NAMING,
                        message=f"Reserved keyword '{token.value}' used as identifier",
                        description=f"'{token.value}' is a reserved SQL keyword",
                        original_code=statement.strip(),
                        suggested_fix=f"Use `{token.value}` or [{token.value}] or \"{token.value}\"",
                        explanation="Reserved keywords should be quoted when used as identifiers",
                        rule_id="RESERVED_KEYWORD"
                    )
    
    def _check_logic_errors(self, statement: str, parsed, line_number: int):
        """Check for logical errors in SQL."""
        statement_upper = statement.upper()
        
        # Check for impossible conditions
        if re.search(r'WHERE\s+1\s*=\s*0', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.LOGIC,
                message="Impossible WHERE condition",
                description="WHERE 1=0 will never return any results",
                original_code=statement.strip(),
                suggested_fix="Remove the impossible condition or use a valid condition",
                explanation="This condition will always evaluate to false",
                rule_id="IMPOSSIBLE_CONDITION"
            )
        
        # Check for redundant conditions
        if re.search(r'WHERE\s+1\s*=\s*1', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.INFO,
                category=ErrorCategory.LOGIC,
                message="Redundant WHERE condition",
                description="WHERE 1=1 is always true and redundant",
                original_code=statement.strip(),
                suggested_fix="Remove the redundant condition",
                explanation="This condition is always true and serves no filtering purpose",
                rule_id="REDUNDANT_CONDITION"
            )
        
        # Check for potential NULL comparison issues
        if re.search(r'=\s*NULL|NULL\s*=', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.LOGIC,
                message="Incorrect NULL comparison",
                description="Use IS NULL or IS NOT NULL instead of = NULL",
                original_code=statement.strip(),
                suggested_fix=re.sub(r'=\s*NULL', 'IS NULL', statement, flags=re.IGNORECASE),
                explanation="NULL values cannot be compared using = operator",
                rule_id="NULL_COMPARISON"
            )

    def _check_performance_issues(self, statement: str, parsed, line_number: int):
        """Check for performance-related issues."""
        statement_upper = statement.upper()

        # Check for SELECT *
        if 'SELECT *' in statement_upper:
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.PERFORMANCE,
                message="SELECT * usage",
                description="Using SELECT * can impact performance and maintainability",
                original_code=statement.strip(),
                suggested_fix="Specify only the columns you need",
                explanation="SELECT * retrieves all columns, which may be unnecessary and slow",
                rule_id="SELECT_STAR"
            )

        # Check for missing WHERE clause in DELETE/UPDATE
        if re.search(r'DELETE\s+FROM\s+\w+(?!\s+WHERE)', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.PERFORMANCE,
                message="DELETE without WHERE clause",
                description="DELETE without WHERE will remove all rows",
                original_code=statement.strip(),
                suggested_fix="Add WHERE clause to limit deletion",
                explanation="This will delete all rows from the table",
                rule_id="DELETE_NO_WHERE"
            )

        if re.search(r'UPDATE\s+\w+\s+SET\s+.*(?!\s+WHERE)', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.PERFORMANCE,
                message="UPDATE without WHERE clause",
                description="UPDATE without WHERE will modify all rows",
                original_code=statement.strip(),
                suggested_fix="Add WHERE clause to limit update scope",
                explanation="This will update all rows in the table",
                rule_id="UPDATE_NO_WHERE"
            )

        # Check for functions in WHERE clause
        if re.search(r'WHERE\s+.*\b(UPPER|LOWER|SUBSTRING|LEFT|RIGHT)\s*\(', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.PERFORMANCE,
                message="Function in WHERE clause",
                description="Functions in WHERE clause can prevent index usage",
                original_code=statement.strip(),
                suggested_fix="Consider using functional indexes or restructuring the query",
                explanation="Functions on columns in WHERE clause can make queries slower",
                rule_id="FUNCTION_IN_WHERE"
            )

    def _check_security_issues(self, statement: str, parsed, line_number: int):
        """Check for security vulnerabilities."""
        statement_upper = statement.upper()

        # Check for SQL injection patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, statement_upper):
                self._add_error(
                    line_number=line_number,
                    severity=ErrorSeverity.CRITICAL,
                    category=ErrorCategory.SECURITY,
                    message="Potential SQL injection pattern",
                    description=f"Detected dangerous pattern: {pattern}",
                    original_code=statement.strip(),
                    suggested_fix="Use parameterized queries instead",
                    explanation="This pattern is commonly used in SQL injection attacks",
                    rule_id="SQL_INJECTION"
                )

        # Check for dynamic SQL construction
        if re.search(r'EXEC\s*\(\s*[\'"].*\+.*[\'"]', statement_upper):
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.SECURITY,
                message="Dynamic SQL construction",
                description="Dynamic SQL construction can be vulnerable to injection",
                original_code=statement.strip(),
                suggested_fix="Use parameterized queries or stored procedures",
                explanation="Building SQL strings dynamically increases injection risk",
                rule_id="DYNAMIC_SQL"
            )

    def _check_best_practices(self, statement: str, parsed, line_number: int):
        """Check for best practice violations."""
        statement_upper = statement.upper()

        # Check for table aliases
        if 'FROM' in statement_upper and 'JOIN' in statement_upper:
            # Complex query should use aliases
            if not re.search(r'\w+\s+AS\s+\w+|\w+\s+\w+(?=\s+(?:WHERE|JOIN|ON))', statement):
                self._add_error(
                    line_number=line_number,
                    severity=ErrorSeverity.INFO,
                    category=ErrorCategory.BEST_PRACTICE,
                    message="Consider using table aliases",
                    description="Table aliases improve readability in complex queries",
                    original_code=statement.strip(),
                    suggested_fix="Add aliases like: FROM table_name AS t1",
                    explanation="Aliases make complex queries more readable and maintainable",
                    rule_id="USE_ALIASES"
                )

        # Check for ORDER BY with LIMIT
        if 'LIMIT' in statement_upper and 'ORDER BY' not in statement_upper:
            self._add_error(
                line_number=line_number,
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.BEST_PRACTICE,
                message="LIMIT without ORDER BY",
                description="LIMIT without ORDER BY may return unpredictable results",
                original_code=statement.strip(),
                suggested_fix="Add ORDER BY clause before LIMIT",
                explanation="Without ORDER BY, LIMIT may return different rows each time",
                rule_id="LIMIT_NO_ORDER"
            )

    def _check_naming_conventions(self, statement: str, parsed, line_number: int):
        """Check naming convention compliance."""
        tokens = list(parsed.flatten())

        for token in tokens:
            if token.ttype is T.Name:
                name = token.value

                # Check for mixed case without quotes
                if re.search(r'[a-z][A-Z]|[A-Z][a-z]', name) and not name.startswith('"'):
                    self._add_error(
                        line_number=line_number,
                        severity=ErrorSeverity.STYLE,
                        category=ErrorCategory.NAMING,
                        message="Mixed case identifier",
                        description=f"Identifier '{name}' uses mixed case",
                        original_code=statement.strip(),
                        suggested_fix=f"Use snake_case: {self._to_snake_case(name)}",
                        explanation="Consistent naming conventions improve code readability",
                        rule_id="MIXED_CASE"
                    )

                # Check for very short names
                if len(name) == 1 and name.lower() not in ['a', 'b', 'i', 'j', 'x', 'y']:
                    self._add_error(
                        line_number=line_number,
                        severity=ErrorSeverity.INFO,
                        category=ErrorCategory.NAMING,
                        message="Very short identifier",
                        description=f"Identifier '{name}' is very short",
                        original_code=statement.strip(),
                        suggested_fix="Use more descriptive names",
                        explanation="Descriptive names improve code maintainability",
                        rule_id="SHORT_NAME"
                    )

    def _add_error(self, line_number: int, severity: ErrorSeverity, category: ErrorCategory,
                   message: str, description: str, original_code: str,
                   suggested_fix: str = "", explanation: str = "", rule_id: str = "",
                   column_number: int = 0, confidence: float = 1.0):
        """Add an error to the detected errors list."""
        error = SQLError(
            line_number=line_number,
            column_number=column_number,
            severity=severity,
            category=category,
            message=message,
            description=description,
            original_code=original_code,
            suggested_fix=suggested_fix,
            explanation=explanation,
            rule_id=rule_id,
            confidence=confidence
        )
        self.detected_errors.append(error)

    def _is_used_as_identifier(self, token, tokens) -> bool:
        """Check if a token is being used as an identifier."""
        # Simple heuristic: if it follows CREATE TABLE, ALTER TABLE, etc.
        token_index = tokens.index(token)
        if token_index > 0:
            prev_token = tokens[token_index - 1]
            if prev_token.ttype is T.Keyword and prev_token.value.upper() in ['TABLE', 'INDEX', 'VIEW']:
                return True
        return False

    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Insert underscore before uppercase letters
        result = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        return result.lower()

    def _load_correction_rules(self) -> Dict[str, Any]:
        """Load correction rules for automatic fixes."""
        return {
            'TRAILING_COMMA': {
                'pattern': r',\s*\)',
                'replacement': ')',
                'description': 'Remove trailing comma'
            },
            'NULL_COMPARISON': {
                'pattern': r'=\s*NULL',
                'replacement': 'IS NULL',
                'description': 'Use IS NULL instead of = NULL'
            },
            'MISSING_SEMICOLON': {
                'pattern': r'([^;])\s*$',
                'replacement': r'\1;',
                'description': 'Add missing semicolon'
            }
        }

    def correct_sql(self, sql_content: str) -> CorrectionResult:
        """
        Automatically correct SQL based on detected errors.

        Args:
            sql_content: Original SQL content

        Returns:
            CorrectionResult with corrections applied
        """
        # First, analyze for errors
        errors = self.analyze_sql(sql_content)

        corrected_sql = sql_content
        corrections_applied = []
        warnings = []
        suggestions = []

        # Apply automatic corrections for fixable errors
        for error in errors:
            if error.rule_id in self.correction_rules and error.suggested_fix:
                rule = self.correction_rules[error.rule_id]
                if 'pattern' in rule and 'replacement' in rule:
                    old_sql = corrected_sql
                    corrected_sql = re.sub(rule['pattern'], rule['replacement'], corrected_sql, flags=re.IGNORECASE)
                    if old_sql != corrected_sql:
                        corrections_applied.append(f"Line {error.line_number}: {rule['description']}")
                elif error.suggested_fix != error.original_code:
                    # Use the suggested fix directly
                    corrected_sql = corrected_sql.replace(error.original_code, error.suggested_fix)
                    corrections_applied.append(f"Line {error.line_number}: {error.message}")

            # Collect warnings and suggestions
            if error.severity in [ErrorSeverity.WARNING, ErrorSeverity.INFO]:
                if error.suggested_fix:
                    suggestions.append(f"Line {error.line_number}: {error.message} - {error.explanation}")
                else:
                    warnings.append(f"Line {error.line_number}: {error.message}")

        # Calculate confidence score
        critical_errors = sum(1 for e in errors if e.severity == ErrorSeverity.CRITICAL)
        total_errors = len(errors)
        confidence_score = max(0.0, 1.0 - (critical_errors * 0.5 + total_errors * 0.1))

        return CorrectionResult(
            original_sql=sql_content,
            corrected_sql=corrected_sql,
            errors_found=errors,
            corrections_applied=corrections_applied,
            warnings=warnings,
            suggestions=suggestions,
            confidence_score=confidence_score
        )

    def generate_error_report(self, errors: List[SQLError]) -> str:
        """Generate a detailed error report."""
        if not errors:
            return "No errors detected."

        report = []
        report.append("SQL Error Analysis Report")
        report.append("=" * 50)
        report.append("")

        # Group errors by severity
        by_severity = {}
        for error in errors:
            severity = error.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(error)

        # Report by severity
        for severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR, ErrorSeverity.WARNING, ErrorSeverity.INFO, ErrorSeverity.STYLE]:
            if severity.value in by_severity:
                report.append(f"{severity.value} Issues ({len(by_severity[severity.value])})")
                report.append("-" * 30)

                for error in by_severity[severity.value]:
                    report.append(f"Line {error.line_number}: {error.message}")
                    report.append(f"  Category: {error.category.value}")
                    report.append(f"  Description: {error.description}")
                    if error.suggested_fix:
                        report.append(f"  Suggested Fix: {error.suggested_fix}")
                    if error.explanation:
                        report.append(f"  Explanation: {error.explanation}")
                    report.append("")

        return "\n".join(report)
