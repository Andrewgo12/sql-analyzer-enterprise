"""
Gestor de Configuración Empresarial

Sistema avanzado de gestión de configuración para diferentes entornos,
perfiles de usuario, y configuraciones específicas de la industria.
"""

import os
import json
import yaml
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TipoEntorno(Enum):
    """Tipos de entorno de configuración."""
    DESARROLLO = "desarrollo"
    PRUEBAS = "pruebas"
    PRODUCCION = "produccion"
    EMPRESARIAL = "empresarial"


class NivelHabilidad(Enum):
    """Niveles de habilidad del usuario."""
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    EXPERTO = "experto"
    DESARROLLADOR = "desarrollador"


@dataclass
class ConfiguracionBaseDatos:
    """Configuración específica de base de datos."""
    tipo: str = "mysql"
    host: str = "localhost"
    puerto: int = 3306
    nombre_bd: str = ""
    usuario: str = ""
    contraseña: str = ""
    ssl_habilitado: bool = False
    timeout_conexion: int = 30
    pool_conexiones: int = 10
    charset: str = "utf8mb4"


@dataclass
class ConfiguracionRendimiento:
    """Configuración de rendimiento del sistema."""
    max_trabajadores: int = 8
    tamaño_cache_mb: int = 1000
    limite_memoria_gb: float = 4.0
    procesamiento_paralelo: bool = True
    optimizacion_memoria: bool = True
    usar_cache_disco: bool = True
    directorio_cache: str = ""
    limite_tamaño_archivo_gb: float = 10.0


@dataclass
class ConfiguracionSeguridad:
    """Configuración de seguridad empresarial."""
    cifrado_habilitado: bool = True
    algoritmo_cifrado: str = "AES-256"
    autenticacion_requerida: bool = False
    timeout_sesion_minutos: int = 60
    registro_auditoria: bool = True
    nivel_registro: str = "INFO"
    directorio_logs: str = ""
    rotacion_logs: bool = True
    retencion_logs_dias: int = 30


@dataclass
class ConfiguracionAnalisis:
    """Configuración de análisis SQL."""
    analisis_sintaxis: bool = True
    deteccion_errores: bool = True
    analisis_esquema: bool = True
    analisis_dominio: bool = True
    analisis_rendimiento: bool = True
    analisis_seguridad: bool = False
    correcciones_automaticas: bool = False
    generar_reportes: bool = True
    formatos_reporte: List[str] = field(default_factory=lambda: ["html", "markdown"])


@dataclass
class ConfiguracionSalida:
    """Configuración de archivos de salida."""
    directorio_salida: str = "resultados_analisis"
    mantener_formato_original: bool = True
    agregar_comentarios: bool = True
    crear_respaldos: bool = True
    organizar_por_fecha: bool = True
    crear_archivo_conclusiones: bool = True
    comprimir_salida: bool = False
    formato_nombres: str = "{nombre_original}_{timestamp}"


@dataclass
class ConfiguracionEmpresarial:
    """Configuración empresarial completa."""
    # Información general
    nombre_organizacion: str = ""
    entorno: TipoEntorno = TipoEntorno.DESARROLLO
    nivel_habilidad: NivelHabilidad = NivelHabilidad.INTERMEDIO
    version_config: str = "2.0"
    creado_en: datetime = field(default_factory=datetime.now)
    actualizado_en: datetime = field(default_factory=datetime.now)
    
    # Configuraciones específicas
    base_datos: ConfiguracionBaseDatos = field(default_factory=ConfiguracionBaseDatos)
    rendimiento: ConfiguracionRendimiento = field(default_factory=ConfiguracionRendimiento)
    seguridad: ConfiguracionSeguridad = field(default_factory=ConfiguracionSeguridad)
    analisis: ConfiguracionAnalisis = field(default_factory=ConfiguracionAnalisis)
    salida: ConfiguracionSalida = field(default_factory=ConfiguracionSalida)
    
    # Configuraciones personalizadas
    configuraciones_personalizadas: Dict[str, Any] = field(default_factory=dict)
    plantillas_personalizadas: Dict[str, str] = field(default_factory=dict)
    reglas_personalizadas: List[str] = field(default_factory=list)


class GestorConfiguracion:
    """
    Gestor de configuración empresarial avanzado.
    
    Características:
    - Configuraciones por entorno (desarrollo, pruebas, producción)
    - Perfiles de usuario por nivel de habilidad
    - Configuraciones específicas de industria
    - Validación y migración de configuraciones
    - Respaldo y restauración automática
    - Configuración distribuida para equipos
    """
    
    def __init__(self, directorio_config: Optional[Path] = None):
        """Inicializar el gestor de configuración."""
        self.directorio_config = directorio_config or Path.home() / ".analizador_sql"
        self.directorio_config.mkdir(parents=True, exist_ok=True)
        
        # Archivos de configuración
        self.archivo_config_principal = self.directorio_config / "config.yaml"
        self.archivo_config_usuario = self.directorio_config / "usuario.json"
        self.directorio_perfiles = self.directorio_config / "perfiles"
        self.directorio_plantillas = self.directorio_config / "plantillas"
        self.directorio_respaldos = self.directorio_config / "respaldos"
        
        # Crear directorios necesarios
        for directorio in [self.directorio_perfiles, self.directorio_plantillas, self.directorio_respaldos]:
            directorio.mkdir(exist_ok=True)
        
        # Configuración actual
        self.configuracion_actual: Optional[ConfiguracionEmpresarial] = None
        self.perfiles_disponibles: Dict[str, ConfiguracionEmpresarial] = {}
        
        # Cargar configuración
        self._cargar_configuracion()
    
    def obtener_configuracion(self) -> ConfiguracionEmpresarial:
        """Obtener configuración actual."""
        return self.configuracion_actual
    
    def actualizar_configuracion(self, nueva_config: ConfiguracionEmpresarial):
        """Actualizar configuración actual."""
        nueva_config.actualizado_en = datetime.now()
        self.configuracion_actual = nueva_config
        self._guardar_configuracion()
    
    def crear_perfil(self, nombre_perfil: str, configuracion: ConfiguracionEmpresarial):
        """Crear nuevo perfil de configuración."""
        archivo_perfil = self.directorio_perfiles / f"{nombre_perfil}.yaml"
        
        # Convertir a diccionario y guardar
        datos_perfil = asdict(configuracion)
        datos_perfil['entorno'] = configuracion.entorno.value
        datos_perfil['nivel_habilidad'] = configuracion.nivel_habilidad.value
        datos_perfil['creado_en'] = configuracion.creado_en.isoformat()
        datos_perfil['actualizado_en'] = datetime.now().isoformat()
        
        with open(archivo_perfil, 'w', encoding='utf-8') as f:
            yaml.dump(datos_perfil, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        self.perfiles_disponibles[nombre_perfil] = configuracion
        logger.info(f"Perfil '{nombre_perfil}' creado exitosamente")
    
    def cargar_perfil(self, nombre_perfil: str) -> bool:
        """Cargar perfil específico."""
        if nombre_perfil in self.perfiles_disponibles:
            self.configuracion_actual = self.perfiles_disponibles[nombre_perfil]
            self._guardar_configuracion()
            logger.info(f"Perfil '{nombre_perfil}' cargado exitosamente")
            return True
        else:
            logger.error(f"Perfil '{nombre_perfil}' no encontrado")
            return False
    
    def listar_perfiles(self) -> List[str]:
        """Listar perfiles disponibles."""
        return list(self.perfiles_disponibles.keys())
    
    def validar_configuracion(self) -> List[str]:
        """Validar configuración actual y retornar lista de problemas."""
        problemas = []
        
        config = self.configuracion_actual
        
        # Validar configuración de rendimiento
        if config.rendimiento.max_trabajadores < 1:
            problemas.append("Número de trabajadores debe ser mayor a 0")
        
        if config.rendimiento.limite_memoria_gb < 0.5:
            problemas.append("Límite de memoria debe ser al menos 0.5 GB")
        
        # Validar configuración de base de datos
        if config.base_datos.puerto < 1 or config.base_datos.puerto > 65535:
            problemas.append("Puerto de base de datos debe estar entre 1 y 65535")
        
        # Validar configuración de salida
        if not config.salida.directorio_salida:
            problemas.append("Directorio de salida no puede estar vacío")
        
        return problemas
    
    def obtener_configuracion_por_entorno(self, entorno: TipoEntorno) -> ConfiguracionEmpresarial:
        """Obtener configuración optimizada para un entorno específico."""
        config = ConfiguracionEmpresarial()
        config.entorno = entorno
        
        if entorno == TipoEntorno.DESARROLLO:
            config.rendimiento.max_trabajadores = 4
            config.rendimiento.limite_memoria_gb = 2.0
            config.seguridad.registro_auditoria = False
            config.analisis.analisis_seguridad = False
        
        elif entorno == TipoEntorno.PRUEBAS:
            config.rendimiento.max_trabajadores = 6
            config.rendimiento.limite_memoria_gb = 4.0
            config.seguridad.registro_auditoria = True
            config.analisis.analisis_seguridad = True
        
        elif entorno == TipoEntorno.PRODUCCION:
            config.rendimiento.max_trabajadores = 8
            config.rendimiento.limite_memoria_gb = 8.0
            config.seguridad.registro_auditoria = True
            config.seguridad.cifrado_habilitado = True
            config.analisis.analisis_seguridad = True
            config.salida.crear_respaldos = True
        
        elif entorno == TipoEntorno.EMPRESARIAL:
            config.rendimiento.max_trabajadores = 16
            config.rendimiento.limite_memoria_gb = 16.0
            config.seguridad.registro_auditoria = True
            config.seguridad.cifrado_habilitado = True
            config.seguridad.autenticacion_requerida = True
            config.analisis.analisis_seguridad = True
            config.salida.crear_respaldos = True
            config.salida.comprimir_salida = True
        
        return config


# Instancia global del gestor de configuración
GESTOR_CONFIG = GestorConfiguracion()
