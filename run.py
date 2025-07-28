#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - MAIN APPLICATION RUNNER
Production-ready application with comprehensive MVC architecture
"""

import os
import sys
import logging
from app import create_app
from app.config.settings import APP_METADATA

def main():
    """Main application entry point"""
    
    # Print startup banner
    print("=" * 60)
    print(f"🚀 {APP_METADATA['name']} v{APP_METADATA['version']}")
    print(f"📝 {APP_METADATA['description']}")
    print("=" * 60)
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create application
    try:
        app = create_app(config_name)
        
        # Print configuration info
        print(f"🔧 Configuration: {config_name}")
        print(f"🐛 Debug Mode: {app.config['DEBUG']}")
        print(f"📁 Max File Size: {app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB")
        print(f"🔒 Security Enabled: {app.config['SECURITY_ENABLED']}")
        print(f"⚡ Performance Target: {app.config['PERFORMANCE_TARGET']}s")
        print("=" * 60)
        
        # Print available routes
        print("📍 Available Routes:")
        print("   🏠 Main Views:")
        print("      / - SQL Analysis & Correction")
        print("      /security-analysis - Security & Vulnerability Scanning")
        print("      /performance-optimization - Performance Optimization")
        print("      /schema-analysis - Schema & Relationship Analysis")
        print("      /export-center - Export & Format Conversion")
        print("      /version-management - Version Management")
        print("      /comment-documentation - Comment & Documentation")
        print()
        print("   🔌 API Endpoints:")
        print("      GET  /api/health - Health check")
        print("      POST /api/analyze - Analyze SQL file")
        print("      GET  /api/analysis/<id> - Get analysis details")
        print("      GET  /api/analysis/<id>/summary - Get analysis summary")
        print("      GET  /api/analysis/<id>/security - Get security analysis")
        print("      GET  /api/analysis/<id>/performance - Get performance analysis")
        print("      GET  /api/analysis/<id>/schema - Get schema analysis")
        print("      GET  /api/export/<id>/<format> - Export analysis results")
        print("=" * 60)
        
        # Print supported features
        print("✨ Enterprise Features:")
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
        print("=" * 60)
        
        # Start application
        host = os.environ.get('HOST', '127.0.0.1')
        port = int(os.environ.get('PORT', 5000))
        
        print(f"🌐 Starting server on http://{host}:{port}")
        print("🔥 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        app.run(
            host=host,
            port=port,
            debug=app.config['DEBUG'],
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("💡 Make sure all required modules are available:")
        print("   - comprehensive_sql_analyzer.py")
        print("   - enterprise_file_processor.py") 
        print("   - export_engine.py")
        print("   - Flask and other dependencies")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Application Error: {str(e)}")
        logging.exception("Application startup failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
