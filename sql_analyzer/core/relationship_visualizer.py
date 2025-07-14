"""
Database Relationship Visualizer

Generates interactive relationship diagrams showing table relationships,
foreign keys, and database structure using D3.js and other visualization libraries.
"""

import re
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import sqlparse

logger = logging.getLogger(__name__)


@dataclass
class TableNode:
    """Represents a table node in the relationship diagram."""
    id: str
    name: str
    columns: List[Dict[str, Any]]
    x: float = 0
    y: float = 0
    width: float = 200
    height: float = 100
    color: str = "#e3f2fd"


@dataclass
class Relationship:
    """Represents a relationship between tables."""
    id: str
    source_table: str
    target_table: str
    source_column: str
    target_column: str
    relationship_type: str  # 'one-to-one', 'one-to-many', 'many-to-many'
    cardinality: str
    description: str


@dataclass
class DiagramData:
    """Complete diagram data structure."""
    nodes: List[TableNode]
    relationships: List[Relationship]
    metadata: Dict[str, Any]


class RelationshipVisualizer:
    """Generates interactive database relationship diagrams."""
    
    def __init__(self):
        self.tables = {}
        self.relationships = []
        
    def generate_diagram(self, sql_content: str, diagram_type: str = "interactive") -> Dict:
        """
        Generate relationship diagram from SQL schema.
        
        Args:
            sql_content: SQL schema content
            diagram_type: Type of diagram ('interactive', 'static', 'svg')
            
        Returns:
            Dict with diagram data and visualization code
        """
        try:
            # Parse SQL schema
            diagram_data = self._parse_schema_for_diagram(sql_content)
            
            # Generate visualization based on type
            if diagram_type == "interactive":
                result = self._generate_interactive_diagram(diagram_data)
            elif diagram_type == "svg":
                result = self._generate_svg_diagram(diagram_data)
            elif diagram_type == "static":
                result = self._generate_static_diagram(diagram_data)
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")
            
            return {
                'success': True,
                'diagram_html': result['html'],
                'diagram_data': result['data'],
                'tables_count': len(diagram_data.nodes),
                'relationships_count': len(diagram_data.relationships),
                'diagram_type': diagram_type
            }
            
        except Exception as e:
            logger.error(f"Error generating relationship diagram: {e}")
            return {
                'success': False,
                'error': str(e),
                'diagram_html': '',
                'diagram_data': {}
            }
    
    def _parse_schema_for_diagram(self, sql_content: str) -> DiagramData:
        """Parse SQL schema and extract relationship information."""
        parsed = sqlparse.parse(sql_content)
        
        nodes = []
        relationships = []
        table_info = {}
        
        # First pass: extract tables and columns
        for statement in parsed:
            statement_str = str(statement).strip()
            if statement_str.upper().startswith('CREATE TABLE'):
                table_data = self._parse_table_for_diagram(statement_str)
                if table_data:
                    table_info[table_data['name']] = table_data
        
        # Second pass: extract relationships
        relationship_id = 1
        for table_name, table_data in table_info.items():
            for fk in table_data.get('foreign_keys', []):
                relationships.append(Relationship(
                    id=f"rel_{relationship_id}",
                    source_table=table_name,
                    target_table=fk['referenced_table'],
                    source_column=fk['column'],
                    target_column=fk['referenced_column'],
                    relationship_type='many-to-one',
                    cardinality='N:1',
                    description=f"{table_name}.{fk['column']} → {fk['referenced_table']}.{fk['referenced_column']}"
                ))
                relationship_id += 1
        
        # Create table nodes
        for i, (table_name, table_data) in enumerate(table_info.items()):
            # Calculate position in a grid layout
            cols = 3
            x = (i % cols) * 250 + 50
            y = (i // cols) * 200 + 50
            
            nodes.append(TableNode(
                id=table_name,
                name=table_name,
                columns=table_data.get('columns', []),
                x=x,
                y=y,
                color=self._get_table_color(table_name)
            ))
        
        return DiagramData(
            nodes=nodes,
            relationships=relationships,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'total_tables': len(nodes),
                'total_relationships': len(relationships)
            }
        )
    
    def _parse_table_for_diagram(self, statement: str) -> Optional[Dict]:
        """Parse CREATE TABLE statement for diagram data."""
        try:
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement, re.IGNORECASE)
            if not table_match:
                return None
            
            table_name = table_match.group(1)
            
            # Parse columns
            columns = []
            foreign_keys = []
            
            # Find column definitions
            paren_content = re.search(r'\((.*)\)', statement, re.DOTALL)
            if paren_content:
                column_defs = paren_content.group(1)
                column_lines = self._split_column_definitions(column_defs)
                
                for line in column_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check for foreign key
                    fk_match = re.search(r'FOREIGN\s+KEY\s*\(\s*(\w+)\s*\)\s+REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', line, re.IGNORECASE)
                    if fk_match:
                        foreign_keys.append({
                            'column': fk_match.group(1),
                            'referenced_table': fk_match.group(2),
                            'referenced_column': fk_match.group(3)
                        })
                        continue
                    
                    # Parse column
                    col_match = re.match(r'^(\w+)\s+(VARCHAR|INT|INTEGER|TEXT|DATETIME|TIMESTAMP|BOOLEAN|DECIMAL|FLOAT)(\([^)]+\))?', line, re.IGNORECASE)
                    if col_match:
                        column_name = col_match.group(1)
                        data_type = col_match.group(2).upper()
                        size_info = col_match.group(3) or ""
                        
                        is_primary_key = 'PRIMARY KEY' in line.upper()
                        is_nullable = 'NOT NULL' not in line.upper()
                        is_unique = 'UNIQUE' in line.upper()
                        
                        columns.append({
                            'name': column_name,
                            'type': data_type + size_info,
                            'primary_key': is_primary_key,
                            'nullable': is_nullable,
                            'unique': is_unique
                        })
            
            return {
                'name': table_name,
                'columns': columns,
                'foreign_keys': foreign_keys
            }
            
        except Exception as e:
            logger.error(f"Error parsing table for diagram: {e}")
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
    
    def _get_table_color(self, table_name: str) -> str:
        """Get color for table based on naming patterns."""
        table_lower = table_name.lower()
        
        color_patterns = {
            'user': '#e8f5e8',      # Light green
            'cliente': '#e8f5e8',
            'producto': '#fff3e0',   # Light orange
            'pedido': '#e3f2fd',     # Light blue
            'orden': '#e3f2fd',
            'factura': '#fce4ec',    # Light pink
            'pago': '#f3e5f5',       # Light purple
            'categoria': '#fff8e1',  # Light yellow
            'inventario': '#e0f2f1', # Light teal
            'config': '#f5f5f5',     # Light gray
            'log': '#efebe9',        # Light brown
            'audit': '#efebe9'
        }
        
        for pattern, color in color_patterns.items():
            if pattern in table_lower:
                return color
        
        return '#e3f2fd'  # Default light blue
    
    def _generate_interactive_diagram(self, diagram_data: DiagramData) -> Dict:
        """Generate interactive D3.js diagram."""
        # Convert data to JSON for JavaScript
        nodes_json = json.dumps([{
            'id': node.id,
            'name': node.name,
            'columns': node.columns,
            'x': node.x,
            'y': node.y,
            'width': node.width,
            'height': node.height,
            'color': node.color
        } for node in diagram_data.nodes])
        
        relationships_json = json.dumps([{
            'id': rel.id,
            'source': rel.source_table,
            'target': rel.target_table,
            'sourceColumn': rel.source_column,
            'targetColumn': rel.target_column,
            'type': rel.relationship_type,
            'cardinality': rel.cardinality,
            'description': rel.description
        } for rel in diagram_data.relationships])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diagrama de Relaciones - Base de Datos</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        #diagram-container {{
            width: 100%;
            height: 80vh;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background-color: white;
            position: relative;
            overflow: hidden;
        }}
        
        .table-node {{
            cursor: move;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
        }}
        
        .table-header {{
            font-weight: bold;
            font-size: 14px;
            fill: #333;
        }}
        
        .column-text {{
            font-size: 12px;
            fill: #666;
        }}
        
        .primary-key {{
            fill: #d4a574;
            font-weight: bold;
        }}
        
        .relationship-line {{
            stroke: #007bff;
            stroke-width: 2;
            fill: none;
            marker-end: url(#arrowhead);
        }}
        
        .relationship-label {{
            font-size: 10px;
            fill: #666;
            text-anchor: middle;
        }}
        
        .controls {{
            margin-bottom: 20px;
        }}
        
        .btn {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }}
        
        .btn:hover {{
            background-color: #0056b3;
        }}
        
        .info-panel {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>Diagrama de Relaciones de Base de Datos</h1>
    
    <div class="controls">
        <button class="btn" onclick="resetZoom()">Restablecer Vista</button>
        <button class="btn" onclick="autoLayout()">Auto Organizar</button>
        <button class="btn" onclick="exportSVG()">Exportar SVG</button>
    </div>
    
    <div id="diagram-container">
        <div class="info-panel">
            <div>Tablas: {len(diagram_data.nodes)}</div>
            <div>Relaciones: {len(diagram_data.relationships)}</div>
        </div>
    </div>

    <script>
        // Data
        const nodes = {nodes_json};
        const relationships = {relationships_json};
        
        // SVG setup
        const container = d3.select("#diagram-container");
        const svg = container.append("svg")
            .attr("width", "100%")
            .attr("height", "100%");
        
        // Define arrowhead marker
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 8)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#007bff");
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        const g = svg.append("g");
        
        // Draw relationships first (so they appear behind tables)
        const relationshipGroup = g.append("g").attr("class", "relationships");
        
        relationships.forEach(rel => {{
            const sourceNode = nodes.find(n => n.id === rel.source);
            const targetNode = nodes.find(n => n.id === rel.target);
            
            if (sourceNode && targetNode) {{
                const line = relationshipGroup.append("line")
                    .attr("class", "relationship-line")
                    .attr("x1", sourceNode.x + sourceNode.width/2)
                    .attr("y1", sourceNode.y + sourceNode.height/2)
                    .attr("x2", targetNode.x + targetNode.width/2)
                    .attr("y2", targetNode.y + targetNode.height/2);
                
                // Add relationship label
                const midX = (sourceNode.x + targetNode.x + sourceNode.width/2 + targetNode.width/2) / 2;
                const midY = (sourceNode.y + targetNode.y + sourceNode.height/2 + targetNode.height/2) / 2;
                
                relationshipGroup.append("text")
                    .attr("class", "relationship-label")
                    .attr("x", midX)
                    .attr("y", midY - 5)
                    .text(rel.cardinality);
            }}
        }});
        
        // Draw tables
        const tableGroup = g.append("g").attr("class", "tables");
        
        nodes.forEach(node => {{
            const tableNode = tableGroup.append("g")
                .attr("class", "table-node")
                .attr("transform", `translate(${{node.x}}, ${{node.y}})`);
            
            // Table background
            tableNode.append("rect")
                .attr("width", node.width)
                .attr("height", node.height)
                .attr("fill", node.color)
                .attr("stroke", "#333")
                .attr("stroke-width", 1)
                .attr("rx", 4);
            
            // Table header
            tableNode.append("rect")
                .attr("width", node.width)
                .attr("height", 25)
                .attr("fill", "#333")
                .attr("rx", 4);
            
            tableNode.append("text")
                .attr("class", "table-header")
                .attr("x", node.width/2)
                .attr("y", 17)
                .attr("text-anchor", "middle")
                .attr("fill", "white")
                .text(node.name);
            
            // Columns
            node.columns.forEach((column, i) => {{
                const y = 40 + i * 16;
                const text = tableNode.append("text")
                    .attr("class", column.primary_key ? "column-text primary-key" : "column-text")
                    .attr("x", 8)
                    .attr("y", y)
                    .text(`${{column.name}} : ${{column.type}}`);
                
                if (column.primary_key) {{
                    tableNode.append("text")
                        .attr("class", "column-text")
                        .attr("x", node.width - 20)
                        .attr("y", y)
                        .attr("text-anchor", "middle")
                        .attr("fill", "#d4a574")
                        .text("🔑");
                }}
            }});
            
            // Make tables draggable
            tableNode.call(d3.drag()
                .on("drag", (event) => {{
                    node.x = event.x;
                    node.y = event.y;
                    tableNode.attr("transform", `translate(${{node.x}}, ${{node.y}})`);
                    updateRelationships();
                }})
            );
        }});
        
        function updateRelationships() {{
            relationshipGroup.selectAll("line")
                .each(function(d, i) {{
                    const rel = relationships[i];
                    const sourceNode = nodes.find(n => n.id === rel.source);
                    const targetNode = nodes.find(n => n.id === rel.target);
                    
                    if (sourceNode && targetNode) {{
                        d3.select(this)
                            .attr("x1", sourceNode.x + sourceNode.width/2)
                            .attr("y1", sourceNode.y + sourceNode.height/2)
                            .attr("x2", targetNode.x + targetNode.width/2)
                            .attr("y2", targetNode.y + targetNode.height/2);
                    }}
                }});
            
            relationshipGroup.selectAll(".relationship-label")
                .each(function(d, i) {{
                    const rel = relationships[i];
                    const sourceNode = nodes.find(n => n.id === rel.source);
                    const targetNode = nodes.find(n => n.id === rel.target);
                    
                    if (sourceNode && targetNode) {{
                        const midX = (sourceNode.x + targetNode.x + sourceNode.width/2 + targetNode.width/2) / 2;
                        const midY = (sourceNode.y + targetNode.y + sourceNode.height/2 + targetNode.height/2) / 2;
                        
                        d3.select(this)
                            .attr("x", midX)
                            .attr("y", midY - 5);
                    }}
                }});
        }}
        
        function resetZoom() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}
        
        function autoLayout() {{
            // Simple grid layout
            const cols = Math.ceil(Math.sqrt(nodes.length));
            nodes.forEach((node, i) => {{
                node.x = (i % cols) * 250 + 50;
                node.y = Math.floor(i / cols) * 200 + 50;
                
                tableGroup.select(`g:nth-child(${{i + 1}})`)
                    .transition()
                    .duration(1000)
                    .attr("transform", `translate(${{node.x}}, ${{node.y}})`);
            }});
            
            setTimeout(updateRelationships, 100);
        }}
        
        function exportSVG() {{
            const svgData = new XMLSerializer().serializeToString(svg.node());
            const blob = new Blob([svgData], {{type: "image/svg+xml"}});
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement("a");
            link.href = url;
            link.download = "database_diagram.svg";
            link.click();
            
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
        """
        
        return {
            'html': html_content,
            'data': {
                'nodes': nodes_json,
                'relationships': relationships_json
            }
        }

    def _generate_svg_diagram(self, diagram_data: DiagramData) -> Dict:
        """Generate static SVG diagram."""
        # Calculate diagram dimensions
        max_x = max([node.x + node.width for node in diagram_data.nodes]) if diagram_data.nodes else 400
        max_y = max([node.y + node.height for node in diagram_data.nodes]) if diagram_data.nodes else 300

        svg_width = max_x + 50
        svg_height = max_y + 50

        svg_content = f"""
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrowhead" viewBox="0 -5 10 10" refX="8" refY="0"
                markerWidth="6" markerHeight="6" orient="auto" fill="#007bff">
            <path d="M0,-5L10,0L0,5"/>
        </marker>
        <style>
            .table-header {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: white; }}
            .column-text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #333; }}
            .primary-key {{ fill: #d4a574; font-weight: bold; }}
            .relationship-line {{ stroke: #007bff; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
            .relationship-label {{ font-family: Arial, sans-serif; font-size: 10px; fill: #666; text-anchor: middle; }}
        </style>
    </defs>

    <!-- Relationships -->
    <g class="relationships">
        {self._generate_svg_relationships(diagram_data)}
    </g>

    <!-- Tables -->
    <g class="tables">
        {self._generate_svg_tables(diagram_data.nodes)}
    </g>
</svg>
        """

        return {
            'html': f'<div style="text-align: center; padding: 20px;">{svg_content}</div>',
            'data': {'svg': svg_content}
        }

    def _generate_svg_relationships(self, diagram_data: DiagramData) -> str:
        """Generate SVG for relationships."""
        svg_relationships = ""

        for rel in diagram_data.relationships:
            source_node = next((n for n in diagram_data.nodes if n.id == rel.source_table), None)
            target_node = next((n for n in diagram_data.nodes if n.id == rel.target_table), None)

            if source_node and target_node:
                x1 = source_node.x + source_node.width / 2
                y1 = source_node.y + source_node.height / 2
                x2 = target_node.x + target_node.width / 2
                y2 = target_node.y + target_node.height / 2

                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                svg_relationships += f"""
        <line class="relationship-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>
        <text class="relationship-label" x="{mid_x}" y="{mid_y - 5}">{rel.cardinality}</text>
                """

        return svg_relationships

    def _generate_svg_tables(self, nodes: List[TableNode]) -> str:
        """Generate SVG for table nodes."""
        svg_tables = ""

        for node in nodes:
            # Calculate table height based on columns
            table_height = 30 + len(node.columns) * 18

            svg_tables += f"""
        <g transform="translate({node.x}, {node.y})">
            <!-- Table background -->
            <rect width="{node.width}" height="{table_height}" fill="{node.color}"
                  stroke="#333" stroke-width="1" rx="4"/>

            <!-- Table header -->
            <rect width="{node.width}" height="25" fill="#333" rx="4"/>
            <text class="table-header" x="{node.width/2}" y="17" text-anchor="middle">{node.name}</text>

            <!-- Columns -->
            {self._generate_svg_columns(node.columns, node.width)}
        </g>
            """

        return svg_tables

    def _generate_svg_columns(self, columns: List[Dict], table_width: float) -> str:
        """Generate SVG for table columns."""
        svg_columns = ""

        for i, column in enumerate(columns):
            y = 40 + i * 16
            column_class = "column-text primary-key" if column.get('primary_key') else "column-text"

            svg_columns += f"""
            <text class="{column_class}" x="8" y="{y}">{column['name']} : {column['type']}</text>
            """

            if column.get('primary_key'):
                svg_columns += f"""
            <text class="column-text" x="{table_width - 20}" y="{y}" text-anchor="middle" fill="#d4a574">🔑</text>
                """

        return svg_columns

    def _generate_static_diagram(self, diagram_data: DiagramData) -> Dict:
        """Generate static HTML diagram."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diagrama de Relaciones - Estático</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}

        .diagram-container {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }}

        .tables-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .table-card {{
            border: 1px solid #333;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .table-header {{
            background-color: #333;
            color: white;
            padding: 10px;
            font-weight: bold;
            text-align: center;
        }}

        .table-body {{
            padding: 10px;
        }}

        .column-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            border-bottom: 1px solid #eee;
        }}

        .column-row:last-child {{
            border-bottom: none;
        }}

        .column-name {{
            font-weight: 500;
        }}

        .column-type {{
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        .primary-key {{
            color: #d4a574;
        }}

        .relationships-section {{
            margin-top: 30px;
        }}

        .relationship-item {{
            background: #e3f2fd;
            border-left: 4px solid #007bff;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }}

        .relationship-arrow {{
            color: #007bff;
            font-weight: bold;
        }}

        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            flex: 1;
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>Diagrama de Relaciones de Base de Datos</h1>

    <div class="diagram-container">
        <!-- Statistics -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(diagram_data.nodes)}</div>
                <div class="stat-label">Tablas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(len(node.columns) for node in diagram_data.nodes)}</div>
                <div class="stat-label">Columnas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(diagram_data.relationships)}</div>
                <div class="stat-label">Relaciones</div>
            </div>
        </div>

        <!-- Tables -->
        <h2>Tablas</h2>
        <div class="tables-grid">
            {self._generate_static_tables(diagram_data.nodes)}
        </div>

        <!-- Relationships -->
        {self._generate_static_relationships(diagram_data.relationships)}
    </div>
</body>
</html>
        """

        return {
            'html': html_content,
            'data': {'static': True}
        }

    def _generate_static_tables(self, nodes: List[TableNode]) -> str:
        """Generate static HTML for tables."""
        tables_html = ""

        for node in nodes:
            tables_html += f"""
            <div class="table-card" style="background-color: {node.color};">
                <div class="table-header">{node.name}</div>
                <div class="table-body">
                    {self._generate_static_columns(node.columns)}
                </div>
            </div>
            """

        return tables_html

    def _generate_static_columns(self, columns: List[Dict]) -> str:
        """Generate static HTML for columns."""
        columns_html = ""

        for column in columns:
            pk_class = "primary-key" if column.get('primary_key') else ""
            pk_icon = "🔑 " if column.get('primary_key') else ""

            columns_html += f"""
            <div class="column-row">
                <span class="column-name {pk_class}">{pk_icon}{column['name']}</span>
                <span class="column-type">{column['type']}</span>
            </div>
            """

        return columns_html

    def _generate_static_relationships(self, relationships: List[Relationship]) -> str:
        """Generate static HTML for relationships."""
        if not relationships:
            return ""

        relationships_html = """
        <div class="relationships-section">
            <h2>Relaciones</h2>
        """

        for rel in relationships:
            relationships_html += f"""
            <div class="relationship-item">
                <strong>{rel.source_table}</strong>
                <span class="relationship-arrow"> → </span>
                <strong>{rel.target_table}</strong>
                <br>
                <small>{rel.description} ({rel.cardinality})</small>
            </div>
            """

        relationships_html += "</div>"
        return relationships_html
