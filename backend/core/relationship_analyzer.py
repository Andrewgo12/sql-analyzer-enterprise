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
    
    def _parse_tables_and_columns(self, sql_content: str):
        """Parse table and column definitions from SQL."""
        
        # Pattern for CREATE TABLE statements
        table_pattern = r'CREATE\s+TABLE\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?\s*\((.*?)\)'
        
        for match in re.finditer(table_pattern, sql_content, re.IGNORECASE | re.DOTALL):
            schema = match.group(1) or "dbo"
            table_name = match.group(2)
            columns_def = match.group(3)
            
            table = Table(name=table_name, schema=schema)
            
            # Parse columns
            self._parse_columns(columns_def, table)
            
            self.tables[table_name] = table
    
    def _parse_columns(self, columns_def: str, table: Table):
        """Parse column definitions."""
        
        # Split by commas, but be careful with nested parentheses
        column_lines = self._split_column_definitions(columns_def)
        
        for line in column_lines:
            line = line.strip()
            if not line or line.upper().startswith(('CONSTRAINT', 'PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK')):
                continue
            
            column = self._parse_single_column(line)
            if column:
                table.columns.append(column)
    
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
    
    def _parse_single_column(self, column_def: str) -> Optional[Column]:
        """Parse a single column definition."""
        
        # Basic column pattern: [column_name] [data_type] [constraints]
        parts = column_def.strip().split()
        if len(parts) < 2:
            return None
        
        column_name = parts[0].strip('[]')
        data_type = parts[1].upper()
        
        # Extract data type details
        type_match = re.match(r'(\w+)(?:\((\d+)(?:,(\d+))?\))?', data_type)
        if not type_match:
            return None
        
        base_type = type_match.group(1)
        max_length = int(type_match.group(2)) if type_match.group(2) else None
        scale = int(type_match.group(3)) if type_match.group(3) else None
        
        # Check for nullable
        nullable = "NOT NULL" not in column_def.upper()
        
        # Check for identity
        is_identity = "IDENTITY" in column_def.upper()
        
        # Extract default value
        default_match = re.search(r'DEFAULT\s+([^,\s]+)', column_def, re.IGNORECASE)
        default_value = default_match.group(1) if default_match else None
        
        return Column(
            name=column_name,
            data_type=base_type,
            nullable=nullable,
            default_value=default_value,
            max_length=max_length,
            scale=scale,
            is_identity=is_identity
        )
    
    def _parse_constraints(self, sql_content: str):
        """Parse constraint definitions from SQL."""
        
        # Parse ALTER TABLE ADD CONSTRAINT statements
        constraint_pattern = r'ALTER\s+TABLE\s+\[?(\w+)\]?\s+ADD\s+CONSTRAINT\s+\[?(\w+)\]?\s+(.*?)(?=;|$)'
        
        for match in re.finditer(constraint_pattern, sql_content, re.IGNORECASE | re.DOTALL):
            table_name = match.group(1)
            constraint_name = match.group(2)
            constraint_def = match.group(3).strip()
            
            constraint = self._parse_constraint_definition(table_name, constraint_name, constraint_def)
            if constraint and table_name in self.tables:
                self.tables[table_name].constraints.append(constraint)
        
        # Parse inline constraints in CREATE TABLE
        for table_name, table in self.tables.items():
            self._parse_inline_constraints(table)
    
    def _parse_constraint_definition(self, table_name: str, constraint_name: str, constraint_def: str) -> Optional[Constraint]:
        """Parse a constraint definition."""
        
        constraint_def_upper = constraint_def.upper()
        
        if constraint_def_upper.startswith('PRIMARY KEY'):
            # PRIMARY KEY (column1, column2)
            columns_match = re.search(r'\((.*?)\)', constraint_def)
            if columns_match:
                columns = [col.strip().strip('[]') for col in columns_match.group(1).split(',')]
                return Constraint(
                    name=constraint_name,
                    type=ConstraintType.PRIMARY_KEY,
                    table_name=table_name,
                    columns=columns
                )
        
        elif constraint_def_upper.startswith('FOREIGN KEY'):
            # FOREIGN KEY (column) REFERENCES table(column)
            fk_match = re.search(r'FOREIGN\s+KEY\s*\((.*?)\)\s+REFERENCES\s+\[?(\w+)\]?\s*\((.*?)\)', constraint_def, re.IGNORECASE)
            if fk_match:
                columns = [col.strip().strip('[]') for col in fk_match.group(1).split(',')]
                ref_table = fk_match.group(2)
                ref_columns = [col.strip().strip('[]') for col in fk_match.group(3).split(',')]
                
                # Parse ON DELETE/UPDATE actions
                on_delete = None
                on_update = None
                
                delete_match = re.search(r'ON\s+DELETE\s+(\w+)', constraint_def, re.IGNORECASE)
                if delete_match:
                    on_delete = delete_match.group(1).upper()
                
                update_match = re.search(r'ON\s+UPDATE\s+(\w+)', constraint_def, re.IGNORECASE)
                if update_match:
                    on_update = update_match.group(1).upper()
                
                return Constraint(
                    name=constraint_name,
                    type=ConstraintType.FOREIGN_KEY,
                    table_name=table_name,
                    columns=columns,
                    referenced_table=ref_table,
                    referenced_columns=ref_columns,
                    on_delete=on_delete,
                    on_update=on_update
                )
        
        elif constraint_def_upper.startswith('UNIQUE'):
            # UNIQUE (column1, column2)
            columns_match = re.search(r'\((.*?)\)', constraint_def)
            if columns_match:
                columns = [col.strip().strip('[]') for col in columns_match.group(1).split(',')]
                return Constraint(
                    name=constraint_name,
                    type=ConstraintType.UNIQUE,
                    table_name=table_name,
                    columns=columns
                )
        
        elif constraint_def_upper.startswith('CHECK'):
            # CHECK (expression)
            check_match = re.search(r'CHECK\s*\((.*)\)', constraint_def, re.IGNORECASE)
            if check_match:
                return Constraint(
                    name=constraint_name,
                    type=ConstraintType.CHECK,
                    table_name=table_name,
                    columns=[],
                    check_expression=check_match.group(1)
                )
        
        return None
    
    def _parse_inline_constraints(self, table: Table):
        """Parse inline constraints from table definition."""
        # This would be implemented to parse constraints defined inline with columns
        pass
    
    def _analyze_relationships(self):
        """Analyze relationships between tables."""
        
        for table_name, table in self.tables.items():
            for fk_constraint in table.get_foreign_keys():
                relationship = self._create_relationship_from_fk(fk_constraint)
                if relationship:
                    self.relationships.append(relationship)
    
    def _create_relationship_from_fk(self, fk_constraint: Constraint) -> Optional[Relationship]:
        """Create a relationship from a foreign key constraint."""
        
        if not fk_constraint.referenced_table:
            return None
        
        # Determine relationship type
        rel_type = self._determine_relationship_type(fk_constraint)
        
        return Relationship(
            name=f"{fk_constraint.table_name}_{fk_constraint.referenced_table}",
            type=rel_type,
            parent_table=fk_constraint.referenced_table,
            child_table=fk_constraint.table_name,
            parent_columns=fk_constraint.referenced_columns or [],
            child_columns=fk_constraint.columns,
            constraint_name=fk_constraint.name,
            on_delete=fk_constraint.on_delete,
            on_update=fk_constraint.on_update
        )
    
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
    
    def _detect_orphaned_tables(self):
        """Detect tables with no relationships."""
        
        referenced_tables = set()
        referencing_tables = set()
        
        for relationship in self.relationships:
            referenced_tables.add(relationship.parent_table)
            referencing_tables.add(relationship.child_table)
        
        all_related_tables = referenced_tables | referencing_tables
        
        self.orphaned_tables = [
            table_name for table_name in self.tables.keys()
            if table_name not in all_related_tables
        ]
    
    def _detect_circular_references(self):
        """Detect circular references in relationships."""
        
        # Build adjacency list
        graph = {}
        for relationship in self.relationships:
            if relationship.parent_table not in graph:
                graph[relationship.parent_table] = []
            graph[relationship.parent_table].append(relationship.child_table)
        
        # Find cycles using DFS
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in self.circular_references:
                    self.circular_references.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for table in self.tables.keys():
            if table not in visited:
                dfs(table, [])
    
    def _calculate_schema_metrics(self) -> Dict[str, Any]:
        """Calculate schema quality metrics."""
        
        total_tables = len(self.tables)
        total_relationships = len(self.relationships)
        total_orphaned = len(self.orphaned_tables)
        total_circular = len(self.circular_references)
        
        # Calculate relationship density
        max_possible_relationships = total_tables * (total_tables - 1)
        relationship_density = total_relationships / max_possible_relationships if max_possible_relationships > 0 else 0
        
        # Calculate normalization score (simplified)
        normalization_score = self._calculate_normalization_score()
        
        return {
            "total_tables": total_tables,
            "total_relationships": total_relationships,
            "orphaned_tables_count": total_orphaned,
            "circular_references_count": total_circular,
            "relationship_density": round(relationship_density, 3),
            "normalization_score": normalization_score,
            "schema_complexity": self._calculate_schema_complexity()
        }
    
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
    
    def _generate_schema_recommendations(self) -> List[Dict[str, str]]:
        """Generate schema improvement recommendations."""
        
        recommendations = []
        
        # Check for missing primary keys
        for table_name, table in self.tables.items():
            if not table.get_primary_key_columns():
                recommendations.append({
                    "type": "missing_primary_key",
                    "severity": "HIGH",
                    "table": table_name,
                    "description": f"La tabla '{table_name}' no tiene clave primaria definida",
                    "recommendation": "Agregar una clave primaria para garantizar la integridad de los datos"
                })
        
        # Check for orphaned tables
        for table_name in self.orphaned_tables:
            recommendations.append({
                "type": "orphaned_table",
                "severity": "MEDIUM",
                "table": table_name,
                "description": f"La tabla '{table_name}' no tiene relaciones con otras tablas",
                "recommendation": "Revisar si esta tabla debería tener relaciones o si es realmente independiente"
            })
        
        # Check for circular references
        for cycle in self.circular_references:
            recommendations.append({
                "type": "circular_reference",
                "severity": "HIGH",
                "tables": cycle,
                "description": f"Referencia circular detectada: {' -> '.join(cycle)}",
                "recommendation": "Revisar el diseño para eliminar dependencias circulares"
            })
        
        return recommendations
    
    def _table_to_dict(self, table: Table) -> Dict[str, Any]:
        """Convert table to dictionary."""
        return {
            "name": table.name,
            "schema": table.schema,
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type,
                    "nullable": col.nullable,
                    "default_value": col.default_value,
                    "max_length": col.max_length,
                    "is_identity": col.is_identity
                }
                for col in table.columns
            ],
            "constraints": [
                {
                    "name": const.name,
                    "type": const.type.value,
                    "columns": const.columns,
                    "referenced_table": const.referenced_table,
                    "referenced_columns": const.referenced_columns
                }
                for const in table.constraints
            ],
            "primary_key_columns": table.get_primary_key_columns(),
            "foreign_key_count": len(table.get_foreign_keys())
        }
    
    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Convert relationship to dictionary."""
        return {
            "name": relationship.name,
            "type": relationship.type.value,
            "parent_table": relationship.parent_table,
            "child_table": relationship.child_table,
            "parent_columns": relationship.parent_columns,
            "child_columns": relationship.child_columns,
            "constraint_name": relationship.constraint_name,
            "on_delete": relationship.on_delete,
            "on_update": relationship.on_update
        }
