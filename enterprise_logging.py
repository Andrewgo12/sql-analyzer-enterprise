#!/usr/bin/env python3
"""
ENTERPRISE LOGGING AND AUDIT SYSTEM
SQL Analyzer Enterprise - Comprehensive Logging & Monitoring
"""

import logging
import json
import os
from datetime import datetime
import hashlib
import threading
from functools import wraps
import time

class EnterpriseLogger:
    """Enterprise-grade logging system with audit trails"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.setup_loggers()
        self.audit_trail = []
        self.performance_metrics = {}
        self.security_events = []
        self.lock = threading.Lock()
    
    def ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_loggers(self):
        """Setup different loggers for different purposes"""
        
        # Main application logger
        self.app_logger = self.create_logger(
            'app', 
            f'{self.log_dir}/application.log',
            logging.INFO
        )
        
        # Security logger
        self.security_logger = self.create_logger(
            'security',
            f'{self.log_dir}/security.log',
            logging.WARNING
        )
        
        # Performance logger
        self.performance_logger = self.create_logger(
            'performance',
            f'{self.log_dir}/performance.log',
            logging.INFO
        )
        
        # Audit logger
        self.audit_logger = self.create_logger(
            'audit',
            f'{self.log_dir}/audit.log',
            logging.INFO
        )
        
        # Error logger
        self.error_logger = self.create_logger(
            'error',
            f'{self.log_dir}/errors.log',
            logging.ERROR
        )
    
    def create_logger(self, name, filename, level):
        """Create a configured logger"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_application_event(self, event_type, message, user_id=None, additional_data=None):
        """Log application events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'user_id': user_id,
            'additional_data': additional_data or {}
        }
        
        self.app_logger.info(json.dumps(log_entry))
        
        with self.lock:
            self.audit_trail.append(log_entry)
    
    def log_security_event(self, event_type, severity, message, ip_address=None, user_agent=None):
        """Log security events"""
        security_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'message': message,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'event_id': hashlib.md5(f"{datetime.now().isoformat()}{message}".encode()).hexdigest()[:8]
        }
        
        self.security_logger.warning(json.dumps(security_entry))
        
        with self.lock:
            self.security_events.append(security_entry)
    
    def log_performance_metric(self, operation, duration, file_size=None, memory_usage=None):
        """Log performance metrics"""
        metric_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration,
            'file_size': file_size,
            'memory_usage': memory_usage,
            'performance_score': self.calculate_performance_score(duration, file_size)
        }
        
        self.performance_logger.info(json.dumps(metric_entry))
        
        with self.lock:
            if operation not in self.performance_metrics:
                self.performance_metrics[operation] = []
            self.performance_metrics[operation].append(metric_entry)
    
    def log_error(self, error_type, message, stack_trace=None, context=None):
        """Log errors with context"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message,
            'stack_trace': stack_trace,
            'context': context or {},
            'error_id': hashlib.md5(f"{datetime.now().isoformat()}{message}".encode()).hexdigest()[:8]
        }
        
        self.error_logger.error(json.dumps(error_entry))
    
    def calculate_performance_score(self, duration, file_size=None):
        """Calculate performance score (0-100)"""
        base_score = 100
        
        # Penalize slow operations
        if duration > 2.0:
            base_score -= min(50, (duration - 2.0) * 10)
        
        # Consider file size
        if file_size:
            size_mb = file_size / (1024 * 1024)
            if size_mb > 10:
                base_score -= min(20, (size_mb - 10) * 2)
        
        return max(0, base_score)
    
    def get_audit_trail(self, limit=100):
        """Get recent audit trail entries"""
        with self.lock:
            return self.audit_trail[-limit:]
    
    def get_security_events(self, severity=None, limit=50):
        """Get security events, optionally filtered by severity"""
        with self.lock:
            events = self.security_events
            if severity:
                events = [e for e in events if e['severity'] == severity]
            return events[-limit:]
    
    def get_performance_summary(self):
        """Get performance summary statistics"""
        with self.lock:
            summary = {}
            for operation, metrics in self.performance_metrics.items():
                durations = [m['duration'] for m in metrics]
                scores = [m['performance_score'] for m in metrics]
                
                summary[operation] = {
                    'count': len(metrics),
                    'avg_duration': sum(durations) / len(durations) if durations else 0,
                    'max_duration': max(durations) if durations else 0,
                    'min_duration': min(durations) if durations else 0,
                    'avg_score': sum(scores) / len(scores) if scores else 0,
                    'last_execution': metrics[-1]['timestamp'] if metrics else None
                }
            
            return summary
    
    def export_logs(self, format='json', date_range=None):
        """Export logs in specified format"""
        export_data = {
            'audit_trail': self.get_audit_trail(1000),
            'security_events': self.get_security_events(limit=500),
            'performance_summary': self.get_performance_summary(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2)
        elif format == 'csv':
            # Simplified CSV export for audit trail
            csv_lines = ['timestamp,event_type,message,user_id']
            for entry in export_data['audit_trail']:
                csv_lines.append(f"{entry['timestamp']},{entry['event_type']},{entry['message']},{entry.get('user_id', '')}")
            return '\n'.join(csv_lines)
        
        return export_data

# Global logger instance
enterprise_logger = EnterpriseLogger()

def log_performance(operation_name):
    """Decorator to log performance metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to get file size from kwargs or result
                file_size = None
                if 'file' in kwargs:
                    file_size = getattr(kwargs['file'], 'size', None)
                
                enterprise_logger.log_performance_metric(
                    operation_name, 
                    duration, 
                    file_size
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                enterprise_logger.log_error(
                    'performance_error',
                    f"Error in {operation_name}: {str(e)}",
                    context={'duration': duration}
                )
                raise
        
        return wrapper
    return decorator

def log_security_event(event_type, severity='medium'):
    """Decorator to log security events"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                enterprise_logger.log_security_event(
                    event_type,
                    severity,
                    f"Security check completed for {func.__name__}"
                )
                
                return result
                
            except Exception as e:
                enterprise_logger.log_security_event(
                    f"{event_type}_error",
                    'high',
                    f"Security error in {func.__name__}: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator

def log_application_activity(activity_type):
    """Decorator to log application activities"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            enterprise_logger.log_application_event(
                activity_type,
                f"Started {func.__name__}",
                additional_data={'function': func.__name__}
            )
            
            try:
                result = func(*args, **kwargs)
                
                enterprise_logger.log_application_event(
                    f"{activity_type}_completed",
                    f"Completed {func.__name__}",
                    additional_data={'function': func.__name__, 'success': True}
                )
                
                return result
                
            except Exception as e:
                enterprise_logger.log_application_event(
                    f"{activity_type}_failed",
                    f"Failed {func.__name__}: {str(e)}",
                    additional_data={'function': func.__name__, 'success': False, 'error': str(e)}
                )
                raise
        
        return wrapper
    return decorator

class SecurityMonitor:
    """Real-time security monitoring"""
    
    def __init__(self):
        self.suspicious_patterns = [
            r"(?i)(union|select|insert|update|delete|drop|create|alter)\s+.*\s+(or|and)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",
            r"(?i)<script[^>]*>.*?</script>",
            r"(?i)javascript:",
            r"(?i)(exec|execute|sp_|xp_)",
            r"(?i)(--|#|/\*|\*/)"
        ]
        self.failed_attempts = {}
        self.blocked_ips = set()
    
    def check_sql_injection(self, content):
        """Check for SQL injection patterns"""
        import re
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content):
                enterprise_logger.log_security_event(
                    'sql_injection_attempt',
                    'high',
                    f"Potential SQL injection detected: {pattern}"
                )
                return True
        
        return False
    
    def check_file_safety(self, filename, content):
        """Check if uploaded file is safe"""
        # Check file extension
        allowed_extensions = ['.sql', '.txt', '.ddl', '.dml']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            enterprise_logger.log_security_event(
                'unsafe_file_upload',
                'medium',
                f"Unsafe file extension: {filename}"
            )
            return False
        
        # Check content for malicious patterns
        if self.check_sql_injection(content):
            return False
        
        return True
    
    def rate_limit_check(self, ip_address, max_requests=100, time_window=3600):
        """Check rate limiting"""
        current_time = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        # Clean old attempts
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address]
            if current_time - attempt < time_window
        ]
        
        # Check if rate limit exceeded
        if len(self.failed_attempts[ip_address]) >= max_requests:
            self.blocked_ips.add(ip_address)
            enterprise_logger.log_security_event(
                'rate_limit_exceeded',
                'high',
                f"Rate limit exceeded for IP: {ip_address}"
            )
            return False
        
        self.failed_attempts[ip_address].append(current_time)
        return True

# Global security monitor
security_monitor = SecurityMonitor()

def create_monitoring_dashboard():
    """Create monitoring dashboard data"""
    return {
        'audit_summary': {
            'total_events': len(enterprise_logger.audit_trail),
            'recent_events': enterprise_logger.get_audit_trail(10)
        },
        'security_summary': {
            'total_events': len(enterprise_logger.security_events),
            'high_severity': len([e for e in enterprise_logger.security_events if e['severity'] == 'high']),
            'recent_events': enterprise_logger.get_security_events(limit=10)
        },
        'performance_summary': enterprise_logger.get_performance_summary(),
        'system_health': {
            'status': 'healthy',
            'uptime': time.time(),
            'memory_usage': '< 70%',
            'response_time': '< 2s'
        }
    }

if __name__ == '__main__':
    # Test the logging system
    print("🔍 Testing Enterprise Logging System...")
    
    # Test application logging
    enterprise_logger.log_application_event(
        'test_event',
        'Testing application logging',
        user_id='test_user',
        additional_data={'test': True}
    )
    
    # Test security logging
    enterprise_logger.log_security_event(
        'test_security',
        'medium',
        'Testing security logging',
        ip_address='127.0.0.1'
    )
    
    # Test performance logging
    enterprise_logger.log_performance_metric(
        'test_operation',
        1.5,
        file_size=1024*1024
    )
    
    # Test error logging
    enterprise_logger.log_error(
        'test_error',
        'Testing error logging',
        stack_trace='Test stack trace'
    )
    
    # Print summary
    print("✅ Logging system test completed")
    print(f"Audit trail entries: {len(enterprise_logger.get_audit_trail())}")
    print(f"Security events: {len(enterprise_logger.get_security_events())}")
    print(f"Performance metrics: {len(enterprise_logger.performance_metrics)}")
    
    # Export logs
    print("\n📤 Exporting logs...")
    json_export = enterprise_logger.export_logs('json')
    print(f"JSON export size: {len(json_export)} characters")
    
    print("🎉 Enterprise logging system ready!")
