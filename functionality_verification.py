#!/usr/bin/env python3
"""
Comprehensive Functionality Verification
Test all claimed features: 22+ database engines, 38+ export formats, and core functionality
"""

import json
import time
import requests
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FunctionalityVerifier:
    """Verify all claimed functionality is working"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.verification_results = {
            'database_engines': {},
            'export_formats': {},
            'core_functionality': {},
            'api_endpoints': {},
            'overall_score': 0
        }
    
    def verify_all_functionality(self) -> Dict[str, Any]:
        """Run comprehensive functionality verification"""
        print("🔍 COMPREHENSIVE FUNCTIONALITY VERIFICATION")
        print("=" * 60)
        
        # Test server availability
        if not self._test_server_availability():
            print("❌ Server not available. Starting verification in offline mode...")
            return self._offline_verification()
        
        # Test API endpoints
        self._verify_api_endpoints()
        
        # Test database engines
        self._verify_database_engines()
        
        # Test export formats
        self._verify_export_formats()
        
        # Test core functionality
        self._verify_core_functionality()
        
        # Calculate overall score
        self._calculate_overall_score()
        
        return self.verification_results
    
def main():
    """Run functionality verification"""
    verifier = FunctionalityVerifier()
    results = verifier.verify_all_functionality()
    
    # Save results
    with open('functionality_verification.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 FUNCTIONALITY VERIFICATION SUMMARY")
    print("=" * 60)
    
    if 'database_engines' in results:
        db_engines = results['database_engines']
        print(f"\n🗄️ DATABASE ENGINES:")
        print(f"  • Total found: {db_engines.get('total_claimed', 0)}")
        print(f"  • Verification score: {db_engines.get('verification_score', 0):.1f}%")
    
    if 'export_formats' in results:
        export_formats = results['export_formats']
        print(f"\n📤 EXPORT FORMATS:")
        print(f"  • Total found: {export_formats.get('total_claimed', 0)}")
        print(f"  • Verification score: {export_formats.get('verification_score', 0):.1f}%")
    
    if 'core_functionality' in results:
        core_func = results['core_functionality']
        print(f"\n🔧 CORE FUNCTIONALITY:")
        print(f"  • Working features: {core_func.get('working_features', 0)}/{core_func.get('total_features', 0)}")
        print(f"  • Functionality score: {core_func.get('functionality_score', 0):.1f}%")
    
    print(f"\n🎯 OVERALL SCORE: {results['overall_score']:.1f}%")
    
    if results['overall_score'] >= 90:
        print("🎉 EXCELLENT: All functionality verified and working!")
    elif results['overall_score'] >= 75:
        print("✅ GOOD: Most functionality working with minor issues")
    elif results['overall_score'] >= 50:
        print("⚠️ FAIR: Some functionality working, improvements needed")
    else:
        print("❌ POOR: Significant functionality issues detected")
    
    print(f"\n✅ Verification complete! Detailed results saved to functionality_verification.json")

if __name__ == '__main__':
    main()
