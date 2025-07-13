#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - DEPENDENCY INSTALLER
Automated installation script for all required dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class DependencyInstaller:
    """Automated dependency installer for SQL Analyzer Enterprise."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_executable = sys.executable
        self.platform = platform.system().lower()
        
        # Core dependencies that must be installed
        self.core_dependencies = [
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "websockets>=12.0",
            "jinja2>=3.1.2",
            "pyyaml>=6.0.1",
            "python-dotenv>=1.0.0",
            "pydantic>=2.5.0",
            "cryptography>=41.0.8",
            "pyjwt>=2.8.0",
            "chardet>=5.2.0",
            "click>=8.1.7",
            "rich>=13.7.0",
            "tqdm>=4.66.1"
        ]
        
        # Optional dependencies for enhanced functionality
        self.optional_dependencies = [
            "sqlalchemy>=2.0.0",
            "pymysql>=1.1.0",
            "psycopg2-binary>=2.9.7",
            "pymongo>=4.5.0",
            "pandas>=2.0.3",
            "openpyxl>=3.1.2",
            "pytest>=7.4.2",
            "pytest-asyncio>=0.21.1",
            "httpx>=0.25.2"
        ]
        
        # Platform-specific dependencies
        self.platform_dependencies = {
            "windows": ["pywin32>=306"],
            "darwin": [],  # macOS
            "linux": []
        }
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8 or higher is required")
            print(f"Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def upgrade_pip(self):
        """Upgrade pip to latest version."""
        print("📦 Upgrading pip...")
        try:
            subprocess.run([
                self.python_executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            print("✅ Pip upgraded successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not upgrade pip: {e}")
            return False
    
    def install_dependencies(self, dependencies, category_name):
        """Install a list of dependencies."""
        print(f"\n📦 Installing {category_name}...")
        
        failed_packages = []
        
        for package in dependencies:
            package_name = package.split(">=")[0].split("==")[0]
            print(f"  Installing {package_name}...")
            
            try:
                subprocess.run([
                    self.python_executable, "-m", "pip", "install", package
                ], check=True, capture_output=True, text=True)
                print(f"  ✅ {package_name} installed successfully")
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {package_name}")
                failed_packages.append(package)
                
                # Try alternative installation methods
                if self.try_alternative_installation(package):
                    print(f"  ✅ {package_name} installed with alternative method")
                else:
                    print(f"  ⚠️  {package_name} will be skipped")
        
        if failed_packages:
            print(f"\n⚠️  Some {category_name.lower()} failed to install:")
            for package in failed_packages:
                print(f"    - {package}")
        else:
            print(f"✅ All {category_name.lower()} installed successfully")
        
        return len(failed_packages) == 0
    
    def try_alternative_installation(self, package):
        """Try alternative installation methods for failed packages."""
        package_name = package.split(">=")[0].split("==")[0]
        
        # Alternative methods for common problematic packages
        alternatives = {
            "psycopg2-binary": ["psycopg2"],
            "python-magic": ["python-magic-bin"] if self.platform == "windows" else [],
            "pywin32": [] if self.platform != "windows" else ["pywin32"],
        }
        
        if package_name in alternatives:
            for alt_package in alternatives[package_name]:
                try:
                    subprocess.run([
                        self.python_executable, "-m", "pip", "install", alt_package
                    ], check=True, capture_output=True)
                    return True
                except subprocess.CalledProcessError:
                    continue
        
        return False
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist."""
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        print("🔧 Creating virtual environment...")
        try:
            subprocess.run([
                self.python_executable, "-m", "venv", str(venv_path)
            ], check=True)
            print("✅ Virtual environment created")
            
            # Provide activation instructions
            if self.platform == "windows":
                activate_script = venv_path / "Scripts" / "activate.bat"
                print(f"💡 To activate: {activate_script}")
            else:
                activate_script = venv_path / "bin" / "activate"
                print(f"💡 To activate: source {activate_script}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def verify_installation(self):
        """Verify that core components can be imported."""
        print("\n🔍 Verifying installation...")
        
        test_imports = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("websockets", "WebSocket support"),
            ("jinja2", "Template engine"),
            ("yaml", "YAML configuration"),
            ("cryptography", "Security features"),
            ("jwt", "JWT authentication"),
            ("pydantic", "Data validation")
        ]
        
        failed_imports = []
        
        for module, description in test_imports:
            try:
                __import__(module)
                print(f"  ✅ {description}")
            except ImportError:
                print(f"  ❌ {description} - Import failed")
                failed_imports.append(module)
        
        if failed_imports:
            print(f"\n⚠️  Some modules failed to import: {', '.join(failed_imports)}")
            print("The application may not work correctly.")
            return False
        else:
            print("\n✅ All core modules verified successfully")
            return True
    
    def install_all(self, create_venv=False, install_optional=True):
        """Install all dependencies."""
        print("🚀 SQL ANALYZER ENTERPRISE - DEPENDENCY INSTALLER")
        print("=" * 60)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Create virtual environment if requested
        if create_venv:
            if not self.create_virtual_environment():
                return False
        
        # Upgrade pip
        self.upgrade_pip()
        
        # Install core dependencies
        core_success = self.install_dependencies(self.core_dependencies, "Core Dependencies")
        
        # Install optional dependencies if requested
        optional_success = True
        if install_optional:
            optional_success = self.install_dependencies(self.optional_dependencies, "Optional Dependencies")
        
        # Install platform-specific dependencies
        platform_deps = self.platform_dependencies.get(self.platform, [])
        platform_success = True
        if platform_deps:
            platform_success = self.install_dependencies(platform_deps, f"Platform Dependencies ({self.platform})")
        
        # Verify installation
        verification_success = self.verify_installation()
        
        # Final report
        print("\n" + "=" * 60)
        print("📊 INSTALLATION SUMMARY")
        print("=" * 60)
        print(f"Core Dependencies: {'✅ SUCCESS' if core_success else '❌ FAILED'}")
        if install_optional:
            print(f"Optional Dependencies: {'✅ SUCCESS' if optional_success else '⚠️  PARTIAL'}")
        if platform_deps:
            print(f"Platform Dependencies: {'✅ SUCCESS' if platform_success else '⚠️  PARTIAL'}")
        print(f"Verification: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
        
        overall_success = core_success and verification_success
        
        if overall_success:
            print("\n🎉 Installation completed successfully!")
            print("You can now run the SQL Analyzer Enterprise application.")
            print("\nTo start the server:")
            print("  python web_app/server.py")
        else:
            print("\n⚠️  Installation completed with issues.")
            print("Some features may not work correctly.")
            print("Please check the error messages above.")
        
        return overall_success

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Install SQL Analyzer Enterprise dependencies')
    parser.add_argument('--venv', action='store_true', help='Create virtual environment')
    parser.add_argument('--core-only', action='store_true', help='Install only core dependencies')
    
    args = parser.parse_args()
    
    installer = DependencyInstaller()
    success = installer.install_all(
        create_venv=args.venv,
        install_optional=not args.core_only
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
