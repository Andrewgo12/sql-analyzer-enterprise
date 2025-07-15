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
# NLTK - use local implementation
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
except ImportError:
    from .local_nltk import nltk, word_tokenize
    from .local_nltk import corpus as nltk_corpus
    stopwords = nltk_corpus.stopwords
# Text distance - use local implementation
try:
    from textdistance import levenshtein
except ImportError:
    from .local_textdistance import levenshtein

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
