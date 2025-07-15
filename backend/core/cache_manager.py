#!/usr/bin/env python3
"""
Advanced Caching System
Optimize API response times from 2-3s to <0.5s with intelligent caching
"""

import json
import hashlib
import time
import threading
import logging
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict
import pickle
import gzip

logger = logging.getLogger(__name__)

class LRUCache:
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.stats['hits'] += 1
                return value
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any):
        """Set item in cache"""
        with self.lock:
            if key in self.cache:
                # Update existing item
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used item
                self.cache.popitem(last=False)
                self.stats['evictions'] += 1
            
            self.cache[key] = value
            self.stats['size'] = len(self.cache)
    
    def delete(self, key: str):
        """Delete item from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats['size'] = len(self.cache)
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.stats['size'] = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }

class TTLCache:
    """Time-to-live cache with automatic expiration"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.default_ttl = default_ttl
        self.cache = {}
        self.expiry_times = {}
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'expired': 0,
            'size': 0
        }
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        with self.lock:
            if key in self.cache:
                if time.time() < self.expiry_times[key]:
                    self.stats['hits'] += 1
                    return self.cache[key]
                else:
                    # Item expired
                    del self.cache[key]
                    del self.expiry_times[key]
                    self.stats['expired'] += 1
                    self.stats['size'] = len(self.cache)
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set item in cache with TTL"""
        with self.lock:
            ttl = ttl or self.default_ttl
            expiry_time = time.time() + ttl
            
            self.cache[key] = value
            self.expiry_times[key] = expiry_time
            self.stats['size'] = len(self.cache)
    
    def delete(self, key: str):
        """Delete item from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.expiry_times[key]
                self.stats['size'] = len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }

class CompressionCache:
    """Cache with compression for large objects"""
    
    def __init__(self, max_size: int = 100, compression_threshold: int = 1024):
        self.max_size = max_size
        self.compression_threshold = compression_threshold
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'compressed_items': 0,
            'compression_ratio': 0.0,
            'size': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                data, is_compressed = self.cache.pop(key)
                self.cache[key] = (data, is_compressed)  # Move to end
                self.stats['hits'] += 1
                
                return self._decompress_data(data, is_compressed)
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any):
        """Set item in cache with compression"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            compressed_data, is_compressed = self._compress_data(value)
            self.cache[key] = (compressed_data, is_compressed)
            self.stats['size'] = len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }

class CacheManager:
    """Advanced cache management system"""
    
    def __init__(self):
        # Different cache types for different use cases
        self.lru_cache = LRUCache(max_size=500)  # Fast access cache
        self.ttl_cache = TTLCache(default_ttl=300)  # Time-based cache
        self.compression_cache = CompressionCache(max_size=100)  # Large object cache
        
        # Cache key prefixes for different data types
        self.prefixes = {
            'sql_analysis': 'sql_',
            'database_engines': 'db_',
            'export_formats': 'exp_',
            'metrics': 'met_',
            'user_data': 'usr_'
        }
        
        logger.info("Advanced cache manager initialized")
    
    def cache_sql_analysis(self, sql_content: str, database_engine: str, result: Any):
        """Cache SQL analysis result"""
        key = self._generate_key(
            self.prefixes['sql_analysis'],
            sql_content, database_engine
        )
        
        # Use compression cache for large analysis results
        self.compression_cache.set(key, result)
        logger.debug(f"Cached SQL analysis: {key}")
    
    def get_sql_analysis(self, sql_content: str, database_engine: str) -> Optional[Any]:
        """Get cached SQL analysis result"""
        key = self._generate_key(
            self.prefixes['sql_analysis'],
            sql_content, database_engine
        )
        
        result = self.compression_cache.get(key)
        if result:
            logger.debug(f"Cache hit for SQL analysis: {key}")
        
        return result
    
    def cache_database_engines(self, engines: Any):
        """Cache database engines list"""
        key = self.prefixes['database_engines'] + 'all'
        self.ttl_cache.set(key, engines, ttl=3600)  # Cache for 1 hour
        logger.debug("Cached database engines")
    
    def get_database_engines(self) -> Optional[Any]:
        """Get cached database engines"""
        key = self.prefixes['database_engines'] + 'all'
        result = self.ttl_cache.get(key)
        if result:
            logger.debug("Cache hit for database engines")
        return result
    
    def cache_export_formats(self, formats: Any):
        """Cache export formats list"""
        key = self.prefixes['export_formats'] + 'all'
        self.ttl_cache.set(key, formats, ttl=3600)  # Cache for 1 hour
        logger.debug("Cached export formats")
    
    def get_export_formats(self) -> Optional[Any]:
        """Get cached export formats"""
        key = self.prefixes['export_formats'] + 'all'
        result = self.ttl_cache.get(key)
        if result:
            logger.debug("Cache hit for export formats")
        return result
    
    def cache_metrics(self, metrics_type: str, metrics: Any):
        """Cache metrics data"""
        key = self.prefixes['metrics'] + metrics_type
        self.lru_cache.set(key, metrics)
        logger.debug(f"Cached metrics: {metrics_type}")
    
    def get_metrics(self, metrics_type: str) -> Optional[Any]:
        """Get cached metrics"""
        key = self.prefixes['metrics'] + metrics_type
        result = self.lru_cache.get(key)
        if result:
            logger.debug(f"Cache hit for metrics: {metrics_type}")
        return result
    
    def invalidate_cache(self, cache_type: str = None):
        """Invalidate specific cache or all caches"""
        if cache_type == 'sql_analysis':
            # Clear compression cache (SQL analysis)
            self.compression_cache.cache.clear()
        elif cache_type == 'database_engines':
            key = self.prefixes['database_engines'] + 'all'
            self.ttl_cache.delete(key)
        elif cache_type == 'export_formats':
            key = self.prefixes['export_formats'] + 'all'
            self.ttl_cache.delete(key)
        elif cache_type == 'metrics':
            # Clear LRU cache (metrics)
            self.lru_cache.clear()
        else:
            # Clear all caches
            self.lru_cache.clear()
            self.ttl_cache.cache.clear()
            self.compression_cache.cache.clear()
        
        logger.info(f"Invalidated cache: {cache_type or 'all'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            'lru_cache': self.lru_cache.get_stats(),
            'ttl_cache': self.ttl_cache.get_stats(),
            'compression_cache': self.compression_cache.get_stats(),
            'total_memory_usage': self._estimate_memory_usage()
        }
    
cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    return cache_manager

# Decorators for automatic caching
def cache_result(cache_type: str = 'lru', ttl: int = 300):
    """Decorator for automatic result caching"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_manager._generate_key(f"func_{func.__name__}_", *args, **kwargs)
            
            # Try to get from cache
            if cache_type == 'lru':
                result = cache_manager.lru_cache.get(key)
            elif cache_type == 'ttl':
                result = cache_manager.ttl_cache.get(key)
            else:
                result = cache_manager.compression_cache.get(key)
            
            if result is not None:
                logger.debug(f"Cache hit for function {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            if cache_type == 'lru':
                cache_manager.lru_cache.set(key, result)
            elif cache_type == 'ttl':
                cache_manager.ttl_cache.set(key, result, ttl)
            else:
                cache_manager.compression_cache.set(key, result)
            
            logger.debug(f"Cached result for function {func.__name__}")
            return result
        
        return wrapper
    return decorator

def cache_sql_analysis(func: Callable) -> Callable:
    """Decorator specifically for SQL analysis caching"""
    @wraps(func)
    def wrapper(sql_content: str, database_engine: str = 'mysql', *args, **kwargs):
        # Try to get from cache
        cached_result = cache_manager.get_sql_analysis(sql_content, database_engine)
        if cached_result:
            return cached_result
        
        # Execute analysis and cache result
        result = func(sql_content, database_engine, *args, **kwargs)
        cache_manager.cache_sql_analysis(sql_content, database_engine, result)
        
        return result
    
    return wrapper
