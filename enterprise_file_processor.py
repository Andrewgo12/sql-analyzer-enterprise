#!/usr/bin/env python3
"""
ENTERPRISE FILE PROCESSOR
High-performance file processing for large SQL files (100MB+)
"""

import os
import mmap
import hashlib
import chardet
import time
import threading
from typing import Dict, List, Any, Optional, Generator
from dataclasses import dataclass
import logging
import tempfile
import shutil

@dataclass
class FileInfo:
    """File information structure"""
    filename: str
    size: int
    encoding: str
    line_count: int
    hash_md5: str
    hash_sha256: str
    processing_time: float
    is_valid: bool
    error_message: Optional[str] = None

class EnterpriseFileProcessor:
    """High-performance file processor for large SQL files"""
    
    def __init__(self, max_file_size: int = 100 * 1024 * 1024):  # 100MB default
        self.max_file_size = max_file_size
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {'.sql', '.txt', '.ddl', '.dml', '.psql', '.mysql', '.oracle'}
        self.chunk_size = 8192  # 8KB chunks for reading
        self.temp_dir = tempfile.gettempdir()
        
        # Security patterns to detect malicious content
        self.malicious_patterns = [
            b'<script',
            b'javascript:',
            b'eval(',
            b'exec(',
            b'system(',
            b'shell_exec(',
            b'passthru(',
            b'file_get_contents(',
            b'file_put_contents(',
            b'fopen(',
            b'fwrite(',
            b'include(',
            b'require(',
            b'<?php',
            b'<%',
            b'<jsp:',
            b'<asp:',
        ]
    
    def process_file(self, file_obj, filename: str = None) -> Dict[str, Any]:
        """Process uploaded file with comprehensive validation and analysis"""
        start_time = time.time()
        
        try:
            # Extract filename if not provided
            if filename is None:
                filename = getattr(file_obj, 'filename', 'unknown.sql')
            
            # Validate file extension
            if not self._is_valid_extension(filename):
                return {
                    'success': False,
                    'error': f'Unsupported file extension. Supported: {", ".join(self.supported_extensions)}',
                    'filename': filename
                }
            
            # Read file content
            file_content = self._read_file_safely(file_obj)
            
            if file_content is None:
                return {
                    'success': False,
                    'error': 'Failed to read file content',
                    'filename': filename
                }
            
            # Validate file size
            file_size = len(file_content)
            if file_size > self.max_file_size:
                return {
                    'success': False,
                    'error': f'File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB',
                    'filename': filename,
                    'size': file_size
                }
            
            # Detect encoding
            encoding_info = chardet.detect(file_content)
            encoding = encoding_info.get('encoding', 'utf-8')
            confidence = encoding_info.get('confidence', 0)
            
            if confidence < 0.7:
                self.logger.warning(f"Low encoding confidence: {confidence}")
            
            # Decode content
            try:
                content_str = file_content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to utf-8 with error handling
                content_str = file_content.decode('utf-8', errors='replace')
                encoding = 'utf-8'
            
            # Security validation
            security_check = self._validate_security(file_content, content_str)
            if not security_check['is_safe']:
                return {
                    'success': False,
                    'error': f'Security validation failed: {security_check["reason"]}',
                    'filename': filename
                }
            
            # Calculate hashes
            md5_hash = hashlib.md5(file_content).hexdigest()
            sha256_hash = hashlib.sha256(file_content).hexdigest()
            
            # Count lines efficiently
            line_count = self._count_lines_efficiently(content_str)
            
            # Create file info
            file_info = FileInfo(
                filename=filename,
                size=file_size,
                encoding=encoding,
                line_count=line_count,
                hash_md5=md5_hash,
                hash_sha256=sha256_hash,
                processing_time=time.time() - start_time,
                is_valid=True
            )
            
            return {
                'success': True,
                'content': content_str,
                'file_info': file_info,
                'metadata': {
                    'encoding_confidence': confidence,
                    'security_validated': True,
                    'processing_time': file_info.processing_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"File processing error: {str(e)}")
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'filename': filename or 'unknown'
            }
    
    def process_large_file_streaming(self, file_obj, filename: str = None) -> Generator[Dict[str, Any], None, None]:
        """Process large files in streaming mode for memory efficiency"""
        try:
            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Copy uploaded file to temporary file
                shutil.copyfileobj(file_obj, temp_file)
            
            # Process file using memory mapping
            with open(temp_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    file_size = len(mmapped_file)
                    
                    # Yield file info first
                    yield {
                        'type': 'file_info',
                        'size': file_size,
                        'filename': filename or 'unknown.sql'
                    }
                    
                    # Process in chunks
                    chunk_size = 1024 * 1024  # 1MB chunks
                    processed_bytes = 0
                    
                    for i in range(0, file_size, chunk_size):
                        chunk = mmapped_file[i:i + chunk_size]
                        processed_bytes += len(chunk)
                        
                        # Decode chunk
                        try:
                            chunk_str = chunk.decode('utf-8', errors='replace')
                        except Exception as e:
                            yield {
                                'type': 'error',
                                'message': f'Decoding error at byte {i}: {str(e)}'
                            }
                            continue
                        
                        # Yield chunk data
                        yield {
                            'type': 'chunk',
                            'data': chunk_str,
                            'chunk_number': i // chunk_size + 1,
                            'progress': (processed_bytes / file_size) * 100,
                            'bytes_processed': processed_bytes
                        }
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            yield {
                'type': 'complete',
                'message': 'File processing completed successfully'
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'message': f'Streaming processing failed: {str(e)}'
            }
    
    def _read_file_safely(self, file_obj) -> Optional[bytes]:
        """Safely read file content with size limits"""
        try:
            # Reset file pointer
            file_obj.seek(0)
            
            # Read in chunks to avoid memory issues
            content = b''
            while True:
                chunk = file_obj.read(self.chunk_size)
                if not chunk:
                    break
                
                content += chunk
                
                # Check size limit
                if len(content) > self.max_file_size:
                    self.logger.warning(f"File exceeds size limit: {len(content)} bytes")
                    return None
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            return None
    
    def _is_valid_extension(self, filename: str) -> bool:
        """Check if file has valid extension"""
        if not filename:
            return False
        
        _, ext = os.path.splitext(filename.lower())
        return ext in self.supported_extensions
    
    def _validate_security(self, file_content: bytes, content_str: str) -> Dict[str, Any]:
        """Validate file content for security threats"""
        try:
            # Check for malicious binary patterns
            for pattern in self.malicious_patterns:
                if pattern in file_content:
                    return {
                        'is_safe': False,
                        'reason': f'Potentially malicious content detected: {pattern.decode("utf-8", errors="replace")}'
                    }
            
            # Check for suspicious SQL patterns
            suspicious_sql = [
                'xp_cmdshell',
                'sp_oacreate',
                'sp_oamethod',
                'openrowset',
                'opendatasource',
                'bulk insert',
                'load_file(',
                'into outfile',
                'into dumpfile'
            ]
            
            content_lower = content_str.lower()
            for pattern in suspicious_sql:
                if pattern in content_lower:
                    return {
                        'is_safe': False,
                        'reason': f'Potentially dangerous SQL function detected: {pattern}'
                    }
            
            # Check file size ratio (compressed vs uncompressed)
            if len(content_str.encode('utf-8')) / len(file_content) > 10:
                return {
                    'is_safe': False,
                    'reason': 'Suspicious compression ratio detected'
                }
            
            return {
                'is_safe': True,
                'reason': 'Content passed security validation'
            }
            
        except Exception as e:
            self.logger.error(f"Security validation error: {str(e)}")
            return {
                'is_safe': False,
                'reason': f'Security validation failed: {str(e)}'
            }
    
    def _count_lines_efficiently(self, content: str) -> int:
        """Efficiently count lines in content"""
        try:
            return content.count('\n') + (1 if content and not content.endswith('\n') else 0)
        except Exception:
            return 0
    
    def get_file_stats(self, content: str) -> Dict[str, Any]:
        """Get comprehensive file statistics"""
        try:
            lines = content.split('\n')
            
            # Basic stats
            stats = {
                'total_lines': len(lines),
                'non_empty_lines': len([line for line in lines if line.strip()]),
                'comment_lines': len([line for line in lines if line.strip().startswith('--')]),
                'total_characters': len(content),
                'total_words': len(content.split()),
                'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
            }
            
            # SQL-specific stats
            content_upper = content.upper()
            stats.update({
                'select_statements': content_upper.count('SELECT'),
                'insert_statements': content_upper.count('INSERT'),
                'update_statements': content_upper.count('UPDATE'),
                'delete_statements': content_upper.count('DELETE'),
                'create_statements': content_upper.count('CREATE'),
                'drop_statements': content_upper.count('DROP'),
                'alter_statements': content_upper.count('ALTER')
            })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating file stats: {str(e)}")
            return {}
    
    def validate_sql_syntax_basic(self, content: str) -> Dict[str, Any]:
        """Basic SQL syntax validation"""
        try:
            issues = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('--'):
                    continue
                
                # Check for unmatched quotes
                single_quotes = line_stripped.count("'") - line_stripped.count("\\'")
                double_quotes = line_stripped.count('"') - line_stripped.count('\\"')
                
                if single_quotes % 2 != 0:
                    issues.append({
                        'line': i,
                        'type': 'syntax_error',
                        'message': 'Unmatched single quote',
                        'content': line_stripped
                    })
                
                if double_quotes % 2 != 0:
                    issues.append({
                        'line': i,
                        'type': 'syntax_error',
                        'message': 'Unmatched double quote',
                        'content': line_stripped
                    })
                
                # Check for unmatched parentheses
                open_parens = line_stripped.count('(')
                close_parens = line_stripped.count(')')
                if open_parens != close_parens:
                    issues.append({
                        'line': i,
                        'type': 'syntax_warning',
                        'message': f'Unmatched parentheses: {open_parens} open, {close_parens} close',
                        'content': line_stripped
                    })
            
            return {
                'is_valid': len(issues) == 0,
                'issues': issues,
                'total_issues': len(issues)
            }
            
        except Exception as e:
            self.logger.error(f"Syntax validation error: {str(e)}")
            return {
                'is_valid': False,
                'issues': [{'line': 0, 'type': 'validation_error', 'message': str(e)}],
                'total_issues': 1
            }
    
    def create_backup(self, content: str, filename: str) -> str:
        """Create backup of processed file"""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{filename}_{timestamp}.backup"
            backup_path = os.path.join(self.temp_dir, backup_filename)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Backup creation error: {str(e)}")
            return ""
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.temp_dir):
                if filename.endswith('.backup') or filename.startswith('sql_analyzer_'):
                    file_path = os.path.join(self.temp_dir, filename)
                    
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getmtime(file_path)
                        
                        if file_age > max_age_seconds:
                            os.unlink(file_path)
                            self.logger.info(f"Cleaned up old temp file: {filename}")
            
        except Exception as e:
            self.logger.error(f"Temp file cleanup error: {str(e)}")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss': memory_info.rss,  # Resident Set Size
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available': psutil.virtual_memory().available
            }
        except ImportError:
            return {'error': 'psutil not available for memory monitoring'}
        except Exception as e:
            return {'error': str(e)}
