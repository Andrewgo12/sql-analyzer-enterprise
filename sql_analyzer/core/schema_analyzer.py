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
import networkx as nx
from textdistance import levenshtein
from sql_analyzer.core.sql_parser import Table, Column, BusinessDomain

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
    
    def _build_schema_graph(self):
        """Build a graph representation of the schema."""
        # Add tables as nodes
        for table_name, table in self.tables.items():
            self.schema_graph.add_node(table_name, table=table)
        
        # Add relationships as edges
        for table_name, table in self.tables.items():
            for fk in table.foreign_keys:
                if fk['references_table'] in self.tables:
                    self.schema_graph.add_edge(
                        table_name, 
                        fk['references_table'],
                        column=fk['column'],
                        references_column=fk['references_column']
                    )
    
    def _analyze_existing_relationships(self) -> List[Relationship]:
        """Analyze explicitly defined relationships."""
        relationships = []
        
        for table_name, table in self.tables.items():
            for fk in table.foreign_keys:
                if fk['references_table'] in self.tables:
                    # Determine relationship type
                    rel_type = self._determine_relationship_type(
                        table_name, fk['column'],
                        fk['references_table'], fk['references_column']
                    )
                    
                    relationship = Relationship(
                        from_table=table_name,
                        from_column=fk['column'],
                        to_table=fk['references_table'],
                        to_column=fk['references_column'],
                        relationship_type=rel_type,
                        confidence=1.0,
                        is_explicit=True
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _detect_missing_relationships(self) -> List[Relationship]:
        """Detect potential missing relationships based on naming patterns."""
        suggested_relationships = []
        
        for table1_name, table1 in self.tables.items():
            for table2_name, table2 in self.tables.items():
                if table1_name != table2_name:
                    # Check for potential foreign key relationships
                    potential_fks = self._find_potential_foreign_keys(table1, table2)
                    
                    for fk_info in potential_fks:
                        # Check if relationship already exists
                        if not self._relationship_exists(table1_name, fk_info['column'], 
                                                      table2_name, fk_info['references_column']):
                            relationship = Relationship(
                                from_table=table1_name,
                                from_column=fk_info['column'],
                                to_table=table2_name,
                                to_column=fk_info['references_column'],
                                relationship_type=RelationshipType.ONE_TO_MANY,
                                confidence=fk_info['confidence'],
                                is_explicit=False,
                                suggested_constraint=f"ALTER TABLE {table1_name} ADD CONSTRAINT fk_{table1_name}_{fk_info['column']} FOREIGN KEY ({fk_info['column']}) REFERENCES {table2_name}({fk_info['references_column']})"
                            )
                            suggested_relationships.append(relationship)
        
        return suggested_relationships
    
    def _find_potential_foreign_keys(self, table1: Table, table2: Table) -> List[Dict[str, Any]]:
        """Find potential foreign key relationships between two tables."""
        potential_fks = []
        
        # Look for columns that might reference the other table
        for col1 in table1.columns:
            col1_name = col1.name.lower()
            
            # Check if column name suggests it references table2
            table2_name_lower = table2.name.lower()
            
            # Pattern 1: column named like "table2_id" or "table2id"
            if (col1_name == f"{table2_name_lower}_id" or 
                col1_name == f"{table2_name_lower}id" or
                col1_name.endswith(f"_{table2_name_lower}_id")):
                
                # Look for matching primary key in table2
                for col2 in table2.columns:
                    if col2.primary_key and self._types_compatible(col1.data_type, col2.data_type):
                        potential_fks.append({
                            'column': col1.name,
                            'references_column': col2.name,
                            'confidence': 0.9
                        })
            
            # Pattern 2: similar column names
            for col2 in table2.columns:
                if col2.primary_key:
                    similarity = 1 - (levenshtein(col1_name, col2.name.lower()) / max(len(col1_name), len(col2.name.lower())))
                    if similarity > 0.8 and self._types_compatible(col1.data_type, col2.data_type):
                        potential_fks.append({
                            'column': col1.name,
                            'references_column': col2.name,
                            'confidence': similarity * 0.7
                        })
        
        return potential_fks
    
    def _types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two data types are compatible for foreign key relationship."""
        # Normalize types
        type1 = type1.upper().split('(')[0]
        type2 = type2.upper().split('(')[0]
        
        # Integer types
        int_types = {'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT'}
        if type1 in int_types and type2 in int_types:
            return True
        
        # String types
        string_types = {'VARCHAR', 'CHAR', 'TEXT'}
        if type1 in string_types and type2 in string_types:
            return True
        
        # Exact match
        return type1 == type2

    def _relationship_exists(self, table1: str, col1: str, table2: str, col2: str) -> bool:
        """Check if a relationship already exists."""
        for table_name, table in self.tables.items():
            if table_name == table1:
                for fk in table.foreign_keys:
                    if (fk['column'] == col1 and
                        fk['references_table'] == table2 and
                        fk['references_column'] == col2):
                        return True
        return False

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

    def _identify_missing_tables(self) -> List[MissingTable]:
        """Identify potentially missing tables based on schema patterns."""
        missing_tables = []
        existing_table_names = set(table.lower() for table in self.tables.keys())

        # Check for common patterns
        for table_name, table in self.tables.items():
            table_name_lower = table_name.lower()

            # Check against common patterns
            for pattern, related_tables in self.COMMON_PATTERNS.items():
                if pattern in table_name_lower:
                    for related_table in related_tables:
                        if related_table not in existing_table_names:
                            missing_table = self._suggest_missing_table(
                                related_table, table_name, table.business_domain
                            )
                            if missing_table:
                                missing_tables.append(missing_table)

        # Check for missing junction tables
        missing_tables.extend(self._identify_missing_junction_tables())

        # Check for missing audit tables
        missing_tables.extend(self._identify_missing_audit_tables())

        return missing_tables

    def _suggest_missing_table(self, suggested_name: str, related_table: str, domain: BusinessDomain) -> Optional[MissingTable]:
        """Suggest a missing table based on patterns."""
        # Generate suggested columns based on the table type
        suggested_columns = []

        if suggested_name in ['profile', 'detail']:
            suggested_columns = [
                {'name': 'id', 'type': 'INT', 'constraint': 'PRIMARY KEY AUTO_INCREMENT'},
                {'name': f'{related_table.lower()}_id', 'type': 'INT', 'constraint': 'NOT NULL'},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'constraint': 'DEFAULT CURRENT_TIMESTAMP'},
                {'name': 'updated_at', 'type': 'TIMESTAMP', 'constraint': 'DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'}
            ]
        elif suggested_name in ['address', 'contact']:
            suggested_columns = [
                {'name': 'id', 'type': 'INT', 'constraint': 'PRIMARY KEY AUTO_INCREMENT'},
                {'name': f'{related_table.lower()}_id', 'type': 'INT', 'constraint': 'NOT NULL'},
                {'name': 'type', 'type': 'VARCHAR(50)', 'constraint': 'NOT NULL'},
                {'name': 'is_primary', 'type': 'BOOLEAN', 'constraint': 'DEFAULT FALSE'}
            ]
        elif suggested_name in ['log', 'audit', 'history']:
            suggested_columns = [
                {'name': 'id', 'type': 'INT', 'constraint': 'PRIMARY KEY AUTO_INCREMENT'},
                {'name': 'table_name', 'type': 'VARCHAR(100)', 'constraint': 'NOT NULL'},
                {'name': 'record_id', 'type': 'INT', 'constraint': 'NOT NULL'},
                {'name': 'action', 'type': 'ENUM("INSERT","UPDATE","DELETE")', 'constraint': 'NOT NULL'},
                {'name': 'timestamp', 'type': 'TIMESTAMP', 'constraint': 'DEFAULT CURRENT_TIMESTAMP'},
                {'name': 'user_id', 'type': 'INT', 'constraint': 'NULL'}
            ]
        else:
            # Generic table structure
            suggested_columns = [
                {'name': 'id', 'type': 'INT', 'constraint': 'PRIMARY KEY AUTO_INCREMENT'},
                {'name': 'name', 'type': 'VARCHAR(255)', 'constraint': 'NOT NULL'},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'constraint': 'DEFAULT CURRENT_TIMESTAMP'}
            ]

        return MissingTable(
            suggested_name=suggested_name,
            purpose=f"Related to {related_table} for {domain.value.lower()} operations",
            business_domain=domain,
            suggested_columns=suggested_columns,
            relationships=[f"References {related_table}"],
            confidence=0.7,
            reasoning=f"Common pattern suggests {suggested_name} table for {related_table}"
        )

    def _identify_missing_junction_tables(self) -> List[MissingTable]:
        """Identify missing junction tables for many-to-many relationships."""
        missing_junction_tables = []
        table_names = list(self.tables.keys())

        # Check common junction patterns
        for pattern in self.JUNCTION_PATTERNS:
            table1_pattern, table2_pattern, junction_name = pattern

            # Find tables matching the patterns
            matching_table1 = None
            matching_table2 = None

            for table_name in table_names:
                if table1_pattern in table_name.lower():
                    matching_table1 = table_name
                if table2_pattern in table_name.lower():
                    matching_table2 = table_name

            # If both tables exist but junction doesn't
            if (matching_table1 and matching_table2 and
                junction_name not in [t.lower() for t in table_names]):

                junction_table = MissingTable(
                    suggested_name=junction_name,
                    purpose=f"Junction table for many-to-many relationship between {matching_table1} and {matching_table2}",
                    business_domain=self.tables[matching_table1].business_domain,
                    suggested_columns=[
                        {'name': 'id', 'type': 'INT', 'constraint': 'PRIMARY KEY AUTO_INCREMENT'},
                        {'name': f'{matching_table1.lower()}_id', 'type': 'INT', 'constraint': 'NOT NULL'},
                        {'name': f'{matching_table2.lower()}_id', 'type': 'INT', 'constraint': 'NOT NULL'},
                        {'name': 'created_at', 'type': 'TIMESTAMP', 'constraint': 'DEFAULT CURRENT_TIMESTAMP'}
                    ],
                    relationships=[f"References {matching_table1}", f"References {matching_table2}"],
                    confidence=0.8,
                    reasoning=f"Many-to-many relationship pattern between {matching_table1} and {matching_table2}"
                )
                missing_junction_tables.append(junction_table)

        return missing_junction_tables

    def _identify_missing_audit_tables(self) -> List[MissingTable]:
        """Identify missing audit/log tables."""
        missing_audit_tables = []

        # Check if there are any audit tables
        has_audit_table = any('audit' in table.lower() or 'log' in table.lower()
                             for table in self.tables.keys())

        if not has_audit_table and len(self.tables) > 5:
            # Suggest a general audit table
            audit_table = MissingTable(
                suggested_name="audit_log",
                purpose="Track changes to all tables for compliance and debugging",
                business_domain=BusinessDomain.AUDIT,
                suggested_columns=[
                    {'name': 'id', 'type': 'INT', 'constraint': 'PRIMARY KEY AUTO_INCREMENT'},
                    {'name': 'table_name', 'type': 'VARCHAR(100)', 'constraint': 'NOT NULL'},
                    {'name': 'record_id', 'type': 'INT', 'constraint': 'NOT NULL'},
                    {'name': 'action', 'type': 'ENUM("INSERT","UPDATE","DELETE")', 'constraint': 'NOT NULL'},
                    {'name': 'old_values', 'type': 'JSON', 'constraint': 'NULL'},
                    {'name': 'new_values', 'type': 'JSON', 'constraint': 'NULL'},
                    {'name': 'user_id', 'type': 'INT', 'constraint': 'NULL'},
                    {'name': 'timestamp', 'type': 'TIMESTAMP', 'constraint': 'DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'ip_address', 'type': 'VARCHAR(45)', 'constraint': 'NULL'}
                ],
                relationships=["Can reference any table"],
                confidence=0.9,
                reasoning="Large schema without audit trail - recommended for compliance and debugging"
            )
            missing_audit_tables.append(audit_table)

        return missing_audit_tables

    def _generate_optimizations(self) -> List[SchemaOptimization]:
        """Generate schema optimization suggestions."""
        optimizations = []

        # Check for normalization issues
        optimizations.extend(self._check_normalization_issues())

        # Check for indexing opportunities
        optimizations.extend(self._check_indexing_opportunities())

        # Check for performance issues
        optimizations.extend(self._check_performance_issues())

        return optimizations

    def _check_normalization_issues(self) -> List[SchemaOptimization]:
        """Check for normalization issues."""
        optimizations = []

        for table_name, table in self.tables.items():
            # Check for potential 1NF violations (repeating groups)
            column_names = [col.name.lower() for col in table.columns]

            # Look for numbered columns (e.g., phone1, phone2, phone3)
            numbered_columns = defaultdict(list)
            for col_name in column_names:
                match = re.match(r'(.+?)(\d+)$', col_name)
                if match:
                    base_name, number = match.groups()
                    numbered_columns[base_name].append(col_name)

            for base_name, cols in numbered_columns.items():
                if len(cols) > 1:
                    optimization = SchemaOptimization(
                        optimization_type=OptimizationType.NORMALIZATION,
                        target_table=table_name,
                        description=f"Normalize repeating columns: {', '.join(cols)}",
                        suggested_changes=[
                            f"Create separate table for {base_name} values",
                            f"Remove columns: {', '.join(cols)}",
                            f"Add foreign key relationship"
                        ],
                        expected_benefit="Improved data integrity and flexibility",
                        complexity="Medium",
                        priority=7
                    )
                    optimizations.append(optimization)

        return optimizations

    def _check_indexing_opportunities(self) -> List[SchemaOptimization]:
        """Check for indexing opportunities."""
        optimizations = []

        for table_name, table in self.tables.items():
            # Suggest indexes for foreign key columns
            for fk in table.foreign_keys:
                optimization = SchemaOptimization(
                    optimization_type=OptimizationType.INDEXING,
                    target_table=table_name,
                    description=f"Add index on foreign key column: {fk['column']}",
                    suggested_changes=[
                        f"CREATE INDEX idx_{table_name}_{fk['column']} ON {table_name}({fk['column']})"
                    ],
                    expected_benefit="Improved JOIN performance",
                    complexity="Low",
                    priority=8
                )
                optimizations.append(optimization)

        return optimizations

    def _check_performance_issues(self) -> List[SchemaOptimization]:
        """Check for performance-related issues."""
        optimizations = []

        for table_name, table in self.tables.items():
            # Check for tables with many columns (potential for vertical partitioning)
            if len(table.columns) > 20:
                optimization = SchemaOptimization(
                    optimization_type=OptimizationType.PARTITIONING,
                    target_table=table_name,
                    description=f"Consider vertical partitioning - table has {len(table.columns)} columns",
                    suggested_changes=[
                        "Identify frequently accessed columns",
                        "Create separate table for less frequently accessed columns",
                        "Maintain 1:1 relationship between tables"
                    ],
                    expected_benefit="Reduced I/O and improved cache efficiency",
                    complexity="High",
                    priority=5
                )
                optimizations.append(optimization)

        return optimizations

    def _calculate_data_integrity_score(self) -> float:
        """Calculate data integrity score (0-100)."""
        if not self.tables:
            return 0.0

        total_tables = len(self.tables)
        tables_with_pk = sum(1 for table in self.tables.values() if table.primary_keys)
        tables_with_fk = sum(1 for table in self.tables.values() if table.foreign_keys)

        # Calculate score based on primary keys and foreign keys
        pk_score = (tables_with_pk / total_tables) * 50
        fk_score = min((tables_with_fk / max(1, total_tables - 1)) * 50, 50)

        return pk_score + fk_score

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
