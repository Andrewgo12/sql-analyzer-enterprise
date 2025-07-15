"""
Configuration Module

Central configuration for the SQL Analyzer Enterprise system.
Provides comprehensive configuration management with environment support.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .format_config import (
    FORMAT_MAPPING, FORMAT_DESCRIPTIONS, ENTERPRISE_FEATURES,
    get_format_info, get_enterprise_feature_info,
    get_formats_by_category, get_enterprise_features_by_category
)


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///sql_analyzer.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    max_connections: int = 100
    timeout: int = 300


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = "change-this-in-production"
    session_timeout: int = 3600
    max_login_attempts: int = 5
    csrf_protection: bool = True
    rate_limiting_enabled: bool = True
    requests_per_minute: int = 60
    burst_limit: int = 10


@dataclass
class FileConfig:
    """File handling configuration."""
    max_file_size: int = 100 * 1024 * 1024 * 1024  # 100GB
    max_files_per_batch: int = 10
    allowed_extensions: List[str] = field(default_factory=lambda: [".sql", ".txt"])
    chunk_size: int = 1024 * 1024  # 1MB
    upload_dir: str = "uploads"
    results_dir: str = "results"
    temp_dir: str = "temp"


@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    max_errors_per_file: int = 1000
    enable_auto_fix: bool = True
    enable_intelligent_comments: bool = True
    enable_sample_data_generation: bool = True
    default_language: str = "es"
    supported_languages: List[str] = field(default_factory=lambda: ["es", "en"])
    analysis_timeout: int = 300
    parallel_workers: int = 4


class Config:
    """Main configuration class."""

    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.database = DatabaseConfig()
        self.server = ServerConfig()
        self.security = SecurityConfig()
        self.files = FileConfig()
        self.analysis = AnalysisConfig()

        # Load environment-specific configuration
        self._load_environment_config()

        # Load from environment variables
        self._load_from_env()

    def _load_environment_config(self):
        """Load environment-specific configuration."""
        if self.environment == Environment.PRODUCTION:
            self.server.debug = False
            self.server.reload = False
            self.server.workers = 4
            self.security.csrf_protection = True

        elif self.environment == Environment.DEVELOPMENT:
            self.server.debug = True
            self.server.reload = True

        elif self.environment == Environment.TESTING:
            self.database.url = "sqlite:///:memory:"

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Server configuration
        self.server.host = os.getenv("SQL_ANALYZER_HOST", self.server.host)
        self.server.port = int(os.getenv("SQL_ANALYZER_PORT", self.server.port))
        self.server.debug = os.getenv("SQL_ANALYZER_DEBUG", "false").lower() == "true"

        # Database configuration
        self.database.url = os.getenv("DATABASE_URL", self.database.url)

        # Security configuration
        self.security.secret_key = os.getenv("SECRET_KEY", self.security.secret_key)

        # File configuration
        max_size_env = os.getenv("MAX_FILE_SIZE")
        if max_size_env:
            self.files.max_file_size = int(max_size_env)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        env = Environment(os.getenv("SQL_ANALYZER_ENV", "development"))
        _config = Config(env)
    return _config


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_config().database


def get_server_config() -> ServerConfig:
    """Get server configuration."""
    return get_config().server


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return get_config().security


def get_file_config() -> FileConfig:
    """Get file configuration."""
    return get_config().files


def get_analysis_config() -> AnalysisConfig:
    """Get analysis configuration."""
    return get_config().analysis


__all__ = [
    'FORMAT_MAPPING', 'FORMAT_DESCRIPTIONS', 'ENTERPRISE_FEATURES',
    'get_format_info', 'get_enterprise_feature_info',
    'get_formats_by_category', 'get_enterprise_features_by_category',
    'Config', 'Environment', 'LogLevel',
    'DatabaseConfig', 'ServerConfig', 'SecurityConfig', 'FileConfig', 'AnalysisConfig',
    'get_config', 'get_database_config', 'get_server_config', 'get_security_config',
    'get_file_config', 'get_analysis_config'
]
