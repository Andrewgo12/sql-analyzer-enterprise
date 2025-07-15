"""
JSON Analysis Generator

Generates structured JSON analysis data with comprehensive error information.
"""

import time
import json
import re
from typing import Dict, Any
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class JSONAnalysisGenerator(BaseFormatGenerator):
    """Generator for structured JSON analysis data."""
    
    @property
    def format_name(self) -> str:
        return "Datos JSON"
    
    @property
    def file_extension(self) -> str:
        return ".json"
    
    @property
    def mime_type(self) -> str:
        return "application/json"
    
    @property
    def is_binary(self) -> bool:
        return False
    
    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate structured JSON analysis data."""
        start_time = time.time()
        
        try:
            self.validate_context(context)
            
            # Generate JSON structure
            json_data = self._generate_json_structure(context)
            
            # Convert to formatted JSON string
            json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
            
            generation_time = time.time() - start_time
            
            return self.create_generation_result(
                json_content, context, generation_time,
                metadata={
                    "schema_version": "1.0",
                    "total_objects": len(json_data.get("errors", [])),
                    "data_size_kb": len(json_content) / 1024
                }
            )
            
        except Exception as e:
            return self.handle_generation_error(e, context)
    
    def _generate_json_structure(self, context: GenerationContext) -> Dict[str, Any]:
        """Generate the complete JSON structure."""
        template_vars = self.get_template_variables(context)
        summary = template_vars['summary']
        
        return {
            "analysis_metadata": {
                "version": "1.0",
                "generator": template_vars['generator_name'],
                "generator_version": template_vars['generator_version'],
                "analysis_timestamp": template_vars['analysis_timestamp'].isoformat(),
                "session_id": template_vars['session_id'],
                "language": template_vars['language'],
                "original_filename": template_vars['original_filename']
            },
            "file_information": {
                "filename": summary['filename'],
                "file_size_bytes": summary['file_size'],
                "lines_analyzed": summary['lines_analyzed'],
                "analysis_date": summary['analysis_date']
            },
            "analysis_summary": {
                "total_errors": summary['total_errors'],
                "errors_by_severity": {
                    "critical": summary['critical_errors'],
                    "high": summary['high_errors'],
                    "medium": summary['medium_errors'],
                    "low": summary['low_errors']
                },
                "fixes_suggested": summary['fixes_suggested'],
                "quality_score": summary['quality_score'],
                "statements_analyzed": summary['statements_analyzed']
            },
            "error_categories": template_vars['categories'],
            "errors": [self._format_error_for_json(error) for error in template_vars['errors']],
            "statistics": self._generate_statistics(context),
            "recommendations": self._generate_recommendations_json(context),
            "performance_metrics": self._generate_performance_metrics(context),
            "security_analysis": self._generate_security_analysis(context),
            "quality_metrics": self._generate_quality_metrics(context)
        }
    
    def _format_error_for_json(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Format an error for JSON output with full details."""
        return {
            "id": error.get("id", ""),
            "severity": {
                "level": error.get("severity", ""),
                "display_name": error.get("severity_display", ""),
                "numeric_value": self._get_severity_numeric_value(error.get("severity", ""))
            },
            "category": error.get("category", ""),
            "error_details": {
                "title": error.get("title", ""),
                "message": error.get("message", ""),
                "description": error.get("description", "")
            },
            "location": {
                "line_number": error.get("line", 0),
                "column_start": error.get("column", 0),
                "character_position": 0  # Would be calculated from actual error data
            },
            "fixes": [
                {
                    "description": fix.get("description", ""),
                    "confidence": fix.get("confidence", 0.0),
                    "fix_type": fix.get("type", ""),
                    "original_text": fix.get("original", ""),
                    "corrected_text": fix.get("corrected", ""),
                    "explanation": fix.get("explanation", "")
                }
                for fix in error.get("fixes", [])
            ],
            "confidence": error.get("confidence", 1.0),
            "tags": error.get("tags", []),
            "related_errors": error.get("related_errors", [])
        }
    
    def _get_severity_numeric_value(self, severity: str) -> int:
        """Get numeric value for severity level."""
        severity_values = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "INFO": 0
        }
        return severity_values.get(severity, 0)
    
    def _generate_statistics(self, context: GenerationContext) -> Dict[str, Any]:
        """Generate detailed statistics."""
        errors = context.analysis_result.get("errors", [])
        
        # Calculate error distribution
        severity_distribution = {}
        category_distribution = {}
        line_distribution = {}
        
        for error in errors:
            # Severity distribution
            severity = error.get("severity", "UNKNOWN")
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # Category distribution
            category = error.get("category", "unknown")
            category_distribution[category] = category_distribution.get(category, 0) + 1
            
            # Line distribution (group by ranges)
            line_num = error.get("location", {}).get("line", 0)
            line_range = f"{(line_num // 10) * 10}-{(line_num // 10) * 10 + 9}"
            line_distribution[line_range] = line_distribution.get(line_range, 0) + 1
        
        return {
            "error_distribution": {
                "by_severity": severity_distribution,
                "by_category": category_distribution,
                "by_line_range": line_distribution
            },
            "fix_statistics": {
                "total_fixes_available": sum(len(error.get("fixes", [])) for error in errors),
                "high_confidence_fixes": sum(
                    1 for error in errors 
                    for fix in error.get("fixes", []) 
                    if fix.get("confidence", 0) > 0.8
                ),
                "average_fix_confidence": self._calculate_average_fix_confidence(errors)
            },
            "complexity_metrics": {
                "average_errors_per_line": len(errors) / max(1, context.analysis_result.get("lines", 1)),
                "error_density": len(errors) / max(1, context.analysis_result.get("size", 1)) * 1000,
                "critical_error_ratio": len([e for e in errors if e.get("severity") == "CRITICAL"]) / max(1, len(errors))
            }
        }
    
    def _calculate_average_fix_confidence(self, errors: list) -> float:
        """Calculate average confidence of all fixes."""
        all_confidences = []
        for error in errors:
            for fix in error.get("fixes", []):
                confidence = fix.get("confidence", 0)
                if confidence > 0:
                    all_confidences.append(confidence)
        
        return sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
    
    def _generate_recommendations_json(self, context: GenerationContext) -> Dict[str, Any]:
        """Generate recommendations in JSON format."""
        summary = self.get_analysis_summary(context)
        categories = self.get_error_categories(context)
        
        recommendations = {
            "immediate_actions": [],
            "improvements": [],
            "best_practices": [],
            "security_recommendations": [],
            "performance_recommendations": []
        }
        
        # Immediate actions
        if summary["critical_errors"] > 0:
            recommendations["immediate_actions"].append({
                "priority": "URGENT",
                "action": "Corrija los errores críticos antes de ejecutar el código",
                "reason": f"Se encontraron {summary['critical_errors']} errores críticos",
                "impact": "Previene fallos de ejecución y corrupción de datos"
            })
        
        if summary["high_errors"] > 0:
            recommendations["immediate_actions"].append({
                "priority": "HIGH",
                "action": "Revise y corrija los errores de alta prioridad",
                "reason": f"Se encontraron {summary['high_errors']} errores de alta prioridad",
                "impact": "Mejora la estabilidad y confiabilidad del código"
            })
        
        # Improvements
        if summary["quality_score"] < 70:
            recommendations["improvements"].append({
                "area": "Calidad del Código",
                "suggestion": "Refactorizar el código para mejorar la calidad",
                "current_score": summary["quality_score"],
                "target_score": 85,
                "benefits": ["Mejor mantenibilidad", "Menor probabilidad de errores", "Código más legible"]
            })
        
        # Security recommendations
        if "logical_security" in categories:
            recommendations["security_recommendations"].append({
                "issue": "Vulnerabilidades de seguridad detectadas",
                "recommendation": "Implementar validación de entrada y consultas parametrizadas",
                "severity": "HIGH",
                "affected_areas": ["SQL Injection", "Exposición de datos"]
            })
        
        # Performance recommendations
        if "logical_performance" in categories:
            recommendations["performance_recommendations"].append({
                "issue": "Problemas de rendimiento detectados",
                "recommendation": "Optimizar consultas y agregar índices apropiados",
                "potential_improvement": "Hasta 10x mejora en velocidad de consulta",
                "affected_queries": categories.get("logical_performance", 0)
            })
        
        return recommendations
    
    def _generate_performance_metrics(self, context: GenerationContext) -> Dict[str, Any]:
        """Generate performance-related metrics."""
        return {
            "analysis_performance": {
                "total_analysis_time": context.analysis_result.get("analysis_time", 0),
                "lines_per_second": context.analysis_result.get("lines", 0) / max(0.001, context.analysis_result.get("analysis_time", 0.001)),
                "errors_detection_rate": context.analysis_result.get("errors_found", 0) / max(1, context.analysis_result.get("lines", 1))
            },
            "code_complexity": {
                "cyclomatic_complexity": self._estimate_complexity(context),
                "nesting_depth": self._estimate_nesting_depth(context),
                "statement_complexity": self._estimate_statement_complexity(context)
            }
        }
    
    def _generate_security_analysis(self, context: GenerationContext) -> Dict[str, Any]:
        """Generate security analysis metrics."""
        errors = context.analysis_result.get("errors", [])
        security_errors = [e for e in errors if "security" in e.get("category", "").lower()]
        
        return {
            "security_score": max(0, 100 - len(security_errors) * 10),
            "vulnerabilities_found": len(security_errors),
            "risk_level": self._calculate_risk_level(security_errors),
            "security_categories": {
                "sql_injection": len([e for e in security_errors if "injection" in e.get("title", "").lower()]),
                "data_exposure": len([e for e in security_errors if "exposure" in e.get("title", "").lower()]),
                "privilege_escalation": len([e for e in security_errors if "privilege" in e.get("title", "").lower()])
            }
        }
    
    def _generate_quality_metrics(self, context: GenerationContext) -> Dict[str, Any]:
        """Generate code quality metrics."""
        return {
            "maintainability_index": self._calculate_maintainability_index(context),
            "technical_debt": self._estimate_technical_debt(context),
            "code_smells": self._detect_code_smells(context),
            "best_practices_compliance": self._check_best_practices_compliance(context)
        }
    
    def _estimate_complexity(self, context: GenerationContext) -> int:
        """Estimate cyclomatic complexity."""
        # Simplified complexity estimation
        content = context.analysis_result.get("processed_content", "")
        complexity_keywords = ["IF", "CASE", "WHILE", "FOR", "AND", "OR"]
        complexity = 1  # Base complexity
        
        for keyword in complexity_keywords:
            complexity += content.upper().count(keyword)
        
        return min(complexity, 50)  # Cap at 50
    
    def _estimate_nesting_depth(self, context: GenerationContext) -> int:
        """Estimate maximum nesting depth."""
        content = context.analysis_result.get("processed_content", "")
        max_depth = 0
        current_depth = 0
        
        for char in content:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _estimate_statement_complexity(self, context: GenerationContext) -> float:
        """Estimate average statement complexity."""
        statements = context.analysis_result.get("analysis_summary", {}).get("total_statements", 1)
        lines = context.analysis_result.get("lines", 1)
        return lines / max(1, statements)
    
    def _calculate_risk_level(self, security_errors: list) -> str:
        """Calculate overall security risk level."""
        if not security_errors:
            return "LOW"
        
        critical_security = len([e for e in security_errors if e.get("severity") == "CRITICAL"])
        high_security = len([e for e in security_errors if e.get("severity") == "HIGH"])
        
        if critical_security > 0:
            return "CRITICAL"
        elif high_security > 2:
            return "HIGH"
        elif len(security_errors) > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_maintainability_index(self, context: GenerationContext) -> float:
        """Calculate maintainability index (0-100)."""
        errors = len(context.analysis_result.get("errors", []))
        lines = context.analysis_result.get("lines", 1)
        complexity = self._estimate_complexity(context)
        
        # Simplified maintainability calculation
        base_score = 100
        error_penalty = min(errors * 2, 50)
        complexity_penalty = min(complexity, 30)
        
        return max(0, base_score - error_penalty - complexity_penalty)
    
    def _estimate_technical_debt(self, context: GenerationContext) -> Dict[str, Any]:
        """Estimate technical debt."""
        errors = context.analysis_result.get("errors", [])
        
        # Estimate time to fix (in hours)
        time_estimates = {
            "CRITICAL": 4,
            "HIGH": 2,
            "MEDIUM": 1,
            "LOW": 0.5
        }
        
        total_time = sum(time_estimates.get(error.get("severity", "LOW"), 0.5) for error in errors)
        
        return {
            "estimated_fix_time_hours": total_time,
            "debt_ratio": min(total_time / max(1, context.analysis_result.get("lines", 1)) * 100, 100),
            "priority_fixes": len([e for e in errors if e.get("severity") in ["CRITICAL", "HIGH"]])
        }
    
    def _detect_code_smells(self, context: GenerationContext) -> Dict[str, int]:
        """Detect code smells."""
        content = context.analysis_result.get("processed_content", "").upper()
        
        return {
            "long_queries": content.count("SELECT") if len(content) > 1000 else 0,
            "magic_numbers": len([line for line in content.split('\n') if any(char.isdigit() for char in line)]),
            "duplicate_code": 0,  # Would need more sophisticated analysis
            "complex_conditions": content.count("AND") + content.count("OR")
        }
    
    def _check_best_practices_compliance(self, context: GenerationContext) -> Dict[str, Any]:
        """Check compliance with SQL best practices."""
        content = context.analysis_result.get("processed_content", "").upper()
        
        practices = {
            "uses_proper_naming": not bool(re.search(r'\b[a-z]+[A-Z]', content)),
            "avoids_select_star": "SELECT *" not in content,
            "uses_explicit_joins": "JOIN" in content and "," not in content.split("FROM")[1].split("WHERE")[0] if "FROM" in content else True,
            "has_proper_indexing": "INDEX" in content,
            "uses_transactions": "BEGIN" in content or "COMMIT" in content
        }
        
        compliance_score = sum(practices.values()) / len(practices) * 100
        
        return {
            "overall_compliance": compliance_score,
            "practices_checked": practices,
            "recommendations": [
                practice.replace("_", " ").title() 
                for practice, compliant in practices.items() 
                if not compliant
            ]
        }
