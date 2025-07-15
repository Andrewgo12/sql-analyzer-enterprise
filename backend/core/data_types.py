"""
Universal Data Type Support System

Comprehensive support for ALL SQL data types including database-specific,
custom types, and even the most obscure data types across all database systems.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataTypeCategory(Enum):
    """Categories of data types."""
    NUMERIC = "Numeric"
    STRING = "String/Text"
    DATE_TIME = "Date/Time"
    BOOLEAN = "Boolean"
    BINARY = "Binary/BLOB"
    JSON_XML = "JSON/XML"
    GEOMETRIC = "Geometric/Spatial"
    ARRAY = "Array/Collection"
    CUSTOM = "Custom/User-Defined"
    NETWORK = "Network/Internet"
    UUID = "UUID/Identifier"
    MONETARY = "Monetary/Currency"
    INTERVAL = "Interval/Duration"
    ENUM = "Enumeration"
    COMPOSITE = "Composite/Structured"
    RANGE = "Range/Interval"
    FULL_TEXT = "Full-Text Search"
    CRYPTOGRAPHIC = "Cryptographic"
    MACHINE_LEARNING = "Machine Learning"
    SCIENTIFIC = "Scientific/Mathematical"
    MULTIMEDIA = "Multimedia/Media"


@dataclass
class DataTypeInfo:
    """Comprehensive information about a data type."""
    name: str
    category: DataTypeCategory
    database_systems: List[str]
    aliases: List[str] = field(default_factory=list)
    size_info: Optional[str] = None
    precision_scale: Optional[Tuple[int, int]] = None
    default_value: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    conversion_rules: Dict[str, str] = field(default_factory=dict)
    validation_pattern: Optional[str] = None
    description: str = ""
    examples: List[str] = field(default_factory=list)
    storage_requirements: Optional[str] = None
    performance_notes: List[str] = field(default_factory=list)
    compatibility_notes: Dict[str, str] = field(default_factory=dict)
    deprecated: bool = False
    introduced_version: Optional[str] = None


class UniversalDataTypeRegistry:
    """
    Universal registry for ALL SQL data types across all database systems.
    
    Supports:
    - Standard SQL data types
    - Database-specific types (MySQL, PostgreSQL, Oracle, SQL Server, etc.)
    - Custom and user-defined types
    - Obscure and legacy data types
    - Scientific and specialized data types
    - Modern data types (JSON, arrays, etc.)
    """
    
    def __init__(self):
        """Initialize the universal data type registry."""
        self.data_types: Dict[str, DataTypeInfo] = {}
        self.category_index: Dict[DataTypeCategory, List[str]] = defaultdict(list)
        self.database_index: Dict[str, List[str]] = defaultdict(list)
        self.alias_index: Dict[str, str] = {}
        
        # Initialize all data types
        self._initialize_standard_types()
        self._initialize_mysql_types()
        self._initialize_postgresql_types()
        self._initialize_oracle_types()
        self._initialize_sqlserver_types()
        self._initialize_sqlite_types()
        self._initialize_specialized_types()
        self._initialize_scientific_types()
        self._initialize_legacy_types()
        self._initialize_modern_types()
        
        # Build indexes
        self._build_indexes()
    
    def _initialize_standard_types(self):
        """Initialize standard SQL data types."""
        standard_types = [
            # Numeric Types
            DataTypeInfo(
                name="INTEGER",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle"],
                aliases=["INT", "INT4"],
                size_info="4 bytes",
                default_value="0",
                description="Standard 32-bit signed integer",
                examples=["42", "-123", "2147483647"],
                storage_requirements="4 bytes",
                validation_pattern=r"^-?\d+$"
            ),
            
            DataTypeInfo(
                name="BIGINT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                aliases=["INT8", "LONG"],
                size_info="8 bytes",
                description="64-bit signed integer",
                examples=["9223372036854775807", "-9223372036854775808"],
                storage_requirements="8 bytes"
            ),
            
            DataTypeInfo(
                name="SMALLINT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                aliases=["INT2"],
                size_info="2 bytes",
                description="16-bit signed integer",
                examples=["32767", "-32768"],
                storage_requirements="2 bytes"
            ),
            
            DataTypeInfo(
                name="TINYINT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["MySQL", "SQL Server"],
                aliases=["INT1"],
                size_info="1 byte",
                description="8-bit signed integer",
                examples=["127", "-128", "0"],
                storage_requirements="1 byte"
            ),
            
            DataTypeInfo(
                name="DECIMAL",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                aliases=["NUMERIC", "DEC"],
                precision_scale=(38, 0),
                description="Exact numeric with user-defined precision and scale",
                examples=["123.45", "999999.99", "0.001"],
                storage_requirements="Variable based on precision"
            ),
            
            DataTypeInfo(
                name="FLOAT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                aliases=["REAL", "SINGLE"],
                size_info="4 bytes",
                description="Single-precision floating-point number",
                examples=["3.14159", "1.23e-4", "2.5e10"],
                storage_requirements="4 bytes"
            ),
            
            DataTypeInfo(
                name="DOUBLE",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server"],
                aliases=["DOUBLE PRECISION", "FLOAT8"],
                size_info="8 bytes",
                description="Double-precision floating-point number",
                examples=["3.141592653589793", "1.7976931348623157e+308"],
                storage_requirements="8 bytes"
            ),
            
            # String Types
            DataTypeInfo(
                name="VARCHAR",
                category=DataTypeCategory.STRING,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                aliases=["CHARACTER VARYING", "STRING"],
                size_info="Variable length up to specified maximum",
                description="Variable-length character string",
                examples=["'Hello World'", "'SQL Analyzer'", "''"],
                storage_requirements="Length + 1-2 bytes overhead"
            ),
            
            DataTypeInfo(
                name="CHAR",
                category=DataTypeCategory.STRING,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                aliases=["CHARACTER"],
                size_info="Fixed length",
                description="Fixed-length character string",
                examples=["'ABC'", "'X'", "'   '"],
                storage_requirements="Specified length"
            ),
            
            DataTypeInfo(
                name="TEXT",
                category=DataTypeCategory.STRING,
                database_systems=["MySQL", "PostgreSQL", "SQLite"],
                aliases=["LONGTEXT", "CLOB"],
                description="Variable-length text string",
                examples=["'Long text content...'", "'Multi-line\\ntext'"],
                storage_requirements="Length + overhead"
            ),
            
            # Date/Time Types
            DataTypeInfo(
                name="DATE",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server", "Oracle"],
                size_info="3-4 bytes",
                description="Date value (year, month, day)",
                examples=["'2023-12-25'", "'1970-01-01'", "'9999-12-31'"],
                storage_requirements="3-4 bytes"
            ),
            
            DataTypeInfo(
                name="TIME",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "SQL Server"],
                size_info="3-6 bytes",
                description="Time value (hour, minute, second)",
                examples=["'14:30:00'", "'23:59:59'", "'00:00:00'"],
                storage_requirements="3-6 bytes"
            ),
            
            DataTypeInfo(
                name="TIMESTAMP",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["SQL Standard", "MySQL", "PostgreSQL", "Oracle"],
                aliases=["DATETIME"],
                size_info="4-8 bytes",
                description="Date and time value",
                examples=["'2023-12-25 14:30:00'", "'1970-01-01 00:00:00'"],
                storage_requirements="4-8 bytes"
            ),
            
            # Boolean Type
            DataTypeInfo(
                name="BOOLEAN",
                category=DataTypeCategory.BOOLEAN,
                database_systems=["SQL Standard", "PostgreSQL", "SQLite"],
                aliases=["BOOL"],
                size_info="1 byte",
                description="Boolean value (true/false)",
                examples=["TRUE", "FALSE", "NULL"],
                storage_requirements="1 byte"
            ),
            
            # Binary Types
            DataTypeInfo(
                name="BLOB",
                category=DataTypeCategory.BINARY,
                database_systems=["SQLite", "MySQL", "Oracle"],
                aliases=["BINARY LARGE OBJECT"],
                description="Binary large object",
                examples=["Binary data", "Images", "Documents"],
                storage_requirements="Length + overhead"
            ),
            
            DataTypeInfo(
                name="BINARY",
                category=DataTypeCategory.BINARY,
                database_systems=["SQL Server", "MySQL"],
                size_info="Fixed length",
                description="Fixed-length binary data",
                examples=["0x48656C6C6F", "0xFF00FF"],
                storage_requirements="Specified length"
            ),
            
            DataTypeInfo(
                name="VARBINARY",
                category=DataTypeCategory.BINARY,
                database_systems=["SQL Server", "MySQL"],
                size_info="Variable length",
                description="Variable-length binary data",
                examples=["0x48656C6C6F", "0x"],
                storage_requirements="Length + overhead"
            )
        ]
        
        for data_type in standard_types:
            self.data_types[data_type.name] = data_type

    def _initialize_mysql_types(self):
        """Initialize MySQL-specific data types."""
        mysql_types = [
            # MySQL Numeric Types
            DataTypeInfo(
                name="MEDIUMINT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["MySQL"],
                size_info="3 bytes",
                description="24-bit signed integer",
                examples=["8388607", "-8388608"],
                storage_requirements="3 bytes"
            ),

            DataTypeInfo(
                name="BIT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["MySQL", "SQL Server"],
                size_info="1-64 bits",
                description="Bit field type",
                examples=["b'1010'", "b'11111111'"],
                storage_requirements="(bits + 7) / 8 bytes"
            ),

            # MySQL String Types
            DataTypeInfo(
                name="TINYTEXT",
                category=DataTypeCategory.STRING,
                database_systems=["MySQL"],
                size_info="Up to 255 characters",
                description="Very small text string",
                examples=["'Short text'"],
                storage_requirements="Length + 1 byte"
            ),

            DataTypeInfo(
                name="MEDIUMTEXT",
                category=DataTypeCategory.STRING,
                database_systems=["MySQL"],
                size_info="Up to 16,777,215 characters",
                description="Medium-length text string",
                examples=["'Medium length text...'"],
                storage_requirements="Length + 3 bytes"
            ),

            DataTypeInfo(
                name="LONGTEXT",
                category=DataTypeCategory.STRING,
                database_systems=["MySQL"],
                size_info="Up to 4,294,967,295 characters",
                description="Very long text string",
                examples=["'Very long text content...'"],
                storage_requirements="Length + 4 bytes"
            ),

            # MySQL Binary Types
            DataTypeInfo(
                name="TINYBLOB",
                category=DataTypeCategory.BINARY,
                database_systems=["MySQL"],
                size_info="Up to 255 bytes",
                description="Very small binary object",
                storage_requirements="Length + 1 byte"
            ),

            DataTypeInfo(
                name="MEDIUMBLOB",
                category=DataTypeCategory.BINARY,
                database_systems=["MySQL"],
                size_info="Up to 16,777,215 bytes",
                description="Medium binary object",
                storage_requirements="Length + 3 bytes"
            ),

            DataTypeInfo(
                name="LONGBLOB",
                category=DataTypeCategory.BINARY,
                database_systems=["MySQL"],
                size_info="Up to 4,294,967,295 bytes",
                description="Very large binary object",
                storage_requirements="Length + 4 bytes"
            ),

            # MySQL Special Types
            DataTypeInfo(
                name="ENUM",
                category=DataTypeCategory.ENUM,
                database_systems=["MySQL"],
                size_info="1-2 bytes",
                description="Enumeration of string values",
                examples=["ENUM('small','medium','large')", "ENUM('red','green','blue')"],
                storage_requirements="1-2 bytes"
            ),

            DataTypeInfo(
                name="SET",
                category=DataTypeCategory.ENUM,
                database_systems=["MySQL"],
                size_info="1-8 bytes",
                description="Set of string values",
                examples=["SET('a','b','c')", "SET('read','write','execute')"],
                storage_requirements="1-8 bytes"
            ),

            DataTypeInfo(
                name="JSON",
                category=DataTypeCategory.JSON_XML,
                database_systems=["MySQL", "PostgreSQL"],
                description="JSON document storage",
                examples=["'{\"name\": \"John\", \"age\": 30}'", "'[1, 2, 3]'"],
                storage_requirements="Variable, optimized binary format"
            ),

            DataTypeInfo(
                name="YEAR",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["MySQL"],
                size_info="1 byte",
                description="Year value (1901-2155)",
                examples=["2023", "1970", "2155"],
                storage_requirements="1 byte"
            )
        ]

        for data_type in mysql_types:
            self.data_types[data_type.name] = data_type

    def _initialize_postgresql_types(self):
        """Initialize PostgreSQL-specific data types."""
        postgresql_types = [
            # PostgreSQL Numeric Types
            DataTypeInfo(
                name="SERIAL",
                category=DataTypeCategory.NUMERIC,
                database_systems=["PostgreSQL"],
                aliases=["SERIAL4"],
                size_info="4 bytes",
                description="Auto-incrementing 4-byte integer",
                examples=["1", "2", "3"],
                storage_requirements="4 bytes"
            ),

            DataTypeInfo(
                name="BIGSERIAL",
                category=DataTypeCategory.NUMERIC,
                database_systems=["PostgreSQL"],
                aliases=["SERIAL8"],
                size_info="8 bytes",
                description="Auto-incrementing 8-byte integer",
                storage_requirements="8 bytes"
            ),

            DataTypeInfo(
                name="SMALLSERIAL",
                category=DataTypeCategory.NUMERIC,
                database_systems=["PostgreSQL"],
                aliases=["SERIAL2"],
                size_info="2 bytes",
                description="Auto-incrementing 2-byte integer",
                storage_requirements="2 bytes"
            ),

            DataTypeInfo(
                name="MONEY",
                category=DataTypeCategory.MONETARY,
                database_systems=["PostgreSQL"],
                size_info="8 bytes",
                description="Currency amount with fixed fractional precision",
                examples=["$12.34", "$1,000.00", "-$50.75"],
                storage_requirements="8 bytes"
            ),

            # PostgreSQL String Types
            DataTypeInfo(
                name="CITEXT",
                category=DataTypeCategory.STRING,
                database_systems=["PostgreSQL"],
                description="Case-insensitive text",
                examples=["'Hello'", "'HELLO'", "'hello'"],
                storage_requirements="Variable length"
            ),

            # PostgreSQL Date/Time Types
            DataTypeInfo(
                name="TIMESTAMPTZ",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["PostgreSQL"],
                aliases=["TIMESTAMP WITH TIME ZONE"],
                size_info="8 bytes",
                description="Timestamp with time zone",
                examples=["'2023-12-25 14:30:00+00'", "'2023-12-25 14:30:00 UTC'"],
                storage_requirements="8 bytes"
            ),

            DataTypeInfo(
                name="TIMETZ",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["PostgreSQL"],
                aliases=["TIME WITH TIME ZONE"],
                size_info="12 bytes",
                description="Time with time zone",
                examples=["'14:30:00+00'", "'14:30:00 UTC'"],
                storage_requirements="12 bytes"
            ),

            DataTypeInfo(
                name="INTERVAL",
                category=DataTypeCategory.INTERVAL,
                database_systems=["PostgreSQL", "SQL Server"],
                size_info="16 bytes",
                description="Time interval",
                examples=["'1 day'", "'2 hours 30 minutes'", "'1 year 2 months'"],
                storage_requirements="16 bytes"
            ),

            # PostgreSQL Network Types
            DataTypeInfo(
                name="INET",
                category=DataTypeCategory.NETWORK,
                database_systems=["PostgreSQL"],
                size_info="7-19 bytes",
                description="IPv4 or IPv6 network address",
                examples=["'192.168.1.1'", "'::1'", "'192.168.1.0/24'"],
                storage_requirements="7-19 bytes"
            ),

            DataTypeInfo(
                name="CIDR",
                category=DataTypeCategory.NETWORK,
                database_systems=["PostgreSQL"],
                size_info="7-19 bytes",
                description="IPv4 or IPv6 network specification",
                examples=["'192.168.1.0/24'", "'2001:db8::/32'"],
                storage_requirements="7-19 bytes"
            ),

            DataTypeInfo(
                name="MACADDR",
                category=DataTypeCategory.NETWORK,
                database_systems=["PostgreSQL"],
                size_info="6 bytes",
                description="MAC address",
                examples=["'08:00:2b:01:02:03'", "'08-00-2b-01-02-03'"],
                storage_requirements="6 bytes"
            ),

            DataTypeInfo(
                name="MACADDR8",
                category=DataTypeCategory.NETWORK,
                database_systems=["PostgreSQL"],
                size_info="8 bytes",
                description="MAC address (EUI-64 format)",
                examples=["'08:00:2b:01:02:03:04:05'"],
                storage_requirements="8 bytes"
            ),

            # PostgreSQL UUID Type
            DataTypeInfo(
                name="UUID",
                category=DataTypeCategory.UUID,
                database_systems=["PostgreSQL", "SQL Server"],
                size_info="16 bytes",
                description="Universally unique identifier",
                examples=["'550e8400-e29b-41d4-a716-446655440000'"],
                storage_requirements="16 bytes"
            ),

            # PostgreSQL Geometric Types
            DataTypeInfo(
                name="POINT",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="16 bytes",
                description="Point on a plane",
                examples=["'(1,2)'", "'(0,0)'", "'(-1.5,2.7)'"],
                storage_requirements="16 bytes"
            ),

            DataTypeInfo(
                name="LINE",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="32 bytes",
                description="Infinite line",
                examples=["'{1,2,3}'", "'{0,1,0}'"],
                storage_requirements="32 bytes"
            ),

            DataTypeInfo(
                name="LSEG",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="32 bytes",
                description="Line segment",
                examples=["'[(1,2),(3,4)]'", "'[(0,0),(1,1)]'"],
                storage_requirements="32 bytes"
            ),

            DataTypeInfo(
                name="BOX",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="32 bytes",
                description="Rectangular box",
                examples=["'((1,2),(3,4))'", "'((0,0),(10,10))'"],
                storage_requirements="32 bytes"
            ),

            DataTypeInfo(
                name="PATH",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="16+16n bytes",
                description="Geometric path",
                examples=["'[(1,2),(3,4),(5,6)]'", "'((0,0),(1,1),(2,0))'"],
                storage_requirements="16+16n bytes"
            ),

            DataTypeInfo(
                name="POLYGON",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="40+16n bytes",
                description="Closed geometric path",
                examples=["'((0,0),(1,1),(2,0))'", "'((0,0),(0,1),(1,1),(1,0))'"],
                storage_requirements="40+16n bytes"
            ),

            DataTypeInfo(
                name="CIRCLE",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["PostgreSQL"],
                size_info="24 bytes",
                description="Circle",
                examples=["'<(0,0),5>'", "'<(1,2),3.5>'"],
                storage_requirements="24 bytes"
            )
        ]

        for data_type in postgresql_types:
            self.data_types[data_type.name] = data_type

    def _initialize_oracle_types(self):
        """Initialize Oracle-specific data types."""
        oracle_types = [
            # Oracle Numeric Types
            DataTypeInfo(
                name="NUMBER",
                category=DataTypeCategory.NUMERIC,
                database_systems=["Oracle"],
                precision_scale=(38, 127),
                description="Oracle's universal numeric type",
                examples=["123", "123.45", "1.23E+10"],
                storage_requirements="Variable, 1-22 bytes"
            ),

            DataTypeInfo(
                name="BINARY_FLOAT",
                category=DataTypeCategory.NUMERIC,
                database_systems=["Oracle"],
                size_info="4 bytes",
                description="32-bit floating point number",
                examples=["3.14159f", "1.23e-4f"],
                storage_requirements="4 bytes"
            ),

            DataTypeInfo(
                name="BINARY_DOUBLE",
                category=DataTypeCategory.NUMERIC,
                database_systems=["Oracle"],
                size_info="8 bytes",
                description="64-bit floating point number",
                examples=["3.141592653589793d", "1.7976931348623157e+308d"],
                storage_requirements="8 bytes"
            ),

            # Oracle String Types
            DataTypeInfo(
                name="VARCHAR2",
                category=DataTypeCategory.STRING,
                database_systems=["Oracle"],
                size_info="Up to 32,767 bytes",
                description="Variable-length character string (Oracle)",
                examples=["'Hello Oracle'", "'Variable length'"],
                storage_requirements="Length + overhead"
            ),

            DataTypeInfo(
                name="NVARCHAR2",
                category=DataTypeCategory.STRING,
                database_systems=["Oracle"],
                size_info="Up to 32,767 bytes",
                description="Variable-length Unicode character string",
                examples=["N'Unicode text'", "N'多言語テキスト'"],
                storage_requirements="Length * 2 + overhead"
            ),

            DataTypeInfo(
                name="CLOB",
                category=DataTypeCategory.STRING,
                database_systems=["Oracle", "SQL Server"],
                description="Character Large Object",
                examples=["'Very large text content...'"],
                storage_requirements="Up to 128TB"
            ),

            DataTypeInfo(
                name="NCLOB",
                category=DataTypeCategory.STRING,
                database_systems=["Oracle"],
                description="National Character Large Object",
                examples=["N'Very large Unicode text...'"],
                storage_requirements="Up to 128TB"
            ),

            # Oracle Date/Time Types
            DataTypeInfo(
                name="TIMESTAMP WITH TIME ZONE",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["Oracle", "PostgreSQL"],
                size_info="13 bytes",
                description="Timestamp with time zone information",
                examples=["'25-DEC-23 02.30.00.000000 PM +05:30'"],
                storage_requirements="13 bytes"
            ),

            DataTypeInfo(
                name="TIMESTAMP WITH LOCAL TIME ZONE",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["Oracle"],
                size_info="11 bytes",
                description="Timestamp normalized to database time zone",
                examples=["'25-DEC-23 02.30.00.000000 PM'"],
                storage_requirements="11 bytes"
            ),

            DataTypeInfo(
                name="INTERVAL YEAR TO MONTH",
                category=DataTypeCategory.INTERVAL,
                database_systems=["Oracle"],
                size_info="5 bytes",
                description="Interval of years and months",
                examples=["INTERVAL '1-2' YEAR TO MONTH", "INTERVAL '123' MONTH"],
                storage_requirements="5 bytes"
            ),

            DataTypeInfo(
                name="INTERVAL DAY TO SECOND",
                category=DataTypeCategory.INTERVAL,
                database_systems=["Oracle"],
                size_info="11 bytes",
                description="Interval of days, hours, minutes, and seconds",
                examples=["INTERVAL '4 5:12:10.222' DAY TO SECOND"],
                storage_requirements="11 bytes"
            ),

            # Oracle Binary Types
            DataTypeInfo(
                name="RAW",
                category=DataTypeCategory.BINARY,
                database_systems=["Oracle"],
                size_info="Up to 32,767 bytes",
                description="Variable-length raw binary data",
                examples=["HEXTORAW('48656C6C6F')"],
                storage_requirements="Length + overhead"
            ),

            DataTypeInfo(
                name="LONG RAW",
                category=DataTypeCategory.BINARY,
                database_systems=["Oracle"],
                size_info="Up to 2GB",
                description="Variable-length raw binary data (deprecated)",
                deprecated=True,
                storage_requirements="Up to 2GB"
            ),

            # Oracle Spatial Types
            DataTypeInfo(
                name="SDO_GEOMETRY",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["Oracle"],
                description="Oracle Spatial geometry object",
                examples=["SDO_GEOMETRY(2001, NULL, SDO_POINT_TYPE(1,2,NULL), NULL, NULL)"],
                storage_requirements="Variable"
            ),

            # Oracle XML Type
            DataTypeInfo(
                name="XMLTYPE",
                category=DataTypeCategory.JSON_XML,
                database_systems=["Oracle"],
                description="XML document storage",
                examples=["XMLType('<root><element>value</element></root>')"],
                storage_requirements="Variable"
            )
        ]

        for data_type in oracle_types:
            self.data_types[data_type.name] = data_type

    def _initialize_sqlserver_types(self):
        """Initialize SQL Server-specific data types."""
        sqlserver_types = [
            # SQL Server String Types
            DataTypeInfo(
                name="NVARCHAR",
                category=DataTypeCategory.STRING,
                database_systems=["SQL Server"],
                size_info="Up to 4,000 characters",
                description="Variable-length Unicode character string",
                examples=["N'Unicode text'", "N'العربية'", "N'中文'"],
                storage_requirements="2 * length + 2 bytes"
            ),

            DataTypeInfo(
                name="NCHAR",
                category=DataTypeCategory.STRING,
                database_systems=["SQL Server"],
                size_info="Fixed length",
                description="Fixed-length Unicode character string",
                examples=["N'ABC'", "N'固定'"],
                storage_requirements="2 * length bytes"
            ),

            DataTypeInfo(
                name="NTEXT",
                category=DataTypeCategory.STRING,
                database_systems=["SQL Server"],
                description="Variable-length Unicode text (deprecated)",
                deprecated=True,
                storage_requirements="Variable"
            ),

            # SQL Server Date/Time Types
            DataTypeInfo(
                name="DATETIME2",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["SQL Server"],
                size_info="6-8 bytes",
                description="Date and time with fractional seconds",
                examples=["'2023-12-25 14:30:00.1234567'"],
                storage_requirements="6-8 bytes"
            ),

            DataTypeInfo(
                name="SMALLDATETIME",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["SQL Server"],
                size_info="4 bytes",
                description="Date and time with minute precision",
                examples=["'2023-12-25 14:30'"],
                storage_requirements="4 bytes"
            ),

            DataTypeInfo(
                name="DATETIMEOFFSET",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["SQL Server"],
                size_info="8-10 bytes",
                description="Date and time with time zone offset",
                examples=["'2023-12-25 14:30:00.1234567 +05:30'"],
                storage_requirements="8-10 bytes"
            ),

            # SQL Server Numeric Types
            DataTypeInfo(
                name="MONEY",
                category=DataTypeCategory.MONETARY,
                database_systems=["SQL Server"],
                size_info="8 bytes",
                description="Monetary data with 4 decimal places",
                examples=["$12.34", "$1000.0000"],
                storage_requirements="8 bytes"
            ),

            DataTypeInfo(
                name="SMALLMONEY",
                category=DataTypeCategory.MONETARY,
                database_systems=["SQL Server"],
                size_info="4 bytes",
                description="Small monetary data with 4 decimal places",
                examples=["$12.34", "$214748.3647"],
                storage_requirements="4 bytes"
            ),

            # SQL Server Binary Types
            DataTypeInfo(
                name="IMAGE",
                category=DataTypeCategory.BINARY,
                database_systems=["SQL Server"],
                description="Variable-length binary data (deprecated)",
                deprecated=True,
                storage_requirements="Up to 2GB"
            ),

            # SQL Server Special Types
            DataTypeInfo(
                name="UNIQUEIDENTIFIER",
                category=DataTypeCategory.UUID,
                database_systems=["SQL Server"],
                size_info="16 bytes",
                description="Globally unique identifier (GUID)",
                examples=["'6F9619FF-8B86-D011-B42D-00C04FC964FF'"],
                storage_requirements="16 bytes"
            ),

            DataTypeInfo(
                name="SQL_VARIANT",
                category=DataTypeCategory.CUSTOM,
                database_systems=["SQL Server"],
                size_info="Up to 8,016 bytes",
                description="Stores values of various data types",
                examples=["123", "'text'", "'2023-12-25'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="TABLE",
                category=DataTypeCategory.COMPOSITE,
                database_systems=["SQL Server"],
                description="Table-valued parameter type",
                examples=["DECLARE @table TABLE (id INT, name VARCHAR(50))"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="CURSOR",
                category=DataTypeCategory.CUSTOM,
                database_systems=["SQL Server"],
                description="Reference to a cursor",
                examples=["DECLARE @cursor CURSOR"],
                storage_requirements="Variable"
            ),

            # SQL Server Spatial Types
            DataTypeInfo(
                name="GEOMETRY",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["SQL Server"],
                description="Planar spatial data",
                examples=["geometry::Point(1, 2, 0)"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="GEOGRAPHY",
                category=DataTypeCategory.GEOMETRIC,
                database_systems=["SQL Server"],
                description="Ellipsoidal (round-earth) spatial data",
                examples=["geography::Point(47.65100, -122.34900, 4326)"],
                storage_requirements="Variable"
            ),

            # SQL Server Hierarchical Type
            DataTypeInfo(
                name="HIERARCHYID",
                category=DataTypeCategory.CUSTOM,
                database_systems=["SQL Server"],
                size_info="Variable",
                description="Variable length system data type for hierarchical data",
                examples=["'/1/1/3/'", "'/1/2/'"],
                storage_requirements="Variable"
            )
        ]

        for data_type in sqlserver_types:
            self.data_types[data_type.name] = data_type

    def _initialize_sqlite_types(self):
        """Initialize SQLite-specific data types."""
        sqlite_types = [
            # SQLite has dynamic typing, but these are common affinity types
            DataTypeInfo(
                name="NUMERIC",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQLite"],
                description="Numeric affinity in SQLite",
                examples=["123", "123.45", "'123'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="REAL",
                category=DataTypeCategory.NUMERIC,
                database_systems=["SQLite", "PostgreSQL"],
                size_info="8 bytes",
                description="Floating point value",
                examples=["3.14159", "1.23e-4"],
                storage_requirements="8 bytes"
            ),

            # SQLite doesn't have true data types, but these are recognized
            DataTypeInfo(
                name="NONE",
                category=DataTypeCategory.CUSTOM,
                database_systems=["SQLite"],
                description="No affinity (SQLite specific)",
                examples=["Any value type"],
                storage_requirements="Variable"
            )
        ]

        for data_type in sqlite_types:
            self.data_types[data_type.name] = data_type

    def _initialize_specialized_types(self):
        """Initialize specialized and domain-specific data types."""
        specialized_types = [
            # Array Types
            DataTypeInfo(
                name="ARRAY",
                category=DataTypeCategory.ARRAY,
                database_systems=["PostgreSQL"],
                description="Array of elements",
                examples=["'{1,2,3}'", "'{\"a\",\"b\",\"c\"}'", "'{{1,2},{3,4}}'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="INT[]",
                category=DataTypeCategory.ARRAY,
                database_systems=["PostgreSQL"],
                description="Array of integers",
                examples=["'{1,2,3,4,5}'", "'{}'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="TEXT[]",
                category=DataTypeCategory.ARRAY,
                database_systems=["PostgreSQL"],
                description="Array of text values",
                examples=["'{\"hello\",\"world\"}'", "'{\"a\",\"b\",\"c\"}'"],
                storage_requirements="Variable"
            ),

            # Range Types (PostgreSQL)
            DataTypeInfo(
                name="INT4RANGE",
                category=DataTypeCategory.RANGE,
                database_systems=["PostgreSQL"],
                description="Range of integers",
                examples=["'[1,10)'", "'(5,15]'", "'[1,1]'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="INT8RANGE",
                category=DataTypeCategory.RANGE,
                database_systems=["PostgreSQL"],
                description="Range of bigints",
                examples=["'[1000000000,2000000000)'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="NUMRANGE",
                category=DataTypeCategory.RANGE,
                database_systems=["PostgreSQL"],
                description="Range of numeric values",
                examples=["'[1.5,10.75)'", "'(0,1)'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="TSRANGE",
                category=DataTypeCategory.RANGE,
                database_systems=["PostgreSQL"],
                description="Range of timestamps",
                examples=["'[2023-01-01,2023-12-31)'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="TSTZRANGE",
                category=DataTypeCategory.RANGE,
                database_systems=["PostgreSQL"],
                description="Range of timestamps with time zone",
                examples=["'[2023-01-01 00:00:00+00,2023-12-31 23:59:59+00)'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="DATERANGE",
                category=DataTypeCategory.RANGE,
                database_systems=["PostgreSQL"],
                description="Range of dates",
                examples=["'[2023-01-01,2023-12-31]'", "'[2023-01-01,)'"],
                storage_requirements="Variable"
            ),

            # Full-Text Search Types
            DataTypeInfo(
                name="TSVECTOR",
                category=DataTypeCategory.FULL_TEXT,
                database_systems=["PostgreSQL"],
                description="Text search vector",
                examples=["'a:1 fat:2 cat:3 sat:4 on:5 a:6 mat:7'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="TSQUERY",
                category=DataTypeCategory.FULL_TEXT,
                database_systems=["PostgreSQL"],
                description="Text search query",
                examples=["'fat & cat'", "'fat | rat'", "'!cat'"],
                storage_requirements="Variable"
            ),

            # Composite Types
            DataTypeInfo(
                name="RECORD",
                category=DataTypeCategory.COMPOSITE,
                database_systems=["PostgreSQL"],
                description="Composite type (record)",
                examples=["ROW(1, 'text', true)"],
                storage_requirements="Variable"
            ),

            # Cryptographic Types
            DataTypeInfo(
                name="BYTEA",
                category=DataTypeCategory.CRYPTOGRAPHIC,
                database_systems=["PostgreSQL"],
                description="Binary data (byte array)",
                examples=["'\\x48656c6c6f'", "'\\000\\001\\002'"],
                storage_requirements="Variable"
            ),

            # Machine Learning Types (PostgreSQL extensions)
            DataTypeInfo(
                name="VECTOR",
                category=DataTypeCategory.MACHINE_LEARNING,
                database_systems=["PostgreSQL"],
                description="Vector for machine learning (pgvector extension)",
                examples=["'[1,2,3]'", "'[0.1,0.2,0.3,0.4]'"],
                storage_requirements="4 * dimensions + 8 bytes"
            ),

            DataTypeInfo(
                name="HALFVEC",
                category=DataTypeCategory.MACHINE_LEARNING,
                database_systems=["PostgreSQL"],
                description="Half-precision vector (pgvector extension)",
                examples=["'[1,2,3]'::halfvec"],
                storage_requirements="2 * dimensions + 8 bytes"
            ),

            DataTypeInfo(
                name="SPARSEVEC",
                category=DataTypeCategory.MACHINE_LEARNING,
                database_systems=["PostgreSQL"],
                description="Sparse vector (pgvector extension)",
                examples=["'{1:0.1,3:0.3,5:0.5}/10'"],
                storage_requirements="Variable"
            )
        ]

        for data_type in specialized_types:
            self.data_types[data_type.name] = data_type

    def _initialize_scientific_types(self):
        """Initialize scientific and mathematical data types."""
        scientific_types = [
            # Scientific Numeric Types
            DataTypeInfo(
                name="COMPLEX",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Complex number (real + imaginary)",
                examples=["'3+4i'", "'1.5-2.7i'", "'0+1i'"],
                storage_requirements="16 bytes (2 doubles)"
            ),

            DataTypeInfo(
                name="QUATERNION",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Quaternion for 3D rotations",
                examples=["'1+2i+3j+4k'", "'0.707+0+0+0.707k'"],
                storage_requirements="32 bytes (4 doubles)"
            ),

            DataTypeInfo(
                name="MATRIX",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Mathematical matrix",
                examples=["'[[1,2],[3,4]]'", "'[[1,0,0],[0,1,0],[0,0,1]]'"],
                storage_requirements="Variable"
            ),

            # Chemical Types
            DataTypeInfo(
                name="MOLECULE",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Chemical molecule structure",
                examples=["'CCO'", "'C1=CC=CC=C1'", "'CC(=O)O'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="SMILES",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="SMILES chemical notation",
                examples=["'CCO'", "'C1=CC=CC=C1'", "'CC(=O)O'"],
                storage_requirements="Variable"
            ),

            # Biological Types
            DataTypeInfo(
                name="DNA_SEQUENCE",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="DNA sequence data",
                examples=["'ATCGATCGATCG'", "'AAATTTCCCGGG'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="PROTEIN_SEQUENCE",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Protein amino acid sequence",
                examples=["'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'"],
                storage_requirements="Variable"
            ),

            # Astronomical Types
            DataTypeInfo(
                name="CELESTIAL_COORDINATE",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Celestial coordinates (RA/Dec)",
                examples=["'14h39m36.49s -60°50′02.3″'", "'J2000 12:30:45.6 +41:16:09'"],
                storage_requirements="16 bytes"
            ),

            # Physics Types
            DataTypeInfo(
                name="UNIT_VALUE",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Value with physical units",
                examples=["'9.8 m/s²'", "'299792458 m/s'", "'6.626e-34 J⋅s'"],
                storage_requirements="Variable"
            ),

            # Statistical Types
            DataTypeInfo(
                name="DISTRIBUTION",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Statistical distribution parameters",
                examples=["'normal(0,1)'", "'exponential(0.5)'", "'uniform(0,10)'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="HISTOGRAM",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Histogram data structure",
                examples=["'{bins:[0,1,2,3,4], counts:[10,20,15,5]}'"],
                storage_requirements="Variable"
            )
        ]

        for data_type in scientific_types:
            self.data_types[data_type.name] = data_type

    def _initialize_legacy_types(self):
        """Initialize legacy and deprecated data types."""
        legacy_types = [
            # Legacy Oracle Types
            DataTypeInfo(
                name="LONG",
                category=DataTypeCategory.STRING,
                database_systems=["Oracle"],
                size_info="Up to 2GB",
                description="Variable-length character string (deprecated)",
                deprecated=True,
                storage_requirements="Up to 2GB"
            ),

            # Legacy SQL Server Types
            DataTypeInfo(
                name="TEXT",
                category=DataTypeCategory.STRING,
                database_systems=["SQL Server"],
                description="Variable-length text (deprecated)",
                deprecated=True,
                storage_requirements="Variable"
            ),

            # Legacy MySQL Types
            DataTypeInfo(
                name="DATETIME",
                category=DataTypeCategory.DATE_TIME,
                database_systems=["MySQL", "SQL Server"],
                size_info="8 bytes",
                description="Date and time value",
                examples=["'2023-12-25 14:30:00'"],
                storage_requirements="8 bytes"
            ),

            # Ancient Database Types
            DataTypeInfo(
                name="MEMO",
                category=DataTypeCategory.STRING,
                database_systems=["Access", "dBASE"],
                description="Memo field for long text",
                deprecated=True,
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="CURRENCY",
                category=DataTypeCategory.MONETARY,
                database_systems=["Access"],
                size_info="8 bytes",
                description="Currency data type",
                examples=["$12.34", "$1,000.00"],
                storage_requirements="8 bytes"
            ),

            DataTypeInfo(
                name="AUTONUMBER",
                category=DataTypeCategory.NUMERIC,
                database_systems=["Access"],
                size_info="4 bytes",
                description="Auto-incrementing number",
                storage_requirements="4 bytes"
            ),

            DataTypeInfo(
                name="OLEOBJECT",
                category=DataTypeCategory.BINARY,
                database_systems=["Access"],
                description="OLE object storage",
                deprecated=True,
                storage_requirements="Up to 1GB"
            ),

            # Legacy IBM DB2 Types
            DataTypeInfo(
                name="GRAPHIC",
                category=DataTypeCategory.STRING,
                database_systems=["DB2"],
                description="Fixed-length graphic string",
                storage_requirements="2 * length bytes"
            ),

            DataTypeInfo(
                name="VARGRAPHIC",
                category=DataTypeCategory.STRING,
                database_systems=["DB2"],
                description="Variable-length graphic string",
                storage_requirements="2 * length + 2 bytes"
            ),

            DataTypeInfo(
                name="DBCLOB",
                category=DataTypeCategory.STRING,
                database_systems=["DB2"],
                description="Double-byte character large object",
                storage_requirements="Variable"
            )
        ]

        for data_type in legacy_types:
            self.data_types[data_type.name] = data_type

    def _initialize_modern_types(self):
        """Initialize modern and emerging data types."""
        modern_types = [
            # Modern JSON Types
            DataTypeInfo(
                name="JSONB",
                category=DataTypeCategory.JSON_XML,
                database_systems=["PostgreSQL"],
                description="Binary JSON with indexing support",
                examples=["'{\"name\": \"John\", \"age\": 30}'", "'[1, 2, 3]'"],
                storage_requirements="Variable, compressed binary format"
            ),

            # Graph Database Types
            DataTypeInfo(
                name="GRAPH_NODE",
                category=DataTypeCategory.CUSTOM,
                database_systems=["Custom"],
                description="Graph database node",
                examples=["'(person:Person {name: \"John\", age: 30})'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="GRAPH_EDGE",
                category=DataTypeCategory.CUSTOM,
                database_systems=["Custom"],
                description="Graph database relationship",
                examples=["'[:KNOWS {since: 2020}]'", "'[:WORKS_FOR]'"],
                storage_requirements="Variable"
            ),

            # Time Series Types
            DataTypeInfo(
                name="TIMESERIES",
                category=DataTypeCategory.CUSTOM,
                database_systems=["Custom"],
                description="Time series data structure",
                examples=["'{timestamps: [...], values: [...]}'"],
                storage_requirements="Variable"
            ),

            # Blockchain Types
            DataTypeInfo(
                name="HASH256",
                category=DataTypeCategory.CRYPTOGRAPHIC,
                database_systems=["Custom"],
                size_info="32 bytes",
                description="256-bit cryptographic hash",
                examples=["'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'"],
                storage_requirements="32 bytes"
            ),

            DataTypeInfo(
                name="MERKLE_ROOT",
                category=DataTypeCategory.CRYPTOGRAPHIC,
                database_systems=["Custom"],
                size_info="32 bytes",
                description="Merkle tree root hash",
                examples=["'4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'"],
                storage_requirements="32 bytes"
            ),

            # IoT and Sensor Types
            DataTypeInfo(
                name="SENSOR_READING",
                category=DataTypeCategory.CUSTOM,
                database_systems=["Custom"],
                description="IoT sensor reading with metadata",
                examples=["'{value: 23.5, unit: \"°C\", accuracy: 0.1, timestamp: \"2023-12-25T14:30:00Z\"}'"],
                storage_requirements="Variable"
            ),

            # Multimedia Types
            DataTypeInfo(
                name="IMAGE_METADATA",
                category=DataTypeCategory.MULTIMEDIA,
                database_systems=["Custom"],
                description="Image metadata and features",
                examples=["'{width: 1920, height: 1080, format: \"JPEG\", features: [...]}'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="AUDIO_FEATURES",
                category=DataTypeCategory.MULTIMEDIA,
                database_systems=["Custom"],
                description="Audio feature vectors",
                examples=["'{mfcc: [...], spectral_centroid: 1500.5, tempo: 120}'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="VIDEO_METADATA",
                category=DataTypeCategory.MULTIMEDIA,
                database_systems=["Custom"],
                description="Video metadata and analysis",
                examples=["'{duration: 3600, fps: 30, resolution: \"1920x1080\", scenes: [...]}'"],
                storage_requirements="Variable"
            ),

            # Cloud and Distributed Types
            DataTypeInfo(
                name="CLOUD_RESOURCE_ID",
                category=DataTypeCategory.CUSTOM,
                database_systems=["Custom"],
                description="Cloud resource identifier",
                examples=["'arn:aws:s3:::bucket/object'", "'projects/my-project/instances/my-instance'"],
                storage_requirements="Variable"
            ),

            # Quantum Computing Types
            DataTypeInfo(
                name="QUBIT_STATE",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Quantum bit state representation",
                examples=["'|0⟩'", "'|1⟩'", "'α|0⟩ + β|1⟩'"],
                storage_requirements="Variable"
            ),

            DataTypeInfo(
                name="QUANTUM_CIRCUIT",
                category=DataTypeCategory.SCIENTIFIC,
                database_systems=["Custom"],
                description="Quantum circuit description",
                examples=["'{gates: [{type: \"H\", qubit: 0}, {type: \"CNOT\", control: 0, target: 1}]}'"],
                storage_requirements="Variable"
            )
        ]

        for data_type in modern_types:
            self.data_types[data_type.name] = data_type

    def _build_indexes(self):
        """Build indexes for efficient data type lookup."""
        # Clear existing indexes
        self.category_index.clear()
        self.database_index.clear()
        self.alias_index.clear()

        # Build indexes
        for type_name, type_info in self.data_types.items():
            # Category index
            self.category_index[type_info.category].append(type_name)

            # Database index
            for db_system in type_info.database_systems:
                self.database_index[db_system].append(type_name)

            # Alias index
            for alias in type_info.aliases:
                self.alias_index[alias.upper()] = type_name

            # Also index the main name
            self.alias_index[type_name.upper()] = type_name

    # Comprehensive Data Type Methods
    def get_data_type(self, type_name: str) -> Optional[DataTypeInfo]:
        """Get data type information by name or alias."""
        # Try exact match first
        if type_name in self.data_types:
            return self.data_types[type_name]

        # Try case-insensitive lookup
        upper_name = type_name.upper()
        if upper_name in self.alias_index:
            canonical_name = self.alias_index[upper_name]
            return self.data_types[canonical_name]

        return None

    def get_types_by_category(self, category: DataTypeCategory) -> List[DataTypeInfo]:
        """Get all data types in a specific category."""
        type_names = self.category_index.get(category, [])
        return [self.data_types[name] for name in type_names]

    def get_types_by_database(self, database_system: str) -> List[DataTypeInfo]:
        """Get all data types supported by a specific database system."""
        type_names = self.database_index.get(database_system, [])
        return [self.data_types[name] for name in type_names]

    def find_compatible_types(self, source_type: str, target_database: str) -> List[DataTypeInfo]:
        """Find compatible data types for conversion between databases."""
        source_info = self.get_data_type(source_type)
        if not source_info:
            return []

        # Get all types for target database
        target_types = self.get_types_by_database(target_database)

        # Find compatible types (same category or explicit conversion rules)
        compatible = []
        for target_type in target_types:
            if (target_type.category == source_info.category or
                target_database in source_info.conversion_rules):
                compatible.append(target_type)

        return compatible

    def suggest_data_type(self, value_examples: List[str],
                         target_database: str = None) -> List[Tuple[DataTypeInfo, float]]:
        """Suggest appropriate data types based on value examples."""
        suggestions = []

        for type_info in self.data_types.values():
            if target_database and target_database not in type_info.database_systems:
                continue

            confidence = self._calculate_type_confidence(value_examples, type_info)
            if confidence > 0:
                suggestions.append((type_info, confidence))

        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:10]  # Return top 10 suggestions

    def _calculate_type_confidence(self, value_examples: List[str],
                                  type_info: DataTypeInfo) -> float:
        """Calculate confidence score for a data type based on value examples."""
        if not value_examples:
            return 0.0

        matches = 0
        total = len(value_examples)

        for value in value_examples:
            if self._value_matches_type(value, type_info):
                matches += 1

        return matches / total

    def _value_matches_type(self, value: str, type_info: DataTypeInfo) -> bool:
        """Check if a value matches a specific data type."""
        if not value or value.upper() == 'NULL':
            return True  # NULL can be any type

        # Remove quotes if present
        clean_value = value.strip("'\"")

        # Category-specific validation
        if type_info.category == DataTypeCategory.NUMERIC:
            return self._is_numeric(clean_value)
        elif type_info.category == DataTypeCategory.BOOLEAN:
            return clean_value.upper() in ['TRUE', 'FALSE', '1', '0', 'YES', 'NO']
        elif type_info.category == DataTypeCategory.DATE_TIME:
            return self._is_datetime(clean_value)
        elif type_info.category == DataTypeCategory.UUID:
            return self._is_uuid(clean_value)
        elif type_info.category == DataTypeCategory.JSON_XML:
            return self._is_json_or_xml(clean_value)
        elif type_info.category == DataTypeCategory.NETWORK:
            return self._is_network_address(clean_value)

        # Use validation pattern if available
        if type_info.validation_pattern:
            try:
                return bool(re.match(type_info.validation_pattern, clean_value))
            except re.error:
                pass

        # Default: assume string types can hold any value
        return type_info.category == DataTypeCategory.STRING

    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _is_datetime(self, value: str) -> bool:
        """Check if value looks like a date/time."""
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{2}:\d{2}:\d{2}',  # HH:MM:SS
            r'\d{4}',  # YYYY (year only)
        ]

        return any(re.match(pattern, value) for pattern in datetime_patterns)

    def _is_uuid(self, value: str) -> bool:
        """Check if value looks like a UUID."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, value, re.IGNORECASE))

    def _is_json_or_xml(self, value: str) -> bool:
        """Check if value looks like JSON or XML."""
        # JSON check
        if (value.startswith('{') and value.endswith('}')) or \
           (value.startswith('[') and value.endswith(']')):
            try:
                json.loads(value)
                return True
            except json.JSONDecodeError:
                pass

        # XML check
        if value.startswith('<') and value.endswith('>'):
            return True

        return False

    def _is_network_address(self, value: str) -> bool:
        """Check if value looks like a network address."""
        # IPv4 pattern
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ipv4_pattern, value):
            return True

        # IPv6 pattern (simplified)
        if ':' in value and len(value.split(':')) >= 3:
            return True

        # MAC address pattern
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if re.match(mac_pattern, value):
            return True

        return False

    def get_conversion_path(self, source_type: str, target_type: str) -> Optional[List[str]]:
        """Get conversion path between two data types."""
        source_info = self.get_data_type(source_type)
        target_info = self.get_data_type(target_type)

        if not source_info or not target_info:
            return None

        # Direct conversion
        if target_type in source_info.conversion_rules:
            return [source_type, target_type]

        # Same category conversion
        if source_info.category == target_info.category:
            return [source_type, target_type]

        # Multi-step conversion (simplified)
        # In a real implementation, this would use graph algorithms
        intermediate_types = []

        # Try to find common category
        for type_name, type_info in self.data_types.items():
            if (type_info.category == source_info.category and
                target_type in type_info.conversion_rules):
                intermediate_types.append(type_name)

        if intermediate_types:
            return [source_type, intermediate_types[0], target_type]

        return None

    def validate_data_type_usage(self, type_name: str,
                                database_system: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate data type usage in a specific context."""
        type_info = self.get_data_type(type_name)

        result = {
            'valid': False,
            'warnings': [],
            'suggestions': [],
            'compatibility_notes': []
        }

        if not type_info:
            result['warnings'].append(f"Unknown data type: {type_name}")
            return result

        # Check database compatibility
        if database_system not in type_info.database_systems:
            result['warnings'].append(f"{type_name} is not supported in {database_system}")

            # Suggest alternatives
            compatible_types = self.find_compatible_types(type_name, database_system)
            if compatible_types:
                suggestions = [t.name for t in compatible_types[:3]]
                result['suggestions'].extend(suggestions)
        else:
            result['valid'] = True

        # Check for deprecation
        if type_info.deprecated:
            result['warnings'].append(f"{type_name} is deprecated")

            # Suggest modern alternatives
            modern_alternatives = self.get_types_by_category(type_info.category)
            non_deprecated = [t for t in modern_alternatives if not t.deprecated]
            if non_deprecated:
                result['suggestions'].extend([t.name for t in non_deprecated[:2]])

        # Add compatibility notes
        if database_system in type_info.compatibility_notes:
            result['compatibility_notes'].append(type_info.compatibility_notes[database_system])

        # Context-specific validation
        if context:
            self._validate_context_specific(type_info, context, result)

        return result

    def _validate_context_specific(self, type_info: DataTypeInfo,
                                  context: Dict[str, Any],
                                  result: Dict[str, Any]):
        """Perform context-specific validation."""
        # Check size constraints
        if 'max_length' in context and type_info.size_info:
            try:
                # Extract numeric size from size_info
                size_match = re.search(r'(\d+)', type_info.size_info)
                if size_match:
                    type_size = int(size_match.group(1))
                    if context['max_length'] > type_size:
                        result['warnings'].append(f"Specified length exceeds type maximum: {type_size}")
            except (ValueError, AttributeError):
                pass

        # Check precision/scale for numeric types
        if (type_info.category == DataTypeCategory.NUMERIC and
            'precision' in context and type_info.precision_scale):
            max_precision, max_scale = type_info.precision_scale
            if context['precision'] > max_precision:
                result['warnings'].append(f"Precision exceeds maximum: {max_precision}")
            if context.get('scale', 0) > max_scale:
                result['warnings'].append(f"Scale exceeds maximum: {max_scale}")

    def get_all_categories(self) -> List[DataTypeCategory]:
        """Get all available data type categories."""
        return list(self.category_index.keys())

    def get_all_databases(self) -> List[str]:
        """Get all supported database systems."""
        return list(self.database_index.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the data type registry."""
        return {
            'total_types': len(self.data_types),
            'categories': len(self.category_index),
            'databases': len(self.database_index),
            'aliases': len(self.alias_index),
            'deprecated_types': sum(1 for t in self.data_types.values() if t.deprecated),
            'types_by_category': {cat.value: len(types) for cat, types in self.category_index.items()},
            'types_by_database': {db: len(types) for db, types in self.database_index.items()}
        }


# Global instance of the data type registry
DATA_TYPE_REGISTRY = UniversalDataTypeRegistry()
