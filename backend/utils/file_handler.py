"""
File Handler - Módulo de Manejo de Archivos
Gestiona la carga, validación y procesamiento de archivos SQL
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

class FileHandler:
    """Manejador de archivos SQL especializado"""
    
    def __init__(self):
        """Inicializar manejador de archivos"""
        self.allowed_extensions = {'.sql', '.txt'}
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.temp_dir = Path(tempfile.gettempdir()) / 'sql_analyzer'
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info("FileHandler inicializado")
    
    def is_allowed_file(self, filename: str) -> bool:
        """
        Verificar si el archivo tiene una extensión permitida
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si la extensión está permitida
        """
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.allowed_extensions
    
    def validate_file_size(self, file: FileStorage) -> bool:
        """
        Validar el tamaño del archivo
        
        Args:
            file: Archivo a validar
            
        Returns:
            True si el tamaño es válido
        """
        try:
            # Obtener tamaño del archivo
            file.seek(0, 2)  # Ir al final
            size = file.tell()
            file.seek(0)  # Volver al inicio
            
            return size <= self.max_file_size
        except Exception as e:
            logger.error(f"Error validando tamaño: {e}")
            return False
    
    def read_file_content(self, file: FileStorage) -> Optional[str]:
        """
        Leer contenido del archivo con manejo de encoding
        
        Args:
            file: Archivo a leer
            
        Returns:
            Contenido del archivo o None si hay error
        """
        try:
            # Intentar con UTF-8 primero
            content = file.read().decode('utf-8')
            file.seek(0)  # Reset para uso posterior
            return content
        except UnicodeDecodeError:
            try:
                # Intentar con latin-1
                file.seek(0)
                content = file.read().decode('latin-1')
                file.seek(0)
                return content
            except Exception as e:
                logger.error(f"Error leyendo archivo: {e}")
                return None
        except Exception as e:
            logger.error(f"Error leyendo archivo: {e}")
            return None
    
    def save_temp_file(self, file: FileStorage, prefix: str = 'sql_') -> Optional[Path]:
        """
        Guardar archivo temporal
        
        Args:
            file: Archivo a guardar
            prefix: Prefijo para el archivo temporal
            
        Returns:
            Ruta del archivo temporal o None si hay error
        """
        try:
            # Crear archivo temporal
            suffix = Path(file.filename).suffix if file.filename else '.sql'
            temp_file = tempfile.NamedTemporaryFile(
                prefix=prefix,
                suffix=suffix,
                dir=self.temp_dir,
                delete=False
            )
            
            # Guardar contenido
            file.seek(0)
            temp_file.write(file.read())
            temp_file.close()
            
            file.seek(0)  # Reset para uso posterior
            return Path(temp_file.name)
            
        except Exception as e:
            logger.error(f"Error guardando archivo temporal: {e}")
            return None
    
    def cleanup_temp_file(self, file_path: Path) -> bool:
        """
        Limpiar archivo temporal
        
        Args:
            file_path: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando archivo temporal: {e}")
            return False
    
    def get_file_info(self, file: FileStorage) -> Dict[str, Any]:
        """
        Obtener información del archivo
        
        Args:
            file: Archivo a analizar
            
        Returns:
            Diccionario con información del archivo
        """
        try:
            # Obtener tamaño
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            # Leer contenido para análisis
            content = self.read_file_content(file)
            
            info = {
                'filename': file.filename or 'unknown',
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'extension': Path(file.filename).suffix.lower() if file.filename else '',
                'is_valid_extension': self.is_allowed_file(file.filename),
                'is_valid_size': size <= self.max_file_size,
                'line_count': len(content.split('\n')) if content else 0,
                'char_count': len(content) if content else 0,
                'has_content': bool(content and content.strip())
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error obteniendo información del archivo: {e}")
            return {
                'filename': file.filename or 'unknown',
                'size': 0,
                'size_mb': 0,
                'extension': '',
                'is_valid_extension': False,
                'is_valid_size': False,
                'line_count': 0,
                'char_count': 0,
                'has_content': False,
                'error': str(e)
            }
    
    def validate_sql_content(self, content: str) -> Dict[str, Any]:
        """
        Validar contenido SQL básico
        
        Args:
            content: Contenido a validar
            
        Returns:
            Resultado de validación
        """
        try:
            if not content or not content.strip():
                return {
                    'valid': False,
                    'message': 'El archivo está vacío',
                    'details': []
                }
            
            # Verificaciones básicas
            content_upper = content.upper()
            sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
            
            has_sql_keywords = any(keyword in content_upper for keyword in sql_keywords)
            
            if not has_sql_keywords:
                return {
                    'valid': False,
                    'message': 'No se detectaron palabras clave SQL válidas',
                    'details': ['El archivo no parece contener código SQL válido']
                }
            
            # Verificar balance de paréntesis
            open_parens = content.count('(')
            close_parens = content.count(')')
            
            details = []
            if open_parens != close_parens:
                details.append(f'Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados')
            
            return {
                'valid': True,
                'message': 'Contenido SQL válido',
                'details': details,
                'stats': {
                    'keywords_found': [kw for kw in sql_keywords if kw in content_upper],
                    'line_count': len(content.split('\n')),
                    'char_count': len(content),
                    'parentheses_balanced': open_parens == close_parens
                }
            }
            
        except Exception as e:
            logger.error(f"Error validando contenido SQL: {e}")
            return {
                'valid': False,
                'message': f'Error en validación: {str(e)}',
                'details': []
            }
    
    def cleanup_temp_directory(self) -> int:
        """
        Limpiar directorio temporal de archivos antiguos
        
        Returns:
            Número de archivos eliminados
        """
        try:
            cleaned = 0
            if self.temp_dir.exists():
                for file_path in self.temp_dir.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            cleaned += 1
                        except:
                            pass
            
            logger.info(f"Limpiados {cleaned} archivos temporales")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error limpiando directorio temporal: {e}")
            return 0
