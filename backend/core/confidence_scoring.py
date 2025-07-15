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
