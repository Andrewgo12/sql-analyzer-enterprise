"""
Multi-Database Format Converter

Comprehensive conversion engine supporting MySQL, PostgreSQL, SQLite, 
SQL Server, Oracle, and JSON formats with bidirectional conversion 
capabilities while preserving data integrity.
"""

import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sqlparse
from sqlparse import sql, tokens as T

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types."""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    JSON = "json"


@dataclass
class ConversionResult:
    """Result of database format conversion."""
    source_format: DatabaseType
    target_format: DatabaseType
    original_sql: str
    converted_sql: str = ""
    converted_json: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    conversion_notes: List[str] = field(default_factory=list)
    success: bool = True


class FormatConverter:
    """
    Multi-database format converter with comprehensive support for major database systems.
    
    Features:
    - Convert between MySQL, PostgreSQL, SQLite, SQL Server, Oracle
    - Bidirectional SQL to JSON conversion
    - Data type mapping and compatibility handling
    - Syntax adaptation for different database systems
    - Preservation of data integrity during conversion
    - Detailed conversion reporting and warnings
    """
    
    # Data type mappings between different database systems
    TYPE_MAPPINGS = {
        DatabaseType.MYSQL: {
            'INT': 'INT',
            'INTEGER': 'INT',
            'BIGINT': 'BIGINT',
            'SMALLINT': 'SMALLINT',
            'TINYINT': 'TINYINT',
            'VARCHAR': 'VARCHAR',
            'CHAR': 'CHAR',
            'TEXT': 'TEXT',
            'LONGTEXT': 'LONGTEXT',
            'DECIMAL': 'DECIMAL',
            'FLOAT': 'FLOAT',
            'DOUBLE': 'DOUBLE',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'DATETIME': 'DATETIME',
            'TIMESTAMP': 'TIMESTAMP',
            'BOOLEAN': 'BOOLEAN',
            'BLOB': 'BLOB',
            'JSON': 'JSON'
        },
        DatabaseType.POSTGRESQL: {
            'INT': 'INTEGER',
            'INTEGER': 'INTEGER',
            'BIGINT': 'BIGINT',
            'SMALLINT': 'SMALLINT',
            'TINYINT': 'SMALLINT',  # PostgreSQL doesn't have TINYINT
            'VARCHAR': 'VARCHAR',
            'CHAR': 'CHAR',
            'TEXT': 'TEXT',
            'LONGTEXT': 'TEXT',  # PostgreSQL uses TEXT for all text lengths
            'DECIMAL': 'DECIMAL',
            'FLOAT': 'REAL',
            'DOUBLE': 'DOUBLE PRECISION',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'DATETIME': 'TIMESTAMP',
            'TIMESTAMP': 'TIMESTAMP',
            'BOOLEAN': 'BOOLEAN',
            'BLOB': 'BYTEA',
            'JSON': 'JSON'
        },
        DatabaseType.SQLITE: {
            'INT': 'INTEGER',
            'INTEGER': 'INTEGER',
            'BIGINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'TINYINT': 'INTEGER',
            'VARCHAR': 'TEXT',
            'CHAR': 'TEXT',
            'TEXT': 'TEXT',
            'LONGTEXT': 'TEXT',
            'DECIMAL': 'REAL',
            'FLOAT': 'REAL',
            'DOUBLE': 'REAL',
            'DATE': 'TEXT',  # SQLite stores dates as text
            'TIME': 'TEXT',
            'DATETIME': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'BOOLEAN': 'INTEGER',  # SQLite uses INTEGER for boolean
            'BLOB': 'BLOB',
            'JSON': 'TEXT'  # SQLite stores JSON as text
        },
        DatabaseType.SQLSERVER: {
            'INT': 'INT',
            'INTEGER': 'INT',
            'BIGINT': 'BIGINT',
            'SMALLINT': 'SMALLINT',
            'TINYINT': 'TINYINT',
            'VARCHAR': 'VARCHAR',
            'CHAR': 'CHAR',
            'TEXT': 'TEXT',
            'LONGTEXT': 'TEXT',
            'DECIMAL': 'DECIMAL',
            'FLOAT': 'FLOAT',
            'DOUBLE': 'FLOAT',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'DATETIME': 'DATETIME2',
            'TIMESTAMP': 'DATETIME2',
            'BOOLEAN': 'BIT',
            'BLOB': 'VARBINARY(MAX)',
            'JSON': 'NVARCHAR(MAX)'  # SQL Server 2016+ has JSON support
        },
        DatabaseType.ORACLE: {
            'INT': 'NUMBER(10)',
            'INTEGER': 'NUMBER(10)',
            'BIGINT': 'NUMBER(19)',
            'SMALLINT': 'NUMBER(5)',
            'TINYINT': 'NUMBER(3)',
            'VARCHAR': 'VARCHAR2',
            'CHAR': 'CHAR',
            'TEXT': 'CLOB',
            'LONGTEXT': 'CLOB',
            'DECIMAL': 'NUMBER',
            'FLOAT': 'BINARY_FLOAT',
            'DOUBLE': 'BINARY_DOUBLE',
            'DATE': 'DATE',
            'TIME': 'TIMESTAMP',
            'DATETIME': 'TIMESTAMP',
            'TIMESTAMP': 'TIMESTAMP',
            'BOOLEAN': 'NUMBER(1)',  # Oracle uses NUMBER(1) for boolean
            'BLOB': 'BLOB',
            'JSON': 'CLOB'  # Oracle 12c+ has JSON support
        }
    }
    
    # Database-specific syntax patterns
    SYNTAX_PATTERNS = {
        DatabaseType.MYSQL: {
            'auto_increment': 'AUTO_INCREMENT',
            'quote_char': '`',
            'limit_syntax': 'LIMIT',
            'string_concat': 'CONCAT',
            'current_timestamp': 'CURRENT_TIMESTAMP',
            'if_not_exists': 'IF NOT EXISTS'
        },
        DatabaseType.POSTGRESQL: {
            'auto_increment': 'SERIAL',
            'quote_char': '"',
            'limit_syntax': 'LIMIT',
            'string_concat': '||',
            'current_timestamp': 'CURRENT_TIMESTAMP',
            'if_not_exists': 'IF NOT EXISTS'
        },
        DatabaseType.SQLITE: {
            'auto_increment': 'AUTOINCREMENT',
            'quote_char': '"',
            'limit_syntax': 'LIMIT',
            'string_concat': '||',
            'current_timestamp': 'CURRENT_TIMESTAMP',
            'if_not_exists': 'IF NOT EXISTS'
        },
        DatabaseType.SQLSERVER: {
            'auto_increment': 'IDENTITY(1,1)',
            'quote_char': '[',
            'limit_syntax': 'TOP',
            'string_concat': '+',
            'current_timestamp': 'GETDATE()',
            'if_not_exists': 'IF NOT EXISTS'
        },
        DatabaseType.ORACLE: {
            'auto_increment': '',  # Oracle uses sequences
            'quote_char': '"',
            'limit_syntax': 'ROWNUM',
            'string_concat': '||',
            'current_timestamp': 'SYSDATE',
            'if_not_exists': ''  # Oracle doesn't support IF NOT EXISTS
        }
    }
    
    def __init__(self):
        """Initialize the format converter."""
        self.conversion_history: List[ConversionResult] = []
    
    def convert(self, results: Dict[str, Any], format_type: str) -> Optional[str]:
        """
        Convert analysis results to specified format for download

        Args:
            results: Analysis results dictionary
            format_type: Target format (json, html, txt, etc.)

        Returns:
            Path to generated file or None if failed
        """
        try:
            import tempfile
            import os

            # Create temporary file
            temp_dir = tempfile.gettempdir()
            filename = f"sql_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = os.path.join(temp_dir, filename)

            if format_type.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            elif format_type.lower() == 'txt':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("ANÁLISIS SQL - REPORTE COMPLETO\n")
                    f.write("=" * 50 + "\n\n")

                    # Basic info
                    f.write(f"Archivo: {results.get('filename', 'N/A')}\n")
                    f.write(f"Fecha: {results.get('timestamp', 'N/A')}\n")
                    f.write(f"Tamaño: {results.get('file_size', 0)} bytes\n")
                    f.write(f"Líneas: {results.get('line_count', 0)}\n\n")

                    # Summary
                    summary = results.get('summary', {})
                    f.write("RESUMEN\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Errores encontrados: {summary.get('total_errors', 0)}\n")
                    f.write(f"Score de rendimiento: {summary.get('performance_score', 100)}\n")
                    f.write(f"Score de seguridad: {summary.get('security_score', 100)}\n\n")

                    # Errors
                    errors = results.get('analysis', {}).get('errors', [])
                    if errors:
                        f.write("ERRORES DETECTADOS\n")
                        f.write("-" * 20 + "\n")
                        for i, error in enumerate(errors, 1):
                            f.write(f"{i}. Línea {error.get('line', 'N/A')}: {error.get('message', 'N/A')}\n")
                        f.write("\n")

                    # Recommendations
                    recommendations = summary.get('recommendations', [])
                    if recommendations:
                        f.write("RECOMENDACIONES\n")
                        f.write("-" * 20 + "\n")
                        for i, rec in enumerate(recommendations, 1):
                            f.write(f"{i}. {rec.get('message', 'N/A')}\n")

            elif format_type.lower() == 'html':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._generate_html_report(results))

            else:
                # Default to JSON for unsupported formats
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            return file_path

        except Exception as e:
            logger.error(f"Error converting to {format_type}: {e}")
            return None

    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML report from analysis results"""
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Análisis SQL - Reporte</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .success {{ color: #28a745; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Análisis SQL - Reporte Completo</h1>
                <p><strong>Archivo:</strong> {results.get('filename', 'N/A')}</p>
                <p><strong>Fecha:</strong> {results.get('timestamp', 'N/A')}</p>
                <p><strong>Tamaño:</strong> {results.get('file_size', 0)} bytes</p>
                <p><strong>Líneas:</strong> {results.get('line_count', 0)}</p>
            </div>

            <div class="section">
                <h2>Resumen</h2>
                <table>
                    <tr><th>Métrica</th><th>Valor</th></tr>
                    <tr><td>Errores encontrados</td><td class="error">{results.get('summary', {}).get('total_errors', 0)}</td></tr>
                    <tr><td>Score de rendimiento</td><td>{results.get('summary', {}).get('performance_score', 100)}</td></tr>
                    <tr><td>Score de seguridad</td><td>{results.get('summary', {}).get('security_score', 100)}</td></tr>
                </table>
            </div>
        """

        # Add errors section
        errors = results.get('analysis', {}).get('errors', [])
        if errors:
            html += """
            <div class="section">
                <h2>Errores Detectados</h2>
                <table>
                    <tr><th>Línea</th><th>Mensaje</th><th>Severidad</th></tr>
            """
            for error in errors:
                html += f"""
                    <tr>
                        <td>{error.get('line', 'N/A')}</td>
                        <td>{error.get('message', 'N/A')}</td>
                        <td class="error">{error.get('severity', 'N/A')}</td>
                    </tr>
                """
            html += "</table></div>"

        # Add recommendations
        recommendations = results.get('summary', {}).get('recommendations', [])
        if recommendations:
            html += """
            <div class="section">
                <h2>Recomendaciones</h2>
                <ul>
            """
            for rec in recommendations:
                html += f"<li>{rec.get('message', 'N/A')}</li>"
            html += "</ul></div>"

        html += """
        </body>
        </html>
        """

        return html

    def convert_database_format(self, sql_content: str, source_format: DatabaseType,
                target_format: DatabaseType) -> ConversionResult:
        """
        Convert SQL from one database format to another.
        
        Args:
            sql_content: SQL content to convert
            source_format: Source database format
            target_format: Target database format
            
        Returns:
            ConversionResult with converted SQL and metadata
        """
        logger.info(f"Converting from {source_format.value} to {target_format.value}")
        
        result = ConversionResult(
            source_format=source_format,
            target_format=target_format,
            original_sql=sql_content
        )
        
        try:
            if target_format == DatabaseType.JSON:
                # Convert SQL to JSON
                result.converted_json = self._sql_to_json(sql_content, source_format)
                result.converted_sql = json.dumps(result.converted_json, indent=2)
            elif source_format == DatabaseType.JSON:
                # Convert JSON to SQL
                json_data = json.loads(sql_content)
                result.converted_sql = self._json_to_sql(json_data, target_format)
            else:
                # Convert between SQL formats
                result.converted_sql = self._convert_sql_format(
                    sql_content, source_format, target_format, result
                )
            
            self.conversion_history.append(result)
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Conversion failed: {str(e)}")
            logger.error(f"Conversion error: {e}")
        
        return result
    
    def _convert_sql_format(self, sql_content: str, source_format: DatabaseType,
                           target_format: DatabaseType, result: ConversionResult) -> str:
        """Convert SQL between different database formats."""
        converted_sql = sql_content
        
        # Parse SQL statements
        statements = sqlparse.split(sql_content)
        converted_statements = []
        
        for statement in statements:
            if statement.strip():
                converted_stmt = self._convert_statement(
                    statement, source_format, target_format, result
                )
                converted_statements.append(converted_stmt)
        
        return '\n\n'.join(converted_statements)
    
    def _convert_statement(self, statement: str, source_format: DatabaseType,
                          target_format: DatabaseType, result: ConversionResult) -> str:
        """Convert a single SQL statement."""
        converted = statement
        
        # Convert data types
        converted = self._convert_data_types(converted, source_format, target_format, result)
        
        # Convert syntax patterns
        converted = self._convert_syntax(converted, source_format, target_format, result)
        
        # Convert auto-increment
        converted = self._convert_auto_increment(converted, source_format, target_format, result)
        
        # Convert quotes
        converted = self._convert_quotes(converted, source_format, target_format)
        
        # Convert functions
        converted = self._convert_functions(converted, source_format, target_format, result)
        
        return converted

    def _convert_data_types(self, statement: str, source_format: DatabaseType,
                           target_format: DatabaseType, result: ConversionResult) -> str:
        """Convert data types between database formats."""
        if source_format == target_format:
            return statement

        source_types = self.TYPE_MAPPINGS.get(source_format, {})
        target_types = self.TYPE_MAPPINGS.get(target_format, {})

        converted = statement

        # Find and replace data types
        for source_type, target_type in target_types.items():
            if source_type in source_types:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(source_type) + r'\b'
                if re.search(pattern, converted, re.IGNORECASE):
                    converted = re.sub(pattern, target_type, converted, flags=re.IGNORECASE)
                    result.conversion_notes.append(f"Converted {source_type} to {target_type}")

        return converted

    def _convert_syntax(self, statement: str, source_format: DatabaseType,
                       target_format: DatabaseType, result: ConversionResult) -> str:
        """Convert database-specific syntax."""
        if source_format == target_format:
            return statement

        converted = statement

        # Convert LIMIT syntax
        if target_format == DatabaseType.SQLSERVER:
            # Convert LIMIT to TOP
            limit_match = re.search(r'LIMIT\s+(\d+)', converted, re.IGNORECASE)
            if limit_match:
                limit_value = limit_match.group(1)
                # Move TOP to after SELECT
                converted = re.sub(r'SELECT\s+', f'SELECT TOP {limit_value} ', converted, flags=re.IGNORECASE)
                converted = re.sub(r'LIMIT\s+\d+', '', converted, flags=re.IGNORECASE)
                result.conversion_notes.append(f"Converted LIMIT {limit_value} to TOP {limit_value}")

        elif source_format == DatabaseType.SQLSERVER and 'TOP' in converted.upper():
            # Convert TOP to LIMIT
            top_match = re.search(r'SELECT\s+TOP\s+(\d+)', converted, re.IGNORECASE)
            if top_match:
                top_value = top_match.group(1)
                converted = re.sub(r'SELECT\s+TOP\s+\d+\s+', 'SELECT ', converted, flags=re.IGNORECASE)
                converted += f' LIMIT {top_value}'
                result.conversion_notes.append(f"Converted TOP {top_value} to LIMIT {top_value}")

        return converted

    def _convert_auto_increment(self, statement: str, source_format: DatabaseType,
                               target_format: DatabaseType, result: ConversionResult) -> str:
        """Convert auto-increment syntax."""
        if source_format == target_format:
            return statement

        source_syntax = self.SYNTAX_PATTERNS.get(source_format, {})
        target_syntax = self.SYNTAX_PATTERNS.get(target_format, {})

        source_auto_inc = source_syntax.get('auto_increment', '')
        target_auto_inc = target_syntax.get('auto_increment', '')

        converted = statement

        if source_auto_inc and target_auto_inc and source_auto_inc != target_auto_inc:
            if source_auto_inc in converted:
                converted = converted.replace(source_auto_inc, target_auto_inc)
                result.conversion_notes.append(f"Converted {source_auto_inc} to {target_auto_inc}")

        # Special handling for PostgreSQL SERIAL
        if target_format == DatabaseType.POSTGRESQL:
            # Convert INT AUTO_INCREMENT to SERIAL
            converted = re.sub(r'INT\s+AUTO_INCREMENT', 'SERIAL', converted, flags=re.IGNORECASE)
            converted = re.sub(r'INTEGER\s+AUTO_INCREMENT', 'SERIAL', converted, flags=re.IGNORECASE)

        elif source_format == DatabaseType.POSTGRESQL and target_format != DatabaseType.POSTGRESQL:
            # Convert SERIAL back to INT AUTO_INCREMENT (for MySQL) or appropriate equivalent
            if target_format == DatabaseType.MYSQL:
                converted = re.sub(r'\bSERIAL\b', 'INT AUTO_INCREMENT', converted, flags=re.IGNORECASE)
            elif target_format == DatabaseType.SQLSERVER:
                converted = re.sub(r'\bSERIAL\b', 'INT IDENTITY(1,1)', converted, flags=re.IGNORECASE)

        return converted

    def _convert_quotes(self, statement: str, source_format: DatabaseType,
                       target_format: DatabaseType) -> str:
        """Convert identifier quotes between database formats."""
        if source_format == target_format:
            return statement

        source_quote = self.SYNTAX_PATTERNS.get(source_format, {}).get('quote_char', '"')
        target_quote = self.SYNTAX_PATTERNS.get(target_format, {}).get('quote_char', '"')

        if source_quote != target_quote:
            # Handle SQL Server's bracket notation
            if source_format == DatabaseType.SQLSERVER:
                # Convert [identifier] to target quote style
                statement = re.sub(r'\[([^\]]+)\]', f'{target_quote}\\1{target_quote}', statement)
            elif target_format == DatabaseType.SQLSERVER:
                # Convert quotes to brackets
                statement = re.sub(f'{re.escape(source_quote)}([^{re.escape(source_quote)}]+){re.escape(source_quote)}',
                                 r'[\1]', statement)
            else:
                # Simple quote replacement
                statement = statement.replace(source_quote, target_quote)

        return statement

    def _convert_functions(self, statement: str, source_format: DatabaseType,
                          target_format: DatabaseType, result: ConversionResult) -> str:
        """Convert database-specific functions."""
        if source_format == target_format:
            return statement

        converted = statement

        # Convert string concatenation
        if source_format == DatabaseType.MYSQL and target_format in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
            # Convert CONCAT() to ||
            concat_pattern = r'CONCAT\s*\(([^)]+)\)'
            matches = re.finditer(concat_pattern, converted, re.IGNORECASE)
            for match in matches:
                args = match.group(1).split(',')
                concat_expr = ' || '.join(arg.strip() for arg in args)
                converted = converted.replace(match.group(0), f'({concat_expr})')
                result.conversion_notes.append("Converted CONCAT() to || operator")

        elif source_format in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE] and target_format == DatabaseType.MYSQL:
            # Convert || to CONCAT()
            # This is more complex as we need to identify || used for concatenation vs other uses
            # Simple pattern for basic cases
            concat_pattern = r'(\w+)\s*\|\|\s*(\w+)'
            converted = re.sub(concat_pattern, r'CONCAT(\1, \2)', converted)

        # Convert current timestamp functions
        source_ts = self.SYNTAX_PATTERNS.get(source_format, {}).get('current_timestamp', 'CURRENT_TIMESTAMP')
        target_ts = self.SYNTAX_PATTERNS.get(target_format, {}).get('current_timestamp', 'CURRENT_TIMESTAMP')

        if source_ts != target_ts and source_ts in converted:
            converted = converted.replace(source_ts, target_ts)
            result.conversion_notes.append(f"Converted {source_ts} to {target_ts}")

        return converted

    def _sql_to_json(self, sql_content: str, source_format: DatabaseType) -> Dict[str, Any]:
        """Convert SQL to JSON representation."""
        json_schema = {
            "database_type": source_format.value,
            "tables": [],
            "indexes": [],
            "views": [],
            "procedures": [],
            "metadata": {
                "conversion_timestamp": "",
                "source_format": source_format.value
            }
        }

        # Parse SQL statements
        statements = sqlparse.split(sql_content)

        for statement in statements:
            if statement.strip():
                parsed = sqlparse.parse(statement)[0]
                stmt_type = self._get_statement_type(parsed)

                if stmt_type == "CREATE_TABLE":
                    table_info = self._parse_create_table_to_json(statement)
                    if table_info:
                        json_schema["tables"].append(table_info)
                elif stmt_type == "CREATE_INDEX":
                    index_info = self._parse_create_index_to_json(statement)
                    if index_info:
                        json_schema["indexes"].append(index_info)
                elif stmt_type == "CREATE_VIEW":
                    view_info = self._parse_create_view_to_json(statement)
                    if view_info:
                        json_schema["views"].append(view_info)

        return json_schema

    def _json_to_sql(self, json_data: Dict[str, Any], target_format: DatabaseType) -> str:
        """Convert JSON representation to SQL."""
        sql_statements = []

        # Add database creation if specified
        if "database_name" in json_data:
            if target_format == DatabaseType.MYSQL:
                sql_statements.append(f"CREATE DATABASE IF NOT EXISTS {json_data['database_name']};")
                sql_statements.append(f"USE {json_data['database_name']};")
            elif target_format == DatabaseType.POSTGRESQL:
                sql_statements.append(f"CREATE DATABASE {json_data['database_name']};")

        # Convert tables
        if "tables" in json_data:
            for table in json_data["tables"]:
                table_sql = self._json_table_to_sql(table, target_format)
                if table_sql:
                    sql_statements.append(table_sql)

        # Convert indexes
        if "indexes" in json_data:
            for index in json_data["indexes"]:
                index_sql = self._json_index_to_sql(index, target_format)
                if index_sql:
                    sql_statements.append(index_sql)

        # Convert views
        if "views" in json_data:
            for view in json_data["views"]:
                view_sql = self._json_view_to_sql(view, target_format)
                if view_sql:
                    sql_statements.append(view_sql)

        return '\n\n'.join(sql_statements)

    def _get_statement_type(self, parsed) -> str:
        """Get the type of SQL statement."""
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
                return "CREATE_TABLE"
            elif second_token == 'INDEX':
                return "CREATE_INDEX"
            elif second_token == 'VIEW':
                return "CREATE_VIEW"

        return "UNKNOWN"

    def _parse_create_table_to_json(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE TABLE statement to JSON representation."""
        try:
            parsed = sqlparse.parse(statement)[0]
            tokens = list(parsed.flatten())

            # Find table name
            table_name = None
            create_found = False
            table_found = False

            for token in tokens:
                if token.ttype is T.Keyword and token.value.upper() == 'CREATE':
                    create_found = True
                elif create_found and token.ttype is T.Keyword and token.value.upper() == 'TABLE':
                    table_found = True
                elif table_found and token.ttype is T.Name:
                    table_name = token.value
                    break

            if not table_name:
                return None

            # Extract column definitions (simplified)
            columns = []
            in_parentheses = False
            current_column = ""

            for token in tokens:
                if token.value == '(':
                    in_parentheses = True
                    continue
                elif token.value == ')':
                    if current_column.strip():
                        columns.append(self._parse_column_definition(current_column.strip()))
                    break
                elif in_parentheses:
                    if token.value == ',':
                        if current_column.strip():
                            columns.append(self._parse_column_definition(current_column.strip()))
                            current_column = ""
                    else:
                        current_column += token.value

            return {
                "name": table_name,
                "columns": [col for col in columns if col],
                "constraints": [],
                "indexes": []
            }

        except Exception as e:
            logger.warning(f"Error parsing CREATE TABLE: {e}")
            return None

    def _parse_column_definition(self, col_def: str) -> Optional[Dict[str, Any]]:
        """Parse a column definition to JSON."""
        parts = col_def.strip().split()
        if len(parts) < 2:
            return None

        column = {
            "name": parts[0].strip('`"[]'),
            "type": parts[1],
            "nullable": True,
            "primary_key": False,
            "auto_increment": False,
            "default": None
        }

        col_def_upper = col_def.upper()

        if 'NOT NULL' in col_def_upper:
            column["nullable"] = False
        if 'PRIMARY KEY' in col_def_upper:
            column["primary_key"] = True
        if 'AUTO_INCREMENT' in col_def_upper or 'AUTOINCREMENT' in col_def_upper:
            column["auto_increment"] = True

        # Extract default value
        default_match = re.search(r'DEFAULT\s+([^,\s]+)', col_def_upper)
        if default_match:
            column["default"] = default_match.group(1)

        return column

    def _parse_create_index_to_json(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE INDEX statement to JSON representation."""
        # Simplified index parsing
        match = re.search(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)\s+ON\s+(\w+)\s*\(([^)]+)\)',
                         statement, re.IGNORECASE)
        if match:
            return {
                "name": match.group(1),
                "table": match.group(2),
                "columns": [col.strip() for col in match.group(3).split(',')],
                "unique": 'UNIQUE' in statement.upper()
            }
        return None

    def _parse_create_view_to_json(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE VIEW statement to JSON representation."""
        match = re.search(r'CREATE\s+VIEW\s+(\w+)\s+AS\s+(.+)', statement, re.IGNORECASE | re.DOTALL)
        if match:
            return {
                "name": match.group(1),
                "definition": match.group(2).strip()
            }
        return None

    def _json_table_to_sql(self, table: Dict[str, Any], target_format: DatabaseType) -> str:
        """Convert JSON table definition to SQL."""
        table_name = table.get("name", "")
        columns = table.get("columns", [])

        if not table_name or not columns:
            return ""

        # Build CREATE TABLE statement
        sql_parts = [f"CREATE TABLE {table_name} ("]

        column_definitions = []
        for column in columns:
            col_def = self._json_column_to_sql(column, target_format)
            if col_def:
                column_definitions.append(f"    {col_def}")

        sql_parts.append(",\n".join(column_definitions))
        sql_parts.append(");")

        return "\n".join(sql_parts)

    def _json_column_to_sql(self, column: Dict[str, Any], target_format: DatabaseType) -> str:
        """Convert JSON column definition to SQL."""
        name = column.get("name", "")
        col_type = column.get("type", "")

        if not name or not col_type:
            return ""

        # Map data type to target format
        target_types = self.TYPE_MAPPINGS.get(target_format, {})
        mapped_type = target_types.get(col_type.upper(), col_type)

        col_def = f"{name} {mapped_type}"

        # Add constraints
        if not column.get("nullable", True):
            col_def += " NOT NULL"

        if column.get("primary_key", False):
            col_def += " PRIMARY KEY"

        if column.get("auto_increment", False):
            auto_inc = self.SYNTAX_PATTERNS.get(target_format, {}).get('auto_increment', '')
            if auto_inc:
                col_def += f" {auto_inc}"

        if column.get("default") is not None:
            col_def += f" DEFAULT {column['default']}"

        return col_def

    def _json_index_to_sql(self, index: Dict[str, Any], target_format: DatabaseType) -> str:
        """Convert JSON index definition to SQL."""
        name = index.get("name", "")
        table = index.get("table", "")
        columns = index.get("columns", [])
        unique = index.get("unique", False)

        if not name or not table or not columns:
            return ""

        unique_keyword = "UNIQUE " if unique else ""
        columns_str = ", ".join(columns)

        return f"CREATE {unique_keyword}INDEX {name} ON {table} ({columns_str});"

    def _json_view_to_sql(self, view: Dict[str, Any], target_format: DatabaseType) -> str:
        """Convert JSON view definition to SQL."""
        name = view.get("name", "")
        definition = view.get("definition", "")

        if not name or not definition:
            return ""

        return f"CREATE VIEW {name} AS {definition};"

    def get_supported_conversions(self) -> Dict[str, List[str]]:
        """Get list of supported conversion paths."""
        conversions = {}

        for source in DatabaseType:
            conversions[source.value] = [target.value for target in DatabaseType if target != source]

        return conversions

    def validate_conversion(self, source_format: DatabaseType, target_format: DatabaseType) -> Tuple[bool, List[str]]:
        """Validate if conversion between formats is supported."""
        warnings = []

        if source_format == target_format:
            return False, ["Source and target formats are the same"]

        # Check for potential data loss scenarios
        if source_format == DatabaseType.MYSQL and target_format == DatabaseType.SQLITE:
            warnings.append("Some MySQL-specific features may not be supported in SQLite")

        if target_format == DatabaseType.ORACLE and source_format != DatabaseType.ORACLE:
            warnings.append("Oracle has specific syntax requirements that may need manual adjustment")

        if source_format == DatabaseType.JSON:
            warnings.append("JSON to SQL conversion may require manual schema validation")

        return True, warnings

    def generate_conversion_report(self, result: ConversionResult) -> str:
        """Generate a detailed conversion report."""
        report = []
        report.append("Database Format Conversion Report")
        report.append("=" * 50)
        report.append("")

        report.append(f"Source Format: {result.source_format.value}")
        report.append(f"Target Format: {result.target_format.value}")
        report.append(f"Conversion Status: {'SUCCESS' if result.success else 'FAILED'}")
        report.append("")

        if result.conversion_notes:
            report.append("Conversion Notes:")
            for note in result.conversion_notes:
                report.append(f"  - {note}")
            report.append("")

        if result.warnings:
            report.append("Warnings:")
            for warning in result.warnings:
                report.append(f"  - {warning}")
            report.append("")

        if result.errors:
            report.append("Errors:")
            for error in result.errors:
                report.append(f"  - {error}")
            report.append("")

        return "\n".join(report)
