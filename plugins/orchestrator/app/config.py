"""Configuration loader for orchestrator plugin."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OrchestratorConfig:
    """Orchestrator plugin configuration."""
    
    # Elasticsearch settings
    ELK_URL = os.getenv('ELK_URL', 'http://localhost:9200')
    ELK_INDEX = os.getenv('ELK_INDEX', 'purple-team-logs')
    ELK_API_KEY = os.getenv('ELK_API_KEY', '')
    ELK_VERIFY_SSL = os.getenv('ELK_VERIFY_SSL', 'false').lower() == 'true'
    ELK_CONNECTION_TIMEOUT = int(os.getenv('ELK_CONNECTION_TIMEOUT', '30'))
    ELK_MAX_RETRIES = int(os.getenv('ELK_MAX_RETRIES', '3'))
    
    # Paths
    FALLBACK_LOG_DIR = Path('plugins/orchestrator/data/fallback_logs')
    
    # Health check thresholds
    MEMORY_WARNING_GB = float(os.getenv('MEMORY_WARNING_GB', '6.5'))
    MEMORY_CRITICAL_GB = float(os.getenv('MEMORY_CRITICAL_GB', '7.5'))
    DISK_WARNING_GB = float(os.getenv('DISK_WARNING_GB', '10'))
    DISK_CRITICAL_GB = float(os.getenv('DISK_CRITICAL_GB', '5'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.ELK_URL:
            raise ValueError("ELK_URL must be set in .env")
        if not cls.ELK_INDEX:
            raise ValueError("ELK_INDEX must be set in .env")
        cls.FALLBACK_LOG_DIR.mkdir(parents=True, exist_ok=True)
