"""
Database Schema Intelligence Module

Intelligent schema analyzer that identifies missing tables, suggests relationships,
optimizes database structure, and provides comprehensive schema insights.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
# Graph analysis - use local implementation
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    # Use local NetworkX implementation
    from .local_networkx import nx
    NETWORKX_AVAILABLE = True
# Text distance - use local implementation
try:
    from textdistance import levenshtein
except ImportError:
    from .local_textdistance import levenshtein
from .sql_parser import Table, Column, BusinessDomain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of database relationships."""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "M:N"
    SELF_REFERENCING = "SELF"


class OptimizationType(Enum):
    """Types of schema optimizations."""
    NORMALIZATION = "Normalization"
    DENORMALIZATION = "Denormalization"
    INDEXING = "Indexing"
    PARTITIONING = "Partitioning"
    ARCHIVING = "Archiving"


@dataclass
class Relationship:
    """Represents a database relationship."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: RelationshipType
    confidence: float = 1.0
    is_explicit: bool = True  # True if FK constraint exists
    suggested_constraint: Optional[str] = None


@dataclass
class MissingTable:
    """Represents a potentially missing table."""
    suggested_name: str
    purpose: str
    business_domain: BusinessDomain
    suggested_columns: List[Dict[str, str]] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class SchemaOptimization:
    """Represents a schema optimization suggestion."""
    optimization_type: OptimizationType
    target_table: str
    description: str
    suggested_changes: List[str] = field(default_factory=list)
    expected_benefit: str = ""
    complexity: str = "Medium"  # Low, Medium, High
    priority: int = 5  # 1-10, 10 being highest


@dataclass
class SchemaAnalysisResult:
    """Complete schema analysis result."""
    tables_analyzed: int
    relationships_found: List[Relationship] = field(default_factory=list)
    missing_tables: List[MissingTable] = field(default_factory=list)
    optimizations: List[SchemaOptimization] = field(default_factory=list)
    data_integrity_score: float = 0.0
    normalization_score: float = 0.0
    performance_score: float = 0.0
    overall_health_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class SchemaAnalyzer:
    """
    Intelligent database schema analyzer.
    
    Features:
    - Identify missing tables and relationships
    - Suggest schema optimizations
    - Analyze data integrity and normalization
    - Detect performance bottlenecks
    - Provide comprehensive schema health assessment
    """
    
    # Common table patterns and their typical relationships
    COMMON_PATTERNS = {
        'user': ['profile', 'role', 'permission', 'session', 'activity'],
        'customer': ['order', 'payment', 'address', 'contact'],
        'product': ['category', 'inventory', 'price', 'review'],
        'order': ['order_item', 'payment', 'shipping', 'status'],
        'employee': ['department', 'position', 'salary', 'attendance'],
        'patient': ['appointment', 'diagnosis', 'treatment', 'prescription'],
        'student': ['enrollment', 'grade', 'course', 'assignment']
    }
    
    # Common junction table patterns
    JUNCTION_PATTERNS = [
        ('user', 'role', 'user_role'),
        ('student', 'course', 'enrollment'),
        ('product', 'category', 'product_category'),
        ('order', 'product', 'order_item'),
        ('doctor', 'patient', 'appointment')
    ]
    
    def __init__(self):
        """Initialize the schema analyzer."""
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Relationship] = []
        # NetworkX is always available (local implementation as fallback)
        self.schema_graph = nx.DiGraph()
        
    def analyze_schema(self, tables: Dict[str, Table]) -> SchemaAnalysisResult:
        """
        Perform comprehensive schema analysis.
        
        Args:
            tables: Dictionary of table objects to analyze
            
        Returns:
            Complete schema analysis result
        """
        self.tables = tables
        self.relationships = []
        # NetworkX is always available (local implementation as fallback)
        self.schema_graph = nx.DiGraph()
        
        logger.info(f"Analyzing schema with {len(tables)} tables")
        
        # Build schema graph
        self._build_schema_graph()
        
        # Analyze existing relationships
        existing_relationships = self._analyze_existing_relationships()
        
        # Detect missing relationships
        suggested_relationships = self._detect_missing_relationships()
        
        # Identify missing tables
        missing_tables = self._identify_missing_tables()
        
        # Generate optimization suggestions
        optimizations = self._generate_optimizations()
        
        # Calculate health scores
        data_integrity_score = self._calculate_data_integrity_score()
        normalization_score = self._calculate_normalization_score()
        performance_score = self._calculate_performance_score()
        overall_health_score = (data_integrity_score + normalization_score + performance_score) / 3
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return SchemaAnalysisResult(
            tables_analyzed=len(tables),
            relationships_found=existing_relationships + suggested_relationships,
            missing_tables=missing_tables,
            optimizations=optimizations,
            data_integrity_score=data_integrity_score,
            normalization_score=normalization_score,
            performance_score=performance_score,
            overall_health_score=overall_health_score,
            recommendations=recommendations
        )
    
    def _determine_relationship_type(self, table1: str, col1: str, table2: str, col2: str) -> RelationshipType:
        """Determine the type of relationship between two tables."""
        # Check if it's self-referencing
        if table1 == table2:
            return RelationshipType.SELF_REFERENCING

        # Check if the foreign key column is also a primary key (1:1 relationship)
        table1_obj = self.tables[table1]
        for col in table1_obj.columns:
            if col.name == col1 and col.primary_key:
                return RelationshipType.ONE_TO_ONE

        # Default to one-to-many
        return RelationshipType.ONE_TO_MANY

    def _calculate_normalization_score(self) -> float:
        """Calculate normalization score (0-100)."""
        if not self.tables:
            return 0.0

        total_score = 0
        total_tables = len(self.tables)

        for table in self.tables.values():
            table_score = 100  # Start with perfect score

            # Deduct points for potential normalization issues
            column_names = [col.name.lower() for col in table.columns]

            # Check for repeating groups (numbered columns)
            numbered_groups = defaultdict(int)
            for col_name in column_names:
                match = re.match(r'(.+?)(\d+)$', col_name)
                if match:
                    base_name = match.group(1)
                    numbered_groups[base_name] += 1

            # Deduct points for each repeating group
            for count in numbered_groups.values():
                if count > 1:
                    table_score -= 20

            # Check for very wide tables (potential for normalization)
            if len(table.columns) > 15:
                table_score -= 10
            elif len(table.columns) > 25:
                table_score -= 20

            total_score += max(0, table_score)

        return total_score / total_tables

    def _calculate_performance_score(self) -> float:
        """Calculate performance score (0-100)."""
        if not self.tables:
            return 0.0

        total_score = 0
        total_tables = len(self.tables)

        for table in self.tables.values():
            table_score = 100  # Start with perfect score

            # Deduct points for missing indexes on foreign keys
            fk_count = len(table.foreign_keys)
            if fk_count > 0:
                # Assume indexes exist for explicit foreign keys
                # In a real implementation, you'd check actual index definitions
                pass

            # Deduct points for very wide tables
            if len(table.columns) > 20:
                table_score -= 15

            # Deduct points for missing primary key
            if not table.primary_keys:
                table_score -= 25

            total_score += max(0, table_score)

        return total_score / total_tables

    def _generate_recommendations(self) -> List[str]:
        """Generate high-level recommendations for schema improvement."""
        recommendations = []

        # Check overall schema health
        total_tables = len(self.tables)
        tables_with_pk = sum(1 for table in self.tables.values() if table.primary_keys)
        tables_with_fk = sum(1 for table in self.tables.values() if table.foreign_keys)

        # Primary key recommendations
        if tables_with_pk < total_tables:
            missing_pk_count = total_tables - tables_with_pk
            recommendations.append(
                f"Add primary keys to {missing_pk_count} table(s) for better data integrity and performance"
            )

        # Foreign key recommendations
        if tables_with_fk < total_tables * 0.3:  # Less than 30% have foreign keys
            recommendations.append(
                "Consider adding foreign key constraints to improve data integrity and document relationships"
            )

        # Business domain recommendations
        domain_distribution = Counter(table.business_domain for table in self.tables.values())
        if BusinessDomain.UNKNOWN in domain_distribution and domain_distribution[BusinessDomain.UNKNOWN] > total_tables * 0.5:
            recommendations.append(
                "Many tables have unclear business purpose - consider better naming conventions and documentation"
            )

        # Schema complexity recommendations
        if total_tables > 50:
            recommendations.append(
                "Large schema detected - consider modularization or microservices architecture"
            )
        elif total_tables < 5:
            recommendations.append(
                "Small schema - ensure all necessary entities are represented"
            )

        # Audit trail recommendations
        has_audit = any('audit' in table.lower() or 'log' in table.lower()
                       for table in self.tables.keys())
        if not has_audit and total_tables > 10:
            recommendations.append(
                "Consider implementing audit trails for compliance and debugging purposes"
            )

        return recommendations

    def generate_schema_report(self, analysis_result: SchemaAnalysisResult) -> str:
        """Generate a comprehensive schema analysis report."""
        report = []
        report.append("Database Schema Analysis Report")
        report.append("=" * 50)
        report.append("")

        # Summary
        report.append("SUMMARY")
        report.append("-" * 20)
        report.append(f"Tables Analyzed: {analysis_result.tables_analyzed}")
        report.append(f"Relationships Found: {len(analysis_result.relationships_found)}")
        report.append(f"Missing Tables Suggested: {len(analysis_result.missing_tables)}")
        report.append(f"Optimization Opportunities: {len(analysis_result.optimizations)}")
        report.append("")

        # Health Scores
        report.append("HEALTH SCORES")
        report.append("-" * 20)
        report.append(f"Overall Health: {analysis_result.overall_health_score:.1f}/100")
        report.append(f"Data Integrity: {analysis_result.data_integrity_score:.1f}/100")
        report.append(f"Normalization: {analysis_result.normalization_score:.1f}/100")
        report.append(f"Performance: {analysis_result.performance_score:.1f}/100")
        report.append("")

        # Relationships
        if analysis_result.relationships_found:
            report.append("RELATIONSHIPS")
            report.append("-" * 20)
            for rel in analysis_result.relationships_found:
                status = "Explicit" if rel.is_explicit else "Suggested"
                report.append(f"{rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column} ({rel.relationship_type.value}) [{status}]")
            report.append("")

        # Missing Tables
        if analysis_result.missing_tables:
            report.append("SUGGESTED MISSING TABLES")
            report.append("-" * 30)
            for missing in analysis_result.missing_tables:
                report.append(f"Table: {missing.suggested_name}")
                report.append(f"  Purpose: {missing.purpose}")
                report.append(f"  Domain: {missing.business_domain.value}")
                report.append(f"  Confidence: {missing.confidence:.1f}")
                report.append(f"  Reasoning: {missing.reasoning}")
                report.append("")

        # Optimizations
        if analysis_result.optimizations:
            report.append("OPTIMIZATION SUGGESTIONS")
            report.append("-" * 30)
            # Sort by priority (highest first)
            sorted_optimizations = sorted(analysis_result.optimizations,
                                        key=lambda x: x.priority, reverse=True)
            for opt in sorted_optimizations:
                report.append(f"Priority {opt.priority}: {opt.description}")
                report.append(f"  Type: {opt.optimization_type.value}")
                report.append(f"  Target: {opt.target_table}")
                report.append(f"  Complexity: {opt.complexity}")
                report.append(f"  Expected Benefit: {opt.expected_benefit}")
                if opt.suggested_changes:
                    report.append("  Suggested Changes:")
                    for change in opt.suggested_changes:
                        report.append(f"    - {change}")
                report.append("")

        # Recommendations
        if analysis_result.recommendations:
            report.append("RECOMMENDATIONS")
            report.append("-" * 20)
            for i, rec in enumerate(analysis_result.recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")

        return "\n".join(report)
