#!/usr/bin/env python3
"""
ENTERPRISE FILE PROCESSOR - ADVANCED SQL FILE HANDLING
High-performance file processing with streaming, validation, and analysis
"""

import os
import re
import time
import hashlib
import mimetypes
import tempfile
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from datetime import datetime

class EnterpriseFileProcessor:
    """Enterprise-grade file processor for SQL files with advanced capabilities"""
    
    def __init__(self):
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.chunk_size = 8192  # 8KB chunks for streaming
        self.allowed_extensions = {'.sql', '.txt', '.ddl', '.dml'}
        self.allowed_mime_types = {
            'text/plain',
            'application/sql',
            'text/x-sql',
            'application/x-sql'
        }
        
    def process_file(self, file_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Process uploaded file with comprehensive analysis"""
        start_time = time.time()
        
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            # Validate file
            if progress_callback:
                progress_callback(10, "Validating file...")
            
            validation_result = self.validate_file(file_path)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Read file content with progress
            if progress_callback:
                progress_callback(30, "Reading file content...")
            
            content_result = self.read_file_content_with_progress(file_path, progress_callback)
            if not content_result['success']:
                return {'success': False, 'error': content_result['error']}
            
            content = content_result['content']
            
            # Generate file metadata
            if progress_callback:
                progress_callback(80, "Generating metadata...")
            
            metadata = self.generate_comprehensive_metadata(file_path, content)
            
            # Perform content analysis
            if progress_callback:
                progress_callback(90, "Analyzing content...")
            
            content_analysis = self.analyze_sql_content(content)
            
            if progress_callback:
                progress_callback(100, "Processing complete!")
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'content': content,
                'metadata': metadata,
                'content_analysis': content_analysis,
                'processing_time': round(processing_time, 3),
                'file_hash': metadata['hash_md5']
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Processing error: {str(e)}'}
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Enhanced file validation with security checks"""
        try:
            file_path = Path(file_path)
            
            # Check if file exists and is a file
            if not file_path.exists():
                return {'valid': False, 'error': 'File does not exist'}
            
            if not file_path.is_file():
                return {'valid': False, 'error': 'Path is not a file'}
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                return {'valid': False, 'error': 'File is empty'}
            
            if file_size > self.max_file_size:
                size_mb = self.max_file_size / (1024*1024)
                return {'valid': False, 'error': f'File too large. Maximum size: {size_mb:.0f}MB'}
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                allowed = ", ".join(self.allowed_extensions)
                return {'valid': False, 'error': f'Invalid file type. Allowed: {allowed}'}
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type not in self.allowed_mime_types:
                return {'valid': False, 'error': f'Invalid MIME type: {mime_type}'}
            
            # Basic content validation (check if it's text)
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(1024)
                    if b'\x00' in sample:
                        return {'valid': False, 'error': 'File appears to be binary, not text'}
            except Exception:
                return {'valid': False, 'error': 'Cannot read file for validation'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def read_file_content_with_progress(self, file_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Read file content with progress tracking and encoding detection"""
        try:
            file_size = os.path.getsize(file_path)
            content_parts = []
            bytes_read = 0
            
            # Try different encodings
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding, buffering=self.chunk_size) as f:
                        while True:
                            chunk = f.read(self.chunk_size)
                            if not chunk:
                                break
                            
                            content_parts.append(chunk)
                            bytes_read += len(chunk.encode(encoding))
                            
                            # Update progress
                            if progress_callback and file_size > 0:
                                progress = 30 + int((bytes_read / file_size) * 40)  # 30-70% range
                                progress_callback(min(progress, 70), f"Reading file... ({bytes_read}/{file_size} bytes)")
                    
                    content = ''.join(content_parts)
                    return {
                        'success': True,
                        'content': content,
                        'encoding': encoding,
                        'size': bytes_read
                    }
                    
                except UnicodeDecodeError:
                    content_parts.clear()
                    bytes_read = 0
                    continue
                except Exception as e:
                    return {'success': False, 'error': f'Error reading with {encoding}: {str(e)}'}
            
            return {'success': False, 'error': 'Could not decode file with any supported encoding'}
            
        except Exception as e:
            return {'success': False, 'error': f'File reading error: {str(e)}'}
    
    def generate_comprehensive_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Generate comprehensive file metadata"""
        file_path = Path(file_path)
        stat = file_path.stat()
        
        # Calculate hashes
        content_bytes = content.encode('utf-8')
        md5_hash = hashlib.md5(content_bytes).hexdigest()
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Analyze content structure
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith('--') or line.strip().startswith('/*')]
        
        return {
            'filename': file_path.name,
            'filepath': str(file_path),
            'size': stat.st_size,
            'size_human': self.format_file_size(stat.st_size),
            'extension': file_path.suffix.lower(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'processed': datetime.now().isoformat(),
            
            # Content metrics
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'comment_lines': len(comment_lines),
            'code_lines': len(non_empty_lines) - len(comment_lines),
            'character_count': len(content),
            'word_count': len(content.split()),
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            
            # Hashes
            'hash_md5': md5_hash,
            'hash_sha256': sha256_hash,
            
            # File type detection
            'mime_type': mimetypes.guess_type(str(file_path))[0],
            'is_sql_file': file_path.suffix.lower() in {'.sql', '.ddl', '.dml'},
            
            # Performance metrics
            'estimated_processing_time': self.estimate_processing_time(len(content)),
            'complexity_indicator': self.calculate_content_complexity(content)
        }
    
    def analyze_sql_content(self, content: str) -> Dict[str, Any]:
        """Analyze SQL content structure and characteristics"""
        try:
            content_upper = content.upper()
            
            # Count SQL statement types
            statement_counts = {
                'SELECT': content_upper.count('SELECT'),
                'INSERT': content_upper.count('INSERT'),
                'UPDATE': content_upper.count('UPDATE'),
                'DELETE': content_upper.count('DELETE'),
                'CREATE': content_upper.count('CREATE'),
                'DROP': content_upper.count('DROP'),
                'ALTER': content_upper.count('ALTER'),
                'GRANT': content_upper.count('GRANT'),
                'REVOKE': content_upper.count('REVOKE')
            }
            
            # Detect SQL features
            features = {
                'has_joins': 'JOIN' in content_upper,
                'has_subqueries': content_upper.count('SELECT') > 1,
                'has_functions': bool(re.search(r'\w+\(', content)),
                'has_procedures': 'PROCEDURE' in content_upper or 'FUNCTION' in content_upper,
                'has_triggers': 'TRIGGER' in content_upper,
                'has_views': 'VIEW' in content_upper,
                'has_indexes': 'INDEX' in content_upper,
                'has_transactions': 'BEGIN' in content_upper or 'COMMIT' in content_upper,
                'has_comments': '--' in content or '/*' in content
            }
            
            # Detect database engine hints
            engine_hints = []
            if 'AUTO_INCREMENT' in content_upper:
                engine_hints.append('MySQL')
            if 'SERIAL' in content_upper or 'NEXTVAL' in content_upper:
                engine_hints.append('PostgreSQL')
            if 'IDENTITY' in content_upper or 'NVARCHAR' in content_upper:
                engine_hints.append('SQL Server')
            if 'ROWNUM' in content_upper or 'DUAL' in content_upper:
                engine_hints.append('Oracle')
            
            # Calculate complexity metrics
            complexity_score = self.calculate_sql_complexity(content)
            
            return {
                'statement_counts': statement_counts,
                'total_statements': sum(statement_counts.values()),
                'features': features,
                'engine_hints': engine_hints,
                'complexity_score': complexity_score,
                'estimated_execution_complexity': self.get_complexity_level(complexity_score),
                'potential_issues': self.detect_potential_issues(content),
                'content_summary': self.generate_content_summary(statement_counts, features)
            }
            
        except Exception as e:
            return {
                'error': f'Content analysis failed: {str(e)}',
                'statement_counts': {},
                'features': {},
                'complexity_score': 0
            }
    
    def calculate_content_complexity(self, content: str) -> int:
        """Calculate content complexity score (0-100)"""
        complexity = 0
        content_upper = content.upper()
        
        # Base complexity from length
        complexity += min(len(content) / 10000, 20)  # Max 20 points for length
        
        # Add complexity for SQL features
        complexity += content_upper.count('JOIN') * 2
        complexity += content_upper.count('UNION') * 3
        complexity += content_upper.count('CASE') * 2
        complexity += len(re.findall(r'\w+\(', content)) * 0.5  # Functions
        
        return min(int(complexity), 100)
    
    def calculate_sql_complexity(self, content: str) -> int:
        """Calculate SQL-specific complexity score"""
        complexity = 0
        content_upper = content.upper()
        
        # Statement complexity
        complexity += content_upper.count('SELECT') * 5
        complexity += content_upper.count('JOIN') * 10
        complexity += content_upper.count('UNION') * 15
        complexity += content_upper.count('CASE') * 8
        complexity += content_upper.count('EXISTS') * 12
        complexity += content_upper.count('GROUP BY') * 10
        complexity += content_upper.count('ORDER BY') * 5
        complexity += content_upper.count('HAVING') * 12
        
        # Nested queries
        select_count = content_upper.count('SELECT')
        if select_count > 1:
            complexity += (select_count - 1) * 15  # Subqueries
        
        return min(complexity, 100)
    
    def get_complexity_level(self, score: int) -> str:
        """Get complexity level description"""
        if score <= 25:
            return "Simple"
        elif score <= 50:
            return "Moderate"
        elif score <= 75:
            return "Complex"
        else:
            return "Very Complex"
    
    def detect_potential_issues(self, content: str) -> List[str]:
        """Detect potential issues in SQL content"""
        issues = []
        content_upper = content.upper()
        
        if 'SELECT *' in content_upper:
            issues.append("Contains SELECT * statements")
        
        if content_upper.count('SELECT') > 10:
            issues.append("High number of SELECT statements")
        
        if 'DROP TABLE' in content_upper or 'DROP DATABASE' in content_upper:
            issues.append("Contains potentially destructive DROP statements")
        
        if len(content) > 50000:
            issues.append("Large file size may impact processing time")
        
        if content.count('\n') > 1000:
            issues.append("High line count may indicate complex operations")
        
        return issues
    
    def generate_content_summary(self, statement_counts: Dict[str, int], features: Dict[str, bool]) -> str:
        """Generate human-readable content summary"""
        total_statements = sum(statement_counts.values())
        
        if total_statements == 0:
            return "No SQL statements detected"
        
        summary_parts = []
        
        # Most common statement type
        most_common = max(statement_counts.items(), key=lambda x: x[1])
        if most_common[1] > 0:
            summary_parts.append(f"Primarily {most_common[0]} operations ({most_common[1]} statements)")
        
        # Notable features
        notable_features = [k.replace('has_', '').replace('_', ' ') for k, v in features.items() if v]
        if notable_features:
            summary_parts.append(f"Features: {', '.join(notable_features[:3])}")
        
        return "; ".join(summary_parts) if summary_parts else f"{total_statements} SQL statements"
    
    def estimate_processing_time(self, content_length: int) -> str:
        """Estimate processing time based on content length"""
        if content_length < 1000:
            return "< 1 second"
        elif content_length < 10000:
            return "1-3 seconds"
        elif content_length < 100000:
            return "3-10 seconds"
        elif content_length < 1000000:
            return "10-30 seconds"
        else:
            return "30+ seconds"
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
