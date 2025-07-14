#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - CONFIGURATION MANAGEMENT SYSTEM
Enterprise-grade configuration management for different environments and use cases
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import configparser

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class ConfigFormat(Enum):
    """Configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    ENV = "env"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "sql_analyzer"
    username: str = "admin"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: str = ""
    session_timeout: int = 3600
    max_login_attempts: int = 5
    password_min_length: int = 8
    enable_2fa: bool = False
    encryption_enabled: bool = True

@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "127.0.0.1"
    port: int = 8081
    workers: int = 4
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"
    cors_origins: List[str] = None

@dataclass
class ProcessingConfig:
    """File processing configuration."""
    max_file_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    max_concurrent_files: int = 5
    chunk_size: int = 8192
    supported_formats: List[str] = None
    temp_dir: str = "temp"
    output_dir: str = "output"

@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    enable_syntax_check: bool = True
    enable_security_scan: bool = True
    enable_performance_analysis: bool = True
    enable_schema_analysis: bool = True
    max_analysis_time: int = 300  # 5 minutes
    parallel_analysis: bool = True

class ConfigurationManager:
    """Enterprise configuration management system."""
    
    def __init__(self, config_dir: str = "config", environment: Environment = Environment.DEVELOPMENT):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.environment = environment
        
        # Configuration storage
        self.configs = {}
        
        # Setup logging
        self.setup_logging()
        
        # Load configurations
        self.load_configurations()
    
    def setup_logging(self):
        """Setup configuration logging."""
        log_file = self.config_dir / "config.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_configurations(self):
        """Load all configuration files."""
        try:
            # Load base configuration
            self.load_base_config()
            
            # Load environment-specific configuration
            self.load_environment_config()
            
            # Load user-specific configuration
            self.load_user_config()
            
            # Validate configurations
            self.validate_configurations()
            
            self.logger.info(f"✅ Configurations loaded for environment: {self.environment.value}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configurations: {e}")
            raise
    
    def load_base_config(self):
        """Load base configuration."""
        base_config_file = self.config_dir / "base.yaml"
        
        if not base_config_file.exists():
            # Create default base configuration
            default_config = {
                'database': asdict(DatabaseConfig()),
                'security': asdict(SecurityConfig()),
                'server': asdict(ServerConfig(cors_origins=["*"])),
                'processing': asdict(ProcessingConfig(supported_formats=[".sql", ".txt", ".pdf"])),
                'analysis': asdict(AnalysisConfig())
            }
            
            self.save_config(default_config, base_config_file, ConfigFormat.YAML)
        
        self.configs['base'] = self.load_config(base_config_file, ConfigFormat.YAML)
    
    def load_environment_config(self):
        """Load environment-specific configuration."""
        env_config_file = self.config_dir / f"{self.environment.value}.yaml"
        
        if env_config_file.exists():
            env_config = self.load_config(env_config_file, ConfigFormat.YAML)
            self.configs['environment'] = env_config
            
            # Merge with base configuration
            self.merge_configurations('base', 'environment')
        else:
            # Create default environment configuration
            env_config = self.create_default_environment_config()
            self.save_config(env_config, env_config_file, ConfigFormat.YAML)
            self.configs['environment'] = env_config
    
    def load_user_config(self):
        """Load user-specific configuration."""
        user_config_file = self.config_dir / "user.yaml"
        
        if user_config_file.exists():
            user_config = self.load_config(user_config_file, ConfigFormat.YAML)
            self.configs['user'] = user_config
            
            # Merge with existing configuration
            self.merge_configurations('base', 'user')
    
    def create_default_environment_config(self) -> Dict[str, Any]:
        """Create default environment-specific configuration."""
        if self.environment == Environment.DEVELOPMENT:
            return {
                'server': {
                    'debug': True,
                    'reload': True,
                    'log_level': 'DEBUG'
                },
                'security': {
                    'jwt_secret': 'dev-secret-key',
                    'encryption_enabled': False
                },
                'processing': {
                    'max_file_size': 100 * 1024 * 1024,  # 100MB for dev
                    'max_concurrent_files': 2
                }
            }
        elif self.environment == Environment.TESTING:
            return {
                'server': {
                    'debug': False,
                    'log_level': 'INFO'
                },
                'database': {
                    'database': 'sql_analyzer_test'
                },
                'processing': {
                    'max_file_size': 50 * 1024 * 1024,  # 50MB for testing
                    'temp_dir': 'temp_test'
                }
            }
        elif self.environment == Environment.PRODUCTION:
            return {
                'server': {
                    'debug': False,
                    'reload': False,
                    'log_level': 'WARNING',
                    'workers': 8
                },
                'security': {
                    'encryption_enabled': True,
                    'enable_2fa': True,
                    'session_timeout': 1800  # 30 minutes
                },
                'processing': {
                    'max_concurrent_files': 10,
                    'parallel_analysis': True
                }
            }
        else:
            return {}
    
    def load_config(self, file_path: Path, format_type: ConfigFormat) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if format_type == ConfigFormat.JSON:
                    return json.load(f)
                elif format_type == ConfigFormat.YAML:
                    return yaml.safe_load(f) or {}
                elif format_type == ConfigFormat.INI:
                    config = configparser.ConfigParser()
                    config.read(file_path)
                    return {section: dict(config[section]) for section in config.sections()}
                else:
                    raise ValueError(f"Unsupported config format: {format_type}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load config from {file_path}: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any], file_path: Path, format_type: ConfigFormat):
        """Save configuration to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type == ConfigFormat.JSON:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                elif format_type == ConfigFormat.YAML:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                elif format_type == ConfigFormat.INI:
                    config_parser = configparser.ConfigParser()
                    for section, values in config.items():
                        config_parser[section] = values
                    config_parser.write(f)
                else:
                    raise ValueError(f"Unsupported config format: {format_type}")
                    
            self.logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config to {file_path}: {e}")
            raise
    
    def merge_configurations(self, base_key: str, override_key: str):
        """Merge configurations with override priority."""
        if base_key not in self.configs or override_key not in self.configs:
            return
        
        base_config = self.configs[base_key]
        override_config = self.configs[override_key]
        
        merged = self._deep_merge(base_config.copy(), override_config)
        self.configs['merged'] = merged
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value."""
        config = self.configs.get('merged', self.configs.get('base', {}))
        
        if section not in config:
            return default
        
        if key is None:
            return config[section]
        
        return config[section].get(key, default)
    
    def set_config(self, section: str, key: str, value: Any):
        """Set configuration value."""
        if 'user' not in self.configs:
            self.configs['user'] = {}
        
        if section not in self.configs['user']:
            self.configs['user'][section] = {}
        
        self.configs['user'][section][key] = value
        
        # Save user configuration
        user_config_file = self.config_dir / "user.yaml"
        self.save_config(self.configs['user'], user_config_file, ConfigFormat.YAML)
        
        # Re-merge configurations
        self.merge_configurations('base', 'user')
    
    def validate_configurations(self):
        """Validate configuration values."""
        config = self.configs.get('merged', self.configs.get('base', {}))
        
        # Validate server configuration
        server_config = config.get('server', {})
        if not (1 <= server_config.get('port', 8081) <= 65535):
            raise ValueError("Server port must be between 1 and 65535")
        
        # Validate security configuration
        security_config = config.get('security', {})
        if security_config.get('password_min_length', 8) < 4:
            raise ValueError("Password minimum length must be at least 4")
        
        # Validate processing configuration
        processing_config = config.get('processing', {})
        if processing_config.get('max_file_size', 0) <= 0:
            raise ValueError("Maximum file size must be positive")
        
        self.logger.info("✅ Configuration validation passed")
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration as dataclass."""
        db_config = self.get_config('database', default={})
        return DatabaseConfig(**db_config)
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration as dataclass."""
        security_config = self.get_config('security', default={})
        return SecurityConfig(**security_config)
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration as dataclass."""
        server_config = self.get_config('server', default={})
        if server_config.get('cors_origins') is None:
            server_config['cors_origins'] = ["*"]
        return ServerConfig(**server_config)
    
    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration as dataclass."""
        processing_config = self.get_config('processing', default={})
        if processing_config.get('supported_formats') is None:
            processing_config['supported_formats'] = [".sql", ".txt", ".pdf"]
        return ProcessingConfig(**processing_config)
    
    def get_analysis_config(self) -> AnalysisConfig:
        """Get analysis configuration as dataclass."""
        analysis_config = self.get_config('analysis', default={})
        return AnalysisConfig(**analysis_config)
    
    def export_config(self, output_file: str, format_type: ConfigFormat = ConfigFormat.YAML):
        """Export current configuration to file."""
        config = self.configs.get('merged', self.configs.get('base', {}))
        output_path = Path(output_file)
        self.save_config(config, output_path, format_type)
        
        self.logger.info(f"Configuration exported to {output_file}")
    
    def list_configurations(self) -> Dict[str, Any]:
        """List all loaded configurations."""
        return {
            'environment': self.environment.value,
            'loaded_configs': list(self.configs.keys()),
            'config_dir': str(self.config_dir),
            'current_config': self.configs.get('merged', self.configs.get('base', {}))
        }

if __name__ == "__main__":
    # Example usage
    config_manager = ConfigurationManager(environment=Environment.DEVELOPMENT)
    
    # Get configurations
    server_config = config_manager.get_server_config()
    db_config = config_manager.get_database_config()
    
    print(f"✅ Server running on {server_config.host}:{server_config.port}")
    print(f"✅ Database: {db_config.database} on {db_config.host}:{db_config.port}")
    print(f"✅ Debug mode: {server_config.debug}")
    
    # List all configurations
    config_info = config_manager.list_configurations()
    print(f"✅ Configuration manager initialized with {len(config_info['loaded_configs'])} config sources")
