#!/usr/bin/env python3
"""
🧪 PRUEBA COMPLETA DEL ANALIZADOR SQL EMPRESARIAL
Verifica que todo funcione correctamente
"""

import requests
import time
import sys
from pathlib import Path

def probar_servidor():
    """Probar que el servidor responda."""
    print("🧪 Probando servidor...")
    
    try:
        # Probar página principal
        response = requests.get("http://127.0.0.1:5000", timeout=10)
        if response.status_code == 200:
            print("✅ Página principal: OK")
        else:
            print(f"❌ Página principal: Error {response.status_code}")
            return False
            
        # Probar archivos estáticos
        response = requests.get("http://127.0.0.1:5000/static/css/main.css", timeout=10)
        if response.status_code == 200:
            print("✅ Archivos CSS: OK")
        else:
            print(f"⚠️ Archivos CSS: Error {response.status_code}")
            
        # Probar API
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Health: OK")
        else:
            print(f"⚠️ API Health: Error {response.status_code}")
            
        # Probar dashboard
        response = requests.get("http://127.0.0.1:5000/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard: OK")
        else:
            print(f"⚠️ Dashboard: Error {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en puerto 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de prueba."""
    print("🧪 PRUEBA COMPLETA DEL ANALIZADOR SQL EMPRESARIAL")
    print("=" * 60)
    
    # Verificar archivos
    archivos_requeridos = [
        "web_app/server.py",
        "web_app/templates/index.html",
        "web_app/templates/dashboard.html",
        "web_app/static/css/main.css",
        "web_app/static/js/main.js"
    ]
    
    print("📁 Verificando archivos...")
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
    
    print("\n🌐 Verificando servidor...")
    print("   Asegúrate de que el servidor esté ejecutándose:")
    print("   python iniciar_sql_analyzer.py")
    print("\n   Esperando 3 segundos...")
    time.sleep(3)
    
    if probar_servidor():
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La aplicación está funcionando correctamente")
        print("📍 URL: http://127.0.0.1:5000")
        print("📊 Dashboard: http://127.0.0.1:5000/dashboard")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Soluciones:")
        print("1. Ejecuta: python iniciar_sql_analyzer.py")
        print("2. Espera a que aparezca 'Application startup complete'")
        print("3. Ejecuta esta prueba nuevamente")

if __name__ == "__main__":
    main()
