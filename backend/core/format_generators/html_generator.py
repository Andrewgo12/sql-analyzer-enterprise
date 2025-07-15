"""
HTML Report Generators

Generates comprehensive HTML reports with embedded CSS and interactive elements.
"""

import time
import json
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class HTMLReportGenerator(BaseFormatGenerator):
    """Generator for comprehensive HTML reports."""
    
    @property
    def format_name(self) -> str:
        return "Reporte HTML"
    
    @property
    def file_extension(self) -> str:
        return ".html"
    
    @property
    def mime_type(self) -> str:
        return "text/html"
    
    @property
    def is_binary(self) -> bool:
        return False
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate comprehensive HTML report."""
        start_time = time.time()
        
        try:
            self.validate_context(context)
            
            # Generate HTML content
            html_content = self._generate_html_report(context)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                html_content, context, generation_time,
                metadata={
                    "report_type": "comprehensive",
                    "includes_charts": True,
                    "interactive_elements": True
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
    def _generate_html_report(self, context: GenerationContext) -> str:
        """Generate the complete HTML report."""
        template_vars = self.get_template_variables(context)
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Análisis SQL - {template_vars['original_filename']}</title>
    {self._get_embedded_css()}
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        {self._generate_header(template_vars)}
        {self._generate_executive_summary(template_vars)}
        {self._generate_charts_section(template_vars)}
        {self._generate_errors_section(template_vars)}
        {self._generate_recommendations_section(template_vars)}
        {self._generate_technical_details(template_vars)}
        {self._generate_footer(template_vars)}
    </div>
    {self._get_embedded_javascript(template_vars)}
</body>
</html>"""
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .metric-label {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .error-item {
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #dc3545;
        }
        
        .error-item.high { border-left-color: #fd7e14; }
        .error-item.medium { border-left-color: #ffc107; }
        .error-item.low { border-left-color: #28a745; }
        
        .error-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .error-title {
            font-weight: bold;
            color: #495057;
        }
        
        .error-severity {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }
        
        .severity-critical { background-color: #dc3545; }
        .severity-high { background-color: #fd7e14; }
        .severity-medium { background-color: #ffc107; color: #212529; }
        .severity-low { background-color: #28a745; }
        
        .error-location {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 8px;
        }
        
        .error-description {
            color: #495057;
            margin-bottom: 10px;
        }
        
        .error-fixes {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #2196f3;
        }
        
        .fix-item {
            margin-bottom: 5px;
        }
        
        .confidence-bar {
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
            transition: width 0.3s ease;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        
        .recommendations {
            background: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .recommendation-item {
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .recommendation-icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .footer {
            text-align: center;
            color: #6c757d;
            padding: 20px;
            border-top: 1px solid #dee2e6;
            margin-top: 30px;
        }
        
        .code-block {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media print {
            body {
                background: white;
            }
            
            .section {
                box-shadow: none;
                border: 1px solid #dee2e6;
            }
            
            .chart-container {
                page-break-inside: avoid;
            }
        }
    </style>"""
    
    def _generate_header(self, template_vars: Dict[str, Any]) -> str:
        """Generate the report header."""
        return f"""
        <div class="header">
            <h1>📊 Reporte de Análisis SQL</h1>
            <div class="subtitle">
                Archivo: {template_vars['original_filename']} | 
                Fecha: {template_vars['analysis_timestamp'].strftime('%d/%m/%Y %H:%M:%S')}
            </div>
        </div>"""
    
    def _generate_executive_summary(self, template_vars: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        summary = template_vars['summary']
        
        return f"""
        <div class="section">
            <h2>📋 Resumen Ejecutivo</h2>
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value">{summary['total_errors']}</div>
                    <div class="metric-label">Errores Totales</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['quality_score']}%</div>
                    <div class="metric-label">Puntuación de Calidad</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['fixes_suggested']}</div>
                    <div class="metric-label">Correcciones Sugeridas</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{summary['lines_analyzed']}</div>
                    <div class="metric-label">Líneas Analizadas</div>
                </div>
            </div>
        </div>"""
    
    def _generate_errors_section(self, template_vars: Dict[str, Any]) -> str:
        """Generate errors section."""
        errors_html = []
        
        for error in template_vars['errors'][:20]:  # Limit to first 20 errors
            severity_class = error['severity'].lower()
            
            fixes_html = ""
            if error['fixes']:
                fixes_html = f"""
                <div class="error-fixes">
                    <strong>💡 Correcciones Sugeridas:</strong>
                    {self._generate_fixes_html(error['fixes'])}
                </div>"""
            
            errors_html.append(f"""
            <div class="error-item {severity_class}">
                <div class="error-header">
                    <div class="error-title">{error['title']}</div>
                    <span class="error-severity severity-{severity_class}">{error['severity_display']}</span>
                </div>
                <div class="error-location">📍 Línea {error['line']}, Columna {error['column']}</div>
                <div class="error-description">{error['description']}</div>
                {fixes_html}
            </div>""")
        
        return f"""
        <div class="section">
            <h2>🐛 Errores Detectados</h2>
            {''.join(errors_html)}
        </div>"""
    
    def _generate_recommendations_section(self, template_vars: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        summary = template_vars['summary']
        recommendations = []
        
        if summary['critical_errors'] > 0:
            recommendations.append(("🚨", "Corrija inmediatamente los errores críticos antes de usar este código en producción"))
        
        if summary['quality_score'] < 70:
            recommendations.append(("📈", "La puntuación de calidad es baja. Considere refactorizar el código"))
        
        if summary['fixes_suggested'] > 0:
            recommendations.append(("🔧", f"Se sugieren {summary['fixes_suggested']} correcciones automáticas"))
        
        recommendations.append(("📚", "Revise la documentación para mejores prácticas de SQL"))
        
        recommendations_html = ''.join([
            f'<div class="recommendation-item"><span class="recommendation-icon">{icon}</span><span>{text}</span></div>'
            for icon, text in recommendations
        ])
        
        return f"""
        <div class="section">
            <h2>💡 Recomendaciones</h2>
            <div class="recommendations">
                {recommendations_html}
            </div>
        </div>"""
    
    def _generate_technical_details(self, template_vars: Dict[str, Any]) -> str:
        """Generate technical details section."""
        return f"""
        <div class="section">
            <h2>🔧 Detalles Técnicos</h2>
            <p><strong>Generador:</strong> {template_vars['generator_name']} v{template_vars['generator_version']}</p>
            <p><strong>Sesión:</strong> {template_vars['session_id']}</p>
            <p><strong>Idioma:</strong> {template_vars['language']}</p>
            <p><strong>Archivo Original:</strong> {template_vars['original_filename']}</p>
        </div>"""
    
    def _generate_footer(self, template_vars: Dict[str, Any]) -> str:
        """Generate report footer."""
        return """
        <div class="footer">
            <p>Generado por SQL Analyzer Enterprise | © 2024 | Todos los derechos reservados</p>
        </div>"""
    
    def _get_embedded_javascript(self, template_vars: Dict[str, Any]) -> str:
        """Get embedded JavaScript for charts."""
        summary = template_vars['summary']
        categories = template_vars['categories']
        
        severity_data = {
            'critical': summary['critical_errors'],
            'high': summary['high_errors'],
            'medium': summary['medium_errors'],
            'low': summary['low_errors']
        }
        
        return f"""
    <script>
        // Severity Chart
        const severityCtx = document.getElementById('severityChart').getContext('2d');
        new Chart(severityCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Críticos', 'Altos', 'Medios', 'Bajos'],
                datasets: [{{
                    data: [{severity_data['critical']}, {severity_data['high']}, {severity_data['medium']}, {severity_data['low']}],
                    backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Distribución de Errores por Severidad'
                    }}
                }}
            }}
        }});
        
        // Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(categories.keys()))},
                datasets: [{{
                    label: 'Errores',
                    data: {json.dumps(list(categories.values()))},
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Errores por Categoría'
                    }}
                }}
            }}
        }});
    </script>"""


class InteractiveHTMLGenerator(HTMLReportGenerator):
    """Generator for interactive HTML dashboards with real-time charts."""
    
    @property
    def format_name(self) -> str:
        return "Dashboard HTML Interactivo"
    
