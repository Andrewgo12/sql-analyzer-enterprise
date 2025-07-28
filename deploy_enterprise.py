#!/usr/bin/env python3
"""
ENTERPRISE DEPLOYMENT SCRIPT
Production-ready deployment with comprehensive validation and monitoring
"""

import os
import sys
import time
import logging
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import APP_METADATA, get_config
from app.utils.helpers import LoggingHelper, FileHelper
from tests.test_enterprise_system import run_enterprise_tests

class EnterpriseDeployment:
    """Enterprise deployment manager with comprehensive validation"""
    
    def __init__(self):
        self.logger = LoggingHelper.setup_logger('enterprise_deployment')
        self.deployment_start_time = datetime.now()
        self.deployment_steps = []
        self.validation_results = {}
        
        print("🚀 ENTERPRISE SQL ANALYZER DEPLOYMENT")
        print("=" * 60)
        print(f"📦 Application: {APP_METADATA['name']} v{APP_METADATA['version']}")
        print(f"📅 Deployment Time: {self.deployment_start_time.isoformat()}")
        print("=" * 60)
    
    def deploy(self, environment: str = 'production') -> bool:
        """Execute complete enterprise deployment"""
        try:
            # Step 1: Pre-deployment validation
            if not self._pre_deployment_validation():
                return False
            
            # Step 2: System requirements check
            if not self._check_system_requirements():
                return False
            
            # Step 3: Run comprehensive tests
            if not self._run_comprehensive_tests():
                return False
            
            # Step 4: Validate configuration
            if not self._validate_configuration(environment):
                return False
            
            # Step 5: Initialize database
            if not self._initialize_database():
                return False
            
            # Step 6: Validate core components
            if not self._validate_core_components():
                return False
            
            # Step 7: Performance validation
            if not self._validate_performance():
                return False
            
            # Step 8: Security validation
            if not self._validate_security():
                return False
            
            # Step 9: Start application
            if not self._start_application(environment):
                return False
            
            # Step 10: Post-deployment validation
            if not self._post_deployment_validation():
                return False
            
            # Step 11: Generate deployment report
            self._generate_deployment_report()
            
            print("\n🎉 ENTERPRISE DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            print(f"\n❌ DEPLOYMENT FAILED: {str(e)}")
            return False
    
    def _pre_deployment_validation(self) -> bool:
        """Pre-deployment validation checks"""
        print("\n📋 Step 1: Pre-deployment Validation")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                print("❌ Python 3.8+ required")
                return False
            print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check required files
            required_files = [
                'app/__init__.py',
                'app/models/analysis_models.py',
                'app/services/analysis_service.py',
                'app/controllers/analysis_controller.py',
                'comprehensive_sql_analyzer.py',
                'enterprise_file_processor.py',
                'export_engine.py'
            ]
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    print(f"❌ Required file missing: {file_path}")
                    return False
            print(f"✅ All {len(required_files)} required files present")
            
            # Check directory structure
            required_dirs = [
                'app/models', 'app/services', 'app/controllers',
                'app/templates', 'app/static', 'app/utils', 'tests'
            ]
            
            for dir_path in required_dirs:
                if not os.path.isdir(dir_path):
                    print(f"❌ Required directory missing: {dir_path}")
                    return False
            print(f"✅ All {len(required_dirs)} required directories present")
            
            self.deployment_steps.append("Pre-deployment validation: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Pre-deployment validation failed: {str(e)}")
            return False
    
    def _check_system_requirements(self) -> bool:
        """Check system requirements"""
        print("\n🖥️ Step 2: System Requirements Check")
        
        try:
            # Check available memory
            try:
                import psutil
                memory = psutil.virtual_memory()
                available_gb = memory.available / (1024**3)
                
                if available_gb < 1.0:
                    print(f"⚠️ Low memory: {available_gb:.1f}GB available (recommended: 2GB+)")
                else:
                    print(f"✅ Memory: {available_gb:.1f}GB available")
            except ImportError:
                print("⚠️ psutil not available - cannot check memory")
            
            # Check disk space
            try:
                disk_usage = os.statvfs('.')
                free_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
                
                if free_gb < 1.0:
                    print(f"⚠️ Low disk space: {free_gb:.1f}GB free (recommended: 5GB+)")
                else:
                    print(f"✅ Disk space: {free_gb:.1f}GB free")
            except AttributeError:
                # Windows doesn't have statvfs
                print("⚠️ Cannot check disk space on this platform")
            
            # Check required Python packages
            required_packages = ['flask', 'chardet']
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                    print(f"✅ Package: {package}")
                except ImportError:
                    missing_packages.append(package)
                    print(f"❌ Missing package: {package}")
            
            if missing_packages:
                print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
                return False
            
            self.deployment_steps.append("System requirements: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ System requirements check failed: {str(e)}")
            return False
    
    def _run_comprehensive_tests(self) -> bool:
        """Run comprehensive test suite"""
        print("\n🧪 Step 3: Comprehensive Testing")
        
        try:
            print("Running enterprise test suite...")
            test_success = run_enterprise_tests()
            
            if test_success:
                print("✅ All tests passed")
                self.deployment_steps.append("Comprehensive testing: PASSED")
                return True
            else:
                print("❌ Some tests failed")
                return False
                
        except Exception as e:
            print(f"❌ Testing failed: {str(e)}")
            return False
    
    def _validate_configuration(self, environment: str) -> bool:
        """Validate application configuration"""
        print(f"\n⚙️ Step 4: Configuration Validation ({environment})")
        
        try:
            # Load configuration
            config = get_config(environment)
            
            # Validate critical settings
            critical_settings = [
                'SECRET_KEY', 'MAX_CONTENT_LENGTH', 'ALLOWED_EXTENSIONS',
                'ANALYSIS_TIMEOUT', 'EXPORT_FORMATS'
            ]
            
            for setting in critical_settings:
                if not hasattr(config, setting):
                    print(f"❌ Missing configuration: {setting}")
                    return False
                print(f"✅ Configuration: {setting}")
            
            # Validate security settings
            if config.SECRET_KEY == 'sql-analyzer-enterprise-2024-secure-key':
                print("⚠️ Using default secret key - change for production!")
            
            # Validate file size limits
            max_size_mb = config.MAX_CONTENT_LENGTH / (1024 * 1024)
            print(f"✅ Max file size: {max_size_mb:.0f}MB")
            
            # Validate export formats
            print(f"✅ Export formats: {len(config.EXPORT_FORMATS)} supported")
            
            self.deployment_steps.append(f"Configuration validation ({environment}): PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {str(e)}")
            return False
    
    def _initialize_database(self) -> bool:
        """Initialize database"""
        print("\n🗄️ Step 5: Database Initialization")
        
        try:
            from app.models.data_access import DatabaseManager
            
            # Initialize database
            db_manager = DatabaseManager()
            
            # Test database connection
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                print(f"✅ Database initialized with {table_count} tables")
            
            db_manager.close_all_connections()
            
            self.deployment_steps.append("Database initialization: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            return False
    
    def _validate_core_components(self) -> bool:
        """Validate core components"""
        print("\n🔧 Step 6: Core Components Validation")
        
        try:
            # Test analysis service
            from app.services.analysis_service import AnalysisService
            analysis_service = AnalysisService()
            print("✅ Analysis service initialized")
            
            # Test controller
            from app.controllers.analysis_controller import AnalysisController
            controller = AnalysisController()
            print("✅ Analysis controller initialized")
            
            # Test validator
            from app.utils.validation import EnterpriseValidator
            validator = EnterpriseValidator()
            print("✅ Enterprise validator initialized")
            
            # Test quality engine
            from app.services.business_logic import QualityAssessmentEngine
            quality_engine = QualityAssessmentEngine()
            print("✅ Quality assessment engine initialized")
            
            # Cleanup
            analysis_service.shutdown()
            
            self.deployment_steps.append("Core components validation: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Core components validation failed: {str(e)}")
            return False
    
    def _validate_performance(self) -> bool:
        """Validate performance requirements"""
        print("\n⚡ Step 7: Performance Validation")
        
        try:
            from io import BytesIO
            from app.services.analysis_service import AnalysisService
            
            # Test SQL content
            test_sql = """
            SELECT u.id, u.name, u.email
            FROM users u
            WHERE u.is_active = TRUE
            ORDER BY u.created_at DESC
            LIMIT 10;
            """
            
            # Performance test
            analysis_service = AnalysisService()
            test_file = BytesIO(test_sql.encode('utf-8'))
            test_file.filename = 'performance_test.sql'
            
            start_time = time.time()
            result = analysis_service.analyze_sql_file(test_file, 'performance_test.sql')
            processing_time = time.time() - start_time
            
            if result['success'] and processing_time < 2.0:
                print(f"✅ Performance test passed: {processing_time:.3f}s")
                self.validation_results['performance_time'] = processing_time
            else:
                print(f"❌ Performance test failed: {processing_time:.3f}s (target: <2.0s)")
                return False
            
            analysis_service.shutdown()
            
            self.deployment_steps.append("Performance validation: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Performance validation failed: {str(e)}")
            return False
    
    def _validate_security(self) -> bool:
        """Validate security requirements"""
        print("\n🛡️ Step 8: Security Validation")
        
        try:
            from app.utils.validation import EnterpriseValidator
            
            validator = EnterpriseValidator()
            
            # Test malicious content detection
            malicious_content = "SELECT * FROM users; <script>alert('xss')</script>"
            validation_result = validator.validate_content(malicious_content)
            
            if not validation_result.is_valid:
                print("✅ Malicious content detection working")
            else:
                print("❌ Malicious content detection failed")
                return False
            
            # Test file validation
            from io import BytesIO
            test_file = BytesIO(b"SELECT * FROM users;")
            test_file.filename = 'test.sql'
            
            file_validation = validator.validate_file_upload(test_file, 'test.sql')
            if file_validation.is_valid:
                print("✅ File validation working")
            else:
                print("❌ File validation failed")
                return False
            
            self.deployment_steps.append("Security validation: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Security validation failed: {str(e)}")
            return False
    
    def _start_application(self, environment: str) -> bool:
        """Start application"""
        print(f"\n🌐 Step 9: Application Startup ({environment})")
        
        try:
            from app import create_app
            
            # Create application
            app = create_app(environment)
            
            # Test application creation
            if app:
                print("✅ Application created successfully")
                print(f"✅ Debug mode: {app.config['DEBUG']}")
                print(f"✅ Environment: {environment}")
                
                # Test route registration
                routes = [rule.rule for rule in app.url_map.iter_rules()]
                print(f"✅ Routes registered: {len(routes)}")
                
                self.deployment_steps.append(f"Application startup ({environment}): PASSED")
                return True
            else:
                print("❌ Application creation failed")
                return False
                
        except Exception as e:
            print(f"❌ Application startup failed: {str(e)}")
            return False
    
    def _post_deployment_validation(self) -> bool:
        """Post-deployment validation"""
        print("\n✅ Step 10: Post-deployment Validation")
        
        try:
            # Validate all components are working together
            from app import create_app
            from app.services.analysis_service import AnalysisService
            
            # Create app and test basic functionality
            app = create_app('production')
            
            with app.app_context():
                # Test service metrics
                analysis_service = AnalysisService()
                metrics = analysis_service.get_service_metrics()
                
                print("✅ Service metrics available")
                print(f"   - Cache hit rate: {metrics['cache_stats']['hit_rate']:.1f}%")
                print(f"   - Database connections: {metrics['database_stats']['connection_count']}")
                
                analysis_service.shutdown()
            
            self.deployment_steps.append("Post-deployment validation: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Post-deployment validation failed: {str(e)}")
            return False
    
    def _generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        print("\n📊 Step 11: Deployment Report Generation")
        
        deployment_time = datetime.now() - self.deployment_start_time
        
        report = {
            'deployment_info': {
                'application': APP_METADATA['name'],
                'version': APP_METADATA['version'],
                'deployment_time': self.deployment_start_time.isoformat(),
                'duration': str(deployment_time),
                'success': True
            },
            'validation_results': self.validation_results,
            'deployment_steps': self.deployment_steps,
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }
        
        # Save report
        report_filename = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✅ Deployment report saved: {report_filename}")
            
            # Print summary
            print("\n📋 DEPLOYMENT SUMMARY:")
            print(f"   Duration: {deployment_time}")
            print(f"   Steps completed: {len(self.deployment_steps)}")
            if 'performance_time' in self.validation_results:
                print(f"   Performance: {self.validation_results['performance_time']:.3f}s")
            print(f"   Report: {report_filename}")
            
        except Exception as e:
            print(f"⚠️ Could not save deployment report: {str(e)}")

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enterprise SQL Analyzer Deployment')
    parser.add_argument('--environment', '-e', default='production',
                       choices=['development', 'production', 'testing'],
                       help='Deployment environment')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip comprehensive testing (not recommended)')
    
    args = parser.parse_args()
    
    # Create deployment manager
    deployment = EnterpriseDeployment()
    
    # Execute deployment
    success = deployment.deploy(args.environment)
    
    if success:
        print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("🚀 Your enterprise SQL analyzer is ready for production use!")
        sys.exit(0)
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("🔧 Please review the errors above and try again.")
        sys.exit(1)

if __name__ == '__main__':
    main()
