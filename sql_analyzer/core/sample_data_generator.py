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
        
    def generate_sample_data(self, sql_content: str, config: GenerationConfig) -> Dict:
        """
        Generate sample data for all tables in SQL schema.
        
        Args:
            sql_content: SQL schema content
            config: Generation configuration
            
        Returns:
            Dict with generated INSERT statements and metadata
        """
        try:
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
    
    def _parse_schema(self, sql_content: str) -> Dict[str, TableInfo]:
        """Parse SQL schema and extract table information."""
        tables = {}
        
        # Parse SQL statements
        parsed = sqlparse.parse(sql_content)
        
        for statement in parsed:
            statement_str = str(statement).strip()
            
            if statement_str.upper().startswith('CREATE TABLE'):
                table_info = self._parse_create_table(statement_str)
                if table_info:
                    tables[table_info.name] = table_info
        
        return tables
    
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
    
    def _sort_tables_by_dependencies(self) -> List[str]:
        """Sort tables by foreign key dependencies."""
        sorted_tables = []
        remaining_tables = set(self.tables.keys())
        
        while remaining_tables:
            # Find tables with no unresolved dependencies
            ready_tables = []
            
            for table_name in remaining_tables:
                table_info = self.tables[table_name]
                dependencies_resolved = True
                
                for fk in table_info.foreign_keys:
                    ref_table = fk['referenced_table']
                    if ref_table in remaining_tables and ref_table != table_name:
                        dependencies_resolved = False
                        break
                
                if dependencies_resolved:
                    ready_tables.append(table_name)
            
            if not ready_tables:
                # Circular dependency or error - add remaining tables
                ready_tables = list(remaining_tables)
            
            sorted_tables.extend(ready_tables)
            remaining_tables -= set(ready_tables)
        
        return sorted_tables
    
    def _generate_table_data(self, table_info: TableInfo, config: GenerationConfig) -> List[Dict[str, Any]]:
        """Generate sample data for a specific table."""
        data = []
        
        for i in range(config.records_per_table):
            record = {}
            
            for column in table_info.columns:
                value = self._generate_column_value(column, table_info, i, config)
                record[column['name']] = value
            
            data.append(record)
        
        return data
    
    def _generate_column_value(self, column: Dict[str, Any], table_info: TableInfo, record_index: int, config: GenerationConfig) -> Any:
        """Generate a value for a specific column."""
        col_name = column['name'].lower()
        col_type = column['type']
        
        # Handle auto-increment columns
        if column.get('auto_increment'):
            return record_index + 1
        
        # Handle foreign keys
        for fk in table_info.foreign_keys:
            if fk['column'] == column['name']:
                return self._generate_foreign_key_value(fk, config)
        
        # Handle primary keys
        if column['name'] == table_info.primary_key and not column.get('auto_increment'):
            return record_index + 1
        
        # Generate based on column name patterns
        if config.use_realistic_data:
            realistic_value = self._generate_realistic_value(col_name, col_type, column.get('size'))
            if realistic_value is not None:
                return realistic_value
        
        # Generate based on data type
        return self._generate_typed_value(col_type, column.get('size'), record_index)
    
    def _generate_realistic_value(self, col_name: str, col_type: str, size: Optional[int]) -> Any:
        """Generate realistic value based on column name patterns."""
        for pattern, generator in self.name_patterns.items():
            if pattern in col_name:
                if callable(generator):
                    return generator(size)
                else:
                    return random.choice(generator)
        
        return None
    
    def _generate_typed_value(self, col_type: str, size: Optional[int], index: int) -> Any:
        """Generate value based on data type."""
        if col_type in ['INT', 'INTEGER']:
            return random.randint(1, 1000)
        elif col_type in ['VARCHAR', 'TEXT']:
            length = min(size or 50, 50)
            return f"Texto_{index}_{random.randint(1, 999)}"[:length]
        elif col_type in ['DATETIME', 'TIMESTAMP']:
            base_date = datetime.now() - timedelta(days=random.randint(0, 730))
            return base_date.strftime('%Y-%m-%d %H:%M:%S')
        elif col_type == 'DATE':
            base_date = datetime.now() - timedelta(days=random.randint(0, 730))
            return base_date.strftime('%Y-%m-%d')
        elif col_type == 'TIME':
            return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        elif col_type in ['BOOLEAN', 'BOOL']:
            return random.choice([True, False])
        elif col_type in ['DECIMAL', 'FLOAT', 'DOUBLE']:
            return round(random.uniform(1.0, 1000.0), 2)
        else:
            return f"Valor_{index}"
    
    def _generate_foreign_key_value(self, fk: Dict[str, str], config: GenerationConfig) -> Any:
        """Generate foreign key value maintaining referential integrity."""
        ref_table = fk['referenced_table']
        ref_column = fk['referenced_column']
        
        if ref_table in self.generated_data:
            ref_data = self.generated_data[ref_table]
            if ref_data:
                ref_record = random.choice(ref_data)
                return ref_record.get(ref_column, 1)
        
        # Fallback to simple integer
        return random.randint(1, min(config.records_per_table, 10))
    
    def _create_insert_statements(self, table_info: TableInfo, data: List[Dict[str, Any]]) -> str:
        """Create INSERT statements for table data."""
        if not data:
            return ""
        
        # Get column names (excluding auto-increment columns)
        columns = [col['name'] for col in table_info.columns if not col.get('auto_increment')]
        
        if not columns:
            return ""
        
        # Create INSERT statement
        insert_lines = []
        insert_lines.append(f"INSERT INTO {table_info.name} ({', '.join(columns)}) VALUES")
        
        # Add value rows
        value_rows = []
        for record in data:
            values = []
            for col_name in columns:
                value = record.get(col_name)
                if value is None:
                    values.append('NULL')
                elif isinstance(value, str):
                    # Escape single quotes
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                elif isinstance(value, bool):
                    values.append('1' if value else '0')
                else:
                    values.append(str(value))
            
            value_rows.append(f"    ({', '.join(values)})")
        
        insert_lines.append(',\n'.join(value_rows) + ';')
        
        return '\n'.join(insert_lines)
    
    def _load_name_patterns(self) -> Dict[str, Any]:
        """Load column name patterns for realistic data generation."""
        return {
            'nombre': lambda size: random.choice([
                'María García', 'Carlos López', 'Ana Martínez', 'José Rodríguez',
                'Carmen Fernández', 'Antonio González', 'Isabel Sánchez', 'Manuel Pérez',
                'Pilar Ruiz', 'Francisco Jiménez', 'Teresa Muñoz', 'Miguel Álvarez'
            ]),
            'name': lambda size: random.choice([
                'John Smith', 'Jane Doe', 'Michael Johnson', 'Sarah Wilson',
                'David Brown', 'Lisa Davis', 'Robert Miller', 'Jennifer Garcia',
                'William Martinez', 'Elizabeth Anderson', 'James Taylor', 'Mary Thomas'
            ]),
            'email': lambda size: f"{random.choice(['juan', 'maria', 'carlos', 'ana', 'luis', 'sofia'])}.{random.choice(['garcia', 'lopez', 'martinez', 'rodriguez', 'fernandez'])}@{random.choice(['gmail.com', 'hotmail.com', 'yahoo.com', 'empresa.com'])}",
            'correo': lambda size: f"{random.choice(['juan', 'maria', 'carlos', 'ana', 'luis', 'sofia'])}.{random.choice(['garcia', 'lopez', 'martinez', 'rodriguez', 'fernandez'])}@{random.choice(['gmail.com', 'hotmail.com', 'yahoo.com', 'empresa.com'])}",
            'telefono': lambda size: f"+34 {random.randint(600, 999)} {random.randint(100, 999)} {random.randint(100, 999)}",
            'phone': lambda size: f"+1 {random.randint(200, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
            'direccion': lambda size: f"Calle {random.choice(['Mayor', 'Principal', 'Real', 'Nueva', 'San Juan'])} {random.randint(1, 100)}, {random.choice(['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao'])}",
            'address': lambda size: f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Park Rd', 'First St', 'Second Ave'])}, {random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])}",
            'ciudad': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza', 'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao'],
            'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'],
            'pais': ['España', 'Francia', 'Italia', 'Portugal', 'Alemania', 'Reino Unido', 'Países Bajos', 'Bélgica', 'Suiza', 'Austria'],
            'country': ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Australia', 'Japan', 'Brazil'],
            'empresa': ['Tecnología S.L.', 'Innovación Corp', 'Desarrollo SA', 'Sistemas Avanzados', 'Soluciones Digitales', 'Consultoría Tech'],
            'company': ['Tech Solutions Inc', 'Innovation Corp', 'Digital Systems', 'Advanced Technologies', 'Smart Solutions', 'Future Tech'],
            'descripcion': lambda size: random.choice([
                'Descripción detallada del elemento',
                'Información completa y actualizada',
                'Datos relevantes para el sistema',
                'Contenido importante para la aplicación',
                'Detalles específicos del registro'
            ]),
            'description': lambda size: random.choice([
                'Detailed description of the item',
                'Complete and updated information',
                'Relevant data for the system',
                'Important content for the application',
                'Specific details of the record'
            ])
        }
    
    def _load_data_patterns(self) -> Dict[str, Any]:
        """Load data type patterns for generation."""
        return {
            'status': ['activo', 'inactivo', 'pendiente', 'completado', 'cancelado'],
            'estado': ['activo', 'inactivo', 'pendiente', 'completado', 'cancelado'],
            'tipo': ['tipo_a', 'tipo_b', 'tipo_c', 'especial', 'premium'],
            'type': ['type_a', 'type_b', 'type_c', 'special', 'premium'],
            'categoria': ['general', 'especial', 'premium', 'básico', 'avanzado'],
            'category': ['general', 'special', 'premium', 'basic', 'advanced']
        }
