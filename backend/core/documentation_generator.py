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

{view.get('description', '')}

**Dependencias**: {', '.join(view.get('dependencies', []))}

```sql
{view.get('definition', '')}
```

"""
        return markdown

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

