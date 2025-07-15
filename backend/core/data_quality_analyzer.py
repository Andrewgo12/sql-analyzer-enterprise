"""
Data Quality Analyzer
Advanced data quality assessment and validation for SQL schemas and queries
"""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class QualityIssueType(Enum):
    """Types of data quality issues."""
    MISSING_CONSTRAINTS = "missing_constraints"
    INCONSISTENT_NAMING = "inconsistent_naming"
    MISSING_DOCUMENTATION = "missing_documentation"
    DATA_TYPE_ISSUES = "data_type_issues"
    NORMALIZATION_ISSUES = "normalization_issues"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    BUSINESS_RULE_VIOLATIONS = "business_rule_violations"


class QualitySeverity(Enum):
    """Severity levels for quality issues."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class QualityIssue:
    """Data quality issue representation."""
    type: QualityIssueType
    severity: QualitySeverity
    title: str
    description: str
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    recommendation: Optional[str] = None
    impact: Optional[str] = None
    fix_sql: Optional[str] = None


@dataclass
class QualityMetrics:
    """Data quality metrics."""
    overall_score: float
    constraint_coverage: float
    naming_consistency: float
    documentation_coverage: float
    normalization_score: float
    referential_integrity_score: float
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int


class DataQualityAnalyzer:
    """Advanced data quality analyzer."""
    
    def __init__(self):
        self.naming_conventions = self._initialize_naming_conventions()
        self.data_type_rules = self._initialize_data_type_rules()
        self.business_rules = self._initialize_business_rules()
    
    def analyze_data_quality(self, sql_content: str, schema_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze data quality of SQL schema and queries."""
        
        # Parse schema information
        tables = self._parse_schema_from_sql(sql_content)
        
        # Analyze different quality aspects
        issues = []
        
        # Check naming conventions
        issues.extend(self._check_naming_conventions(tables))
        
        # Check data type appropriateness
        issues.extend(self._check_data_types(tables))
        
        # Check constraints and integrity
        issues.extend(self._check_constraints(tables))
        
        # Check normalization
        issues.extend(self._check_normalization(tables))
        
        # Check business rules
        issues.extend(self._check_business_rules(tables))
        
        # Calculate quality metrics
        metrics = self._calculate_quality_metrics(issues, tables)
        
        return {
            "quality_metrics": self._metrics_to_dict(metrics),
            "issues": [self._issue_to_dict(issue) for issue in issues],
            "recommendations": self._generate_quality_recommendations(issues, metrics),
            "summary": {
                "total_tables": len(tables),
                "total_issues": len(issues),
                "quality_score": metrics.overall_score,
                "improvement_areas": self._identify_improvement_areas(issues)
            }
        }
    
    def _calculate_normalization_score(self, issues: List[QualityIssue]) -> float:
        """Calculate normalization score."""
        
        normalization_issues = [i for i in issues if i.type == QualityIssueType.NORMALIZATION_ISSUES]
        base_score = 100
        
        return max(0, base_score - (len(normalization_issues) * 10))
    
    def _issue_to_dict(self, issue: QualityIssue) -> Dict[str, Any]:
        """Convert quality issue to dictionary."""
        return {
            "type": issue.type.value,
            "severity": issue.severity.value,
            "title": issue.title,
            "description": issue.description,
            "table_name": issue.table_name,
            "column_name": issue.column_name,
            "recommendation": issue.recommendation,
            "impact": issue.impact,
            "fix_sql": issue.fix_sql
        }
