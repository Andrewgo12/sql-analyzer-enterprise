#!/usr/bin/env python3
"""
Enterprise Metrics and Monitoring System
Real-time performance monitoring, analytics, and system health tracking
"""

import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'tags': self.tags or {}
        }

@dataclass
class SystemHealth:
    """System health status"""
    status: str  # healthy, warning, critical
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    response_time: float
    error_rate: float
    uptime: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MetricsCollector:
    """Collects and stores system metrics"""
    
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
        
        # System health tracking
        self.health_history: deque = deque(maxlen=100)
        self.start_time = datetime.now()
        
        # Analysis statistics
        self.analysis_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'avg_processing_time': 0.0,
            'total_files_processed': 0,
            'total_lines_analyzed': 0,
            'total_errors_detected': 0,
            'database_engines_used': defaultdict(int),
            'export_formats_used': defaultdict(int)
        }
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value"""
        with self.lock:
            point = MetricPoint(datetime.now(), value, tags)
            self.metrics[name].append(point)
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        with self.lock:
            self.counters[name] += value
            self.record_metric(f"{name}_total", self.counters[name], tags)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        with self.lock:
            self.gauges[name] = value
            self.record_metric(name, value, tags)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timing metric"""
        with self.lock:
            self.timers[name].append(duration)
            # Keep only last 100 measurements
            if len(self.timers[name]) > 100:
                self.timers[name] = self.timers[name][-100:]
            
            # Calculate statistics
            times = self.timers[name]
            avg_time = sum(times) / len(times)
            self.record_metric(f"{name}_avg", avg_time, tags)
            self.record_metric(f"{name}_latest", duration, tags)
    
    def record_analysis_start(self, filename: str, database_engine: str = None):
        """Record the start of an analysis"""
        with self.lock:
            self.analysis_stats['total_analyses'] += 1
            if database_engine:
                self.analysis_stats['database_engines_used'][database_engine] += 1
            
            self.increment_counter('analyses_started')
            self.record_metric('active_analyses', self.get_active_analyses())
    
    def record_analysis_success(self, filename: str, processing_time: float, 
                              lines_analyzed: int, errors_detected: int):
        """Record successful analysis completion"""
        with self.lock:
            self.analysis_stats['successful_analyses'] += 1
            self.analysis_stats['total_files_processed'] += 1
            self.analysis_stats['total_lines_analyzed'] += lines_analyzed
            self.analysis_stats['total_errors_detected'] += errors_detected
            
            # Update average processing time
            total = self.analysis_stats['total_analyses']
            current_avg = self.analysis_stats['avg_processing_time']
            self.analysis_stats['avg_processing_time'] = (
                (current_avg * (total - 1) + processing_time) / total
            )
            
            self.increment_counter('analyses_successful')
            self.record_timer('analysis_duration', processing_time)
            self.record_metric('lines_per_analysis', lines_analyzed)
            self.record_metric('errors_per_analysis', errors_detected)
    
    def record_analysis_failure(self, filename: str, error: str):
        """Record failed analysis"""
        with self.lock:
            self.analysis_stats['failed_analyses'] += 1
            self.increment_counter('analyses_failed')
            logger.error(f"Analysis failed for {filename}: {error}")
    
    def record_export(self, format_name: str, file_size: int):
        """Record export operation"""
        with self.lock:
            self.analysis_stats['export_formats_used'][format_name] += 1
            self.increment_counter('exports_total')
            self.record_metric('export_file_size', file_size, {'format': format_name})
    
    def get_active_analyses(self) -> int:
        """Get number of currently active analyses"""
        # This would be implemented with proper tracking
        return max(0, self.analysis_stats['total_analyses'] - 
                  self.analysis_stats['successful_analyses'] - 
                  self.analysis_stats['failed_analyses'])
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        import psutil
        
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate error rate
            total_analyses = self.analysis_stats['total_analyses']
            failed_analyses = self.analysis_stats['failed_analyses']
            error_rate = (failed_analyses / total_analyses * 100) if total_analyses > 0 else 0
            
            # Calculate uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Determine overall health status
            status = "healthy"
            if cpu_usage > 80 or memory.percent > 85 or error_rate > 10:
                status = "warning"
            if cpu_usage > 95 or memory.percent > 95 or error_rate > 25:
                status = "critical"
            
            health = SystemHealth(
                status=status,
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_connections=self.get_active_analyses(),
                response_time=self.analysis_stats['avg_processing_time'],
                error_rate=error_rate,
                uptime=uptime
            )
            
            self.health_history.append(health)
            return health
            
        except ImportError:
            # Fallback if psutil is not available
            return SystemHealth(
                status="healthy",
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                active_connections=self.get_active_analyses(),
                response_time=self.analysis_stats['avg_processing_time'],
                error_rate=0.0,
                uptime=(datetime.now() - self.start_time).total_seconds()
            )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self.lock:
            health = self.get_system_health()
            
            return {
                'system_health': health.to_dict(),
                'analysis_statistics': self.analysis_stats.copy(),
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'recent_metrics': {
                    name: [point.to_dict() for point in list(points)[-10:]]
                    for name, points in self.metrics.items()
                },
                'performance_summary': {
                    'avg_analysis_time': self.analysis_stats['avg_processing_time'],
                    'success_rate': (
                        self.analysis_stats['successful_analyses'] / 
                        max(1, self.analysis_stats['total_analyses']) * 100
                    ),
                    'total_throughput': self.analysis_stats['total_lines_analyzed'],
                    'error_detection_rate': (
                        self.analysis_stats['total_errors_detected'] /
                        max(1, self.analysis_stats['total_lines_analyzed']) * 100
                    )
                }
            }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display"""
        summary = self.get_metrics_summary()
        
        return {
            'overview': {
                'total_analyses': self.analysis_stats['total_analyses'],
                'success_rate': summary['performance_summary']['success_rate'],
                'avg_processing_time': self.analysis_stats['avg_processing_time'],
                'system_status': summary['system_health']['status']
            },
            'real_time': {
                'active_analyses': self.get_active_analyses(),
                'cpu_usage': summary['system_health']['cpu_usage'],
                'memory_usage': summary['system_health']['memory_usage'],
                'error_rate': summary['system_health']['error_rate']
            },
            'trends': {
                'database_engines': dict(self.analysis_stats['database_engines_used']),
                'export_formats': dict(self.analysis_stats['export_formats_used']),
                'recent_performance': [
                    point.to_dict() for point in list(self.metrics.get('analysis_duration_avg', []))[-20:]
                ]
            }
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()

class MetricsTimer:
    """Context manager for timing operations"""
    
    def __init__(self, metric_name: str, tags: Dict[str, str] = None):
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            metrics_collector.record_timer(self.metric_name, duration, self.tags)

def time_operation(metric_name: str, tags: Dict[str, str] = None):
    """Decorator for timing function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with MetricsTimer(metric_name, tags):
                return func(*args, **kwargs)
        return wrapper
    return decorator
