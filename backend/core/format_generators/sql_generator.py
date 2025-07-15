"""
Enhanced SQL Generator

Generates enhanced SQL files with intelligent comments and corrections.
"""

import time
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class EnhancedSQLGenerator(BaseFormatGenerator):
    """Generator for enhanced SQL files with comments and corrections."""
    
    @property
    def format_name(self) -> str:
        return "SQL Mejorado"
    
    @property
    def file_extension(self) -> str:
        return ".sql"
    
    @property
    def mime_type(self) -> str:
        return "text/sql"
    
    @property
    def is_binary(self) -> bool:
        return False
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate enhanced SQL with comments and corrections."""
        start_time = time.time()
        
        try:
            self.validate_context(context)
            
            # Get the original SQL content
            original_sql = context.analysis_result.get("processed_content", "")
            if not original_sql:
                original_sql = context.analysis_result.get("original_content", "")
            
            # Generate enhanced SQL
            enhanced_sql = self._enhance_sql_content(original_sql, context)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                enhanced_sql, context, generation_time,
                metadata={
                    "original_lines": len(original_sql.split('\n')),
                    "enhanced_lines": len(enhanced_sql.split('\n')),
                    "comments_added": enhanced_sql.count('--'),
                    "corrections_applied": len(context.analysis_result.get("corrections_applied", []))
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
    def _enhance_sql_content(self, original_sql: str, context: GenerationContext) -> str:
        """Enhance SQL content with comments and corrections."""
        lines = original_sql.split('\n')
        enhanced_lines = []
        
        # Add header comment
        enhanced_lines.extend(self._generate_header_comment(context))
        enhanced_lines.append("")
        
        # Add analysis summary comment
        enhanced_lines.extend(self._generate_summary_comment(context))
        enhanced_lines.append("")
        
        # Process each line
        errors_by_line = self._group_errors_by_line(context.analysis_result.get("errors", []))
        
        for line_num, line in enumerate(lines, 1):
            # Add error comments before the line if there are errors
            if line_num in errors_by_line:
                enhanced_lines.extend(self._generate_error_comments(errors_by_line[line_num]))
            
            # Add the original line (potentially corrected)
            corrected_line = self._apply_corrections(line, line_num, context)
            enhanced_lines.append(corrected_line)
            
            # Add explanatory comments for complex statements
            if self._is_complex_statement(line):
                enhanced_lines.extend(self._generate_explanation_comment(line))
        
        # Add footer with recommendations
        enhanced_lines.append("")
        enhanced_lines.extend(self._generate_recommendations_comment(context))
        
        return '\n'.join(enhanced_lines)
    
    def _generate_header_comment(self, context: GenerationContext) -> List[str]:
        """Generate header comment block."""
        return [
            "-- ============================================================================",
            "-- ARCHIVO SQL MEJORADO - ANÁLISIS AUTOMÁTICO",
            "-- ============================================================================",
            f"-- Archivo original: {context.original_filename}",
            f"-- Fecha de análisis: {context.analysis_timestamp.strftime('%d/%m/%Y %H:%M:%S')}",
            f"-- Generado por: SQL Analyzer Enterprise",
            f"-- Sesión: {context.session_id[:8]}...",
            "-- ============================================================================"
        ]
    
    def _generate_summary_comment(self, context: GenerationContext) -> List[str]:
        """Generate analysis summary comment."""
        summary = self.get_analysis_summary(context)
        
        return [
            "-- RESUMEN DEL ANÁLISIS",
            "-- ============================================================================",
            f"-- Total de errores encontrados: {summary['total_errors']}",
            f"--   • Críticos: {summary['critical_errors']}",
            f"--   • Altos: {summary['high_errors']}",
            f"--   • Medios: {summary['medium_errors']}",
            f"--   • Bajos: {summary['low_errors']}",
            f"-- Correcciones sugeridas: {summary['fixes_suggested']}",
            f"-- Puntuación de calidad: {summary['quality_score']}%",
            f"-- Líneas analizadas: {summary['lines_analyzed']}",
            f"-- Declaraciones SQL: {summary['statements_analyzed']}",
            "-- ============================================================================"
        ]
    
    def _group_errors_by_line(self, errors: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Group errors by line number."""
        errors_by_line = {}
        
        for error in errors:
            line_num = error.get("location", {}).get("line", 0)
            if line_num > 0:
                if line_num not in errors_by_line:
                    errors_by_line[line_num] = []
                errors_by_line[line_num].append(error)
        
        return errors_by_line
    
    def _generate_error_comments(self, errors: List[Dict[str, Any]]) -> List[str]:
        """Generate error comments for a line."""
        comments = []
        
        for error in errors:
            severity = error.get("severity", "")
            title = error.get("title", "")
            message = error.get("message", "")
            
            # Choose comment style based on severity
            if severity == "CRITICAL":
                prefix = "-- ❌ CRÍTICO:"
            elif severity == "HIGH":
                prefix = "-- ⚠️  ALTO:"
            elif severity == "MEDIUM":
                prefix = "-- ⚡ MEDIO:"
            elif severity == "LOW":
                prefix = "-- ℹ️  BAJO:"
            else:
                prefix = "-- 📝 INFO:"
            
            comments.append(f"{prefix} {title}")
            if message != title:
                comments.append(f"--    {message}")
            
            # Add fix suggestions
            fixes = error.get("fixes", [])
            if fixes:
                best_fix = max(fixes, key=lambda f: f.get("confidence", 0))
                comments.append(f"--    💡 Sugerencia: {best_fix.get('description', '')}")
        
        return comments
    
    def _apply_corrections(self, line: str, line_num: int, context: GenerationContext) -> str:
        """Apply automatic corrections to a line."""
        corrected_line = line
        
        # Apply high-confidence corrections
        corrections = context.analysis_result.get("corrections_applied", [])
        for correction in corrections:
            if correction.get("confidence", 0) > 0.9:
                original = correction.get("original_text", "")
                corrected = correction.get("corrected_text", "")
                if original in corrected_line:
                    corrected_line = corrected_line.replace(original, corrected)
                    # Add inline comment about the correction
                    corrected_line += f"  -- ✅ Corregido automáticamente"
        
        return corrected_line
    
    def _is_complex_statement(self, line: str) -> bool:
        """Check if a line contains a complex SQL statement."""
        line_upper = line.upper().strip()
        
        complex_patterns = [
            "JOIN", "UNION", "SUBQUERY", "CASE WHEN", "EXISTS",
            "WINDOW", "PARTITION BY", "RECURSIVE", "CTE"
        ]
        
        return any(pattern in line_upper for pattern in complex_patterns)
    
    def _generate_explanation_comment(self, line: str) -> List[str]:
        """Generate explanatory comment for complex statements."""
        line_upper = line.upper().strip()
        
        explanations = {
            "JOIN": "-- 📚 JOIN: Une datos de múltiples tablas basándose en una condición",
            "LEFT JOIN": "-- 📚 LEFT JOIN: Incluye todos los registros de la tabla izquierda",
            "INNER JOIN": "-- 📚 INNER JOIN: Solo incluye registros que coinciden en ambas tablas",
            "UNION": "-- 📚 UNION: Combina resultados de múltiples consultas SELECT",
            "CASE WHEN": "-- 📚 CASE WHEN: Lógica condicional similar a if-else",
            "EXISTS": "-- 📚 EXISTS: Verifica si una subconsulta devuelve al menos un resultado",
            "WINDOW": "-- 📚 WINDOW FUNCTION: Función que opera sobre un conjunto de filas relacionadas",
            "PARTITION BY": "-- 📚 PARTITION BY: Divide el resultado en grupos para funciones de ventana",
            "RECURSIVE": "-- 📚 RECURSIVE: Consulta que se refiere a sí misma para datos jerárquicos"
        }
        
        for pattern, explanation in explanations.items():
            if pattern in line_upper:
                return [explanation]
        
        return []
    
    def _generate_recommendations_comment(self, context: GenerationContext) -> List[str]:
        """Generate recommendations comment block."""
        comments = [
            "-- ============================================================================",
            "-- RECOMENDACIONES GENERALES",
            "-- ============================================================================"
        ]
        
        summary = self.get_analysis_summary(context)
        
        if summary["critical_errors"] > 0:
            comments.append("-- 🚨 URGENTE: Corrija los errores críticos antes de ejecutar este código")
        
        if summary["high_errors"] > 0:
            comments.append("-- ⚠️  IMPORTANTE: Revise y corrija los errores de alta prioridad")
        
        if summary["quality_score"] < 70:
            comments.append("-- 📈 MEJORA: La puntuación de calidad es baja, considere refactorizar")
        
        # Add specific recommendations based on error categories
        categories = self.get_error_categories(context)
        
        if "logical_performance" in categories:
            comments.append("-- 🚀 RENDIMIENTO: Optimice las consultas para mejor rendimiento")
        
        if "logical_security" in categories:
            comments.append("-- 🔒 SEGURIDAD: Revise las vulnerabilidades de seguridad detectadas")
        
        if "syntax_punctuation" in categories:
            comments.append("-- ✏️  SINTAXIS: Revise la puntuación y sintaxis SQL")
        
        comments.extend([
            "-- ============================================================================",
            "-- Para más información, consulte la documentación completa del análisis",
            "-- ============================================================================"
        ])
        
        return comments
