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
    class TableStyle:
        def __init__(self, *args, **kwargs):
            pass

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
    
    def _estimate_page_count(self, context: GenerationContext) -> int:
        """Estimate the number of pages in the PDF."""
        errors_count = len(context.analysis_result.get("errors", []))
        
        # Base pages: title, summary, charts, recommendations
        base_pages = 4
        
        # Estimate pages for errors (approximately 5 errors per page)
        error_pages = (errors_count + 4) // 5
        
        return base_pages + error_pages
