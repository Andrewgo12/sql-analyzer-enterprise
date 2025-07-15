"""
PDF Report Generator

Generates professional PDF reports using reportlab with charts and formatting.
"""

import time
import io
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult

# Optional imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, black, red, orange, yellow, green, blue
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus.flowables import Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Create dummy classes for when reportlab is not available
    class ParagraphStyle:
        def __init__(self, *args, **kwargs):
            pass

    class Drawing:
        def __init__(self, *args, **kwargs):
            pass

    class SimpleDocTemplate:
        def __init__(self, *args, **kwargs):
            pass
        def build(self, *args, **kwargs):
            pass

    class Paragraph:
        def __init__(self, *args, **kwargs):
            pass

    class Spacer:
        def __init__(self, *args, **kwargs):
            pass

    class Table:
        def __init__(self, *args, **kwargs):
            pass
        def setStyle(self, *args, **kwargs):
            pass

    class TableStyle:
        def __init__(self, *args, **kwargs):
            pass

    def getSampleStyleSheet():
        return {}

    # Dummy constants
    letter = (612, 792)
    inch = 72
    TA_CENTER = 1
    TA_LEFT = 0


class PDFReportGenerator(BaseFormatGenerator):
    """Generator for professional PDF reports."""
    
    @property
    def format_name(self) -> str:
        return "Reporte PDF"
    
    @property
    def file_extension(self) -> str:
        return ".pdf"
    
    @property
    def mime_type(self) -> str:
        return "application/pdf"
    
    @property
    def is_binary(self) -> bool:
        return True
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate professional PDF report."""
        start_time = time.time()
        
        try:
            if not REPORTLAB_AVAILABLE:
                raise Exception("ReportLab no está disponible. Instale con: pip install reportlab")
            
            self.validate_context(context)
            
            # Generate PDF content
            pdf_content = self._generate_pdf_report(context)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                pdf_content, context, generation_time,
                metadata={
                    "pages_generated": self._estimate_page_count(context),
                    "includes_charts": True,
                    "format": "PDF/A"
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
    def _generate_pdf_report(self, context: GenerationContext) -> bytes:
        """Generate the complete PDF report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Get template variables
        template_vars = self.get_template_variables(context)
        
        # Build story (content elements)
        story = []
        
        # Add title page
        story.extend(self._create_title_page(template_vars))
        story.append(PageBreak())
        
        # Add executive summary
        story.extend(self._create_executive_summary(template_vars))
        story.append(PageBreak())
        
        # Add charts
        story.extend(self._create_charts_section(template_vars))
        story.append(PageBreak())
        
        # Add detailed errors
        story.extend(self._create_errors_section(template_vars))
        
        # Add recommendations
        story.extend(self._create_recommendations_section(template_vars))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _get_styles(self) -> Dict[str, ParagraphStyle]:
        """Get custom paragraph styles."""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#667eea'),
                alignment=TA_CENTER
            ),
            'CustomHeading1': ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                textColor=colors.HexColor('#667eea'),
                borderWidth=1,
                borderColor=colors.HexColor('#e9ecef'),
                borderPadding=5
            ),
            'CustomHeading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#495057')
            ),
            'ErrorCritical': ParagraphStyle(
                'ErrorCritical',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.red,
                leftIndent=20
            ),
            'ErrorHigh': ParagraphStyle(
                'ErrorHigh',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.orange,
                leftIndent=20
            ),
            'ErrorMedium': ParagraphStyle(
                'ErrorMedium',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.Color(1, 0.8, 0),
                leftIndent=20
            ),
            'ErrorLow': ParagraphStyle(
                'ErrorLow',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.green,
                leftIndent=20
            )
        }
        
        return {**styles, **custom_styles}
    
    def _create_title_page(self, template_vars: Dict[str, Any]) -> List:
        """Create the title page."""
        styles = self._get_styles()
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("📊 Reporte de Análisis SQL", styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        story.append(Paragraph(f"Análisis Completo de {template_vars['original_filename']}", styles['Heading2']))
        story.append(Spacer(1, 1*inch))
        
        # Summary table
        summary = template_vars['summary']
        summary_data = [
            ['Métrica', 'Valor'],
            ['Archivo Analizado', template_vars['original_filename']],
            ['Fecha de Análisis', template_vars['analysis_timestamp'].strftime('%d/%m/%Y %H:%M:%S')],
            ['Total de Errores', str(summary['total_errors'])],
            ['Puntuación de Calidad', f"{summary['quality_score']}%"],
            ['Líneas Analizadas', str(summary['lines_analyzed'])],
            ['Correcciones Sugeridas', str(summary['fixes_suggested'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 1*inch))
        
        # Footer
        story.append(Paragraph("Generado por SQL Analyzer Enterprise", styles['Normal']))
        story.append(Paragraph(f"Sesión: {template_vars['session_id']}", styles['Normal']))
        
        return story
    
    def _create_executive_summary(self, template_vars: Dict[str, Any]) -> List:
        """Create executive summary section."""
        styles = self._get_styles()
        story = []
        summary = template_vars['summary']
        
        story.append(Paragraph("📋 Resumen Ejecutivo", styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        # Overview paragraph
        overview_text = f"""
        El análisis del archivo <b>{template_vars['original_filename']}</b> ha identificado 
        <b>{summary['total_errors']} errores</b> en total, con una puntuación de calidad de 
        <b>{summary['quality_score']}%</b>. Se han analizado <b>{summary['lines_analyzed']} líneas</b> 
        de código SQL y se sugieren <b>{summary['fixes_suggested']} correcciones</b> automáticas.
        """
        
        story.append(Paragraph(overview_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Severity breakdown
        story.append(Paragraph("Distribución de Errores por Severidad", styles['CustomHeading2']))
        
        severity_data = [
            ['Severidad', 'Cantidad', 'Porcentaje'],
            ['🚨 Críticos', str(summary['critical_errors']), f"{(summary['critical_errors']/max(1,summary['total_errors'])*100):.1f}%"],
            ['⚠️ Altos', str(summary['high_errors']), f"{(summary['high_errors']/max(1,summary['total_errors'])*100):.1f}%"],
            ['⚡ Medios', str(summary['medium_errors']), f"{(summary['medium_errors']/max(1,summary['total_errors'])*100):.1f}%"],
            ['ℹ️ Bajos', str(summary['low_errors']), f"{(summary['low_errors']/max(1,summary['total_errors'])*100):.1f}%"]
        ]
        
        severity_table = Table(severity_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(severity_table)
        story.append(Spacer(1, 20))
        
        # Key findings
        story.append(Paragraph("Hallazgos Clave", styles['CustomHeading2']))
        
        findings = []
        if summary['critical_errors'] > 0:
            findings.append(f"• Se encontraron {summary['critical_errors']} errores críticos que requieren atención inmediata")
        
        if summary['quality_score'] < 70:
            findings.append(f"• La puntuación de calidad ({summary['quality_score']}%) está por debajo del umbral recomendado (70%)")
        
        if summary['fixes_suggested'] > 0:
            findings.append(f"• {summary['fixes_suggested']} correcciones pueden aplicarse automáticamente")
        
        findings.append(f"• Se analizaron {summary['statements_analyzed']} declaraciones SQL")
        
        for finding in findings:
            story.append(Paragraph(finding, styles['Normal']))
        
        return story
    
    def _create_charts_section(self, template_vars: Dict[str, Any]) -> List:
        """Create charts section."""
        styles = self._get_styles()
        story = []
        summary = template_vars['summary']
        
        story.append(Paragraph("📈 Análisis Visual", styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        # Severity pie chart
        story.append(Paragraph("Distribución de Errores por Severidad", styles['CustomHeading2']))
        
        pie_chart = self._create_severity_pie_chart(summary)
        story.append(pie_chart)
        story.append(Spacer(1, 20))
        
        # Category bar chart
        story.append(Paragraph("Errores por Categoría", styles['CustomHeading2']))
        
        bar_chart = self._create_category_bar_chart(template_vars['categories'])
        story.append(bar_chart)
        
        return story
    
    def _create_severity_pie_chart(self, summary: Dict[str, Any]) -> Drawing:
        """Create a pie chart for error severity distribution."""
        drawing = Drawing(400, 200)
        
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        pie.data = [
            summary['critical_errors'],
            summary['high_errors'],
            summary['medium_errors'],
            summary['low_errors']
        ]
        
        pie.labels = ['Críticos', 'Altos', 'Medios', 'Bajos']
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.red
        pie.slices[1].fillColor = colors.orange
        pie.slices[2].fillColor = colors.yellow
        pie.slices[3].fillColor = colors.green
        
        drawing.add(pie)
        return drawing
    
    def _create_category_bar_chart(self, categories: Dict[str, int]) -> Drawing:
        """Create a bar chart for error categories."""
        drawing = Drawing(400, 200)
        
        if not categories:
            return drawing
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        
        chart.data = [list(categories.values())]
        chart.categoryAxis.categoryNames = list(categories.keys())
        chart.bars[0].fillColor = colors.HexColor('#667eea')
        
        drawing.add(chart)
        return drawing
    
    def _create_errors_section(self, template_vars: Dict[str, Any]) -> List:
        """Create detailed errors section."""
        styles = self._get_styles()
        story = []
        
        story.append(Paragraph("🐛 Errores Detectados", styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        # Limit to first 20 errors for PDF
        errors = template_vars['errors'][:20]
        
        for i, error in enumerate(errors, 1):
            # Error header
            error_title = f"{i}. {error['title']} (Línea {error['line']})"
            
            # Choose style based on severity
            severity = error['severity'].lower()
            if severity == 'critical':
                style = styles['ErrorCritical']
            elif severity == 'high':
                style = styles['ErrorHigh']
            elif severity == 'medium':
                style = styles['ErrorMedium']
            else:
                style = styles['ErrorLow']
            
            story.append(Paragraph(error_title, style))
            story.append(Paragraph(f"<b>Severidad:</b> {error['severity_display']}", styles['Normal']))
            story.append(Paragraph(f"<b>Descripción:</b> {error['description']}", styles['Normal']))
            
            # Add fixes if available
            if error['fixes']:
                story.append(Paragraph("<b>Correcciones Sugeridas:</b>", styles['Normal']))
                for fix in error['fixes'][:2]:  # Limit to 2 fixes
                    fix_text = f"• {fix.get('description', '')} (Confianza: {fix.get('confidence', 0)*100:.1f}%)"
                    story.append(Paragraph(fix_text, styles['Normal']))
            
            story.append(Spacer(1, 10))
        
        if len(template_vars['errors']) > 20:
            story.append(Paragraph(f"... y {len(template_vars['errors']) - 20} errores adicionales", styles['Normal']))
        
        return story
    
    def _create_recommendations_section(self, template_vars: Dict[str, Any]) -> List:
        """Create recommendations section."""
        styles = self._get_styles()
        story = []
        summary = template_vars['summary']
        
        story.append(Paragraph("💡 Recomendaciones", styles['CustomHeading1']))
        story.append(Spacer(1, 12))
        
        recommendations = []
        
        if summary['critical_errors'] > 0:
            recommendations.append("🚨 URGENTE: Corrija los errores críticos antes de ejecutar este código en producción")
        
        if summary['high_errors'] > 0:
            recommendations.append("⚠️ IMPORTANTE: Revise y corrija los errores de alta prioridad")
        
        if summary['quality_score'] < 70:
            recommendations.append("📈 MEJORA: La puntuación de calidad es baja, considere refactorizar el código")
        
        if summary['fixes_suggested'] > 0:
            recommendations.append(f"🔧 AUTOMATIZACIÓN: {summary['fixes_suggested']} correcciones pueden aplicarse automáticamente")
        
        recommendations.append("📚 DOCUMENTACIÓN: Revise la documentación completa para mejores prácticas")
        recommendations.append("🔍 REVISIÓN: Implemente revisiones de código regulares")
        recommendations.append("🧪 TESTING: Pruebe el código en un entorno de desarrollo antes de producción")
        
        for recommendation in recommendations:
            story.append(Paragraph(recommendation, styles['Normal']))
            story.append(Spacer(1, 8))
        
        return story
    
    def _estimate_page_count(self, context: GenerationContext) -> int:
        """Estimate the number of pages in the PDF."""
        errors_count = len(context.analysis_result.get("errors", []))
        
        # Base pages: title, summary, charts, recommendations
        base_pages = 4
        
        # Estimate pages for errors (approximately 5 errors per page)
        error_pages = (errors_count + 4) // 5
        
        return base_pages + error_pages
