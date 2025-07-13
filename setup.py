#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - AUTOMATED SETUP SCRIPT
Complete installation and configuration for immediate project execution
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json

class SQLAnalyzerSetup:
    """Automated setup for SQL Analyzer Enterprise."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.platform = platform.system().lower()
        self.python_executable = sys.executable
        
        # Required directories
        self.required_dirs = [
            "web_app/static/css",
            "web_app/static/js", 
            "web_app/static/images",
            "web_app/templates",
            "web_app/security",
            "web_app/integrations",
            "config",
            "tests",
            "conclusions_arc/reports",
            "conclusions_arc/analytics",
            "conclusions_arc/exports",
            "conclusions_arc/logs",
            "temp",
            "uploads",
            "output"
        ]
        
        # Core dependencies
        self.dependencies = [
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "websockets>=12.0",
            "jinja2>=3.1.2",
            "pyyaml>=6.0.1",
            "pyjwt>=2.8.0",
            "cryptography>=41.0.8",
            "sqlalchemy>=2.0.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "click>=8.1.7",
            "rich>=13.7.0"
        ]
    
    def print_banner(self):
        """Print setup banner."""
        print("=" * 70)
        print("🚀 SQL ANALYZER ENTERPRISE - AUTOMATED SETUP")
        print("=" * 70)
        print("Setting up your enterprise SQL analysis environment...")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print("=" * 70)
    
    def check_python_version(self):
        """Check Python version compatibility."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ ERROR: Python 3.8 or higher is required")
            print(f"Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python version check passed: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def create_directories(self):
        """Create required project directories."""
        print("\n📁 Creating project directories...")
        
        for dir_path in self.required_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {dir_path}")
        
        print("✅ All directories created successfully")
    
    def install_dependencies(self):
        """Install required Python dependencies."""
        print("\n📦 Installing Python dependencies...")
        
        # Upgrade pip first
        try:
            subprocess.run([
                self.python_executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            print("  ✅ Pip upgraded")
        except subprocess.CalledProcessError:
            print("  ⚠️  Warning: Could not upgrade pip")
        
        # Install dependencies
        failed_packages = []
        for package in self.dependencies:
            package_name = package.split(">=")[0]
            print(f"  Installing {package_name}...")
            
            try:
                subprocess.run([
                    self.python_executable, "-m", "pip", "install", package
                ], check=True, capture_output=True)
                print(f"    ✅ {package_name}")
            except subprocess.CalledProcessError:
                print(f"    ❌ Failed: {package_name}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n⚠️  Some packages failed to install: {', '.join(failed_packages)}")
            print("The application may still work with reduced functionality.")
        else:
            print("✅ All dependencies installed successfully")
    
    def create_configuration_files(self):
        """Create default configuration files."""
        print("\n⚙️  Creating configuration files...")
        
        # Create .env file
        env_file = self.project_root / ".env"
        if not env_file.exists():
            env_content = """# SQL Analyzer Enterprise Configuration
DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///sql_analyzer.db
UPLOAD_MAX_SIZE=10737418240
ALLOWED_EXTENSIONS=.sql,.txt,.pdf,.csv,.json
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("  ✅ .env file created")
        
        # Create basic config.yaml
        config_file = self.project_root / "config" / "base.yaml"
        if not config_file.exists():
            config_content = """# SQL Analyzer Enterprise Base Configuration
server:
  host: "127.0.0.1"
  port: 8081
  debug: true

database:
  url: "sqlite:///sql_analyzer.db"

security:
  session_timeout: 3600
  max_login_attempts: 5

processing:
  max_file_size: 10737418240
  temp_dir: "temp"
  output_dir: "output"
"""
            with open(config_file, 'w') as f:
                f.write(config_content)
            print("  ✅ Configuration file created")
    
    def verify_installation(self):
        """Verify that the installation is working."""
        print("\n🔍 Verifying installation...")
        
        # Test core imports
        test_modules = [
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("websockets", "WebSockets"),
            ("jinja2", "Jinja2"),
            ("yaml", "PyYAML"),
            ("jwt", "PyJWT"),
            ("cryptography", "Cryptography")
        ]
        
        failed_imports = []
        for module, name in test_modules:
            try:
                __import__(module)
                print(f"  ✅ {name}")
            except ImportError:
                print(f"  ❌ {name}")
                failed_imports.append(name)
        
        # Test server import
        try:
            sys.path.insert(0, str(self.project_root / "web_app"))
            import server
            print("  ✅ Server module")
        except Exception as e:
            print(f"  ❌ Server module: {e}")
            failed_imports.append("Server")
        
        if failed_imports:
            print(f"\n⚠️  Some components failed verification: {', '.join(failed_imports)}")
            return False
        else:
            print("✅ All components verified successfully")
            return True
    
    def create_startup_scripts(self):
        """Create startup scripts for different platforms."""
        print("\n📜 Creating startup scripts...")
        
        # Windows batch file
        if self.platform == "windows":
            batch_content = f"""@echo off
echo Starting SQL Analyzer Enterprise...
cd /d "{self.project_root}"
cd web_app
"{self.python_executable}" server.py
pause
"""
            with open(self.project_root / "start_server.bat", 'w') as f:
                f.write(batch_content)
            print("  ✅ Windows batch file created (start_server.bat)")
        
        # Unix shell script
        shell_content = f"""#!/bin/bash
echo "Starting SQL Analyzer Enterprise..."
cd "{self.project_root}"
cd web_app
"{self.python_executable}" server.py
"""
        shell_script = self.project_root / "start_server.sh"
        with open(shell_script, 'w') as f:
            f.write(shell_content)
        
        # Make executable on Unix systems
        if self.platform != "windows":
            os.chmod(shell_script, 0o755)
        
        print("  ✅ Shell script created (start_server.sh)")
    
    def run_setup(self):
        """Run complete setup process."""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        # Setup steps
        try:
            self.create_directories()
            self.install_dependencies()
            self.create_configuration_files()
            self.create_startup_scripts()
            
            # Verify installation
            if self.verify_installation():
                self.print_success_message()
                return True
            else:
                self.print_partial_success_message()
                return False
                
        except Exception as e:
            print(f"\n❌ Setup failed with error: {e}")
            return False
    
    def print_success_message(self):
        """Print success message with instructions."""
        print("\n" + "=" * 70)
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("Your SQL Analyzer Enterprise is ready to use!")
        print()
        print("🚀 TO START THE APPLICATION:")
        print()
        if self.platform == "windows":
            print("   Option 1: Double-click 'start_server.bat'")
            print("   Option 2: Run in command prompt:")
            print("             cd web_app")
            print("             python server.py")
        else:
            print("   Option 1: Run './start_server.sh'")
            print("   Option 2: Run in terminal:")
            print("             cd web_app")
            print("             python server.py")
        print()
        print("🌐 ACCESS THE APPLICATION:")
        print("   Open your browser and go to: http://localhost:8081")
        print()
        print("📚 DEFAULT LOGIN:")
        print("   Username: admin")
        print("   Password: admin123")
        print()
        print("=" * 70)
    
    def print_partial_success_message(self):
        """Print partial success message."""
        print("\n" + "=" * 70)
        print("⚠️  SETUP COMPLETED WITH WARNINGS")
        print("=" * 70)
        print("The application was set up but some components may not work correctly.")
        print("Please check the error messages above and install missing dependencies manually.")
        print("=" * 70)

def main():
    """Main setup function."""
    setup = SQLAnalyzerSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
