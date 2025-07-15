"""
Interfaz de Línea de Comandos para Analizador SQL - Edición Empresarial

Interfaz CLI empresarial con características avanzadas incluyendo:
- Procesamiento de archivos masivos (10GB+) con paralelización
- Reconocimiento inteligente de dominios industriales
- Análisis de seguridad y cumplimiento normativo
- Gestión avanzada de sesiones y configuración
- Reportes comprehensivos en múltiples formatos
- Integración con herramientas empresariales
"""

import os
import sys
import time
import json
import yaml
import pickle
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.rule import Rule
from rich.status import Status
from rich.spinner import Spinner
import questionary
from questionary import Style
import configparser
import threading
import queue
from collections import defaultdict

# Import core modules
from sql_analyzer.core.file_processor import FileProcessor, FileInfo
from sql_analyzer.core.sql_parser import SQLParser
from sql_analyzer.core.error_detector import ErrorDetector
from sql_analyzer.core.schema_analyzer import SchemaAnalyzer
from sql_analyzer.core.format_converter import FormatConverter, DatabaseType
from sql_analyzer.core.data_types import DATA_TYPE_REGISTRY

@dataclass
class UserPreferences:
    """User preferences for the CLI interface."""
    default_output_format: str = "enhanced_sql"
    auto_save_results: bool = True
    show_progress_bars: bool = True
    color_output: bool = True
    max_concurrent_analyses: int = 3
    default_analysis_types: List[str] = field(default_factory=lambda: ["syntax", "schema", "performance"])

# Simple ProcessingOptions class for compatibility
@dataclass
class ProcessingOptions:
    """Processing options for SQL analysis."""
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    timeout: int = 300  # 5 minutes
    parallel_processing: bool = True
    memory_limit: int = 1024 * 1024 * 1024  # 1GB
from sql_analyzer.core.domain_recognition import DOMAIN_RECOGNIZER


@dataclass
class SesionProcesamiento:
    """Representa una sesión de procesamiento con todos sus datos."""
    id_sesion: str
    creado_en: datetime
    archivos_procesados: List[str] = field(default_factory=list)
    resultados: Dict[str, Any] = field(default_factory=dict)
    configuracion: Dict[str, Any] = field(default_factory=dict)
    estadisticas: Dict[str, Any] = field(default_factory=dict)
    notas: List[str] = field(default_factory=list)
    etiquetas: List[str] = field(default_factory=list)


@dataclass
class PreferenciasUsuario:
    """Preferencias y configuraciones del usuario."""
    formato_salida_predeterminado: str = "detallado"
    guardar_sesiones_automaticamente: bool = True
    mostrar_barras_progreso: bool = True
    tema_color: str = "predeterminado"
    tamaño_maximo_archivo_mb: int = 1000
    procesamiento_paralelo: bool = True
    respaldo_automatico: bool = True
    nivel_notificacion: str = "normal"  # silencioso, normal, detallado
    base_datos_preferida: str = "mysql"
    plantillas_personalizadas: Dict[str, str] = field(default_factory=dict)


@dataclass
class OpcionesProcesamiento:
    """Opciones comprehensivas de procesamiento."""
    # Opciones de procesamiento de archivos
    mantener_formato_original: bool = True
    agregar_comentarios_debajo_problemas: bool = True
    aplicar_correcciones_automaticas: bool = False
    convertir_a_formato_base_datos: Optional[str] = None

    # Opciones de análisis
    realizar_analisis_sintaxis: bool = True
    realizar_deteccion_errores: bool = True
    realizar_analisis_esquema: bool = True
    realizar_analisis_dominio: bool = True
    realizar_analisis_rendimiento: bool = True
    realizar_analisis_seguridad: bool = True

    # Opciones de salida
    organizar_en_bloques_logicos: bool = True
    agregar_comentarios_detallados: bool = True
    generar_reporte_resumen: bool = True
    crear_archivo_conclusiones: bool = True

    # Opciones avanzadas
    procesamiento_paralelo: bool = True
    optimizacion_memoria: bool = True
    almacenar_resultados_cache: bool = True
    crear_respaldos: bool = True

    # Opciones de personalización
    reglas_personalizadas: List[str] = field(default_factory=list)
    verificaciones_excluidas: List[str] = field(default_factory=list)
    plantillas_personalizadas: Dict[str, str] = field(default_factory=dict)


class InterfazCLIMejorada:
    """
    Interfaz CLI de grado empresarial con funcionalidad comprehensiva.

    Características:
    - Interfaces de múltiples niveles de habilidad (Principiante, Intermedio, Experto)
    - Flujos de trabajo guiados y asistentes
    - Gestión de sesiones y funcionalidad guardar/cargar
    - Sistemas de ayuda comprehensivos y tutoriales
    - Gestión de configuración interactiva
    - Seguimiento de progreso en tiempo real con estimaciones de tiempo
    - Reportes avanzados y análisis
    - Plantillas personalizadas y automatización
    - Integración con herramientas externas
    """

    def __init__(self, detallado: bool = False):
        """Inicializar la interfaz CLI mejorada."""
        self.consola = Console()
        self.detallado = detallado

        # Inicializar componentes principales
        self.procesador_archivos = FileProcessor()
        self.analizador_sql = SQLParser()
        self.detector_errores = ErrorDetector()
        self.analizador_esquema = SchemaAnalyzer()
        self.convertidor_formato = FormatConverter()

        # Gestión de sesiones
        self.sesion_actual: Optional[SesionProcesamiento] = None
        self.historial_sesiones: List[SesionProcesamiento] = []
        self.directorio_sesiones = Path.home() / ".analizador_sql" / "sesiones"
        self.directorio_sesiones.mkdir(parents=True, exist_ok=True)

        # Preferencias del usuario
        self.preferencias = self._cargar_preferencias_usuario()
        self.archivo_config = Path.home() / ".analizador_sql" / "config.ini"

        # Estado de procesamiento
        self.cola_procesamiento = queue.Queue()
        self.cache_resultados = {}
        self.tareas_activas = {}

        # Personalización de UI
        self.estilo_personalizado = Style([
            ('qmark', 'fg:#ff9d00 bold'),
            ('question', 'bold'),
            ('answer', 'fg:#ff9d00 bold'),
            ('pointer', 'fg:#ff9d00 bold'),
            ('highlighted', 'fg:#ff9d00 bold'),
            ('selected', 'fg:#cc5454'),
            ('separator', 'fg:#cc5454'),
            ('instruction', ''),
            ('text', ''),
            ('disabled', 'fg:#858585 italic')
        ])

        # Cargar sesiones anteriores
        self._cargar_historial_sesiones()

        # Mostrar bienvenida mejorada
        self._mostrar_bienvenida_mejorada()

    def _mostrar_bienvenida_mejorada(self):
        """Mostrar mensaje de bienvenida mejorado con información del sistema."""
        contenido_bienvenida = f"""
[bold blue]Analizador y Corrector SQL - Edición Empresarial[/bold blue]
[dim]Versión 2.0 - Análisis SQL Avanzado y Soporte Multi-Base de Datos[/dim]

[bold green]🚀 Características Empresariales:[/bold green]
• Procesar archivos hasta 10GB+ con procesamiento paralelo
• Soporte para 100+ formatos de archivo y todas las bases de datos principales
• Reconocimiento de dominio con IA para cualquier industria
• Detección de errores en tiempo real y corrección automática
• Análisis de esquema avanzado y optimización
• Verificación de seguridad y cumplimiento comprehensiva

[bold yellow]📊 Estado del Sistema:[/bold yellow]
• Memoria Disponible: {self._obtener_memoria_disponible():.1f} GB
• Núcleos CPU: {os.cpu_count()}
• Trabajadores Paralelos: {self.procesador_archivos.max_workers}
• Tamaño Cache: {self.procesador_archivos.file_cache.max_cache_size // (1024*1024)} MB

[bold cyan]💡 Inicio Rápido:[/bold cyan]
• Escribe 'ayuda' para documentación comprehensiva
• Usa 'asistente' para configuración guiada
• Prueba 'demo' para ejemplos interactivos
        """

        self.consola.print(Panel(contenido_bienvenida, title="Bienvenido", border_style="blue", padding=(1, 2)))

        # Mostrar actividad reciente si está disponible
        if self.historial_sesiones:
            sesion_reciente = self.historial_sesiones[-1]
            self.consola.print(f"[dim]Última sesión: {sesion_reciente.creado_en.strftime('%Y-%m-%d %H:%M')} "
                             f"({len(sesion_reciente.archivos_procesados)} archivos procesados)[/dim]")

    def _obtener_memoria_disponible(self) -> float:
        """Obtener memoria disponible del sistema en GB."""
        try:
            import psutil
            return psutil.virtual_memory().available / (1024**3)
        except ImportError:
            return 0.0

    def ejecutar_interactivo(self):
        """Ejecutar el modo CLI interactivo mejorado."""
        while True:
            try:
                # Mostrar menú principal basado en el nivel de habilidad del usuario
                nivel_habilidad = self.preferencias.get('nivel_habilidad', 'intermedio')

                if nivel_habilidad == 'principiante':
                    eleccion = self._mostrar_menu_principiante()
                elif nivel_habilidad == 'experto':
                    eleccion = self._mostrar_menu_experto()
                else:
                    eleccion = self._mostrar_menu_intermedio()

                # Manejar opciones del menú
                if eleccion == "salir":
                    self._manejar_salida()
                    break
                elif eleccion == "analizar_archivo":
                    self._asistente_analizar_archivo()
                elif eleccion == "procesamiento_lote":
                    self._asistente_procesamiento_lote()
                elif eleccion == "convertir_formato":
                    self._asistente_conversion_formato()
                elif eleccion == "analisis_esquema":
                    self._asistente_analisis_esquema()
                elif eleccion == "analisis_dominio":
                    self._asistente_analisis_dominio()
                elif eleccion == "explorador_tipos_datos":
                    self._explorador_tipos_datos()
                elif eleccion == "gestion_sesiones":
                    self._menu_gestion_sesiones()
                elif eleccion == "configuracion":
                    self._menu_configuracion()
                elif eleccion == "ayuda":
                    self._mostrar_ayuda_comprehensiva()
                elif eleccion == "tutorial":
                    self._ejecutar_tutorial_interactivo()
                elif eleccion == "demo":
                    self._ejecutar_modo_demo()
                elif eleccion == "asistente":
                    self._ejecutar_asistente_configuracion()
                elif eleccion == "analiticas":
                    self._mostrar_panel_analiticas()
                elif eleccion == "plantillas":
                    self._gestion_plantillas()
                elif eleccion == "integraciones":
                    self._gestion_integraciones()
                else:
                    self.consola.print("[red]Opción inválida. Por favor intenta de nuevo.[/red]")

            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]¿Estás seguro de que quieres salir?[/yellow]"):
                    self._manejar_salida()
                    break
            except Exception as e:
                self.consola.print(f"[red]Error: {e}[/red]")
                if self.detallado:
                    import traceback
                    self.consola.print(traceback.format_exc())

    def _mostrar_menu_principiante(self) -> str:
        """Mostrar menú amigable para principiantes."""
        self.consola.print("\n[bold]🌟 Modo Principiante - Simple y Guiado[/bold]")

        opciones = [
            "🔍 Analizar un archivo SQL (Guiado)",
            "📁 Procesar múltiples archivos",
            "🔄 Convertir formato de base de datos",
            "📚 Tutorial interactivo",
            "🎯 Modo demostración",
            "⚙️ Asistente de configuración",
            "❓ Ayuda y documentación",
            "🚪 Salir"
        ]

        eleccion = questionary.select(
            "¿Qué te gustaría hacer?",
            choices=opciones,
            style=self.estilo_personalizado
        ).ask()

        mapa_opciones = {
            opciones[0]: "analizar_archivo",
            opciones[1]: "procesamiento_lote",
            opciones[2]: "convertir_formato",
            opciones[3]: "tutorial",
            opciones[4]: "demo",
            opciones[5]: "asistente",
            opciones[6]: "ayuda",
            opciones[7]: "salir"
        }

        return mapa_opciones.get(eleccion, "ayuda")

    def _mostrar_menu_intermedio(self) -> str:
        """Mostrar menú para usuario intermedio."""
        self.consola.print("\n[bold]⚡ Modo Intermedio - Características Balanceadas[/bold]")

        opciones = [
            "📄 Analizar archivo SQL",
            "📁 Procesamiento en lote",
            "🔄 Conversión de formato",
            "🏗️ Análisis de esquema",
            "🎯 Análisis de dominio",
            "📊 Panel de analíticas",
            "💾 Gestión de sesiones",
            "⚙️ Configuración",
            "📚 Ayuda y tutoriales",
            "🚪 Salir"
        ]

        eleccion = questionary.select(
            "Selecciona una operación:",
            choices=opciones,
            style=self.estilo_personalizado
        ).ask()

        mapa_opciones = {
            opciones[0]: "analizar_archivo",
            opciones[1]: "procesamiento_lote",
            opciones[2]: "convertir_formato",
            opciones[3]: "analisis_esquema",
            opciones[4]: "analisis_dominio",
            opciones[5]: "analiticas",
            opciones[6]: "gestion_sesiones",
            opciones[7]: "configuracion",
            opciones[8]: "ayuda",
            opciones[9]: "salir"
        }

        return mapa_opciones.get(eleccion, "ayuda")

    def _mostrar_menu_experto(self) -> str:
        """Mostrar menú de usuario experto con todas las características."""
        self.consola.print("\n[bold]🚀 Modo Experto - Acceso Completo a Características[/bold]")

        opciones = [
            "📄 Análisis de Archivo (Avanzado)",
            "📁 Procesamiento en Lote (Paralelo)",
            "🔄 Conversión de Formato (Multi-BD)",
            "🏗️ Análisis de Esquema (Profundo)",
            "🎯 Reconocimiento de Dominio (IA)",
            "🔍 Explorador de Tipos de Datos",
            "📊 Analíticas y Reportes",
            "💾 Gestión de Sesiones",
            "📝 Gestión de Plantillas",
            "🔗 Integraciones de Herramientas",
            "⚙️ Configuración Avanzada",
            "🛠️ Herramientas de Desarrollador",
            "📚 Documentación",
            "🚪 Salir"
        ]

        eleccion = questionary.select(
            "Elige operación:",
            choices=opciones,
            style=self.estilo_personalizado
        ).ask()

        mapa_opciones = {
            opciones[0]: "analizar_archivo",
            opciones[1]: "procesamiento_lote",
            opciones[2]: "convertir_formato",
            opciones[3]: "analisis_esquema",
            opciones[4]: "analisis_dominio",
            opciones[5]: "explorador_tipos_datos",
            opciones[6]: "analiticas",
            opciones[7]: "gestion_sesiones",
            opciones[8]: "plantillas",
            opciones[9]: "integraciones",
            opciones[10]: "configuracion",
            opciones[11]: "herramientas_desarrollador",
            opciones[12]: "ayuda",
            opciones[13]: "salir"
        }

        return mapa_opciones.get(eleccion, "ayuda")

    def _analyze_file_wizard(self):
        """Comprehensive file analysis wizard."""
        self.console.print("\n[bold blue]📄 File Analysis Wizard[/bold blue]")

        # Step 1: File selection
        file_path = self._get_file_path_interactive()
        if not file_path:
            return

        # Step 2: Processing options
        options = self._get_processing_options_interactive()

        # Step 3: Output preferences
        output_config = self._get_output_configuration()

        # Step 4: Confirm and process
        self._confirm_and_process_file(file_path, options, output_config)

    def _get_file_path_interactive(self) -> Optional[str]:
        """Interactive file path selection with validation."""
        while True:
            # Option to browse or enter path
            selection_method = questionary.select(
                "How would you like to select the file?",
                choices=[
                    "📁 Browse for file",
                    "⌨️ Enter file path",
                    "📋 Select from recent files",
                    "🔙 Back to main menu"
                ],
                style=self.custom_style
            ).ask()

            if selection_method == "🔙 Back to main menu":
                return None
            elif selection_method == "📁 Browse for file":
                file_path = self._browse_for_file()
            elif selection_method == "⌨️ Enter file path":
                file_path = questionary.path(
                    "Enter the file path:",
                    validate=lambda x: Path(x).exists() or "File does not exist"
                ).ask()
            elif selection_method == "📋 Select from recent files":
                file_path = self._select_from_recent_files()
            else:
                continue

            if file_path and Path(file_path).exists():
                # Show file information
                self._display_file_preview(file_path)

                if Confirm.ask("Use this file?"):
                    return file_path
            else:
                self.console.print("[red]File not found or invalid path.[/red]")
                if not Confirm.ask("Try again?"):
                    return None

    def _browse_for_file(self) -> Optional[str]:
        """Simple file browser implementation."""
        current_dir = Path.cwd()

        while True:
            # List directory contents
            try:
                items = []

                # Add parent directory option
                if current_dir.parent != current_dir:
                    items.append("📁 .. (Parent Directory)")

                # Add directories
                for item in sorted(current_dir.iterdir()):
                    if item.is_dir():
                        items.append(f"📁 {item.name}/")
                    elif item.suffix.lower() in ['.sql', '.txt', '.json', '.csv', '.xlsx']:
                        items.append(f"📄 {item.name}")

                items.append("🔙 Back")

                if not items:
                    self.console.print("[yellow]No accessible files in this directory.[/yellow]")
                    return None

                choice = questionary.select(
                    f"Current directory: {current_dir}",
                    choices=items,
                    style=self.custom_style
                ).ask()

                if choice == "🔙 Back":
                    return None
                elif choice.startswith("📁 .. "):
                    current_dir = current_dir.parent
                elif choice.startswith("📁 "):
                    dir_name = choice[2:].rstrip('/')
                    current_dir = current_dir / dir_name
                elif choice.startswith("📄 "):
                    file_name = choice[2:]
                    return str(current_dir / file_name)

            except PermissionError:
                self.console.print("[red]Permission denied accessing this directory.[/red]")
                return None

    def _select_from_recent_files(self) -> Optional[str]:
        """Select from recently processed files."""
        recent_files = []

        # Collect recent files from session history
        for session in self.session_history[-10:]:  # Last 10 sessions
            recent_files.extend(session.files_processed)

        # Remove duplicates and non-existent files
        unique_files = []
        seen = set()
        for file_path in reversed(recent_files):  # Most recent first
            if file_path not in seen and Path(file_path).exists():
                unique_files.append(file_path)
                seen.add(file_path)
                if len(unique_files) >= 10:  # Limit to 10 files
                    break

        if not unique_files:
            self.console.print("[yellow]No recent files found.[/yellow]")
            return None

        # Add relative paths for display
        display_files = []
        for file_path in unique_files:
            try:
                rel_path = Path(file_path).relative_to(Path.cwd())
                display_files.append(f"📄 {rel_path}")
            except ValueError:
                display_files.append(f"📄 {file_path}")

        display_files.append("🔙 Back")

        choice = questionary.select(
            "Select a recent file:",
            choices=display_files,
            style=self.custom_style
        ).ask()

        if choice == "🔙 Back":
            return None

        # Find the corresponding file path
        index = display_files.index(choice)
        return unique_files[index]

    def _display_file_preview(self, file_path: str):
        """Display file information and preview."""
        try:
            file_info = self.file_processor.get_file_info_enterprise(file_path)

            # Create file info table
            info_table = Table(title=f"File Information: {Path(file_path).name}")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value")

            info_table.add_row("Path", file_path)
            info_table.add_row("Size", f"{file_info.size:,} bytes ({file_info.size / (1024*1024):.2f} MB)")
            info_table.add_row("Format", file_info.format)
            info_table.add_row("Encoding", file_info.encoding)
            info_table.add_row("Estimated Lines", f"{file_info.line_count:,}")
            info_table.add_row("Processing Time", f"{file_info.estimated_processing_time:.1f} seconds")
            info_table.add_row("Memory Required", f"{file_info.memory_requirement / (1024*1024):.1f} MB")
            info_table.add_row("Supported", "✅" if file_info.supported else "❌")

            self.console.print(info_table)

            # Show file preview if it's a text file
            if file_info.supported and file_info.size < 1024 * 1024:  # Less than 1MB
                self._show_file_preview_content(file_path)

        except Exception as e:
            self.console.print(f"[red]Error reading file information: {e}[/red]")

    def _show_file_preview_content(self, file_path: str, max_lines: int = 10):
        """Show preview of file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip())

            if lines:
                preview_content = '\n'.join(lines)
                if len(lines) == max_lines:
                    preview_content += "\n... (truncated)"

                syntax = Syntax(preview_content, "sql", theme="monokai", line_numbers=True)
                self.console.print(Panel(syntax, title="File Preview", border_style="dim"))

        except Exception as e:
            self.console.print(f"[dim]Could not preview file content: {e}[/dim]")

    def _get_processing_options_interactive(self) -> ProcessingOptions:
        """Interactive processing options configuration."""
        self.console.print("\n[bold]⚙️ Processing Options[/bold]")

        # Quick presets or custom configuration
        preset_choice = questionary.select(
            "Choose processing mode:",
            choices=[
                "🚀 Quick Analysis (Fast, basic checks)",
                "⚖️ Balanced Analysis (Recommended)",
                "🔬 Comprehensive Analysis (Thorough, slower)",
                "🛠️ Custom Configuration"
            ],
            style=self.custom_style
        ).ask()

        if preset_choice == "🚀 Quick Analysis (Fast, basic checks)":
            return ProcessingOptions(
                perform_syntax_analysis=True,
                perform_error_detection=True,
                perform_schema_analysis=False,
                perform_domain_analysis=False,
                perform_performance_analysis=False,
                perform_security_analysis=False,
                organize_into_logical_blocks=False,
                add_detailed_comments=False
            )
        elif preset_choice == "⚖️ Balanced Analysis (Recommended)":
            return ProcessingOptions(
                perform_syntax_analysis=True,
                perform_error_detection=True,
                perform_schema_analysis=True,
                perform_domain_analysis=True,
                perform_performance_analysis=True,
                perform_security_analysis=False,
                organize_into_logical_blocks=True,
                add_detailed_comments=True
            )
        elif preset_choice == "🔬 Comprehensive Analysis (Thorough, slower)":
            return ProcessingOptions(
                perform_syntax_analysis=True,
                perform_error_detection=True,
                perform_schema_analysis=True,
                perform_domain_analysis=True,
                perform_performance_analysis=True,
                perform_security_analysis=True,
                organize_into_logical_blocks=True,
                add_detailed_comments=True,
                create_conclusions_arc=True
            )
        else:
            return self._get_custom_processing_options()

    def _get_custom_processing_options(self) -> ProcessingOptions:
        """Get custom processing options through interactive prompts."""
        options = ProcessingOptions()

        self.console.print("\n[bold]🛠️ Custom Configuration[/bold]")

        # Analysis options
        analysis_choices = questionary.checkbox(
            "Select analysis types to perform:",
            choices=[
                "Syntax Analysis",
                "Error Detection",
                "Schema Analysis",
                "Domain Analysis",
                "Performance Analysis",
                "Security Analysis"
            ],
            default=["Syntax Analysis", "Error Detection", "Schema Analysis"]
        ).ask()

        options.perform_syntax_analysis = "Syntax Analysis" in analysis_choices
        options.perform_error_detection = "Error Detection" in analysis_choices
        options.perform_schema_analysis = "Schema Analysis" in analysis_choices
        options.perform_domain_analysis = "Domain Analysis" in analysis_choices
        options.perform_performance_analysis = "Performance Analysis" in analysis_choices
        options.perform_security_analysis = "Security Analysis" in analysis_choices

        # Output format options
        output_choices = questionary.checkbox(
            "Select output options:",
            choices=[
                "Keep original format with comments",
                "Apply automatic corrections",
                "Organize into logical blocks",
                "Add detailed comments",
                "Generate summary report",
                "Create conclusions archive"
            ],
            default=["Keep original format with comments", "Add detailed comments"]
        ).ask()

        options.keep_original_format = "Keep original format with comments" in output_choices
        options.apply_automatic_corrections = "Apply automatic corrections" in output_choices
        options.organize_into_logical_blocks = "Organize into logical blocks" in output_choices
        options.add_detailed_comments = "Add detailed comments" in output_choices
        options.generate_summary_report = "Generate summary report" in output_choices
        options.create_conclusions_arc = "Create conclusions archive" in output_choices

        # Database conversion option
        if questionary.confirm("Convert to different database format?").ask():
            database_choices = [db.value for db in DatabaseType]
            target_db = questionary.select(
                "Select target database:",
                choices=database_choices
            ).ask()
            options.convert_to_database_format = target_db

        # Advanced options
        if questionary.confirm("Configure advanced options?").ask():
            options.parallel_processing = questionary.confirm("Enable parallel processing?", default=True).ask()
            options.memory_optimization = questionary.confirm("Enable memory optimization?", default=True).ask()
            options.cache_results = questionary.confirm("Cache results for faster re-processing?", default=True).ask()
            options.create_backups = questionary.confirm("Create backup of original files?", default=True).ask()

        return options

    def _get_output_configuration(self) -> Dict[str, Any]:
        """Get output configuration preferences."""
        self.console.print("\n[bold]📁 Output Configuration[/bold]")

        config = {}

        # Output directory
        default_output = Path.cwd() / "sql_analysis_results"
        output_dir = questionary.path(
            "Output directory:",
            default=str(default_output)
        ).ask()
        config['output_directory'] = output_dir

        # File naming convention
        naming_choice = questionary.select(
            "File naming convention:",
            choices=[
                "Keep original names with suffix",
                "Add timestamp to names",
                "Use custom naming pattern",
                "Organize by analysis type"
            ]
        ).ask()
        config['naming_convention'] = naming_choice

        # Report format
        report_formats = questionary.checkbox(
            "Generate reports in formats:",
            choices=["HTML", "PDF", "Markdown", "JSON", "Excel"],
            default=["HTML", "Markdown"]
        ).ask()
        config['report_formats'] = report_formats

        return config

    def _confirm_and_process_file(self, file_path: str,
                                 options: ProcessingOptions,
                                 output_config: Dict[str, Any]):
        """Confirm settings and process the file."""
        # Display summary
        self._display_processing_summary(file_path, options, output_config)

        if not Confirm.ask("\n[bold]Proceed with processing?[/bold]"):
            return

        # Create new session
        self._create_new_session()

        # Process the file with progress tracking
        self._process_file_with_progress(file_path, options, output_config)

    def _display_processing_summary(self, file_path: str,
                                   options: ProcessingOptions,
                                   output_config: Dict[str, Any]):
        """Display processing summary before execution."""
        summary_table = Table(title="Processing Summary")
        summary_table.add_column("Setting", style="cyan")
        summary_table.add_column("Value")

        summary_table.add_row("File", Path(file_path).name)
        summary_table.add_row("Output Directory", output_config['output_directory'])

        # Analysis types
        analysis_types = []
        if options.perform_syntax_analysis:
            analysis_types.append("Syntax")
        if options.perform_error_detection:
            analysis_types.append("Error Detection")
        if options.perform_schema_analysis:
            analysis_types.append("Schema")
        if options.perform_domain_analysis:
            analysis_types.append("Domain")
        if options.perform_performance_analysis:
            analysis_types.append("Performance")
        if options.perform_security_analysis:
            analysis_types.append("Security")

        summary_table.add_row("Analysis Types", ", ".join(analysis_types))

        # Output options
        output_options = []
        if options.keep_original_format:
            output_options.append("Original + Comments")
        if options.apply_automatic_corrections:
            output_options.append("Auto-Corrections")
        if options.organize_into_logical_blocks:
            output_options.append("Logical Blocks")
        if options.create_conclusions_arc:
            output_options.append("Conclusions Archive")

        summary_table.add_row("Output Options", ", ".join(output_options))

        if options.convert_to_database_format:
            summary_table.add_row("Convert To", options.convert_to_database_format)

        summary_table.add_row("Report Formats", ", ".join(output_config['report_formats']))

        self.console.print(summary_table)

    def _create_new_session(self):
        """Create a new processing session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = ProcessingSession(
            session_id=session_id,
            created_at=datetime.now()
        )
        self.session_history.append(self.current_session)

    def _process_file_with_progress(self, file_path: str,
                                   options: ProcessingOptions,
                                   output_config: Dict[str, Any]):
        """Process file with comprehensive progress tracking."""
        start_time = time.time()

        try:
            # Create output directory
            output_dir = Path(output_config['output_directory'])
            output_dir.mkdir(parents=True, exist_ok=True)

            # Initialize progress tracking
            total_steps = self._calculate_total_steps(options)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:

                main_task = progress.add_task("Processing file...", total=total_steps)

                # Step 1: File reading and parsing
                progress.update(main_task, description="Reading and parsing file...")
                sql_lines = list(self.file_processor.process_file_enterprise(file_path))
                parsed_statements = self.sql_parser.parse_sql_file(sql_lines)
                progress.advance(main_task)

                # Step 2: Error detection
                if options.perform_error_detection:
                    progress.update(main_task, description="Detecting errors...")
                    sql_content = '\n'.join(sql_lines)
                    errors = self.error_detector.analyze_sql(sql_content)
                    correction_result = self.error_detector.correct_sql(sql_content)
                    progress.advance(main_task)
                else:
                    errors = []
                    correction_result = None

                # Step 3: Schema analysis
                if options.perform_schema_analysis:
                    progress.update(main_task, description="Analyzing schema...")
                    schema_result = self.schema_analyzer.analyze_schema(self.sql_parser.tables)
                    progress.advance(main_task)
                else:
                    schema_result = None

                # Step 4: Domain analysis
                if options.perform_domain_analysis:
                    progress.update(main_task, description="Analyzing domain...")
                    domain_result = self._perform_domain_analysis()
                    progress.advance(main_task)
                else:
                    domain_result = None

                # Step 5: Performance analysis
                if options.perform_performance_analysis:
                    progress.update(main_task, description="Analyzing performance...")
                    performance_result = self._perform_performance_analysis(parsed_statements)
                    progress.advance(main_task)
                else:
                    performance_result = None

                # Step 6: Security analysis
                if options.perform_security_analysis:
                    progress.update(main_task, description="Analyzing security...")
                    security_result = self._perform_security_analysis(sql_content)
                    progress.advance(main_task)
                else:
                    security_result = None

                # Step 7: Format conversion
                if options.convert_to_database_format:
                    progress.update(main_task, description="Converting format...")
                    conversion_result = self._perform_format_conversion(
                        sql_content, options.convert_to_database_format
                    )
                    progress.advance(main_task)
                else:
                    conversion_result = None

                # Step 8: Generate outputs
                progress.update(main_task, description="Generating outputs...")
                self._generate_comprehensive_outputs(
                    file_path, output_dir, options, output_config,
                    {
                        'parsed_statements': parsed_statements,
                        'errors': errors,
                        'correction_result': correction_result,
                        'schema_result': schema_result,
                        'domain_result': domain_result,
                        'performance_result': performance_result,
                        'security_result': security_result,
                        'conversion_result': conversion_result
                    }
                )
                progress.advance(main_task)

                progress.update(main_task, description="✅ Processing complete!")

            # Update session
            processing_time = time.time() - start_time
            self.current_session.files_processed.append(file_path)
            self.current_session.statistics['processing_time'] = processing_time

            # Display results summary
            self._display_results_summary(file_path, output_dir, processing_time)

            # Save session
            if self.preferences.auto_save_sessions:
                self._save_current_session()

        except Exception as e:
            self.console.print(f"[red]Processing failed: {e}[/red]")
            if self.verbose:
                import traceback
                self.console.print(traceback.format_exc())

    def _calculate_total_steps(self, options: ProcessingOptions) -> int:
        """Calculate total processing steps for progress tracking."""
        steps = 1  # File reading

        if options.perform_error_detection:
            steps += 1
        if options.perform_schema_analysis:
            steps += 1
        if options.perform_domain_analysis:
            steps += 1
        if options.perform_performance_analysis:
            steps += 1
        if options.perform_security_analysis:
            steps += 1
        if options.convert_to_database_format:
            steps += 1

        steps += 1  # Output generation

        return steps

    def _perform_domain_analysis(self) -> Dict[str, Any]:
        """Perform domain analysis using the domain recognizer."""
        tables_dict = {}
        for table_name, table_obj in self.sql_parser.tables.items():
            column_names = [col.name for col in table_obj.columns]
            tables_dict[table_name] = column_names

        if tables_dict:
            domain_result = DOMAIN_RECOGNIZER.analyze_schema_domain(tables_dict)
            return {
                'primary_domain': domain_result.primary_domain.value,
                'confidence_score': domain_result.confidence_score,
                'secondary_domains': [(d.value, s) for d, s in domain_result.secondary_domains],
                'suggestions': domain_result.domain_specific_suggestions,
                'business_context': domain_result.business_context,
                'compliance_requirements': domain_result.compliance_requirements,
                'industry_standards': domain_result.industry_standards
            }

        return {'primary_domain': 'Unknown', 'confidence_score': 0.0}

    def _perform_performance_analysis(self, parsed_statements: List) -> Dict[str, Any]:
        """Perform performance analysis on parsed statements."""
        performance_issues = []
        recommendations = []

        for statement in parsed_statements:
            # Check for common performance issues
            if statement.statement_type.value == 'SELECT':
                # Check for SELECT *
                if '*' in statement.original_sql:
                    performance_issues.append({
                        'type': 'SELECT_ALL',
                        'severity': 'MEDIUM',
                        'message': 'SELECT * can impact performance',
                        'line': statement.line_number
                    })
                    recommendations.append('Specify explicit column names instead of SELECT *')

                # Check for missing WHERE clause
                if 'WHERE' not in statement.original_sql.upper():
                    performance_issues.append({
                        'type': 'NO_WHERE_CLAUSE',
                        'severity': 'HIGH',
                        'message': 'Query without WHERE clause may scan entire table',
                        'line': statement.line_number
                    })
                    recommendations.append('Add WHERE clause to limit result set')

        return {
            'issues_found': len(performance_issues),
            'performance_issues': performance_issues,
            'recommendations': recommendations,
            'overall_score': max(0, 100 - len(performance_issues) * 10)
        }

    def _perform_security_analysis(self, sql_content: str) -> Dict[str, Any]:
        """Perform security analysis on SQL content."""
        security_issues = []
        recommendations = []

        # Check for potential SQL injection patterns
        injection_patterns = [
            (r"'\s*OR\s*'1'\s*=\s*'1'", "Potential SQL injection pattern"),
            (r";\s*DROP\s+TABLE", "Potential DROP TABLE injection"),
            (r"UNION\s+SELECT", "Potential UNION-based injection"),
            (r"--", "SQL comments that might hide malicious code")
        ]

        for pattern, description in injection_patterns:
            if re.search(pattern, sql_content, re.IGNORECASE):
                security_issues.append({
                    'type': 'SQL_INJECTION_RISK',
                    'severity': 'HIGH',
                    'message': description,
                    'pattern': pattern
                })
                recommendations.append('Use parameterized queries to prevent SQL injection')

        # Check for hardcoded credentials
        credential_patterns = [
            (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
            (r"pwd\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
            (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret")
        ]

        for pattern, description in credential_patterns:
            if re.search(pattern, sql_content, re.IGNORECASE):
                security_issues.append({
                    'type': 'HARDCODED_CREDENTIALS',
                    'severity': 'CRITICAL',
                    'message': description,
                    'pattern': pattern
                })
                recommendations.append('Remove hardcoded credentials and use secure configuration')

        return {
            'issues_found': len(security_issues),
            'security_issues': security_issues,
            'recommendations': recommendations,
            'security_score': max(0, 100 - len(security_issues) * 20)
        }

    def _perform_format_conversion(self, sql_content: str, target_format: str) -> Dict[str, Any]:
        """Perform database format conversion."""
        try:
            # Detect source format (simplified)
            source_format = DatabaseType.MYSQL  # Default assumption
            target_db_type = DatabaseType(target_format.lower())

            conversion_result = self.format_converter.convert(sql_content, source_format, target_db_type)

            return {
                'success': conversion_result.success,
                'converted_sql': conversion_result.converted_sql,
                'conversion_notes': conversion_result.conversion_notes,
                'warnings': conversion_result.warnings,
                'errors': conversion_result.errors
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'converted_sql': '',
                'conversion_notes': [],
                'warnings': [],
                'errors': [str(e)]
            }

    def _generate_comprehensive_outputs(self, file_path: str, output_dir: Path,
                                       options: ProcessingOptions, output_config: Dict[str, Any],
                                       results: Dict[str, Any]):
        """Generate comprehensive output files and reports."""
        base_name = Path(file_path).stem

        # Create conclusions_arc directory if requested
        if options.create_conclusions_arc:
            conclusions_dir = output_dir / f"{base_name}_conclusions_arc"
            conclusions_dir.mkdir(exist_ok=True)
            self._create_conclusions_archive(conclusions_dir, results)

        # Generate corrected SQL file
        if options.keep_original_format and results.get('correction_result'):
            corrected_file = output_dir / f"{base_name}_corrected.sql"
            self._generate_corrected_sql_file(corrected_file, results, options)

        # Generate converted SQL file
        if options.convert_to_database_format and results.get('conversion_result'):
            converted_file = output_dir / f"{base_name}_converted_{options.convert_to_database_format}.sql"
            self._generate_converted_sql_file(converted_file, results['conversion_result'])

        # Generate reports in requested formats
        for report_format in output_config['report_formats']:
            if report_format == "HTML":
                self._generate_html_report(output_dir / f"{base_name}_report.html", results)
            elif report_format == "Markdown":
                self._generate_markdown_report(output_dir / f"{base_name}_report.md", results)
            elif report_format == "JSON":
                self._generate_json_report(output_dir / f"{base_name}_report.json", results)
            elif report_format == "PDF":
                self._generate_pdf_report(output_dir / f"{base_name}_report.pdf", results)
            elif report_format == "Excel":
                self._generate_excel_report(output_dir / f"{base_name}_report.xlsx", results)

    def _create_conclusions_archive(self, conclusions_dir: Path, results: Dict[str, Any]):
        """Create comprehensive conclusions archive."""
        # Summary file
        summary_file = conclusions_dir / "analysis_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# SQL Analysis Summary\n\n")

            if results.get('domain_result'):
                domain = results['domain_result']
                f.write(f"## Domain Analysis\n")
                f.write(f"**Primary Domain:** {domain['primary_domain']}\n")
                f.write(f"**Confidence:** {domain['confidence_score']:.1%}\n\n")

                if domain.get('suggestions'):
                    f.write("### Recommendations\n")
                    for suggestion in domain['suggestions']:
                        f.write(f"- {suggestion}\n")
                    f.write("\n")

            if results.get('errors'):
                f.write(f"## Error Analysis\n")
                f.write(f"**Total Errors:** {len(results['errors'])}\n")
                critical_errors = sum(1 for e in results['errors'] if e.severity.value == "CRITICAL")
                f.write(f"**Critical Errors:** {critical_errors}\n\n")

            if results.get('performance_result'):
                perf = results['performance_result']
                f.write(f"## Performance Analysis\n")
                f.write(f"**Performance Score:** {perf['overall_score']}/100\n")
                f.write(f"**Issues Found:** {perf['issues_found']}\n\n")

            if results.get('security_result'):
                sec = results['security_result']
                f.write(f"## Security Analysis\n")
                f.write(f"**Security Score:** {sec['security_score']}/100\n")
                f.write(f"**Issues Found:** {sec['issues_found']}\n\n")

        # Detailed recommendations
        recommendations_file = conclusions_dir / "recommendations.md"
        with open(recommendations_file, 'w', encoding='utf-8') as f:
            f.write("# Detailed Recommendations\n\n")

            # Collect all recommendations
            all_recommendations = []

            if results.get('domain_result', {}).get('suggestions'):
                all_recommendations.extend([
                    f"**Domain:** {rec}" for rec in results['domain_result']['suggestions']
                ])

            if results.get('performance_result', {}).get('recommendations'):
                all_recommendations.extend([
                    f"**Performance:** {rec}" for rec in results['performance_result']['recommendations']
                ])

            if results.get('security_result', {}).get('recommendations'):
                all_recommendations.extend([
                    f"**Security:** {rec}" for rec in results['security_result']['recommendations']
                ])

            for i, rec in enumerate(all_recommendations, 1):
                f.write(f"{i}. {rec}\n")

        # Compliance requirements
        if results.get('domain_result', {}).get('compliance_requirements'):
            compliance_file = conclusions_dir / "compliance_requirements.md"
            with open(compliance_file, 'w', encoding='utf-8') as f:
                f.write("# Compliance Requirements\n\n")
                for req in results['domain_result']['compliance_requirements']:
                    f.write(f"- {req}\n")

        # Industry standards
        if results.get('domain_result', {}).get('industry_standards'):
            standards_file = conclusions_dir / "industry_standards.md"
            with open(standards_file, 'w', encoding='utf-8') as f:
                f.write("# Industry Standards\n\n")
                for standard in results['domain_result']['industry_standards']:
                    f.write(f"- {standard}\n")

    def _generate_corrected_sql_file(self, output_file: Path, results: Dict[str, Any],
                                    options: ProcessingOptions):
        """Generate corrected SQL file with comments."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- SQL Analyzer - Corrected SQL File\n")
            f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- \n")

            if results.get('correction_result'):
                correction_result = results['correction_result']

                if correction_result.corrections_applied:
                    f.write("-- AUTOMATIC CORRECTIONS APPLIED:\n")
                    for correction in correction_result.corrections_applied:
                        f.write(f"-- ✓ {correction}\n")
                    f.write("-- \n")

                if options.add_detailed_comments and results.get('errors'):
                    f.write("-- ISSUES FOUND AND ADDRESSED:\n")
                    for error in results['errors'][:10]:  # Limit to first 10
                        f.write(f"-- Line {error.line_number}: {error.message}\n")
                    f.write("-- \n")

                f.write("\n")
                f.write(correction_result.corrected_sql)
            else:
                f.write("-- No corrections were applied\n")

    def _generate_converted_sql_file(self, output_file: Path, conversion_result: Dict[str, Any]):
        """Generate converted SQL file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- SQL Analyzer - Database Format Conversion\n")
            f.write(f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- \n")

            if conversion_result.get('conversion_notes'):
                f.write("-- CONVERSION NOTES:\n")
                for note in conversion_result['conversion_notes']:
                    f.write(f"-- • {note}\n")
                f.write("-- \n")

            if conversion_result.get('warnings'):
                f.write("-- WARNINGS:\n")
                for warning in conversion_result['warnings']:
                    f.write(f"-- ⚠ {warning}\n")
                f.write("-- \n")

            f.write("\n")
            f.write(conversion_result.get('converted_sql', ''))

    def _generate_html_report(self, output_file: Path, results: Dict[str, Any]):
        """Generate comprehensive HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .success {{ color: #388e3c; }}
        .info {{ color: #1976d2; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .score {{ font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SQL Analysis Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""

        # Add domain analysis section
        if results.get('domain_result'):
            domain = results['domain_result']
            html_content += f"""
    <div class="section">
        <h2>Domain Analysis</h2>
        <p><strong>Primary Domain:</strong> {domain['primary_domain']}</p>
        <p><strong>Confidence:</strong> <span class="score">{domain['confidence_score']:.1%}</span></p>

        {self._format_html_list('Recommendations', domain.get('suggestions', []))}
        {self._format_html_list('Compliance Requirements', domain.get('compliance_requirements', []))}
        {self._format_html_list('Industry Standards', domain.get('industry_standards', []))}
    </div>
"""

        # Add error analysis section
        if results.get('errors'):
            errors = results['errors']
            html_content += f"""
    <div class="section">
        <h2>Error Analysis</h2>
        <p><strong>Total Errors:</strong> {len(errors)}</p>

        <table>
            <tr><th>Line</th><th>Severity</th><th>Category</th><th>Message</th></tr>
"""
            for error in errors[:20]:  # Limit to first 20 errors
                severity_class = error.severity.value.lower()
                html_content += f"""
            <tr>
                <td>{error.line_number}</td>
                <td class="{severity_class}">{error.severity.value}</td>
                <td>{error.category.value}</td>
                <td>{error.message}</td>
            </tr>
"""
            html_content += """
        </table>
    </div>
"""

        # Add performance analysis section
        if results.get('performance_result'):
            perf = results['performance_result']
            html_content += f"""
    <div class="section">
        <h2>Performance Analysis</h2>
        <p><strong>Performance Score:</strong> <span class="score">{perf['overall_score']}/100</span></p>
        <p><strong>Issues Found:</strong> {perf['issues_found']}</p>

        {self._format_html_list('Recommendations', perf.get('recommendations', []))}
    </div>
"""

        # Add security analysis section
        if results.get('security_result'):
            sec = results['security_result']
            html_content += f"""
    <div class="section">
        <h2>Security Analysis</h2>
        <p><strong>Security Score:</strong> <span class="score">{sec['security_score']}/100</span></p>
        <p><strong>Issues Found:</strong> {sec['issues_found']}</p>

        {self._format_html_list('Recommendations', sec.get('recommendations', []))}
    </div>
"""

        html_content += """
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _format_html_list(self, title: str, items: List[str]) -> str:
        """Format a list for HTML output."""
        if not items:
            return ""

        html = f"<h3>{title}</h3><ul>"
        for item in items:
            html += f"<li>{item}</li>"
        html += "</ul>"
        return html

    def _generate_markdown_report(self, output_file: Path, results: Dict[str, Any]):
        """Generate Markdown report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# SQL Analysis Report\n\n")
            f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Domain analysis
            if results.get('domain_result'):
                domain = results['domain_result']
                f.write("## Domain Analysis\n\n")
                f.write(f"**Primary Domain:** {domain['primary_domain']}\n")
                f.write(f"**Confidence:** {domain['confidence_score']:.1%}\n\n")

                if domain.get('suggestions'):
                    f.write("### Recommendations\n\n")
                    for suggestion in domain['suggestions']:
                        f.write(f"- {suggestion}\n")
                    f.write("\n")

            # Error analysis
            if results.get('errors'):
                errors = results['errors']
                f.write("## Error Analysis\n\n")
                f.write(f"**Total Errors:** {len(errors)}\n\n")

                if errors:
                    f.write("### Error Details\n\n")
                    f.write("| Line | Severity | Category | Message |\n")
                    f.write("|------|----------|----------|----------|\n")
                    for error in errors[:20]:
                        f.write(f"| {error.line_number} | {error.severity.value} | {error.category.value} | {error.message} |\n")
                    f.write("\n")

            # Performance analysis
            if results.get('performance_result'):
                perf = results['performance_result']
                f.write("## Performance Analysis\n\n")
                f.write(f"**Performance Score:** {perf['overall_score']}/100\n")
                f.write(f"**Issues Found:** {perf['issues_found']}\n\n")

                if perf.get('recommendations'):
                    f.write("### Performance Recommendations\n\n")
                    for rec in perf['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")

            # Security analysis
            if results.get('security_result'):
                sec = results['security_result']
                f.write("## Security Analysis\n\n")
                f.write(f"**Security Score:** {sec['security_score']}/100\n")
                f.write(f"**Issues Found:** {sec['issues_found']}\n\n")

                if sec.get('recommendations'):
                    f.write("### Security Recommendations\n\n")
                    for rec in sec['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")

    def _generate_json_report(self, output_file: Path, results: Dict[str, Any]):
        """Generate JSON report."""
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'analysis_results': {}
        }

        # Add all results to the report
        for key, value in results.items():
            if key == 'parsed_statements':
                # Convert parsed statements to serializable format
                report_data['analysis_results']['parsed_statements'] = [
                    {
                        'statement_type': stmt.statement_type.value,
                        'line_number': stmt.line_number,
                        'is_valid': stmt.is_valid,
                        'table_name': stmt.table_name,
                        'referenced_tables': stmt.referenced_tables
                    }
                    for stmt in value
                ]
            elif key == 'errors':
                # Convert errors to serializable format
                report_data['analysis_results']['errors'] = [
                    {
                        'line_number': error.line_number,
                        'severity': error.severity.value,
                        'category': error.category.value,
                        'message': error.message,
                        'suggestion': error.suggestion
                    }
                    for error in value
                ]
            else:
                report_data['analysis_results'][key] = value

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)

    def _generate_pdf_report(self, output_file: Path, results: Dict[str, Any]):
        """Generate PDF report (placeholder - would require reportlab)."""
        # For now, create a text file with PDF extension
        # In a real implementation, you would use reportlab or similar
        with open(output_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
            f.write("SQL Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if results.get('domain_result'):
                domain = results['domain_result']
                f.write("DOMAIN ANALYSIS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Primary Domain: {domain['primary_domain']}\n")
                f.write(f"Confidence: {domain['confidence_score']:.1%}\n\n")

            if results.get('errors'):
                f.write(f"ERROR ANALYSIS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Errors: {len(results['errors'])}\n\n")

        self.console.print(f"[yellow]Note: PDF generation requires additional libraries. Text report created instead.[/yellow]")

    def _generate_excel_report(self, output_file: Path, results: Dict[str, Any]):
        """Generate Excel report (placeholder - would require openpyxl)."""
        # For now, create a CSV file
        import csv

        with open(output_file.with_suffix('.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Analysis Type', 'Metric', 'Value'])

            # Domain analysis
            if results.get('domain_result'):
                domain = results['domain_result']
                writer.writerow(['Domain', 'Primary Domain', domain['primary_domain']])
                writer.writerow(['Domain', 'Confidence', f"{domain['confidence_score']:.1%}"])

            # Error analysis
            if results.get('errors'):
                writer.writerow(['Errors', 'Total Count', len(results['errors'])])
                critical_count = sum(1 for e in results['errors'] if e.severity.value == "CRITICAL")
                writer.writerow(['Errors', 'Critical Count', critical_count])

            # Performance analysis
            if results.get('performance_result'):
                perf = results['performance_result']
                writer.writerow(['Performance', 'Score', f"{perf['overall_score']}/100"])
                writer.writerow(['Performance', 'Issues Found', perf['issues_found']])

            # Security analysis
            if results.get('security_result'):
                sec = results['security_result']
                writer.writerow(['Security', 'Score', f"{sec['security_score']}/100"])
                writer.writerow(['Security', 'Issues Found', sec['issues_found']])

        self.console.print(f"[yellow]Note: Excel generation requires additional libraries. CSV report created instead.[/yellow]")

    def _display_results_summary(self, file_path: str, output_dir: Path, processing_time: float):
        """Display comprehensive results summary."""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]✅ Processing Complete![/bold green]")
        self.console.print("="*60)

        # Create summary table
        summary_table = Table(title="Processing Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value")

        summary_table.add_row("File Processed", Path(file_path).name)
        summary_table.add_row("Processing Time", f"{processing_time:.2f} seconds")
        summary_table.add_row("Output Directory", str(output_dir))

        # Count output files
        output_files = list(output_dir.glob("*"))
        summary_table.add_row("Files Generated", str(len(output_files)))

        self.console.print(summary_table)

        # Show output files
        if output_files:
            self.console.print("\n[bold]Generated Files:[/bold]")
            for file in output_files:
                file_size = file.stat().st_size
                self.console.print(f"  📄 {file.name} ({file_size:,} bytes)")

        # Ask to open output directory
        if Confirm.ask("\n[bold]Open output directory?[/bold]"):
            self._open_output_directory(output_dir)

        # Ask to view specific reports
        if Confirm.ask("View analysis summary?"):
            self._display_quick_summary()

    def _open_output_directory(self, output_dir: Path):
        """Open output directory in file explorer."""
        import subprocess
        import platform

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(output_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(output_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_dir)])
        except Exception as e:
            self.console.print(f"[yellow]Could not open directory: {e}[/yellow]")
            self.console.print(f"Output directory: {output_dir}")

    def _display_quick_summary(self):
        """Display quick analysis summary."""
        if not self.current_session or not self.current_session.results:
            self.console.print("[yellow]No analysis results available.[/yellow]")
            return

        results = self.current_session.results

        # Create summary panel
        summary_content = ""

        if 'domain_analysis' in results:
            domain = results['domain_analysis']
            summary_content += f"🎯 **Domain:** {domain.get('primary_domain', 'Unknown')}\n"
            summary_content += f"📊 **Confidence:** {domain.get('confidence_score', 0):.1%}\n\n"

        if 'error_count' in results:
            summary_content += f"🐛 **Errors Found:** {results['error_count']}\n"
            if 'critical_errors' in results:
                summary_content += f"🚨 **Critical:** {results['critical_errors']}\n\n"

        if 'performance_score' in results:
            summary_content += f"⚡ **Performance Score:** {results['performance_score']}/100\n\n"

        if 'security_score' in results:
            summary_content += f"🔒 **Security Score:** {results['security_score']}/100\n\n"

        if summary_content:
            self.console.print(Panel(
                Markdown(summary_content),
                title="Analysis Summary",
                border_style="green"
            ))

    # Helper methods for user preferences and session management
    def _load_user_preferences(self) -> UserPreferences:
        """Load user preferences from config file."""
        preferences = UserPreferences()
        config_file = Path.home() / ".sql_analyzer" / "preferences.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(preferences, key):
                            setattr(preferences, key, value)
            except Exception as e:
                self.console.print(f"[yellow]Could not load preferences: {e}[/yellow]")

        return preferences

    def _save_user_preferences(self):
        """Save user preferences to config file."""
        config_dir = Path.home() / ".sql_analyzer"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "preferences.json"

        try:
            with open(config_file, 'w') as f:
                json.dump(self.preferences.__dict__, f, indent=2)
        except Exception as e:
            self.console.print(f"[yellow]Could not save preferences: {e}[/yellow]")

    def _load_session_history(self):
        """Load session history from disk."""
        try:
            for session_file in self.sessions_dir.glob("session_*.json"):
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    session = ProcessingSession(
                        session_id=data['session_id'],
                        created_at=datetime.fromisoformat(data['created_at']),
                        files_processed=data.get('files_processed', []),
                        results=data.get('results', {}),
                        configuration=data.get('configuration', {}),
                        statistics=data.get('statistics', {}),
                        notes=data.get('notes', []),
                        tags=data.get('tags', [])
                    )
                    self.session_history.append(session)

            # Sort by creation time
            self.session_history.sort(key=lambda s: s.created_at)

        except Exception as e:
            if self.verbose:
                self.console.print(f"[dim]Could not load session history: {e}[/dim]")

    def _save_current_session(self):
        """Save current session to disk."""
        if not self.current_session:
            return

        try:
            session_file = self.sessions_dir / f"{self.current_session.session_id}.json"
            session_data = {
                'session_id': self.current_session.session_id,
                'created_at': self.current_session.created_at.isoformat(),
                'files_processed': self.current_session.files_processed,
                'results': self.current_session.results,
                'configuration': self.current_session.configuration,
                'statistics': self.current_session.statistics,
                'notes': self.current_session.notes,
                'tags': self.current_session.tags
            }

            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)

        except Exception as e:
            self.console.print(f"[yellow]Could not save session: {e}[/yellow]")

    def _handle_exit(self):
        """Handle application exit."""
        self.console.print("\n[bold blue]Thank you for using SQL Analyzer![/bold blue]")

        # Save current session if exists
        if self.current_session and self.preferences.auto_save_sessions:
            self._save_current_session()
            self.console.print("[dim]Session saved automatically.[/dim]")

        # Save preferences
        self._save_user_preferences()

        # Display usage statistics
        if self.session_history:
            total_files = sum(len(s.files_processed) for s in self.session_history)
            self.console.print(f"[dim]Total files processed in all sessions: {total_files}[/dim]")

        self.console.print("[dim]Goodbye![/dim]")


class CLIInterface:
    """
    Command Line Interface for SQL Analyzer.
    
    Provides interactive and command-line modes for:
    - File selection and processing
    - SQL analysis and error detection
    - Schema analysis and optimization
    - Format conversion between database systems
    - Results visualization and export
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the CLI interface."""
        self.console = Console()
        self.verbose = verbose
        
        # Initialize core components
        self.file_processor = FileProcessor()
        self.sql_parser = SQLParser()
        self.error_detector = ErrorDetector()
        self.schema_analyzer = SchemaAnalyzer()
        self.format_converter = FormatConverter()
        
        # Display welcome message
        self._display_welcome()
    
    def _display_welcome(self):
        """Display welcome message and tool information."""
        welcome_text = """
[bold blue]SQL Analyzer and Corrector[/bold blue]
[dim]Comprehensive SQL file analysis, error detection, and database format conversion[/dim]

Features:
• Process SQL files up to 10M+ lines
• Support 50+ file formats
• Intelligent error detection and correction
• Database schema analysis and optimization
• Multi-database format conversion
• Data integrity preservation
        """
        
        self.console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    def run_interactive(self):
        """Run the interactive CLI mode."""
        while True:
            try:
                choice = self._show_main_menu()
                
                if choice == "1":
                    self._analyze_file_interactive()
                elif choice == "2":
                    self._convert_format_interactive()
                elif choice == "3":
                    self._batch_process_interactive()
                elif choice == "4":
                    self._view_history()
                elif choice == "5":
                    self._show_help()
                elif choice == "6":
                    self.console.print("[green]Thank you for using SQL Analyzer![/green]")
                    break
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled.[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                if self.verbose:
                    import traceback
                    self.console.print(traceback.format_exc())
    
    def _show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        self.console.print("\n[bold]Main Menu[/bold]")
        
        menu_table = Table(show_header=False, box=None)
        menu_table.add_column("Option", style="cyan")
        menu_table.add_column("Description")
        
        menu_table.add_row("1", "Analyze SQL File")
        menu_table.add_row("2", "Convert Database Format")
        menu_table.add_row("3", "Batch Process Files")
        menu_table.add_row("4", "View Processing History")
        menu_table.add_row("5", "Help & Documentation")
        menu_table.add_row("6", "Exit")
        
        self.console.print(menu_table)
        
        return Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6"])
    
    def _analyze_file_interactive(self):
        """Interactive file analysis workflow."""
        self.console.print("\n[bold]SQL File Analysis[/bold]")
        
        # Get file path
        file_path = self._get_file_path()
        if not file_path:
            return
        
        # Get analysis options
        options = self._get_analysis_options()
        
        # Process the file
        self._process_single_file(file_path, options)
    
    def _get_file_path(self) -> Optional[str]:
        """Get file path from user input."""
        while True:
            file_path = Prompt.ask("Enter the path to your SQL file")
            
            if not file_path:
                return None
            
            path = Path(file_path)
            if path.exists():
                return str(path.absolute())
            else:
                self.console.print(f"[red]File not found: {file_path}[/red]")
                if not Confirm.ask("Try again?"):
                    return None
    
    def _get_analysis_options(self) -> Dict[str, bool]:
        """Get analysis options from user."""
        self.console.print("\n[bold]Analysis Options[/bold]")
        
        options = {
            'syntax_check': Confirm.ask("Perform syntax analysis?", default=True),
            'error_detection': Confirm.ask("Detect and suggest corrections?", default=True),
            'schema_analysis': Confirm.ask("Analyze database schema?", default=True),
            'performance_check': Confirm.ask("Check for performance issues?", default=True),
            'generate_report': Confirm.ask("Generate detailed report?", default=True)
        }
        
        return options
    
    def _process_single_file(self, file_path: str, options: Dict[str, bool]):
        """Process a single SQL file with given options."""
        self.console.print(f"\n[bold]Processing: {file_path}[/bold]")
        
        try:
            # Get file information
            file_info = self.file_processor.get_file_info(file_path)
            self._display_file_info(file_info)
            
            if not file_info.supported:
                self.console.print(f"[red]Unsupported file format: {file_info.format}[/red]")
                return
            
            # Process file content
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                
                # Read file
                read_task = progress.add_task("Reading file...", total=100)
                sql_lines = list(self.file_processor.process_file(file_path))
                progress.update(read_task, completed=100)
                
                # Parse SQL
                if options.get('syntax_check', True):
                    parse_task = progress.add_task("Parsing SQL...", total=100)
                    parsed_statements = self.sql_parser.parse_sql_file(sql_lines)
                    progress.update(parse_task, completed=100)
                else:
                    parsed_statements = []
                
                # Error detection
                if options.get('error_detection', True):
                    error_task = progress.add_task("Detecting errors...", total=100)
                    sql_content = '\n'.join(sql_lines)
                    errors = self.error_detector.analyze_sql(sql_content)
                    correction_result = self.error_detector.correct_sql(sql_content)
                    progress.update(error_task, completed=100)
                else:
                    errors = []
                    correction_result = None
                
                # Schema analysis
                if options.get('schema_analysis', True):
                    schema_task = progress.add_task("Analyzing schema...", total=100)
                    schema_result = self.schema_analyzer.analyze_schema(self.sql_parser.tables)
                    progress.update(schema_task, completed=100)
                else:
                    schema_result = None
            
            # Display results
            self._display_analysis_results(
                file_info, parsed_statements, errors, correction_result, schema_result, options
            )
            
            # Ask about saving results
            if options.get('generate_report', True):
                self._save_results_interactive(file_path, {
                    'file_info': file_info,
                    'parsed_statements': parsed_statements,
                    'errors': errors,
                    'correction_result': correction_result,
                    'schema_result': schema_result
                })
                
        except Exception as e:
            self.console.print(f"[red]Error processing file: {e}[/red]")
            if self.verbose:
                import traceback
                self.console.print(traceback.format_exc())
    
    def _display_file_info(self, file_info: FileInfo):
        """Display file information."""
        info_table = Table(title="File Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value")
        
        info_table.add_row("Path", file_info.path)
        info_table.add_row("Size", f"{file_info.size:,} bytes ({file_info.size / (1024*1024):.2f} MB)")
        info_table.add_row("Encoding", file_info.encoding)
        info_table.add_row("Format", file_info.format)
        info_table.add_row("Lines", f"{file_info.line_count:,}")
        info_table.add_row("Estimated Processing Time", f"{file_info.estimated_processing_time:.2f} seconds")
        info_table.add_row("Supported", "✓" if file_info.supported else "✗")
        
        self.console.print(info_table)
    
    def _display_analysis_results(self, file_info: FileInfo, parsed_statements: List,
                                 errors: List, correction_result, schema_result, options: Dict[str, bool]):
        """Display comprehensive analysis results."""
        
        # Summary
        summary_table = Table(title="Analysis Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value")
        
        summary_table.add_row("Total Statements", str(len(parsed_statements)))
        summary_table.add_row("Errors Found", str(len(errors)))
        summary_table.add_row("Critical Errors", str(sum(1 for e in errors if e.severity.value == "CRITICAL")))
        
        if schema_result:
            summary_table.add_row("Tables Analyzed", str(schema_result.tables_analyzed))
            summary_table.add_row("Schema Health Score", f"{schema_result.overall_health_score:.1f}/100")
        
        self.console.print(summary_table)
        
        # Error details
        if errors and options.get('error_detection', True):
            self._display_errors(errors)
        
        # Correction suggestions
        if correction_result and correction_result.corrections_applied:
            self._display_corrections(correction_result)
        
        # Schema analysis
        if schema_result and options.get('schema_analysis', True):
            self._display_schema_analysis(schema_result)
    
    def _display_errors(self, errors: List):
        """Display error analysis results."""
        if not errors:
            self.console.print("[green]No errors detected![/green]")
            return
        
        error_table = Table(title="Detected Errors")
        error_table.add_column("Line", style="cyan")
        error_table.add_column("Severity", style="red")
        error_table.add_column("Category")
        error_table.add_column("Message")
        
        for error in errors[:10]:  # Show first 10 errors
            severity_color = {
                "CRITICAL": "red",
                "ERROR": "red",
                "WARNING": "yellow",
                "INFO": "blue",
                "STYLE": "dim"
            }.get(error.severity.value, "white")
            
            error_table.add_row(
                str(error.line_number),
                f"[{severity_color}]{error.severity.value}[/{severity_color}]",
                error.category.value,
                error.message
            )
        
        self.console.print(error_table)
        
        if len(errors) > 10:
            self.console.print(f"[dim]... and {len(errors) - 10} more errors[/dim]")
    
    def _display_corrections(self, correction_result):
        """Display correction suggestions."""
        if correction_result.corrections_applied:
            self.console.print("\n[bold green]Automatic Corrections Applied:[/bold green]")
            for correction in correction_result.corrections_applied:
                self.console.print(f"  ✓ {correction}")
        
        if correction_result.suggestions:
            self.console.print("\n[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in correction_result.suggestions[:5]:
                self.console.print(f"  • {suggestion}")
    
    def _display_schema_analysis(self, schema_result):
        """Display schema analysis results."""
        # Health scores
        health_table = Table(title="Schema Health Scores")
        health_table.add_column("Metric", style="cyan")
        health_table.add_column("Score", style="green")
        
        health_table.add_row("Overall Health", f"{schema_result.overall_health_score:.1f}/100")
        health_table.add_row("Data Integrity", f"{schema_result.data_integrity_score:.1f}/100")
        health_table.add_row("Normalization", f"{schema_result.normalization_score:.1f}/100")
        health_table.add_row("Performance", f"{schema_result.performance_score:.1f}/100")
        
        self.console.print(health_table)
        
        # Missing tables
        if schema_result.missing_tables:
            self.console.print(f"\n[bold yellow]Suggested Missing Tables ({len(schema_result.missing_tables)}):[/bold yellow]")
            for missing in schema_result.missing_tables[:3]:
                self.console.print(f"  • {missing.suggested_name}: {missing.purpose}")
        
        # Optimizations
        if schema_result.optimizations:
            self.console.print(f"\n[bold blue]Optimization Opportunities ({len(schema_result.optimizations)}):[/bold blue]")
            for opt in schema_result.optimizations[:3]:
                self.console.print(f"  • Priority {opt.priority}: {opt.description}")
    
    def _convert_format_interactive(self):
        """Interactive database format conversion."""
        self.console.print("\n[bold]Database Format Conversion[/bold]")
        
        # Get source file
        file_path = self._get_file_path()
        if not file_path:
            return
        
        # Get source and target formats
        source_format = self._get_database_format("source")
        target_format = self._get_database_format("target")
        
        if source_format == target_format:
            self.console.print("[yellow]Source and target formats are the same.[/yellow]")
            return
        
        # Perform conversion
        self._perform_conversion(file_path, source_format, target_format)
    
    def _get_database_format(self, format_type: str) -> DatabaseType:
        """Get database format from user."""
        formats = {
            "1": DatabaseType.MYSQL,
            "2": DatabaseType.POSTGRESQL,
            "3": DatabaseType.SQLITE,
            "4": DatabaseType.SQLSERVER,
            "5": DatabaseType.ORACLE,
            "6": DatabaseType.JSON
        }
        
        format_table = Table(show_header=False, box=None)
        format_table.add_column("Option", style="cyan")
        format_table.add_column("Format")
        
        for key, db_type in formats.items():
            format_table.add_row(key, db_type.value.upper())
        
        self.console.print(f"\nSelect {format_type} format:")
        self.console.print(format_table)
        
        choice = Prompt.ask("Choose format", choices=list(formats.keys()))
        return formats[choice]

    def _perform_conversion(self, file_path: str, source_format: DatabaseType, target_format: DatabaseType):
        """Perform database format conversion."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Perform conversion
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Converting format...", total=None)
                result = self.format_converter.convert(sql_content, source_format, target_format)
                progress.update(task, completed=100)

            # Display results
            if result.success:
                self.console.print("[green]Conversion completed successfully![/green]")

                if result.conversion_notes:
                    self.console.print("\n[bold]Conversion Notes:[/bold]")
                    for note in result.conversion_notes:
                        self.console.print(f"  • {note}")

                if result.warnings:
                    self.console.print("\n[bold yellow]Warnings:[/bold yellow]")
                    for warning in result.warnings:
                        self.console.print(f"  ⚠ {warning}")

                # Ask to save converted file
                if Confirm.ask("Save converted file?"):
                    self._save_converted_file(file_path, result, target_format)
            else:
                self.console.print("[red]Conversion failed![/red]")
                for error in result.errors:
                    self.console.print(f"  ✗ {error}")

        except Exception as e:
            self.console.print(f"[red]Conversion error: {e}[/red]")

    def _save_converted_file(self, original_path: str, result, target_format: DatabaseType):
        """Save converted file."""
        original_path_obj = Path(original_path)

        # Generate output filename
        if target_format == DatabaseType.JSON:
            output_path = original_path_obj.with_suffix('.json')
        else:
            output_path = original_path_obj.with_name(
                f"{original_path_obj.stem}_{target_format.value}{original_path_obj.suffix}"
            )

        # Ask for custom path
        custom_path = Prompt.ask(f"Output file path", default=str(output_path))
        output_path = Path(custom_path)

        try:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write converted content
            with open(output_path, 'w', encoding='utf-8') as f:
                if target_format == DatabaseType.JSON and result.converted_json:
                    import json
                    json.dump(result.converted_json, f, indent=2)
                else:
                    f.write(result.converted_sql)

            self.console.print(f"[green]File saved: {output_path}[/green]")

        except Exception as e:
            self.console.print(f"[red]Error saving file: {e}[/red]")

    def _batch_process_interactive(self):
        """Interactive batch processing."""
        self.console.print("\n[bold]Batch File Processing[/bold]")

        # Get directory path
        dir_path = Prompt.ask("Enter directory path containing SQL files")

        if not Path(dir_path).exists():
            self.console.print(f"[red]Directory not found: {dir_path}[/red]")
            return

        # Find SQL files
        sql_files = self._find_sql_files(dir_path)

        if not sql_files:
            self.console.print("[yellow]No SQL files found in directory.[/yellow]")
            return

        self.console.print(f"Found {len(sql_files)} SQL files")

        # Get processing options
        options = self._get_analysis_options()

        # Process files
        self._process_batch_files(sql_files, options)

    def _find_sql_files(self, directory: str) -> List[str]:
        """Find SQL files in directory."""
        sql_extensions = {'.sql', '.ddl', '.dml', '.mysql', '.pgsql'}
        sql_files = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in sql_extensions:
                    sql_files.append(os.path.join(root, file))

        return sql_files

    def _process_batch_files(self, file_paths: List[str], options: Dict[str, bool]):
        """Process multiple files in batch."""
        results = []

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:

            task = progress.add_task("Processing files...", total=len(file_paths))

            for file_path in file_paths:
                try:
                    # Process individual file
                    file_info = self.file_processor.get_file_info(file_path)

                    if file_info.supported:
                        sql_lines = list(self.file_processor.process_file(file_path))

                        if options.get('syntax_check', True):
                            parsed_statements = self.sql_parser.parse_sql_file(sql_lines)
                        else:
                            parsed_statements = []

                        if options.get('error_detection', True):
                            sql_content = '\n'.join(sql_lines)
                            errors = self.error_detector.analyze_sql(sql_content)
                        else:
                            errors = []

                        results.append({
                            'file_path': file_path,
                            'file_info': file_info,
                            'statements': len(parsed_statements),
                            'errors': len(errors),
                            'critical_errors': sum(1 for e in errors if e.severity.value == "CRITICAL")
                        })
                    else:
                        results.append({
                            'file_path': file_path,
                            'file_info': file_info,
                            'statements': 0,
                            'errors': 0,
                            'critical_errors': 0
                        })

                except Exception as e:
                    results.append({
                        'file_path': file_path,
                        'error': str(e),
                        'statements': 0,
                        'errors': 0,
                        'critical_errors': 0
                    })

                progress.advance(task)

        # Display batch results
        self._display_batch_results(results)

    def _display_batch_results(self, results: List[Dict]):
        """Display batch processing results."""
        results_table = Table(title="Batch Processing Results")
        results_table.add_column("File", style="cyan")
        results_table.add_column("Status")
        results_table.add_column("Statements", justify="right")
        results_table.add_column("Errors", justify="right")
        results_table.add_column("Critical", justify="right")

        total_files = len(results)
        successful_files = 0
        total_statements = 0
        total_errors = 0
        total_critical = 0

        for result in results:
            file_name = Path(result['file_path']).name

            if 'error' in result:
                status = "[red]Error[/red]"
            elif hasattr(result.get('file_info'), 'supported') and not result['file_info'].supported:
                status = "[yellow]Unsupported[/yellow]"
            else:
                status = "[green]Success[/green]"
                successful_files += 1
                total_statements += result['statements']
                total_errors += result['errors']
                total_critical += result['critical_errors']

            results_table.add_row(
                file_name,
                status,
                str(result['statements']),
                str(result['errors']),
                str(result['critical_errors'])
            )

        self.console.print(results_table)

        # Summary
        summary_text = f"""
[bold]Batch Processing Summary[/bold]
Total Files: {total_files}
Successful: {successful_files}
Total Statements: {total_statements:,}
Total Errors: {total_errors:,}
Critical Errors: {total_critical:,}
        """

        self.console.print(Panel(summary_text, title="Summary", border_style="green"))

    def _view_history(self):
        """View processing history."""
        self.console.print("\n[bold]Processing History[/bold]")

        # File processing history
        if self.file_processor.processed_files:
            stats = self.file_processor.get_processing_stats()

            history_table = Table(title="File Processing History")
            history_table.add_column("Metric", style="cyan")
            history_table.add_column("Value")

            history_table.add_row("Total Files Processed", str(stats['total_files']))
            history_table.add_row("Total Size", f"{stats['total_size_mb']} MB")
            history_table.add_row("Total Lines", f"{stats['total_lines']:,}")
            history_table.add_row("Average File Size", f"{stats['average_file_size']:,.0f} bytes")

            self.console.print(history_table)

            # Format distribution
            if stats['formats_processed']:
                format_table = Table(title="Formats Processed")
                format_table.add_column("Format", style="cyan")
                format_table.add_column("Count", justify="right")

                for format_type, count in stats['formats_processed'].items():
                    format_table.add_row(format_type, str(count))

                self.console.print(format_table)
        else:
            self.console.print("[yellow]No processing history available.[/yellow]")

        # Conversion history
        if self.format_converter.conversion_history:
            self.console.print(f"\n[bold]Format Conversions: {len(self.format_converter.conversion_history)}[/bold]")

            for i, conversion in enumerate(self.format_converter.conversion_history[-5:], 1):
                status = "✓" if conversion.success else "✗"
                self.console.print(f"  {i}. {conversion.source_format.value} → {conversion.target_format.value} {status}")

    def _show_help(self):
        """Show help and documentation."""
        help_text = """
[bold blue]SQL Analyzer Help[/bold blue]

[bold]Main Features:[/bold]
• [cyan]File Analysis[/cyan]: Comprehensive SQL file analysis with error detection
• [cyan]Format Conversion[/cyan]: Convert between MySQL, PostgreSQL, SQLite, SQL Server, Oracle, and JSON
• [cyan]Batch Processing[/cyan]: Process multiple files at once
• [cyan]Schema Analysis[/cyan]: Intelligent database schema analysis and optimization

[bold]Supported File Formats:[/bold]
SQL files: .sql, .ddl, .dml, .mysql, .pgsql
Text files: .txt, .text, .log, .dat
Data files: .csv, .json, .yaml, .xml
Documents: .docx, .xlsx, .html
Compressed: .gz, .bz2, .xz, .zip, .tar

[bold]Database Formats:[/bold]
• MySQL
• PostgreSQL
• SQLite
• SQL Server
• Oracle
• JSON

[bold]Command Line Usage:[/bold]
python main.py -f file.sql                    # Analyze file
python main.py -f file.sql -o output/         # Specify output directory
python main.py --convert mysql postgresql     # Convert formats
python main.py --analyze-only                 # Analysis only, no corrections

[bold]Tips:[/bold]
• Use batch processing for multiple files
• Check the processing history to track your work
• Large files (10M+ lines) are processed efficiently in chunks
• All operations preserve data integrity
        """

        self.console.print(Panel(help_text, title="Help & Documentation", border_style="blue"))

    def _save_results_interactive(self, file_path: str, results: Dict[str, Any]):
        """Interactive results saving."""
        if not Confirm.ask("Save analysis results?"):
            return

        # Generate output directory
        output_dir = Path(file_path).parent / "sql_analysis_results"
        output_dir.mkdir(exist_ok=True)

        base_name = Path(file_path).stem

        # Save different types of results
        if Confirm.ask("Save error report?"):
            error_report = self.error_detector.generate_error_report(results.get('errors', []))
            with open(output_dir / f"{base_name}_errors.txt", 'w') as f:
                f.write(error_report)

        if results.get('schema_result') and Confirm.ask("Save schema analysis?"):
            schema_report = self.schema_analyzer.generate_schema_report(results['schema_result'])
            with open(output_dir / f"{base_name}_schema.txt", 'w') as f:
                f.write(schema_report)

        if results.get('correction_result') and Confirm.ask("Save corrected SQL?"):
            with open(output_dir / f"{base_name}_corrected.sql", 'w') as f:
                f.write(results['correction_result'].corrected_sql)

        self.console.print(f"[green]Results saved to: {output_dir}[/green]")

    def process_file(self, file_path: str, output_dir: str = "output",
                    convert_formats: Optional[List[str]] = None,
                    analyze_only: bool = False):
        """Process file via command line interface."""
        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Process the file
            self.console.print(f"Processing: {file_path}")

            # Get file info and process
            file_info = self.file_processor.get_file_info(file_path)

            if not file_info.supported:
                self.console.print(f"[red]Unsupported file format: {file_info.format}[/red]")
                return

            # Read and analyze file
            sql_lines = list(self.file_processor.process_file(file_path))
            parsed_statements = self.sql_parser.parse_sql_file(sql_lines)

            sql_content = '\n'.join(sql_lines)
            errors = self.error_detector.analyze_sql(sql_content)

            if not analyze_only:
                correction_result = self.error_detector.correct_sql(sql_content)
                schema_result = self.schema_analyzer.analyze_schema(self.sql_parser.tables)
            else:
                correction_result = None
                schema_result = None

            # Save results
            base_name = Path(file_path).stem

            # Error report
            error_report = self.error_detector.generate_error_report(errors)
            with open(Path(output_dir) / f"{base_name}_analysis.txt", 'w') as f:
                f.write(error_report)

            if correction_result:
                with open(Path(output_dir) / f"{base_name}_corrected.sql", 'w') as f:
                    f.write(correction_result.corrected_sql)

            if schema_result:
                schema_report = self.schema_analyzer.generate_schema_report(schema_result)
                with open(Path(output_dir) / f"{base_name}_schema.txt", 'w') as f:
                    f.write(schema_report)

            # Format conversion
            if convert_formats and len(convert_formats) == 2:
                source_format = DatabaseType(convert_formats[0].lower())
                target_format = DatabaseType(convert_formats[1].lower())

                conversion_result = self.format_converter.convert(sql_content, source_format, target_format)

                if conversion_result.success:
                    if target_format == DatabaseType.JSON:
                        output_file = Path(output_dir) / f"{base_name}_converted.json"
                        with open(output_file, 'w') as f:
                            import json
                            json.dump(conversion_result.converted_json, f, indent=2)
                    else:
                        output_file = Path(output_dir) / f"{base_name}_converted_{target_format.value}.sql"
                        with open(output_file, 'w') as f:
                            f.write(conversion_result.converted_sql)

                    self.console.print(f"[green]Converted file saved: {output_file}[/green]")

            self.console.print(f"[green]Analysis complete. Results saved to: {output_dir}[/green]")

        except Exception as e:
            self.console.print(f"[red]Error processing file: {e}[/red]")
            raise
