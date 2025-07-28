#!/usr/bin/env python3
"""
ENTERPRISE SQL ANALYZER - PRODUCTION STARTER
Complete production-ready application with all enterprise features
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config.settings import APP_METADATA

def print_startup_banner():
    """Print enterprise startup banner"""
    print("=" * 80)
    print("🚀 SQL ANALYZER ENTERPRISE - PRODUCTION READY")
    print("=" * 80)
    print(f"📦 Application: {APP_METADATA['name']}")
    print(f"🔢 Version: {APP_METADATA['version']}")
    print(f"📝 Description: {APP_METADATA['description']}")
    print(f"👥 Author: {APP_METADATA['author']}")
    from datetime import datetime
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def print_features():
    """Print enterprise features"""
    print("✨ ENTERPRISE FEATURES:")
    print("   ✅ Multi-Database Support (MySQL, PostgreSQL, Oracle, SQL Server, SQLite)")
    print("   ✅ Large File Processing (up to 100MB)")
    print("   ✅ Real-Time SQL Analysis (<2s processing)")
    print("   ✅ Security Vulnerability Scanning (OWASP compliance)")
    print("   ✅ Performance Optimization Suggestions")
    print("   ✅ Intelligent Commenting in Spanish")
    print("   ✅ Schema & Relationship Analysis")
    print("   ✅ Multi-Format Export (20+ formats)")
    print("   ✅ Auto-Correction Capabilities")
    print("   ✅ Enterprise-Grade Error Handling")
    print("   ✅ Comprehensive Validation & Security")
    print("   ✅ Business Logic & Quality Assessment")
    print("   ✅ Data Persistence & Caching")
    print("   ✅ Performance Monitoring & Metrics")
    print("=" * 80)

def print_architecture():
    """Print system architecture"""
    print("🏗️ ENTERPRISE ARCHITECTURE:")
    print("   📊 Models: Comprehensive data models with validation")
    print("   🔧 Services: Business logic and analysis services")
    print("   🎮 Controllers: Request handling and validation")
    print("   🌐 Views: Professional web interface")
    print("   🛠️ Utils: Enterprise utilities and helpers")
    print("   🗄️ Data Access: Repository pattern with caching")
    print("   ✅ Validation: Multi-layer validation engine")
    print("   📈 Business Logic: Quality assessment and rules")
    print("   🧪 Testing: Comprehensive test suite")
    print("=" * 80)

def print_api_endpoints():
    """Print available API endpoints"""
    print("🔌 API ENDPOINTS:")
    print("   📊 Health Check:")
    print("      GET  /api/health")
    print("   🔬 Analysis:")
    print("      POST /api/analyze")
    print("      GET  /api/analysis/<id>")
    print("      GET  /api/analysis/<id>/summary")
    print("   🛡️ Security:")
    print("      GET  /api/analysis/<id>/security")
    print("   ⚡ Performance:")
    print("      GET  /api/analysis/<id>/performance")
    print("   🗄️ Schema:")
    print("      GET  /api/analysis/<id>/schema")
    print("   📤 Export:")
    print("      GET  /api/export/<id>/<format>")
    print("=" * 80)

def print_web_views():
    """Print available web views"""
    print("🌐 WEB VIEWS:")
    print("   🏠 Main Views:")
    print("      /                        - SQL Analysis & Correction")
    print("      /sql-analysis           - SQL Analysis & Correction")
    print("      /security-analysis      - Security & Vulnerability Scanning")
    print("      /performance-optimization - Performance Optimization")
    print("      /schema-analysis        - Schema & Relationship Analysis")
    print("      /export-center          - Export & Format Conversion")
    print("      /version-management     - Version Management")
    print("      /comment-documentation  - Comment & Documentation")
    print("=" * 80)

def check_dependencies():
    """Check required dependencies"""
    print("🔍 CHECKING DEPENDENCIES:")
    
    required_modules = [
        'flask', 'chardet', 'psutil'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module} (missing)")
    
    if missing_modules:
        print(f"\n💡 Install missing dependencies:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    print("   ✅ All dependencies satisfied")
    return True

def check_core_files():
    """Check core application files"""
    print("\n📁 CHECKING CORE FILES:")
    
    core_files = [
        'comprehensive_sql_analyzer.py',
        'enterprise_file_processor.py',
        'export_engine.py',
        'app/__init__.py',
        'app/models/analysis_models.py',
        'app/services/analysis_service.py',
        'app/controllers/analysis_controller.py'
    ]
    
    missing_files = []
    
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} (missing)")
    
    if missing_files:
        print(f"\n❌ Missing core files. Please ensure all files are present.")
        return False
    
    print("   ✅ All core files present")
    return True

def main():
    """Main application starter"""
    print_startup_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ STARTUP FAILED: Missing dependencies")
        sys.exit(1)
    
    # Check core files
    if not check_core_files():
        print("\n❌ STARTUP FAILED: Missing core files")
        sys.exit(1)
    
    # Print system information
    print_features()
    print_architecture()
    print_api_endpoints()
    print_web_views()
    
    # Get configuration
    environment = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = environment == 'development'
    
    print("⚙️ CONFIGURATION:")
    print(f"   🌍 Environment: {environment}")
    print(f"   🖥️ Host: {host}")
    print(f"   🔌 Port: {port}")
    print(f"   🐛 Debug: {debug}")
    print("=" * 80)
    
    try:
        # Create application
        print("🔧 INITIALIZING APPLICATION...")
        app = create_app(environment)
        
        if not app:
            print("❌ STARTUP FAILED: Could not create application")
            sys.exit(1)
        
        print("✅ Application initialized successfully")
        
        # Print startup completion
        print("\n🎉 STARTUP COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"🌐 Server starting on http://{host}:{port}")
        print("🔥 Press Ctrl+C to stop the server")
        print("📖 Visit the URL above to access the SQL Analyzer Enterprise")
        print("=" * 80)
        
        # Start the server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=debug
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 SERVER STOPPED BY USER")
        print("👋 Thank you for using SQL Analyzer Enterprise!")
        
    except Exception as e:
        print(f"\n❌ STARTUP ERROR: {str(e)}")
        logging.exception("Application startup failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
