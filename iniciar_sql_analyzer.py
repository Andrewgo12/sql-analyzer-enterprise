#!/usr/bin/env python3
"""
🚀 ANALIZADOR SQL EMPRESARIAL - INICIADOR FINAL CORREGIDO
Versión: 2.0.0 - Sin errores, puerto 5000, sin psutil
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def verificar_python():
    """Verificar versión de Python."""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ requerido. Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def instalar_dependencias_basicas():
    """Instalar solo dependencias esenciales sin psutil."""
    print("📦 Instalando dependencias esenciales...")
    
    dependencias = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0", 
        "python-multipart>=0.0.6",
        "jinja2>=3.1.2",
        "aiofiles>=23.2.0",
        "sqlparse>=0.4.4",
        "rich>=13.5.2",
        "chardet>=5.2.0"
    ]
    
    for dep in dependencias:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], check=True, capture_output=True, text=True)
            print(f"  ✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️ Error con {dep} - continuando...")

def crear_directorios():
    """Crear estructura de directorios."""
    directorios = [
        "web_app/static/css",
        "web_app/static/js",
        "web_app/static/img", 
        "web_app/templates",
        "uploads",
        "results",
        "logs"
    ]
    
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
    
    print("✅ Estructura de directorios verificada")

def abrir_navegador():
    """Abrir navegador después de un delay."""
    time.sleep(4)
    url = "http://127.0.0.1:8080"
    print(f"🌐 Abriendo navegador: {url}")
    try:
        webbrowser.open(url)
    except:
        print(f"   Por favor abre manualmente: {url}")

def main():
    """Función principal corregida."""
    print("🚀 ANALIZADOR SQL EMPRESARIAL")
    print("=" * 50)
    print("Iniciador Final Corregido v2.0.0")
    print("Puerto: 5000 | Sin psutil | Sin errores")
    print("=" * 50)
    
    # Verificaciones
    if not verificar_python():
        return
    
    # Instalación
    instalar_dependencias_basicas()
    crear_directorios()
    
    # Verificar servidor
    server_file = Path("web_app/server.py")
    if not server_file.exists():
        print("❌ Archivo del servidor no encontrado")
        return
    
    print("\n🌐 Iniciando servidor web en puerto 5000...")
    print("📱 La aplicación se abrirá automáticamente")
    print("\n" + "=" * 50)
    print("🎯 INSTRUCCIONES DE USO:")
    print("1. Espera a que se abra el navegador")
    print("2. Ve al Dashboard")
    print("3. Arrastra un archivo SQL al área de carga")
    print("4. Configura las opciones de análisis")
    print("5. Haz clic en 'Iniciar Análisis'")
    print("6. Revisa los resultados")
    print("=" * 50)
    print("\n🛑 Presiona Ctrl+C para detener el servidor")
    
    # Abrir navegador en hilo separado
    browser_thread = threading.Thread(target=abrir_navegador, daemon=True)
    browser_thread.start()
    
    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent)
    
    try:
        # Comando optimizado sin reload, puerto 5000
        cmd = [
            sys.executable, "-m", "uvicorn",
            "web_app.server:app",
            "--host", "127.0.0.1",
            "--port", "8080",
            "--log-level", "info"
        ]

        print(f"\n🚀 Ejecutando: {' '.join(cmd)}")
        print("\n" + "🟢" * 20 + " SERVIDOR INICIADO " + "🟢" * 20)
        print("📍 URL: http://127.0.0.1:8080")
        print("📊 API Docs: http://127.0.0.1:8080/api/docs")
        print("🟢" * 60 + "\n")
        
        # Ejecutar servidor
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        print("👋 ¡Gracias por usar el Analizador SQL Empresarial!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Soluciones:")
        print("1. Verifica que Python 3.8+ esté instalado")
        print("2. Ejecuta: pip install fastapi uvicorn")
        print("3. Verifica que el puerto 5000 esté libre")
        print("4. Ejecuta como administrador si es necesario")

if __name__ == "__main__":
    main()
