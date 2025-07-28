#!/usr/bin/env python3
"""
UTILITY HELPERS
Common utility functions for the application
"""

import os
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

class FileHelper:
    """File handling utilities"""
    
    @staticmethod
    def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
        """Check if file has allowed extension"""
        if not filename:
            return False
        
        return '.' in filename and \
               '.' + filename.rsplit('.', 1)[1].lower() in {ext.lstrip('.') for ext in allowed_extensions}
    
    @staticmethod
    def secure_filename_with_timestamp(filename: str) -> str:
        """Generate secure filename with timestamp"""
        if not filename:
            return f"file_{int(time.time())}"
        
        name, ext = os.path.splitext(secure_filename(filename))
        timestamp = int(time.time())
        return f"{name}_{timestamp}{ext}"
    
    @staticmethod
    def calculate_file_hash(content: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """Calculate file hash"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if algorithm == 'md5':
            return hashlib.md5(content).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(content).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(content).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

class TimeHelper:
    """Time and date utilities"""

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def get_relative_time(timestamp: datetime) -> str:
        """Get relative time description"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """Format timestamp in ISO format"""
        return timestamp.isoformat()
    
    @staticmethod
    def format_timestamp(timestamp, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format timestamp"""
        from datetime import datetime
        if isinstance(timestamp, str):
            try:
                # Try to parse string timestamp
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return timestamp  # Return as-is if can't parse
        elif not isinstance(timestamp, datetime):
            return str(timestamp)  # Convert to string if not datetime
        return timestamp.strftime(format_str)

class ValidationHelper:
    """Validation utilities"""
    
    @staticmethod
    def validate_analysis_id(analysis_id: str) -> bool:
        """Validate analysis ID format"""
        if not analysis_id:
            return False
        
        # Check if it's a valid UUID-like string
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        return bool(uuid_pattern.match(analysis_id))
    
    @staticmethod
    def validate_export_format(format_type: str, allowed_formats: List[str]) -> bool:
        """Validate export format"""
        return format_type in allowed_formats
    
    @staticmethod
    def validate_database_type(db_type: str, allowed_types: List[str]) -> bool:
        """Validate database type"""
        return db_type in allowed_types
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        import re
        sanitized = re.sub(r'[<>"\']', '', input_str)
        
        # Limit length
        return sanitized[:max_length]

class ResponseHelper:
    """Response formatting utilities"""
    
    @staticmethod
    def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Create success response"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if data is not None:
            response['data'] = data
        
        return response
    
    @staticmethod
    def error_response(error: str, error_code: str = "GENERAL_ERROR", status_code: int = 400) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error,
            'error_code': error_code,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def paginated_response(data: List[Any], page: int, per_page: int, total: int) -> Dict[str, Any]:
        """Create paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'timestamp': datetime.now().isoformat()
        }

class LoggingHelper:
    """Logging utilities"""
    
    @staticmethod
    def setup_logger(name: str, level: str = 'INFO', log_file: str = None) -> logging.Logger:
        """Setup logger with proper configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def log_performance(logger: logging.Logger, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        message = f"Performance: {operation} completed in {TimeHelper.format_duration(duration)}"
        
        if details:
            message += f" - Details: {details}"
        
        if duration > 5.0:
            logger.warning(message)
        elif duration > 2.0:
            logger.info(message)
        else:
            logger.debug(message)

class SecurityHelper:
    """Security utilities"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return token == session_token
    
    @staticmethod
    def sanitize_sql_content(content: str) -> str:
        """Basic SQL content sanitization"""
        if not content:
            return ""
        
        # Remove potentially dangerous SQL commands for display
        dangerous_patterns = [
            r'(?i)\bDROP\s+DATABASE\b',
            r'(?i)\bDROP\s+SCHEMA\b',
            r'(?i)\bSHUTDOWN\b',
            r'(?i)\bxp_cmdshell\b'
        ]
        
        import re
        sanitized = content
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '[DANGEROUS_COMMAND_REMOVED]', sanitized)
        
        return sanitized

class CacheHelper:
    """Caching utilities"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        return self._cache.get(key, default)
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL"""
        self._cache[key] = value
        self._timestamps[key] = time.time() + ttl
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear_expired(self) -> None:
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._timestamps.items()
            if current_time > expiry
        ]
        
        for key in expired_keys:
            self.delete(key)
    
    def clear_all(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()

class ConfigHelper:
    """Configuration utilities"""
    
    @staticmethod
    def get_env_var(name: str, default: Any = None, var_type: type = str) -> Any:
        """Get environment variable with type conversion"""
        value = os.environ.get(name, default)
        
        if value is None:
            return default
        
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            try:
                return int(value)
            except ValueError:
                return default
        elif var_type == float:
            try:
                return float(value)
            except ValueError:
                return default
        else:
            return value
    
    @staticmethod
    def validate_config(config: Dict[str, Any], required_keys: List[str]) -> List[str]:
        """Validate configuration and return missing keys"""
        missing_keys = []
        
        for key in required_keys:
            if key not in config or config[key] is None:
                missing_keys.append(key)
        
        return missing_keys

# Global cache instance
cache = CacheHelper()
