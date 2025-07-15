"""
SQL Utilities for SQL Analyzer

Common SQL operations, formatting, and utility functions.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Set
import sqlparse
from sqlparse import sql, tokens as T, keywords

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLUtils:
    """Utility class for SQL operations."""
    
    # Common SQL keywords by category
    SQL_KEYWORDS = {
        'DDL': ['CREATE', 'ALTER', 'DROP', 'TRUNCATE'],
        'DML': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'DCL': ['GRANT', 'REVOKE'],
        'TCL': ['COMMIT', 'ROLLBACK', 'SAVEPOINT'],
        'JOINS': ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS'],
        'CLAUSES': ['WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET'],
        'FUNCTIONS': ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT']
    }
    
    # SQL data types by database
    DATA_TYPES = {
        'NUMERIC': ['INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL'],
        'STRING': ['VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT', 'TINYTEXT'],
        'DATE_TIME': ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR'],
        'BINARY': ['BINARY', 'VARBINARY', 'BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB'],
        'OTHER': ['BOOLEAN', 'BOOL', 'BIT', 'JSON', 'XML', 'UUID', 'ENUM', 'SET']
    }
    
    @staticmethod
    def format_sql(sql_content: str, reindent: bool = True, strip_comments: bool = False) -> str:
        """
        Format SQL content for better readability.
        
        Args:
            sql_content: SQL content to format
            reindent: Whether to reindent the SQL
            strip_comments: Whether to remove comments
            
        Returns:
            Formatted SQL content
        """
        try:
            formatted = sqlparse.format(
                sql_content,
                reindent=reindent,
                strip_comments=strip_comments,
                keyword_case='upper',
                identifier_case='lower'
            )
            return formatted
        except Exception as e:
            logger.warning(f"Error formatting SQL: {e}")
            return sql_content
    
    @staticmethod
    def split_sql_statements(sql_content: str) -> List[str]:
        """
        Split SQL content into individual statements.
        
        Args:
            sql_content: SQL content to split
            
        Returns:
            List of SQL statements
        """
        try:
            statements = sqlparse.split(sql_content)
            return [stmt.strip() for stmt in statements if stmt.strip()]
        except Exception as e:
            logger.warning(f"Error splitting SQL statements: {e}")
            return [sql_content]
    
    @staticmethod
    def extract_table_names(sql_statement: str) -> List[str]:
        """
        Extract table names from SQL statement.
        
        Args:
            sql_statement: SQL statement to analyze
            
        Returns:
            List of table names
        """
        table_names = []
        
        try:
            parsed = sqlparse.parse(sql_statement)[0]
            tokens = list(parsed.flatten())
            
            # Look for table names after specific keywords
            keywords_before_table = ['FROM', 'JOIN', 'INTO', 'UPDATE', 'TABLE']
            
            for i, token in enumerate(tokens):
                if (token.ttype is T.Keyword and 
                    token.value.upper() in keywords_before_table):
                    
                    # Look for the next name token
                    for j in range(i + 1, len(tokens)):
                        if tokens[j].ttype is T.Name:
                            table_name = tokens[j].value.strip('`"[]')
                            if table_name not in table_names:
                                table_names.append(table_name)
                            break
                        elif tokens[j].ttype is T.Keyword:
                            break
            
        except Exception as e:
            logger.warning(f"Error extracting table names: {e}")
        
        return table_names
    
    @staticmethod
    def extract_column_names(sql_statement: str) -> List[str]:
        """
        Extract column names from SQL statement.
        
        Args:
            sql_statement: SQL statement to analyze
            
        Returns:
            List of column names
        """
        column_names = []
        
        try:
            # Simple regex-based extraction for SELECT statements
            if sql_statement.upper().strip().startswith('SELECT'):
                # Extract columns between SELECT and FROM
                select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_statement, re.IGNORECASE | re.DOTALL)
                if select_match:
                    columns_part = select_match.group(1)
                    
                    # Skip if SELECT *
                    if '*' not in columns_part:
                        # Split by comma and clean up
                        columns = [col.strip() for col in columns_part.split(',')]
                        for col in columns:
                            # Remove aliases (AS keyword)
                            col_clean = re.sub(r'\s+AS\s+\w+', '', col, flags=re.IGNORECASE)
                            # Extract just the column name (remove table prefix)
                            if '.' in col_clean:
                                col_clean = col_clean.split('.')[-1]
                            col_clean = col_clean.strip('`"[]')
                            if col_clean and col_clean not in column_names:
                                column_names.append(col_clean)
            
        except Exception as e:
            logger.warning(f"Error extracting column names: {e}")
        
        return column_names
    
    @staticmethod
    def get_statement_type(sql_statement: str) -> str:
        """
        Get the type of SQL statement.
        
        Args:
            sql_statement: SQL statement to analyze
            
        Returns:
            Statement type (SELECT, INSERT, UPDATE, etc.)
        """
        try:
            parsed = sqlparse.parse(sql_statement)[0]
            
            for token in parsed.flatten():
                if token.ttype is T.Keyword:
                    return token.value.upper()
            
        except Exception as e:
            logger.warning(f"Error getting statement type: {e}")
        
        return 'UNKNOWN'
    
    @staticmethod
    def is_valid_identifier(identifier: str) -> bool:
        """
        Check if a string is a valid SQL identifier.
        
        Args:
            identifier: String to check
            
        Returns:
            True if valid identifier
        """
        if not identifier:
            return False
        
        # SQL identifier rules:
        # - Must start with letter or underscore
        # - Can contain letters, digits, underscores
        # - Cannot be a reserved keyword (unless quoted)
        
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        
        if not re.match(pattern, identifier):
            return False
        
        # Check if it's a reserved keyword
        if identifier.upper() in keywords.KEYWORDS:
            return False
        
        return True
    
    @staticmethod
    def normalize_whitespace(sql_content: str) -> str:
        """
        Normalize whitespace in SQL content.
        
        Args:
            sql_content: SQL content to normalize
            
        Returns:
            SQL content with normalized whitespace
        """
        # Replace multiple whitespace with single space
        normalized = re.sub(r'\s+', ' ', sql_content)
        
        # Remove leading/trailing whitespace
        normalized = normalized.strip()
        
        return normalized
    
    @staticmethod
    def remove_comments(sql_content: str) -> str:
        """
        Remove comments from SQL content.
        
        Args:
            sql_content: SQL content with comments
            
        Returns:
            SQL content without comments
        """
        # Remove single-line comments (-- style)
        sql_content = re.sub(r'--.*$', '', sql_content, flags=re.MULTILINE)
        
        # Remove multi-line comments (/* */ style)
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        return sql_content
    
    @staticmethod
    def extract_create_table_info(create_table_sql: str) -> Dict[str, any]:
        """
        Extract information from CREATE TABLE statement.
        
        Args:
            create_table_sql: CREATE TABLE SQL statement
            
        Returns:
            Dictionary with table information
        """
        info = {
            'table_name': None,
            'columns': [],
            'primary_keys': [],
            'foreign_keys': [],
            'constraints': []
        }
        
        try:
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', 
                                  create_table_sql, re.IGNORECASE)
            if table_match:
                info['table_name'] = table_match.group(1)
            
            # Extract column definitions
            # Find content between parentheses
            paren_match = re.search(r'\((.*)\)', create_table_sql, re.DOTALL)
            if paren_match:
                columns_part = paren_match.group(1)
                
                # Split by comma (simple approach)
                column_defs = [col.strip() for col in columns_part.split(',')]
                
                for col_def in column_defs:
                    col_def = col_def.strip()
                    if not col_def:
                        continue
                    
                    # Extract column name and type
                    parts = col_def.split()
                    if len(parts) >= 2:
                        col_name = parts[0].strip('`"[]')
                        col_type = parts[1]
                        
                        column_info = {
                            'name': col_name,
                            'type': col_type,
                            'nullable': 'NOT NULL' not in col_def.upper(),
                            'primary_key': 'PRIMARY KEY' in col_def.upper(),
                            'auto_increment': any(keyword in col_def.upper() 
                                                for keyword in ['AUTO_INCREMENT', 'AUTOINCREMENT', 'SERIAL'])
                        }
                        
                        info['columns'].append(column_info)
                        
                        if column_info['primary_key']:
                            info['primary_keys'].append(col_name)
            
        except Exception as e:
            logger.warning(f"Error extracting CREATE TABLE info: {e}")
        
        return info
    
    @staticmethod
    def get_sql_complexity_score(sql_statement: str) -> int:
        """
        Calculate complexity score for SQL statement.
        
        Args:
            sql_statement: SQL statement to analyze
            
        Returns:
            Complexity score (higher = more complex)
        """
        score = 0
        sql_upper = sql_statement.upper()
        
        # Base score for statement type
        if 'SELECT' in sql_upper:
            score += 1
        if 'INSERT' in sql_upper:
            score += 2
        if 'UPDATE' in sql_upper:
            score += 3
        if 'DELETE' in sql_upper:
            score += 3
        
        # Add score for joins
        join_keywords = ['JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN']
        for join_type in join_keywords:
            score += sql_upper.count(join_type) * 2
        
        # Add score for subqueries
        score += sql_statement.count('(') * 1
        
        # Add score for complex clauses
        complex_clauses = ['WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'UNION']
        for clause in complex_clauses:
            if clause in sql_upper:
                score += 1
        
        # Add score for functions
        functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN']
        for func in functions:
            score += sql_upper.count(func) * 1
        
        return score
    
    @staticmethod
    def validate_sql_syntax(sql_statement: str) -> Tuple[bool, List[str]]:
        """
        Basic SQL syntax validation.
        
        Args:
            sql_statement: SQL statement to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Try to parse with sqlparse
            parsed = sqlparse.parse(sql_statement)
            if not parsed:
                errors.append("Failed to parse SQL statement")
                return False, errors
            
            # Check for basic syntax issues
            sql_upper = sql_statement.upper().strip()
            
            # Check for unmatched parentheses
            open_parens = sql_statement.count('(')
            close_parens = sql_statement.count(')')
            if open_parens != close_parens:
                errors.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
            
            # Check for unmatched quotes
            single_quotes = sql_statement.count("'")
            if single_quotes % 2 != 0:
                errors.append("Unmatched single quotes")
            
            double_quotes = sql_statement.count('"')
            if double_quotes % 2 != 0:
                errors.append("Unmatched double quotes")
            
            # Check for basic statement structure
            if sql_upper.startswith('SELECT') and 'FROM' not in sql_upper:
                errors.append("SELECT statement missing FROM clause")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Syntax validation error: {str(e)}")
            return False, errors
