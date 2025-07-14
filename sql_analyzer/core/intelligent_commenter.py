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
            
            # Generate commented SQL
            commented_sql = self._insert_comments(sql_content, comments)
            
            return {
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
            'LIMIT': "Limita el número de resultados"
        }
