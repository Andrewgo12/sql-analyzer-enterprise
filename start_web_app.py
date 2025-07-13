#!/usr/bin/env python3
"""
Iniciador Simplificado - Analizador SQL Empresarial
Script para iniciar rápidamente la aplicación web
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def install_dependencies():
    """Instalar dependencias básicas."""
    print("📦 Instalando dependencias...")
    
    dependencies = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0", 
        "python-multipart>=0.0.6",
        "jinja2>=3.1.2",
        "aiofiles>=23.2.0",
        "sqlparse>=0.4.4",
        "rich>=13.5.2",
        "pyyaml>=6.0.1",
        "chardet>=5.2.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"  ✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️ Error instalando {dep}")

def create_basic_structure():
    """Crear estructura básica de directorios."""
    print("📁 Creando estructura de directorios...")
    
    directories = [
        "web_app/static/css",
        "web_app/static/js", 
        "web_app/static/img",
        "web_app/templates",
        "sql_analyzer/core",
        "uploads",
        "results"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Estructura creada")

def open_browser_delayed():
    """Abrir navegador después de un delay."""
    time.sleep(3)
    url = "http://127.0.0.1:8000"
    print(f"🌐 Abriendo navegador: {url}")
    webbrowser.open(url)

def main():
    """Función principal."""
    print("🚀 Analizador SQL Empresarial - Inicio Rápido")
    print("=" * 50)
    
    try:
        # Verificar Python
        if sys.version_info < (3, 8):
            print(f"❌ Python 3.8+ requerido. Versión actual: {sys.version}")
            return
        
        print(f"✅ Python {sys.version.split()[0]}")
        
        # Instalar dependencias
        install_dependencies()
        
        # Crear estructura
        create_basic_structure()
        
        # Verificar que el servidor existe
        server_file = Path("web_app/server.py")
        if not server_file.exists():
            print(f"❌ Archivo del servidor no encontrado: {server_file}")
            print("Por favor, asegúrate de que todos los archivos estén en su lugar.")
            return
        
        print("🌐 Iniciando servidor web...")
        print("📱 La aplicación se abrirá automáticamente en tu navegador")
        print("\n" + "=" * 50)
        print("🎯 INSTRUCCIONES:")
        print("1. Espera a que se abra el navegador")
        print("2. Arrastra un archivo SQL al área de carga")
        print("3. Configura las opciones de análisis")
        print("4. Haz clic en 'Iniciar Análisis'")
        print("5. Descarga los resultados")
        print("=" * 50)
        print("\n🛑 Presiona Ctrl+C para detener el servidor")
        
        # Programar apertura del navegador
        browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
        browser_thread.start()
        
        # Cambiar al directorio del proyecto
        os.chdir(Path(__file__).parent)
        
        # Iniciar servidor optimizado sin reload
        cmd = [
            sys.executable, "-m", "uvicorn",
            "web_app.server:app",
            "--host", "127.0.0.1",
            "--port", "5000",
            "--log-level", "info"
        ]
        
        print(f"🚀 Ejecutando: {' '.join(cmd)}")
        print("\n" + "🟢" * 20 + " SERVIDOR INICIADO " + "🟢" * 20)
        print("📍 URL: http://127.0.0.1:5000")
        print("🟢" * 60 + "\n")
        
        # Ejecutar servidor
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        print("👋 ¡Gracias por usar el Analizador SQL Empresarial!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Soluciones posibles:")
        print("1. Verifica que Python 3.8+ esté instalado")
        print("2. Verifica que pip funcione correctamente")
        print("3. Ejecuta: pip install fastapi uvicorn")
        print("4. Verifica que todos los archivos estén presentes")

if __name__ == "__main__":
    main()
