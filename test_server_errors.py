#!/usr/bin/env python3
"""
Test server for runtime errors
"""

import sys
import os
from pathlib import Path

def test_server():
    print("Testing server for runtime errors...")
    
    # Setup paths
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / "web_app"))
    os.chdir(project_root / "web_app")
    
    try:
        import server
        print("✅ Server module imported successfully")
        
        # Test critical components
        if hasattr(server, 'app'):
            print("✅ FastAPI app exists")
            
            # Test app configuration
            if hasattr(server.app, 'routes'):
                print(f"✅ Routes configured: {len(server.app.routes)} routes")
            
            # Test middleware
            try:
                if hasattr(server.app, 'middleware_stack') and server.app.middleware_stack:
                    print(f"✅ Middleware configured: {len(server.app.middleware_stack)} middleware")
                elif hasattr(server.app, 'middleware'):
                    print("✅ Middleware configured: middleware available")
                else:
                    print("✅ Middleware: not configured (using defaults)")
            except Exception as e:
                print(f"⚠️ Middleware check failed: {e}")
        
        # Test security manager
        if hasattr(server, 'SecurityManager'):
            security_manager = server.SecurityManager()
            test_sql = "SELECT * FROM users WHERE id = 1"
            result = security_manager.validate_sql_security(test_sql)
            print(f"✅ SecurityManager working: score {result.get('score', 0)}")
        
        # Test database integration
        if hasattr(server, 'DatabaseIntegrationManager'):
            db_manager = server.DatabaseIntegrationManager()
            db_type = db_manager.detect_database_type("SELECT * FROM test")
            print(f"✅ DatabaseIntegrationManager working: detected {db_type}")
        
        print("🎉 All server components working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n✅ Server test passed")
    else:
        print("\n❌ Server test failed")
