"""
Validators - Módulo de Validación
Validadores especializados para archivos y contenido SQL
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

class FileValidator:
    """Validador de archivos SQL especializado"""
    
    def __init__(self):
        """Inicializar validador"""
        self.allowed_extensions = {'.sql', '.txt'}
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.min_file_size = 1  # 1 byte mínimo
        
        # Patrones SQL básicos
        self.sql_patterns = [
            r'\bSELECT\b',
            r'\bINSERT\b',
            r'\bUPDATE\b',
            r'\bDELETE\b',
            r'\bCREATE\b',
            r'\bDROP\b',
            r'\bALTER\b',
            r'\bFROM\b',
            r'\bWHERE\b',
            r'\bJOIN\b'
        ]
        
        logger.info("FileValidator inicializado")
    
    def validate_file(self, file: FileStorage) -> Dict[str, Any]:
        """
        Validar archivo completo
        
        Args:
            file: Archivo a validar
            
        Returns:
            Resultado de validación completa
        """
        try:
            # Validaciones básicas
            basic_validation = self._validate_basic_file_properties(file)
            if not basic_validation['valid']:
                return basic_validation
            
            # Validar contenido
            content_validation = self._validate_file_content(file)
            if not content_validation['valid']:
                return content_validation
            
            return {
                'valid': True,
                'message': 'Archivo válido',
                'details': {
                    'filename': file.filename,
                    'size': self._get_file_size(file),
                    'extension': Path(file.filename).suffix.lower() if file.filename else '',
                    'content_valid': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error en validación de archivo: {e}")
            return {
                'valid': False,
                'message': f'Error en validación: {str(e)}',
                'details': {}
            }
    
    def _validate_basic_file_properties(self, file: FileStorage) -> Dict[str, Any]:
        """Validar propiedades básicas del archivo"""
        try:
            # Verificar que existe el archivo
            if not file or not file.filename:
                return {
                    'valid': False,
                    'message': 'No se proporcionó archivo o nombre de archivo',
                    'details': {}
                }
            
            # Verificar extensión
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                return {
                    'valid': False,
                    'message': f'Extensión no permitida: {file_ext}. Extensiones permitidas: {", ".join(self.allowed_extensions)}',
                    'details': {'extension': file_ext}
                }
            
            # Verificar tamaño
            file_size = self._get_file_size(file)
            if file_size < self.min_file_size:
                return {
                    'valid': False,
                    'message': 'El archivo está vacío',
                    'details': {'size': file_size}
                }
            
            if file_size > self.max_file_size:
                return {
                    'valid': False,
                    'message': f'Archivo demasiado grande: {file_size / (1024*1024):.1f}MB. Máximo permitido: {self.max_file_size / (1024*1024):.1f}MB',
                    'details': {'size': file_size, 'max_size': self.max_file_size}
                }
            
            return {
                'valid': True,
                'message': 'Propiedades básicas válidas',
                'details': {
                    'filename': file.filename,
                    'extension': file_ext,
                    'size': file_size
                }
            }
            
        except Exception as e:
            logger.error(f"Error validando propiedades básicas: {e}")
            return {
                'valid': False,
                'message': f'Error validando propiedades: {str(e)}',
                'details': {}
            }
    
    def _validate_file_content(self, file: FileStorage) -> Dict[str, Any]:
        """Validar contenido del archivo"""
        try:
            # Leer contenido
            content = self._read_file_content(file)
            if content is None:
                return {
                    'valid': False,
                    'message': 'No se pudo leer el contenido del archivo',
                    'details': {}
                }
            
            # Verificar que no esté vacío
            if not content.strip():
                return {
                    'valid': False,
                    'message': 'El archivo está vacío o solo contiene espacios en blanco',
                    'details': {'content_length': len(content)}
                }
            
            # Verificar patrones SQL
            sql_validation = self._validate_sql_patterns(content)
            if not sql_validation['valid']:
                return sql_validation
            
            return {
                'valid': True,
                'message': 'Contenido válido',
                'details': {
                    'content_length': len(content),
                    'line_count': len(content.split('\n')),
                    'sql_patterns_found': sql_validation['patterns_found']
                }
            }
            
        except Exception as e:
            logger.error(f"Error validando contenido: {e}")
            return {
                'valid': False,
                'message': f'Error validando contenido: {str(e)}',
                'details': {}
            }
    
    def _validate_sql_patterns(self, content: str) -> Dict[str, Any]:
        """Validar patrones SQL en el contenido"""
        try:
            content_upper = content.upper()
            patterns_found = []
            
            for pattern in self.sql_patterns:
                if re.search(pattern, content_upper, re.IGNORECASE):
                    patterns_found.append(pattern.replace(r'\b', '').replace('\\', ''))
            
            if not patterns_found:
                return {
                    'valid': False,
                    'message': 'No se detectaron patrones SQL válidos en el archivo',
                    'details': {'patterns_searched': len(self.sql_patterns)},
                    'patterns_found': []
                }
            
            return {
                'valid': True,
                'message': f'Se encontraron {len(patterns_found)} patrones SQL',
                'patterns_found': patterns_found
            }
            
        except Exception as e:
            logger.error(f"Error validando patrones SQL: {e}")
            return {
                'valid': False,
                'message': f'Error validando patrones SQL: {str(e)}',
                'patterns_found': []
            }
    
    def _get_file_size(self, file: FileStorage) -> int:
        """Obtener tamaño del archivo"""
        try:
            current_pos = file.tell()
            file.seek(0, 2)  # Ir al final
            size = file.tell()
            file.seek(current_pos)  # Volver a posición original
            return size
        except Exception as e:
            logger.error(f"Error obteniendo tamaño de archivo: {e}")
            return 0
    
    def _read_file_content(self, file: FileStorage) -> Optional[str]:
        """Leer contenido del archivo con manejo de encoding"""
        try:
            current_pos = file.tell()
            
            # Intentar UTF-8 primero
            try:
                file.seek(0)
                content = file.read().decode('utf-8')
                file.seek(current_pos)
                return content
            except UnicodeDecodeError:
                # Intentar latin-1
                file.seek(0)
                content = file.read().decode('latin-1')
                file.seek(current_pos)
                return content
                
        except Exception as e:
            logger.error(f"Error leyendo contenido: {e}")
            return None
    
    def validate_sql_syntax_basic(self, content: str) -> Dict[str, Any]:
        """
        Validación básica de sintaxis SQL
        
        Args:
            content: Contenido SQL a validar
            
        Returns:
            Resultado de validación de sintaxis
        """
        try:
            issues = []
            
            # Verificar balance de paréntesis
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens != close_parens:
                issues.append(f'Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados')
            
            # Verificar balance de comillas
            single_quotes = content.count("'")
            if single_quotes % 2 != 0:
                issues.append('Comillas simples desbalanceadas')
            
            double_quotes = content.count('"')
            if double_quotes % 2 != 0:
                issues.append('Comillas dobles desbalanceadas')
            
            # Verificar punto y coma al final de statements
            lines = content.split('\n')
            statements_without_semicolon = []
            
            for i, line in enumerate(lines, 1):
                line_clean = line.strip()
                if line_clean and not line_clean.startswith('--'):
                    # Verificar si parece ser un statement SQL
                    if any(keyword in line_clean.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']):
                        if not line_clean.endswith(';') and not line_clean.endswith(','):
                            statements_without_semicolon.append(i)
            
            if statements_without_semicolon:
                issues.append(f'Posibles statements sin punto y coma en líneas: {", ".join(map(str, statements_without_semicolon[:5]))}')
            
            return {
                'valid': len(issues) == 0,
                'message': 'Sintaxis válida' if len(issues) == 0 else f'Se encontraron {len(issues)} problemas de sintaxis',
                'issues': issues,
                'stats': {
                    'parentheses_balanced': open_parens == close_parens,
                    'quotes_balanced': single_quotes % 2 == 0 and double_quotes % 2 == 0,
                    'statements_checked': len([l for l in lines if l.strip() and not l.strip().startswith('--')])
                }
            }
            
        except Exception as e:
            logger.error(f"Error en validación de sintaxis: {e}")
            return {
                'valid': False,
                'message': f'Error en validación de sintaxis: {str(e)}',
                'issues': [str(e)],
                'stats': {}
            }
