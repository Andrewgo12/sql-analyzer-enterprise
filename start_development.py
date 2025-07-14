#!/usr/bin/env python3
"""
Script de inicio para desarrollo - SQL Analyzer Enterprise
Inicia tanto el backend como el frontend automáticamente
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def print_banner():
    """Mostrar banner de inicio"""
    print("🚀 SQL ANALYZER ENTERPRISE - DESARROLLO")
    print("=" * 60)
    print("🎯 Iniciando sistema completo...")
    print("📍 Backend: http://localhost:5000")
    print("📍 Frontend: http://localhost:3000")
    print("=" * 60)

def check_requirements():
    """Verificar requisitos del sistema"""
    print("🔍 Verificando requisitos...")
    
    # Verificar Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ requerido")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    except:
        print("❌ Python no encontrado")
        return False
    
    # Verificar Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            node_version = result.stdout.strip()
            print(f"✅ Node.js {node_version}")
        else:
            print("❌ Node.js no encontrado")
            return False
    except:
        print("❌ Node.js no encontrado")
        return False
    
    # Verificar npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            npm_version = result.stdout.strip()
            print(f"✅ npm {npm_version}")
        else:
            print("❌ npm no encontrado")
            return False
    except:
        print("❌ npm no encontrado")
        return False
    
    return True

def install_python_dependencies():
    """Instalar dependencias de Python"""
    print("📦 Instalando dependencias de Python...")
    
    required_packages = ['flask', 'flask-cors']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} ya instalado")
        except ImportError:
            print(f"📥 Instalando {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package])
            if result.returncode == 0:
                print(f"✅ {package} instalado")
            else:
                print(f"❌ Error instalando {package}")
                return False
    
    return True

def install_node_dependencies():
    """Instalar dependencias de Node.js"""
    frontend_path = Path('frontend')
    
    if not frontend_path.exists():
        print("❌ Carpeta frontend no encontrada")
        return False
    
    package_json = frontend_path / 'package.json'
    node_modules = frontend_path / 'node_modules'
    
    if not package_json.exists():
        print("❌ package.json no encontrado")
        return False
    
    if not node_modules.exists():
        print("📦 Instalando dependencias de Node.js...")
        result = subprocess.run(['npm', 'install'], cwd=frontend_path)
        if result.returncode != 0:
            print("❌ Error instalando dependencias de Node.js")
            return False
        print("✅ Dependencias de Node.js instaladas")
    else:
        print("✅ Dependencias de Node.js ya instaladas")
    
    return True

def start_backend():
    """Iniciar servidor backend"""
    print("🐍 Iniciando servidor backend...")
    
    try:
        # Ejecutar backend_server.py
        process = subprocess.Popen([sys.executable, 'backend_server.py'])
        return process
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")
        return None

def start_frontend():
    """Iniciar servidor frontend"""
    print("⚛️ Iniciando servidor frontend...")
    
    frontend_path = Path('frontend')
    
    try:
        # Ejecutar npm run dev
        process = subprocess.Popen(['npm', 'run', 'dev'], cwd=frontend_path)
        return process
    except Exception as e:
        print(f"❌ Error iniciando frontend: {e}")
        return None

def wait_for_servers():
    """Esperar a que los servidores estén listos"""
    print("⏳ Esperando a que los servidores estén listos...")
    
    import requests
    import time
    
    # Esperar backend
    backend_ready = False
    for i in range(30):  # 30 segundos máximo
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=1)
            if response.status_code == 200:
                backend_ready = True
                print("✅ Backend listo")
                break
        except:
            pass
        time.sleep(1)
    
    if not backend_ready:
        print("⚠️ Backend tardando en iniciar")
    
    # El frontend tarda más, así que esperamos un poco más
    time.sleep(3)
    print("✅ Frontend debería estar listo")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        print("❌ Requisitos no cumplidos. Instale Python 3.8+ y Node.js")
        return 1
    
    # Instalar dependencias
    if not install_python_dependencies():
        print("❌ Error instalando dependencias de Python")
        return 1
    
    if not install_node_dependencies():
        print("❌ Error instalando dependencias de Node.js")
        return 1
    
    print("\n🚀 Iniciando servidores...")
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ No se pudo iniciar el backend")
        return 1
    
    # Esperar un poco antes de iniciar frontend
    time.sleep(2)
    
    # Iniciar frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ No se pudo iniciar el frontend")
        backend_process.terminate()
        return 1
    
    # Esperar a que estén listos
    wait_for_servers()
    
    print("\n🎉 SISTEMA LISTO!")
    print("=" * 60)
    print("📍 Backend API: http://localhost:5000")
    print("📍 Frontend App: http://localhost:3000")
    print("📍 Health Check: http://localhost:5000/api/health")
    print("=" * 60)
    print("💡 Presiona Ctrl+C para detener ambos servidores")
    print("=" * 60)
    
    try:
        # Esperar hasta que el usuario presione Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidores...")
        
        # Terminar procesos
        if backend_process:
            backend_process.terminate()
            print("✅ Backend detenido")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend detenido")
        
        print("👋 ¡Hasta luego!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
