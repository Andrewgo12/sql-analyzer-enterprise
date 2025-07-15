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
    
[bold]Batch Processing Summary[/bold]
Total Files: {total_files}
Successful: {successful_files}
Total Statements: {total_statements:,}
Total Errors: {total_errors:,}
Critical Errors: {total_critical:,}
        """

        self.console.print(Panel(summary_text, title="Summary", border_style="green"))

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
