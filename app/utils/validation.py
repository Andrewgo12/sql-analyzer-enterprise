#!/usr/bin/env python3
"""
ENTERPRISE VALIDATION LAYER
Comprehensive validation with business rules and security checks
"""

import re
import os
import mimetypes
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass

from app.models.analysis_models import DatabaseType, ErrorSeverity
from app.utils.helpers import LoggingHelper

@dataclass
class ValidationRule:
    """Validation rule definition"""
    name: str
    description: str
    validator: callable
    error_message: str
    severity: ErrorSeverity = ErrorSeverity.MEDIUM

@dataclass
class ValidationResult:
    """Validation result with detailed information"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    passed_rules: List[str]
    failed_rules: List[str]
    validation_time: float

class EnterpriseValidator:
    """Enterprise-grade validation with comprehensive rule engine"""
    
    def __init__(self):
        self.logger = LoggingHelper.setup_logger('enterprise_validator')
        self._initialize_validation_rules()
    
    def _initialize_validation_rules(self):
        """Initialize comprehensive validation rules"""
        self.file_validation_rules = [
            ValidationRule(
                name="file_size_limit",
                description="File size must be within acceptable limits",
                validator=self._validate_file_size,
                error_message="File size exceeds maximum limit of 100MB",
                severity=ErrorSeverity.HIGH
            ),
            ValidationRule(
                name="file_extension",
                description="File must have valid SQL extension",
                validator=self._validate_file_extension,
                error_message="Invalid file extension. Allowed: .sql, .txt, .ddl, .dml",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                name="file_content_type",
                description="File content type must be text-based",
                validator=self._validate_content_type,
                error_message="Invalid content type. File must be text-based",
                severity=ErrorSeverity.HIGH
            ),
            ValidationRule(
                name="filename_security",
                description="Filename must not contain malicious patterns",
                validator=self._validate_filename_security,
                error_message="Filename contains potentially malicious characters",
                severity=ErrorSeverity.HIGH
            ),
            ValidationRule(
                name="file_encoding",
                description="File encoding must be supported",
                validator=self._validate_file_encoding,
                error_message="Unsupported file encoding detected",
                severity=ErrorSeverity.MEDIUM
            )
        ]
        
        self.content_validation_rules = [
            ValidationRule(
                name="content_length",
                description="Content length must be reasonable",
                validator=self._validate_content_length,
                error_message="Content is too large or empty",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                name="malicious_content",
                description="Content must not contain malicious patterns",
                validator=self._validate_malicious_content,
                error_message="Potentially malicious content detected",
                severity=ErrorSeverity.CRITICAL
            ),
            ValidationRule(
                name="sql_structure",
                description="Content must have basic SQL structure",
                validator=self._validate_sql_structure,
                error_message="Content does not appear to be valid SQL",
                severity=ErrorSeverity.LOW
            ),
            ValidationRule(
                name="encoding_consistency",
                description="Content encoding must be consistent",
                validator=self._validate_encoding_consistency,
                error_message="Inconsistent character encoding detected",
                severity=ErrorSeverity.MEDIUM
            )
        ]
        
        self.parameter_validation_rules = [
            ValidationRule(
                name="analysis_id_format",
                description="Analysis ID must be valid UUID format",
                validator=self._validate_analysis_id_format,
                error_message="Invalid analysis ID format",
                severity=ErrorSeverity.HIGH
            ),
            ValidationRule(
                name="database_type_valid",
                description="Database type must be supported",
                validator=self._validate_database_type,
                error_message="Unsupported database type",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                name="export_format_valid",
                description="Export format must be supported",
                validator=self._validate_export_format,
                error_message="Unsupported export format",
                severity=ErrorSeverity.MEDIUM
            ),
            ValidationRule(
                name="options_structure",
                description="Options must have valid structure",
                validator=self._validate_options_structure,
                error_message="Invalid options structure",
                severity=ErrorSeverity.LOW
            )
        ]
    
    def validate_file_upload(self, file_data: Any, filename: str, 
                           max_size: int = 100 * 1024 * 1024) -> ValidationResult:
        """Comprehensive file upload validation"""
        start_time = datetime.now()
        errors = []
        warnings = []
        passed_rules = []
        failed_rules = []
        
        try:
            # Prepare validation context
            context = {
                'file_data': file_data,
                'filename': filename,
                'max_size': max_size,
                'file_size': self._get_file_size(file_data),
                'content_sample': self._get_content_sample(file_data)
            }
            
            # Run file validation rules
            for rule in self.file_validation_rules:
                try:
                    is_valid, details = rule.validator(context)
                    
                    if is_valid:
                        passed_rules.append(rule.name)
                    else:
                        failed_rules.append(rule.name)
                        
                        error_info = {
                            'rule': rule.name,
                            'message': rule.error_message,
                            'severity': rule.severity.value,
                            'details': details,
                            'description': rule.description
                        }
                        
                        if rule.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                            errors.append(error_info)
                        else:
                            warnings.append(error_info)
                
                except Exception as e:
                    self.logger.error(f"Validation rule {rule.name} failed: {str(e)}")
                    failed_rules.append(rule.name)
                    errors.append({
                        'rule': rule.name,
                        'message': f"Validation error: {str(e)}",
                        'severity': 'high',
                        'details': {'exception': str(e)}
                    })
            
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                validation_time=validation_time
            )
            
        except Exception as e:
            self.logger.error(f"File validation failed: {str(e)}")
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=False,
                errors=[{
                    'rule': 'validation_system',
                    'message': f"Validation system error: {str(e)}",
                    'severity': 'critical',
                    'details': {'exception': str(e)}
                }],
                warnings=[],
                passed_rules=[],
                failed_rules=['validation_system'],
                validation_time=validation_time
            )
    
    def validate_content(self, content: str, filename: str = None) -> ValidationResult:
        """Comprehensive content validation"""
        start_time = datetime.now()
        errors = []
        warnings = []
        passed_rules = []
        failed_rules = []
        
        try:
            # Prepare validation context
            context = {
                'content': content,
                'filename': filename,
                'content_length': len(content),
                'line_count': content.count('\n') + 1 if content else 0
            }
            
            # Run content validation rules
            for rule in self.content_validation_rules:
                try:
                    is_valid, details = rule.validator(context)
                    
                    if is_valid:
                        passed_rules.append(rule.name)
                    else:
                        failed_rules.append(rule.name)
                        
                        error_info = {
                            'rule': rule.name,
                            'message': rule.error_message,
                            'severity': rule.severity.value,
                            'details': details,
                            'description': rule.description
                        }
                        
                        if rule.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                            errors.append(error_info)
                        else:
                            warnings.append(error_info)
                
                except Exception as e:
                    self.logger.error(f"Content validation rule {rule.name} failed: {str(e)}")
                    failed_rules.append(rule.name)
                    errors.append({
                        'rule': rule.name,
                        'message': f"Content validation error: {str(e)}",
                        'severity': 'high',
                        'details': {'exception': str(e)}
                    })
            
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                validation_time=validation_time
            )
            
        except Exception as e:
            self.logger.error(f"Content validation failed: {str(e)}")
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=False,
                errors=[{
                    'rule': 'content_validation_system',
                    'message': f"Content validation system error: {str(e)}",
                    'severity': 'critical',
                    'details': {'exception': str(e)}
                }],
                warnings=[],
                passed_rules=[],
                failed_rules=['content_validation_system'],
                validation_time=validation_time
            )
    
    def validate_parameters(self, params: Dict[str, Any]) -> ValidationResult:
        """Comprehensive parameter validation"""
        start_time = datetime.now()
        errors = []
        warnings = []
        passed_rules = []
        failed_rules = []
        
        try:
            # Prepare validation context
            context = {'params': params}
            
            # Run parameter validation rules
            for rule in self.parameter_validation_rules:
                try:
                    is_valid, details = rule.validator(context)
                    
                    if is_valid:
                        passed_rules.append(rule.name)
                    else:
                        failed_rules.append(rule.name)
                        
                        error_info = {
                            'rule': rule.name,
                            'message': rule.error_message,
                            'severity': rule.severity.value,
                            'details': details,
                            'description': rule.description
                        }
                        
                        if rule.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                            errors.append(error_info)
                        else:
                            warnings.append(error_info)
                
                except Exception as e:
                    self.logger.error(f"Parameter validation rule {rule.name} failed: {str(e)}")
                    failed_rules.append(rule.name)
                    errors.append({
                        'rule': rule.name,
                        'message': f"Parameter validation error: {str(e)}",
                        'severity': 'high',
                        'details': {'exception': str(e)}
                    })
            
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                validation_time=validation_time
            )
            
        except Exception as e:
            self.logger.error(f"Parameter validation failed: {str(e)}")
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=False,
                errors=[{
                    'rule': 'parameter_validation_system',
                    'message': f"Parameter validation system error: {str(e)}",
                    'severity': 'critical',
                    'details': {'exception': str(e)}
                }],
                warnings=[],
                passed_rules=[],
                failed_rules=['parameter_validation_system'],
                validation_time=validation_time
            )
    
    # File validation rule implementations
    def _validate_file_size(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate file size"""
        file_size = context.get('file_size', 0)
        max_size = context.get('max_size', 100 * 1024 * 1024)
        
        is_valid = 0 < file_size <= max_size
        details = {
            'file_size': file_size,
            'max_size': max_size,
            'size_mb': file_size / (1024 * 1024)
        }
        
        return is_valid, details
    
    def _validate_file_extension(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate file extension"""
        filename = context.get('filename', '')
        allowed_extensions = {'.sql', '.txt', '.ddl', '.dml', '.psql', '.mysql', '.oracle'}
        
        if not filename:
            return False, {'error': 'No filename provided'}
        
        _, ext = os.path.splitext(filename.lower())
        is_valid = ext in allowed_extensions
        
        details = {
            'extension': ext,
            'allowed_extensions': list(allowed_extensions),
            'filename': filename
        }
        
        return is_valid, details
    
    def _validate_content_type(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate content type"""
        filename = context.get('filename', '')
        
        if not filename:
            return True, {'note': 'No filename to check content type'}
        
        content_type, _ = mimetypes.guess_type(filename)
        is_valid = content_type is None or content_type.startswith('text/')
        
        details = {
            'content_type': content_type,
            'filename': filename
        }
        
        return is_valid, details
    
    def _validate_filename_security(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate filename for security issues"""
        filename = context.get('filename', '')
        
        # Check for malicious patterns
        malicious_patterns = [
            r'\.\./',  # Directory traversal
            r'[<>:"|?*]',  # Invalid filename characters
            r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Windows reserved names
            r'^\.',  # Hidden files
            r'[^\x20-\x7E]'  # Non-printable characters
        ]
        
        issues = []
        for pattern in malicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                issues.append(f"Matches pattern: {pattern}")
        
        is_valid = len(issues) == 0
        details = {
            'filename': filename,
            'issues': issues,
            'patterns_checked': len(malicious_patterns)
        }
        
        return is_valid, details
    
    def _validate_file_encoding(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate file encoding"""
        content_sample = context.get('content_sample', b'')
        
        if not content_sample:
            return True, {'note': 'No content to validate encoding'}
        
        # Try to decode with common encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        valid_encodings = []
        
        for encoding in encodings:
            try:
                content_sample.decode(encoding)
                valid_encodings.append(encoding)
            except UnicodeDecodeError:
                continue
        
        is_valid = len(valid_encodings) > 0
        details = {
            'valid_encodings': valid_encodings,
            'sample_size': len(content_sample)
        }
        
        return is_valid, details
    
    # Content validation rule implementations
    def _validate_content_length(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate content length"""
        content_length = context.get('content_length', 0)
        min_length = 10  # Minimum reasonable SQL content
        max_length = 50 * 1024 * 1024  # 50MB text content
        
        is_valid = min_length <= content_length <= max_length
        details = {
            'content_length': content_length,
            'min_length': min_length,
            'max_length': max_length
        }
        
        return is_valid, details
    
    def _validate_malicious_content(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate content for malicious patterns"""
        content = context.get('content', '')
        
        # Malicious patterns to detect
        malicious_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'eval\s*\(',  # Eval functions
            r'exec\s*\(',  # Exec functions
            r'system\s*\(',  # System calls
            r'xp_cmdshell',  # SQL Server command shell
            r'sp_oacreate',  # SQL Server OLE automation
            r'load_file\s*\(',  # MySQL file loading
            r'into\s+outfile',  # MySQL file writing
        ]
        
        detected_patterns = []
        for pattern in malicious_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                detected_patterns.append({
                    'pattern': pattern,
                    'matches': len(matches),
                    'examples': matches[:3]  # First 3 matches
                })
        
        is_valid = len(detected_patterns) == 0
        details = {
            'detected_patterns': detected_patterns,
            'patterns_checked': len(malicious_patterns),
            'content_length': len(content)
        }
        
        return is_valid, details
    
    def _validate_sql_structure(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate basic SQL structure"""
        content = context.get('content', '')
        
        # Basic SQL keywords
        sql_keywords = [
            r'\bSELECT\b', r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b',
            r'\bCREATE\b', r'\bDROP\b', r'\bALTER\b', r'\bFROM\b',
            r'\bWHERE\b', r'\bJOIN\b', r'\bTABLE\b'
        ]
        
        found_keywords = []
        for keyword in sql_keywords:
            if re.search(keyword, content, re.IGNORECASE):
                found_keywords.append(keyword.strip('\\b'))
        
        # Consider it SQL if at least 2 keywords are found
        is_valid = len(found_keywords) >= 2
        details = {
            'found_keywords': found_keywords,
            'keyword_count': len(found_keywords),
            'content_length': len(content)
        }
        
        return is_valid, details
    
    def _validate_encoding_consistency(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate encoding consistency"""
        content = context.get('content', '')
        
        if not content:
            return True, {'note': 'No content to validate'}
        
        # Check for encoding issues
        issues = []
        
        # Check for replacement characters
        if '\ufffd' in content:
            issues.append('Contains Unicode replacement characters')
        
        # Check for mixed encoding patterns
        try:
            content.encode('utf-8')
        except UnicodeEncodeError as e:
            issues.append(f'UTF-8 encoding error: {str(e)}')
        
        is_valid = len(issues) == 0
        details = {
            'issues': issues,
            'content_length': len(content)
        }
        
        return is_valid, details
    
    # Parameter validation rule implementations
    def _validate_analysis_id_format(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate analysis ID format"""
        params = context.get('params', {})
        analysis_id = params.get('analysis_id')
        
        if not analysis_id:
            return True, {'note': 'No analysis ID to validate'}
        
        # UUID format validation
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        is_valid = bool(uuid_pattern.match(analysis_id))
        details = {
            'analysis_id': analysis_id,
            'format': 'UUID v4',
            'length': len(analysis_id)
        }
        
        return is_valid, details
    
    def _validate_database_type(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate database type"""
        params = context.get('params', {})
        db_type = params.get('database_type')
        
        if not db_type:
            return True, {'note': 'No database type to validate'}
        
        valid_types = [db_type.value for db_type in DatabaseType]
        is_valid = db_type in valid_types
        
        details = {
            'database_type': db_type,
            'valid_types': valid_types
        }
        
        return is_valid, details
    
    def _validate_export_format(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate export format"""
        params = context.get('params', {})
        export_format = params.get('export_format')
        
        if not export_format:
            return True, {'note': 'No export format to validate'}
        
        valid_formats = [
            'json', 'html', 'xml', 'csv', 'markdown', 'txt', 'sql',
            'mysql_dump', 'postgresql_backup', 'oracle_script', 'documentation'
        ]
        
        is_valid = export_format in valid_formats
        details = {
            'export_format': export_format,
            'valid_formats': valid_formats
        }
        
        return is_valid, details
    
    def _validate_options_structure(self, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate options structure"""
        params = context.get('params', {})
        options = params.get('options')
        
        if not options:
            return True, {'note': 'No options to validate'}
        
        if not isinstance(options, dict):
            return False, {'error': 'Options must be a dictionary'}
        
        # Validate known option keys
        valid_option_keys = {
            'database_type', 'auto_fix', 'intelligent_comments',
            'security_scan', 'performance_analysis', 'schema_analysis'
        }
        
        invalid_keys = set(options.keys()) - valid_option_keys
        
        is_valid = len(invalid_keys) == 0
        details = {
            'provided_keys': list(options.keys()),
            'valid_keys': list(valid_option_keys),
            'invalid_keys': list(invalid_keys)
        }
        
        return is_valid, details
    
    # Helper methods
    def _get_file_size(self, file_data: Any) -> int:
        """Get file size safely"""
        try:
            if hasattr(file_data, 'seek') and hasattr(file_data, 'tell'):
                current_pos = file_data.tell()
                file_data.seek(0, 2)  # Seek to end
                size = file_data.tell()
                file_data.seek(current_pos)  # Restore position
                return size
            elif hasattr(file_data, '__len__'):
                return len(file_data)
            else:
                return 0
        except Exception:
            return 0
    
    def _get_content_sample(self, file_data: Any, sample_size: int = 1024) -> bytes:
        """Get content sample safely"""
        try:
            if hasattr(file_data, 'read'):
                current_pos = file_data.tell() if hasattr(file_data, 'tell') else 0
                file_data.seek(0)
                sample = file_data.read(sample_size)
                if hasattr(file_data, 'seek'):
                    file_data.seek(current_pos)
                return sample if isinstance(sample, bytes) else sample.encode('utf-8')
            else:
                return b''
        except Exception:
            return b''
