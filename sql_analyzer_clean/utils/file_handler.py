"""
Manejador de archivos - Sistema robusto
Manejo seguro de archivos con validaciones completas
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

class FileHandler:
    """Manejador robusto de archivos"""
    
    def __init__(self):
        """Inicializar manejador de archivos"""
        self.temp_dir = Path(tempfile.gettempdir()) / 'sql_analyzer_clean'
        self.temp_dir.mkdir(exist_ok=True)
        logger.info("FileHandler inicializado")
    
    def read_file(self, file: FileStorage) -> Optional[str]:
        """
        Leer contenido de archivo de manera segura
        
        Args:
            file: Archivo subido por el usuario
            
        Returns:
            Contenido del archivo como string o None si hay error
        """
        try:
            # Intentar UTF-8 primero
            content = file.read().decode('utf-8')
            file.seek(0)  # Reset para uso posterior si es necesario
            logger.info(f"Archivo leído exitosamente: {file.filename}")
            return content
            
        except UnicodeDecodeError:
            try:
                # Fallback a latin-1
                file.seek(0)
                content = file.read().decode('latin-1')
                file.seek(0)
                logger.warning(f"Archivo leído con encoding latin-1: {file.filename}")
                return content
                
            except Exception as e:
                logger.error(f"Error leyendo archivo {file.filename}: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error general leyendo archivo {file.filename}: {e}")
            return None
    
    def create_download_file(self, data: Dict[str, Any], format: str) -> Optional[str]:
        """
        Crear archivo temporal para descarga
        
        Args:
            data: Datos a incluir en el archivo
            format: Formato del archivo (json, txt, html, csv)
            
        Returns:
            Ruta del archivo temporal o None si hay error
        """
        try:
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix=f'.{format}',
                dir=self.temp_dir,
                delete=False,
                encoding='utf-8'
            )
            
            # Generar contenido según formato
            if format == 'json':
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
                
            elif format == 'txt':
                self._write_text_format(temp_file, data)
                
            elif format == 'html':
                self._write_html_format(temp_file, data)
                
            elif format == 'csv':
                self._write_csv_format(temp_file, data)
                
            else:
                # Formato por defecto (texto)
                temp_file.write(f"SQL Analyzer Enterprise - Reporte\n")
                temp_file.write(f"Timestamp: {data.get('timestamp', 'N/A')}\n")
                temp_file.write(f"Formato: {format}\n")
                temp_file.write(f"Contenido: {data.get('content', 'Sin contenido')}\n")
            
            temp_file.close()
            logger.info(f"Archivo de descarga creado: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creando archivo de descarga: {e}")
            return None
    
    def _write_text_format(self, file, data: Dict[str, Any]):
        """Escribir formato de texto plano"""
        file.write("SQL ANALYZER ENTERPRISE - REPORTE DE ANÁLISIS\n")
        file.write("=" * 60 + "\n\n")
        
        file.write(f"Archivo: {data.get('analyzer', 'N/A')}\n")
        file.write(f"Versión: {data.get('version', 'N/A')}\n")
        file.write(f"Timestamp: {data.get('timestamp', 'N/A')}\n")
        file.write(f"Formato: {data.get('format', 'N/A')}\n\n")
        
        file.write("CONTENIDO DEL ANÁLISIS:\n")
        file.write("-" * 30 + "\n")
        file.write(f"{data.get('content', 'Sin contenido disponible')}\n\n")
        
        file.write("INFORMACIÓN ADICIONAL:\n")
        file.write("-" * 30 + "\n")
        file.write("Este reporte fue generado por SQL Analyzer Enterprise\n")
        file.write("Sistema de análisis SQL profesional con arquitectura limpia\n")
    
    def _write_html_format(self, file, data: Dict[str, Any]):
        """Escribir formato HTML"""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Analyzer Enterprise - Reporte</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .info-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .content-section {{
            background: white;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 5px;
            font-size: 0.9em;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SQL Analyzer Enterprise</h1>
        <p>Reporte de Análisis SQL</p>
    </div>
    
    <div class="info-section">
        <h2>Información del Análisis</h2>
        <p><strong>Analizador:</strong> {data.get('analyzer', 'N/A')}</p>
        <p><strong>Versión:</strong> {data.get('version', 'N/A')}</p>
        <p><strong>Timestamp:</strong> {data.get('timestamp', 'N/A')}</p>
        <p><strong>Formato:</strong> {data.get('format', 'N/A')}</p>
    </div>
    
    <div class="content-section">
        <h2>Contenido del Análisis</h2>
        <p>{data.get('content', 'Sin contenido disponible')}</p>
    </div>
    
    <div class="footer">
        <p>Generado por SQL Analyzer Enterprise - Sistema de análisis SQL profesional</p>
        <p>Arquitectura limpia y robusta para análisis de calidad empresarial</p>
    </div>
</body>
</html>
        """
        file.write(html_content)
    
    def _write_csv_format(self, file, data: Dict[str, Any]):
        """Escribir formato CSV"""
        file.write("Campo,Valor\n")
        file.write(f"Analizador,{data.get('analyzer', 'N/A')}\n")
        file.write(f"Version,{data.get('version', 'N/A')}\n")
        file.write(f"Timestamp,{data.get('timestamp', 'N/A')}\n")
        file.write(f"Formato,{data.get('format', 'N/A')}\n")
        file.write(f"Contenido,\"{data.get('content', 'Sin contenido')}\"\n")
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Limpiar archivos temporales antiguos
        
        Args:
            max_age_hours: Edad máxima en horas para mantener archivos
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.temp_dir.glob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.info(f"Archivo temporal eliminado: {file_path}")
            
            logger.info("Limpieza de archivos temporales completada")
            
        except Exception as e:
            logger.error(f"Error en limpieza de archivos temporales: {e}")
    
    def get_file_info(self, file: FileStorage) -> Dict[str, Any]:
        """
        Obtener información del archivo
        
        Args:
            file: Archivo subido
            
        Returns:
            Diccionario con información del archivo
        """
        try:
            # Obtener tamaño
            file.seek(0, 2)  # Ir al final
            size = file.tell()
            file.seek(0)  # Volver al inicio
            
            return {
                'filename': file.filename,
                'size': size,
                'content_type': file.content_type,
                'size_mb': round(size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información del archivo: {e}")
            return {
                'filename': file.filename if file else 'unknown',
                'size': 0,
                'content_type': 'unknown',
                'size_mb': 0
            }
