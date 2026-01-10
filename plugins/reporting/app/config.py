"""
Configuration module for the Reporting plugin.

Handles loading and validation of plugin configuration from Caldera's
conf/local.yml and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
import yaml
from app.utility.base_world import BaseWorld


class ReportingConfig:
    """Configuration loader for reporting plugin."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to config file (defaults to conf/local.yml)
        """
        self.config_path = config_path or Path('conf/local.yml')
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from Caldera's BaseWorld config system
        reporting_config = BaseWorld.get_config(prop='reporting', name='main') or {}
        
        # Report output directory
        self.output_dir = Path(
            os.getenv(
                'REPORTING_OUTPUT_DIR',
                reporting_config.get('output_dir', 'plugins/reporting/data/reports')
            )
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # PDF generation settings
        self.page_size = reporting_config.get('page_size', 'LETTER')
        self.font_name = reporting_config.get('font_name', 'Helvetica')
        self.font_size = int(reporting_config.get('font_size', 10))
        
        # Performance tuning
        self.max_workers = int(
            os.getenv(
                'REPORTING_MAX_WORKERS',
                reporting_config.get('max_workers', 3)
            )
        )
        self.generation_timeout = int(
            os.getenv(
                'REPORTING_TIMEOUT',
                reporting_config.get('generation_timeout', 30)
            )
        )
        self.max_memory_mb = int(
            os.getenv(
                'REPORTING_MAX_MEMORY_MB',
                reporting_config.get('max_memory_mb', 100)
            )
        )
        
        # Branding
        self.company_name = reporting_config.get('company_name', 'Triskele Labs')
        self.logo_path = Path(
            reporting_config.get('logo_path', 'plugins/reporting/static/assets/triskele_logo.png')
        )
        
        # Colors (Triskele Labs brand colors)
        self.primary_color = reporting_config.get('primary_color', '#0f3460')
        self.accent_color = reporting_config.get('accent_color', '#16a085')
        self.text_color = reporting_config.get('text_color', '#1F2937')
        
        # Feature flags
        self.include_executive_summary = reporting_config.get('include_executive_summary', True)
        self.include_tactic_coverage = reporting_config.get('include_tactic_coverage', True)
        self.include_technique_details = reporting_config.get('include_technique_details', True)
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate output directory is writable
        if not os.access(self.output_dir, os.W_OK):
            errors.append(f"Output directory not writable: {self.output_dir}")
        
        # Validate performance settings
        if self.max_workers < 1 or self.max_workers > 10:
            errors.append(f"max_workers must be between 1 and 10 (got {self.max_workers})")
        
        if self.generation_timeout < 5 or self.generation_timeout > 300:
            errors.append(f"generation_timeout must be between 5 and 300 seconds (got {self.generation_timeout})")
        
        if self.max_memory_mb < 50 or self.max_memory_mb > 500:
            errors.append(f"max_memory_mb must be between 50 and 500 MB (got {self.max_memory_mb})")
        
        # Validate page size
        valid_page_sizes = ['LETTER', 'A4', 'LEGAL']
        if self.page_size not in valid_page_sizes:
            errors.append(f"page_size must be one of {valid_page_sizes} (got {self.page_size})")
        
        # Validate font size
        if self.font_size < 8 or self.font_size > 14:
            errors.append(f"font_size must be between 8 and 14 (got {self.font_size})")
        
        return (len(errors) == 0, errors)
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"ReportingConfig("
            f"output_dir={self.output_dir}, "
            f"max_workers={self.max_workers}, "
            f"timeout={self.generation_timeout}s, "
            f"max_memory={self.max_memory_mb}MB)"
        )
