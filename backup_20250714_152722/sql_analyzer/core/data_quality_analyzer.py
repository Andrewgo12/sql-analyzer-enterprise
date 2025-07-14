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
    
    def _initialize_naming_conventions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize naming convention rules."""
        return {
            "table_naming": {
                "pattern": r"^[a-z][a-z0-9_]*[a-z0-9]$",
                "description": "Nombres de tabla en minúsculas con guiones bajos",
                "examples": ["users", "order_items", "customer_addresses"]
            },
            "column_naming": {
                "pattern": r"^[a-z][a-z0-9_]*[a-z0-9]$",
                "description": "Nombres de columna en minúsculas con guiones bajos",
                "examples": ["user_id", "first_name", "created_at"]
            },
            "primary_key_naming": {
                "pattern": r"^(id|.*_id)$",
                "description": "Claves primarias deben terminar en '_id' o ser 'id'",
                "examples": ["id", "user_id", "order_id"]
            },
            "foreign_key_naming": {
                "pattern": r"^.*_id$",
                "description": "Claves foráneas deben terminar en '_id'",
                "examples": ["user_id", "category_id", "parent_id"]
            },
            "boolean_naming": {
                "pattern": r"^(is_|has_|can_|should_|will_).*",
                "description": "Columnas booleanas deben usar prefijos descriptivos",
                "examples": ["is_active", "has_children", "can_edit"]
            },
            "date_naming": {
                "pattern": r".*(date|time|at)$",
                "description": "Columnas de fecha/hora deben indicar temporalidad",
                "examples": ["created_at", "updated_at", "birth_date"]
            }
        }
    
    def _initialize_data_type_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data type validation rules."""
        return {
            "email_columns": {
                "pattern": r"email",
                "expected_type": "VARCHAR",
                "min_length": 50,
                "constraints": ["CHECK constraint for email format"]
            },
            "phone_columns": {
                "pattern": r"phone",
                "expected_type": "VARCHAR",
                "min_length": 20,
                "constraints": ["CHECK constraint for phone format"]
            },
            "currency_columns": {
                "pattern": r"(price|cost|amount|salary)",
                "expected_type": "DECIMAL",
                "precision": 10,
                "scale": 2,
                "constraints": ["CHECK constraint for positive values"]
            },
            "percentage_columns": {
                "pattern": r"(rate|percent|ratio)",
                "expected_type": "DECIMAL",
                "precision": 5,
                "scale": 4,
                "constraints": ["CHECK constraint for 0-100 range"]
            },
            "id_columns": {
                "pattern": r".*_id$|^id$",
                "expected_type": "INT",
                "constraints": ["PRIMARY KEY or FOREIGN KEY constraint"]
            }
        }
    
    def _initialize_business_rules(self) -> List[Dict[str, Any]]:
        """Initialize business rule validations."""
        return [
            {
                "name": "audit_columns",
                "description": "Tablas deben tener columnas de auditoría",
                "required_columns": ["created_at", "updated_at"],
                "optional_columns": ["created_by", "updated_by"],
                "severity": QualitySeverity.MEDIUM
            },
            {
                "name": "soft_delete",
                "description": "Tablas principales deben soportar soft delete",
                "required_columns": ["is_deleted", "deleted_at"],
                "table_patterns": [r"users", r"orders", r"products"],
                "severity": QualitySeverity.LOW
            },
            {
                "name": "version_control",
                "description": "Tablas críticas deben tener control de versiones",
                "required_columns": ["version", "row_version"],
                "table_patterns": [r".*_master", r"configurations"],
                "severity": QualitySeverity.MEDIUM
            }
        ]
    
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
    
    def _parse_schema_from_sql(self, sql_content: str) -> Dict[str, Dict[str, Any]]:
        """Parse schema information from SQL content."""
        
        tables = {}
        
        # Parse CREATE TABLE statements
        table_pattern = r'CREATE\s+TABLE\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?\s*\((.*?)\)'
        
        for match in re.finditer(table_pattern, sql_content, re.IGNORECASE | re.DOTALL):
            schema = match.group(1) or "dbo"
            table_name = match.group(2)
            columns_def = match.group(3)
            
            table_info = {
                "name": table_name,
                "schema": schema,
                "columns": self._parse_columns_for_quality(columns_def),
                "constraints": self._parse_constraints_for_quality(columns_def),
                "indexes": []
            }
            
            tables[table_name] = table_info
        
        return tables
    
    def _parse_columns_for_quality(self, columns_def: str) -> List[Dict[str, Any]]:
        """Parse column definitions for quality analysis."""
        
        columns = []
        lines = [line.strip() for line in columns_def.split(',') if line.strip()]
        
        for line in lines:
            if line.upper().startswith(('CONSTRAINT', 'PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK')):
                continue
            
            # Basic column parsing
            parts = line.strip().split()
            if len(parts) >= 2:
                column_name = parts[0].strip('[]')
                data_type = parts[1].upper()
                
                # Extract additional properties
                nullable = "NOT NULL" not in line.upper()
                has_default = "DEFAULT" in line.upper()
                is_identity = "IDENTITY" in line.upper()
                
                columns.append({
                    "name": column_name,
                    "data_type": data_type,
                    "nullable": nullable,
                    "has_default": has_default,
                    "is_identity": is_identity,
                    "definition": line
                })
        
        return columns
    
    def _parse_constraints_for_quality(self, columns_def: str) -> List[Dict[str, Any]]:
        """Parse constraint definitions for quality analysis."""
        
        constraints = []
        
        # Look for constraint definitions
        constraint_patterns = [
            (r'PRIMARY\s+KEY\s*\((.*?)\)', 'PRIMARY_KEY'),
            (r'FOREIGN\s+KEY\s*\((.*?)\)', 'FOREIGN_KEY'),
            (r'UNIQUE\s*\((.*?)\)', 'UNIQUE'),
            (r'CHECK\s*\((.*?)\)', 'CHECK')
        ]
        
        for pattern, constraint_type in constraint_patterns:
            for match in re.finditer(pattern, columns_def, re.IGNORECASE):
                constraints.append({
                    "type": constraint_type,
                    "definition": match.group(0),
                    "columns": [col.strip().strip('[]') for col in match.group(1).split(',')]
                })
        
        return constraints
    
    def _check_naming_conventions(self, tables: Dict[str, Dict[str, Any]]) -> List[QualityIssue]:
        """Check naming convention compliance."""
        
        issues = []
        
        for table_name, table_info in tables.items():
            # Check table naming
            table_pattern = self.naming_conventions["table_naming"]["pattern"]
            if not re.match(table_pattern, table_name):
                issues.append(QualityIssue(
                    type=QualityIssueType.INCONSISTENT_NAMING,
                    severity=QualitySeverity.MEDIUM,
                    title="Convención de nombres de tabla",
                    description=f"La tabla '{table_name}' no sigue la convención de nombres",
                    table_name=table_name,
                    recommendation=self.naming_conventions["table_naming"]["description"],
                    fix_sql=f"-- Renombrar tabla a: {self._suggest_table_name(table_name)}"
                ))
            
            # Check column naming
            for column in table_info["columns"]:
                column_name = column["name"]
                column_pattern = self.naming_conventions["column_naming"]["pattern"]
                
                if not re.match(column_pattern, column_name):
                    issues.append(QualityIssue(
                        type=QualityIssueType.INCONSISTENT_NAMING,
                        severity=QualitySeverity.LOW,
                        title="Convención de nombres de columna",
                        description=f"La columna '{column_name}' no sigue la convención de nombres",
                        table_name=table_name,
                        column_name=column_name,
                        recommendation=self.naming_conventions["column_naming"]["description"]
                    ))
                
                # Check specific naming patterns
                self._check_specific_naming_patterns(column, table_name, issues)
        
        return issues
    
    def _check_specific_naming_patterns(self, column: Dict[str, Any], table_name: str, issues: List[QualityIssue]):
        """Check specific naming patterns for different column types."""
        
        column_name = column["name"]
        data_type = column["data_type"]
        
        # Check boolean naming
        if data_type in ["BIT", "BOOLEAN"]:
            boolean_pattern = self.naming_conventions["boolean_naming"]["pattern"]
            if not re.match(boolean_pattern, column_name):
                issues.append(QualityIssue(
                    type=QualityIssueType.INCONSISTENT_NAMING,
                    severity=QualitySeverity.LOW,
                    title="Convención de nombres booleanos",
                    description=f"La columna booleana '{column_name}' debería usar un prefijo descriptivo",
                    table_name=table_name,
                    column_name=column_name,
                    recommendation="Usar prefijos como 'is_', 'has_', 'can_', etc."
                ))
        
        # Check date/time naming
        if data_type in ["DATETIME", "TIMESTAMP", "DATE", "TIME"]:
            date_pattern = self.naming_conventions["date_naming"]["pattern"]
            if not re.match(date_pattern, column_name):
                issues.append(QualityIssue(
                    type=QualityIssueType.INCONSISTENT_NAMING,
                    severity=QualitySeverity.LOW,
                    title="Convención de nombres de fecha/hora",
                    description=f"La columna de fecha '{column_name}' debería indicar temporalidad",
                    table_name=table_name,
                    column_name=column_name,
                    recommendation="Usar sufijos como '_at', '_date', '_time'"
                ))
    
    def _check_data_types(self, tables: Dict[str, Dict[str, Any]]) -> List[QualityIssue]:
        """Check data type appropriateness."""
        
        issues = []
        
        for table_name, table_info in tables.items():
            for column in table_info["columns"]:
                column_name = column["name"]
                data_type = column["data_type"]
                
                # Check against data type rules
                for rule_name, rule_info in self.data_type_rules.items():
                    if re.search(rule_info["pattern"], column_name, re.IGNORECASE):
                        expected_type = rule_info["expected_type"]
                        
                        if not data_type.startswith(expected_type):
                            issues.append(QualityIssue(
                                type=QualityIssueType.DATA_TYPE_ISSUES,
                                severity=QualitySeverity.MEDIUM,
                                title="Tipo de dato inapropiado",
                                description=f"La columna '{column_name}' debería usar tipo {expected_type}",
                                table_name=table_name,
                                column_name=column_name,
                                recommendation=f"Cambiar tipo de dato a {expected_type}",
                                fix_sql=f"ALTER TABLE {table_name} ALTER COLUMN {column_name} {expected_type}"
                            ))
        
        return issues
    
    def _check_constraints(self, tables: Dict[str, Dict[str, Any]]) -> List[QualityIssue]:
        """Check constraint coverage and appropriateness."""
        
        issues = []
        
        for table_name, table_info in tables.items():
            constraints = table_info["constraints"]
            columns = table_info["columns"]
            
            # Check for missing primary key
            has_primary_key = any(c["type"] == "PRIMARY_KEY" for c in constraints)
            if not has_primary_key:
                issues.append(QualityIssue(
                    type=QualityIssueType.MISSING_CONSTRAINTS,
                    severity=QualitySeverity.HIGH,
                    title="Clave primaria faltante",
                    description=f"La tabla '{table_name}' no tiene clave primaria definida",
                    table_name=table_name,
                    recommendation="Agregar una clave primaria para garantizar unicidad",
                    fix_sql=f"ALTER TABLE {table_name} ADD CONSTRAINT PK_{table_name} PRIMARY KEY (id)"
                ))
            
            # Check for missing NOT NULL constraints on important columns
            for column in columns:
                if column["name"] in ["email", "username", "name"] and column["nullable"]:
                    issues.append(QualityIssue(
                        type=QualityIssueType.MISSING_CONSTRAINTS,
                        severity=QualitySeverity.MEDIUM,
                        title="Restricción NOT NULL faltante",
                        description=f"La columna '{column['name']}' debería ser NOT NULL",
                        table_name=table_name,
                        column_name=column["name"],
                        recommendation="Agregar restricción NOT NULL para datos críticos",
                        fix_sql=f"ALTER TABLE {table_name} ALTER COLUMN {column['name']} NOT NULL"
                    ))
        
        return issues
    
    def _check_normalization(self, tables: Dict[str, Dict[str, Any]]) -> List[QualityIssue]:
        """Check database normalization issues."""
        
        issues = []
        
        for table_name, table_info in tables.items():
            columns = table_info["columns"]
            
            # Check for potential denormalization (too many columns)
            if len(columns) > 20:
                issues.append(QualityIssue(
                    type=QualityIssueType.NORMALIZATION_ISSUES,
                    severity=QualitySeverity.MEDIUM,
                    title="Posible desnormalización",
                    description=f"La tabla '{table_name}' tiene {len(columns)} columnas, considerar normalización",
                    table_name=table_name,
                    recommendation="Revisar si la tabla puede dividirse en múltiples tablas relacionadas"
                ))
            
            # Check for repeated column patterns (potential normalization opportunity)
            column_names = [col["name"] for col in columns]
            repeated_patterns = self._find_repeated_patterns(column_names)
            
            for pattern in repeated_patterns:
                issues.append(QualityIssue(
                    type=QualityIssueType.NORMALIZATION_ISSUES,
                    severity=QualitySeverity.LOW,
                    title="Patrón de columnas repetido",
                    description=f"Patrón repetido '{pattern}' en tabla '{table_name}' sugiere oportunidad de normalización",
                    table_name=table_name,
                    recommendation="Considerar extraer columnas repetidas a tabla separada"
                ))
        
        return issues
    
    def _check_business_rules(self, tables: Dict[str, Dict[str, Any]]) -> List[QualityIssue]:
        """Check business rule compliance."""
        
        issues = []
        
        for rule in self.business_rules:
            for table_name, table_info in tables.items():
                # Check if rule applies to this table
                if "table_patterns" in rule:
                    applies = any(re.search(pattern, table_name, re.IGNORECASE) 
                                for pattern in rule["table_patterns"])
                    if not applies:
                        continue
                
                # Check required columns
                column_names = [col["name"] for col in table_info["columns"]]
                missing_columns = [col for col in rule["required_columns"] 
                                 if col not in column_names]
                
                if missing_columns:
                    issues.append(QualityIssue(
                        type=QualityIssueType.BUSINESS_RULE_VIOLATIONS,
                        severity=rule["severity"],
                        title=f"Regla de negocio: {rule['name']}",
                        description=f"Faltan columnas requeridas: {', '.join(missing_columns)}",
                        table_name=table_name,
                        recommendation=rule["description"],
                        fix_sql=self._generate_add_columns_sql(table_name, missing_columns)
                    ))
        
        return issues
    
    def _calculate_quality_metrics(self, issues: List[QualityIssue], tables: Dict[str, Dict[str, Any]]) -> QualityMetrics:
        """Calculate overall quality metrics."""
        
        total_issues = len(issues)
        critical_issues = len([i for i in issues if i.severity == QualitySeverity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == QualitySeverity.HIGH])
        medium_issues = len([i for i in issues if i.severity == QualitySeverity.MEDIUM])
        low_issues = len([i for i in issues if i.severity == QualitySeverity.LOW])
        
        # Calculate overall score (0-100)
        base_score = 100
        score_deductions = (critical_issues * 20) + (high_issues * 10) + (medium_issues * 5) + (low_issues * 2)
        overall_score = max(0, base_score - score_deductions)
        
        # Calculate specific metrics
        constraint_coverage = self._calculate_constraint_coverage(tables)
        naming_consistency = self._calculate_naming_consistency(issues)
        documentation_coverage = 0.8  # Placeholder
        normalization_score = self._calculate_normalization_score(issues)
        referential_integrity_score = self._calculate_referential_integrity_score(tables)
        
        return QualityMetrics(
            overall_score=overall_score,
            constraint_coverage=constraint_coverage,
            naming_consistency=naming_consistency,
            documentation_coverage=documentation_coverage,
            normalization_score=normalization_score,
            referential_integrity_score=referential_integrity_score,
            total_issues=total_issues,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues
        )
    
    def _calculate_constraint_coverage(self, tables: Dict[str, Dict[str, Any]]) -> float:
        """Calculate constraint coverage percentage."""
        
        total_tables = len(tables)
        tables_with_pk = sum(1 for table in tables.values() 
                           if any(c["type"] == "PRIMARY_KEY" for c in table["constraints"]))
        
        return (tables_with_pk / total_tables) * 100 if total_tables > 0 else 0
    
    def _calculate_naming_consistency(self, issues: List[QualityIssue]) -> float:
        """Calculate naming consistency percentage."""
        
        naming_issues = [i for i in issues if i.type == QualityIssueType.INCONSISTENT_NAMING]
        total_naming_checks = 100  # Placeholder for total naming checks performed
        
        consistency = ((total_naming_checks - len(naming_issues)) / total_naming_checks) * 100
        return max(0, consistency)
    
    def _calculate_normalization_score(self, issues: List[QualityIssue]) -> float:
        """Calculate normalization score."""
        
        normalization_issues = [i for i in issues if i.type == QualityIssueType.NORMALIZATION_ISSUES]
        base_score = 100
        
        return max(0, base_score - (len(normalization_issues) * 10))
    
    def _calculate_referential_integrity_score(self, tables: Dict[str, Dict[str, Any]]) -> float:
        """Calculate referential integrity score."""
        
        total_fk_opportunities = 0
        actual_fks = 0
        
        for table in tables.values():
            # Count potential foreign key columns (ending with _id)
            fk_candidates = [col for col in table["columns"] if col["name"].endswith("_id")]
            total_fk_opportunities += len(fk_candidates)
            
            # Count actual foreign key constraints
            actual_fks += len([c for c in table["constraints"] if c["type"] == "FOREIGN_KEY"])
        
        return (actual_fks / total_fk_opportunities) * 100 if total_fk_opportunities > 0 else 100
    
    def _suggest_table_name(self, table_name: str) -> str:
        """Suggest a better table name following conventions."""
        return re.sub(r'[A-Z]', lambda m: '_' + m.group(0).lower(), table_name).lstrip('_').lower()
    
    def _find_repeated_patterns(self, column_names: List[str]) -> List[str]:
        """Find repeated patterns in column names."""
        
        patterns = []
        
        # Look for numbered columns (column1, column2, etc.)
        numbered_pattern = r'(.+)(\d+)$'
        base_names = {}
        
        for name in column_names:
            match = re.match(numbered_pattern, name)
            if match:
                base_name = match.group(1)
                if base_name in base_names:
                    base_names[base_name] += 1
                else:
                    base_names[base_name] = 1
        
        patterns.extend([base for base, count in base_names.items() if count > 2])
        
        return patterns
    
    def _generate_add_columns_sql(self, table_name: str, columns: List[str]) -> str:
        """Generate SQL to add missing columns."""
        
        column_definitions = {
            "created_at": "DATETIME DEFAULT GETDATE()",
            "updated_at": "DATETIME DEFAULT GETDATE()",
            "created_by": "INT",
            "updated_by": "INT",
            "is_deleted": "BIT DEFAULT 0",
            "deleted_at": "DATETIME",
            "version": "INT DEFAULT 1",
            "row_version": "ROWVERSION"
        }
        
        sql_statements = []
        for column in columns:
            definition = column_definitions.get(column, "VARCHAR(255)")
            sql_statements.append(f"ALTER TABLE {table_name} ADD {column} {definition}")
        
        return ";\n".join(sql_statements) + ";"
    
    def _generate_quality_recommendations(self, issues: List[QualityIssue], metrics: QualityMetrics) -> List[str]:
        """Generate quality improvement recommendations."""
        
        recommendations = []
        
        if metrics.critical_issues > 0:
            recommendations.append("🚨 CRÍTICO: Resolver problemas críticos de calidad inmediatamente")
        
        if metrics.constraint_coverage < 80:
            recommendations.append("🔒 Mejorar cobertura de restricciones (claves primarias, NOT NULL)")
        
        if metrics.naming_consistency < 70:
            recommendations.append("📝 Estandarizar convenciones de nombres en toda la base de datos")
        
        if metrics.normalization_score < 80:
            recommendations.append("🔄 Revisar normalización de tablas con muchas columnas")
        
        if metrics.referential_integrity_score < 60:
            recommendations.append("🔗 Implementar más restricciones de integridad referencial")
        
        recommendations.extend([
            "📚 Documentar esquema de base de datos y reglas de negocio",
            "🧪 Implementar pruebas de calidad de datos automatizadas",
            "📊 Establecer métricas de calidad y monitoreo continuo",
            "🔍 Realizar revisiones regulares de calidad de esquema"
        ])
        
        return recommendations
    
    def _identify_improvement_areas(self, issues: List[QualityIssue]) -> List[str]:
        """Identify main areas for improvement."""
        
        issue_counts = {}
        for issue in issues:
            issue_type = issue.type.value
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Sort by frequency
        sorted_areas = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        area_names = {
            "missing_constraints": "Restricciones faltantes",
            "inconsistent_naming": "Convenciones de nombres",
            "data_type_issues": "Tipos de datos",
            "normalization_issues": "Normalización",
            "business_rule_violations": "Reglas de negocio"
        }
        
        return [area_names.get(area, area) for area, _ in sorted_areas[:3]]
    
    def _metrics_to_dict(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "overall_score": round(metrics.overall_score, 1),
            "constraint_coverage": round(metrics.constraint_coverage, 1),
            "naming_consistency": round(metrics.naming_consistency, 1),
            "documentation_coverage": round(metrics.documentation_coverage, 1),
            "normalization_score": round(metrics.normalization_score, 1),
            "referential_integrity_score": round(metrics.referential_integrity_score, 1),
            "total_issues": metrics.total_issues,
            "critical_issues": metrics.critical_issues,
            "high_issues": metrics.high_issues,
            "medium_issues": metrics.medium_issues,
            "low_issues": metrics.low_issues
        }
    
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
