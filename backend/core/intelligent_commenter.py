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

