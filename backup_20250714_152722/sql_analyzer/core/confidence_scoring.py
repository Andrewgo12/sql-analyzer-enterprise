"""
Confidence Scoring System
Advanced confidence scoring for SQL analysis results
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class ConfidenceLevel(Enum):
    """Confidence levels."""
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class AnalysisType(Enum):
    """Types of analysis."""
    SYNTAX = "SYNTAX"
    SEMANTIC = "SEMANTIC"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    SCHEMA = "SCHEMA"
    LOGIC = "LOGIC"


@dataclass
class ConfidenceMetrics:
    """Confidence metrics for analysis results."""
    pattern_match_score: float = 0.0
    context_relevance_score: float = 0.0
    historical_accuracy_score: float = 0.0
    complexity_penalty: float = 0.0
    validation_score: float = 0.0
    consensus_score: float = 0.0
    
    def calculate_overall_confidence(self) -> float:
        """Calculate overall confidence score."""
        # Weighted average of different metrics
        weights = {
            'pattern_match': 0.25,
            'context_relevance': 0.20,
            'historical_accuracy': 0.20,
            'complexity_penalty': -0.10,  # Negative weight for penalty
            'validation': 0.15,
            'consensus': 0.10
        }
        
        score = (
            self.pattern_match_score * weights['pattern_match'] +
            self.context_relevance_score * weights['context_relevance'] +
            self.historical_accuracy_score * weights['historical_accuracy'] +
            self.complexity_penalty * weights['complexity_penalty'] +
            self.validation_score * weights['validation'] +
            self.consensus_score * weights['consensus']
        )
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))


class ConfidenceScorer:
    """Advanced confidence scoring system."""
    
    def __init__(self):
        self.pattern_database = self._initialize_pattern_database()
        self.historical_data = self._initialize_historical_data()
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_pattern_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize pattern database with known SQL patterns and their confidence factors."""
        return {
            # Syntax patterns
            "missing_semicolon": {
                "confidence_base": 0.95,
                "pattern_strength": 0.9,
                "false_positive_rate": 0.02
            },
            "unmatched_parentheses": {
                "confidence_base": 0.98,
                "pattern_strength": 0.95,
                "false_positive_rate": 0.01
            },
            "invalid_keyword": {
                "confidence_base": 0.92,
                "pattern_strength": 0.85,
                "false_positive_rate": 0.05
            },
            
            # Security patterns
            "sql_injection_concat": {
                "confidence_base": 0.85,
                "pattern_strength": 0.8,
                "false_positive_rate": 0.15
            },
            "dynamic_sql_execution": {
                "confidence_base": 0.78,
                "pattern_strength": 0.75,
                "false_positive_rate": 0.20
            },
            "privilege_escalation": {
                "confidence_base": 0.88,
                "pattern_strength": 0.82,
                "false_positive_rate": 0.10
            },
            
            # Performance patterns
            "missing_index_hint": {
                "confidence_base": 0.65,
                "pattern_strength": 0.6,
                "false_positive_rate": 0.30
            },
            "inefficient_join": {
                "confidence_base": 0.70,
                "pattern_strength": 0.65,
                "false_positive_rate": 0.25
            },
            "select_star_usage": {
                "confidence_base": 0.75,
                "pattern_strength": 0.7,
                "false_positive_rate": 0.20
            },
            
            # Schema patterns
            "foreign_key_violation": {
                "confidence_base": 0.90,
                "pattern_strength": 0.88,
                "false_positive_rate": 0.08
            },
            "data_type_mismatch": {
                "confidence_base": 0.85,
                "pattern_strength": 0.8,
                "false_positive_rate": 0.12
            },
            "constraint_violation": {
                "confidence_base": 0.92,
                "pattern_strength": 0.9,
                "false_positive_rate": 0.06
            }
        }
    
    def _initialize_historical_data(self) -> Dict[str, float]:
        """Initialize historical accuracy data for different error types."""
        return {
            "syntax_errors": 0.94,
            "security_vulnerabilities": 0.82,
            "performance_issues": 0.68,
            "schema_problems": 0.86,
            "logic_errors": 0.71,
            "semantic_errors": 0.79
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for different analysis types."""
        return {
            AnalysisType.SYNTAX.value: {
                "min_pattern_matches": 1,
                "context_window": 5,
                "validation_checks": ["parser_validation", "ast_validation"]
            },
            AnalysisType.SECURITY.value: {
                "min_pattern_matches": 2,
                "context_window": 10,
                "validation_checks": ["pattern_validation", "context_validation", "severity_validation"]
            },
            AnalysisType.PERFORMANCE.value: {
                "min_pattern_matches": 1,
                "context_window": 15,
                "validation_checks": ["complexity_validation", "impact_validation"]
            },
            AnalysisType.SCHEMA.value: {
                "min_pattern_matches": 1,
                "context_window": 8,
                "validation_checks": ["schema_validation", "relationship_validation"]
            }
        }
    
    def calculate_confidence(
        self,
        error_type: str,
        analysis_type: AnalysisType,
        context: Dict[str, Any]
    ) -> Tuple[float, ConfidenceMetrics]:
        """Calculate confidence score for an analysis result."""
        
        metrics = ConfidenceMetrics()
        
        # 1. Pattern Match Score
        metrics.pattern_match_score = self._calculate_pattern_match_score(error_type, context)
        
        # 2. Context Relevance Score
        metrics.context_relevance_score = self._calculate_context_relevance_score(
            error_type, analysis_type, context
        )
        
        # 3. Historical Accuracy Score
        metrics.historical_accuracy_score = self._calculate_historical_accuracy_score(
            analysis_type, context
        )
        
        # 4. Complexity Penalty
        metrics.complexity_penalty = self._calculate_complexity_penalty(context)
        
        # 5. Validation Score
        metrics.validation_score = self._calculate_validation_score(
            error_type, analysis_type, context
        )
        
        # 6. Consensus Score
        metrics.consensus_score = self._calculate_consensus_score(error_type, context)
        
        # Calculate overall confidence
        overall_confidence = metrics.calculate_overall_confidence()
        
        return overall_confidence, metrics
    
    def _calculate_pattern_match_score(self, error_type: str, context: Dict[str, Any]) -> float:
        """Calculate pattern match confidence score."""
        pattern_info = self.pattern_database.get(error_type, {})
        
        if not pattern_info:
            return 0.5  # Default medium confidence for unknown patterns
        
        base_confidence = pattern_info.get("confidence_base", 0.5)
        pattern_strength = pattern_info.get("pattern_strength", 0.5)
        false_positive_rate = pattern_info.get("false_positive_rate", 0.2)
        
        # Adjust based on pattern matches
        pattern_matches = context.get("pattern_matches", 1)
        match_bonus = min(0.2, (pattern_matches - 1) * 0.05)
        
        # Adjust based on false positive rate
        fp_penalty = false_positive_rate * 0.3
        
        score = base_confidence * pattern_strength + match_bonus - fp_penalty
        return max(0.0, min(1.0, score))
    
    def _calculate_context_relevance_score(
        self,
        error_type: str,
        analysis_type: AnalysisType,
        context: Dict[str, Any]
    ) -> float:
        """Calculate context relevance score."""
        
        # Base relevance based on analysis type
        type_relevance = {
            AnalysisType.SYNTAX: 0.9,
            AnalysisType.SECURITY: 0.8,
            AnalysisType.PERFORMANCE: 0.7,
            AnalysisType.SCHEMA: 0.85,
            AnalysisType.LOGIC: 0.75,
            AnalysisType.SEMANTIC: 0.8
        }
        
        base_score = type_relevance.get(analysis_type, 0.5)
        
        # Adjust based on context factors
        context_factors = {
            "line_number": context.get("line_number", 0),
            "column_number": context.get("column_number", 0),
            "surrounding_code": context.get("surrounding_code", ""),
            "sql_statement_type": context.get("sql_statement_type", ""),
            "table_references": context.get("table_references", []),
            "function_calls": context.get("function_calls", [])
        }
        
        # Calculate context richness
        context_richness = 0.0
        if context_factors["line_number"] > 0:
            context_richness += 0.1
        if context_factors["column_number"] > 0:
            context_richness += 0.1
        if context_factors["surrounding_code"]:
            context_richness += 0.2
        if context_factors["sql_statement_type"]:
            context_richness += 0.15
        if context_factors["table_references"]:
            context_richness += 0.1 * min(1.0, len(context_factors["table_references"]) / 3)
        if context_factors["function_calls"]:
            context_richness += 0.1 * min(1.0, len(context_factors["function_calls"]) / 2)
        
        return min(1.0, base_score + context_richness)
    
    def _calculate_historical_accuracy_score(
        self,
        analysis_type: AnalysisType,
        context: Dict[str, Any]
    ) -> float:
        """Calculate historical accuracy score."""
        
        # Map analysis type to historical category
        type_mapping = {
            AnalysisType.SYNTAX: "syntax_errors",
            AnalysisType.SECURITY: "security_vulnerabilities",
            AnalysisType.PERFORMANCE: "performance_issues",
            AnalysisType.SCHEMA: "schema_problems",
            AnalysisType.LOGIC: "logic_errors",
            AnalysisType.SEMANTIC: "semantic_errors"
        }
        
        category = type_mapping.get(analysis_type, "syntax_errors")
        base_accuracy = self.historical_data.get(category, 0.7)
        
        # Adjust based on similar past cases
        similar_cases = context.get("similar_cases_count", 0)
        if similar_cases > 0:
            similarity_bonus = min(0.15, similar_cases * 0.03)
            base_accuracy += similarity_bonus
        
        return min(1.0, base_accuracy)
    
    def _calculate_complexity_penalty(self, context: Dict[str, Any]) -> float:
        """Calculate complexity penalty (higher complexity = lower confidence)."""
        
        complexity_factors = {
            "nested_queries": context.get("nested_queries", 0),
            "join_count": context.get("join_count", 0),
            "function_complexity": context.get("function_complexity", 0),
            "condition_complexity": context.get("condition_complexity", 0),
            "statement_length": context.get("statement_length", 0)
        }
        
        # Calculate complexity score
        complexity_score = 0.0
        
        # Nested queries penalty
        if complexity_factors["nested_queries"] > 2:
            complexity_score += (complexity_factors["nested_queries"] - 2) * 0.1
        
        # Join complexity penalty
        if complexity_factors["join_count"] > 3:
            complexity_score += (complexity_factors["join_count"] - 3) * 0.05
        
        # Function complexity penalty
        complexity_score += complexity_factors["function_complexity"] * 0.02
        
        # Condition complexity penalty
        complexity_score += complexity_factors["condition_complexity"] * 0.03
        
        # Statement length penalty
        if complexity_factors["statement_length"] > 500:
            complexity_score += (complexity_factors["statement_length"] - 500) / 10000
        
        return min(0.5, complexity_score)  # Cap penalty at 0.5
    
    def _calculate_validation_score(
        self,
        error_type: str,
        analysis_type: AnalysisType,
        context: Dict[str, Any]
    ) -> float:
        """Calculate validation score based on validation checks."""
        
        validation_rules = self.validation_rules.get(analysis_type.value, {})
        validation_checks = validation_rules.get("validation_checks", [])
        
        if not validation_checks:
            return 0.5  # Default if no validation rules
        
        passed_checks = 0
        total_checks = len(validation_checks)
        
        # Simulate validation check results based on context
        for check in validation_checks:
            if self._simulate_validation_check(check, context):
                passed_checks += 1
        
        return passed_checks / total_checks if total_checks > 0 else 0.5
    
    def _simulate_validation_check(self, check: str, context: Dict[str, Any]) -> bool:
        """Simulate validation check (in real implementation, this would perform actual validation)."""
        
        # Simulate different validation checks
        validation_results = {
            "parser_validation": context.get("parser_valid", True),
            "ast_validation": context.get("ast_valid", True),
            "pattern_validation": context.get("pattern_matches", 0) > 0,
            "context_validation": len(context.get("surrounding_code", "")) > 10,
            "severity_validation": context.get("severity", "MEDIUM") in ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "complexity_validation": context.get("complexity_score", 0.5) < 0.8,
            "impact_validation": context.get("impact_score", 0.5) > 0.2,
            "schema_validation": context.get("schema_valid", True),
            "relationship_validation": len(context.get("table_references", [])) > 0
        }
        
        return validation_results.get(check, True)
    
    def _calculate_consensus_score(self, error_type: str, context: Dict[str, Any]) -> float:
        """Calculate consensus score from multiple analysis methods."""
        
        # Simulate multiple analysis methods agreeing on the result
        analysis_methods = context.get("analysis_methods", ["primary"])
        
        if len(analysis_methods) <= 1:
            return 0.5  # No consensus possible with single method
        
        # Simulate agreement between methods
        agreement_count = context.get("method_agreement_count", len(analysis_methods))
        consensus_ratio = agreement_count / len(analysis_methods)
        
        # Higher consensus = higher confidence
        return consensus_ratio
    
    def get_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level."""
        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def get_confidence_description(self, confidence_level: ConfidenceLevel) -> str:
        """Get human-readable description of confidence level."""
        descriptions = {
            ConfidenceLevel.VERY_HIGH: "Muy alta confianza - Resultado altamente confiable",
            ConfidenceLevel.HIGH: "Alta confianza - Resultado confiable",
            ConfidenceLevel.MEDIUM: "Confianza media - Resultado probablemente correcto",
            ConfidenceLevel.LOW: "Baja confianza - Resultado requiere verificación",
            ConfidenceLevel.VERY_LOW: "Muy baja confianza - Resultado incierto"
        }
        return descriptions.get(confidence_level, "Confianza desconocida")


# Global confidence scorer instance
_confidence_scorer: Optional[ConfidenceScorer] = None


def get_confidence_scorer() -> ConfidenceScorer:
    """Get the global confidence scorer instance."""
    global _confidence_scorer
    if _confidence_scorer is None:
        _confidence_scorer = ConfidenceScorer()
    return _confidence_scorer


def calculate_error_confidence(
    error_type: str,
    analysis_type: AnalysisType,
    context: Dict[str, Any]
) -> Tuple[float, ConfidenceLevel, str]:
    """Calculate confidence for an error with convenience wrapper."""
    scorer = get_confidence_scorer()
    confidence_score, metrics = scorer.calculate_confidence(error_type, analysis_type, context)
    confidence_level = scorer.get_confidence_level(confidence_score)
    description = scorer.get_confidence_description(confidence_level)
    
    return confidence_score, confidence_level, description
