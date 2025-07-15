#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Development Starter
Automated script to start both frontend and backend servers
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 SQL ANALYZER ENTERPRISE - DEVELOPMENT MODE")
    print("=" * 60)
    print("Starting both frontend and backend servers...")
    print()

def check_dependencies():
    """Check if required dependencies are available"""
    print("📋 Checking dependencies...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    print()
    return True

def install_frontend_dependencies():
    """Install frontend dependencies if needed"""
    frontend_dir = Path('frontend')
    node_modules = frontend_dir / 'node_modules'
    
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def start_backend():
    """Start the backend server"""
    print("🐍 Starting backend server...")
    try:
        # Start backend server
        process = subprocess.Popen(
            [sys.executable, 'backend_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor backend output
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"[BACKEND] {line.strip()}")
                if "Running on" in line:
                    print("✅ Backend server started successfully")
                    break
        
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("⚛️  Starting frontend server...")
    try:
        frontend_dir = Path('frontend')
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor frontend output
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"[FRONTEND] {line.strip()}")
                if "Local:" in line or "localhost:3000" in line:
                    print("✅ Frontend server started successfully")
                    break
        
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def monitor_process(process, name):
    """Monitor a process and print its output"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"[{name}] {line.strip()}")
    except Exception:
        pass

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("❌ Failed to install frontend dependencies.")
        sys.exit(1)
    
    # Start servers
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Failed to start backend server")
            sys.exit(1)
        
        # Wait a bit for backend to fully start
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Failed to start frontend server")
            if backend_process:
                backend_process.terminate()
            sys.exit(1)
        
        # Start monitoring threads
        backend_thread = threading.Thread(
            target=monitor_process, 
            args=(backend_process, "BACKEND"),
            daemon=True
        )
        frontend_thread = threading.Thread(
            target=monitor_process, 
            args=(frontend_process, "FRONTEND"),
            daemon=True
        )
        
        backend_thread.start()
        frontend_thread.start()
        
        print()
        print("🎉 Both servers are running!")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:5000")
        print("❤️  Health Check: http://localhost:5000/api/health")
        print()
        print("Press Ctrl+C to stop both servers")
        print()
        
        # Wait for processes
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
    
    finally:
        # Clean up processes
        if backend_process:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
        
        if frontend_process:
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
        
        print("✅ Servers stopped")

if __name__ == '__main__':
    main()
