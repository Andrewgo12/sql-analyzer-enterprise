#!/usr/bin/env python3
"""
SQL Analyzer Enterprise - Automatic Startup System
Launches both frontend and backend simultaneously with health monitoring
"""

import os
import sys
import time
import json
import signal
import subprocess
import threading
import requests
from pathlib import Path
from datetime import datetime

class EnterpriseStartupManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        self.startup_timeout = 60  # seconds
        self.health_check_interval = 10  # seconds
        
        # Paths
        self.root_path = Path(__file__).parent
        self.backend_path = self.root_path
        self.frontend_path = self.root_path / 'frontend'
        
        # URLs
        self.backend_url = 'http://localhost:5000'
        self.frontend_url = 'http://localhost:3000'
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.shutdown()
        sys.exit(0)
    
    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        self.log("🔍 Checking system dependencies...")
        
        # Check Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.log("❌ Python 3.8+ is required", "ERROR")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                self.log(f"✅ Node.js version: {node_version}")
            else:
                self.log("❌ Node.js is not installed", "ERROR")
                return False
        except FileNotFoundError:
            self.log("❌ Node.js is not installed", "ERROR")
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                self.log(f"✅ npm version: {npm_version}")
            else:
                self.log("❌ npm is not available", "ERROR")
                return False
        except FileNotFoundError:
            self.log("❌ npm is not available", "ERROR")
            return False
        
        # Check required files
        required_files = [
            self.backend_path / 'backend_server.py',
            self.frontend_path / 'package.json',
            self.frontend_path / 'vite.config.js'
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.log(f"❌ Required file missing: {file_path}", "ERROR")
                return False
        
        self.log("✅ All dependencies check passed")
        return True
    
    def install_frontend_dependencies(self):
        """Install frontend dependencies if needed"""
        node_modules_path = self.frontend_path / 'node_modules'
        
        if not node_modules_path.exists():
            self.log("📦 Installing frontend dependencies...")
            try:
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=self.frontend_path,
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    self.log("✅ Frontend dependencies installed successfully")
                    return True
                else:
                    self.log(f"❌ Failed to install frontend dependencies: {result.stderr}", "ERROR")
                    return False
            except subprocess.TimeoutExpired:
                self.log("❌ Frontend dependency installation timed out", "ERROR")
                return False
            except Exception as e:
                self.log(f"❌ Error installing frontend dependencies: {e}", "ERROR")
                return False
        else:
            self.log("✅ Frontend dependencies already installed")
            return True
    
    def start_backend(self):
        """Start the backend server"""
        self.log("🚀 Starting backend server...")
        
        try:
            # Start backend process
            self.backend_process = subprocess.Popen(
                [sys.executable, 'backend_server.py'],
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log(f"✅ Backend process started (PID: {self.backend_process.pid})")
            
            # Start backend output monitoring in separate thread
            backend_monitor = threading.Thread(
                target=self.monitor_backend_output,
                daemon=True
            )
            backend_monitor.start()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        self.log("🚀 Starting frontend development server...")
        
        try:
            # Start frontend process
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log(f"✅ Frontend process started (PID: {self.frontend_process.pid})")
            
            # Start frontend output monitoring in separate thread
            frontend_monitor = threading.Thread(
                target=self.monitor_frontend_output,
                daemon=True
            )
            frontend_monitor.start()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start frontend: {e}", "ERROR")
            return False
    
    def monitor_backend_output(self):
        """Monitor backend process output"""
        if not self.backend_process:
            return
        
        for line in iter(self.backend_process.stdout.readline, ''):
            if not self.running:
                break
            if line.strip():
                self.log(f"[BACKEND] {line.strip()}")
    
    def monitor_frontend_output(self):
        """Monitor frontend process output"""
        if not self.frontend_process:
            return
        
        for line in iter(self.frontend_process.stdout.readline, ''):
            if not self.running:
                break
            if line.strip():
                # Filter out verbose Vite output
                if any(keyword in line.lower() for keyword in ['local:', 'network:', 'ready in']):
                    self.log(f"[FRONTEND] {line.strip()}")
    
    def wait_for_backend_health(self):
        """Wait for backend to be healthy"""
        self.log("⏳ Waiting for backend to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            try:
                response = requests.get(f"{self.backend_url}/api/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get('status') == 'healthy':
                        self.log("✅ Backend is healthy and ready")
                        return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        self.log("❌ Backend health check timed out", "ERROR")
        return False
    
    def wait_for_frontend_ready(self):
        """Wait for frontend to be ready"""
        self.log("⏳ Waiting for frontend to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            try:
                response = requests.get(self.frontend_url, timeout=5)
                if response.status_code == 200:
                    self.log("✅ Frontend is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        self.log("❌ Frontend readiness check timed out", "ERROR")
        return False
    
    def health_monitor(self):
        """Continuous health monitoring"""
        while self.running:
            try:
                # Check backend health
                backend_healthy = False
                try:
                    response = requests.get(f"{self.backend_url}/api/health", timeout=3)
                    backend_healthy = response.status_code == 200
                except:
                    pass
                
                # Check frontend health
                frontend_healthy = False
                try:
                    response = requests.get(self.frontend_url, timeout=3)
                    frontend_healthy = response.status_code == 200
                except:
                    pass
                
                # Check process status
                backend_running = self.backend_process and self.backend_process.poll() is None
                frontend_running = self.frontend_process and self.frontend_process.poll() is None
                
                if not backend_running or not frontend_running:
                    self.log("❌ One or more processes have stopped", "ERROR")
                    break
                
                if not backend_healthy or not frontend_healthy:
                    self.log("⚠️ Health check failed, but processes are running", "WARNING")
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.log(f"❌ Health monitor error: {e}", "ERROR")
                break
    
    def shutdown(self):
        """Gracefully shutdown all processes"""
        self.log("🛑 Shutting down SQL Analyzer Enterprise...")
        
        # Stop frontend
        if self.frontend_process:
            self.log("Stopping frontend server...")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
                self.log("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.log("⚠️ Force killing frontend process")
                self.frontend_process.kill()
            except Exception as e:
                self.log(f"❌ Error stopping frontend: {e}", "ERROR")
        
        # Stop backend
        if self.backend_process:
            self.log("Stopping backend server...")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
                self.log("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.log("⚠️ Force killing backend process")
                self.backend_process.kill()
            except Exception as e:
                self.log(f"❌ Error stopping backend: {e}", "ERROR")
        
        self.log("✅ Shutdown complete")
    
    def start(self):
        """Main startup sequence"""
        self.log("🚀 SQL Analyzer Enterprise - Automatic Startup System")
        self.log("=" * 80)
        
        # Check dependencies
        if not self.check_dependencies():
            self.log("❌ Dependency check failed", "ERROR")
            return False
        
        # Install frontend dependencies
        if not self.install_frontend_dependencies():
            self.log("❌ Frontend dependency installation failed", "ERROR")
            return False
        
        # Start backend
        if not self.start_backend():
            self.log("❌ Backend startup failed", "ERROR")
            return False
        
        # Wait for backend to be healthy
        if not self.wait_for_backend_health():
            self.log("❌ Backend health check failed", "ERROR")
            self.shutdown()
            return False
        
        # Start frontend
        if not self.start_frontend():
            self.log("❌ Frontend startup failed", "ERROR")
            self.shutdown()
            return False
        
        # Wait for frontend to be ready
        if not self.wait_for_frontend_ready():
            self.log("❌ Frontend readiness check failed", "ERROR")
            self.shutdown()
            return False
        
        # Success message
        self.log("=" * 80)
        self.log("🎉 SQL Analyzer Enterprise is now running!")
        self.log(f"🌐 Frontend: {self.frontend_url}")
        self.log(f"🔧 Backend API: {self.backend_url}")
        self.log("=" * 80)
        
        # Start health monitoring
        health_monitor = threading.Thread(target=self.health_monitor, daemon=True)
        health_monitor.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True

def main():
    """Main entry point"""
    startup_manager = EnterpriseStartupManager()
    
    try:
        success = startup_manager.start()
        if not success:
            sys.exit(1)
    except Exception as e:
        startup_manager.log(f"❌ Unexpected error: {e}", "ERROR")
        startup_manager.shutdown()
        sys.exit(1)

if __name__ == '__main__':
    main()
