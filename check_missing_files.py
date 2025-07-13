#!/usr/bin/env python3
"""
Check for missing files referenced in templates
"""

import os

def check_missing_files():
    print("Checking for missing files...")
    
    # Files referenced in template
    template_refs = [
        'web_app/static/css/main.css',
        'web_app/static/css/dashboard-enterprise.css', 
        'web_app/static/css/modals-enterprise.css',
        'web_app/static/js/utils.js',
        'web_app/static/js/notifications.js',
        'web_app/static/js/modals.js',
        'web_app/static/js/websocket-manager.js',
        'web_app/static/js/api.js',
        'web_app/static/js/auth.js',
        'web_app/static/js/upload.js',
        'web_app/static/js/analysis.js',
        'web_app/static/js/navigation.js',
        'web_app/static/js/results.js',
        'web_app/static/js/events.js',
        'web_app/static/js/app-controller.js',
        'web_app/static/js/navigation-tests.js',
        'web_app/static/js/test-dashboard.js',
        'web_app/static/js/comprehensive-test.js'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in template_refs:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MISSING")
    
    print(f"\nSummary:")
    print(f"✅ Existing: {len(existing_files)}")
    print(f"❌ Missing: {len(missing_files)}")
    
    if missing_files:
        print(f"\nMissing files:")
        for missing in missing_files:
            print(f"  • {missing}")
        return False
    else:
        print(f"\nAll referenced files exist!")
        return True

if __name__ == "__main__":
    check_missing_files()
