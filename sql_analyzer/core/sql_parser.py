"""
SQL Parser and Analyzer Module

Advanced SQL parsing engine that analyzes syntax, detects errors, 
identifies table business domains, and provides intelligent insights.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import sqlparse
from sqlparse import sql, tokens as T
from sqlparse.keywords import KEYWORDS
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textdistance import levenshtein

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)


class StatementType(Enum):
    """SQL statement types."""
    CREATE_TABLE = "CREATE_TABLE"
    CREATE_INDEX = "CREATE_INDEX"
    CREATE_VIEW = "CREATE_VIEW"
    CREATE_PROCEDURE = "CREATE_PROCEDURE"
    CREATE_FUNCTION = "CREATE_FUNCTION"
    CREATE_TRIGGER = "CREATE_TRIGGER"
    ALTER_TABLE = "ALTER_TABLE"
    DROP_TABLE = "DROP_TABLE"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    COMMENT = "COMMENT"
    UNKNOWN = "UNKNOWN"


class BusinessDomain(Enum):
    """Business domain classifications for database tables."""
    HEALTHCARE = "Healthcare"
    FINANCE = "Finance"
    ECOMMERCE = "E-commerce"
    EDUCATION = "Education"
    HUMAN_RESOURCES = "Human Resources"
    INVENTORY = "Inventory Management"
    CUSTOMER_MANAGEMENT = "Customer Management"
    SECURITY = "Security & Authentication"
    AUDIT = "Audit & Logging"
    CONFIGURATION = "Configuration"
    REPORTING = "Reporting & Analytics"
    COMMUNICATION = "Communication"
    GEOGRAPHIC = "Geographic & Location"
    TEMPORAL = "Temporal & Scheduling"
    UNKNOWN = "Unknown"


@dataclass
class Column:
    """Represents a database column."""
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: bool = False
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None
    default_value: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    comment: Optional[str] = None


@dataclass
class Table:
    """Represents a database table."""
    name: str
    columns: List[Column] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    comment: Optional[str] = None
    business_domain: BusinessDomain = BusinessDomain.UNKNOWN
    estimated_purpose: Optional[str] = None


@dataclass
class SQLStatement:
    """Represents a parsed SQL statement."""
    original_text: str
    statement_type: StatementType
    table_name: Optional[str] = None
    columns: List[str] = field(default_factory=list)
    referenced_tables: List[str] = field(default_factory=list)
    line_number: int = 0
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class SQLParser:
    """
    Advanced SQL parser with business domain analysis and error detection.
    
    Features:
    - Parse SQL statements and extract table/column information
    - Identify business domains based on table/column names
    - Detect syntax errors and provide suggestions
    - Analyze table relationships and dependencies
    - Generate schema insights and recommendations
    """
    
    # Business domain keywords for classification
    DOMAIN_KEYWORDS = {
        BusinessDomain.HEALTHCARE: [
            'patient', 'doctor', 'hospital', 'medical', 'diagnosis', 'treatment',
            'prescription', 'medication', 'clinic', 'nurse', 'surgery', 'appointment',
            'symptom', 'disease', 'health', 'vital', 'blood', 'test', 'lab', 'radiology'
        ],
        BusinessDomain.FINANCE: [
            'account', 'transaction', 'payment', 'invoice', 'billing', 'credit',
            'debit', 'balance', 'bank', 'loan', 'interest', 'currency', 'exchange',
            'financial', 'budget', 'expense', 'revenue', 'profit', 'tax', 'audit'
        ],
        BusinessDomain.ECOMMERCE: [
            'product', 'order', 'cart', 'customer', 'purchase', 'inventory',
            'catalog', 'category', 'price', 'discount', 'coupon', 'shipping',
            'delivery', 'warehouse', 'supplier', 'vendor', 'review', 'rating'
        ],
        BusinessDomain.EDUCATION: [
            'student', 'teacher', 'course', 'class', 'grade', 'exam', 'assignment',
            'school', 'university', 'enrollment', 'semester', 'subject', 'curriculum',
            'academic', 'education', 'learning', 'instructor', 'faculty'
        ],
        BusinessDomain.HUMAN_RESOURCES: [
            'employee', 'staff', 'personnel', 'payroll', 'salary', 'wage',
            'department', 'position', 'job', 'hire', 'recruitment', 'performance',
            'evaluation', 'training', 'benefit', 'leave', 'attendance', 'hr'
        ],
        BusinessDomain.SECURITY: [
            'user', 'password', 'login', 'authentication', 'authorization', 'role',
            'permission', 'access', 'security', 'token', 'session', 'credential',
            'encrypt', 'decrypt', 'hash', 'salt', 'oauth', 'ldap'
        ],
        BusinessDomain.AUDIT: [
            'log', 'audit', 'history', 'change', 'track', 'monitor', 'event',
            'activity', 'trace', 'record', 'timestamp', 'version', 'revision'
        ],
        BusinessDomain.GEOGRAPHIC: [
            'address', 'location', 'city', 'state', 'country', 'region', 'zip',
            'postal', 'coordinate', 'latitude', 'longitude', 'map', 'geographic'
        ]
    }
    
    def __init__(self):
        """Initialize the SQL parser."""
        self.parsed_statements: List[SQLStatement] = []
        self.tables: Dict[str, Table] = {}
        self.stop_words = set(stopwords.words('english'))
        
    def parse_sql_file(self, sql_content: List[str]) -> List[SQLStatement]:
        """
        Parse SQL content and return list of parsed statements.
        
        Args:
            sql_content: List of SQL lines
            
        Returns:
            List of parsed SQL statements
        """
        self.parsed_statements = []
        self.tables = {}
        
        # Join lines and split into statements
        full_content = '\n'.join(sql_content)
        statements = sqlparse.split(full_content)
        
        line_number = 1
        for statement_text in statements:
            if statement_text.strip():
                try:
                    parsed_stmt = self._parse_statement(statement_text, line_number)
                    self.parsed_statements.append(parsed_stmt)
                    
                    # Update line number based on statement content
                    line_number += statement_text.count('\n') + 1
                    
                except Exception as e:
                    logger.warning(f"Error parsing statement at line {line_number}: {e}")
                    error_stmt = SQLStatement(
                        original_text=statement_text,
                        statement_type=StatementType.UNKNOWN,
                        line_number=line_number,
                        is_valid=False,
                        errors=[f"Parse error: {str(e)}"]
                    )
                    self.parsed_statements.append(error_stmt)
        
        # Analyze relationships and business domains
        self._analyze_table_relationships()
        self._classify_business_domains()
        
        return self.parsed_statements
    
    def _parse_statement(self, statement_text: str, line_number: int) -> SQLStatement:
        """
        Parse a single SQL statement.
        
        Args:
            statement_text: SQL statement text
            line_number: Line number in the original file
            
        Returns:
            Parsed SQL statement
        """
        parsed = sqlparse.parse(statement_text)[0]
        
        # Determine statement type
        stmt_type = self._get_statement_type(parsed)
        
        # Extract table and column information
        table_name = None
        columns = []
        referenced_tables = []
        
        if stmt_type == StatementType.CREATE_TABLE:
            table_name, columns = self._parse_create_table(parsed)
            if table_name:
                self._add_table_to_schema(table_name, columns, statement_text)
        elif stmt_type in [StatementType.INSERT, StatementType.UPDATE, StatementType.DELETE]:
            table_name = self._extract_table_name(parsed)
            if table_name:
                referenced_tables.append(table_name)
        elif stmt_type == StatementType.SELECT:
            referenced_tables = self._extract_referenced_tables(parsed)
        
        # Validate statement and detect errors
        is_valid, errors, warnings, suggestions = self._validate_statement(parsed, stmt_type)
        
        return SQLStatement(
            original_text=statement_text,
            statement_type=stmt_type,
            table_name=table_name,
            columns=columns,
            referenced_tables=referenced_tables,
            line_number=line_number,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def _get_statement_type(self, parsed) -> StatementType:
        """Determine the type of SQL statement."""
        first_token = None
        second_token = None

        for token in parsed.flatten():
            if token.ttype is T.Keyword:
                if first_token is None:
                    first_token = token.value.upper()
                elif second_token is None:
                    second_token = token.value.upper()
                    break

        if first_token == 'CREATE':
            if second_token == 'TABLE':
                return StatementType.CREATE_TABLE
            elif second_token == 'INDEX':
                return StatementType.CREATE_INDEX
            elif second_token == 'VIEW':
                return StatementType.CREATE_VIEW
            elif second_token in ['PROCEDURE', 'PROC']:
                return StatementType.CREATE_PROCEDURE
            elif second_token == 'FUNCTION':
                return StatementType.CREATE_FUNCTION
            elif second_token == 'TRIGGER':
                return StatementType.CREATE_TRIGGER
        elif first_token == 'ALTER':
            return StatementType.ALTER_TABLE
        elif first_token == 'DROP':
            return StatementType.DROP_TABLE
        elif first_token == 'INSERT':
            return StatementType.INSERT
        elif first_token == 'UPDATE':
            return StatementType.UPDATE
        elif first_token == 'DELETE':
            return StatementType.DELETE
        elif first_token == 'SELECT':
            return StatementType.SELECT
        elif first_token == 'GRANT':
            return StatementType.GRANT
        elif first_token == 'REVOKE':
            return StatementType.REVOKE

        return StatementType.UNKNOWN

    def _parse_create_table(self, parsed) -> Tuple[Optional[str], List[str]]:
        """Parse CREATE TABLE statement to extract table name and columns."""
        table_name = None
        columns = []

        tokens = list(parsed.flatten())

        # Find table name
        create_found = False
        table_found = False
        for i, token in enumerate(tokens):
            if token.ttype is T.Keyword and token.value.upper() == 'CREATE':
                create_found = True
            elif create_found and token.ttype is T.Keyword and token.value.upper() == 'TABLE':
                table_found = True
            elif table_found and token.ttype is T.Name:
                table_name = token.value
                break

        # Extract column definitions
        in_parentheses = False
        current_column = ""

        for token in tokens:
            if token.value == '(':
                in_parentheses = True
                continue
            elif token.value == ')':
                if current_column.strip():
                    columns.append(current_column.strip())
                break
            elif in_parentheses:
                if token.value == ',':
                    if current_column.strip():
                        columns.append(current_column.strip())
                        current_column = ""
                else:
                    current_column += token.value

        return table_name, columns

    def _extract_table_name(self, parsed) -> Optional[str]:
        """Extract table name from INSERT, UPDATE, DELETE statements."""
        tokens = list(parsed.flatten())

        for i, token in enumerate(tokens):
            if token.ttype is T.Keyword and token.value.upper() in ['FROM', 'INTO', 'UPDATE']:
                # Look for the next name token
                for j in range(i + 1, len(tokens)):
                    if tokens[j].ttype is T.Name:
                        return tokens[j].value

        return None

    def _extract_referenced_tables(self, parsed) -> List[str]:
        """Extract all referenced table names from SELECT statements."""
        tables = []
        tokens = list(parsed.flatten())

        from_found = False
        join_found = False

        for i, token in enumerate(tokens):
            if token.ttype is T.Keyword:
                keyword = token.value.upper()
                if keyword == 'FROM':
                    from_found = True
                    join_found = False
                elif keyword in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS']:
                    join_found = True
                elif keyword in ['WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT']:
                    from_found = False
                    join_found = False
            elif (from_found or join_found) and token.ttype is T.Name:
                if token.value not in tables:
                    tables.append(token.value)
                from_found = False
                join_found = False

        return tables

    def _validate_statement(self, parsed, stmt_type: StatementType) -> Tuple[bool, List[str], List[str], List[str]]:
        """Validate SQL statement and provide error detection."""
        errors = []
        warnings = []
        suggestions = []

        # Check for common syntax errors
        statement_text = str(parsed).strip()

        # Check for missing semicolon
        if not statement_text.endswith(';') and stmt_type != StatementType.COMMENT:
            warnings.append("Statement should end with semicolon (;)")
            suggestions.append("Add semicolon at the end of the statement")

        # Check for trailing commas
        if ',)' in statement_text or ', )' in statement_text:
            errors.append("Trailing comma before closing parenthesis")
            suggestions.append("Remove trailing comma before closing parenthesis")

        # Check for unmatched parentheses
        open_parens = statement_text.count('(')
        close_parens = statement_text.count(')')
        if open_parens != close_parens:
            errors.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
            suggestions.append("Check and balance parentheses")

        # Check for reserved word usage as identifiers
        tokens = list(parsed.flatten())
        for token in tokens:
            if token.ttype is T.Name and token.value.upper() in KEYWORDS:
                warnings.append(f"'{token.value}' is a reserved keyword used as identifier")
                suggestions.append(f"Consider renaming '{token.value}' or use quotes/backticks")

        # Statement-specific validations
        if stmt_type == StatementType.CREATE_TABLE:
            self._validate_create_table(parsed, errors, warnings, suggestions)
        elif stmt_type == StatementType.SELECT:
            self._validate_select(parsed, errors, warnings, suggestions)

        is_valid = len(errors) == 0
        return is_valid, errors, warnings, suggestions

    def _validate_create_table(self, parsed, errors: List[str], warnings: List[str], suggestions: List[str]):
        """Validate CREATE TABLE statements."""
        statement_text = str(parsed).upper()

        # Check for primary key
        if 'PRIMARY KEY' not in statement_text:
            warnings.append("Table does not have a primary key defined")
            suggestions.append("Consider adding a primary key for better performance and data integrity")

        # Check for data types
        common_types = ['INT', 'VARCHAR', 'TEXT', 'DATE', 'TIMESTAMP', 'DECIMAL', 'FLOAT', 'BOOLEAN']
        has_data_type = any(dtype in statement_text for dtype in common_types)
        if not has_data_type:
            warnings.append("No common data types found in table definition")

    def _validate_select(self, parsed, errors: List[str], warnings: List[str], suggestions: List[str]):
        """Validate SELECT statements."""
        statement_text = str(parsed).upper()

        # Check for SELECT *
        if 'SELECT *' in statement_text:
            warnings.append("Using SELECT * can impact performance")
            suggestions.append("Consider specifying only needed columns")

        # Check for missing WHERE clause in potentially large tables
        if 'WHERE' not in statement_text and 'LIMIT' not in statement_text:
            warnings.append("Query without WHERE clause may return large result set")
            suggestions.append("Consider adding WHERE clause or LIMIT to improve performance")

    def _add_table_to_schema(self, table_name: str, column_definitions: List[str], statement_text: str):
        """Add parsed table to schema dictionary."""
        columns = []
        primary_keys = []
        foreign_keys = []
        constraints = []

        for col_def in column_definitions:
            col_def = col_def.strip()
            if not col_def:
                continue

            # Parse column definition
            parts = col_def.split()
            if len(parts) >= 2:
                col_name = parts[0].strip('`"[]')
                data_type = parts[1]

                # Check for constraints
                col_def_upper = col_def.upper()
                nullable = 'NOT NULL' not in col_def_upper
                primary_key = 'PRIMARY KEY' in col_def_upper

                if primary_key:
                    primary_keys.append(col_name)

                # Check for foreign key
                foreign_key = False
                foreign_table = None
                foreign_column = None
                if 'REFERENCES' in col_def_upper:
                    foreign_key = True
                    # Extract foreign key reference
                    ref_match = re.search(r'REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', col_def_upper)
                    if ref_match:
                        foreign_table = ref_match.group(1)
                        foreign_column = ref_match.group(2)
                        foreign_keys.append({
                            'column': col_name,
                            'references_table': foreign_table,
                            'references_column': foreign_column
                        })

                # Extract default value
                default_value = None
                default_match = re.search(r'DEFAULT\s+([^,\s]+)', col_def_upper)
                if default_match:
                    default_value = default_match.group(1)

                column = Column(
                    name=col_name,
                    data_type=data_type,
                    nullable=nullable,
                    primary_key=primary_key,
                    foreign_key=foreign_key,
                    foreign_table=foreign_table,
                    foreign_column=foreign_column,
                    default_value=default_value
                )
                columns.append(column)

        # Create table object
        table = Table(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            constraints=constraints
        )

        self.tables[table_name] = table

    def _analyze_table_relationships(self):
        """Analyze relationships between tables."""
        for table_name, table in self.tables.items():
            # Analyze foreign key relationships
            for fk in table.foreign_keys:
                referenced_table = fk['references_table']
                if referenced_table in self.tables:
                    # Add relationship information
                    logger.info(f"Found relationship: {table_name}.{fk['column']} -> {referenced_table}.{fk['references_column']}")

    def _classify_business_domains(self):
        """Classify tables into business domains based on names and content."""
        for table_name, table in self.tables.items():
            domain_scores = {domain: 0 for domain in BusinessDomain}

            # Analyze table name
            table_words = self._extract_words(table_name)

            # Analyze column names
            column_words = []
            for column in table.columns:
                column_words.extend(self._extract_words(column.name))

            all_words = table_words + column_words

            # Score against domain keywords
            for domain, keywords in self.DOMAIN_KEYWORDS.items():
                for word in all_words:
                    if word.lower() in keywords:
                        domain_scores[domain] += 1
                    else:
                        # Check for partial matches using Levenshtein distance
                        for keyword in keywords:
                            if levenshtein(word.lower(), keyword) <= 2 and len(word) > 3:
                                domain_scores[domain] += 0.5

            # Assign domain with highest score
            if max(domain_scores.values()) > 0:
                best_domain = max(domain_scores, key=domain_scores.get)
                table.business_domain = best_domain

                # Generate purpose estimation
                table.estimated_purpose = self._estimate_table_purpose(table_name, table.columns, best_domain)

    def _extract_words(self, text: str) -> List[str]:
        """Extract meaningful words from table/column names."""
        # Split on common separators
        words = re.split(r'[_\-\s]+', text.lower())

        # Remove stop words and short words
        meaningful_words = []
        for word in words:
            if len(word) > 2 and word not in self.stop_words:
                meaningful_words.append(word)

        return meaningful_words

    def _estimate_table_purpose(self, table_name: str, columns: List[Column], domain: BusinessDomain) -> str:
        """Estimate the purpose of a table based on its structure and domain."""
        column_names = [col.name.lower() for col in columns]

        # Common patterns
        if any('log' in name or 'audit' in name for name in column_names + [table_name.lower()]):
            return f"Audit/logging table for {domain.value.lower()} operations"
        elif any('config' in name or 'setting' in name for name in column_names + [table_name.lower()]):
            return f"Configuration table for {domain.value.lower()} settings"
        elif any('user' in name or 'person' in name for name in column_names + [table_name.lower()]):
            return f"User/person management table for {domain.value.lower()}"
        elif any('transaction' in name or 'payment' in name for name in column_names + [table_name.lower()]):
            return f"Transaction/payment table for {domain.value.lower()}"
        else:
            return f"Data table for {domain.value.lower()} domain"

    def get_schema_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the parsed schema."""
        if not self.tables:
            return {}

        domain_distribution = {}
        for table in self.tables.values():
            domain = table.business_domain.value
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

        total_columns = sum(len(table.columns) for table in self.tables.values())
        tables_with_pk = sum(1 for table in self.tables.values() if table.primary_keys)
        tables_with_fk = sum(1 for table in self.tables.values() if table.foreign_keys)

        return {
            'total_tables': len(self.tables),
            'total_columns': total_columns,
            'average_columns_per_table': round(total_columns / len(self.tables), 2),
            'tables_with_primary_keys': tables_with_pk,
            'tables_with_foreign_keys': tables_with_fk,
            'domain_distribution': domain_distribution,
            'data_integrity_score': round((tables_with_pk / len(self.tables)) * 100, 2),
            'relationship_score': round((tables_with_fk / len(self.tables)) * 100, 2)
        }

    def get_table_details(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific table."""
        if table_name not in self.tables:
            return None

        table = self.tables[table_name]

        return {
            'name': table.name,
            'business_domain': table.business_domain.value,
            'estimated_purpose': table.estimated_purpose,
            'column_count': len(table.columns),
            'primary_keys': table.primary_keys,
            'foreign_keys': table.foreign_keys,
            'columns': [
                {
                    'name': col.name,
                    'type': col.data_type,
                    'nullable': col.nullable,
                    'primary_key': col.primary_key,
                    'foreign_key': col.foreign_key,
                    'foreign_reference': f"{col.foreign_table}.{col.foreign_column}" if col.foreign_key else None,
                    'default_value': col.default_value
                }
                for col in table.columns
            ]
        }
