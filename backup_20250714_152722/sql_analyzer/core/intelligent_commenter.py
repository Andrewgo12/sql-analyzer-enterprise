"""
Intelligent SQL Commenter Module

Generates contextual Spanish comments for SQL code based on analysis
of table structures, query patterns, and business logic.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlparse
from sqlparse import sql, tokens as T

logger = logging.getLogger(__name__)


class CommentType(Enum):
    """Types of comments that can be generated."""
    TABLE_DESCRIPTION = "table_description"
    COLUMN_DESCRIPTION = "column_description"
    QUERY_EXPLANATION = "query_explanation"
    JOIN_EXPLANATION = "join_explanation"
    BUSINESS_LOGIC = "business_logic"
    PERFORMANCE_NOTE = "performance_note"
    SECURITY_NOTE = "security_note"


@dataclass
class Comment:
    """Represents a generated comment."""
    line_number: int
    comment_type: CommentType
    text: str
    position: str  # 'before', 'after', 'inline'
    confidence: float


class IntelligentCommenter:
    """Generates intelligent Spanish comments for SQL code."""
    
    def __init__(self):
        self.table_patterns = self._load_table_patterns()
        self.column_patterns = self._load_column_patterns()
        self.query_patterns = self._load_query_patterns()
    
    def add_comments(self, sql_content: str) -> Dict:
        """
        Add intelligent comments to SQL content.

        Args:
            sql_content: Original SQL content

        Returns:
            Dict with commented SQL and metadata
        """
        try:
            # Parse SQL content
            parsed = sqlparse.parse(sql_content)
            lines = sql_content.split('\n')
            comments = []

            # Analyze each statement
            for statement in parsed:
                statement_comments = self._analyze_statement(statement, lines)
                comments.extend(statement_comments)

            # Add contextual comments based on patterns
            contextual_comments = self._add_contextual_comments(sql_content, lines)
            comments.extend(contextual_comments)

            # Generate commented SQL
            commented_sql = self._insert_comments(sql_content, comments)

            return {
                'success': True,
                'commented_sql': commented_sql,
                'comments_added': len(comments),
                'comment_details': [
                    {
                        'line': c.line_number,
                        'type': c.comment_type.value,
                        'text': c.text,
                        'confidence': c.confidence
                    } for c in comments
                ],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error adding comments: {e}")
            return {
                'commented_sql': sql_content,
                'comments_added': 0,
                'comment_details': [],
                'success': False,
                'error': str(e)
            }

    def analyze_sql_structure(self, sql_content: str) -> Dict:
        """
        Analyze SQL structure for intelligent commenting.

        Args:
            sql_content: SQL content to analyze

        Returns:
            Dict with structure analysis results
        """
        try:
            parsed = sqlparse.parse(sql_content)
            structure = {
                'statements': [],
                'tables': set(),
                'columns': set(),
                'operations': set(),
                'complexity_score': 0
            }

            for statement in parsed:
                stmt_info = {
                    'type': self._get_statement_type(statement),
                    'tokens': len(list(statement.flatten())),
                    'tables': [],
                    'columns': []
                }

                # Extract basic information
                stmt_str = str(statement).strip().upper()
                if stmt_str.startswith('SELECT'):
                    stmt_info['type'] = 'SELECT'
                elif stmt_str.startswith('INSERT'):
                    stmt_info['type'] = 'INSERT'
                elif stmt_str.startswith('UPDATE'):
                    stmt_info['type'] = 'UPDATE'
                elif stmt_str.startswith('DELETE'):
                    stmt_info['type'] = 'DELETE'
                elif stmt_str.startswith('CREATE'):
                    stmt_info['type'] = 'CREATE'
                else:
                    stmt_info['type'] = 'OTHER'

                structure['statements'].append(stmt_info)
                structure['operations'].add(stmt_info['type'])

            # Calculate complexity score
            structure['complexity_score'] = len(structure['statements']) * 10

            # Convert sets to lists for JSON serialization
            structure['tables'] = list(structure['tables'])
            structure['columns'] = list(structure['columns'])
            structure['operations'] = list(structure['operations'])

            return structure

        except Exception as e:
            logger.error(f"Error analyzing SQL structure: {e}")
            return {
                'statements': [],
                'tables': [],
                'columns': [],
                'operations': [],
                'complexity_score': 0,
                'error': str(e)
            }

    def _get_statement_type(self, statement) -> str:
        """Get the type of SQL statement."""
        try:
            stmt_str = str(statement).strip().upper()
            if stmt_str.startswith('SELECT'):
                return 'SELECT'
            elif stmt_str.startswith('INSERT'):
                return 'INSERT'
            elif stmt_str.startswith('UPDATE'):
                return 'UPDATE'
            elif stmt_str.startswith('DELETE'):
                return 'DELETE'
            elif stmt_str.startswith('CREATE'):
                return 'CREATE'
            elif stmt_str.startswith('DROP'):
                return 'DROP'
            elif stmt_str.startswith('ALTER'):
                return 'ALTER'
            else:
                return 'OTHER'
        except:
            return 'UNKNOWN'

    def _is_table_name(self, token, statement) -> bool:
        """Check if token is likely a table name."""
        # Simple heuristic - this could be improved
        token_str = str(token).strip()
        return (len(token_str) > 1 and
                token_str.isalnum() and
                not token_str.upper() in ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE'])

    def _is_column_name(self, token, statement) -> bool:
        """Check if token is likely a column name."""
        # Simple heuristic - this could be improved
        token_str = str(token).strip()
        return (len(token_str) > 1 and
                token_str.isalnum() and
                not token_str.upper() in ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE'])

    def _calculate_complexity(self, structure) -> int:
        """Calculate complexity score based on structure."""
        score = 0
        score += len(structure['statements']) * 10
        score += len(structure['tables']) * 5
        score += len(structure['columns']) * 2
        score += len(structure['operations']) * 15
        return score

    def _analyze_statement(self, statement, lines: List[str]) -> List[Comment]:
        """Analyze a SQL statement and generate appropriate comments."""
        comments = []
        statement_str = str(statement).strip()
        
        if not statement_str or statement_str.startswith('--'):
            return comments
        
        # Determine statement type
        statement_upper = statement_str.upper()
        
        if statement_upper.startswith('CREATE TABLE'):
            comments.extend(self._comment_create_table(statement, lines))
        elif statement_upper.startswith('SELECT'):
            comments.extend(self._comment_select_query(statement, lines))
        elif statement_upper.startswith('INSERT'):
            comments.extend(self._comment_insert_query(statement, lines))
        elif statement_upper.startswith('UPDATE'):
            comments.extend(self._comment_update_query(statement, lines))
        elif statement_upper.startswith('DELETE'):
            comments.extend(self._comment_delete_query(statement, lines))
        
        return comments
    
    def _comment_create_table(self, statement, lines: List[str]) -> List[Comment]:
        """Generate comments for CREATE TABLE statements."""
        comments = []
        statement_str = str(statement)
        
        # Extract table name
        table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement_str, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            
            # Generate table description based on name patterns
            table_description = self._get_table_description(table_name)
            
            # Find line number
            line_num = self._find_statement_line(statement_str, lines)
            
            comments.append(Comment(
                line_number=line_num,
                comment_type=CommentType.TABLE_DESCRIPTION,
                text=f"-- Tabla: {table_name} - {table_description}",
                position='before',
                confidence=0.8
            ))
            
            # Comment columns
            column_comments = self._comment_table_columns(statement_str, line_num)
            comments.extend(column_comments)
        
        return comments
    
    def _comment_select_query(self, statement, lines: List[str]) -> List[Comment]:
        """Generate comments for SELECT queries."""
        comments = []
        statement_str = str(statement)
        line_num = self._find_statement_line(statement_str, lines)
        
        # Analyze query complexity
        if 'JOIN' in statement_str.upper():
            join_comment = self._analyze_joins(statement_str)
            comments.append(Comment(
                line_number=line_num,
                comment_type=CommentType.JOIN_EXPLANATION,
                text=f"-- {join_comment}",
                position='before',
                confidence=0.9
            ))
        
        # Analyze WHERE conditions
        where_comment = self._analyze_where_conditions(statement_str)
        if where_comment:
            comments.append(Comment(
                line_number=line_num + 1,
                comment_type=CommentType.QUERY_EXPLANATION,
                text=f"-- {where_comment}",
                position='after',
                confidence=0.7
            ))
        
        return comments
    
    def _get_table_description(self, table_name: str) -> str:
        """Get description for table based on naming patterns."""
        table_lower = table_name.lower()
        
        for pattern, description in self.table_patterns.items():
            if pattern in table_lower:
                return description
        
        return "Almacena información del sistema"
    
    def _get_column_description(self, column_name: str, data_type: str) -> str:
        """Get description for column based on naming patterns."""
        column_lower = column_name.lower()
        
        for pattern, description in self.column_patterns.items():
            if pattern in column_lower:
                return description.format(type=data_type)
        
        return f"Campo de tipo {data_type}"
    
    def _comment_table_columns(self, statement_str: str, base_line: int) -> List[Comment]:
        """Generate comments for table columns."""
        comments = []
        
        # Extract column definitions
        column_pattern = r'(\w+)\s+(VARCHAR|INT|TEXT|DATETIME|TIMESTAMP|BOOLEAN|DECIMAL|FLOAT)(\([^)]+\))?\s*(NOT\s+NULL|NULL)?\s*(DEFAULT\s+[^,\n]+)?'
        columns = re.findall(column_pattern, statement_str, re.IGNORECASE)
        
        for i, (col_name, data_type, size, null_constraint, default) in enumerate(columns):
            description = self._get_column_description(col_name, data_type)
            
            # Add constraints info
            constraint_info = []
            if 'NOT NULL' in (null_constraint or ''):
                constraint_info.append("obligatorio")
            if default:
                constraint_info.append(f"valor por defecto: {default.replace('DEFAULT', '').strip()}")
            
            if constraint_info:
                description += f" ({', '.join(constraint_info)})"
            
            comments.append(Comment(
                line_number=base_line + i + 1,
                comment_type=CommentType.COLUMN_DESCRIPTION,
                text=f"    -- {col_name}: {description}",
                position='after',
                confidence=0.8
            ))
        
        return comments
    
    def _analyze_joins(self, statement_str: str) -> str:
        """Analyze JOIN operations and generate explanations."""
        join_types = {
            'INNER JOIN': 'Combina registros que coinciden en ambas tablas',
            'LEFT JOIN': 'Incluye todos los registros de la tabla izquierda',
            'RIGHT JOIN': 'Incluye todos los registros de la tabla derecha',
            'FULL JOIN': 'Incluye todos los registros de ambas tablas'
        }
        
        for join_type, description in join_types.items():
            if join_type in statement_str.upper():
                return f"Consulta con {join_type.lower()}: {description}"
        
        return "Consulta que combina múltiples tablas"
    
    def _analyze_where_conditions(self, statement_str: str) -> Optional[str]:
        """Analyze WHERE conditions and generate explanations."""
        if 'WHERE' not in statement_str.upper():
            return None
        
        conditions = []
        
        if re.search(r'WHERE.*=', statement_str, re.IGNORECASE):
            conditions.append("filtro por igualdad")
        if re.search(r'WHERE.*LIKE', statement_str, re.IGNORECASE):
            conditions.append("búsqueda por patrón")
        if re.search(r'WHERE.*BETWEEN', statement_str, re.IGNORECASE):
            conditions.append("filtro por rango")
        if re.search(r'WHERE.*IN\s*\(', statement_str, re.IGNORECASE):
            conditions.append("filtro por lista de valores")
        
        if conditions:
            return f"Aplica {', '.join(conditions)}"
        
        return "Aplica condiciones de filtrado"
    
    def _comment_insert_query(self, statement, lines: List[str]) -> List[Comment]:
        """Generate comments for INSERT queries."""
        statement_str = str(statement)
        line_num = self._find_statement_line(statement_str, lines)
        
        # Extract table name
        table_match = re.search(r'INSERT\s+INTO\s+(\w+)', statement_str, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            return [Comment(
                line_number=line_num,
                comment_type=CommentType.QUERY_EXPLANATION,
                text=f"-- Insertar nuevos registros en la tabla {table_name}",
                position='before',
                confidence=0.9
            )]
        
        return []
    
    def _comment_update_query(self, statement, lines: List[str]) -> List[Comment]:
        """Generate comments for UPDATE queries."""
        statement_str = str(statement)
        line_num = self._find_statement_line(statement_str, lines)
        
        # Extract table name
        table_match = re.search(r'UPDATE\s+(\w+)', statement_str, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            
            # Check for WHERE clause
            if 'WHERE' in statement_str.upper():
                comment_text = f"-- Actualizar registros específicos en la tabla {table_name}"
            else:
                comment_text = f"-- ⚠️ CUIDADO: Actualizar TODOS los registros en la tabla {table_name}"
            
            return [Comment(
                line_number=line_num,
                comment_type=CommentType.QUERY_EXPLANATION,
                text=comment_text,
                position='before',
                confidence=0.9
            )]
        
        return []
    
    def _comment_delete_query(self, statement, lines: List[str]) -> List[Comment]:
        """Generate comments for DELETE queries."""
        statement_str = str(statement)
        line_num = self._find_statement_line(statement_str, lines)
        
        # Extract table name
        table_match = re.search(r'DELETE\s+FROM\s+(\w+)', statement_str, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            
            # Check for WHERE clause
            if 'WHERE' in statement_str.upper():
                comment_text = f"-- Eliminar registros específicos de la tabla {table_name}"
            else:
                comment_text = f"-- ⚠️ PELIGRO: Eliminar TODOS los registros de la tabla {table_name}"
            
            return [Comment(
                line_number=line_num,
                comment_type=CommentType.QUERY_EXPLANATION,
                text=comment_text,
                position='before',
                confidence=0.9
            )]
        
        return []
    
    def _find_statement_line(self, statement_str: str, lines: List[str]) -> int:
        """Find the line number where a statement begins."""
        first_word = statement_str.split()[0] if statement_str.split() else ""
        
        for i, line in enumerate(lines, 1):
            if first_word.upper() in line.upper():
                return i
        
        return 1
    
    def _insert_comments(self, sql_content: str, comments: List[Comment]) -> str:
        """Insert comments into SQL content."""
        lines = sql_content.split('\n')
        
        # Sort comments by line number (reverse order to maintain line numbers)
        comments.sort(key=lambda c: c.line_number, reverse=True)
        
        for comment in comments:
            line_idx = comment.line_number - 1
            
            if 0 <= line_idx < len(lines):
                if comment.position == 'before':
                    lines.insert(line_idx, comment.text)
                elif comment.position == 'after':
                    lines.insert(line_idx + 1, comment.text)
                elif comment.position == 'inline':
                    lines[line_idx] += f"  {comment.text}"
        
        return '\n'.join(lines)
    
    def _load_table_patterns(self) -> Dict[str, str]:
        """Load table naming patterns and descriptions."""
        return {
            'user': "Gestiona información de usuarios del sistema",
            'cliente': "Almacena datos de clientes",
            'producto': "Catálogo de productos disponibles",
            'pedido': "Registra pedidos realizados",
            'orden': "Gestiona órdenes de trabajo",
            'factura': "Almacena información de facturación",
            'pago': "Registra transacciones de pago",
            'categoria': "Clasificación y categorización",
            'config': "Configuración del sistema",
            'log': "Registro de eventos y actividades",
            'audit': "Auditoría y seguimiento",
            'session': "Gestión de sesiones de usuario",
            'role': "Roles y permisos del sistema",
            'permission': "Permisos específicos",
            'address': "Direcciones y ubicaciones",
            'contact': "Información de contacto",
            'inventory': "Control de inventario",
            'stock': "Gestión de existencias",
            'report': "Reportes y estadísticas",
            'notification': "Sistema de notificaciones"
        }
    
    def _load_column_patterns(self) -> Dict[str, str]:
        """Load column naming patterns and descriptions."""
        return {
            'id': "Identificador único de tipo {type}",
            'name': "Nombre descriptivo de tipo {type}",
            'nombre': "Nombre descriptivo de tipo {type}",
            'email': "Dirección de correo electrónico de tipo {type}",
            'correo': "Dirección de correo electrónico de tipo {type}",
            'password': "Contraseña encriptada de tipo {type}",
            'contraseña': "Contraseña encriptada de tipo {type}",
            'phone': "Número telefónico de tipo {type}",
            'telefono': "Número telefónico de tipo {type}",
            'address': "Dirección física de tipo {type}",
            'direccion': "Dirección física de tipo {type}",
            'date': "Fecha de tipo {type}",
            'fecha': "Fecha de tipo {type}",
            'time': "Hora de tipo {type}",
            'hora': "Hora de tipo {type}",
            'created': "Fecha de creación de tipo {type}",
            'updated': "Fecha de última actualización de tipo {type}",
            'status': "Estado o condición de tipo {type}",
            'estado': "Estado o condición de tipo {type}",
            'active': "Indicador de actividad de tipo {type}",
            'activo': "Indicador de actividad de tipo {type}",
            'price': "Precio monetario de tipo {type}",
            'precio': "Precio monetario de tipo {type}",
            'amount': "Cantidad o monto de tipo {type}",
            'cantidad': "Cantidad o monto de tipo {type}",
            'description': "Descripción detallada de tipo {type}",
            'descripcion': "Descripción detallada de tipo {type}",
            'code': "Código identificador de tipo {type}",
            'codigo': "Código identificador de tipo {type}"
        }
    
    def _load_query_patterns(self) -> Dict[str, str]:
        """Load query patterns and descriptions."""
        return {
            'COUNT': "Cuenta el número de registros",
            'SUM': "Calcula la suma total",
            'AVG': "Calcula el promedio",
            'MAX': "Obtiene el valor máximo",
            'MIN': "Obtiene el valor mínimo",
            'GROUP BY': "Agrupa resultados por criterio",
            'ORDER BY': "Ordena resultados",
            'HAVING': "Filtra grupos de resultados",
            'DISTINCT': "Elimina duplicados",
            'LIMIT': "Limita el número de resultados",
            'WHERE': "Filtra registros según condición",
            'JOIN': "Relaciona tablas mediante claves"
        }

    def _add_contextual_comments(self, sql_content: str, lines: List[str]) -> List[Comment]:
        """Add contextual comments based on advanced pattern analysis."""
        comments = []

        # Analyze CREATE TABLE statements for intelligent table descriptions
        table_comments = self._analyze_table_definitions(lines)
        comments.extend(table_comments)

        # Analyze column definitions for data type explanations
        column_comments = self._analyze_column_definitions(lines)
        comments.extend(column_comments)

        # Analyze complex queries for business logic explanations
        query_comments = self._analyze_complex_queries(lines)
        comments.extend(query_comments)

        # Analyze constraints for business rule explanations
        constraint_comments = self._analyze_constraints(lines)
        comments.extend(constraint_comments)

        return comments

    def _analyze_table_definitions(self, lines: List[str]) -> List[Comment]:
        """Analyze CREATE TABLE statements and generate intelligent descriptions."""
        comments = []

        for i, line in enumerate(lines):
            line_clean = line.strip().upper()

            # Detect CREATE TABLE statements
            if line_clean.startswith('CREATE TABLE'):
                table_match = re.search(r'CREATE\s+TABLE\s+(?:\[?(\w+)\]?\.)?\[?(\w+)\]?', line, re.IGNORECASE)
                if table_match:
                    table_name = table_match.group(2).lower()
                    description = self._generate_table_description(table_name)

                    comment = Comment(
                        line_number=i + 1,
                        comment_type=CommentType.TABLE_DESCRIPTION,
                        text=f"-- {description}",
                        position='before',
                        confidence=0.9
                    )
                    comments.append(comment)

        return comments

    def _analyze_column_definitions(self, lines: List[str]) -> List[Comment]:
        """Analyze column definitions and generate data type explanations."""
        comments = []
        in_table_definition = False

        for i, line in enumerate(lines):
            line_clean = line.strip().upper()

            # Track if we're inside a table definition
            if line_clean.startswith('CREATE TABLE'):
                in_table_definition = True
                continue
            elif in_table_definition and (line_clean.startswith(')') or line_clean.startswith('GO') or line_clean.startswith('CREATE')):
                in_table_definition = False
                continue

            # Analyze column definitions
            if in_table_definition and line.strip() and not line.strip().startswith('--'):
                column_comment = self._generate_column_comment(line, i + 1)
                if column_comment:
                    comments.append(column_comment)

        return comments

    def _analyze_complex_queries(self, lines: List[str]) -> List[Comment]:
        """Analyze complex queries and generate business logic explanations."""
        comments = []

        for i, line in enumerate(lines):
            line_clean = line.strip().upper()

            # Detect complex SELECT statements
            if 'SELECT' in line_clean and ('JOIN' in line_clean or 'WHERE' in line_clean):
                description = self._generate_query_description(line)
                if description:
                    comment = Comment(
                        line_number=i + 1,
                        comment_type=CommentType.QUERY_EXPLANATION,
                        text=f"-- {description}",
                        position='before',
                        confidence=0.8
                    )
                    comments.append(comment)

            # Detect JOIN operations
            elif 'JOIN' in line_clean:
                join_description = self._generate_join_description(line)
                if join_description:
                    comment = Comment(
                        line_number=i + 1,
                        comment_type=CommentType.JOIN_EXPLANATION,
                        text=f"-- {join_description}",
                        position='before',
                        confidence=0.85
                    )
                    comments.append(comment)

        return comments

    def _analyze_constraints(self, lines: List[str]) -> List[Comment]:
        """Analyze constraints and generate business rule explanations."""
        comments = []

        for i, line in enumerate(lines):
            line_clean = line.strip().upper()

            # Detect PRIMARY KEY constraints
            if 'PRIMARY KEY' in line_clean:
                comment = Comment(
                    line_number=i + 1,
                    comment_type=CommentType.BUSINESS_LOGIC,
                    text="-- Clave primaria: garantiza unicidad e identifica cada registro",
                    position='after',
                    confidence=0.95
                )
                comments.append(comment)

            # Detect FOREIGN KEY constraints
            elif 'FOREIGN KEY' in line_clean:
                fk_description = self._generate_foreign_key_description(line)
                comment = Comment(
                    line_number=i + 1,
                    comment_type=CommentType.BUSINESS_LOGIC,
                    text=f"-- {fk_description}",
                    position='after',
                    confidence=0.9
                )
                comments.append(comment)

            # Detect CHECK constraints
            elif 'CHECK' in line_clean:
                comment = Comment(
                    line_number=i + 1,
                    comment_type=CommentType.BUSINESS_LOGIC,
                    text="-- Restricción de validación: asegura integridad de datos",
                    position='after',
                    confidence=0.85
                )
                comments.append(comment)

        return comments

    def _generate_table_description(self, table_name: str) -> str:
        """Generate intelligent table description based on name patterns."""
        table_name = table_name.lower()

        # Common table patterns
        if 'user' in table_name or 'usuario' in table_name:
            return "Tabla de usuarios: almacena información de personas registradas en el sistema"
        elif 'product' in table_name or 'producto' in table_name:
            return "Tabla de productos: contiene el catálogo de artículos disponibles"
        elif 'order' in table_name or 'pedido' in table_name:
            return "Tabla de pedidos: registra las transacciones de compra realizadas"
        elif 'customer' in table_name or 'cliente' in table_name:
            return "Tabla de clientes: información de contacto y datos comerciales"
        elif 'invoice' in table_name or 'factura' in table_name:
            return "Tabla de facturas: documentos fiscales de las ventas realizadas"
        elif 'payment' in table_name or 'pago' in table_name:
            return "Tabla de pagos: registro de transacciones monetarias"
        elif 'category' in table_name or 'categoria' in table_name:
            return "Tabla de categorías: clasificación y organización de elementos"
        elif 'log' in table_name or 'audit' in table_name:
            return "Tabla de auditoría: registro de eventos y cambios del sistema"
        elif 'config' in table_name or 'setting' in table_name:
            return "Tabla de configuración: parámetros y ajustes del sistema"
        else:
            return f"Tabla {table_name}: almacena información relacionada con {table_name.replace('_', ' ')}"

    def _generate_column_comment(self, line: str, line_number: int) -> Optional[Comment]:
        """Generate intelligent column comment based on name and data type."""
        # Extract column name and data type
        column_match = re.match(r'\s*\[?(\w+)\]?\s+(\w+)(?:\(([^)]+)\))?\s*(.*)', line.strip())
        if not column_match:
            return None

        column_name = column_match.group(1).lower()
        data_type = column_match.group(2).upper()
        size = column_match.group(3)
        constraints = column_match.group(4).upper()

        # Generate description based on column name patterns
        description = self._get_column_description(column_name, data_type, size, constraints)

        if description:
            return Comment(
                line_number=line_number,
                comment_type=CommentType.COLUMN_DESCRIPTION,
                text=f"-- {description}",
                position='after',
                confidence=0.8
            )

        return None

    def _get_column_description(self, column_name: str, data_type: str, size: str, constraints: str) -> str:
        """Get intelligent column description."""
        base_descriptions = {
            'id': "Identificador único del registro",
            'name': "Nombre descriptivo",
            'nombre': "Nombre descriptivo",
            'email': "Dirección de correo electrónico",
            'correo': "Dirección de correo electrónico",
            'password': "Contraseña encriptada",
            'phone': "Número telefónico",
            'telefono': "Número telefónico",
            'address': "Dirección física",
            'direccion': "Dirección física",
            'created_at': "Fecha y hora de creación",
            'updated_at': "Fecha y hora de última modificación",
            'status': "Estado actual del registro",
            'estado': "Estado actual del registro",
            'active': "Indicador de actividad (activo/inactivo)",
            'price': "Precio en moneda local",
            'precio': "Precio en moneda local",
            'amount': "Cantidad o monto",
            'cantidad': "Cantidad o monto",
            'description': "Descripción detallada",
            'descripcion': "Descripción detallada"
        }

        # Check for exact matches
        if column_name in base_descriptions:
            description = base_descriptions[column_name]
        else:
            # Check for partial matches
            description = None
            for pattern, desc in base_descriptions.items():
                if pattern in column_name:
                    description = desc
                    break

            if not description:
                description = f"Campo {column_name.replace('_', ' ')}"

        # Add data type information
        type_info = self._get_data_type_description(data_type, size)
        if type_info:
            description += f" ({type_info})"

        # Add constraint information
        if 'NOT NULL' in constraints:
            description += " - Campo obligatorio"
        if 'UNIQUE' in constraints:
            description += " - Valor único"

        return description

    def _get_data_type_description(self, data_type: str, size: str) -> str:
        """Get data type description in Spanish."""
        type_descriptions = {
            'INT': "número entero",
            'INTEGER': "número entero",
            'BIGINT': "número entero grande",
            'SMALLINT': "número entero pequeño",
            'DECIMAL': "número decimal",
            'NUMERIC': "número decimal",
            'FLOAT': "número decimal flotante",
            'REAL': "número real",
            'VARCHAR': f"texto variable hasta {size} caracteres" if size else "texto variable",
            'CHAR': f"texto fijo de {size} caracteres" if size else "texto fijo",
            'TEXT': "texto largo",
            'NVARCHAR': f"texto Unicode hasta {size} caracteres" if size else "texto Unicode",
            'DATE': "fecha",
            'DATETIME': "fecha y hora",
            'TIMESTAMP': "marca de tiempo",
            'TIME': "hora",
            'BIT': "valor booleano (verdadero/falso)",
            'BOOLEAN': "valor booleano (verdadero/falso)",
            'BLOB': "datos binarios",
            'VARBINARY': "datos binarios variables"
        }

        return type_descriptions.get(data_type, f"tipo {data_type.lower()}")

    def _generate_query_description(self, line: str) -> str:
        """Generate description for complex queries."""
        line_upper = line.upper()

        if 'COUNT' in line_upper:
            return "Consulta de conteo: obtiene el número total de registros"
        elif 'SUM' in line_upper:
            return "Consulta de suma: calcula el total acumulado"
        elif 'AVG' in line_upper:
            return "Consulta de promedio: calcula el valor medio"
        elif 'MAX' in line_upper:
            return "Consulta de máximo: obtiene el valor más alto"
        elif 'MIN' in line_upper:
            return "Consulta de mínimo: obtiene el valor más bajo"
        elif 'GROUP BY' in line_upper:
            return "Consulta agrupada: organiza resultados por categorías"
        elif 'ORDER BY' in line_upper:
            return "Consulta ordenada: organiza resultados según criterio"
        else:
            return "Consulta de selección: obtiene datos específicos"

    def _generate_join_description(self, line: str) -> str:
        """Generate description for JOIN operations."""
        line_upper = line.upper()

        if 'INNER JOIN' in line_upper:
            return "Unión interna: combina registros que coinciden en ambas tablas"
        elif 'LEFT JOIN' in line_upper:
            return "Unión izquierda: incluye todos los registros de la tabla izquierda"
        elif 'RIGHT JOIN' in line_upper:
            return "Unión derecha: incluye todos los registros de la tabla derecha"
        elif 'FULL JOIN' in line_upper:
            return "Unión completa: incluye todos los registros de ambas tablas"
        else:
            return "Unión de tablas: combina datos de múltiples fuentes"

    def _generate_foreign_key_description(self, line: str) -> str:
        """Generate description for foreign key constraints."""
        # Try to extract referenced table
        ref_match = re.search(r'REFERENCES\s+(\w+)', line, re.IGNORECASE)
        if ref_match:
            ref_table = ref_match.group(1)
            return f"Clave foránea: establece relación con la tabla {ref_table}"
        else:
            return "Clave foránea: establece relación con otra tabla"
