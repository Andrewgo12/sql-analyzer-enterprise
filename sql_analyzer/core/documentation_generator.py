"""
Advanced SQL Documentation Generator

Generates comprehensive database documentation in multiple formats
including HTML, PDF, and Markdown with detailed analysis.
"""

import re
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sqlparse
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TableDocumentation:
    """Documentation for a database table."""
    name: str
    description: str
    columns: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    estimated_rows: Optional[int] = None
    business_rules: List[str] = None
    
    def __post_init__(self):
        if self.business_rules is None:
            self.business_rules = []


@dataclass
class DatabaseDocumentation:
    """Complete database documentation."""
    database_name: str
    tables: List[TableDocumentation]
    views: List[Dict[str, Any]]
    procedures: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    generated_at: datetime
    version: str = "1.0"


class DocumentationGenerator:
    """Generates comprehensive database documentation."""
    
    def __init__(self):
        self.column_descriptions = self._load_column_descriptions()
        self.table_descriptions = self._load_table_descriptions()
        
    def generate_documentation(self, sql_content: str, format_type: str = "html") -> Dict:
        """
        Generate comprehensive database documentation.
        
        Args:
            sql_content: SQL schema content
            format_type: Output format ('html', 'pdf', 'markdown')
            
        Returns:
            Dict with generated documentation and metadata
        """
        try:
            # Parse SQL content
            db_doc = self._parse_database_schema(sql_content)
            
            # Generate documentation in requested format
            if format_type.lower() == 'html':
                content = self._generate_html_documentation(db_doc)
                mime_type = 'text/html'
            elif format_type.lower() == 'markdown':
                content = self._generate_markdown_documentation(db_doc)
                mime_type = 'text/markdown'
            elif format_type.lower() == 'pdf':
                content = self._generate_pdf_documentation(db_doc)
                mime_type = 'application/pdf'
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            return {
                'success': True,
                'content': content,
                'mime_type': mime_type,
                'filename': f"database_documentation.{format_type.lower()}",
                'tables_documented': len(db_doc.tables),
                'total_columns': sum(len(table.columns) for table in db_doc.tables),
                'generated_at': db_doc.generated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'mime_type': 'text/plain'
            }
    
    def _parse_database_schema(self, sql_content: str) -> DatabaseDocumentation:
        """Parse SQL content and extract database schema information."""
        parsed = sqlparse.parse(sql_content)
        
        tables = []
        views = []
        procedures = []
        functions = []
        triggers = []
        
        for statement in parsed:
            statement_str = str(statement).strip()
            statement_upper = statement_str.upper()
            
            if statement_upper.startswith('CREATE TABLE'):
                table_doc = self._parse_table_documentation(statement_str)
                if table_doc:
                    tables.append(table_doc)
            elif statement_upper.startswith('CREATE VIEW'):
                view_doc = self._parse_view_documentation(statement_str)
                if view_doc:
                    views.append(view_doc)
            elif statement_upper.startswith('CREATE PROCEDURE'):
                proc_doc = self._parse_procedure_documentation(statement_str)
                if proc_doc:
                    procedures.append(proc_doc)
            elif statement_upper.startswith('CREATE FUNCTION'):
                func_doc = self._parse_function_documentation(statement_str)
                if func_doc:
                    functions.append(func_doc)
            elif statement_upper.startswith('CREATE TRIGGER'):
                trigger_doc = self._parse_trigger_documentation(statement_str)
                if trigger_doc:
                    triggers.append(trigger_doc)
        
        return DatabaseDocumentation(
            database_name="Database Schema",
            tables=tables,
            views=views,
            procedures=procedures,
            functions=functions,
            triggers=triggers,
            generated_at=datetime.now()
        )
    
    def _parse_table_documentation(self, statement: str) -> Optional[TableDocumentation]:
        """Parse CREATE TABLE statement and generate documentation."""
        try:
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement, re.IGNORECASE)
            if not table_match:
                return None
            
            table_name = table_match.group(1)
            
            # Generate table description
            description = self._get_table_description(table_name)
            
            # Parse columns
            columns = self._parse_table_columns(statement)
            
            # Parse indexes
            indexes = self._parse_table_indexes(statement)
            
            # Parse constraints
            constraints = self._parse_table_constraints(statement)
            
            # Parse relationships
            relationships = self._parse_table_relationships(statement)
            
            # Generate business rules
            business_rules = self._generate_business_rules(table_name, columns, constraints)
            
            return TableDocumentation(
                name=table_name,
                description=description,
                columns=columns,
                indexes=indexes,
                constraints=constraints,
                relationships=relationships,
                business_rules=business_rules
            )
            
        except Exception as e:
            logger.error(f"Error parsing table documentation: {e}")
            return None
    
    def _parse_table_columns(self, statement: str) -> List[Dict[str, Any]]:
        """Parse table columns with detailed information."""
        columns = []
        
        # Find column definitions between parentheses
        paren_content = re.search(r'\((.*)\)', statement, re.DOTALL)
        if not paren_content:
            return columns
        
        column_defs = paren_content.group(1)
        column_lines = self._split_column_definitions(column_defs)
        
        for line in column_lines:
            line = line.strip()
            if not line or any(keyword in line.upper() for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'INDEX']):
                if not re.match(r'^\w+\s+', line):
                    continue
            
            column_info = self._parse_column_info(line)
            if column_info:
                columns.append(column_info)
        
        return columns
    
    def _parse_column_info(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse detailed column information."""
        try:
            # Extract column name and type
            col_match = re.match(r'^(\w+)\s+(VARCHAR|INT|INTEGER|TEXT|DATETIME|TIMESTAMP|BOOLEAN|BOOL|DECIMAL|FLOAT|DOUBLE|DATE|TIME)(\([^)]+\))?', line, re.IGNORECASE)
            if not col_match:
                return None
            
            column_name = col_match.group(1)
            data_type = col_match.group(2).upper()
            size_info = col_match.group(3) or ""
            
            # Extract size/precision
            size = None
            precision = None
            scale = None
            
            if size_info:
                if ',' in size_info:
                    # DECIMAL(10,2) format
                    size_match = re.search(r'\((\d+),(\d+)\)', size_info)
                    if size_match:
                        precision = int(size_match.group(1))
                        scale = int(size_match.group(2))
                else:
                    # VARCHAR(50) format
                    size_match = re.search(r'\((\d+)\)', size_info)
                    if size_match:
                        size = int(size_match.group(1))
            
            # Parse constraints and properties
            is_nullable = 'NOT NULL' not in line.upper()
            is_auto_increment = 'AUTO_INCREMENT' in line.upper() or 'AUTOINCREMENT' in line.upper()
            is_unique = 'UNIQUE' in line.upper()
            is_primary_key = 'PRIMARY KEY' in line.upper()
            
            # Extract default value
            default_value = None
            default_match = re.search(r'DEFAULT\s+([^,\s]+)', line, re.IGNORECASE)
            if default_match:
                default_value = default_match.group(1).strip("'\"")
            
            # Generate column description
            description = self._get_column_description(column_name, data_type)
            
            return {
                'name': column_name,
                'type': data_type,
                'size': size,
                'precision': precision,
                'scale': scale,
                'nullable': is_nullable,
                'auto_increment': is_auto_increment,
                'unique': is_unique,
                'primary_key': is_primary_key,
                'default': default_value,
                'description': description,
                'business_meaning': self._get_business_meaning(column_name)
            }
            
        except Exception as e:
            logger.error(f"Error parsing column info '{line}': {e}")
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
    
    def _parse_table_indexes(self, statement: str) -> List[Dict[str, Any]]:
        """Parse table indexes."""
        indexes = []
        
        # Look for INDEX definitions
        index_matches = re.findall(r'INDEX\s+(\w+)\s*\(([^)]+)\)', statement, re.IGNORECASE)
        for index_name, columns in index_matches:
            indexes.append({
                'name': index_name,
                'columns': [col.strip() for col in columns.split(',')],
                'type': 'INDEX',
                'unique': False
            })
        
        # Look for UNIQUE INDEX definitions
        unique_matches = re.findall(r'UNIQUE\s+INDEX\s+(\w+)\s*\(([^)]+)\)', statement, re.IGNORECASE)
        for index_name, columns in unique_matches:
            indexes.append({
                'name': index_name,
                'columns': [col.strip() for col in columns.split(',')],
                'type': 'UNIQUE INDEX',
                'unique': True
            })
        
        return indexes
    
    def _parse_table_constraints(self, statement: str) -> List[Dict[str, Any]]:
        """Parse table constraints."""
        constraints = []
        
        # Primary key constraints
        pk_matches = re.findall(r'PRIMARY\s+KEY\s*\(([^)]+)\)', statement, re.IGNORECASE)
        for columns in pk_matches:
            constraints.append({
                'type': 'PRIMARY KEY',
                'columns': [col.strip() for col in columns.split(',')],
                'description': 'Clave primaria que identifica únicamente cada registro'
            })
        
        # Foreign key constraints
        fk_matches = re.findall(r'FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+(\w+)\s*\(([^)]+)\)', statement, re.IGNORECASE)
        for local_cols, ref_table, ref_cols in fk_matches:
            constraints.append({
                'type': 'FOREIGN KEY',
                'columns': [col.strip() for col in local_cols.split(',')],
                'referenced_table': ref_table,
                'referenced_columns': [col.strip() for col in ref_cols.split(',')],
                'description': f'Referencia a la tabla {ref_table}'
            })
        
        # Check constraints
        check_matches = re.findall(r'CHECK\s*\(([^)]+)\)', statement, re.IGNORECASE)
        for check_condition in check_matches:
            constraints.append({
                'type': 'CHECK',
                'condition': check_condition,
                'description': f'Validación: {check_condition}'
            })
        
        return constraints
    
    def _parse_table_relationships(self, statement: str) -> List[Dict[str, Any]]:
        """Parse table relationships."""
        relationships = []
        
        # Foreign key relationships
        fk_matches = re.findall(r'FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+(\w+)\s*\(([^)]+)\)', statement, re.IGNORECASE)
        for local_cols, ref_table, ref_cols in fk_matches:
            relationships.append({
                'type': 'BELONGS_TO',
                'related_table': ref_table,
                'local_columns': [col.strip() for col in local_cols.split(',')],
                'foreign_columns': [col.strip() for col in ref_cols.split(',')],
                'cardinality': 'many-to-one',
                'description': f'Cada registro pertenece a un registro en {ref_table}'
            })
        
        return relationships
    
    def _parse_view_documentation(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE VIEW statement."""
        view_match = re.search(r'CREATE\s+VIEW\s+(\w+)', statement, re.IGNORECASE)
        if not view_match:
            return None
        
        view_name = view_match.group(1)
        
        return {
            'name': view_name,
            'type': 'VIEW',
            'description': f'Vista que proporciona una representación específica de los datos',
            'definition': statement,
            'dependencies': self._extract_table_dependencies(statement)
        }
    
    def _parse_procedure_documentation(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE PROCEDURE statement."""
        proc_match = re.search(r'CREATE\s+PROCEDURE\s+(\w+)', statement, re.IGNORECASE)
        if not proc_match:
            return None
        
        proc_name = proc_match.group(1)
        
        return {
            'name': proc_name,
            'type': 'PROCEDURE',
            'description': f'Procedimiento almacenado para operaciones específicas',
            'parameters': self._extract_procedure_parameters(statement),
            'definition': statement
        }
    
    def _parse_function_documentation(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE FUNCTION statement."""
        func_match = re.search(r'CREATE\s+FUNCTION\s+(\w+)', statement, re.IGNORECASE)
        if not func_match:
            return None
        
        func_name = func_match.group(1)
        
        return {
            'name': func_name,
            'type': 'FUNCTION',
            'description': f'Función que retorna un valor calculado',
            'parameters': self._extract_function_parameters(statement),
            'return_type': self._extract_return_type(statement),
            'definition': statement
        }
    
    def _parse_trigger_documentation(self, statement: str) -> Optional[Dict[str, Any]]:
        """Parse CREATE TRIGGER statement."""
        trigger_match = re.search(r'CREATE\s+TRIGGER\s+(\w+)', statement, re.IGNORECASE)
        if not trigger_match:
            return None
        
        trigger_name = trigger_match.group(1)
        
        return {
            'name': trigger_name,
            'type': 'TRIGGER',
            'description': f'Trigger que se ejecuta automáticamente en respuesta a eventos',
            'event': self._extract_trigger_event(statement),
            'table': self._extract_trigger_table(statement),
            'definition': statement
        }
    
    def _get_table_description(self, table_name: str) -> str:
        """Get description for table based on naming patterns."""
        table_lower = table_name.lower()
        
        for pattern, description in self.table_descriptions.items():
            if pattern in table_lower:
                return description
        
        return f"Tabla {table_name} - Almacena información del sistema"
    
    def _get_column_description(self, column_name: str, data_type: str) -> str:
        """Get description for column based on naming patterns."""
        column_lower = column_name.lower()
        
        for pattern, description in self.column_descriptions.items():
            if pattern in column_lower:
                return description.format(type=data_type)
        
        return f"Campo de tipo {data_type}"
    
    def _get_business_meaning(self, column_name: str) -> str:
        """Get business meaning for column."""
        column_lower = column_name.lower()
        
        business_meanings = {
            'id': 'Identificador único del registro',
            'name': 'Nombre descriptivo del elemento',
            'nombre': 'Nombre descriptivo del elemento',
            'email': 'Dirección de correo electrónico',
            'correo': 'Dirección de correo electrónico',
            'phone': 'Número de teléfono de contacto',
            'telefono': 'Número de teléfono de contacto',
            'address': 'Dirección física o postal',
            'direccion': 'Dirección física o postal',
            'created': 'Fecha y hora de creación del registro',
            'updated': 'Fecha y hora de última modificación',
            'status': 'Estado actual del registro',
            'estado': 'Estado actual del registro',
            'active': 'Indica si el registro está activo',
            'activo': 'Indica si el registro está activo'
        }
        
        for pattern, meaning in business_meanings.items():
            if pattern in column_lower:
                return meaning
        
        return 'Campo de datos del sistema'
    
    def _generate_business_rules(self, table_name: str, columns: List[Dict], constraints: List[Dict]) -> List[str]:
        """Generate business rules for the table."""
        rules = []
        
        # Rules based on constraints
        for constraint in constraints:
            if constraint['type'] == 'PRIMARY KEY':
                rules.append(f"Cada registro debe tener un identificador único ({', '.join(constraint['columns'])})")
            elif constraint['type'] == 'FOREIGN KEY':
                rules.append(f"Debe existir una referencia válida en la tabla {constraint['referenced_table']}")
            elif constraint['type'] == 'CHECK':
                rules.append(f"Los datos deben cumplir la condición: {constraint['condition']}")
        
        # Rules based on column properties
        for column in columns:
            if not column['nullable']:
                rules.append(f"El campo {column['name']} es obligatorio")
            if column['unique']:
                rules.append(f"El campo {column['name']} debe ser único")
            if column['auto_increment']:
                rules.append(f"El campo {column['name']} se genera automáticamente")
        
        return rules
    
    def _extract_table_dependencies(self, statement: str) -> List[str]:
        """Extract table dependencies from SQL statement."""
        dependencies = []
        
        # Look for table names in FROM and JOIN clauses
        from_matches = re.findall(r'FROM\s+(\w+)', statement, re.IGNORECASE)
        join_matches = re.findall(r'JOIN\s+(\w+)', statement, re.IGNORECASE)
        
        dependencies.extend(from_matches)
        dependencies.extend(join_matches)
        
        return list(set(dependencies))
    
    def _extract_procedure_parameters(self, statement: str) -> List[Dict[str, str]]:
        """Extract parameters from procedure definition."""
        # Simplified parameter extraction
        param_match = re.search(r'\(([^)]*)\)', statement)
        if not param_match:
            return []
        
        params = []
        param_text = param_match.group(1)
        
        if param_text.strip():
            for param in param_text.split(','):
                param = param.strip()
                if param:
                    params.append({
                        'name': param.split()[0] if param.split() else 'param',
                        'type': param.split()[1] if len(param.split()) > 1 else 'unknown',
                        'description': 'Parámetro del procedimiento'
                    })
        
        return params
    
    def _extract_function_parameters(self, statement: str) -> List[Dict[str, str]]:
        """Extract parameters from function definition."""
        return self._extract_procedure_parameters(statement)
    
    def _extract_return_type(self, statement: str) -> str:
        """Extract return type from function definition."""
        return_match = re.search(r'RETURNS\s+(\w+)', statement, re.IGNORECASE)
        return return_match.group(1) if return_match else 'unknown'
    
    def _extract_trigger_event(self, statement: str) -> str:
        """Extract trigger event."""
        event_match = re.search(r'(BEFORE|AFTER)\s+(INSERT|UPDATE|DELETE)', statement, re.IGNORECASE)
        return event_match.group(0) if event_match else 'unknown'
    
    def _extract_trigger_table(self, statement: str) -> str:
        """Extract trigger table."""
        table_match = re.search(r'ON\s+(\w+)', statement, re.IGNORECASE)
        return table_match.group(1) if table_match else 'unknown'

    def _generate_html_documentation(self, db_doc: DatabaseDocumentation) -> str:
        """Generate HTML documentation."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación de Base de Datos - {db_doc.database_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .table-section {{ margin-bottom: 3rem; }}
        .column-type {{ font-family: 'Courier New', monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }}
        .constraint-badge {{ font-size: 0.8em; }}
        .business-rule {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: 10px; margin: 5px 0; }}
        .toc {{ position: sticky; top: 20px; }}
        .relationship-arrow {{ color: #007bff; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Table of Contents -->
            <div class="col-md-3">
                <div class="toc">
                    <h5><i class="fas fa-list me-2"></i>Contenido</h5>
                    <ul class="list-unstyled">
                        <li><a href="#overview" class="text-decoration-none">Resumen General</a></li>
                        {self._generate_toc_tables(db_doc.tables)}
                        {self._generate_toc_views(db_doc.views)}
                        {self._generate_toc_procedures(db_doc.procedures)}
                    </ul>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9">
                <!-- Header -->
                <div class="mb-5">
                    <h1><i class="fas fa-database me-3"></i>{db_doc.database_name}</h1>
                    <p class="lead">Documentación técnica generada automáticamente</p>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-primary">{len(db_doc.tables)}</h3>
                                    <small class="text-muted">Tablas</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-info">{sum(len(table.columns) for table in db_doc.tables)}</h3>
                                    <small class="text-muted">Columnas</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-success">{len(db_doc.views)}</h3>
                                    <small class="text-muted">Vistas</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-warning">{len(db_doc.procedures)}</h3>
                                    <small class="text-muted">Procedimientos</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <p class="text-muted mt-3">
                        <i class="fas fa-clock me-2"></i>Generado el {db_doc.generated_at.strftime('%d/%m/%Y a las %H:%M')}
                    </p>
                </div>

                <!-- Tables Documentation -->
                <section id="tables">
                    <h2><i class="fas fa-table me-2"></i>Tablas</h2>
                    {self._generate_tables_html(db_doc.tables)}
                </section>

                <!-- Views Documentation -->
                {self._generate_views_html(db_doc.views)}

                <!-- Procedures Documentation -->
                {self._generate_procedures_html(db_doc.procedures)}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        return html_content

    def _generate_toc_tables(self, tables: List[TableDocumentation]) -> str:
        """Generate table of contents for tables."""
        if not tables:
            return ""

        toc_html = "<li><strong>Tablas</strong><ul>"
        for table in tables:
            toc_html += f'<li><a href="#table-{table.name}" class="text-decoration-none">{table.name}</a></li>'
        toc_html += "</ul></li>"
        return toc_html

    def _generate_toc_views(self, views: List[Dict]) -> str:
        """Generate table of contents for views."""
        if not views:
            return ""

        toc_html = "<li><strong>Vistas</strong><ul>"
        for view in views:
            toc_html += f'<li><a href="#view-{view["name"]}" class="text-decoration-none">{view["name"]}</a></li>'
        toc_html += "</ul></li>"
        return toc_html

    def _generate_toc_procedures(self, procedures: List[Dict]) -> str:
        """Generate table of contents for procedures."""
        if not procedures:
            return ""

        toc_html = "<li><strong>Procedimientos</strong><ul>"
        for proc in procedures:
            toc_html += f'<li><a href="#proc-{proc["name"]}" class="text-decoration-none">{proc["name"]}</a></li>'
        toc_html += "</ul></li>"
        return toc_html

    def _generate_tables_html(self, tables: List[TableDocumentation]) -> str:
        """Generate HTML for tables documentation."""
        if not tables:
            return "<p>No se encontraron tablas en el esquema.</p>"

        tables_html = ""
        for table in tables:
            tables_html += f"""
            <div class="table-section" id="table-{table.name}">
                <div class="card">
                    <div class="card-header">
                        <h3><i class="fas fa-table me-2"></i>{table.name}</h3>
                        <p class="mb-0">{table.description}</p>
                    </div>
                    <div class="card-body">
                        <!-- Columns -->
                        <h5><i class="fas fa-columns me-2"></i>Columnas</h5>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Nombre</th>
                                        <th>Tipo</th>
                                        <th>Propiedades</th>
                                        <th>Descripción</th>
                                        <th>Significado de Negocio</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {self._generate_columns_html(table.columns)}
                                </tbody>
                            </table>
                        </div>

                        <!-- Constraints -->
                        {self._generate_constraints_html(table.constraints)}

                        <!-- Relationships -->
                        {self._generate_relationships_html(table.relationships)}

                        <!-- Business Rules -->
                        {self._generate_business_rules_html(table.business_rules)}
                    </div>
                </div>
            </div>
            """

        return tables_html

    def _generate_columns_html(self, columns: List[Dict]) -> str:
        """Generate HTML for table columns."""
        columns_html = ""

        for column in columns:
            # Build type string
            type_str = column['type']
            if column.get('size'):
                type_str += f"({column['size']})"
            elif column.get('precision') and column.get('scale'):
                type_str += f"({column['precision']},{column['scale']})"

            # Build properties badges
            properties = []
            if column.get('primary_key'):
                properties.append('<span class="badge bg-warning constraint-badge">PK</span>')
            if not column.get('nullable'):
                properties.append('<span class="badge bg-danger constraint-badge">NOT NULL</span>')
            if column.get('unique'):
                properties.append('<span class="badge bg-info constraint-badge">UNIQUE</span>')
            if column.get('auto_increment'):
                properties.append('<span class="badge bg-success constraint-badge">AUTO</span>')
            if column.get('default'):
                properties.append(f'<span class="badge bg-secondary constraint-badge">DEFAULT: {column["default"]}</span>')

            columns_html += f"""
            <tr>
                <td><strong>{column['name']}</strong></td>
                <td><span class="column-type">{type_str}</span></td>
                <td>{' '.join(properties)}</td>
                <td>{column.get('description', '')}</td>
                <td>{column.get('business_meaning', '')}</td>
            </tr>
            """

        return columns_html

    def _generate_constraints_html(self, constraints: List[Dict]) -> str:
        """Generate HTML for table constraints."""
        if not constraints:
            return ""

        constraints_html = """
        <h5><i class="fas fa-lock me-2"></i>Restricciones</h5>
        <div class="row">
        """

        for constraint in constraints:
            icon = {
                'PRIMARY KEY': 'fas fa-key text-warning',
                'FOREIGN KEY': 'fas fa-link text-info',
                'CHECK': 'fas fa-check-circle text-success',
                'UNIQUE': 'fas fa-fingerprint text-primary'
            }.get(constraint['type'], 'fas fa-shield-alt')

            constraints_html += f"""
            <div class="col-md-6 mb-2">
                <div class="card">
                    <div class="card-body py-2">
                        <h6><i class="{icon} me-2"></i>{constraint['type']}</h6>
                        <small>{constraint.get('description', '')}</small>
                    </div>
                </div>
            </div>
            """

        constraints_html += "</div>"
        return constraints_html

    def _generate_relationships_html(self, relationships: List[Dict]) -> str:
        """Generate HTML for table relationships."""
        if not relationships:
            return ""

        relationships_html = """
        <h5><i class="fas fa-project-diagram me-2"></i>Relaciones</h5>
        <div class="list-group">
        """

        for rel in relationships:
            relationships_html += f"""
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">
                        <i class="fas fa-arrow-right relationship-arrow me-2"></i>
                        {rel.get('related_table', 'N/A')}
                    </h6>
                    <small>{rel.get('cardinality', 'N/A')}</small>
                </div>
                <p class="mb-1">{rel.get('description', '')}</p>
                <small>Columnas: {', '.join(rel.get('local_columns', []))}</small>
            </div>
            """

        relationships_html += "</div>"
        return relationships_html

    def _generate_business_rules_html(self, business_rules: List[str]) -> str:
        """Generate HTML for business rules."""
        if not business_rules:
            return ""

        rules_html = """
        <h5><i class="fas fa-business-time me-2"></i>Reglas de Negocio</h5>
        """

        for rule in business_rules:
            rules_html += f'<div class="business-rule">{rule}</div>'

        return rules_html

    def _generate_views_html(self, views: List[Dict]) -> str:
        """Generate HTML for views documentation."""
        if not views:
            return ""

        views_html = """
        <section id="views" class="mt-5">
            <h2><i class="fas fa-eye me-2"></i>Vistas</h2>
        """

        for view in views:
            views_html += f"""
            <div class="card mb-3" id="view-{view['name']}">
                <div class="card-header">
                    <h4>{view['name']}</h4>
                    <p class="mb-0">{view.get('description', '')}</p>
                </div>
                <div class="card-body">
                    <h6>Dependencias:</h6>
                    <p>{', '.join(view.get('dependencies', []))}</p>
                    <h6>Definición:</h6>
                    <pre class="bg-light p-3 rounded"><code>{view.get('definition', '')}</code></pre>
                </div>
            </div>
            """

        views_html += "</section>"
        return views_html

    def _generate_procedures_html(self, procedures: List[Dict]) -> str:
        """Generate HTML for procedures documentation."""
        if not procedures:
            return ""

        procedures_html = """
        <section id="procedures" class="mt-5">
            <h2><i class="fas fa-cogs me-2"></i>Procedimientos</h2>
        """

        for proc in procedures:
            procedures_html += f"""
            <div class="card mb-3" id="proc-{proc['name']}">
                <div class="card-header">
                    <h4>{proc['name']}</h4>
                    <p class="mb-0">{proc.get('description', '')}</p>
                </div>
                <div class="card-body">
                    <h6>Parámetros:</h6>
                    <ul>
                        {self._generate_parameters_html(proc.get('parameters', []))}
                    </ul>
                    <h6>Definición:</h6>
                    <pre class="bg-light p-3 rounded"><code>{proc.get('definition', '')}</code></pre>
                </div>
            </div>
            """

        procedures_html += "</section>"
        return procedures_html

    def _generate_parameters_html(self, parameters: List[Dict]) -> str:
        """Generate HTML for procedure parameters."""
        if not parameters:
            return "<li>Sin parámetros</li>"

        params_html = ""
        for param in parameters:
            params_html += f"""
            <li>
                <strong>{param.get('name', 'N/A')}</strong>
                <span class="column-type">{param.get('type', 'N/A')}</span>
                - {param.get('description', '')}
            </li>
            """

        return params_html

    def _generate_markdown_documentation(self, db_doc: DatabaseDocumentation) -> str:
        """Generate Markdown documentation."""
        markdown_content = f"""# Documentación de Base de Datos - {db_doc.database_name}

*Documentación técnica generada automáticamente el {db_doc.generated_at.strftime('%d/%m/%Y a las %H:%M')}*

## Resumen General

- **Tablas**: {len(db_doc.tables)}
- **Columnas**: {sum(len(table.columns) for table in db_doc.tables)}
- **Vistas**: {len(db_doc.views)}
- **Procedimientos**: {len(db_doc.procedures)}

## Tablas

{self._generate_tables_markdown(db_doc.tables)}

## Vistas

{self._generate_views_markdown(db_doc.views)}

## Procedimientos

{self._generate_procedures_markdown(db_doc.procedures)}
"""
        return markdown_content

    def _generate_tables_markdown(self, tables: List[TableDocumentation]) -> str:
        """Generate Markdown for tables."""
        if not tables:
            return "No se encontraron tablas en el esquema."

        markdown = ""
        for table in tables:
            markdown += f"""
### {table.name}

{table.description}

#### Columnas

| Nombre | Tipo | Propiedades | Descripción |
|--------|------|-------------|-------------|
"""

            for column in table.columns:
                type_str = column['type']
                if column.get('size'):
                    type_str += f"({column['size']})"

                properties = []
                if column.get('primary_key'):
                    properties.append('PK')
                if not column.get('nullable'):
                    properties.append('NOT NULL')
                if column.get('unique'):
                    properties.append('UNIQUE')
                if column.get('auto_increment'):
                    properties.append('AUTO')

                markdown += f"| {column['name']} | `{type_str}` | {', '.join(properties)} | {column.get('description', '')} |\n"

            if table.business_rules:
                markdown += "\n#### Reglas de Negocio\n\n"
                for rule in table.business_rules:
                    markdown += f"- {rule}\n"

            markdown += "\n"

        return markdown

    def _generate_views_markdown(self, views: List[Dict]) -> str:
        """Generate Markdown for views."""
        if not views:
            return "No se encontraron vistas en el esquema."

        markdown = ""
        for view in views:
            markdown += f"""
### {view['name']}

{view.get('description', '')}

**Dependencias**: {', '.join(view.get('dependencies', []))}

```sql
{view.get('definition', '')}
```

"""
        return markdown

    def _generate_procedures_markdown(self, procedures: List[Dict]) -> str:
        """Generate Markdown for procedures."""
        if not procedures:
            return "No se encontraron procedimientos en el esquema."

        markdown = ""
        for proc in procedures:
            markdown += f"""
### {proc['name']}

{proc.get('description', '')}

#### Parámetros

"""
            if proc.get('parameters'):
                for param in proc['parameters']:
                    markdown += f"- **{param.get('name', 'N/A')}** (`{param.get('type', 'N/A')}`) - {param.get('description', '')}\n"
            else:
                markdown += "Sin parámetros\n"

            markdown += f"""
```sql
{proc.get('definition', '')}
```

"""
        return markdown

    def _generate_pdf_documentation(self, db_doc: DatabaseDocumentation) -> str:
        """Generate PDF documentation (placeholder - would need additional libraries)."""
        # This would require libraries like reportlab or weasyprint
        # For now, return HTML that can be converted to PDF
        return self._generate_html_documentation(db_doc)

    def _load_table_descriptions(self) -> Dict[str, str]:
        """Load table naming patterns and descriptions."""
        return {
            'user': "Gestiona información de usuarios del sistema",
            'cliente': "Almacena datos de clientes y contactos",
            'producto': "Catálogo de productos y servicios disponibles",
            'pedido': "Registra pedidos y órdenes de compra",
            'factura': "Almacena información de facturación y cobros",
            'pago': "Registra transacciones y métodos de pago",
            'categoria': "Sistema de clasificación y categorización",
            'inventario': "Control de stock y existencias",
            'empleado': "Información del personal y recursos humanos",
            'proveedor': "Datos de proveedores y suministradores",
            'direccion': "Direcciones y ubicaciones geográficas",
            'telefono': "Números telefónicos y contactos",
            'email': "Direcciones de correo electrónico",
            'config': "Configuración y parámetros del sistema",
            'log': "Registro de eventos y actividades",
            'audit': "Auditoría y seguimiento de cambios",
            'session': "Gestión de sesiones de usuario",
            'role': "Roles y permisos del sistema",
            'permission': "Permisos específicos y autorizaciones"
        }

    def _load_column_descriptions(self) -> Dict[str, str]:
        """Load column naming patterns and descriptions."""
        return {
            'id': "Identificador único de tipo {type}",
            'name': "Nombre descriptivo de tipo {type}",
            'nombre': "Nombre descriptivo de tipo {type}",
            'email': "Dirección de correo electrónico de tipo {type}",
            'correo': "Dirección de correo electrónico de tipo {type}",
            'password': "Contraseña encriptada de tipo {type}",
            'contraseña': "Contraseña encriptada de tipo {type}",
            'phone': "Número telefónico de tipo {type}",
            'telefono': "Número telefónico de tipo {type}",
            'address': "Dirección física de tipo {type}",
            'direccion': "Dirección física de tipo {type}",
            'date': "Fecha de tipo {type}",
            'fecha': "Fecha de tipo {type}",
            'created': "Fecha de creación de tipo {type}",
            'updated': "Fecha de última actualización de tipo {type}",
            'status': "Estado o condición de tipo {type}",
            'estado': "Estado o condición de tipo {type}",
            'active': "Indicador de actividad de tipo {type}",
            'activo': "Indicador de actividad de tipo {type}",
            'price': "Precio monetario de tipo {type}",
            'precio': "Precio monetario de tipo {type}",
            'amount': "Cantidad o monto de tipo {type}",
            'cantidad': "Cantidad o monto de tipo {type}",
            'description': "Descripción detallada de tipo {type}",
            'descripcion': "Descripción detallada de tipo {type}"
        }
