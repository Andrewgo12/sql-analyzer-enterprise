"""
Sample Data Generator Module

Generates realistic sample data for SQL database schemas based on
table structures, column types, and naming patterns.
"""

import re
import random
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlparse
from sqlparse import sql, tokens as T

logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    columns: List[Dict[str, Any]]
    primary_key: Optional[str] = None
    foreign_keys: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.foreign_keys is None:
            self.foreign_keys = []


@dataclass
class GenerationConfig:
    """Configuration for data generation."""
    records_per_table: int = 100
    use_realistic_data: bool = True
    maintain_referential_integrity: bool = True
    generate_unique_values: bool = True
    date_range_years: int = 2


class SampleDataGenerator:
    """Generates realistic sample data for SQL schemas."""
    
    def __init__(self):
        self.tables = {}
        self.generated_data = {}
        self.name_patterns = self._load_name_patterns()
        self.data_patterns = self._load_data_patterns()
        
    def generate_sample_data(self, sql_content: str, config: GenerationConfig = None) -> Dict:
        """
        Generate sample data for all tables in SQL schema.
        
        Args:
            sql_content: SQL schema content
            config: Generation configuration
            
        Returns:
            Dict with generated INSERT statements and metadata
        """
        try:
            if config is None:
                config = GenerationConfig()
            # Parse schema
            self.tables = self._parse_schema(sql_content)
            
            if not self.tables:
                return {
                    'success': False,
                    'error': 'No se encontraron tablas en el esquema SQL',
                    'insert_statements': '',
                    'tables_processed': 0
                }
            
            # Generate data for each table
            insert_statements = []
            tables_processed = 0
            
            # Sort tables by dependency order
            sorted_tables = self._sort_tables_by_dependencies()
            
            for table_name in sorted_tables:
                table_info = self.tables[table_name]
                
                # Generate data for this table
                table_data = self._generate_table_data(table_info, config)
                self.generated_data[table_name] = table_data
                
                # Create INSERT statements
                insert_sql = self._create_insert_statements(table_info, table_data)
                insert_statements.append(f"\n-- Datos de prueba para la tabla: {table_name}")
                insert_statements.append(insert_sql)
                
                tables_processed += 1
            
            return {
                'success': True,
                'insert_statements': '\n'.join(insert_statements),
                'tables_processed': tables_processed,
                'total_records': sum(len(data) for data in self.generated_data.values()),
                'generation_config': {
                    'records_per_table': config.records_per_table,
                    'realistic_data': config.use_realistic_data,
                    'referential_integrity': config.maintain_referential_integrity
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            return {
                'success': False,
                'error': str(e),
                'insert_statements': '',
                'tables_processed': 0
            }

    def analyze_schema(self, sql_content: str) -> Dict:
        """
        Analyze SQL schema structure for data generation.

        Args:
            sql_content: SQL schema content to analyze

        Returns:
            Dict with schema analysis results
        """
        try:
            tables = self._parse_schema(sql_content)

            analysis = {
                'tables_found': len(tables),
                'table_details': [],
                'relationships': [],
                'data_types': set(),
                'constraints': []
            }

            for table_name, table_info in tables.items():
                table_detail = {
                    'name': table_name,
                    'columns': len(table_info.columns),
                    'primary_keys': [col.name for col in table_info.columns if getattr(col, 'is_primary_key', False)],
                    'foreign_keys': [col.name for col in table_info.columns if getattr(col, 'foreign_key_table', None)],
                    'nullable_columns': [col.name for col in table_info.columns if getattr(col, 'nullable', True)],
                    'data_types': [getattr(col, 'data_type', 'VARCHAR') for col in table_info.columns]
                }
                analysis['table_details'].append(table_detail)

                # Collect data types
                for col in table_info.columns:
                    analysis['data_types'].add(col.data_type)

                # Collect relationships
                for col in table_info.columns:
                    if col.foreign_key_table:
                        analysis['relationships'].append({
                            'from_table': table_name,
                            'from_column': col.name,
                            'to_table': col.foreign_key_table,
                            'to_column': col.foreign_key_column or 'id'
                        })

            # Convert set to list for JSON serialization
            analysis['data_types'] = list(analysis['data_types'])

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing schema: {e}")
            return {
                'tables_found': 0,
                'table_details': [],
                'relationships': [],
                'data_types': [],
                'constraints': [],
                'error': str(e)
            }

    def _parse_create_table(self, statement: str) -> Optional[TableInfo]:
        """Parse CREATE TABLE statement and extract table information."""
        try:
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement, re.IGNORECASE)
            if not table_match:
                return None
            
            table_name = table_match.group(1)
            
            # Extract column definitions
            columns = []
            primary_key = None
            foreign_keys = []
            
            # Find column definitions between parentheses
            paren_content = re.search(r'\((.*)\)', statement, re.DOTALL)
            if not paren_content:
                return None
            
            column_defs = paren_content.group(1)
            
            # Split by commas (but not within parentheses)
            column_lines = self._split_column_definitions(column_defs)
            
            for line in column_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for PRIMARY KEY constraint
                if 'PRIMARY KEY' in line.upper():
                    if line.strip().upper().startswith('PRIMARY KEY'):
                        # Table-level primary key
                        pk_match = re.search(r'PRIMARY\s+KEY\s*\(\s*(\w+)\s*\)', line, re.IGNORECASE)
                        if pk_match:
                            primary_key = pk_match.group(1)
                    else:
                        # Column-level primary key
                        col_match = re.search(r'^(\w+)', line)
                        if col_match:
                            primary_key = col_match.group(1)
                
                # Check for FOREIGN KEY constraint
                if 'FOREIGN KEY' in line.upper():
                    fk_match = re.search(r'FOREIGN\s+KEY\s*\(\s*(\w+)\s*\)\s+REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', line, re.IGNORECASE)
                    if fk_match:
                        foreign_keys.append({
                            'column': fk_match.group(1),
                            'referenced_table': fk_match.group(2),
                            'referenced_column': fk_match.group(3)
                        })
                
                # Parse column definition
                column_info = self._parse_column_definition(line)
                if column_info:
                    columns.append(column_info)
            
            return TableInfo(
                name=table_name,
                columns=columns,
                primary_key=primary_key,
                foreign_keys=foreign_keys
            )
            
        except Exception as e:
            logger.error(f"Error parsing CREATE TABLE statement: {e}")
            return None
    
    def _split_column_definitions(self, column_defs: str) -> List[str]:
        """Split column definitions by commas, respecting parentheses."""
        lines = []
        current_line = ""
        paren_count = 0
        
        for char in column_defs:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                lines.append(current_line.strip())
                current_line = ""
                continue
            
            current_line += char
        
        if current_line.strip():
            lines.append(current_line.strip())
        
        return lines
    
    def _parse_column_definition(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single column definition."""
        try:
            # Skip constraint definitions
            if any(keyword in line.upper() for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'INDEX']):
                if not re.match(r'^\w+\s+', line):  # If it doesn't start with column name
                    return None
            
            # Extract column name and type
            col_match = re.match(r'^(\w+)\s+(VARCHAR|INT|INTEGER|TEXT|DATETIME|TIMESTAMP|BOOLEAN|BOOL|DECIMAL|FLOAT|DOUBLE|DATE|TIME)(\([^)]+\))?', line, re.IGNORECASE)
            if not col_match:
                return None
            
            column_name = col_match.group(1)
            data_type = col_match.group(2).upper()
            size_info = col_match.group(3) or ""
            
            # Extract size/precision
            size = None
            if size_info:
                size_match = re.search(r'\((\d+)\)', size_info)
                if size_match:
                    size = int(size_match.group(1))
            
            # Check constraints
            is_nullable = 'NOT NULL' not in line.upper()
            is_auto_increment = 'AUTO_INCREMENT' in line.upper() or 'AUTOINCREMENT' in line.upper()
            is_unique = 'UNIQUE' in line.upper()
            
            # Extract default value
            default_value = None
            default_match = re.search(r'DEFAULT\s+([^,\s]+)', line, re.IGNORECASE)
            if default_match:
                default_value = default_match.group(1).strip("'\"")
            
            return {
                'name': column_name,
                'type': data_type,
                'size': size,
                'nullable': is_nullable,
                'auto_increment': is_auto_increment,
                'unique': is_unique,
                'default': default_value
            }
            
        except Exception as e:
            logger.error(f"Error parsing column definition '{line}': {e}")
            return None
    
