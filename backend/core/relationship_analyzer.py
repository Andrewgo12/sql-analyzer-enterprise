"""
Database Relationship Analyzer
Advanced analysis of database relationships, foreign keys, and schema dependencies
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum


class RelationshipType(Enum):
    """Types of database relationships."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    SELF_REFERENCING = "self_referencing"


class ConstraintType(Enum):
    """Types of database constraints."""
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    CHECK = "check"
    NOT_NULL = "not_null"
    DEFAULT = "default"


@dataclass
class Column:
    """Database column representation."""
    name: str
    data_type: str
    nullable: bool = True
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_identity: bool = False
    is_computed: bool = False


@dataclass
class Constraint:
    """Database constraint representation."""
    name: str
    type: ConstraintType
    table_name: str
    columns: List[str]
    referenced_table: Optional[str] = None
    referenced_columns: Optional[List[str]] = None
    on_delete: Optional[str] = None
    on_update: Optional[str] = None
    check_expression: Optional[str] = None


@dataclass
class Table:
    """Database table representation."""
    name: str
    schema: str = "dbo"
    columns: List[Column] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    estimated_rows: int = 0
    
    def get_primary_key_columns(self) -> List[str]:
        """Get primary key columns."""
        for constraint in self.constraints:
            if constraint.type == ConstraintType.PRIMARY_KEY:
                return constraint.columns
        return []
    
    def get_foreign_keys(self) -> List[Constraint]:
        """Get foreign key constraints."""
        return [c for c in self.constraints if c.type == ConstraintType.FOREIGN_KEY]


@dataclass
class Relationship:
    """Database relationship representation."""
    name: str
    type: RelationshipType
    parent_table: str
    child_table: str
    parent_columns: List[str]
    child_columns: List[str]
    constraint_name: Optional[str] = None
    on_delete: Optional[str] = None
    on_update: Optional[str] = None
    cardinality_estimate: Optional[str] = None


class RelationshipAnalyzer:
    """Advanced database relationship analyzer."""
    
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Relationship] = []
        self.orphaned_tables: List[str] = []
        self.circular_references: List[List[str]] = []
        
    def analyze_sql_content(self, sql_content: str) -> Dict[str, Any]:
        """Analyze SQL content for relationships and schema structure."""
        
        # Parse SQL content
        self._parse_tables_and_columns(sql_content)
        self._parse_constraints(sql_content)
        self._analyze_relationships()
        self._detect_orphaned_tables()
        self._detect_circular_references()
        
        return {
            "tables": {name: self._table_to_dict(table) for name, table in self.tables.items()},
            "relationships": [self._relationship_to_dict(rel) for rel in self.relationships],
            "orphaned_tables": self.orphaned_tables,
            "circular_references": self.circular_references,
            "schema_metrics": self._calculate_schema_metrics(),
            "recommendations": self._generate_schema_recommendations()
        }
    
    def _split_column_definitions(self, columns_def: str) -> List[str]:
        """Split column definitions handling nested parentheses."""
        lines = []
        current_line = ""
        paren_count = 0
        
        for char in columns_def:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                lines.append(current_line.strip())
                current_line = ""
                continue
            
            current_line += char
        
        if current_line.strip():
            lines.append(current_line.strip())
        
        return lines
    
    def _determine_relationship_type(self, fk_constraint: Constraint) -> RelationshipType:
        """Determine the type of relationship."""
        
        # Check if it's self-referencing
        if fk_constraint.table_name == fk_constraint.referenced_table:
            return RelationshipType.SELF_REFERENCING
        
        # Check if child table has unique constraint on FK columns
        child_table = self.tables.get(fk_constraint.table_name)
        if child_table:
            for constraint in child_table.constraints:
                if (constraint.type in [ConstraintType.UNIQUE, ConstraintType.PRIMARY_KEY] and
                    set(constraint.columns) == set(fk_constraint.columns)):
                    return RelationshipType.ONE_TO_ONE
        
        # Default to one-to-many
        return RelationshipType.ONE_TO_MANY
    
    def _calculate_normalization_score(self) -> float:
        """Calculate a simplified normalization score."""
        
        score = 1.0
        
        # Penalize for missing primary keys
        tables_without_pk = 0
        for table in self.tables.values():
            if not table.get_primary_key_columns():
                tables_without_pk += 1
        
        if self.tables:
            pk_penalty = (tables_without_pk / len(self.tables)) * 0.3
            score -= pk_penalty
        
        # Penalize for orphaned tables
        if self.tables:
            orphan_penalty = (len(self.orphaned_tables) / len(self.tables)) * 0.2
            score -= orphan_penalty
        
        # Penalize for circular references
        circular_penalty = len(self.circular_references) * 0.1
        score -= circular_penalty
        
        return max(0.0, min(1.0, score))
    
    def _calculate_schema_complexity(self) -> str:
        """Calculate schema complexity level."""
        
        total_tables = len(self.tables)
        total_relationships = len(self.relationships)
        
        if total_tables <= 5 and total_relationships <= 5:
            return "Simple"
        elif total_tables <= 15 and total_relationships <= 20:
            return "Medium"
        elif total_tables <= 50 and total_relationships <= 100:
            return "Complex"
        else:
            return "Very Complex"
    
