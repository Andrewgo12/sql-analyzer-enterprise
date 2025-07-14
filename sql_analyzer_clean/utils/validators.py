"""
Validadores del sistema - Seguridad y robustez
Validaciones exhaustivas para archivos y contenido
"""

import re
import logging
from typing import Dict, Any, List
from werkzeug.datastructures import FileStorage
from config import Config

logger = logging.getLogger(__name__)

class FileValidator:
    """Validador robusto de archivos"""
    
    def __init__(self):
        """Inicializar validador"""
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS
        self.max_file_size = Config.MAX_FILE_SIZE
        self.max_lines = Config.MAX_LINES
        logger.info("FileValidator inicializado")
    
    def validate_file(self, file: FileStorage) -> Dict[str, Any]:
        """
        Validar archivo completo
        
        Args:
            file: Archivo a validar
            
        Returns:
            Diccionario con resultado de validación
        """
        try:
            # Validar existencia
            if not file or not file.filename:
                return {
                    'valid': False,
                    'error': 'No se proporcionó archivo válido'
                }
            
            # Validar nombre de archivo
            filename_validation = self._validate_filename(file.filename)
            if not filename_validation['valid']:
                return filename_validation
            
            # Validar tamaño
            size_validation = self._validate_file_size(file)
            if not size_validation['valid']:
                return size_validation
            
            # Validar extensión
            extension_validation = self._validate_extension(file.filename)
            if not extension_validation['valid']:
                return extension_validation
            
            # Validar contenido
            content_validation = self._validate_content(file)
            if not content_validation['valid']:
                return content_validation
            
            logger.info(f"Archivo validado exitosamente: {file.filename}")
            return {
                'valid': True,
                'message': 'Archivo válido'
            }
            
        except Exception as e:
            logger.error(f"Error validando archivo: {e}")
            return {
                'valid': False,
                'error': f'Error en validación: {str(e)}'
            }
    
    def _validate_filename(self, filename: str) -> Dict[str, Any]:
        """Validar nombre de archivo"""
        # Caracteres peligrosos
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        
        if any(char in filename for char in dangerous_chars):
            return {
                'valid': False,
                'error': 'Nombre de archivo contiene caracteres no permitidos'
            }
        
        # Longitud máxima
        if len(filename) > 255:
            return {
                'valid': False,
                'error': 'Nombre de archivo demasiado largo (máximo 255 caracteres)'
            }
        
        # Nombres reservados en Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
            'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = filename.rsplit('.', 1)[0].upper()
        if name_without_ext in reserved_names:
            return {
                'valid': False,
                'error': 'Nombre de archivo reservado por el sistema'
            }
        
        return {'valid': True}
    
    def _validate_file_size(self, file: FileStorage) -> Dict[str, Any]:
        """Validar tamaño de archivo"""
        try:
            # Obtener tamaño
            file.seek(0, 2)  # Ir al final
            size = file.tell()
            file.seek(0)  # Volver al inicio
            
            if size == 0:
                return {
                    'valid': False,
                    'error': 'El archivo está vacío'
                }
            
            if size > self.max_file_size:
                size_mb = size / (1024 * 1024)
                max_mb = self.max_file_size / (1024 * 1024)
                return {
                    'valid': False,
                    'error': f'Archivo demasiado grande ({size_mb:.1f}MB). Máximo permitido: {max_mb}MB'
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error verificando tamaño: {str(e)}'
            }
    
    def _validate_extension(self, filename: str) -> Dict[str, Any]:
        """Validar extensión de archivo"""
        if '.' not in filename:
            return {
                'valid': False,
                'error': 'Archivo sin extensión'
            }
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        if extension not in self.allowed_extensions:
            allowed_list = ', '.join(self.allowed_extensions)
            return {
                'valid': False,
                'error': f'Extensión no permitida. Extensiones válidas: {allowed_list}'
            }
        
        return {'valid': True}
    
    def _validate_content(self, file: FileStorage) -> Dict[str, Any]:
        """Validar contenido del archivo"""
        try:
            # Leer contenido
            content = file.read().decode('utf-8')
            file.seek(0)  # Reset
            
            # Validar que no esté vacío
            if not content.strip():
                return {
                    'valid': False,
                    'error': 'El archivo no contiene contenido válido'
                }
            
            # Validar número de líneas
            lines = content.split('\n')
            if len(lines) > self.max_lines:
                return {
                    'valid': False,
                    'error': f'Archivo demasiado largo ({len(lines)} líneas). Máximo: {self.max_lines} líneas'
                }
            
            # Validar que parece SQL
            sql_validation = self._validate_sql_content(content)
            if not sql_validation['valid']:
                return sql_validation
            
            return {'valid': True}
            
        except UnicodeDecodeError:
            return {
                'valid': False,
                'error': 'El archivo no tiene codificación UTF-8 válida'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validando contenido: {str(e)}'
            }
    
    def _validate_sql_content(self, content: str) -> Dict[str, Any]:
        """Validar que el contenido parece SQL válido"""
        # Palabras clave SQL comunes
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW'
        ]
        
        content_upper = content.upper()
        
        # Verificar que contiene al menos una palabra clave SQL
        has_sql_keyword = any(keyword in content_upper for keyword in sql_keywords)
        
        if not has_sql_keyword:
            return {
                'valid': False,
                'error': 'El archivo no parece contener código SQL válido'
            }
        
        # Verificar patrones peligrosos extremos
        dangerous_patterns = [
            r'EXEC\s*\(',
            r'EXECUTE\s*\(',
            r'xp_cmdshell',
            r'sp_executesql'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content_upper):
                return {
                    'valid': False,
                    'error': 'El archivo contiene código SQL potencialmente peligroso'
                }
        
        return {'valid': True}

class ContentValidator:
    """Validador de contenido SQL"""
    
    def __init__(self):
        """Inicializar validador de contenido"""
        logger.info("ContentValidator inicializado")
    
    def validate_sql_syntax(self, content: str) -> Dict[str, Any]:
        """
        Validar sintaxis SQL básica
        
        Args:
            content: Contenido SQL a validar
            
        Returns:
            Resultado de validación
        """
        try:
            errors = []
            
            # Verificar paréntesis balanceados
            paren_errors = self._check_balanced_parentheses(content)
            errors.extend(paren_errors)
            
            # Verificar comillas balanceadas
            quote_errors = self._check_balanced_quotes(content)
            errors.extend(quote_errors)
            
            # Verificar punto y coma
            semicolon_errors = self._check_semicolons(content)
            errors.extend(semicolon_errors)
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'error_count': len(errors)
            }
            
        except Exception as e:
            logger.error(f"Error validando sintaxis SQL: {e}")
            return {
                'valid': False,
                'errors': [f'Error en validación: {str(e)}'],
                'error_count': 1
            }
    
    def _check_balanced_parentheses(self, content: str) -> List[str]:
        """Verificar paréntesis balanceados"""
        errors = []
        stack = []
        
        for i, char in enumerate(content):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    errors.append(f"Paréntesis de cierre sin apertura en posición {i}")
                else:
                    stack.pop()
        
        if stack:
            errors.append(f"Paréntesis sin cerrar: {len(stack)} paréntesis abiertos")
        
        return errors
    
    def _check_balanced_quotes(self, content: str) -> List[str]:
        """Verificar comillas balanceadas"""
        errors = []
        
        # Verificar comillas simples
        single_quotes = content.count("'")
        if single_quotes % 2 != 0:
            errors.append("Comillas simples desbalanceadas")
        
        # Verificar comillas dobles
        double_quotes = content.count('"')
        if double_quotes % 2 != 0:
            errors.append("Comillas dobles desbalanceadas")
        
        return errors
    
    def _check_semicolons(self, content: str) -> List[str]:
        """Verificar uso de punto y coma"""
        errors = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('--'):
                # Verificar statements que deberían terminar en punto y coma
                sql_statements = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
                
                if any(line.upper().startswith(stmt) for stmt in sql_statements):
                    if not line.endswith(';') and line_num == len(lines):
                        errors.append(f"Statement en línea {line_num} podría necesitar punto y coma")
        
        return errors
