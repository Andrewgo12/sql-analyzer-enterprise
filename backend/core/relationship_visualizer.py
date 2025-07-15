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

