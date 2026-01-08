"""Configuration loader for orchestrator plugin.

Uses Caldera's BaseWorld config system to read from conf/local.yml.
Supports API key auth (preferred) or basic auth fallback for Elasticsearch.
"""

import os
import logging
from pathlib import Path

try:
    from app.utility.base_world import BaseWorld
except ImportError:
    # Fallback for testing outside Caldera
    BaseWorld = None

try:
    from elasticsearch import AsyncElasticsearch
except ImportError:
    AsyncElasticsearch = None


class OrchestratorConfig:
    """
    Orchestrator plugin configuration.
    
    Reads from conf/local.yml under plugins.orchestrator.* keys.
    Falls back to environment variables if BaseWorld unavailable.
    """
    
    _log = logging.getLogger('orchestrator.config')
    
    # Default values (overridden by conf/local.yml or env vars)
    ELK_URL = 'http://20.28.49.97:9200'
    ELK_INDEX = 'purple-team-logs'
    ELK_API_KEY = ''
    ELK_USER = 'elastic'
    ELK_PASS = 'ms4FiYr-C1bx0F1=GFrM'
    ELK_VERIFY_SSL = False
    ELK_CONNECTION_TIMEOUT = 30
    ELK_MAX_RETRIES = 3
    
    # Paths
    FALLBACK_LOG_DIR = Path('plugins/orchestrator/data/fallback_logs')
    
    # Health check thresholds
    MEMORY_WARNING_GB = 6.5
    MEMORY_CRITICAL_GB = 7.5
    DISK_WARNING_GB = 10.0
    DISK_CRITICAL_GB = 5.0
    
    @classmethod
    def _get_config(cls, key: str, default=None):
        """
        Get config value from BaseWorld or environment.
        
        Args:
            key: Config key (e.g., 'elk_url')
            default: Default value if not found
            
        Returns:
            Config value
        """
        # Try BaseWorld config first (conf/local.yml)
        if BaseWorld:
            try:
                # Caldera stores plugin config under plugins.{name}.{key}
                caldera_key = f'plugins.orchestrator.{key}'
                value = BaseWorld.get_config(caldera_key)
                if value is not None:
                    return value
            except Exception:
                pass
        
        # Fall back to environment variable
        env_key = f'ORCHESTRATOR_{key.upper()}'
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Legacy env var support (ELK_URL, etc.)
        legacy_key = key.upper()
        legacy_value = os.getenv(legacy_key)
        if legacy_value is not None:
            return legacy_value
        
        return default
    
    @classmethod
    def load(cls):
        """Load configuration from BaseWorld/environment."""
        cls.ELK_URL = cls._get_config('elk_url', cls.ELK_URL)
        cls.ELK_INDEX = cls._get_config('elk_index', cls.ELK_INDEX)
        cls.ELK_API_KEY = cls._get_config('elk_api_key', cls.ELK_API_KEY)
        cls.ELK_USER = cls._get_config('elk_user', cls.ELK_USER)
        cls.ELK_PASS = cls._get_config('elk_pass', cls.ELK_PASS)
        
        # Boolean/int conversions
        verify_ssl = cls._get_config('elk_verify_ssl', cls.ELK_VERIFY_SSL)
        cls.ELK_VERIFY_SSL = str(verify_ssl).lower() in ('true', '1', 'yes')
        
        timeout = cls._get_config('elk_connection_timeout', cls.ELK_CONNECTION_TIMEOUT)
        cls.ELK_CONNECTION_TIMEOUT = int(timeout)
        
        retries = cls._get_config('elk_max_retries', cls.ELK_MAX_RETRIES)
        cls.ELK_MAX_RETRIES = int(retries)
        
        cls._log.info(f'Config loaded: ELK_URL={cls.ELK_URL}, INDEX={cls.ELK_INDEX}')
    
    @classmethod
    def get_es_client(cls) -> 'AsyncElasticsearch':
        """
        Create Elasticsearch client with appropriate authentication.
        
        Uses API key if configured, otherwise falls back to basic auth.
        
        Returns:
            AsyncElasticsearch client instance
            
        Raises:
            ImportError: If elasticsearch library not installed
        """
        if not AsyncElasticsearch:
            raise ImportError('elasticsearch library not installed')
        
        # Load latest config
        cls.load()
        
        client_kwargs = {
            'hosts': [cls.ELK_URL],
            'verify_certs': cls.ELK_VERIFY_SSL,
            'request_timeout': cls.ELK_CONNECTION_TIMEOUT,
            'max_retries': cls.ELK_MAX_RETRIES,
            'retry_on_timeout': True
        }
        
        # API key auth (preferred - more secure)
        if cls.ELK_API_KEY:
            cls._log.info('Using API key authentication for Elasticsearch')
            client_kwargs['api_key'] = cls.ELK_API_KEY
        
        # Basic auth fallback
        elif cls.ELK_USER and cls.ELK_PASS:
            cls._log.info(f'Using basic auth for Elasticsearch (user: {cls.ELK_USER})')
            client_kwargs['basic_auth'] = (cls.ELK_USER, cls.ELK_PASS)
        
        else:
            cls._log.warning('No Elasticsearch authentication configured')
        
        return AsyncElasticsearch(**client_kwargs)
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        cls.load()
        
        if not cls.ELK_URL:
            raise ValueError("elk_url must be set in conf/local.yml or ELK_URL env var")
        if not cls.ELK_INDEX:
            raise ValueError("elk_index must be set in conf/local.yml or ELK_INDEX env var")
        
        cls.FALLBACK_LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls._log.info('Orchestrator configuration validated')
