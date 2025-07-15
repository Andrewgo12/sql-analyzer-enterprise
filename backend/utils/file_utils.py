"""
File Utilities for SQL Analyzer

Common file operations and utilities for handling various file formats
and file system operations.
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
# import magic  # Commented out for Windows compatibility
import chardet


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """
        Calculate file hash.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (md5, sha1, sha256)
            
        Returns:
            Hexadecimal hash string
        """
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_mime_type(file_path: str) -> str:
        """
        Get MIME type of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        try:
            # Use mimetypes (python-magic commented out for Windows compatibility)
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or 'application/octet-stream'
        except:
            return 'application/octet-stream'
    
    @staticmethod
    def detect_file_encoding(file_path: str, sample_size: int = 10000) -> Dict[str, Any]:
        """
        Detect file encoding with confidence score.
        
        Args:
            file_path: Path to the file
            sample_size: Number of bytes to sample
            
        Returns:
            Dictionary with encoding information
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            
        return {
            'encoding': result.get('encoding', 'utf-8'),
            'confidence': result.get('confidence', 0.0),
            'language': result.get('language', '')
        }
    
    @staticmethod
    def safe_file_copy(source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Safely copy a file with error handling.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return False
            
            if dest_path.exists() and not overwrite:
                return False
            
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def create_backup(file_path: str, backup_suffix: str = '.bak') -> Optional[str]:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            backup_suffix: Suffix for backup file
            
        Returns:
            Path to backup file if successful, None otherwise
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            backup_path = source_path.with_suffix(source_path.suffix + backup_suffix)
            
            # If backup already exists, add timestamp
            if backup_path.exists():
                import time
                timestamp = int(time.time())
                backup_path = source_path.with_suffix(f"{source_path.suffix}.{timestamp}{backup_suffix}")
            
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
            
        except Exception:
            return None
    
    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str, recursive: bool = True) -> List[str]:
        """
        Find files matching a pattern.
        
        Args:
            directory: Directory to search
            pattern: File pattern (glob style)
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return []
        
        if recursive:
            return [str(p) for p in directory_path.rglob(pattern)]
        else:
            return [str(p) for p in directory_path.glob(pattern)]
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """
        Calculate total size of a directory.
        
        Args:
            directory: Directory path
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception:
            pass
        
        return total_size
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        import re
        
        # Remove invalid characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Remove leading/trailing underscores and dots
        cleaned = cleaned.strip('_.')
        
        return cleaned or 'unnamed'
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def is_text_file(file_path: str, sample_size: int = 1024) -> bool:
        """
        Check if a file is a text file.
        
        Args:
            file_path: Path to the file
            sample_size: Number of bytes to sample
            
        Returns:
            True if file appears to be text
        """
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
            
            # Check for null bytes (common in binary files)
            if b'\x00' in sample:
                return False
            
            # Try to decode as text
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                try:
                    sample.decode('latin-1')
                    return True
                except UnicodeDecodeError:
                    return False
                    
        except Exception:
            return False
    
    @staticmethod
    def get_file_stats(file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive file statistics.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file statistics
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'size': stat.st_size,
                'size_formatted': FileUtils.format_file_size(stat.st_size),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'is_symlink': path.is_symlink(),
                'suffix': path.suffix,
                'stem': path.stem,
                'name': path.name,
                'parent': str(path.parent),
                'absolute_path': str(path.absolute()),
                'exists': path.exists(),
                'is_text': FileUtils.is_text_file(file_path) if path.is_file() else False,
                'mime_type': FileUtils.get_file_mime_type(file_path) if path.is_file() else None
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        Ensure directory exists, create if necessary.
        
        Args:
            directory: Directory path
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def temp_file_path(suffix: str = '.tmp', prefix: str = 'sql_analyzer_') -> str:
        """
        Generate a temporary file path.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Returns:
            Temporary file path
        """
        import tempfile
        import uuid
        
        temp_dir = tempfile.gettempdir()
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{prefix}{unique_id}{suffix}"
        
        return os.path.join(temp_dir, filename)
