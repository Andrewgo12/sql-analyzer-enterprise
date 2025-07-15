"""
Word Document Generator

Generates professional Word documents with analysis results.
"""

import time
import io
from typing import Dict, Any
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult

# Optional import for Word document generation
try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    from docx.oxml.shared import OxmlElement, qn
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    # Create dummy classes for when python-docx is not available
    class Document:
        def __init__(self, *args, **kwargs):
            pass
        def add_heading(self, *args, **kwargs):
            return self
        def add_paragraph(self, *args, **kwargs):
            return self
        def add_table(self, *args, **kwargs):
            return self
        def save(self, *args, **kwargs):
            pass

    class Inches:
        def __init__(self, *args, **kwargs):
            pass

    class Pt:
        def __init__(self, *args, **kwargs):
            pass

    WD_ALIGN_PARAGRAPH = type('WD_ALIGN_PARAGRAPH', (), {'CENTER': 1, 'LEFT': 0})
    WD_STYLE_TYPE = type('WD_STYLE_TYPE', (), {'PARAGRAPH': 1})


class WordDocumentGenerator(BaseFormatGenerator):
    """Generator for professional Word documents."""

    @property
    def format_name(self) -> str:
        return "Documento Word"

    @property
    def file_extension(self) -> str:
        return ".docx"

    @property
    def mime_type(self) -> str:
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    @property
    def is_binary(self) -> bool:
        return True

    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate professional Word document."""
        start_time = time.time()

        try:
            if not DOCX_AVAILABLE:
                # Create a simple text-based document if python-docx is not available
                return self._generate_text_fallback(context, start_time)

            self.validate_context(context)

            # Generate Word document
            doc_content = self._generate_word_document(context)

            generation_time = time.time() - start_time

            return self.create_generation_result(
                doc_content, context, generation_time,
                metadata={
                    "pages_estimated": self._estimate_page_count(context),
                    "sections": 5,
                    "format": "DOCX"
                }
            )

        except Exception as e:
            return self.handle_generation_error(e, context)

========================

Archivo: {template_vars['original_filename']}
Fecha: {template_vars['analysis_timestamp'].strftime('%d/%m/%Y %H:%M:%S')}

RESUMEN EJECUTIVO
=================
Total de errores: {summary['total_errors']}
Puntuación de calidad: {summary['quality_score']}%
Líneas analizadas: {summary['lines_analyzed']}
Correcciones sugeridas: {summary['fixes_suggested']}

DISTRIBUCIÓN DE ERRORES
========================
Críticos: {summary['critical_errors']}
Altos: {summary['high_errors']}
Medios: {summary['medium_errors']}
Bajos: {summary['low_errors']}

RECOMENDACIONES
===============
- Revise los errores críticos inmediatamente
- Implemente las correcciones sugeridas
- Mejore la calidad general del código

Generado por SQL Analyzer Enterprise
"""

        generation_time = time.time() - start_time

        return self.create_generation_result(
            content.encode('utf-8'), context, generation_time,
            metadata={"fallback": True, "format": "text"}
        )

    def _estimate_page_count(self, context: GenerationContext) -> int:
        """Estimate the number of pages in the document."""
        errors_count = len(context.analysis_result.get("errors", []))

        # Base pages: title, summary, recommendations
        base_pages = 3

        # Estimate pages for errors (approximately 3 errors per page)
        error_pages = (errors_count + 2) // 3

        return base_pages + error_pages
