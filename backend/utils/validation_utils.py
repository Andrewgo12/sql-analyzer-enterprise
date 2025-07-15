"""
Validation Utilities for SQL Analyzer

Common validation functions and data integrity checks.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path
import json
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationUtils:
    """Utility class for validation operations."""
    
    # Common validation patterns
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?1?-?\.?\s?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})$',
        'url': r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$',
        'ipv4': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        'ipv6': r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        'sql_identifier': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
        'table_name': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
        'column_name': r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    }
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """
        Validate file path.
        
        Args:
            file_path: File path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, f"File does not exist: {file_path}"
            
            if not path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            if not os.access(file_path, os.R_OK):
                return False, f"File is not readable: {file_path}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid file path: {str(e)}"
    
    @staticmethod
    def validate_directory_path(dir_path: str) -> Tuple[bool, str]:
        """
        Validate directory path.
        
        Args:
            dir_path: Directory path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(dir_path)
            
            if not path.exists():
                return False, f"Directory does not exist: {dir_path}"
            
            if not path.is_dir():
                return False, f"Path is not a directory: {dir_path}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid directory path: {str(e)}"
    
    @staticmethod
    def validate_sql_identifier(identifier: str) -> Tuple[bool, str]:
        """
        Validate SQL identifier (table name, column name, etc.).
        
        Args:
            identifier: Identifier to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not identifier:
            return False, "Identifier cannot be empty"
        
        if not re.match(ValidationUtils.PATTERNS['sql_identifier'], identifier):
            return False, f"Invalid SQL identifier: {identifier}"
        
        # Check length (most databases have limits)
        if len(identifier) > 64:
            return False, f"Identifier too long (max 64 characters): {identifier}"
        
        # Check for reserved keywords (basic check)
        reserved_keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'PRIMARY', 'KEY',
            'FOREIGN', 'REFERENCES', 'CONSTRAINT', 'UNIQUE', 'NOT', 'NULL', 'DEFAULT',
            'AUTO_INCREMENT', 'TIMESTAMP', 'CURRENT_TIMESTAMP'
        }
        
        if identifier.upper() in reserved_keywords:
            return False, f"Identifier is a reserved keyword: {identifier}"
        
        return True, ""
    
    @staticmethod
    def validate_data_type(data_type: str, database_type: str = 'mysql') -> Tuple[bool, str]:
        """
        Validate SQL data type.
        
        Args:
            data_type: Data type to validate
            database_type: Target database type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data_type:
            return False, "Data type cannot be empty"
        
        # Common data types by database
        valid_types = {
            'mysql': {
                'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT', 'MEDIUMINT',
                'VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT', 'TINYTEXT',
                'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL',
                'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR',
                'BOOLEAN', 'BOOL', 'BIT',
                'BINARY', 'VARBINARY', 'BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB',
                'JSON', 'ENUM', 'SET'
            },
            'postgresql': {
                'INTEGER', 'BIGINT', 'SMALLINT', 'SERIAL', 'BIGSERIAL',
                'VARCHAR', 'CHAR', 'TEXT',
                'DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE PRECISION',
                'DATE', 'TIME', 'TIMESTAMP', 'TIMESTAMPTZ', 'INTERVAL',
                'BOOLEAN', 'BIT', 'VARBIT',
                'BYTEA', 'UUID', 'JSON', 'JSONB', 'XML',
                'POINT', 'LINE', 'LSEG', 'BOX', 'PATH', 'POLYGON', 'CIRCLE'
            },
            'sqlite': {
                'INTEGER', 'REAL', 'TEXT', 'BLOB', 'NUMERIC'
            },
            'sqlserver': {
                'INT', 'BIGINT', 'SMALLINT', 'TINYINT',
                'VARCHAR', 'NVARCHAR', 'CHAR', 'NCHAR', 'TEXT', 'NTEXT',
                'DECIMAL', 'NUMERIC', 'FLOAT', 'REAL', 'MONEY', 'SMALLMONEY',
                'DATE', 'TIME', 'DATETIME', 'DATETIME2', 'SMALLDATETIME', 'DATETIMEOFFSET',
                'BIT', 'BINARY', 'VARBINARY', 'IMAGE',
                'UNIQUEIDENTIFIER', 'XML', 'GEOGRAPHY', 'GEOMETRY'
            }
        }
        
        # Extract base type (remove size specifications)
        base_type = re.sub(r'\([^)]*\)', '', data_type.upper()).strip()
        
        db_types = valid_types.get(database_type.lower(), valid_types['mysql'])
        
        if base_type not in db_types:
            return False, f"Invalid data type '{data_type}' for {database_type}"
        
        return True, ""
    
    @staticmethod
    def validate_json_structure(json_data: Union[str, Dict], required_keys: List[str] = None) -> Tuple[bool, str]:
        """
        Validate JSON structure.
        
        Args:
            json_data: JSON data to validate (string or dict)
            required_keys: List of required keys
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            if not isinstance(data, dict):
                return False, "JSON data must be an object"
            
            if required_keys:
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    return False, f"Missing required keys: {', '.join(missing_keys)}"
            
            return True, ""
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"JSON validation error: {str(e)}"
    
    @staticmethod
    def validate_yaml_structure(yaml_data: Union[str, Dict], required_keys: List[str] = None) -> Tuple[bool, str]:
        """
        Validate YAML structure.
        
        Args:
            yaml_data: YAML data to validate (string or dict)
            required_keys: List of required keys
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if isinstance(yaml_data, str):
                data = yaml.safe_load(yaml_data)
            else:
                data = yaml_data
            
            if not isinstance(data, dict):
                return False, "YAML data must be a mapping"
            
            if required_keys:
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    return False, f"Missing required keys: {', '.join(missing_keys)}"
            
            return True, ""
            
        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {str(e)}"
        except Exception as e:
            return False, f"YAML validation error: {str(e)}"
    
    @staticmethod
    def validate_pattern(value: str, pattern_name: str) -> Tuple[bool, str]:
        """
        Validate value against a predefined pattern.
        
        Args:
            value: Value to validate
            pattern_name: Name of the pattern to use
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pattern_name not in ValidationUtils.PATTERNS:
            return False, f"Unknown pattern: {pattern_name}"
        
        pattern = ValidationUtils.PATTERNS[pattern_name]
        
        if not re.match(pattern, value):
            return False, f"Value does not match {pattern_name} pattern: {value}"
        
        return True, ""
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 100) -> Tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum size in MB
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_size = Path(file_path).stat().st_size
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                actual_mb = file_size / (1024 * 1024)
                return False, f"File too large: {actual_mb:.2f}MB (max: {max_size_mb}MB)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error checking file size: {str(e)}"
    
    @staticmethod
    def validate_encoding(file_path: str, allowed_encodings: List[str] = None) -> Tuple[bool, str]:
        """
        Validate file encoding.
        
        Args:
            file_path: Path to file
            allowed_encodings: List of allowed encodings
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if allowed_encodings is None:
            allowed_encodings = ['utf-8', 'ascii', 'latin-1', 'cp1252']
        
        try:
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Sample first 10KB
                result = chardet.detect(raw_data)
            
            detected_encoding = result.get('encoding', '').lower()
            confidence = result.get('confidence', 0.0)
            
            if confidence < 0.7:
                return False, f"Low confidence in encoding detection: {confidence:.2f}"
            
            if detected_encoding not in [enc.lower() for enc in allowed_encodings]:
                return False, f"Unsupported encoding: {detected_encoding}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating encoding: {str(e)}"
    
    @staticmethod
    def validate_sql_statement_structure(sql_statement: str) -> Tuple[bool, List[str]]:
        """
        Validate basic SQL statement structure.
        
        Args:
            sql_statement: SQL statement to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        sql_upper = sql_statement.upper().strip()
        
        if not sql_statement.strip():
            errors.append("SQL statement is empty")
            return False, errors
        
        # Check for basic statement types
        valid_starts = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'GRANT', 'REVOKE']
        if not any(sql_upper.startswith(start) for start in valid_starts):
            errors.append("SQL statement does not start with a valid keyword")
        
        # Check for balanced parentheses
        open_count = sql_statement.count('(')
        close_count = sql_statement.count(')')
        if open_count != close_count:
            errors.append(f"Unbalanced parentheses: {open_count} open, {close_count} close")
        
        # Check for balanced quotes
        single_quotes = sql_statement.count("'")
        if single_quotes % 2 != 0:
            errors.append("Unbalanced single quotes")
        
        double_quotes = sql_statement.count('"')
        if double_quotes % 2 != 0:
            errors.append("Unbalanced double quotes")
        
        # Check for common syntax errors
        if re.search(r',\s*\)', sql_statement):
            errors.append("Trailing comma before closing parenthesis")
        
        if re.search(r'\(\s*,', sql_statement):
            errors.append("Leading comma after opening parenthesis")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_database_connection_params(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate database connection parameters.
        
        Args:
            params: Dictionary of connection parameters
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_params = ['host', 'database']
        
        # Check required parameters
        for param in required_params:
            if param not in params or not params[param]:
                errors.append(f"Missing required parameter: {param}")
        
        # Validate host
        if 'host' in params:
            host = params['host']
            if not (ValidationUtils.validate_pattern(host, 'ipv4')[0] or 
                   ValidationUtils.validate_pattern(host, 'ipv6')[0] or
                   re.match(r'^[a-zA-Z0-9.-]+$', host)):
                errors.append(f"Invalid host format: {host}")
        
        # Validate port
        if 'port' in params:
            try:
                port = int(params['port'])
                if not (1 <= port <= 65535):
                    errors.append(f"Port must be between 1 and 65535: {port}")
            except (ValueError, TypeError):
                errors.append(f"Invalid port format: {params['port']}")
        
        # Validate database name
        if 'database' in params:
            db_name = params['database']
            if not ValidationUtils.validate_sql_identifier(db_name)[0]:
                errors.append(f"Invalid database name: {db_name}")
        
        return len(errors) == 0, errors
