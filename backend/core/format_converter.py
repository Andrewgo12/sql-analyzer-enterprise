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
