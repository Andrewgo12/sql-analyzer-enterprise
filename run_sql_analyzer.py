#!/usr/bin/env python3
"""
Analizador SQL Empresarial - Iniciador Optimizado
Inicio automático de alto rendimiento para la aplicación web
"""

import os
import sys
import subprocess
import platform
import webbrowser
import time
from pathlib import Path
import json
import logging

# Configuración optimizada de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class SQLAnalyzerLauncher:
    """Lanzador optimizado del Analizador SQL Empresarial."""

    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.web_app_dir = self.project_dir / "web_app"
        self.python_executable = sys.executable
        self.host = "127.0.0.1"
        self.port = 8000
        self.auto_open_browser = True

        # Configuración optimizada
        self.config = {
            'max_workers': os.cpu_count() or 4,
            'timeout': 300,
            'memory_limit': '2GB',
            'cache_size': '500MB'
        }

        # Detectar sistema operativo
        self.os_type = platform.system().lower()

        print("🚀 Analizador SQL Empresarial - Iniciador Optimizado")
        print("=" * 60)
    
    def run(self):
        """Ejecutar el proceso completo de inicio."""
        try:
            print("📋 Verificando requisitos del sistema...")
            self.check_system_requirements()
            
            print("📦 Verificando e instalando dependencias...")
            self.install_dependencies()
            
            print("📁 Creando estructura de directorios...")
            self.create_directory_structure()
            
            print("⚙️ Configurando aplicación...")
            self.configure_application()
            
            print("🌐 Iniciando servidor web...")
            self.start_web_server()
            
        except KeyboardInterrupt:
            print("\n\n👋 Inicio cancelado por el usuario.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error durante el inicio: {e}")
            logger.error(f"Error: {e}", exc_info=True)
            sys.exit(1)
    
    def check_system_requirements(self):
        """Verificar requisitos del sistema."""
        # Verificar Python
        if sys.version_info < (3, 8):
            raise RuntimeError(f"Python 3.8+ requerido. Versión actual: {sys.version}")
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        
        # Verificar pip
        try:
            subprocess.run([self.python_executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("✅ pip - Disponible")
        except subprocess.CalledProcessError:
            raise RuntimeError("pip no está disponible")
        
        # Verificar memoria disponible
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 2:
                print(f"⚠️ Memoria disponible: {memory_gb:.1f}GB (recomendado: 4GB+)")
            else:
                print(f"✅ Memoria disponible: {memory_gb:.1f}GB")
        except ImportError:
            print("⚠️ No se pudo verificar memoria disponible")
    
    def install_dependencies(self):
        """Instalación optimizada de dependencias."""
        # Dependencias esenciales optimizadas
        essential_deps = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "jinja2>=3.1.2",
            "aiofiles>=23.2.0",
            "sqlparse>=0.4.4",
            "rich>=13.5.2",
            "chardet>=5.2.0"
        ]

        # Dependencias avanzadas
        advanced_deps = [
            "pandas>=2.1.0",
            "openpyxl>=3.1.2",
            "pyyaml>=6.0.1",
            "psutil>=5.9.5"
        ]

        print("📦 Instalando dependencias esenciales...")
        success_count = 0

        # Instalación en lote para mejor rendimiento
        try:
            subprocess.run([
                self.python_executable, '-m', 'pip', 'install', '--upgrade'
            ] + essential_deps, check=True, capture_output=True, text=True)
            success_count += len(essential_deps)
            print(f"✅ {len(essential_deps)} dependencias esenciales instaladas")
        except subprocess.CalledProcessError:
            # Fallback: instalación individual
            for dep in essential_deps:
                if self.install_package(dep, required=True):
                    success_count += 1

        print("📦 Instalando dependencias avanzadas...")
        for dep in advanced_deps:
            if self.install_package(dep, required=False):
                success_count += 1

        print(f"✅ Instalación completada: {success_count} paquetes instalados")
    
    def install_package(self, package, required=True):
        """Instalación optimizada de paquete individual."""
        try:
            result = subprocess.run([
                self.python_executable, '-m', 'pip', 'install',
                '--upgrade', '--no-warn-script-location', package
            ], check=True, capture_output=True, text=True, timeout=120)
            print(f"  ✅ {package}")
            return True
        except subprocess.CalledProcessError as e:
            if required:
                print(f"  ❌ {package} - Error: {e.stderr.strip()}")
                raise RuntimeError(f"No se pudo instalar dependencia requerida: {package}")
            else:
                print(f"  ⚠️ {package} - Opcional, omitido")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {package} - Timeout, omitido")
            return False
    
    def create_directory_structure(self):
        """Crear estructura de directorios necesaria."""
        directories = [
            "web_app/static/css",
            "web_app/static/js",
            "web_app/static/img",
            "web_app/templates",
            "sql_analyzer/core",
            "sql_analyzer/ui",
            "uploads",
            "results",
            "logs",
            "cache"
        ]
        
        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("✅ Estructura de directorios creada")
    
    def configure_application(self):
        """Configurar la aplicación."""
        # Crear archivo de configuración
        config = {
            "app": {
                "name": "Analizador SQL Empresarial",
                "version": "2.0.0",
                "debug": False
            },
            "server": {
                "host": self.host,
                "port": self.port,
                "reload": False
            },
            "upload": {
                "max_file_size": 10 * 1024 * 1024 * 1024,  # 10GB
                "allowed_extensions": [".sql", ".txt", ".text"],
                "upload_dir": "uploads"
            },
            "analysis": {
                "max_workers": min(8, os.cpu_count() or 4),
                "timeout_seconds": 3600,
                "cache_enabled": True
            }
        }
        
        config_file = self.project_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ Configuración de aplicación creada")
    
    def start_web_server(self):
        """Iniciar el servidor web."""
        print(f"🌐 Iniciando servidor en http://{self.host}:{self.port}")
        print("📱 La interfaz web se abrirá automáticamente...")
        print("\n" + "=" * 60)
        print("🎯 INSTRUCCIONES DE USO:")
        print("1. La aplicación se abrirá en tu navegador web")
        print("2. Arrastra un archivo SQL al área de carga")
        print("3. Configura las opciones de análisis")
        print("4. Haz clic en 'Iniciar Análisis'")
        print("5. Descarga los resultados cuando esté completo")
        print("=" * 60)
        print("\n⏳ Iniciando servidor...")
        
        # Cambiar al directorio del proyecto
        os.chdir(self.project_dir)
        
        # Verificar que el archivo del servidor existe
        server_file = self.web_app_dir / "server.py"
        if not server_file.exists():
            raise FileNotFoundError(f"Archivo del servidor no encontrado: {server_file}")
        
        # Programar apertura del navegador
        if self.auto_open_browser:
            import threading
            def open_browser():
                time.sleep(3)  # Esperar a que el servidor inicie
                url = f"http://{self.host}:{self.port}"
                print(f"🌐 Abriendo navegador: {url}")
                webbrowser.open(url)
            
            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()
        
        # Iniciar servidor
        try:
            cmd = [
                self.python_executable, "-m", "uvicorn",
                "web_app.server:app",
                "--host", self.host,
                "--port", str(self.port),
                "--reload"
            ]
            
            print(f"🚀 Ejecutando: {' '.join(cmd)}")
            print("\n" + "🟢" * 20 + " SERVIDOR INICIADO " + "🟢" * 20)
            print(f"📍 URL: http://{self.host}:{self.port}")
            print("🛑 Presiona Ctrl+C para detener el servidor")
            print("🟢" * 60 + "\n")
            
            # Ejecutar servidor
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error iniciando servidor: {e}")
            print("\n🔧 Intentando método alternativo...")
            
            # Método alternativo: ejecutar directamente
            try:
                sys.path.insert(0, str(self.project_dir))
                import uvicorn
                from web_app.server import app
                
                uvicorn.run(
                    app,
                    host=self.host,
                    port=self.port,
                    reload=True,
                    log_level="info"
                )
            except Exception as alt_error:
                print(f"❌ Error en método alternativo: {alt_error}")
                raise
        
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor detenido por el usuario")
            print("👋 ¡Gracias por usar el Analizador SQL Empresarial!")
    
    def show_help(self):
        """Mostrar ayuda de uso."""
        help_text = """
🚀 Analizador SQL Empresarial - Ayuda

USO:
    python run_sql_analyzer.py [opciones]

OPCIONES:
    --host HOST         Dirección IP del servidor (default: 127.0.0.1)
    --port PORT         Puerto del servidor (default: 8000)
    --no-browser        No abrir navegador automáticamente
    --help              Mostrar esta ayuda

EJEMPLOS:
    python run_sql_analyzer.py
    python run_sql_analyzer.py --port 8080
    python run_sql_analyzer.py --host 0.0.0.0 --port 8000
    python run_sql_analyzer.py --no-browser

CARACTERÍSTICAS:
    ✅ Análisis de archivos SQL hasta 10GB
    ✅ Detección automática de errores
    ✅ Análisis de esquema de base de datos
    ✅ Reconocimiento de dominio con IA
    ✅ Reportes empresariales en múltiples formatos
    ✅ Interfaz web moderna y responsiva
    ✅ Procesamiento en tiempo real

SOPORTE:
    📧 Para soporte técnico, consulta la documentación
    🌐 Interfaz web: http://localhost:8000
    📊 API Docs: http://localhost:8000/api/docs
        """
        print(help_text)

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analizador SQL Empresarial - Iniciador Automático",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Dirección IP del servidor (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Puerto del servidor (default: 8000)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='No abrir navegador automáticamente'
    )
    
    args = parser.parse_args()
    
    # Crear y configurar launcher
    launcher = SQLAnalyzerLauncher()
    launcher.host = args.host
    launcher.port = args.port
    launcher.auto_open_browser = not args.no_browser
    
    # Ejecutar
    launcher.run()

if __name__ == "__main__":
    main()
