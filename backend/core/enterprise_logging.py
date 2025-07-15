"""
Sistema de Logging y Auditoría Empresarial

Sistema avanzado de logging, auditoría y monitoreo para cumplimiento
normativo y trazabilidad empresarial.
"""

import os
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import threading
import queue
import hashlib
import uuid
from contextlib import contextmanager

# Configuración de logging básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NivelEvento(Enum):
    """Niveles de eventos de auditoría."""
    CRITICO = "CRITICO"
    ERROR = "ERROR"
    ADVERTENCIA = "ADVERTENCIA"
    INFO = "INFO"
    DEBUG = "DEBUG"
    AUDITORIA = "AUDITORIA"


class TipoEvento(Enum):
    """Tipos de eventos del sistema."""
    INICIO_SESION = "inicio_sesion"
    FIN_SESION = "fin_sesion"
    PROCESAMIENTO_ARCHIVO = "procesamiento_archivo"
    ERROR_PROCESAMIENTO = "error_procesamiento"
    ACCESO_DATOS = "acceso_datos"
    MODIFICACION_CONFIG = "modificacion_config"
    GENERACION_REPORTE = "generacion_reporte"
    OPERACION_SEGURIDAD = "operacion_seguridad"
    CAMBIO_PERMISOS = "cambio_permisos"
    EXPORTACION_DATOS = "exportacion_datos"


@dataclass
class EventoAuditoria:
    """Evento de auditoría del sistema."""
    id_evento: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    nivel: NivelEvento = NivelEvento.INFO
    tipo_evento: TipoEvento = TipoEvento.PROCESAMIENTO_ARCHIVO
    usuario: str = "sistema"
    sesion_id: str = ""
    mensaje: str = ""
    detalles: Dict[str, Any] = field(default_factory=dict)
    archivo_origen: str = ""
    ip_origen: str = ""
    duracion_ms: Optional[int] = None
    resultado: str = "exitoso"
    hash_integridad: str = ""
    
    def __post_init__(self):
        """Calcular hash de integridad después de la inicialización."""
        if not self.hash_integridad:
            self.hash_integridad = self._calcular_hash()
    
class GestorLoggingEmpresarial:
    """
    Gestor de logging y auditoría empresarial.
    
    Características:
    - Logging estructurado con múltiples niveles
    - Auditoría completa de operaciones
    - Rotación automática de logs
    - Compresión y archivado
    - Alertas en tiempo real
    - Cumplimiento normativo (SOX, GDPR, etc.)
    - Integridad y no repudio
    - Monitoreo de rendimiento
    """
    
    def __init__(self, directorio_logs: Optional[Path] = None):
        """Inicializar el gestor de logging empresarial."""
        self.directorio_logs = directorio_logs or Path("logs_empresariales")
        self.directorio_logs.mkdir(parents=True, exist_ok=True)
        
        # Subdirectorios especializados
        self.dir_auditoria = self.directorio_logs / "auditoria"
        self.dir_seguridad = self.directorio_logs / "seguridad"
        self.dir_rendimiento = self.directorio_logs / "rendimiento"
        self.dir_errores = self.directorio_logs / "errores"
        self.dir_archivados = self.directorio_logs / "archivados"
        
        for directorio in [self.dir_auditoria, self.dir_seguridad, 
                          self.dir_rendimiento, self.dir_errores, self.dir_archivados]:
            directorio.mkdir(exist_ok=True)
        
        # Configurar loggers especializados
        self._configurar_loggers()
        
        # Cola de eventos para procesamiento asíncrono
        self.cola_eventos = queue.Queue()
        self.procesando_eventos = True
        
        # Hilo de procesamiento de eventos
        self.hilo_procesamiento = threading.Thread(target=self._procesar_eventos, daemon=True)
        self.hilo_procesamiento.start()
        
        # Métricas de rendimiento
        self.metricas_rendimiento = {
            'eventos_procesados': 0,
            'errores_logging': 0,
            'tiempo_promedio_procesamiento': 0.0
        }
        
        # Sesión actual
        self.sesion_actual = str(uuid.uuid4())
        
        # Registrar inicio del sistema
        self.registrar_evento(
            nivel=NivelEvento.AUDITORIA,
            tipo_evento=TipoEvento.INICIO_SESION,
            mensaje="Sistema de logging empresarial iniciado",
            detalles={'version': '2.0', 'sesion_id': self.sesion_actual}
        )
    
    def registrar_evento(self, nivel: NivelEvento, tipo_evento: TipoEvento,
                        mensaje: str, detalles: Optional[Dict[str, Any]] = None,
                        usuario: str = "sistema", archivo_origen: str = "",
                        duracion_ms: Optional[int] = None):
        """Registrar evento de auditoría."""
        evento = EventoAuditoria(
            nivel=nivel,
            tipo_evento=tipo_evento,
            usuario=usuario,
            sesion_id=self.sesion_actual,
            mensaje=mensaje,
            detalles=detalles or {},
            archivo_origen=archivo_origen,
            duracion_ms=duracion_ms
        )
        
        # Agregar a cola para procesamiento asíncrono
        self.cola_eventos.put(evento)
    
    @contextmanager
    def cronometrar_operacion(self, tipo_evento: TipoEvento, descripcion: str, 
                             usuario: str = "sistema", archivo: str = ""):
        """Context manager para cronometrar operaciones."""
        inicio = datetime.now()
        
        try:
            yield
            
            # Operación exitosa
            duracion = (datetime.now() - inicio).total_seconds() * 1000
            self.registrar_evento(
                nivel=NivelEvento.INFO,
                tipo_evento=tipo_evento,
                mensaje=f"Operación completada: {descripcion}",
                usuario=usuario,
                archivo_origen=archivo,
                duracion_ms=int(duracion)
            )
            
        except Exception as e:
            # Operación falló
            duracion = (datetime.now() - inicio).total_seconds() * 1000
            self.registrar_evento(
                nivel=NivelEvento.ERROR,
                tipo_evento=TipoEvento.ERROR_PROCESAMIENTO,
                mensaje=f"Operación falló: {descripcion} - Error: {str(e)}",
                usuario=usuario,
                archivo_origen=archivo,
                duracion_ms=int(duracion),
                detalles={'error': str(e), 'tipo_error': type(e).__name__}
            )
            raise
    
    def obtener_metricas_rendimiento(self) -> Dict[str, Any]:
        """Obtener métricas actuales de rendimiento."""
        return self.metricas_rendimiento.copy()
    
    def buscar_eventos(self, filtros: Dict[str, Any], 
                      fecha_inicio: Optional[datetime] = None,
                      fecha_fin: Optional[datetime] = None) -> List[EventoAuditoria]:
        """Buscar eventos en los logs (implementación simplificada)."""
        # En una implementación real, esto buscaría en los archivos de log
        # o en una base de datos de auditoría
        eventos_encontrados = []
        
        # Por ahora, retornar lista vacía
        logger.info(f"Búsqueda de eventos con filtros: {filtros}")
        
        return eventos_encontrados
    
    def generar_reporte_auditoria(self, fecha_inicio: datetime, 
                                 fecha_fin: datetime) -> Dict[str, Any]:
        """Generar reporte de auditoría para un período."""
        reporte = {
            'periodo': {
                'inicio': fecha_inicio.isoformat(),
                'fin': fecha_fin.isoformat()
            },
            'resumen': {
                'total_eventos': 0,
                'eventos_por_nivel': {},
                'eventos_por_tipo': {},
                'usuarios_activos': set(),
                'archivos_procesados': set()
            },
            'alertas_generadas': 0,
            'tiempo_promedio_operaciones': 0.0
        }
        
        # En una implementación real, esto analizaría los logs del período
        logger.info(f"Generando reporte de auditoría para período {fecha_inicio} - {fecha_fin}")
        
        return reporte
    
    def archivar_logs_antiguos(self, dias_retencion: int = 90):
        """Archivar logs antiguos según política de retención."""
        fecha_limite = datetime.now() - timedelta(days=dias_retencion)
        
        # Buscar archivos de log antiguos
        archivos_archivados = 0
        
        for directorio in [self.dir_auditoria, self.dir_seguridad, 
                          self.dir_rendimiento, self.dir_errores]:
            for archivo_log in directorio.glob("*.log.*"):
                try:
                    # Verificar fecha de modificación
                    fecha_modificacion = datetime.fromtimestamp(archivo_log.stat().st_mtime)
                    
                    if fecha_modificacion < fecha_limite:
                        # Mover a directorio de archivados
                        archivo_destino = self.dir_archivados / archivo_log.name
                        archivo_log.rename(archivo_destino)
                        archivos_archivados += 1
                        
                except Exception as e:
                    logger.error(f"Error archivando {archivo_log}: {e}")
        
        self.registrar_evento(
            nivel=NivelEvento.AUDITORIA,
            tipo_evento=TipoEvento.OPERACION_SEGURIDAD,
            mensaje=f"Archivado de logs completado: {archivos_archivados} archivos archivados",
            detalles={'archivos_archivados': archivos_archivados, 'dias_retencion': dias_retencion}
        )
    
    def finalizar(self):
        """Finalizar el gestor de logging."""
        self.registrar_evento(
            nivel=NivelEvento.AUDITORIA,
            tipo_evento=TipoEvento.FIN_SESION,
            mensaje="Sistema de logging empresarial finalizando",
            detalles=self.obtener_metricas_rendimiento()
        )
        
        # Detener procesamiento de eventos
        self.procesando_eventos = False
        
        # Esperar a que termine el hilo de procesamiento
        if self.hilo_procesamiento.is_alive():
            self.hilo_procesamiento.join(timeout=5.0)
        
        # Procesar eventos restantes en la cola
        while not self.cola_eventos.empty():
            try:
                evento = self.cola_eventos.get_nowait()
                self._procesar_evento_individual(evento)
            except queue.Empty:
                break


# Instancia global del gestor de logging
GESTOR_LOGGING = GestorLoggingEmpresarial()
